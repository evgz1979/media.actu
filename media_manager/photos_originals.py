"""PhotoKit originals written into a bound copy; resume uses file metadata only.

SQLite contains manifests and receipts, never original media bytes.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import json
import os
from pathlib import PurePosixPath
import re
import stat
import threading
import time
from uuid import uuid4

from .comparison import fingerprint, name_key, open_readonly
from .copy_files import destination_directory, object_id
from .photo_libraries import now
from .photos_adapter import PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable, PhotosTransferStopped


ACTIVE = {'manifest', 'inventory', 'saving', 'pausing'}
WRITE_BUFFER_BYTES = 64 * 1024 * 1024
SPACE_CHECK_SECONDS = 5
SPACE_RESERVE_BYTES = 64 * 1024 * 1024
COPY_BATCH_RESOURCES = 256


#: Сериализует данные задания в стабильный JSON с сохранением Unicode.
#: Использует json.dumps.
def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


#: Сравнивает размер, mtime, inode и device сохранённого файла.
#: ctime исключён: SMB может уточнять его после успешного завершения записи.
def same_file(left, right):
    # ctime can settle after a successful SMB write. It is not a content version.
    return all(left.get(key) == right.get(key) for key in ('size', 'mtime_ns', 'inode', 'device'))


#: Очищает имя ресурса от опасных символов и ограничивает длину в UTF-8.
#: Использует (stem + ext).encode, os.path.splitext, re.sub, re.sub('[\\x00-\\x1f/\\\\:]', '_', str(value)).strip.
def safe_name(value):
    value = re.sub(r'[\x00-\x1f/\\:]', '_', str(value)).strip(' .')
    # Leave room for a deterministic collision suffix on common filesystems.
    stem, ext = os.path.splitext(value)
    while len((stem + ext).encode()) > 190:
        stem = stem[:-1]
        if not stem:
            ext = ext[:30]
    return (stem + ext) or 'original'


#: Сохраняет оригинальные ресурсы Photos и продолжает работу по квитанциям метаданных.
#: Зависимости конструктора: libraries, adapter.
class PhotosOriginals:
    #: Инициализирует PhotosOriginals и его рабочее состояние.
    #: Изменяет SQLite-таблицы: photos_original_inventory, photos_original_jobs, photos_original_log, photos_original_resources, photos_original_staging и ещё 1.
    def __init__(self, libraries, adapter):
        self.libraries, self.catalog, self.storage = libraries, libraries.catalog, libraries.storage
        self.adapter = adapter
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self.schedule = None
        self._source_id = None
        self._progress_at = self._validate_at = 0
        self._inventories = {}
        self._validation_link = None
        self._replicas = {}
        with self.catalog._write_lock, self._db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS photos_original_jobs (
                    id TEXT PRIMARY KEY, link_id TEXT NOT NULL REFERENCES photos_copy_links(id),
                    state TEXT NOT NULL, updated_at TEXT NOT NULL, data TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS photos_original_jobs_link ON photos_original_jobs(link_id,updated_at);
                CREATE TABLE IF NOT EXISTS photos_original_resources (
                    job_id TEXT NOT NULL REFERENCES photos_original_jobs(id), asset TEXT NOT NULL,
                    resource TEXT NOT NULL, data TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
                    PRIMARY KEY(job_id,asset,resource));
                CREATE TABLE IF NOT EXISTS photos_original_versions (
                    link_id TEXT NOT NULL, asset TEXT NOT NULL, resource TEXT NOT NULL,
                    version TEXT NOT NULL, fingerprint TEXT NOT NULL,
                    PRIMARY KEY(link_id,asset,resource));
                CREATE TABLE IF NOT EXISTS photos_original_inventory (
                    link_id TEXT NOT NULL, path TEXT NOT NULL, fingerprint TEXT NOT NULL,
                    size INTEGER NOT NULL, sha256 TEXT NOT NULL, seen TEXT NOT NULL,
                    PRIMARY KEY(link_id,path));
                CREATE TABLE IF NOT EXISTS photos_original_staging (
                    job_id TEXT NOT NULL, path TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(job_id,path));
                CREATE TABLE IF NOT EXISTS photos_original_log (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    level TEXT NOT NULL, path TEXT NOT NULL, message TEXT NOT NULL);
            ''')
            # Keep legacy checksum columns for database compatibility, unused.
            columns = {r['name'] for r in db.execute('PRAGMA table_info(photos_original_resources)')}
            if 'seen' not in columns:
                db.execute("ALTER TABLE photos_original_resources ADD COLUMN seen TEXT NOT NULL DEFAULT ''")
            db.execute('DROP INDEX IF EXISTS photos_original_inventory_hash')
            rows = list(db.execute('SELECT id,data FROM photos_original_jobs WHERE state IN (\'manifest\',\'inventory\',\'saving\',\'pausing\')'))
            for row in rows:
                data = json.loads(row['data'])
                data['message'] = 'Сохранение прервано перезапуском. Можно продолжить.'
                db.execute("UPDATE photos_original_jobs SET state='paused',data=?,updated_at=? WHERE id=?", (encoded(data), now(), row['id']))
            jobs = [r[0] for r in db.execute('''SELECT j.id FROM photos_original_jobs j WHERE j.id=(
                SELECT newest.id FROM photos_original_jobs newest WHERE newest.link_id=j.link_id
                ORDER BY newest.updated_at DESC LIMIT 1)''')]
        # Older runs reset the working manifest while receipts remained intact.
        # Restore their progress from SQLite without opening originals.
        for job in jobs:
            self._restore_receipts(job)

    #: Восстанавливает готовность ресурсов по сохранённым версиям и квитанциям SQLite.
    #: Изменяет SQLite-таблицы: photos_original_resources.
    def _restore_receipts(self, job):
        with self.catalog._write_lock, self._db() as db:
            db.execute('''UPDATE photos_original_resources AS r SET state='reused'
                WHERE r.job_id=? AND r.state NOT IN ('saved','reused') AND EXISTS (
                    SELECT 1 FROM photos_original_jobs j JOIN photos_copy_files f ON f.link_id=j.link_id
                    JOIN photos_original_versions v ON v.link_id=f.link_id
                        AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                    WHERE j.id=r.job_id AND f.asset_identifier=r.asset AND f.resource_id=r.resource
                        AND v.version=json_extract(r.data,'$.version'))''', (job,))
        self._update(job, **self._counts(job))

    #: Предоставляет транзакционное соединение каталога с гарантированным закрытием.
    #: Использует connection.close, self.catalog.connect.
    @contextmanager
    def _db(self):
        connection = self.catalog.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    #: Проверяет существование, медиатеку и подключение привязанной копии.
    #: Явно отклоняет недопустимое состояние через KeyError, PhotosLibraryUnavailable.
    def _link(self, link_id, source_id=None):
        with self._db() as db:
            row = db.execute('SELECT * FROM photos_copy_links WHERE id=?', (link_id,)).fetchone()
        if not row or (source_id is not None and row['source_id'] != source_id):
            raise KeyError('Копия медиатеки не найдена')
        if not row['connected']:
            raise PhotosLibraryUnavailable('Папка копии отвязана')
        return dict(row)

    #: Возвращает последнее состояние копии с незавершёнными файлами и расписанием.
    #: Читает SQLite-таблицы: photos_original_jobs, photos_original_staging.
    def summary(self, link_id, *, raw=False):
        with self._db() as db:
            row = db.execute('SELECT * FROM photos_original_jobs WHERE link_id=? ORDER BY updated_at DESC LIMIT 1', (link_id,)).fetchone()
        if not row:
            result = dict(state='idle', done_assets=0, total_assets=0, message='Сохранение ещё не запускалось')
            return self.schedule.decorate(self.libraries.root_copy(link_id), result) if self.schedule and not raw else result
        with self._db() as db:
            incomplete = db.execute("SELECT COUNT(*) FROM photos_original_staging s JOIN photos_original_jobs j ON j.id=s.job_id WHERE j.link_id=? AND json_extract(s.data,'$.final')=1", (link_id,)).fetchone()[0]
        result = dict(json.loads(row['data']), id=row['id'], state=row['state'], updated_at=row['updated_at'], incomplete_files=incomplete)
        return self.schedule.decorate(self.libraries.root_copy(link_id), result) if self.schedule and not raw else result

    #: Возвращает последние события задания и пути незавершённых конечных файлов.
    #: Поля результата: job, items, incomplete_paths.
    def journal(self, link_id, source_id=None):
        self._link(link_id, source_id)
        job = self.summary(link_id)
        with self._db() as db:
            rows = [dict(r) for r in db.execute('SELECT created_at,level,path,message FROM photos_original_log WHERE job_id=? ORDER BY id DESC LIMIT 200', (job.get('id', ''),))]
            incomplete = [r[0] for r in db.execute("SELECT s.path FROM photos_original_staging s JOIN photos_original_jobs j ON j.id=s.job_id WHERE j.link_id=? AND json_extract(s.data,'$.final')=1 ORDER BY s.path", (link_id,))]
        return dict(job=job, items=rows, incomplete_paths=incomplete)

    #: Обновляет состояние и JSON-поля задания сохранения оригиналов.
    #: Изменяет SQLite-таблицы: photos_original_jobs.
    def _update(self, job, state=None, **values):
        with self.catalog._write_lock, self._db() as db:
            row = db.execute('SELECT state,data FROM photos_original_jobs WHERE id=?', (job,)).fetchone()
            data = dict(json.loads(row['data']), **values)
            db.execute('UPDATE photos_original_jobs SET state=?,data=?,updated_at=? WHERE id=?', (state or row['state'], encoded(data), now(), job))

    #: Добавляет событие оригиналов с уровнем, путём и временем.
    #: Изменяет SQLite-таблицы: photos_original_log.
    def _log(self, job, level, path, message):
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT INTO photos_original_log(job_id,created_at,level,path,message) VALUES (?,?,?,?,?)', (job, now(), level, path, message))

    #: Возвращает доступный том копии из уже обнаруженного состояния.
    #: Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
    def _volume(self, link):
        volume = next((v for v in self.storage.refresh(cached_only=True)['volumes'] if v['id'] == link['volume_id']), None)
        if not volume or volume['availability'] != 'online':
            raise PhotosLibraryUnavailable('Том копии отключён. Подключи его и продолжи сохранение.')
        return volume

    #: Запускает или продолжает корневую цепочку сохранения с учётом расписания.
    #: Изменяет SQLite-таблицы: photos_original_jobs.
    def start(self, link_id, source_id=None, *, background=True, _scheduled=False):
        root_id = self.libraries.root_copy(link_id)
        if root_id != link_id:
            self._link(link_id, source_id)
            return self.start(root_id, source_id, background=background, _scheduled=_scheduled)
        if self.schedule and not _scheduled:
            link = self._link(link_id, source_id)
            if self.schedule.settings(link['source_id'])['night_only'] or self.schedule.manages(link_id):
                return self.schedule.request(link_id, source_id)
        with self._lock:
            if self._thread and self._thread.is_alive():
                raise ValueError('Сначала приостанови текущее сохранение оригиналов')
            link = self._link(link_id, source_id)
            self._source_id = link['source_id']
            if self.schedule and self.schedule.blocked(self._source_id):
                raise PhotosLibraryUnavailable('Сохранение ожидает ночного окна')
            self.libraries._require_active(link['source_id'])
            volume = self._volume(link)
            with open_readonly(volume, link['path'], directory=True) as fd:
                root = object_id(os.fstat(fd))
            previous = self.summary(link_id, raw=True)
            if previous.get('id'):
                job = previous['id']
                if previous['root'] != root:
                    raise ValueError('Привязанная папка была заменена. Проверь привязку перед сохранением.')
                self._restore_receipts(job)
                self._update(job, state='manifest', message='Читаю список оригиналов Photos', current_path='', current_bytes=0, fraction=0, errors=0,
                             write_buffer_bytes=WRITE_BUFFER_BYTES, buffered_bytes=0, written_bytes=0, write_batches=0)
            else:
                job = uuid4().hex
                data = dict(root=root, done_assets=0, total_assets=0, done_resources=0, total_resources=0,
                            saved=0, reused=0, errors=0, checked_files=0, checked_bytes=0,
                            current_path='', current_bytes=0, fraction=0, message='Читаю список оригиналов Photos')
                data.update(write_buffer_bytes=WRITE_BUFFER_BYTES, buffered_bytes=0, written_bytes=0, write_batches=0)
                with self.catalog._write_lock, self._db() as db:
                    db.execute('INSERT INTO photos_original_jobs VALUES (?,?,?,?,?)', (job, link_id, 'manifest', now(), encoded(data)))
            self._stop.clear()
            self._replicas = {}
            self._inventories = {}
            self._validate_at = 0
            self._log(job, 'info', '', 'Начато сохранение оригиналов в привязанную копию')
            if background:
                self._thread = threading.Thread(target=self.run, args=(job, link), name='photos-originals', daemon=True)
                self._thread.start()
        if not background:
            self.run(job, link)
        return self.summary(link_id)

    #: Ставит корневую цепочку на паузу и при ручном вызове снимает запрос расписания.
    #: Использует self._link, self._stop.set, self._update, self.libraries.root_copy, self.schedule.cancel.
    def pause(self, link_id, source_id=None, *, _scheduled=False):
        with self._lock:
            self._link(link_id, source_id)
            link_id = self.libraries.root_copy(link_id)
            if self.schedule and not _scheduled:
                self.schedule.cancel(link_id)
            job = self.summary(link_id)
            if job['state'] in ACTIVE:
                self._stop.set()
                self._update(job['id'], state='pausing', message='Приостанавливаю сохранение…')
        return self.summary(link_id)

    #: Запрашивает остановку воркера оригиналов при завершении Core.
    #: Использует self._stop.set, self._thread.join.
    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)
        # The worker closes its own channel after cancellation. Never block on
        # its operation lock while an unavailable network disk is unwinding.

    #: Прерывает передачу при ручной остановке или закрытии разрешённого окна.
    #: Явно отклоняет недопустимое состояние через PhotosTransferStopped.
    def _check(self):
        if self._stopped():
            raise PhotosTransferStopped('Сохранение приостановлено')

    #: Проверяет ручной флаг остановки и временное окно медиатеки.
    #: Использует self._stop.is_set, self.schedule.blocked.
    def _stopped(self):
        return self._stop.is_set() or bool(self.schedule and self._source_id is not None
                                          and self.schedule.blocked(self._source_id))

    #: Проверяет актуальность привязки, активность медиатеки, том и корневую папку.
    #: Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
    def _validate(self, job, link, volume, *, force=False):
        self._check()
        if not force and self._validation_link == link['id'] and time.monotonic() - self._validate_at < .5:
            return
        current = self._link(link['id'])
        if current != link:
            raise PhotosLibraryUnavailable('Привязка папки изменилась')
        self.libraries._require_active(link['source_id'])
        current_volume = self._volume(link)
        if any(current_volume.get(k) != volume.get(k) for k in ('mount_path', 'device', 'marker_id')):
            raise PhotosLibraryUnavailable('Том копии изменился')
        with open_readonly(volume, link['path'], directory=True) as fd:
            if object_id(os.fstat(fd)) != self.summary(link['id'])['root']:
                raise PhotosLibraryUnavailable('Привязанная папка была заменена')
        self._validate_at = time.monotonic()
        self._validation_link = link['id']

    #: Сохраняет промежуточный прогресс с ограничением частоты обновлений.
    #: Обновляет состояние объекта: _progress_at.
    def _progress(self, job, **values):
        if time.monotonic() - self._progress_at > .5:
            self._update(job, **values)
            self._progress_at = time.monotonic()

    #: Открывает готовый ресурс внутри папки копии только для чтения.
    #: Использует PurePosixPath, open_readonly.
    @contextmanager
    def _file(self, volume, link, path):
        with open_readonly(volume, str(PurePosixPath(link['path']) / path)) as fd:
            yield fd

    #: Сохраняет параметры и поколение обнаруженного файла назначения.
    #: Изменяет SQLite-таблицы: photos_original_inventory.
    def _inventory_record(self, link, path, fp, seen):
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_original_inventory VALUES (?,?,?,?,?,?)',
                       (link['id'], path, encoded(fp), fp['size'], '', seen))

    #: Удаляет подтверждённые старые временные файлы, сохраняя конечные незавершённые пути.
    #: Изменяет SQLite-таблицы: photos_original_staging.
    def _cleanup(self, job, link, volume):
        with self._db() as db:
            rows = list(db.execute('SELECT * FROM photos_original_staging WHERE job_id IN (SELECT id FROM photos_original_jobs WHERE link_id=?)', (link['id'],)))
        for row in rows:
            data = json.loads(row['data'])
            if data.get('final'):
                continue  # Never remove final paths, including interrupted SMB writes.
            path = PurePosixPath(row['path'])
            self._validate(job, link, volume, force=True)
            try:
                with destination_directory(volume, link, str(path.parent) if path.parent != PurePosixPath('.') else '') as parent:
                    info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode) or object_id(info) != data['identity']:
                        raise OSError('Промежуточный файл заменён; оставлен для ручной проверки: ' + str(path))
                    os.unlink(path.name, dir_fd=parent)
            except FileNotFoundError:
                pass
            with self.catalog._write_lock, self._db() as db:
                db.execute('DELETE FROM photos_original_staging WHERE job_id=? AND path=?', (row['job_id'], row['path']))

    #: Индексирует имена и stat-параметры файлов копии без чтения содержимого.
    #: Изменяет SQLite-таблицы: photos_original_inventory.
    def _inventory(self, job, link, volume):
        self._update(job, state='inventory', message='Сверяю параметры файлов', checked_files=0, checked_bytes=0)
        inventory = self._inventories[link['id']] = dict(files={}, names={}, recorded=set())
        with self._db() as db:
            inventory['recorded'] = {r[0] for r in db.execute('SELECT path FROM photos_copy_files WHERE link_id=?', (link['id'],))}
        generation = uuid4().hex
        with self._db() as db:
            incomplete = {r['path'] for r in db.execute('SELECT path FROM photos_original_staging WHERE job_id IN (SELECT id FROM photos_original_jobs WHERE link_id=?)', (link['id'],))}
        count = size = 0
        #: Рекурсивно перечисляет обычные файлы и папки копии через дескрипторы.
        #: Явно отклоняет недопустимое состояние через OSError.
        def walk(fd, prefix=''):
            nonlocal count, size
            with os.scandir(fd) as entries:
                for entry in entries:
                    self._validate(job, link, volume)
                    name = entry.name
                    if name.startswith(('.media-actu-', '._')) or name == '.DS_Store':
                        continue
                    path = str(PurePosixPath(prefix) / name)
                    if path in incomplete:
                        continue
                    info = entry.stat(follow_symlinks=False)
                    if info.st_dev != os.fstat(fd).st_dev:
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                        try:
                            if os.fstat(child).st_dev != os.fstat(fd).st_dev:
                                raise OSError('Переход на другой том запрещён')
                            walk(child, path)
                        finally:
                            os.close(child)
                    elif stat.S_ISREG(info.st_mode):
                        fp = fingerprint(info)
                        inventory['files'][path] = fp
                        inventory['names'].setdefault(name_key(name), []).append(path)
                        self._inventory_record(link, path, fp, generation)
                        count += 1; size += fp['size']
                        self._progress(job, checked_files=count, checked_bytes=size, current_path=path)
        with open_readonly(volume, link['path'], directory=True) as fd:
            walk(fd)
        with self.catalog._write_lock, self._db() as db:
            db.execute('DELETE FROM photos_original_inventory WHERE link_id=? AND seen<>?', (link['id'], generation))
        self._update(job, checked_files=count, checked_bytes=size)

    #: Фиксирует готовый ресурс, версию, параметры файла и завершение записи.
    #: Изменяет SQLite-таблицы: photos_copy_files, photos_original_resources, photos_original_staging, photos_original_versions.
    def _receipt(self, job, link, asset, resource, version, path, fp, reused):
        self._validate(job, link, self._volume(link), force=True)
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_copy_files VALUES (?,?,?,?,?,?,?)', (link['id'], asset, resource, path, fp['size'], '', now()))
            db.execute('INSERT OR REPLACE INTO photos_original_versions VALUES (?,?,?,?,?)', (link['id'], asset, resource, version, encoded(fp)))
            db.execute("UPDATE photos_original_resources SET state=? WHERE job_id=? AND asset=? AND resource=?", ('reused' if reused else 'saved', job, asset, resource))
            db.execute('DELETE FROM photos_original_staging WHERE job_id=? AND path=?', (job, path))
        if link['id'] in self._inventories:
            self._inventories[link['id']]['recorded'].add(path)
        self._inventory_record(link, path, fp, job)

    #: Принимает готовый ресурс повторно после проверки версии и параметров файла.
    #: Обрабатывает ошибки: FileNotFoundError.
    def _reuse_receipt(self, job, link, volume, asset, resource, version):
        with self._db() as db:
            row = db.execute('''SELECT f.*,v.version,v.fingerprint FROM photos_copy_files f JOIN photos_original_versions v
                ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                WHERE f.link_id=? AND f.asset_identifier=? AND f.resource_id=?''', (link['id'], asset, resource)).fetchone()
        if not row or row['version'] != version:
            return False
        try:
            with self._file(volume, link, row['path']) as fd:
                fp = fingerprint(os.fstat(fd))
        except FileNotFoundError:
            return False
        if fp['size'] != row['size'] or not same_file(fp, json.loads(row['fingerprint'])):
            return False
        self._receipt(job, link, asset, resource, version, row['path'], fp, True)
        return True

    #: Журналирует созданный путь и его идентичность до передачи содержимого.
    #: Изменяет SQLite-таблицы: photos_original_staging.
    def _stage(self, job, path, identity, final=False):
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_original_staging VALUES (?,?,?)', (job, path, encoded(dict(identity=identity, final=final))))

    #: Исключительно создаёт свободное конечное имя и фиксирует намерение записи.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _create_original(self, job, link, volume, parent, parent_path, name):
        # Collision names do not depend on a file's position in an enumeration.
        for index in range(10000):
            candidate = name if index == 0 else f'{os.path.splitext(name)[0]}-{index}{os.path.splitext(name)[1]}'
            path = str(PurePosixPath(parent_path) / candidate)
            self._validate(job, link, volume, force=True)
            with destination_directory(volume, link, parent_path) as current:
                if object_id(os.fstat(current)) != object_id(os.fstat(parent)):
                    raise OSError('Целевая папка заменена')
            try:
                fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=parent)
            except FileExistsError:
                continue
            try:
                identity = object_id(os.fstat(fd))
                # The intent is durable before the first byte is written.
                self._stage(job, path, identity, final=True)
            except BaseException:
                os.close(fd)
                raise
            return fd, path, identity
        raise OSError('Не удалось выбрать свободное имя оригинала')

    #: Полностью записывает блок через memoryview с проверкой остановки.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _write(self, fd, chunk):
        view = memoryview(chunk)
        try:
            while view:
                self._check()
                written = os.write(fd, view)
                if written <= 0:
                    raise OSError('Не удалось записать оригинал')
                remaining = view[written:]
                view.release()
                view = remaining
        finally:
            view.release()

    #: Ищет квитанцию подходящего ресурса в разрешённой копии-источнике.
    #: Читает SQLite-таблицы: photos_copy_files, photos_copy_links, photos_original_versions.
    def _peer(self, link, item):
        upstream = self.libraries.copy_source(link['id'])
        with self._db() as db:
            rows = list(db.execute('''SELECT f.*,v.version,v.fingerprint,l.number FROM photos_copy_files f
                JOIN photos_original_versions v ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                JOIN photos_copy_links l ON l.id=f.link_id
                WHERE l.source_id=? AND f.link_id<>? AND f.asset_identifier=? AND f.resource_id=? AND v.version=?
                  AND (? IS NULL OR f.link_id=?) ORDER BY l.number''',
                (link['source_id'],link['id'],item['asset'],item['resource'],item['version'],upstream,upstream)))
        return dict(rows[0]) if rows else None

    #: Передаёт готовый оригинал из другой копии с проверками источника.
    #: Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
    def _stream_peer(self, peer, write):
        source = self._link(peer['link_id'])
        volume = self._volume(source)
        job = self.summary(source['id'], raw=True)
        expected = json.loads(peer['fingerprint'])
        #: Проверяет остановку, привязку, том и корень копии-источника между блоками.
        #: Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
        def check():
            self._check()
            if self._link(source['id']) != source:
                raise PhotosLibraryUnavailable('Источник копирования изменился')
            current = self._volume(source)
            if any(current.get(k) != volume.get(k) for k in ('mount_path','device','marker_id')):
                raise PhotosLibraryUnavailable('Том источника копирования изменился')
            with open_readonly(volume,source['path'],directory=True) as root:
                if job.get('root') and object_id(os.fstat(root)) != job['root']:
                    raise PhotosLibraryUnavailable('Папка источника копирования заменена')
        check()
        try:
            with self._file(volume,source,peer['path']) as fd:
                if not same_file(fingerprint(os.fstat(fd)),expected) or os.fstat(fd).st_size != peer['size']:
                    raise PhotosLibraryUnavailable('Параметры сохранённого оригинала изменились: ' + peer['path'])
                count = 0
                while chunk := os.read(fd,WRITE_BUFFER_BYTES):
                    check()
                    write(chunk)
                    count += len(chunk)
                check()
                if not same_file(fingerprint(os.fstat(fd)),expected):
                    raise PhotosLibraryUnavailable('Источник изменился во время копирования: ' + peer['path'])
                return dict(size=count)
        except FileNotFoundError as error:
            raise PhotosLibraryUnavailable('Сохранённый оригинал отсутствует в копии: ' + peer['path']) from error
        except OSError as error:
            raise PhotosLibraryUnavailable('Не удалось передать оригинал из копии: ' + str(error)) from error

    #: Повторно использует ресурс либо сохраняет поток в новый конечный файл.
    #: Буфер ограничен 64 МиБ; после fsync проверяются размер и ID без чтения содержимого.
    def _save(self, job, link, volume, profile, item):
        asset, resource, version = item['asset'], item['resource'], item['version']
        if self._reuse_receipt(job, link, volume, asset, resource, version):
            return 'reused'
        peer = self._peer(link,item)
        if not peer and self.libraries.copy_source(link['id']):
            raise PhotosLibraryUnavailable('Ожидаю готовый оригинал в копии-источнике')
        source_label = f"{peer['number']:02d}-copy" if peer else 'Photos'
        self._update(job,current_source=source_label)
        created = item.get('created_at', '')
        try:
            date = datetime.fromisoformat(created.replace('Z', '+00:00'))
            parent_path = f'{date.year:04d}/{date.year:04d}-{date.month:02d}'
        except ValueError:
            parent_path = 'Без даты'
        name = safe_name(item['name'])
        if peer:
            path = PurePosixPath(peer['path'])
            parent_path = '' if str(path.parent)=='.' else str(path.parent)
            name = safe_name(path.name)
        with destination_directory(volume, link, parent_path, create=True) as parent:
            fd, path, identity = None, None, None
            buffer = bytearray()
            count = written = batches = 0
            space_at, space_left = None, 0

            #: Проверяет свободное место и записывает накопленный буфер в конечный файл.
            #: Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
            def flush():
                nonlocal fd, path, identity, written, batches, space_at, space_left
                if not buffer:
                    return
                self._validate(job, link, volume)
                instant = time.monotonic()
                if space_at is None or instant - space_at >= SPACE_CHECK_SECONDS or space_left < len(buffer) + SPACE_RESERVE_BYTES:
                    capacity = os.fstatvfs(parent)
                    space_left = capacity.f_bavail * (capacity.f_frsize or capacity.f_bsize)
                    space_at = instant
                if space_left < len(buffer) + SPACE_RESERVE_BYTES:
                    raise PhotosLibraryUnavailable('Недостаточно свободного места в папке копии. Освободи место и продолжи.')
                if fd is None:
                    fd, path, identity = self._create_original(job, link, volume, parent, parent_path, name)
                self._write(fd, buffer)
                written += len(buffer)
                space_left -= len(buffer)
                batches += 1
                buffer.clear()
                self._progress(job, current_bytes=count, buffered_bytes=0, written_bytes=written, write_batches=batches)

            #: Разбивает принятые данные на ограниченный буфер и публикует прогресс.
            #: Использует buffer.extend, flush, memoryview, self._check, self._progress.
            def write(chunk):
                nonlocal count
                self._validate(job, link, volume)
                view = memoryview(chunk)
                try:
                    while view:
                        self._check()
                        take = min(len(view), WRITE_BUFFER_BYTES - len(buffer))
                        buffer.extend(view[:take])
                        count += take
                        remaining = view[take:]
                        view.release()
                        view = remaining
                        if len(buffer) == WRITE_BUFFER_BYTES:
                            flush()
                finally:
                    view.release()
                self._progress(job, current_bytes=count, buffered_bytes=len(buffer), written_bytes=written, write_batches=batches)
            try:
                trailer = (self._stream_peer(peer,write) if peer else
                    self.adapter.stream_original(asset, resource, version, profile['anchors'], write,
                    lambda fraction: self._progress(job, fraction=fraction, current_bytes=count), self._stopped))
                if trailer.get('size') != count or count == 0:
                    raise PhotosAdapterError('Размер переданного оригинала не совпал')
                self._check()
                # A small manual copy can be adopted before any destination is
                # created. Once writing starts, that new file is the result.
                inventory = self._inventories.get(link['id'],dict(files={},names={},recorded=set()))
                candidates = [path for path in inventory['names'].get(name_key(item['name']), [])
                              if path not in inventory['recorded'] and inventory['files'][path]['size'] == count]
                # Ambiguous manually exported names are left untouched.
                if fd is not None or len(candidates) != 1:
                    candidates = []
                for candidate in candidates:
                    try:
                        with self._file(volume, link, candidate) as existing:
                            existing_fp = fingerprint(os.fstat(existing))
                        if same_file(existing_fp, inventory['files'][candidate]):
                            self._receipt(job, link, asset, resource, version, candidate, existing_fp, True)
                            return 'reused'
                    except FileNotFoundError:
                        continue
                flush()
                os.fsync(fd)
                if os.fstat(fd).st_size != count:
                    raise OSError('Размер записанного оригинала не совпал')
                completed_fd, fd = fd, None
                os.close(completed_fd)
                self._validate(job, link, volume, force=True)
                with self._file(volume, link, path) as metadata:
                    info = os.fstat(metadata)
                    if object_id(info) != identity or info.st_size != count:
                        raise OSError('Записанный оригинал заменён или изменился')
                    final_fp = fingerprint(info)
                self._receipt(job, link, asset, resource, version, path, final_fp, False)
                self._update(job, current_bytes=count, buffered_bytes=0, written_bytes=written, write_batches=batches)
                return 'saved'
            finally:
                # Interrupted final files remain journalled and are never
                # deleted, adopted by inventory, or opened for another write.
                if fd is not None:
                    os.close(fd)
                buffer.clear()

    #: Пересчитывает готовые объекты и ресурсы по состояниям манифеста.
    #: Читает SQLite-таблицы: photos_original_resources.
    def _counts(self, job):
        with self._db() as db:
            row = db.execute('''SELECT COUNT(*) total_resources,
                COALESCE(SUM(state IN ('saved','reused')),0) done_resources,
                COALESCE(SUM(state='saved'),0) saved,COALESCE(SUM(state='reused'),0) reused,
                COALESCE(SUM(state='error'),0) errors FROM photos_original_resources WHERE job_id=?''', (job,)).fetchone()
            assets = db.execute('''SELECT COUNT(*) total_assets,COALESCE(SUM(ready),0) done_assets FROM
                (SELECT asset,MIN(state IN ('saved','reused')) ready FROM photos_original_resources WHERE job_id=? GROUP BY asset)''', (job,)).fetchone()
        return dict(row) | dict(assets)

    #: Подготавливает задание зависимой копии и сверяет её квитанции с манифестом.
    #: Изменяет SQLite-таблицы: photos_original_jobs, photos_original_resources.
    def _prepare_replica(self, parent_job, link):
        volume = self._volume(link)
        with open_readonly(volume,link['path'],directory=True) as fd:
            root = object_id(os.fstat(fd))
        previous = self.summary(link['id'],raw=True)
        if previous.get('id'):
            if previous['root'] != root:
                raise PhotosLibraryUnavailable('Папка копии заменена: ' + link['path'])
            job = previous['id']
        else:
            job = uuid4().hex
            data = dict(root=root,done_assets=0,total_assets=0,done_resources=0,total_resources=0,
                        saved=0,reused=0,errors=0,current_bytes=0,current_path='',fraction=0)
            with self.catalog._write_lock,self._db() as db:
                db.execute('INSERT INTO photos_original_jobs VALUES (?,?,?,?,?)',(job,link['id'],'inventory',now(),encoded(data)))
        self._cleanup(job,link,volume)
        self._inventory(job,link,volume)
        inventory = self._inventories[link['id']]['files']
        with self._db() as db:
            rows = [dict(r) for r in db.execute('SELECT asset,resource,data FROM photos_original_resources WHERE job_id=?',(parent_job,))]
            receipts = {(r['asset_identifier'],r['resource_id']):dict(r) for r in db.execute('''
                SELECT f.*,v.version,v.fingerprint FROM photos_copy_files f JOIN photos_original_versions v
                ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id WHERE f.link_id=?''',(link['id'],))}
        generation = uuid4().hex
        with self.catalog._write_lock,self._db() as db:
            for row in rows:
                item = json.loads(row['data'])
                receipt = receipts.get((row['asset'],row['resource']))
                fp = inventory.get(receipt['path']) if receipt else None
                ready = bool(fp and receipt['version']==item['version'] and fp['size']==receipt['size']
                             and same_file(fp,json.loads(receipt['fingerprint'])))
                db.execute('''INSERT INTO photos_original_resources(job_id,asset,resource,data,state,seen) VALUES (?,?,?,?,?,?)
                    ON CONFLICT(job_id,asset,resource) DO UPDATE SET data=excluded.data,state=excluded.state,seen=excluded.seen''',
                    (job,row['asset'],row['resource'],row['data'],'reused' if ready else 'pending',generation))
            db.execute('DELETE FROM photos_original_resources WHERE job_id=? AND seen<>?',(job,generation))
        self._update(job,state='waiting_primary',message='Ожидаю новые оригиналы из копии-источника',**self._counts(job))
        return job,volume

    #: Дополняет зависимые копии готовыми ресурсами в порядке источников.
    #: Обрабатывает ошибки: (OSError, ValueError, PhotosAdapterError, KeyError), PhotosTransferStopped.
    def _replicate_all(self, master_job, master):
        with self._db() as db:
            links = {r['id']:dict(r) for r in db.execute('SELECT * FROM photos_copy_links WHERE source_id=? AND connected=1',(master['source_id'],))}
            edges = dict(db.execute('SELECT link_id,source_link_id FROM photos_copy_sources'))
        jobs = {master['id']:master_job}
        remaining = set(links)-{master['id']}
        while remaining:
            eligible = sorted((identifier for identifier in remaining if edges.get(identifier) in jobs),key=lambda identifier:links[identifier]['number'])
            if not eligible:
                break
            for identifier in eligible:
                self._check()
                remaining.remove(identifier)
                link,upstream = links[identifier],edges[identifier]
                job = None
                try:
                    if identifier not in self._replicas:
                        self._replicas[identifier] = self._prepare_replica(jobs[upstream],link)
                    job,volume = self._replicas[identifier]
                    jobs[identifier] = job
                    with self._db() as db:
                        rows = [dict(r) for r in db.execute('''SELECT r.asset,r.resource,r.data FROM photos_original_resources r
                            JOIN photos_copy_files f ON f.link_id=? AND f.asset_identifier=r.asset AND f.resource_id=r.resource
                            JOIN photos_original_versions v ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                            WHERE r.job_id=? AND r.state NOT IN ('saved','reused') AND v.version=json_extract(r.data,'$.version')
                            ORDER BY f.path,r.asset,r.resource''',(upstream,job))]
                    if rows:
                        self._update(job,state='saving',message=f"Копирую из {links[upstream]['number']:02d}-copy",errors=0)
                    for row in rows:
                        self._validate(job,link,volume)
                        item = json.loads(row['data'])
                        self._update(job,current_path=item['name'],current_bytes=0,fraction=0,buffered_bytes=0,written_bytes=0,write_batches=0)
                        self._save(job,link,volume,None,item)
                        self._update(job,**self._counts(job))
                    counts = self._counts(job)
                    complete = counts['done_resources']==counts['total_resources']
                    self._update(job,state='completed' if complete else 'waiting_primary',current_path='',current_bytes=0,buffered_bytes=0,
                        message='Копия дополнена из источника' if complete else f"Ожидаю новые оригиналы из {links[upstream]['number']:02d}-copy",**counts)
                except PhotosTransferStopped:
                    stopped_job = job or self.summary(identifier,raw=True).get('id')
                    if stopped_job:
                        self._update(stopped_job,state='paused',message='Сохранение приостановлено',current_bytes=0,buffered_bytes=0,**self._counts(stopped_job))
                    raise
                except (OSError,ValueError,PhotosAdapterError,KeyError) as error:
                    current = self.summary(identifier,raw=True)
                    if current.get('id'):
                        self._update(current['id'],state='waiting',message=str(error),current_bytes=0,buffered_bytes=0)
                        self._log(current['id'],'error','',str(error))

    #: Обновляет манифест, сохраняет недостающие ресурсы и обслуживает цепочку копий.
    #: Изменяет SQLite-таблицы: photos_original_resources.
    def run(self, job, link):
        state, message = 'completed', 'Оригиналы сохранены'
        manifest_ready = False
        try:
            volume = self._volume(link)
            self._validate(job, link, volume, force=True)
            profile = self.libraries._require_active(link['source_id'])
            self._cleanup(job, link, volume)
            self._inventory(job, link, volume)
            with self._db() as db:
                receipts = {(r['asset_identifier'], r['resource_id']): dict(r) for r in db.execute('''
                    SELECT f.*,v.version,v.fingerprint FROM photos_copy_files f
                    JOIN photos_original_versions v ON v.link_id=f.link_id
                        AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                    WHERE f.link_id=?''', (link['id'],))}
            self._update(job, state='manifest', message='Обновляю список оригиналов Photos', current_path='')
            generation = uuid4().hex
            received = 0
            #: Сохраняет ресурсы поступившего объекта манифеста и восстанавливает готовность.
            #: Изменяет SQLite-таблицы: photos_original_resources.
            def asset_received(asset):
                nonlocal received
                self._validate(job, link, volume)
                resources = asset.get('resources') or [dict(id='missing', name=asset.get('name', 'original'), error='Photos не вернула оригинальные ресурсы')]
                with self.catalog._write_lock, self._db() as db:
                    for resource in resources:
                        item = dict(resource, asset=asset['id'], resource=resource['id'], version=asset['version'], created_at=asset.get('created_at', ''))
                        receipt = receipts.get((asset['id'], resource['id']))
                        fp = self._inventories[link['id']]['files'].get(receipt['path']) if receipt else None
                        ready = bool(fp and not item.get('error') and receipt['version'] == asset['version'] and fp['size'] == receipt['size']
                                     and same_file(fp, json.loads(receipt['fingerprint'])))
                        db.execute('''INSERT INTO photos_original_resources(job_id,asset,resource,data,state,seen)
                            VALUES (?,?,?,?,?,?) ON CONFLICT(job_id,asset,resource) DO UPDATE
                            SET data=excluded.data,state=excluded.state,seen=excluded.seen''',
                            (job, asset['id'], resource['id'], encoded(item), 'reused' if ready else 'pending', generation))
                received += 1
                self._progress(job, message=f'Обновляю список оригиналов Photos · {received:,}'.replace(',', ' '))
            self.adapter.original_manifest(profile['anchors'], asset_received, self._stopped)
            # A partial/interrupted manifest never removes older progress.
            with self.catalog._write_lock, self._db() as db:
                db.execute('DELETE FROM photos_original_resources WHERE job_id=? AND seen<>?', (job, generation))
            manifest_ready = True
            counters = self._counts(job)
            self._update(job, **counters)
            self._update(job, state='saving', message='Сохраняю оставшиеся оригиналы', current_path='')
            self._replicate_all(job,link)
            # Restore known copies first, ordered by folder/date. No PhotoKit
            # resource transfer starts until the existing copies are imported.
            with self._db() as db:
                work = [dict(row) for row in db.execute('''SELECT r.asset,r.resource,r.data FROM photos_original_resources r
                    WHERE r.job_id=? AND r.state NOT IN ('saved','reused') ORDER BY EXISTS (
                        SELECT 1 FROM photos_copy_files f JOIN photos_original_versions v ON v.link_id=f.link_id
                            AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                        JOIN photos_copy_links l ON l.id=f.link_id
                        WHERE l.source_id=? AND l.id<>? AND f.asset_identifier=r.asset AND f.resource_id=r.resource
                            AND v.version=json_extract(r.data,'$.version')) DESC,
                    json_extract(r.data,'$.created_at'),r.asset,r.resource''',(job,link['source_id'],link['id']))]
            for index,row in enumerate(work,1):
                self._validate(job, link, volume)
                item = json.loads(row['data'])
                self._update(job, current_path=item['name'], current_bytes=0, fraction=0,
                             buffered_bytes=0, written_bytes=0, write_batches=0)
                try:
                    if item.get('error'):
                        raise PhotosAdapterError(item['error'])
                    result = self._save(job, link, volume, profile, item)
                    counters[result] += 1
                    counters['done_resources'] += 1
                    with self._db() as db:
                        ready = db.execute("SELECT MIN(state IN ('saved','reused')) FROM photos_original_resources WHERE job_id=? AND asset=?", (job, item['asset'])).fetchone()[0]
                    if ready:
                        counters['done_assets'] += 1
                except (PhotosTransferStopped, PhotosLibraryUnavailable, PhotosAccessDenied):
                    raise
                except (OSError, PhotosAdapterError, ValueError) as error:
                    # A disconnected/replaced destination stops the whole job.
                    self._validate(job, link, volume, force=True)
                    with self.catalog._write_lock, self._db() as db:
                        db.execute("UPDATE photos_original_resources SET state='error' WHERE job_id=? AND asset=? AND resource=?", (job, row['asset'],row['resource']))
                    self._log(job, 'error', item['name'], str(error))
                    counters['errors'] += 1
                self._update(job, **counters)
                if index % COPY_BATCH_RESOURCES == 0:
                    self._replicate_all(job,link)
            self._replicate_all(job,link)
            if self._counts(job)['errors']:
                state, message = 'completed_with_errors', 'Часть оригиналов не сохранена. Ошибки — в журнале; можно повторить.'
        except PhotosTransferStopped:
            state, message = 'paused', 'Сохранение приостановлено. Готовые оригиналы сохранены.'
        except (PhotosLibraryUnavailable, PhotosAccessDenied) as error:
            state, message = 'waiting', str(error)
        except Exception as error:
            state, message = 'failed', str(error)
        finally:
            self.adapter.close()
            incomplete = self.summary(link['id']).get('incomplete_files', 0)
            if incomplete:
                message += f' · Незавершённых файлов в копии: {incomplete}; пути — в журнале.'
            counts = self._counts(job) if manifest_ready else {}
            self._update(job, state=state, message=message, current_path='', current_bytes=0, fraction=0, buffered_bytes=0, **counts)
            with self._db() as db:
                unfinished = [r[0] for r in db.execute('''SELECT j.id FROM photos_original_jobs j
                    JOIN photos_copy_links l ON l.id=j.link_id WHERE l.source_id=? AND j.id<>?
                    AND j.state IN ('manifest','inventory','saving','pausing')''',(link['source_id'],job))]
            for child in unfinished:
                self._update(child,state='paused' if state=='paused' else 'waiting',
                             message='Цепочка остановлена: ' + message,current_bytes=0,buffered_bytes=0)
            self._log(job, 'error' if state in ('failed', 'waiting', 'completed_with_errors') else 'info', '', message)
