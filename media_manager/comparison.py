"""Read-only name comparisons using persistent directory lists, never file contents."""
from __future__ import annotations

import json
import os
import stat
import threading
import uuid
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import PurePosixPath

from .storage import StorageCatalog, now, relative_path
from .volume_identity import MARKER_FILES, copy_temporary, verify_identity


LABELS = {
    'names_found': 'Совпали имена', 'other_folder': 'Имя в другой папке',
    'names_missing': 'Не найдено по именам',
    'found': 'Есть на NAS', 'cached': 'Есть по сохранённым хэшам',
    'missing': 'Не найдено', 'candidate': 'Кандидат на совпадение',
    'unverified': 'Не проверено', 'skipped': 'Не сравнивается',
}
NAME_STATUSES = ('names_found', 'other_folder', 'names_missing', 'unverified', 'skipped')


def name_key(name):
    return unicodedata.normalize('NFC', name).casefold()


def parent_key(parent):
    return name_key(PurePosixPath(parent).name) if parent else ''


class Paused(Exception):
    pass


@contextmanager
def open_readonly(volume: dict, path: str, *, directory=False):
    """No symlinks, no special files, no crossing a mount boundary."""
    path = relative_path(path)
    descriptors = []
    flags = os.O_RDONLY | os.O_NOFOLLOW
    try:
        root = os.open(volume['mount_path'], flags | os.O_DIRECTORY)
        descriptors.append(root)
        device = os.fstat(root).st_dev
        if volume.get('device') is not None and device != volume['device']:
            raise OSError('Том был отключён или заменён')
        verify_identity(root, volume)
        parts = PurePosixPath(path).parts
        for index, part in enumerate(parts):
            is_directory = index < len(parts) - 1 or directory
            # NONBLOCK prevents a replaced FIFO from blocking before fstat.
            descriptor = os.open(part, flags | (os.O_DIRECTORY if is_directory else os.O_NONBLOCK), dir_fd=descriptors[-1])
            descriptors.append(descriptor)
            info = os.fstat(descriptor)
            if info.st_dev != device:
                raise OSError('Переход на другой том запрещён')
        descriptor = descriptors[-1]
        info = os.fstat(descriptor)
        if directory and not stat.S_ISDIR(info.st_mode):
            raise OSError('Нужна папка')
        if not directory and not stat.S_ISREG(info.st_mode):
            raise OSError('Содержимое этого типа файлов не читается')
        yield descriptor
        verify_identity(root, volume)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def sqlite_file_identifier(value: int) -> int | str:
    """Preserve opaque IDs outside SQLite's signed int64 without REAL coercion.

    Keep ordinary IDs unchanged so existing inventory/hash rows stay compatible.
    The nonnumeric prefix keeps INTEGER affinity from rounding a large decimal
    string through a floating-point value. No schema migration is necessary.
    """
    return value if -(1 << 63) <= value < (1 << 63) else f'fsid:{value}'


def fingerprint(info):
    return dict(size=info.st_size, mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns,
                inode=sqlite_file_identifier(info.st_ino), device=sqlite_file_identifier(info.st_dev))


class ComparisonCatalog:
    def __init__(self, storage: StorageCatalog):
        self.storage = storage
        self._lock = threading.RLock()
        self._thread = None
        self._stop = threading.Event()
        with self.storage.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS comparison_jobs (
                    id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    state TEXT NOT NULL, phase TEXT NOT NULL, reread INTEGER NOT NULL,
                    current_path TEXT NOT NULL DEFAULT '', message TEXT NOT NULL DEFAULT '',
                    hashed_bytes INTEGER NOT NULL DEFAULT 0, total_bytes INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS comparison_scans (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, side TEXT NOT NULL,
                    volume_id TEXT NOT NULL, root_path TEXT NOT NULL, state TEXT NOT NULL,
                    started_at TEXT, finished_at TEXT, error TEXT
                );
                CREATE TABLE IF NOT EXISTS comparison_entries (
                    id INTEGER PRIMARY KEY, scan_id INTEGER NOT NULL, path TEXT NOT NULL,
                    parent TEXT, name TEXT NOT NULL, kind TEXT NOT NULL, size INTEGER,
                    mtime_ns INTEGER, ctime_ns INTEGER, inode INTEGER, device INTEGER,
                    error TEXT, digest TEXT, hashed_at TEXT, cached INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(scan_id,path)
                );
                CREATE INDEX IF NOT EXISTS comparison_parent ON comparison_entries(scan_id,parent,path);
                CREATE INDEX IF NOT EXISTS comparison_content ON comparison_entries(scan_id,size,digest);
                CREATE INDEX IF NOT EXISTS comparison_scan_job ON comparison_scans(job_id,side);
                CREATE TABLE IF NOT EXISTS comparison_results (
                    entry_id INTEGER PRIMARY KEY, status TEXT NOT NULL, reason TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS comparison_hashes (
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, size INTEGER NOT NULL,
                    mtime_ns INTEGER NOT NULL, ctime_ns INTEGER NOT NULL, inode INTEGER NOT NULL,
                    device INTEGER NOT NULL, digest TEXT NOT NULL, hashed_at TEXT NOT NULL,
                    PRIMARY KEY(volume_id,path)
                );
                CREATE TABLE IF NOT EXISTS comparison_events (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, at TEXT NOT NULL,
                    level TEXT NOT NULL, message TEXT NOT NULL, path TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS comparison_event_job ON comparison_events(job_id,id);
            ''')
            additions = {
                'comparison_jobs': {'mode': "TEXT NOT NULL DEFAULT 'content'", 'reuse_index': 'INTEGER NOT NULL DEFAULT 1'},
                'comparison_scans': {'reused_from': 'INTEGER'},
                'comparison_entries': {'name_key': "TEXT NOT NULL DEFAULT ''", 'parent_key': "TEXT NOT NULL DEFAULT ''"},
            }
            for table, columns in additions.items():
                present = {r['name'] for r in db.execute('PRAGMA table_info(' + table + ')')}
                for name, declaration in columns.items():
                    if name not in present:
                        db.execute('ALTER TABLE ' + table + ' ADD COLUMN ' + name + ' ' + declaration)
            db.execute('CREATE INDEX IF NOT EXISTS comparison_names ON comparison_entries(scan_id,kind,name_key,parent_key)')
            interrupted = db.execute("SELECT id FROM comparison_jobs WHERE state IN ('running','pausing')").fetchall()
            for row in interrupted:
                db.execute("UPDATE comparison_jobs SET state='paused',message=?,updated_at=? WHERE id=?",
                           ('Приложение было остановлено. Продолжение запускается вручную.', now(), row['id']))
                self._event(db, row['id'], 'warning', 'Проверка прервана перезапуском приложения')

    @staticmethod
    def _event(db, job, level, message, path=''):
        db.execute('INSERT INTO comparison_events(job_id,at,level,message,path) VALUES (?,?,?,?,?)',
                   (job, now(), level, message, path))

    def _update(self, job, **values):
        values['updated_at'] = now()
        with self.storage.connect() as db:
            db.execute('UPDATE comparison_jobs SET ' + ','.join(k + '=?' for k in values) + ' WHERE id=?', (*values.values(), job))

    def _check(self):
        if self._stop.is_set():
            raise Paused()

    def create(self, source: dict, targets: list[dict], reread=False, *, background=True, reuse_index=True):
        scopes = []
        if not targets or len(targets) > 16:
            raise ValueError('Выбери от 1 до 16 областей поиска')
        for side, scope in [('source', source), *(('target', t) for t in targets)]:
            volume = self.storage.get_volume(scope['volume_id'])
            if volume['identity_status'] == 'unverified':
                raise ValueError('Сначала зарегистрируй сменный диск, чтобы не использовать индекс другого носителя')
            path = relative_path(scope.get('path', ''))
            for previous in scopes:
                if previous['volume_id'] == volume['id']:
                    a, b = previous['path'], path
                    if a == b or not a or not b or a.startswith(b + '/') or b.startswith(a + '/'):
                        raise ValueError('Источник и области поиска не должны пересекаться')
            scopes.append(dict(side=side, volume_id=volume['id'], path=path))
        with self._lock:
            self._assert_idle()
            job = uuid.uuid4().hex
            with self.storage.connect() as db:
                db.execute('INSERT INTO comparison_jobs(id,created_at,updated_at,state,phase,reread,mode,reuse_index) VALUES (?,?,?,?,?,?,?,?)',
                           (job, now(), now(), 'paused', 'index', 0, 'names', int(reuse_index)))
                for scope in scopes:
                    db.execute('INSERT INTO comparison_scans(job_id,side,volume_id,root_path,state) VALUES (?,?,?,?,?)',
                               (job, scope['side'], scope['volume_id'], scope['path'], 'pending'))
                self._event(db, job, 'info', 'Создана сверка только имён папок и файлов. Содержимое файлов не открывается.')
            if background:
                self.resume(job)
            return self.job(job)

    def _assert_idle(self):
        if self._thread and self._thread.is_alive():
            raise ValueError('Уже выполняется сверка. Сначала останови её.')

    def resume(self, job):
        with self._lock:
            self._assert_idle()
            report = self.job(job)
            if report['mode'] != 'names':
                if report['state'] in ('running', 'pausing'):
                    raise ValueError('Сначала останови старую сверку содержимого')
                source = next(s for s in report['scans'] if s['side'] == 'source')
                targets = [dict(volume_id=s['volume_id'], path=s['root_path']) for s in report['scans'] if s['side'] == 'target']
                return self.create(dict(volume_id=source['volume_id'], path=source['root_path']), targets, reuse_index=True)
            if report['state'] not in ('paused', 'failed'):
                raise ValueError('Эту проверку нельзя продолжить')
            self._stop.clear()
            self._update(job, state='running', message='Сверка имён по готовым спискам; отсутствующие списки будут собраны' )
            self._thread = threading.Thread(target=self.run, args=(job,), name='storage-compare', daemon=True)
            self._thread.start()
        return self.job(job)

    def pause(self, job):
        with self._lock:
            report = self.job(job)
            if report['state'] == 'running':
                self._stop.set()
                self._update(job, state='pausing', message='Остановка после текущего чтения')
        return self.job(job)

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def run(self, job):
        """Continue completed lists, reuse earlier inventories, and compare names only."""
        try:
            report = self.job(job)
            if report['mode'] != 'names':
                raise ValueError('Старый отчёт сохранён. Запусти новую сверку по именам.')
            with self.storage.connect() as db:
                db.execute('DELETE FROM comparison_results WHERE entry_id IN (SELECT e.id FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=?)', (job,))
                unfinished = [r['id'] for r in db.execute("SELECT id FROM comparison_scans WHERE job_id=? AND state!='complete'", (job,))]
                for scan in unfinished:
                    db.execute('DELETE FROM comparison_entries WHERE scan_id=?', (scan,))
                    db.execute("UPDATE comparison_scans SET state='pending',error=NULL,started_at=NULL,finished_at=NULL,reused_from=NULL WHERE id=?", (scan,))
                self._event(db, job, 'info', 'Начата сверка имён; размеры, даты и содержимое не сравниваются')
            self._update(job, state='running', phase='index', hashed_bytes=0, total_bytes=0, current_path='')
            volumes = None
            with self.storage.connect() as db:
                scans = [dict(r) for r in db.execute('SELECT * FROM comparison_scans WHERE job_id=? ORDER BY id', (job,))]
            for scan in scans:
                self._check()
                if scan['state'] == 'complete':
                    with self.storage.connect() as db:
                        db.execute('UPDATE comparison_scans SET reused_from=COALESCE(reused_from,id) WHERE id=?', (scan['id'],))
                    continue
                if report['reuse_index'] and self._reuse_inventory(job, scan):
                    continue
                if volumes is None:
                    volumes = {v['id']: v for v in self.storage.refresh(True)['volumes']}
                self._inventory(job, scan, volumes.get(scan['volume_id']))
            with self.storage.connect() as db:
                root = db.execute("SELECT e.error FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND s.side='source' AND e.parent IS NULL", (job,)).fetchone()
                if root is None or root['error']:
                    raise OSError('Нет списка источника. Подключи том или используй сохранённый полный индекс.')
            self._check()
            self._update(job, phase='names', current_path='', message='Сопоставление имён по спискам')
            self._classify_names(job)
            self._update(job, state='completed', phase='done', current_path='', message='Сверка имён завершена. Решения о файлах принимаешь ты.')
            with self.storage.connect() as db:
                self._event(db, job, 'info', 'Сверка имён завершена; содержимое файлов не открывалось')
        except Paused:
            self._update(job, state='paused', message='Остановлено. Готовые списки сохранены для продолжения.')
            with self.storage.connect() as db:
                self._event(db, job, 'info', 'Сверка остановлена пользователем или при закрытии Core')
        except Exception as error:
            self._update(job, state='failed', message=str(error))
            with self.storage.connect() as db:
                db.execute("UPDATE comparison_scans SET state='error',error=?,finished_at=? WHERE job_id=? AND state='running'", (str(error), now(), job))
                self._event(db, job, 'error', str(error))

    def _reuse_inventory(self, job, scan):
        with self.storage.connect() as db:
            previous = db.execute("""SELECT * FROM comparison_scans WHERE volume_id=? AND root_path=?
                AND state='complete' AND id!=? ORDER BY finished_at DESC,id DESC LIMIT 1""",
                (scan['volume_id'], scan['root_path'], scan['id'])).fetchone()
            if previous is None:
                return False
            # Old content-check inventories are reusable without touching the disks.
            # Nonnumeric IDs and old hash fields are copied exactly; names get Unicode keys.
            self._update(job, current_path='Используем сохранённый список: ' + scan['volume_id'] + '/' + scan['root_path'])
            db.create_function('comparison_name', 1, name_key)
            db.create_function('comparison_parent', 1, parent_key)
            db.execute('''INSERT INTO comparison_entries
                (scan_id,path,parent,name,kind,size,mtime_ns,ctime_ns,inode,device,error,name_key,parent_key)
                SELECT ?,path,parent,name,kind,size,mtime_ns,ctime_ns,inode,device,NULL,
                    comparison_name(name),comparison_parent(parent)
                FROM comparison_entries WHERE scan_id=?''', (scan['id'], previous['id']))
            db.execute("UPDATE comparison_scans SET state='complete',started_at=?,finished_at=?,error=NULL,reused_from=? WHERE id=?",
                       (previous['started_at'], previous['finished_at'], previous['id'], scan['id']))
            self._event(db, job, 'info', 'Использован готовый список от ' + (previous['finished_at'] or ''), scan['volume_id'] + '/' + scan['root_path'])
        return True

    def _inventory(self, job, scan, volume):
        with self.storage.connect() as db:
            db.execute("UPDATE comparison_scans SET state='running',started_at=? WHERE id=?", (now(), scan['id']))
            self._event(db, job, 'info', 'Обход: ' + (volume['name'] if volume else scan['volume_id']), scan['root_path'])
        errors = 0
        pending = [scan['root_path']]
        root_name = PurePosixPath(scan['root_path']).name if scan['root_path'] else (volume or {}).get('name', 'Источник')
        with self.storage.connect() as db:
            db.execute("INSERT INTO comparison_entries(scan_id,path,parent,name,kind,name_key,parent_key) VALUES (?,?,NULL,?,'directory',?,?)", (scan['id'], scan['root_path'], root_name, name_key(root_name), parent_key(scan['root_path'])))
        if not volume or volume['availability'] != 'online':
            errors += 1
            pending.clear()
            with self.storage.connect() as db:
                db.execute('UPDATE comparison_entries SET error=? WHERE scan_id=? AND parent IS NULL', ('Том отключён или недоступен', scan['id']))
                self._event(db, job, 'error', 'Том отключён или недоступен', scan['root_path'])
        while pending:
            self._check()
            path = pending.pop()
            self._update(job, current_path=volume['name'] + '/' + path)
            try:
                entries = []
                children = []
                with open_readonly(volume, path, directory=True) as descriptor:
                    with os.scandir(descriptor) as iterator:
                        for item in iterator:
                            self._check()
                            if copy_temporary(item.name) or (not path and item.name in MARKER_FILES):
                                continue
                            entry = dict(path=(path + '/' + item.name).lstrip('/'), parent=path, name=item.name,
                                         kind='file', size=None, mtime_ns=None, ctime_ns=None, inode=None, device=None, error=None)
                            entry['name_key'] = name_key(item.name)
                            entry['parent_key'] = parent_key(path)
                            try:
                                entry['kind'] = ('symlink' if item.is_symlink() else 'directory' if item.is_dir(follow_symlinks=False)
                                                 else 'file' if item.is_file(follow_symlinks=False) else 'special')
                                if entry['kind'] == 'directory':
                                    children.append(entry['path'])
                            except OSError as error:
                                entry['error'] = str(error)
                                errors += 1
                            entries.append(entry)
                pending.extend(children)
                timestamp = now()
                with self.storage.connect() as db:
                    db.executemany('''INSERT INTO comparison_entries
                        (scan_id,path,parent,name,kind,size,mtime_ns,ctime_ns,inode,device,error,name_key,parent_key)
                        VALUES (:scan_id,:path,:parent,:name,:kind,:size,:mtime_ns,:ctime_ns,:inode,:device,:error,:name_key,:parent_key)''',
                        [dict(e, scan_id=scan['id']) for e in entries])
                    # Successful directory reads also make the ordinary explorer usable offline.
                    cached = [dict(name=e['name'], path=e['path'], kind='file' if e['kind'] == 'special' else e['kind'],
                                   size=e['size'] if e['kind'] == 'file' else None,
                                   modified_at=None if e['mtime_ns'] is None else datetime.fromtimestamp(e['mtime_ns'] / 1e9, timezone.utc).isoformat(),
                                   **({'error': e['error']} if e['error'] else {})) for e in entries]
                    db.execute('INSERT OR REPLACE INTO directories VALUES (?,?,?,?)', (scan['volume_id'], path, timestamp, json.dumps(cached, ensure_ascii=False)))
                    for e in entries:
                        if e['error']:
                            self._event(db, job, 'error', e['error'], volume['name'] + '/' + e['path'])
            except OSError as error:
                errors += 1
                with self.storage.connect() as db:
                    db.execute('UPDATE comparison_entries SET error=? WHERE scan_id=? AND path=?', (str(error), scan['id'], path))
                    self._event(db, job, 'error', 'Не удалось прочитать папку: ' + str(error), volume['name'] + '/' + path)
        with self.storage.connect() as db:
            db.execute('UPDATE comparison_scans SET state=?,finished_at=?,error=? WHERE id=?',
                       ('error' if errors else 'complete', now(), f'Ошибок обхода: {errors}' if errors else None, scan['id']))
            self._event(db, job, 'warning' if errors else 'info', 'Обход завершён' + (f', ошибок: {errors}' if errors else ''), (volume['name'] if volume else scan['volume_id']) + '/' + scan['root_path'])

    def _classify_names(self, job):
        with self.storage.connect() as db:
            scans = [dict(s) for s in db.execute('SELECT * FROM comparison_scans WHERE job_id=?', (job,))]
            complete = all(s['state'] == 'complete' for s in scans if s['side'] == 'target')
            source = next(s for s in scans if s['side'] == 'source')
            names, pairs = set(), set()
            for row in db.execute("SELECT e.kind,e.name_key,e.parent_key FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND s.side='target' AND e.kind IN ('file','directory') AND e.error IS NULL", (job,)):
                names.add((row['kind'], row['name_key']))
                if row['kind'] == 'file':
                    pairs.add((row['name_key'], row['parent_key']))
            results = []
            for e in db.execute('SELECT id,parent,kind,error,name_key,parent_key FROM comparison_entries WHERE scan_id=?', (source['id'],)):
                if e['parent'] is None:
                    continue
                status, reason = 'unverified', 'Не все выбранные списки прочитаны полностью'
                if e['error']:
                    reason = e['error']
                elif e['kind'] not in ('file', 'directory'):
                    status, reason = 'skipped', 'Ссылки, вложенные тома и специальные файлы не обходятся'
                elif e['kind'] == 'file' and (e['name_key'], e['parent_key']) in pairs:
                    status, reason = 'names_found', 'Совпали имя файла и имя папки, в которой он лежит. Содержимое не проверялось.'
                elif (e['kind'], e['name_key']) in names:
                    status = 'names_found' if e['kind'] == 'directory' else 'other_folder'
                    reason = ('Найдены папки с таким названием. Файлы внутри отмечены отдельно.' if e['kind'] == 'directory'
                              else 'Такое имя файла есть в другой папке. Пути показаны ниже; решение принимаешь ты.')
                elif complete:
                    status, reason = 'names_missing', 'Имя не найдено в выбранных сохранённых списках. Содержимое не сравнивалось.'
                results.append((e['id'], status, reason))
                if len(results) >= 500:
                    self._check()
                    db.executemany('INSERT OR REPLACE INTO comparison_results VALUES (?,?,?)', results)
                    results.clear()
            self._check()
            db.executemany('INSERT OR REPLACE INTO comparison_results VALUES (?,?,?)', results)

    def jobs(self):
        with self.storage.connect() as db:
            ids = [r[0] for r in db.execute('SELECT id FROM comparison_jobs ORDER BY created_at DESC LIMIT 30')]
        return [self.job(job) for job in ids]

    def job(self, job):
        with self.storage.connect() as db:
            row = db.execute('SELECT * FROM comparison_jobs WHERE id=?', (job,)).fetchone()
            if row is None:
                raise KeyError('Проверка не найдена')
            result = dict(row)
            result['scans'] = [dict(r) for r in db.execute('SELECT s.*,v.name AS volume_name FROM comparison_scans s JOIN volumes v ON v.id=s.volume_id WHERE s.job_id=? ORDER BY s.id', (job,))]
            for scan in result['scans']:
                volume = self.storage.get_volume(scan['volume_id'])
                scan['volume_name'] = volume['display_name']
            result['counts'] = {r['status']: r['n'] for r in db.execute('''SELECT r.status,COUNT(*) AS n FROM comparison_results r JOIN comparison_entries e ON e.id=r.entry_id
                JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? GROUP BY r.status''', (job,))}
            result['indexed_files'] = db.execute("SELECT COUNT(*) FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND e.kind='file'", (job,)).fetchone()[0]
            result['indexed_directories'] = db.execute("SELECT COUNT(*) FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND e.kind='directory'", (job,)).fetchone()[0]
            result['errors'] = db.execute("SELECT COUNT(*) FROM comparison_events WHERE job_id=? AND level='error'", (job,)).fetchone()[0]
            return result

    def tree(self, job, path=None, status='', offset=0, limit=200):
        report = self.job(job)
        if status and status not in LABELS:
            raise ValueError('Неизвестный фильтр')
        scan = next(s for s in report['scans'] if s['side'] == 'source')
        path = scan['root_path'] if path is None else relative_path(path)
        if path != scan['root_path'] and (scan['root_path'] and not path.startswith(scan['root_path'] + '/')):
            raise ValueError('Папка вне источника')
        params = [scan['id'], path]
        where = 'e.scan_id=? AND e.parent=?'
        if status:
            where += ''' AND (r.status=? OR (e.kind='directory' AND EXISTS (
                SELECT 1 FROM comparison_entries child JOIN comparison_results cr ON cr.entry_id=child.id
                WHERE child.scan_id=e.scan_id AND child.path>=e.path||'/' AND child.path<e.path||'0' AND cr.status=?)))'''
            params.extend([status, status])
        with self.storage.connect() as db:
            total = db.execute('SELECT COUNT(*) FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE ' + where, params).fetchone()[0]
            rows = db.execute('SELECT e.*,r.status,r.reason FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE ' + where + " ORDER BY e.kind!='directory',e.name COLLATE NOCASE LIMIT ? OFFSET ?", (*params, limit, offset)).fetchall()
            entries = []
            for row in rows:
                e = dict(row)
                if e['kind'] == 'directory':
                    e['counts'] = self._counts(db, scan['id'], e['path'])
                entries.append(e)
        return dict(entries=entries, total=total, path=path, root_path=scan['root_path'])

    @staticmethod
    def _counts(db, scan, path):
        condition = ' AND e.path>=? AND e.path<?' if path else ''
        params = (scan, path + '/', path + '0') if path else (scan,)
        return {r['status']: r['n'] for r in db.execute('''SELECT r.status,COUNT(*) n FROM comparison_entries e JOIN comparison_results r ON r.entry_id=e.id
            WHERE e.scan_id=?''' + condition + ' GROUP BY r.status', params)}

    def detail(self, job, path=None):
        report = self.job(job)
        scan = next(s for s in report['scans'] if s['side'] == 'source')
        path = scan['root_path'] if path is None else relative_path(path)
        with self.storage.connect() as db:
            row = db.execute('SELECT e.*,r.status,r.reason FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE e.scan_id=? AND e.path=?', (scan['id'], path)).fetchone()
            if row is None:
                raise KeyError('Элемент ещё не проиндексирован')
            entry = dict(row)
            entry['metadata'] = self.storage.metadata(scan['volume_id'], path)
            matches = []
            if entry['kind'] == 'directory':
                entry['counts'] = self._counts(db, scan['id'], path)
            if report['mode'] == 'names' and entry['kind'] in ('directory', 'file'):
                matches = [dict(r) for r in db.execute('''SELECT e.path,e.name,e.kind,e.error,e.parent_key,s.id AS scan_id,s.finished_at AS indexed_at,s.reused_from,
                    v.name AS volume_name,s.volume_id,CASE WHEN e.parent_key=? THEN 1 ELSE 0 END AS same_folder
                    FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id JOIN volumes v ON v.id=s.volume_id
                    WHERE s.job_id=? AND s.side='target' AND e.kind=? AND e.name_key=? AND e.error IS NULL
                    ORDER BY same_folder DESC,v.name,e.path LIMIT 100''', (entry['parent_key'], job, entry['kind'], entry['name_key']))]
            elif report['mode'] != 'names' and entry['kind'] == 'file' and entry['size'] is not None:
                condition = 'e.digest=?' if entry['digest'] else 'e.size=?'
                matches = [dict(r) for r in db.execute('''SELECT e.path,e.size,e.digest,e.hashed_at,e.cached,e.error,v.name AS volume_name,s.volume_id
                    FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id JOIN volumes v ON v.id=s.volume_id
                    WHERE s.job_id=? AND s.side='target' AND e.kind='file' AND ''' + condition + ' ORDER BY v.name,e.path LIMIT 100',
                    (job, entry['digest'] or entry['size']))]

        return dict(entry=entry, matches=matches, matches_limit=100)

    def target_tree(self, job, scan_id, path=None, offset=0, limit=200):
        """Read one level of a target snapshot. Never visit the mounted filesystem."""
        with self.storage.connect() as db:
            scan = db.execute("SELECT s.*,v.name AS volume_name FROM comparison_scans s JOIN volumes v ON v.id=s.volume_id WHERE s.job_id=? AND s.id=? AND s.side='target'", (job, scan_id)).fetchone()
            if scan is None:
                raise KeyError('Область NAS не найдена в этой сверке')
            path = scan['root_path'] if path is None else relative_path(path)
            if scan['root_path'] and path != scan['root_path'] and not path.startswith(scan['root_path'] + '/'):
                raise ValueError('Папка вне выбранной области NAS')
            folder = db.execute('SELECT kind,error FROM comparison_entries WHERE scan_id=? AND path=?', (scan_id, path)).fetchone()
            if folder is None:
                raise KeyError('Папка отсутствует в сохранённом списке')
            if folder['kind'] != 'directory':
                raise ValueError('Раскрывать можно только папки из сохранённого списка')
            total = db.execute('SELECT COUNT(*) FROM comparison_entries WHERE scan_id=? AND parent=?', (scan_id, path)).fetchone()[0]
            entries = [dict(row, scan_id=scan_id) for row in db.execute("SELECT path,name,kind,error FROM comparison_entries WHERE scan_id=? AND parent=? ORDER BY kind!='directory',name COLLATE NOCASE LIMIT ? OFFSET ?", (scan_id, path, limit, offset))]
        return dict(entries=entries, total=total, path=path, scan_id=scan_id, volume_name=scan['volume_name'], error=folder['error'])

    def events(self, job, before=None, limit=100):
        self.job(job)
        with self.storage.connect() as db:
            rows = db.execute('SELECT * FROM comparison_events WHERE job_id=?' + (' AND id<?' if before else '') + ' ORDER BY id DESC LIMIT ?',
                              (job, before, limit) if before else (job, limit)).fetchall()
        return [dict(r) for r in rows]
