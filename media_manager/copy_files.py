"""Explicit, journalled creation of missing copies; existing paths are never replaced."""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import ctypes
import errno
import json
import os
from pathlib import PurePosixPath
import stat
import sys
import threading
import time
from uuid import uuid4

from .comparison import fingerprint, open_readonly
from .paired_comparison import absolute_scope_path
from .storage import now, relative_path


class CopyStopped(Exception):
    pass


class DirectCopyRequired(Exception):
    pass


def object_id(info):
    data = fingerprint(info)
    return {key: data[key] for key in ('device', 'inode')}


def publish_exclusive(parent, temporary, name):
    """Publish a complete file atomically, including when a target appears concurrently."""
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, 'renameatx_np' if sys.platform == 'darwin' else 'renameat2', None)
    if function is not None:
        function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        function.restype = ctypes.c_int
        # Darwin sys/stdio.h: RENAME_EXCL; Linux: RENAME_NOREPLACE.
        if function(parent, os.fsencode(temporary), parent, os.fsencode(name), 4 if sys.platform == 'darwin' else 1):
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code), name)
    else:
        os.link(temporary, name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
        os.unlink(temporary, dir_fd=parent)


@contextmanager
def destination_directory(volume, scope, path, *, create=False):
    """Create only children of the selected copy root, traversing without symlinks."""
    descriptors = []
    with open_readonly(volume, scope['path'], directory=True) as root:
        descriptor, device = root, os.fstat(root).st_dev
        try:
            for part in PurePosixPath(relative_path(path)).parts:
                if create:
                    try:
                        os.mkdir(part, 0o755, dir_fd=descriptor)
                    except FileExistsError:
                        pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                descriptors.append(child)
                if os.fstat(child).st_dev != device:
                    raise OSError('Переход на другой том запрещён')
                descriptor = child
            yield descriptor
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)


class MissingCopyCatalog:
    def __init__(self, pairs):
        self.pairs, self.storage = pairs, pairs.storage
        self._thread = None
        self._stop = threading.Event()
        self._progress_at = 0
        self._closing = False
        with self.storage.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS copy_operations (
                    id TEXT PRIMARY KEY, report_id TEXT NOT NULL REFERENCES paired_jobs(id),
                    copy_id TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, data TEXT NOT NULL, message TEXT NOT NULL DEFAULT '',
                    current_path TEXT NOT NULL DEFAULT '', total_files INTEGER NOT NULL,
                    total_directories INTEGER NOT NULL, total_bytes INTEGER NOT NULL,
                    copied_files INTEGER NOT NULL DEFAULT 0, copied_directories INTEGER NOT NULL DEFAULT 0,
                    copied_bytes INTEGER NOT NULL DEFAULT 0, checked_items INTEGER NOT NULL DEFAULT 0,
                    skipped INTEGER NOT NULL DEFAULT 0, errors INTEGER NOT NULL DEFAULT 0,
                    verification_id TEXT REFERENCES paired_jobs(id)
                );
                CREATE INDEX IF NOT EXISTS copy_operations_report ON copy_operations(report_id,created_at);
                CREATE TABLE IF NOT EXISTS copy_operation_items (
                    operation_id TEXT NOT NULL REFERENCES copy_operations(id), position INTEGER NOT NULL,
                    path TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'pending', message TEXT NOT NULL DEFAULT '', staging TEXT,
                    PRIMARY KEY(operation_id,path), UNIQUE(operation_id,position)
                );
            ''')
            db.execute("UPDATE copy_operations SET state='interrupted',message=?,updated_at=? WHERE state IN ('running','stopping')",
                       ('Копирование прервано перезапуском. Заново сверь файлы перед повтором.', now()))
        pairs.transfers = self

    def busy(self):
        return self._thread is not None and self._thread.is_alive()

    def _update(self, operation, **values):
        values['updated_at'] = now()
        with self.storage.connect() as db:
            db.execute('UPDATE copy_operations SET ' + ','.join(key + '=?' for key in values) + ' WHERE id=?',
                       (*values.values(), operation))

    def job(self, operation):
        with self.storage.connect() as db:
            row = db.execute('SELECT * FROM copy_operations WHERE id=?', (operation,)).fetchone()
        if row is None:
            raise KeyError('Копирование не найдено')
        result = dict(row)
        result.update(json.loads(result.pop('data')))
        with self.storage.connect() as db:
            result['incomplete_files'] = sum(bool(json.loads(r['staging']).get('final')) for r in db.execute(
                "SELECT staging FROM copy_operation_items WHERE operation_id=? AND staging IS NOT NULL AND state!='done'", (operation,)))
        return result

    def incomplete(self, copy_id):
        with self.storage.connect() as db:
            rows = db.execute('''SELECT i.path,i.staging,i.state FROM copy_operation_items i JOIN copy_operations o
                ON o.id=i.operation_id WHERE o.copy_id=? AND (i.staging IS NOT NULL OR i.state='done')
                ORDER BY o.created_at''', (copy_id,))
            result = {}
            for row in rows:
                if row['state'] == 'done':
                    result.pop(row['path'], None)
                elif row['staging'] and (value := json.loads(row['staging'])).get('final'):
                    result[row['path']] = value['identity']
            return result

    def latest(self, report):
        with self.storage.connect() as db:
            row = db.execute('''SELECT id FROM copy_operations WHERE report_id=? OR verification_id=?
                                ORDER BY created_at DESC LIMIT 1''', (report, report)).fetchone()
        return self.job(row[0]) if row else None

    def items(self, operation, offset=0, limit=200):
        job = self.job(operation)
        with self.storage.connect() as db:
            rows = [dict(json.loads(r['data']), path=r['path'], kind=r['kind'], state=r['state'], message=r['message'],
                         incomplete=bool(r['staging'] and json.loads(r['staging']).get('final') and r['state'] != 'done'))
                    for r in db.execute('SELECT * FROM copy_operation_items WHERE operation_id=? ORDER BY position LIMIT ? OFFSET ?',
                                        (operation, limit, offset))]
        return {'items': rows, 'total': job['total_files'] + job['total_directories'], 'offset': offset}

    def _volumes(self, scopes):
        current = {v['id']: v for v in self.storage.refresh(True)['volumes']}
        result = {}
        for side, scope in scopes.items():
            volume = current.get(scope['volume_id'])
            if not volume or volume['availability'] != 'online':
                raise ValueError('Оба тома должны быть подключены.')
            if volume['identity_status'] in ('unverified', 'legacy'):
                raise ValueError('Сначала подтверди подключённые диски.')
            result[side] = volume
        return result

    @staticmethod
    def _roots(scopes, volumes):
        result, descriptors = {}, {}
        with ExitStack() as stack:
            for side, scope in scopes.items():
                descriptor = stack.enter_context(open_readonly(volumes[side], scope['path'], directory=True))
                descriptors[side] = descriptor
                result[side] = object_id(os.fstat(descriptor))
            if result['left']['device'] == result['right']['device']:
                for side, other in (('left', 'right'), ('right', 'left')):
                    current = os.dup(descriptors[side])
                    try:
                        while True:
                            identity = object_id(os.fstat(current))
                            if identity == result[other]:
                                raise ValueError('Основная папка и копия пересекаются.')
                            parent = os.open('..', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
                            parent_identity = object_id(os.fstat(parent))
                            os.close(current)
                            current = parent
                            if parent_identity == identity or parent_identity['device'] != identity['device']:
                                break
                    finally:
                        os.close(current)
        return result

    def _binding(self, job):
        current = self.pairs._pair(job['copy_id'])
        if any(current[side][key] != job['scopes'][side][key]
               for side in ('left', 'right') for key in ('id', 'volume_id', 'path')):
            raise ValueError('Связь папок изменилась. Заново сверь файлы.')

    def candidates(self, report_id):
        with self.storage.connect() as db:
            blocked = {r['path'] for r in db.execute("SELECT path FROM paired_rows WHERE job_id=? AND status IN ('conflict','unverified','skipped','copy_incomplete')", (report_id,))}
            rows = [json.loads(r['data']) for r in db.execute("SELECT data FROM paired_rows WHERE job_id=? AND status='missing_copy' ORDER BY position", (report_id,))]
        items = []
        for row in rows:
            path, source = relative_path(row['path']), row['left']
            if not path or source['kind'] not in ('file', 'directory') or source.get('error'):
                continue
            if any(str(parent) in blocked for parent in PurePosixPath(path).parents):
                continue
            if source['kind'] == 'file' and any(source.get(key) is None for key in ('size', 'mtime_ns', 'ctime_ns', 'inode', 'device')):
                continue
            items.append(dict(path=path, kind=source['kind'], source=source, size=source.get('size') or 0))
        return items

    def plan(self, report_id):
        with self.pairs._lock:
            self.pairs._idle()
            report = self.pairs.job(report_id)
            if report['mode'] != 'files' or report['state'] != 'completed':
                raise ValueError('Сначала заверши сверку файлов.')
            self._binding(report)
            volumes = self._volumes(report['scopes'])
            roots = self._roots(report['scopes'], volumes)
            items = self.candidates(report_id)
            if not items:
                raise ValueError('Отсутствующих элементов для копирования нет.')
            # SMB directory enumeration can retain old timestamp metadata. Freeze
            # fresh descriptor metadata in the plan the user actually confirms.
            for item in items:
                if item['kind'] == 'file':
                    with open_readonly(volumes['left'], item['source']['path']) as descriptor:
                        current = fingerprint(os.fstat(descriptor))
                    item['source'].update(current)
                    item['size'] = current['size']
            operation, timestamp = uuid4().hex, now()
            data = {'scopes': report['scopes'], 'roots': roots,
                    'volumes': {s: {k: v.get(k) for k in ('id', 'mount_path', 'device', 'identity_status', 'marker_id')}
                                for s, v in volumes.items()}}
            with self.storage.connect() as db:
                db.execute('''INSERT INTO copy_operations
                    (id,report_id,copy_id,state,created_at,updated_at,data,total_files,total_directories,total_bytes)
                    VALUES (?,?,?,'planned',?,?,?,?,?,?)''',
                           (operation, report_id, report['copy_id'], timestamp, timestamp, json.dumps(data, ensure_ascii=False),
                            sum(i['kind'] == 'file' for i in items), sum(i['kind'] == 'directory' for i in items),
                            sum(i['size'] for i in items if i['kind'] == 'file')))
                db.executemany('INSERT INTO copy_operation_items (operation_id,position,path,kind,data) VALUES (?,?,?,?,?)',
                               [(operation, position, i['path'], i['kind'], json.dumps(i, ensure_ascii=False)) for position, i in enumerate(items)])
            return self.job(operation)

    def start(self, operation, *, background=True):
        with self.pairs._lock:
            self.pairs._idle()
            job = self.job(operation)
            if job['state'] != 'planned':
                raise ValueError('Этот план уже запускался. Заново сверь файлы перед повтором.')
            self._binding(job)
            volumes = self._volumes(job['scopes'])
            self._validate(job, volumes)
            self._stop.clear()
            self._update(operation, state='running', message='Копируем только отсутствующее из 00-main')
            if background:
                self._thread = threading.Thread(target=self.run, args=(operation,), name='copy-missing', daemon=True)
                self._thread.start()
        return self.job(operation)

    def _validate(self, job, volumes):
        self._binding(job)
        if self._roots(job['scopes'], volumes) != job['roots']:
            raise OSError('Основная папка или папка копии была заменена. Заново сверь файлы.')
        for side, volume in volumes.items():
            if any(volume.get(key) != job['volumes'][side].get(key) for key in ('mount_path', 'device', 'marker_id')):
                raise OSError('Том изменился после подготовки плана. Заново сверь файлы.')

    def stop(self, operation):
        with self.pairs._lock:
            if self.job(operation)['state'] == 'running':
                self._stop.set()
                self._update(operation, state='stopping', message='Останавливаем копирование')
        return self.job(operation)

    def close(self):
        self._closing = True
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _check(self):
        if self._stop.is_set():
            raise CopyStopped()

    def _item(self, operation, path, **values):
        with self.storage.connect() as db:
            db.execute('UPDATE copy_operation_items SET ' + ','.join(k + '=?' for k in values) + ' WHERE operation_id=? AND path=?',
                       (*values.values(), operation, path))

    def _cleanup_staging(self, job, volumes):
        with self.storage.connect() as db:
            rows = list(db.execute('''SELECT i.operation_id,i.path,i.staging FROM copy_operation_items i
                JOIN copy_operations o ON o.id=i.operation_id WHERE o.copy_id=? AND i.staging IS NOT NULL''', (job['copy_id'],)))
        for row in rows:
            staging = json.loads(row['staging'])
            if staging.get('final'):
                continue  # Never remove an existing final name, including an incomplete copy.
            parent = str(PurePosixPath(row['path']).parent)
            try:
                with destination_directory(volumes['right'], job['scopes']['right'], '' if parent == '.' else parent) as descriptor:
                    info = os.stat(staging['name'], dir_fd=descriptor, follow_symlinks=False)
                    if stat.S_ISREG(info.st_mode) and object_id(info) == staging['identity']:
                        os.unlink(staging['name'], dir_fd=descriptor)
                    else:
                        raise OSError('Промежуточный файл был заменён; он оставлен на диске.')
            except FileNotFoundError:
                pass
            self._item(row['operation_id'], row['path'], staging=None)

    def _copy_file(self, job, item, volumes, completed_bytes):
        direct = volumes['right'].get('kind') == 'network'
        try:
            return self._write_file(job, item, volumes, completed_bytes, direct=direct)
        except DirectCopyRequired:
            return self._write_file(job, item, volumes, completed_bytes, direct=True)

    def _write_file(self, job, item, volumes, completed_bytes, *, direct):
        path, source = item['path'], item['source']
        parent = str(PurePosixPath(path).parent)
        parent = '' if parent == '.' else parent
        name = PurePosixPath(path).name
        with open_readonly(volumes['left'], source['path']) as original:
            info = os.fstat(original)
            expected = fingerprint(info)
            if any(source.get(key) != value for key, value in expected.items()):
                raise OSError('Исходный файл изменился после сверки. Заново сверь файлы.')
            with destination_directory(volumes['right'], job['scopes']['right'], parent, create=True) as target:
                try:
                    os.stat(name, dir_fd=target, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    return 'skipped', 'Уже существует в копии'
                capacity = os.fstatvfs(target)
                if capacity.f_bavail * (capacity.f_frsize or capacity.f_bsize) < source['size']:
                    raise OSError('Недостаточно свободного места в копии')
                temporary = name if direct else '.media-actu-copy-' + job['id'] + '-' + uuid4().hex + '.part'
                try:
                    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644 if direct else 0o600, dir_fd=target)
                except FileExistsError:
                    return 'skipped', 'Уже появился в копии; существующий файл сохранён'
                identity = object_id(os.fstat(descriptor))
                complete = False
                try:
                    self._item(job['id'], path, staging=json.dumps({'name': temporary, 'identity': identity, 'final': direct}))
                    copied = 0
                    while True:
                        self._check()
                        chunk = os.read(original, 1024 * 1024)
                        if not chunk:
                            break
                        copied += len(chunk)
                        if copied > source['size']:
                            raise OSError('Исходный файл вырос во время копирования')
                        view = memoryview(chunk)
                        while view:
                            written = os.write(descriptor, view)
                            if written <= 0:
                                raise OSError('Не удалось записать файл')
                            view = view[written:]
                        if time.monotonic() - self._progress_at > .5:
                            self._update(job['id'], copied_bytes=completed_bytes + copied)
                            self._progress_at = time.monotonic()
                    if copied != source['size'] or fingerprint(os.fstat(original)) != expected:
                        raise OSError('Исходный файл изменился во время копирования')
                    if os.fstat(descriptor).st_size != copied:
                        raise OSError('Размер записанного файла не совпал')
                    if not direct:
                        os.fchmod(descriptor, 0o644)
                        os.utime(descriptor, ns=(info.st_atime_ns, info.st_mtime_ns))
                    os.fsync(descriptor)
                    self._check()
                    self._validate(job, volumes)
                    with open_readonly(volumes['left'], source['path']) as current:
                        if fingerprint(os.fstat(current)) != expected:
                            raise OSError('Исходный файл заменён во время копирования')
                    with destination_directory(volumes['right'], job['scopes']['right'], parent) as current:
                        if object_id(os.fstat(current)) != object_id(os.fstat(target)):
                            raise OSError('Целевая папка заменена во время копирования')
                    if object_id(os.stat(temporary, dir_fd=target, follow_symlinks=False)) != identity:
                        raise OSError('Промежуточный файл был заменён')
                    if not direct:
                        try:
                            publish_exclusive(target, temporary, name)
                        except FileExistsError:
                            return 'skipped', 'Уже появился в копии; существующий файл сохранён'
                        except OSError as error:
                            if error.errno in (errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS, errno.EINVAL):
                                raise DirectCopyRequired() from error
                            raise
                    complete = True
                    return 'done', ''
                finally:
                    os.close(descriptor)
                    if not direct:
                        try:
                            if object_id(os.stat(temporary, dir_fd=target, follow_symlinks=False)) == identity:
                                os.unlink(temporary, dir_fd=target)
                        except FileNotFoundError:
                            pass
                    if not direct or complete:
                        self._item(job['id'], path, staging=None)

    def run(self, operation, *, recheck=True):
        state, message = 'completed', 'Копирование завершено'
        counters = dict(copied_files=0, copied_directories=0, copied_bytes=0, checked_items=0, skipped=0, errors=0)
        try:
            job = self.job(operation)
            volumes = self._volumes(job['scopes'])
            self._validate(job, volumes)
            self._cleanup_staging(job, volumes)
            with self.storage.connect() as db:
                items = [json.loads(r['data']) for r in db.execute('SELECT data FROM copy_operation_items WHERE operation_id=? ORDER BY position', (operation,))]
            for item in items:
                self._check()
                self._validate(job, volumes)
                self._update(operation, current_path=item['path'])
                try:
                    if item['kind'] == 'directory':
                        with open_readonly(volumes['left'], item['source']['path'], directory=True):
                            try:
                                with destination_directory(volumes['right'], job['scopes']['right'], item['path']):
                                    pass
                            except FileNotFoundError:
                                with destination_directory(volumes['right'], job['scopes']['right'], item['path'], create=True):
                                    pass
                                result, detail = 'done', ''
                            else:
                                result, detail = 'skipped', 'Папка уже существует'
                    else:
                        result, detail = self._copy_file(job, item, volumes, counters['copied_bytes'])
                    if result == 'done':
                        counters['copied_files' if item['kind'] == 'file' else 'copied_directories'] += 1
                        if item['kind'] == 'file':
                            counters['copied_bytes'] += item['size']
                    else:
                        counters['skipped'] += 1
                except OSError as error:
                    result, detail = 'error', str(error)
                    counters['errors'] += 1
                self._item(operation, item['path'], state=result, message=detail)
                counters['checked_items'] += 1
                self._update(operation, **counters)
        except CopyStopped:
            state, message = 'stopped', 'Копирование остановлено. Готовые файлы сохранены.'
        except Exception as error:
            state, message = 'failed', str(error)
        finally:
            with self.pairs._lock:
                self._thread = None
                verification = None
                incomplete = self.job(operation)['incomplete_files']
                if incomplete:
                    message += f' · Незавершённых файлов: {incomplete}. Они оставлены в копии для ручного разбора.'
                if recheck and not self._closing and (counters['copied_files'] or counters['copied_directories'] or counters['skipped'] or incomplete):
                    try:
                        verification = self.pairs.create(job['copy_id'], 'files', job['report_id'], method='size')['id']
                    except (KeyError, ValueError, OSError) as error:
                        message += ' · Обнови сверку: ' + str(error)
                if counters['errors']:
                    message += f" · Ошибок: {counters['errors']}"
                self._update(operation, state=state, message=message, current_path='', verification_id=verification, **counters)
