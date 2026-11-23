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
                    UNIQUE(volume_id, path)
                );
                CREATE TABLE IF NOT EXISTS icloud_copy_items (
                    copy_id TEXT NOT NULL REFERENCES icloud_copies(id) ON DELETE CASCADE,
                    path TEXT NOT NULL, kind TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0, retry_at REAL NOT NULL DEFAULT 0,
                    message TEXT NOT NULL DEFAULT '', staging TEXT, updated_at TEXT NOT NULL,
                    PRIMARY KEY(copy_id, path)
                );
                CREATE INDEX IF NOT EXISTS icloud_copy_due ON icloud_copy_items(copy_id, state, retry_at);
            """)
            db.execute("UPDATE icloud_copies SET current_path='' WHERE active=1")

    #: Возвращает доступный путь облачного источника для операций чтения.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _source_volume(self):
        if self.root is None or not self.root.is_dir():
            raise OSError('iCloud Drive недоступен на M4')
        return dict(mount_path=str(self.root))

    #: Читает метаданные папки iCloud для обычного дерева без скачивания содержимого.
    #: Поля результата: path, volume, entries, scanned_at, cached.
    def browse(self, path):
        path = relative_path(path)
        volume = self._source_volume()
        entries = StorageCatalog._read_directory(volume, path)
        return dict(path=path, volume=icloud_volume(True), entries=entries, scanned_at=now(), cached=False)

    #: Возвращает привязку и проверяет её наличие в базе.
    #: Явно отклоняет недопустимое состояние через KeyError.
    def _copy(self, copy_id):
        with self.storage.connect() as db:
            row = db.execute('SELECT * FROM icloud_copies WHERE id=?', (copy_id,)).fetchone()
        if row is None:
            raise KeyError('Копия iCloud Drive не найдена')
        return dict(row)

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

    #: Создаёт привязку существующей папки назначения к области iCloud Drive.
    #: Проверяет непересечение корней и сохраняет их идентичность.
    def bind(self, source_path, volume_id, path):
        source_path, path = relative_path(source_path), relative_path(path)
        if not path:
            raise ValueError('Выбери папку назначения внутри тома')
        volumes = dict(left=self._source_volume(), right=self._target_volume(volume_id, force=True))
        scopes = dict(left={'path': source_path}, right={'path': path})
        roots = MissingCopyCatalog._roots(dict(left={'path': ''}, right=scopes['right']), volumes)
        with open_readonly(volumes['left'], source_path, directory=True) as source:
            roots['scope'] = object_id(os.fstat(source))
        copy_id = uuid4().hex
        with self._lock, self.storage.connect() as db:
            for row in db.execute('SELECT volume_id,path,roots FROM icloud_copies'):
                other, target = PurePosixPath(row['path']), PurePosixPath(path)
                if json.loads(row['roots'])['right'] == roots['right'] or (
                    row['volume_id'] == volume_id and (target.is_relative_to(other) or other.is_relative_to(target))
                ):
                    raise ValueError('Папка пересекается с уже привязанной копией iCloud Drive')
            number = db.execute('SELECT COALESCE(MAX(number),0)+1 FROM icloud_copies').fetchone()[0]
            db.execute('INSERT INTO icloud_copies (id,number,source_path,volume_id,path,roots,updated_at) VALUES (?,?,?,?,?,?,?)',
                       (copy_id, number, source_path, volume_id, path, json.dumps(roots), now()))
        return dict(id=copy_id, number=number)

    #: Возвращает краткое состояние копий для боковой панели.
    #: Считает готовые файлы, ожидающие повтора пути и расхождения.
    def list(self):
        volumes = {v['id']: v for v in self.storage.refresh(cached_only=True)['volumes']}
        with self.storage.connect() as db:
            rows = db.execute("""
                SELECT c.id,c.number,c.source_path,c.volume_id,c.path,c.active,c.state,c.current_path,c.message,c.retry_at,
                    COUNT(*) FILTER (WHERE i.kind='file') AS total,
                    COUNT(*) FILTER (WHERE i.kind='file' AND i.state IN ('done','existing')) AS done,
                    COUNT(*) FILTER (WHERE i.state='retry') AS waiting,
                    COUNT(*) FILTER (WHERE i.state='conflict') AS conflicts,
                    MIN(i.retry_at) FILTER (WHERE i.state='retry') AS next_attempt
                FROM icloud_copies c LEFT JOIN icloud_copy_items i ON c.id=i.copy_id
                GROUP BY c.id ORDER BY c.number
            """).fetchall()
        copies = []
        for row in rows:
            volume = volumes.get(row['volume_id'], {})
            copies.append(dict(row, volume_name=volume.get('display_name') or volume.get('name') or 'Том',
                               availability=volume.get('availability', 'offline')))
        try:
            self._source_volume()
            available = True
        except OSError:
            available = False
        return dict(volume=icloud_volume(available), copies=copies)

    #: Возвращает страницу журнала с причинами задержек и временем повтора.
    #: Читает SQLite-таблицы: icloud_copy_items.
    def journal(self, copy_id, offset=0, limit=100):
        copy = self._copy(copy_id)
        with self.storage.connect() as db:
            rows = db.execute("""
                SELECT path,kind,state,attempts,retry_at,message,updated_at FROM icloud_copy_items
                WHERE copy_id=? AND state!='pending'
                ORDER BY CASE state WHEN 'retry' THEN 0 WHEN 'conflict' THEN 1 ELSE 2 END, updated_at DESC, path
                LIMIT ? OFFSET ?
            """, (copy_id, limit + 1, offset)).fetchall()
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
                        db.execute("INSERT INTO icloud_copy_items (copy_id,path,kind,updated_at) VALUES (?,'','directory',?)",
                                   (copy_id, now()))
                    self._update_copy(db, copy_id, active=1, state='running', retry_at=0, message='')
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
            if db.execute('SELECT 1 FROM icloud_copy_items WHERE copy_id=? AND staging IS NOT NULL', (copy_id,)).fetchone():
                raise ValueError('Возобнови копирование, чтобы обработать незавершённую запись')
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

    #: Выбирает следующий доступный элемент, затем вычисляет состояние ожидающих привязок.
    #: Изменяет SQLite-таблицу icloud_copies.
    def _next(self):
        current = time.time()
        with self.storage.connect() as db:
            item = db.execute("""
                SELECT i.* FROM icloud_copy_items i JOIN icloud_copies c ON c.id=i.copy_id
                WHERE c.active=1 AND c.retry_at<=? AND i.state IN ('pending','retry') AND i.retry_at<=?
                ORDER BY c.updated_at, i.retry_at, i.path LIMIT 1
            """, (current, current)).fetchone()
            if item:
                return dict(item)
            for row in db.execute("""
                SELECT c.id,COUNT(*) FILTER (WHERE i.state='retry') AS waiting,
                    COUNT(*) FILTER (WHERE i.state='pending') AS pending,
                    COUNT(*) FILTER (WHERE i.state='conflict') AS conflicts
                FROM icloud_copies c LEFT JOIN icloud_copy_items i ON i.copy_id=c.id
                WHERE c.active=1 AND c.retry_at<=? GROUP BY c.id
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
            pending = db.execute("SELECT 1 FROM icloud_copy_items WHERE copy_id=? AND state='pending' LIMIT 1", (copy_id,)).fetchone()
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

    #: Сопоставляет облачный, выбранный и целевой корни с привязкой.
    #: Явно отклоняет недопустимое состояние через OSError.
    def _validate_roots(self, copy, source_volume, target_volume):
        expected = json.loads(copy['roots'])
        for volume, path, key in ((source_volume, '', 'left'), (source_volume, copy['source_path'], 'scope'),
                                  (target_volume, copy['path'], 'right')):
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
            source_volume = self._source_volume()
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
        try:
            if item['kind'] == 'directory':
                state, message = self._scan(item, copy, source_volume, target_volume)
            else:
                state, message = self._transfer(item, copy, source_volume, target_volume)
            self._update_item(item, state=state, message=message, retry_at=0)
        except (OSError, subprocess.SubprocessError) as error:
            attempts = item['attempts'] + 1
            delay = min(900, 15 * 2 ** min(attempts - 1, 6))
            self._update_item(item, state='retry', attempts=attempts, retry_at=time.time() + delay, message=str(error))
        self._finish_item(identifier)

    #: Читает метаданные одной папки и добавляет её дочерние элементы в очередь.
    #: Сохраняет пустые каталоги и пропускает ссылки и специальные объекты.
    def _scan(self, item, copy, source_volume, target_volume):
        path = item['path']
        source = '/'.join(filter(None, (copy['source_path'], path)))
        children = []
        with open_readonly(source_volume, source, directory=True) as descriptor, os.scandir(descriptor) as entries:
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
        full = PurePosixPath(copy['source_path']) / path
        with open_readonly(source_volume, relative_path(str(full.parent)), directory=True) as parent:
            yield parent, full.name

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
                    return self._write(item, copy, source_volume, target_volume, original, source, parent, target, name)
                if stat.S_ISREG(existing.st_mode) and existing.st_size == source.st_size:
                    return 'existing', 'Файл уже есть в копии, размер совпадает'
                return 'conflict', 'Путь занят файлом другого размера или типа'
        except NotADirectoryError:
            return 'conflict', 'Путь к файлу занят другим объектом'

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
            with os.fdopen(os.dup(descriptor), 'wb') as output:
                with closing(self.reader.stream(original, name, check)) as stream:
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
            try:
                with self._lock:
                    self._check(copy['id'])
                    self._validate_transfer(item, copy, source_volume, target_volume, source, parent, target, name)
                    if object_id(os.stat(temporary, dir_fd=target, follow_symlinks=False)) != staging['id']:
                        raise OSError('Промежуточный файл заменён во время копирования')
                    self._publish(target, temporary, name, target_volume.get('kind') == 'network')
            except DirectCopyRequired:
                try:
                    self._write_network(item, copy, source_volume, target_volume, source, parent, target, name,
                                        descriptor, staging, check)
                except FileExistsError:
                    return 'conflict', 'Файл появился в копии во время передачи'
            except FileExistsError:
                return 'conflict', 'Файл появился в копии во время передачи'
            return 'done', 'Скопирован'
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
