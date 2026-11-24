"""Durable, missing-only copies of files from the macOS iCloud Drive."""
from __future__ import annotations

from contextlib import closing, contextmanager
import errno
import json
import os
from pathlib import Path, PurePosixPath
import select
import stat
import subprocess
import sys
import threading
import time
from uuid import uuid4

from .comparison import fingerprint, open_readonly
from .copy_files import CopyStopped, DirectCopyRequired, MissingCopyCatalog, destination_directory, object_id, publish_exclusive
from .storage import StorageCatalog, now, relative_path
from .volume_identity import service_file

ICLOUD_VOLUME_ID = 'icloud-drive'
READ_TIMEOUT = 45
PUBLISH_UNSUPPORTED = {errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS, errno.EINVAL}
CLOUD_BATCH_BYTES = 1024**3
CLOUD_BATCH_FILES = 8
CLOUD_DISK_RESERVE = 2 * 1024**3
CLOUD_IN_PROGRESS = ('reserved', 'requested', 'external', 'copying', 'evict_pending')


#: Откладывает путь, пока iCloud работает или освободится место в пакете.
#: Пауза ожидания не увеличивает интервал обработки обычных ошибок.
class CloudPending(OSError):
    #: Передаёт причину ожидания и задержку до допустимой повторной проверки.
    #: Нулевая задержка передаёт управление проверке вместимости в очереди.
    def __init__(self, message, *, delay=5):
        super().__init__(message)
        self.delay = delay


#: Читает системный признак отсутствующего содержимого из метаданных файла.
#: Использует значение Darwin SF_DATALESS из sys/stat.h.
def cloud_dataless(info):
    return bool(getattr(info, 'st_flags', 0) & 0x40000000)


#: Собирает идентичность, размер и mtime файла для дальнейшей проверки.
#: Не использует ctime, который может измениться после загрузки из облака.
def cloud_version(info):
    return [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]


#: Возвращает доступное место для новых загрузок на системном диске.
#: Использует метаданные файловой системы открытого каталога.
def free_bytes(descriptor):
    capacity = os.fstatvfs(descriptor)
    return capacity.f_bavail * capacity.f_frsize


#: Возвращает виртуальный том iCloud Drive для двухпанельного дерева.
#: Поля результата: id, name, display_name, kind, availability, identity_status, mounted, mount_path.
def icloud_volume(available):
    return dict(id=ICLOUD_VOLUME_ID, name='iCloud Drive', display_name='iCloud Drive',
                kind='icloud', availability='online' if available else 'offline',
                identity_status='virtual', mounted=False, mount_path=None)


#: Запрашивает загрузку и ограничивает ожидание данных отдельного процесса чтения.
#: Зависимость конструктора: build_directory.
class ICloudReader:
    #: Запоминает расположение исполняемого помощника Core.
    #: Обновляет состояние объекта: executable.
    def __init__(self, build_directory):
        self.executable = Path(build_directory) / 'icloud-reader'

    #: Собирает помощник macOS при первом запуске или изменении нативного кода.
    #: Явно отклоняет недопустимое состояние через OSError.
    def command(self):
        source = Path(__file__).with_name('icloud_reader.m')
        if not self.executable.exists() or self.executable.stat().st_mtime_ns < source.stat().st_mtime_ns:
            self.executable.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.executable.with_name('icloud-reader-' + uuid4().hex)
            try:
                result = subprocess.run(
                    ['/usr/bin/clang', '-fobjc-arc', str(source), '-framework', 'Foundation', '-o', str(temporary)],
                    env=dict(os.environ, CLANG_MODULE_CACHE_PATH=str(self.executable.parent / 'clang-module-cache')),
                    capture_output=True, text=True, timeout=120)
                if result.returncode:
                    raise OSError(result.stderr.strip() or 'Не удалось собрать помощник iCloud')
                temporary.replace(self.executable)
            finally:
                temporary.unlink(missing_ok=True)
        return str(self.executable)

    #: Передаёт блоки файла до конца, паузы или тайм-аута без данных.
    #: Сохраняет исходную ошибку помощника для журнала повторных попыток.
    def stream(self, parent, name, check):
        process = subprocess.Popen([self.command(), str(parent), name], pass_fds=(parent,),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with process.stdout, process.stderr:
            try:
                deadline = time.monotonic() + READ_TIMEOUT
                while True:
                    check()
                    if not select.select([process.stdout], [], [], .25)[0]:
                        if time.monotonic() >= deadline:
                            raise TimeoutError('iCloud слишком долго не передаёт данные')
                        continue
                    chunk = os.read(process.stdout.fileno(), 1024 * 1024)
                    if not chunk:
                        break
                    yield chunk
                    deadline = time.monotonic() + READ_TIMEOUT
                if process.wait(timeout=2):
                    raise OSError(process.stderr.read().decode(errors='replace') or 'Ошибка чтения файла iCloud')
            finally:
                if process.poll() is None:
                    process.kill()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        pass

    #: Вызывает одну явную операцию macOS над подтверждённой версией файла.
    #: Отдельно возвращает отказ без изменения файла и временную ошибку.
    def residency(self, parent, name, operation, version):
        device, inode, size, mtime = version
        seconds, nanos = divmod(mtime, 10**9)
        result = subprocess.run([self.command(), str(parent), name, operation, *map(str, (device, inode, size, seconds, nanos))],
                                pass_fds=(parent,), capture_output=True, text=True, timeout=15)
        detail = result.stderr.strip()
        if result.returncode == 0:
            return True, detail
        message = detail or 'macOS отклонила действие iCloud'
        if result.returncode == 76:
            return False, message
        raise OSError(message)


#: Хранит привязки папок iCloud Drive, очередь передачи и результат каждого пути.
#: Зависимости конструктора: storage, build_directory, root, reader.
class ICloudCopies:
    #: Инициализирует постоянную очередь и параметры фонового исполнителя.
    #: Изменяет SQLite-таблицы: icloud_copies, icloud_copy_items.
    def __init__(self, storage, build_directory, *, root=None, reader=None):
        self.storage = storage
        self.root = Path(root) if root is not None else (
            Path.home() / 'Library/Mobile Documents/com~apple~CloudDocs' if sys.platform == 'darwin' else None)
        self.reader = reader or ICloudReader(build_directory)
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._lock = threading.RLock()
        self._thread = None
        self._current = None
        with self.storage.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS icloud_copies (
                    id TEXT PRIMARY KEY, number INTEGER UNIQUE NOT NULL, source_path TEXT NOT NULL,
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, roots TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 0, state TEXT NOT NULL DEFAULT 'idle',
                    current_path TEXT NOT NULL DEFAULT '', message TEXT NOT NULL DEFAULT '',
                    retry_at REAL NOT NULL DEFAULT 0, updated_at TEXT NOT NULL,
                    source_link_id TEXT REFERENCES icloud_copies(id),
                    UNIQUE(volume_id, path)
                );
                CREATE TABLE IF NOT EXISTS icloud_copy_items (
                    copy_id TEXT NOT NULL REFERENCES icloud_copies(id) ON DELETE CASCADE,
                    path TEXT NOT NULL, kind TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0, retry_at REAL NOT NULL DEFAULT 0,
                    message TEXT NOT NULL DEFAULT '', staging TEXT, updated_at TEXT NOT NULL,
                    cloud_phase TEXT NOT NULL DEFAULT '', cloud_bytes INTEGER NOT NULL DEFAULT 0,
                    cloud_version TEXT, cloud_message TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY(copy_id, path)
                );
                CREATE INDEX IF NOT EXISTS icloud_copy_due ON icloud_copy_items(copy_id, state, retry_at);
            """)
            if 'source_link_id' not in {row['name'] for row in db.execute('PRAGMA table_info(icloud_copies)')}:
                db.execute('ALTER TABLE icloud_copies ADD COLUMN source_link_id TEXT REFERENCES icloud_copies(id)')
            self._scope_numbers(db)
            fields = {row['name'] for row in db.execute('PRAGMA table_info(icloud_copy_items)')}
            for name, definition in (('cloud_phase', "TEXT NOT NULL DEFAULT ''"), ('cloud_bytes', 'INTEGER NOT NULL DEFAULT 0'),
                                     ('cloud_version', 'TEXT'), ('cloud_message', "TEXT NOT NULL DEFAULT ''")):
                if name not in fields:
                    db.execute(f'ALTER TABLE icloud_copy_items ADD COLUMN {name} {definition}')
            db.execute("CREATE INDEX IF NOT EXISTS icloud_copy_batch ON icloud_copy_items(cloud_phase, copy_id) WHERE cloud_phase != ''")
            db.execute("UPDATE icloud_copies SET current_path='' WHERE active=1")

    #: Вводит независимую нумерацию копий для каждого корня iCloud.
    #: Прежний порядковый номер задаёт порядок миграции; ID, задания и файлы сохраняются.
    @staticmethod
    def _scope_numbers(db):
        if 'scope_number' not in {row['name'] for row in db.execute('PRAGMA table_info(icloud_copies)')}:
            db.execute('ALTER TABLE icloud_copies ADD COLUMN scope_number INTEGER')
        db.execute("""
            WITH ranked AS MATERIALIZED (
                SELECT p.id, COALESCE((SELECT MAX(c.scope_number) FROM icloud_copies c
                                      WHERE c.source_path=p.source_path),0)
                    + ROW_NUMBER() OVER (PARTITION BY p.source_path ORDER BY p.number) AS scoped
                FROM icloud_copies p WHERE p.scope_number IS NULL
            )
            UPDATE icloud_copies SET scope_number=(SELECT scoped FROM ranked WHERE ranked.id=icloud_copies.id)
            WHERE scope_number IS NULL
        """)
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS icloud_copy_scope_number ON icloud_copies(source_path, scope_number)')

    #: Возвращает доступный путь облачного источника для просмотра и подсчёта.
    #: Явно отклоняет недопустимое состояние через OSError.
    def source_volume(self):
        if self.root is None or not self.root.is_dir():
            raise OSError('iCloud Drive недоступен на M4')
        return dict(mount_path=str(self.root))

    #: Читает метаданные папки iCloud для обычного дерева без скачивания содержимого.
    #: Поля результата: path, volume, entries, scanned_at, cached.
    def browse(self, path):
        path = relative_path(path)
        volume = self.source_volume()
        entries = StorageCatalog._read_directory(volume, path)
        return dict(path=path, volume=icloud_volume(True), entries=entries, scanned_at=now(), cached=False)

    #: Возвращает привязку и проверяет её наличие в базе.
    #: Явно отклоняет недопустимое состояние через KeyError.
    def _copy(self, copy_id):
        with self.storage.connect() as db:
            row = db.execute('SELECT * FROM icloud_copies WHERE id=?', (copy_id,)).fetchone()
        if row is None:
            raise KeyError('Копия iCloud Drive не найдена')
        return dict(row, number=row['scope_number'])

    #: Проверяет доступность и подтверждённую идентичность тома назначения.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _target_volume(self, volume_id, *, force=False):
        volumes = self.storage.refresh(force=force)['volumes']
        volume = next((volume for volume in volumes if volume['id'] == volume_id), None)
        if not volume or volume['availability'] != 'online':
            raise OSError('Том копии отключён или недоступен')
        if volume['identity_status'] in ('unverified', 'legacy'):
            raise OSError('Сначала подтверди том назначения')
        return volume

    #: Возвращает общее число и логический объём загрузок, занявших пакет.
    #: Учитывает очередь всех прямых копий, включая запрошенные до ручной паузы.
    @staticmethod
    def _batch_usage(db):
        marks = ','.join('?' for _ in CLOUD_IN_PROGRESS)
        row = db.execute(f'''SELECT COUNT(*) AS files, COALESCE(SUM(cloud_bytes),0) AS bytes
                            FROM icloud_copy_items WHERE cloud_phase != '' AND cloud_phase IN ({marks})''', CLOUD_IN_PROGRESS).fetchone()
        return dict(row)

    #: Привязывает папку назначения к облачной области или её сохранённой копии.
    #: Проверяет непересечение корней и сохраняет их идентичность.
    def bind(self, source_path, volume_id, path, source_link_id=None):
        source_path, path = relative_path(source_path), relative_path(path)
        if not path:
            raise ValueError('Выбери папку назначения внутри тома')
        destination = self._target_volume(volume_id, force=True)
        copy_id = uuid4().hex
        with self._lock, self.storage.connect() as db:
            upstream = self._copy(source_link_id) if source_link_id else None
            if upstream and upstream['source_path'] != source_path:
                raise ValueError('Выбери копию той же папки iCloud Drive')
            if upstream and self.root is not None:
                cloud_path = self.root.resolve()
                target_path = (Path(destination['mount_path']) / path).resolve()
                if target_path.is_relative_to(cloud_path) or cloud_path.is_relative_to(target_path):
                    raise ValueError('Папка назначения и iCloud Drive пересекаются.')
                if self.root.is_dir():
                    MissingCopyCatalog._roots(dict(left={'path': ''}, right={'path': path}),
                                              dict(left=self.source_volume(), right=destination))
            origin = self._target_volume(upstream['volume_id']) if upstream else self.source_volume()
            scopes = dict(left={'path': upstream['path'] if upstream else ''}, right={'path': path})
            roots = MissingCopyCatalog._roots(scopes, dict(left=origin, right=destination))
            if upstream:
                if roots['left'] != json.loads(upstream['roots'])['right']:
                    raise OSError('Папка копии-источника заменена. Проверь привязку.')
            else:
                with open_readonly(origin, source_path, directory=True) as source:
                    roots['scope'] = object_id(os.fstat(source))
            for row in db.execute('SELECT volume_id,path,roots FROM icloud_copies'):
                other, target = PurePosixPath(row['path']), PurePosixPath(path)
                if json.loads(row['roots'])['right'] == roots['right'] or (
                    row['volume_id'] == volume_id and (target.is_relative_to(other) or other.is_relative_to(target))
                ):
                    raise ValueError('Папка пересекается с уже привязанной копией iCloud Drive')
            sequence = db.execute('SELECT COALESCE(MAX(number),0)+1 FROM icloud_copies').fetchone()[0]
            number = db.execute('SELECT COALESCE(MAX(scope_number),0)+1 FROM icloud_copies WHERE source_path=?',
                                (source_path,)).fetchone()[0]
            db.execute('''INSERT INTO icloud_copies
                          (id,number,scope_number,source_path,volume_id,path,roots,source_link_id,updated_at)
                          VALUES (?,?,?,?,?,?,?,?,?)''',
                       (copy_id, sequence, number, source_path, volume_id, path, json.dumps(roots), source_link_id, now()))
        return dict(id=copy_id, number=number)

    #: Возвращает краткое состояние копий для боковой панели.
    #: Считает готовые файлы, ожидающие повтора пути и расхождения.
    def list(self):
        volumes = {v['id']: v for v in self.storage.refresh(cached_only=True)['volumes']}
        with self.storage.connect() as db:
            batch = self._batch_usage(db)
            marks = ','.join('?' for _ in CLOUD_IN_PROGRESS)
            tracked = db.execute(f"""SELECT c.source_path,i.path,i.cloud_phase,i.cloud_version
                                      FROM icloud_copy_items i JOIN icloud_copies c ON c.id=i.copy_id
                                      WHERE i.cloud_phase IN ({marks})""", CLOUD_IN_PROGRESS).fetchall()
            rows = db.execute("""
                SELECT c.id,c.scope_number AS number,c.source_path,c.source_link_id,p.scope_number AS source_number,
                    c.volume_id,c.path,c.active,c.state,c.current_path,c.message,c.retry_at,
                    COUNT(*) FILTER (WHERE i.kind='file') AS total,
                    COUNT(*) FILTER (WHERE i.kind='file' AND i.state IN ('done','existing')) AS done,
                    COUNT(*) FILTER (WHERE i.state='retry') AS waiting,
                    COUNT(*) FILTER (WHERE i.state='conflict') AS conflicts,
                    COUNT(*) FILTER (WHERE i.cloud_phase='evicted') AS evicted,
                    COALESCE(SUM(i.cloud_bytes) FILTER (WHERE i.cloud_phase='evicted'),0) AS evicted_bytes,
                    COUNT(*) FILTER (WHERE i.cloud_phase='kept') AS kept_downloads,
                    MIN(i.retry_at) FILTER (WHERE i.state='retry' AND i.retry_at>0) AS next_attempt
                FROM icloud_copies c LEFT JOIN icloud_copies p ON p.id=c.source_link_id
                LEFT JOIN icloud_copy_items i ON c.id=i.copy_id
                GROUP BY c.id ORDER BY c.number
            """).fetchall()
        copies = []
        for row in rows:
            volume = volumes.get(row['volume_id'], {})
            copies.append(dict(row, volume_name=volume.get('display_name') or volume.get('name') or 'Том',
                               availability=volume.get('availability', 'offline'),
                               source_label=f"{row['source_number']:02d}-copy" if row['source_number'] else 'iCloud Drive'))
        batch.update(limit_files=CLOUD_BATCH_FILES, limit_bytes=CLOUD_BATCH_BYTES, reserve_bytes=CLOUD_DISK_RESERVE,
                     free_bytes=None, local_bytes=None,
                     downloading=sum(row['cloud_phase'] in ('reserved', 'requested', 'external') for row in tracked),
                     copying=sum(row['cloud_phase'] == 'copying' for row in tracked),
                     releasing=sum(row['cloud_phase'] == 'evict_pending' for row in tracked))
        try:
            source = self.source_volume()
            available = True
        except OSError:
            available = False
        if available:
            try:
                with open_readonly(source, '', directory=True) as descriptor:
                    batch['free_bytes'] = free_bytes(descriptor)
                batch['local_bytes'] = self._batch_local_bytes(source, tracked)
            except OSError:
                pass
        return dict(volume=icloud_volume(available), copies=copies, batch=batch)

    #: Суммирует реально выделенные блоки файлов текущего пакета по метаданным.
    #: Два задания для одного файла учитываются один раз; неполные метаданные дают неизвестный результат.
    @staticmethod
    def _batch_local_bytes(source, tracked):
        occupied = {}
        for row in tracked:
            path = PurePosixPath(row['source_path']) / row['path']
            try:
                with open_readonly(source, relative_path(str(path.parent)), directory=True) as parent:
                    info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            except OSError:
                return None
            version = json.loads(row['cloud_version'])
            if row['cloud_phase'] == 'evict_pending':
                version = version['source']
            if not stat.S_ISREG(info.st_mode) or cloud_version(info) != version:
                return None
            occupied[(info.st_dev, info.st_ino)] = info.st_blocks * 512
        return sum(occupied.values())

    #: Возвращает страницу журнала с причинами задержек и временем повтора.
    #: Читает SQLite-таблицы: icloud_copy_items.
    def journal(self, copy_id, offset=0, limit=100):
        copy = self._copy(copy_id)
        marks = ','.join('?' for _ in CLOUD_IN_PROGRESS)
        with self.storage.connect() as db:
            rows = db.execute(f"""
                SELECT path,kind,state,attempts,retry_at,message,updated_at,cloud_phase,cloud_bytes,cloud_message FROM icloud_copy_items
                WHERE copy_id=? AND (state!='pending' OR cloud_phase!='')
                ORDER BY CASE WHEN cloud_phase IN ({marks}) THEN 0 WHEN state='retry' THEN 1
                              WHEN state='conflict' THEN 2 ELSE 3 END, updated_at DESC, path
                LIMIT ? OFFSET ?
            """, (copy_id, *CLOUD_IN_PROGRESS, limit + 1, offset)).fetchall()
        return dict(state=copy['state'], message=copy['message'], items=[dict(row) for row in rows[:limit]],
                    more=len(rows) > limit)

    #: Включает передачу или начинает новый проход после завершения предыдущего.
    #: Изменяет SQLite-таблицы: icloud_copies, icloud_copy_items.
    def start_copy(self, copy_id):
        with self._lock:
            copy = self._copy(copy_id)
            if not copy['active']:
                with self.storage.connect() as db:
                    if copy['state'] in ('idle', 'completed', 'completed_with_conflicts'):
                        db.execute('DELETE FROM icloud_copy_items WHERE copy_id=?', (copy_id,))
                    empty = not db.execute('SELECT 1 FROM icloud_copy_items WHERE copy_id=? LIMIT 1', (copy_id,)).fetchone()
                    waiting_source = empty and copy['source_link_id']
                    if empty and not waiting_source:
                        db.execute("INSERT INTO icloud_copy_items (copy_id,path,kind,updated_at) VALUES (?,'','directory',?)",
                                   (copy_id, now()))
                    upstream = self._copy(copy['source_link_id']) if waiting_source else None
                    self._update_copy(db, copy_id, active=1, state='waiting_source' if waiting_source else 'running', retry_at=0,
                                      message=f"Ждёт завершения {upstream['number']:02d}-copy. Запусти или продолжи источник." if upstream else '')
        self._wake.set()
        return dict(id=copy_id)

    #: Ставит привязку на постоянную паузу и останавливает текущую передачу.
    #: Изменяет SQLite-таблицы: icloud_copies.
    def pause_copy(self, copy_id):
        with self._lock, self.storage.connect() as db:
            self._copy(copy_id)
            self._update_copy(db, copy_id, active=0, state='paused', current_path='', message='Пауза')
        self._wake.set()
        return dict(id=copy_id)

    #: Удаляет остановленную привязку после выхода исполнителя из текущего файла.
    #: Изменяет SQLite-таблицы: icloud_copies, icloud_copy_items.
    def unbind(self, copy_id):
        with self._lock, self.storage.connect() as db:
            if self._copy(copy_id)['active'] or self._current == copy_id:
                raise ValueError('Сначала поставь копирование на паузу и дождись остановки')
            if db.execute('SELECT 1 FROM icloud_copies WHERE source_link_id=? LIMIT 1', (copy_id,)).fetchone():
                raise ValueError('Сначала отвяжи копии, которые используют это звено как источник')
            if db.execute('SELECT 1 FROM icloud_copy_items WHERE copy_id=? AND staging IS NOT NULL', (copy_id,)).fetchone():
                raise ValueError('Возобнови копирование, чтобы обработать незавершённую запись')
            if db.execute("SELECT 1 FROM icloud_copy_items WHERE copy_id=? AND cloud_phase IN ('reserved','requested','external','copying','evict_pending')",
                          (copy_id,)).fetchone():
                raise ValueError('Возобнови копирование, чтобы закончить обработку запрошенных загрузок iCloud')
            db.execute('DELETE FROM icloud_copies WHERE id=?', (copy_id,))
        return dict(id=copy_id)

    #: Запускает обработку активных привязок, в том числе после перезапуска Core.
    #: Обновляет состояние объекта: _thread.
    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(target=self._work, name='icloud-copies', daemon=True)
            self._thread.start()

    #: Кооперативно завершает поток перед остановкой Core.
    #: Использует _stop, _wake и join.
    def close(self):
        self._stop.set()
        self._wake.set()
        if self._thread:
            self._thread.join(timeout=5)

    #: Обновляет состояние привязки внутри переданной транзакции.
    #: Изменяет SQLite-таблицу icloud_copies.
    @staticmethod
    def _update_copy(db, copy_id, **values):
        values['updated_at'] = now()
        assignments = ','.join(key + '=?' for key in values)
        db.execute('UPDATE icloud_copies SET ' + assignments + ' WHERE id=?', (*values.values(), copy_id))

    #: Обновляет состояние элемента очереди и его промежуточной записи.
    #: Изменяет SQLite-таблицу icloud_copy_items.
    def _update_item(self, item, **values):
        values['updated_at'] = now()
        assignments = ','.join(key + '=?' for key in values)
        with self.storage.connect() as db:
            db.execute('UPDATE icloud_copy_items SET ' + assignments + ' WHERE copy_id=? AND path=?',
                       (*values.values(), item['copy_id'], item['path']))

    #: Прерывает работу при паузе выбранной копии или выходе Core.
    #: Явно отклоняет недопустимое состояние через CopyStopped.
    def _check(self, copy_id):
        if self._stop.is_set() or not self._copy(copy_id)['active']:
            raise CopyStopped()

    #: Формирует очередь зависимой копии из завершённого прохода копии-источника.
    #: Переносит только готовые пути и журналирует расхождения предыдущего звена.
    def _queue_ready_sources(self, db):
        rows = db.execute("""
            SELECT c.id,c.source_link_id FROM icloud_copies c
            JOIN icloud_copies p ON p.id=c.source_link_id
            WHERE c.active=1 AND c.state='waiting_source' AND p.active=0
                AND p.state IN ('completed','completed_with_conflicts')
                AND EXISTS (SELECT 1 FROM icloud_copy_items i WHERE i.copy_id=p.id AND i.path='')
        """).fetchall()
        for row in rows:
            db.execute("""
                INSERT INTO icloud_copy_items (copy_id,path,kind,state,message,updated_at)
                SELECT ?,path,kind,CASE WHEN state='conflict' THEN 'conflict' ELSE 'pending' END,
                    CASE WHEN state='conflict' THEN 'В копии-источнике: ' || message ELSE '' END,?
                FROM icloud_copy_items WHERE copy_id=? AND state IN ('done','existing','conflict')
            """, (row['id'], now(), row['source_link_id']))
            self._update_copy(db, row['id'], state='running', message='')

    #: Сначала проверяет занятые места пакета и откладывает известные заявки без места.
    #: Учитывает общий лимит файлов и байтов, затем обновляет состояние привязок.
    def _next(self):
        current = time.time()
        marks = ','.join('?' for _ in CLOUD_IN_PROGRESS)
        with self.storage.connect() as db:
            self._queue_ready_sources(db)
            batch = self._batch_usage(db)
            item = db.execute(f"""
                SELECT i.* FROM icloud_copy_items i JOIN icloud_copies c ON c.id=i.copy_id
                WHERE c.active=1 AND c.retry_at<=? AND (i.state IN ('pending','retry') OR i.cloud_phase='evict_pending') AND i.retry_at<=?
                  AND (i.cloud_phase!='waiting_space' OR (? AND (?=0 OR i.cloud_bytes<=?)))
                ORDER BY CASE WHEN i.cloud_phase='evict_pending' THEN 0
                              WHEN i.cloud_phase IN ({marks}) THEN 1 ELSE 2 END,
                         c.updated_at, i.retry_at, i.path LIMIT 1
            """, (current, current, batch['files'] < CLOUD_BATCH_FILES, batch['files'],
                  CLOUD_BATCH_BYTES - batch['bytes'], *CLOUD_IN_PROGRESS)).fetchone()
            if item:
                return dict(item)
            for row in db.execute("""
                SELECT c.id,COUNT(*) FILTER (WHERE i.state='retry') AS waiting,
                    COUNT(*) FILTER (WHERE i.state='pending' OR i.cloud_phase='evict_pending') AS pending,
                    COUNT(*) FILTER (WHERE i.state='conflict') AS conflicts
                FROM icloud_copies c LEFT JOIN icloud_copy_items i ON i.copy_id=c.id
                WHERE c.active=1 AND c.state!='waiting_source' AND c.retry_at<=? GROUP BY c.id
            """, (current,)).fetchall():
                if row['waiting']:
                    db.execute("UPDATE icloud_copies SET state='waiting',current_path='' WHERE id=? AND state!='waiting'", (row['id'],))
                elif not row['pending']:
                    state = 'completed_with_conflicts' if row['conflicts'] else 'completed'
                    self._update_copy(db, row['id'], state=state, active=0, current_path='', message='')
        return None

    #: Освобождает текущий путь и завершает привязку сразу после последнего элемента.
    #: Сохраняет статус ожидания при отложенных повторных попытках.
    def _finish_item(self, copy_id):
        with self._lock, self.storage.connect() as db:
            if not self._copy(copy_id)['active']:
                return
            pending = db.execute("""SELECT 1 FROM icloud_copy_items WHERE copy_id=?
                                    AND (state='pending' OR cloud_phase='evict_pending') LIMIT 1""", (copy_id,)).fetchone()
            if pending:
                return
            states = {row[0] for row in db.execute("SELECT DISTINCT state FROM icloud_copy_items WHERE copy_id=? AND state IN ('retry', 'conflict')", (copy_id,))}
            if 'retry' in states:
                db.execute("UPDATE icloud_copies SET state='waiting',current_path='' WHERE id=?", (copy_id,))
            else:
                state = 'completed_with_conflicts' if 'conflict' in states else 'completed'
                self._update_copy(db, copy_id, state=state, active=0, current_path='', message='')

    #: Обходит готовые элементы и оставляет временные ошибки для последующих попыток.
    #: Обрабатывает ошибки: CopyStopped, OSError, subprocess.SubprocessError.
    def _work(self):
        while not self._stop.is_set():
            with self._lock:
                item = self._next()
                self._current = item['copy_id'] if item else None
            if item:
                try:
                    self._process(item)
                except CopyStopped:
                    pass
                finally:
                    with self._lock:
                        self._current = None
                continue
            self._wake.wait(2)
            self._wake.clear()

    #: Сопоставляет действующий источник и целевой корень с сохранённой привязкой.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _validate_roots(self, copy, source_volume, target_volume):
        expected = json.loads(copy['roots'])
        if copy['source_link_id']:
            source_checks = ((source_volume, copy['read_path'], 'left'),)
        else:
            source_checks = ((source_volume, '', 'left'), (source_volume, copy['read_path'], 'scope'))
        for volume, path, key in (*source_checks, (target_volume, copy['path'], 'right')):
            with open_readonly(volume, path, directory=True) as descriptor:
                if object_id(os.fstat(descriptor)) != expected[key]:
                    raise OSError('Папка источника или назначения заменена. Проверь привязку.')

    #: Выполняет одну попытку, фиксируя временный сбой тома или выбранного пути.
    #: Вычисляет паузу от 15 секунд до 15 минут по числу попыток.
    def _process(self, item):
        identifier = item['copy_id']
        self._check(identifier)
        copy = self._copy(identifier)
        try:
            if copy['source_link_id']:
                upstream = self._copy(copy['source_link_id'])
                source_volume = self._target_volume(upstream['volume_id'])
                copy['read_path'] = upstream['path']
            else:
                source_volume = self.source_volume()
                copy['read_path'] = copy['source_path']
            target_volume = self._target_volume(copy['volume_id'])
            self._validate_roots(copy, source_volume, target_volume)
        except OSError as error:
            with self._lock, self.storage.connect() as db:
                self._check(identifier)
                self._update_copy(db, identifier, state='waiting', retry_at=time.time() + 30, message=str(error), current_path='')
            return

        with self._lock, self.storage.connect() as db:
            self._check(identifier)
            self._update_copy(db, identifier, state='running', retry_at=0, message='', current_path=item['path'])
        if item['cloud_phase'] == 'evict_pending':
            self._evict_download(item, copy, source_volume, target_volume)
            self._finish_item(identifier)
            return
        try:
            if item['kind'] == 'directory':
                state, message = self._scan(item, copy, source_volume, target_volume)
            else:
                state, message = self._transfer(item, copy, source_volume, target_volume)
            self._update_item(item, state=state, message=message, retry_at=0)
        except CloudPending as pending:
            retry_at = time.time() + pending.delay if pending.delay else 0
            self._update_item(item, state='retry', retry_at=retry_at, message=str(pending))
        except (OSError, subprocess.SubprocessError) as error:
            attempts = item['attempts'] + 1
            delay = min(900, 15 * 2 ** min(attempts - 1, 6))
            self._update_item(item, state='retry', attempts=attempts, retry_at=time.time() + delay, message=str(error))
        self._finish_item(identifier)

    #: Добавляет облачные дочерние пути или создаёт папку из очереди зависимой копии.
    #: Сохраняет пустые каталоги и пропускает ссылки и специальные объекты.
    def _scan(self, item, copy, source_volume, target_volume):
        path = item['path']
        source = '/'.join(filter(None, (copy['read_path'], path)))
        children = []
        with open_readonly(source_volume, source, directory=True) as descriptor:
            if not copy['source_link_id']:
                with os.scandir(descriptor) as entries:
                    device = os.fstat(descriptor).st_dev
                    for entry in entries:
                        if service_file(entry.name, volume_root=not source):
                            continue
                        try:
                            info = entry.stat(follow_symlinks=False)
                        except FileNotFoundError:
                            continue
                        if info.st_dev == device and (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                            children.append(('/'.join(filter(None, (path, entry.name))),
                                             'directory' if stat.S_ISDIR(info.st_mode) else 'file'))
        with self._lock:
            self._check(copy['id'])
            self._validate_roots(copy, source_volume, target_volume)
            try:
                with destination_directory(target_volume, copy, path, create=True):
                    pass
            except NotADirectoryError:
                return 'conflict', 'Путь папки занят другим объектом'
            if children:
                with self.storage.connect() as db:
                    db.executemany('INSERT OR IGNORE INTO icloud_copy_items (copy_id,path,kind,updated_at) VALUES (?,?,?,?)',
                                   ((copy['id'], name, kind, now()) for name, kind in children))
        return 'done', ''

    #: Удаляет собственную незавершённую запись после сверки идентичности.
    #: Оставляет заменённый внешним процессом объект на диске.
    def _cleanup(self, item, target, staging):
        for entry in (staging.get('direct'), staging):
            if not entry:
                continue
            try:
                info = os.stat(entry['name'], dir_fd=target, follow_symlinks=False)
                if stat.S_ISREG(info.st_mode) and object_id(info) == entry['id']:
                    os.unlink(entry['name'], dir_fd=target)
            except FileNotFoundError:
                pass
        self._update_item(item, staging=None)

    #: Безопасно открывает подтверждённого родителя исходного файла.
    #: Поля результата: дескриптор родителя и имя файла.
    @staticmethod
    @contextmanager
    def _source_parent(copy, source_volume, path):
        full = PurePosixPath(copy['read_path']) / path
        with open_readonly(source_volume, relative_path(str(full.parent)), directory=True) as parent:
            yield parent, full.name

    #: Резервирует место пакета перед первым запросом загрузки заполнителя iCloud.
    #: Разрешает большой файл отдельно, если после загрузки останется резерв диска.
    def _reserve_download(self, item, original, source, version):
        with self._lock, self.storage.connect() as db:
            self._check(item['copy_id'])
            batch = self._batch_usage(db)
            size = source.st_size
            if batch['files'] >= CLOUD_BATCH_FILES or (batch['files'] and batch['bytes'] + size > CLOUD_BATCH_BYTES):
                pending = CloudPending('Ожидает места в пакете загрузки', delay=0)
            elif free_bytes(original) < CLOUD_DISK_RESERVE + batch['bytes'] + size:
                pending = CloudPending('На диске M4 недостаточно места с учётом резерва', delay=30)
            else:
                db.execute("""UPDATE icloud_copy_items
                              SET cloud_phase='reserved',cloud_bytes=?,cloud_version=?,cloud_message=?,updated_at=?
                              WHERE copy_id=? AND path=?""",
                           (size, json.dumps(version), 'Зарезервировано место для загрузки', now(),
                            item['copy_id'], item['path']))
                return
        self._update_item(item, cloud_phase='waiting_space', cloud_bytes=size, cloud_version=None, cloud_message=str(pending))
        raise pending

    #: Управляет явной загрузкой отсутствующего облачного файла и записывает её владельца.
    #: Уже локальный файл доступен сразу; после перезапуска сохраняется прежняя заявка.
    def _prepare_download(self, item, original, name, source):
        version = cloud_version(source)
        phase = item['cloud_phase'] if json.loads(item['cloud_version'] or 'null') == version else ''
        if not phase and item['cloud_phase'] in CLOUD_IN_PROGRESS:
            self._update_item(item, cloud_phase='kept', cloud_message='Версия файла изменилась')
        if not cloud_dataless(source):
            if phase in ('requested', 'copying'):
                self._update_item(item, cloud_phase='copying', cloud_message='Загружен на M4, записывается в копию')
                return 'copying'
            return phase if phase in CLOUD_IN_PROGRESS else 'local'
        if phase not in CLOUD_IN_PROGRESS:
            self._reserve_download(item, original, source, version)
        try:
            operation = 'retry' if phase in ('requested', 'copying') else 'download'
            accepted, message = self.reader.residency(original, name, operation, version)
        except OSError as error:
            self._update_item(item, cloud_phase=phase if phase in CLOUD_IN_PROGRESS else 'waiting_space',
                              cloud_message=str(error))
            raise
        phase = 'requested' if accepted or phase in ('requested', 'copying') else 'external'
        self._update_item(item, cloud_phase=phase, cloud_message=message or 'Загрузка запрошена у macOS')
        raise CloudPending('Ожидание загрузки из iCloud')

    #: Освобождает загрузку приложения после проверки обеих версий файла.
    #: Если macOS сохраняет загрузку, причина остаётся в журнале.
    def _evict_download(self, item, copy, source_volume, target_volume):
        versions = json.loads(item['cloud_version'])
        parent = relative_path(str(PurePosixPath(item['path']).parent))
        try:
            with (self._source_parent(copy, source_volume, item['path']) as (original, name),
                  destination_directory(target_volume, copy, parent) as target):
                source = os.stat(name, dir_fd=original, follow_symlinks=False)
                saved = os.stat(name, dir_fd=target, follow_symlinks=False)
                if (not stat.S_ISREG(source.st_mode) or not stat.S_ISREG(saved.st_mode)
                        or cloud_version(source) != versions['source'] or cloud_version(saved) != versions['target']):
                    self._update_item(item, cloud_phase='kept', cloud_message='Источник или записанная копия изменились')
                    return
                self._check(copy['id'])
                released, reason = self.reader.residency(original, name, 'evict', versions['source'])
        except (OSError, subprocess.SubprocessError) as error:
            attempts = item['attempts'] + 1
            self._update_item(item, cloud_phase='evict_pending' if attempts < 3 else 'kept',
                              attempts=attempts, retry_at=time.time() + 5 if attempts < 3 else 0,
                              cloud_message=str(error))
            return
        self._update_item(item, cloud_phase='evicted' if released else 'kept',
                          cloud_message='Локальная загрузка освобождена' if released else reason, retry_at=0)

    #: Планирует запись одного отсутствующего файла с учётом существующего назначения.
    #: Проверяет размер и не читает содержимое уже существующего файла.
    def _transfer(self, item, copy, source_volume, target_volume):
        path = PurePosixPath(item['path'])
        parent = relative_path(str(path.parent))
        try:
            with (self._source_parent(copy, source_volume, item['path']) as (original, name),
                  destination_directory(target_volume, copy, parent) as target):
                if item['staging']:
                    self._cleanup(item, target, json.loads(item['staging']))
                source = os.stat(name, dir_fd=original, follow_symlinks=False)
                if not stat.S_ISREG(source.st_mode) or source.st_dev != os.fstat(original).st_dev:
                    return 'conflict', 'Источник изменился: ожидался обычный файл'
                try:
                    existing = os.stat(name, dir_fd=target, follow_symlinks=False)
                except FileNotFoundError:
                    linked = bool(copy['source_link_id'])
                    phase = '' if linked else self._prepare_download(item, original, name, source)
                    state, message, written = self._write(item, copy, source_volume, target_volume, original, source, parent, target, name)
                    if phase == 'copying' and written:
                        self._update_item(item, state=state, message=message, attempts=0, cloud_phase='evict_pending',
                                          cloud_version=json.dumps(dict(source=cloud_version(source), target=written)),
                                          cloud_message='Копия записана, ожидает освобождения загрузки')
                    elif phase in CLOUD_IN_PROGRESS:
                        self._update_item(item, cloud_phase='kept', cloud_message='Локальная загрузка сохранена')
                    elif phase:
                        self._update_item(item, cloud_phase='local', cloud_bytes=source.st_size,
                                          cloud_message='Файл уже был загружен на M4')
                    return state, message
                if item['cloud_phase'] in CLOUD_IN_PROGRESS:
                    if cloud_dataless(source):
                        raise CloudPending('Ожидает завершения уже запрошенной загрузки iCloud')
                    self._update_item(item, cloud_phase='kept', cloud_message='Файл назначения уже существует; загрузка сохранена')
                if stat.S_ISREG(existing.st_mode) and existing.st_size == source.st_size:
                    return 'existing', 'Файл уже есть в копии, размер совпадает'
                return 'conflict', 'Путь занят файлом другого размера или типа'
        except NotADirectoryError:
            return 'conflict', 'Путь к файлу занят другим объектом'

    #: Читает подтверждённый локальный файл из предыдущего звена по дескриптору.
    #: Сверяет файловые метаданные перед чтением и проверяет паузу между блоками.
    @staticmethod
    def _read_local(parent, name, source, check):
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(descriptor, 'rb') as stream:
            if fingerprint(os.fstat(descriptor)) != fingerprint(source):
                raise OSError('Файл в копии-источнике изменился перед чтением')
            while True:
                check()
                block = stream.read(1024 * 1024)
                if not block:
                    return
                yield block

    #: Сохраняет содержимое во временный файл и публикует без перезаписи.
    #: Перед публикацией сверяет размер, версию исходника и идентичность папки назначения.
    def _write(self, item, copy, source_volume, target_volume, original, source, parent, target, name):
        temporary = f".media-actu-copy-{copy['id']}-{uuid4().hex}.part"
        descriptor = os.open(temporary, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=target)
        staging = dict(name=temporary, id=object_id(os.fstat(descriptor)))
        try:
            self._update_item(item, staging=json.dumps(staging))
            check_at = 0

            #: Проверяет активность копии во время чтения с ограничением обращения к SQLite.
            #: Обновляет локальное время следующей проверки.
            def check():
                nonlocal check_at
                if time.monotonic() >= check_at or self._stop.is_set():
                    self._check(copy['id'])
                    check_at = time.monotonic() + .5

            size = 0
            reader = (self._read_local(original, name, source, check) if copy['source_link_id']
                      else self.reader.stream(original, name, check))
            with os.fdopen(os.dup(descriptor), 'wb') as output:
                with closing(reader) as stream:
                    for block in stream:
                        size += len(block)
                        if size > source.st_size:
                            raise OSError('Исходный файл вырос во время копирования')
                        output.write(block)
                output.flush()
            if size != source.st_size or os.fstat(descriptor).st_size != size:
                raise OSError('Размер записанного файла не совпал с размером источника')
            os.utime(descriptor, ns=(source.st_atime_ns, source.st_mtime_ns))
            os.fsync(descriptor)
            written = cloud_version(os.fstat(descriptor))
            try:
                with self._lock:
                    self._check(copy['id'])
                    self._validate_transfer(item, copy, source_volume, target_volume, source, parent, target, name)
                    if object_id(os.stat(temporary, dir_fd=target, follow_symlinks=False)) != staging['id']:
                        raise OSError('Промежуточный файл заменён во время копирования')
                    self._publish(target, temporary, name, target_volume.get('kind') == 'network')
            except DirectCopyRequired:
                try:
                    written = self._write_network(item, copy, source_volume, target_volume, source, parent, target, name,
                                                  descriptor, staging, check)
                except FileExistsError:
                    return 'conflict', 'Файл появился в копии во время передачи', None
            except FileExistsError:
                return 'conflict', 'Файл появился в копии во время передачи', None
            return 'done', 'Скопирован', written
        finally:
            os.close(descriptor)
            self._cleanup(item, target, staging)

    #: Проверяет после записи версию источника и идентичность папки назначения.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _validate_transfer(self, item, copy, source_volume, target_volume, source, parent, target, name):
        self._validate_roots(copy, source_volume, target_volume)
        with (self._source_parent(copy, source_volume, item['path']) as (current, _),
              destination_directory(target_volume, copy, parent) as destination):
            if fingerprint(os.stat(name, dir_fd=current, follow_symlinks=False)) != fingerprint(source):
                raise OSError('Исходный файл изменился во время копирования')
            if object_id(os.fstat(target)) != object_id(os.fstat(destination)):
                raise OSError('Целевая папка заменена во время копирования')

    #: Публикует временный путь атомарно, где это поддерживает файловая система.
    #: Запрашивает прямую запись на сетевом томе при отсутствии поддержки.
    @staticmethod
    def _publish(target, temporary, name, network):
        try:
            publish_exclusive(target, temporary, name)
        except OSError as error:
            if error.errno not in PUBLISH_UNSUPPORTED:
                raise
            try:
                os.link(temporary, name, src_dir_fd=target, dst_dir_fd=target, follow_symlinks=False)
            except OSError as failure:
                if not network or failure.errno not in PUBLISH_UNSUPPORTED | {errno.EPERM}:
                    raise
                raise DirectCopyRequired() from failure

    #: Записывает готовый промежуточный файл на SMB без перезаписи существующего пути.
    #: Журналирует незавершённое конечное имя до подтверждения размера и fsync.
    def _write_network(self, item, copy, source_volume, target_volume, source, parent, target, name, descriptor, staging, check):
        with self._lock:
            self._check(copy['id'])
            self._validate_transfer(item, copy, source_volume, target_volume, source, parent, target, name)
            final = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=target)
        with os.fdopen(final, 'wb') as output:
            direct_id = object_id(os.fstat(final))
            staging['direct'] = dict(name=name, id=direct_id)
            self._update_item(item, staging=json.dumps(staging))
            os.lseek(descriptor, 0, os.SEEK_SET)
            while block := os.read(descriptor, 1024 * 1024):
                check()
                output.write(block)
            output.flush()
            if os.fstat(final).st_size != source.st_size:
                raise OSError('Размер записанного файла не совпал с размером источника')
            os.fsync(final)
            with self._lock:
                self._check(copy['id'])
                self._validate_transfer(item, copy, source_volume, target_volume, source, parent, target, name)
                if object_id(os.stat(name, dir_fd=target, follow_symlinks=False)) != direct_id:
                    raise OSError('Файл назначения заменён во время копирования')
                self._update_item(item, staging=json.dumps(dict(staging, direct=None)))
                staging.pop('direct')
                return cloud_version(os.fstat(final))
