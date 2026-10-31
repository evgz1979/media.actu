"""Read-only, two-sided comparisons of a registered main folder and one copy."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import PurePosixPath
import threading
import time
from uuid import uuid4

from .comparison import Paused, fingerprint, open_readonly
from .storage import now, relative_path
from .volume_identity import service_file


STATUS_LABELS = {
    'both': 'Есть в обеих', 'missing_copy': 'Нет в копии', 'extra_copy': 'Только в копии',
    'same': 'Совпадает', 'different': 'Отличается', 'conflict': 'Разный тип',
    'same_size': 'Имя и размер совпали', 'size_different': 'Размер отличается',
    'copy_incomplete': 'Копия не завершена',
    'unverified': 'Не проверено', 'skipped': 'Не сравнивается',
}
DECISIONS = {'keep': 'Оставить в копии', 'add_main': 'Добавить в 00-main',
             'move': 'Подготовить перенос', 'remove': 'Подготовить удаление'}


def absolute_scope_path(scope, path):
    return '/'.join(part for part in (scope['path'], relative_path(path)) if part)


class PairedComparisonCatalog:
    def __init__(self, storage, copies, legacy=None):
        self.storage, self.copies, self.legacy = storage, copies, legacy
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self._flush_at = 0
        self.transfers = None
        with storage.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS paired_jobs (
                    id TEXT PRIMARY KEY, copy_id TEXT NOT NULL, mode TEXT NOT NULL,
                    state TEXT NOT NULL, phase TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, scopes TEXT NOT NULL, base_job_id TEXT,
                    left_complete INTEGER NOT NULL DEFAULT 0, right_complete INTEGER NOT NULL DEFAULT 0,
                    current_path TEXT NOT NULL DEFAULT '', message TEXT NOT NULL DEFAULT '',
                    hashed_bytes INTEGER NOT NULL DEFAULT 0, total_bytes INTEGER NOT NULL DEFAULT 0,
                    checked_files INTEGER NOT NULL DEFAULT 0, total_files INTEGER NOT NULL DEFAULT 0,
                    indexed_directories INTEGER NOT NULL DEFAULT 0,
                    errors INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS paired_jobs_copy ON paired_jobs(copy_id,created_at);
                CREATE TABLE IF NOT EXISTS paired_entries (
                    job_id TEXT NOT NULL REFERENCES paired_jobs(id), side TEXT NOT NULL,
                    path TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(job_id,side,path)
                );
                CREATE TABLE IF NOT EXISTS paired_rows (
                    job_id TEXT NOT NULL REFERENCES paired_jobs(id), position INTEGER NOT NULL,
                    path TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(job_id,path), UNIQUE(job_id,position)
                );
                CREATE TABLE IF NOT EXISTS paired_decisions (
                    job_id TEXT NOT NULL REFERENCES paired_jobs(id), path TEXT NOT NULL,
                    action TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(job_id,path)
                );
            ''')
            if 'indexed_directories' not in {r['name'] for r in db.execute('PRAGMA table_info(paired_jobs)')}:
                db.execute('ALTER TABLE paired_jobs ADD COLUMN indexed_directories INTEGER NOT NULL DEFAULT 0')
            # Existing file reports checked content; preserve their meaning on upgrade.
            if 'method' not in {r['name'] for r in db.execute('PRAGMA table_info(paired_jobs)')}:
                db.execute("ALTER TABLE paired_jobs ADD COLUMN method TEXT NOT NULL DEFAULT 'sha256'")
            db.execute("UPDATE paired_jobs SET state='paused',message=?,updated_at=? WHERE state IN ('running','pausing')",
                       ('Проверка прервана перезапуском. Можно продолжить.', now()))

    def busy(self):
        return (self._thread is not None and self._thread.is_alive()) or bool(self.transfers and self.transfers.busy())

    def _idle(self):
        if self.busy():
            raise ValueError('Другая сверка ещё выполняется. Сначала останови её.')
        if self.legacy:
            self.legacy._assert_idle()

    def _update(self, job, **values):
        values['updated_at'] = now()
        with self.storage.connect() as db:
            db.execute('UPDATE paired_jobs SET ' + ','.join(k + '=?' for k in values) + ' WHERE id=?',
                       (*values.values(), job))

    def _check(self):
        if self._stop.is_set():
            raise Paused()

    def _pair(self, copy_id):
        for group in self.copies.groups():
            if any(copy['id'] == copy_id for copy in group.get('released_copies', [])):
                raise ValueError('Номер прежней привязки освобождён. Для неё доступна только история.')
            for copy in group['copies']:
                if copy['id'] == copy_id:
                    if not group.get('connected', True) or not copy.get('connected', True):
                        raise ValueError('Связь отключена. Сначала подключи её в разделе «Отключённые».')
                    return {'left': group['main'], 'right': copy}
        raise KeyError('Связь с копией не найдена')

    def create(self, copy_id, mode='folders', base_job_id=None, *, method='size', background=True):
        if mode not in ('folders', 'files'):
            raise ValueError('Неизвестный вид сверки')
        if method not in ('size', 'sha256'):
            raise ValueError('Неизвестный метод сверки файлов')
        scopes = self._pair(copy_id)
        if mode == 'files':
            previous = self.job(base_job_id)
            if previous['copy_id'] != copy_id or previous['state'] != 'completed':
                raise ValueError('Сначала заверши сверку папок этой пары.')
            for side in ('left', 'right'):
                if any(scopes[side][key] != previous['scopes'][side][key] for key in ('id', 'volume_id', 'path')):
                    raise ValueError('Связь изменилась. Сначала заново сверь папки.')
        for scope in scopes.values():
            volume = self.storage.get_volume(scope['volume_id'])
            if volume['identity_status'] in ('unverified', 'legacy'):
                raise ValueError('Сначала подтверди подключённый диск.')
        with self._lock:
            self._idle()
            job, timestamp = uuid4().hex, now()
            with self.storage.connect() as db:
                db.execute('''INSERT INTO paired_jobs
                    (id,copy_id,mode,state,phase,created_at,updated_at,scopes,base_job_id,method)
                    VALUES (?,?,?,'paused','index',?,?,?,?,?)''',
                           (job, copy_id, mode, timestamp, timestamp, json.dumps(scopes, ensure_ascii=False), base_job_id, method))
            if background:
                self.resume(job)
        return self.job(job)

    def resume(self, job):
        with self._lock:
            self._idle()
            report = self.job(job)
            if report['state'] not in ('paused', 'failed'):
                raise ValueError('Эту сверку нельзя продолжить.')
            self._pair(report['copy_id'])
            self._stop.clear()
            self._update(job, state='running', message='Читаем выбранную пару папок')
            self._thread = threading.Thread(target=self.run, args=(job,), name='paired-compare', daemon=True)
            self._thread.start()
        return self.job(job)

    def pause(self, job):
        with self._lock:
            if self.job(job)['state'] == 'running':
                self._stop.set()
                self._update(job, state='pausing', message='Остановка после текущего чтения')
        return self.job(job)

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def job(self, job):
        with self.storage.connect() as db:
            row = db.execute('SELECT * FROM paired_jobs WHERE id=?', (job,)).fetchone()
            if row is None:
                raise KeyError('Сверка пары не найдена')
            result = dict(row)
            result['counts'] = {r['status']: r['n'] for r in db.execute(
                'SELECT status,COUNT(*) n FROM paired_rows WHERE job_id=? GROUP BY status', (job,))}
            result['row_count'] = db.execute('SELECT COUNT(*) FROM paired_rows WHERE job_id=?', (job,)).fetchone()[0]
            result['root_errors'] = {r['side']: json.loads(r['data'])['error'] for r in db.execute(
                "SELECT side,data FROM paired_entries WHERE job_id=? AND path=''", (job,)) if json.loads(r['data']).get('error')}
        result['scopes'] = json.loads(result['scopes'])
        result['copy_operation'] = self.transfers.latest(job) if self.transfers else None
        result['copyable_count'] = len(self.transfers.candidates(job)) if self.transfers and result['mode'] == 'files' and result['state'] == 'completed' else 0
        return result

    def jobs(self, copy_id=None):
        with self.storage.connect() as db:
            ids = [r[0] for r in db.execute('SELECT id FROM paired_jobs' + (' WHERE copy_id=?' if copy_id else '') +
                                          ' ORDER BY created_at DESC LIMIT 30', (copy_id,) if copy_id else ())]
        return [self.job(job) for job in ids]

    def _save_entry(self, db, job, side, path, data):
        db.execute('INSERT OR REPLACE INTO paired_entries VALUES (?,?,?,?)',
                   (job, side, path, json.dumps(data, ensure_ascii=False)))

    def _entries(self, job, side):
        with self.storage.connect() as db:
            return {r['path']: json.loads(r['data']) for r in db.execute(
                'SELECT path,data FROM paired_entries WHERE job_id=? AND side=?', (job, side))}

    def _inventory(self, job, side, scope, volume, files):
        with self.storage.connect() as db:
            db.execute('DELETE FROM paired_entries WHERE job_id=? AND side=?', (job, side))
            self._save_entry(db, job, side, '', {'kind': 'directory', 'path': scope['path'], 'error': None})
        pending = ['']
        while pending:
            self._check()
            path = pending.pop()
            actual = absolute_scope_path(scope, path)
            self._update(job, current_path=scope['volume_name'] + ' /' + actual)
            try:
                if not volume or volume['availability'] != 'online':
                    raise OSError('Том отключён или недоступен')
                entries, children = [], []
                with open_readonly(volume, actual, directory=True) as descriptor:
                    device = os.fstat(descriptor).st_dev
                    with os.scandir(descriptor) as iterator:
                        for item in iterator:
                            self._check()
                            if item.name.startswith('._') or item.name == '.DS_Store' or service_file(item.name,volume_root=not actual):
                                continue
                            relative = '/'.join(p for p in (path, item.name) if p)
                            entry = {'path': absolute_scope_path(scope, relative), 'name': item.name, 'error': None}
                            try:
                                entry['kind'] = ('symlink' if item.is_symlink() else 'directory' if item.is_dir(follow_symlinks=False)
                                                 else 'file' if item.is_file(follow_symlinks=False) else 'special')
                                if entry['kind'] == 'directory':
                                    children.append(relative)
                                elif files and entry['kind'] == 'file':
                                    info = item.stat(follow_symlinks=False)
                                    entry.update(fingerprint(info))
                                    if info.st_dev != device:
                                        entry['kind'] = 'mount'
                            except OSError as error:
                                entry.update(kind=entry.get('kind', 'unknown'), error=str(error))
                            entries.append((relative, entry))
                with self.storage.connect() as db:
                    for relative, entry in entries:
                        self._save_entry(db, job, side, relative, entry)
                    # Preserve successful reads for ordinary browsing and properties, too.
                    cached = [{'name': e['name'], 'path': e['path'], 'kind': e['kind'], 'size': e.get('size'),
                               'modified_at': None, **({'error': e['error']} if e['error'] else {})} for _, e in entries]
                    db.execute('INSERT OR REPLACE INTO directories VALUES (?,?,?,?)',
                               (scope['volume_id'], actual, now(), json.dumps(cached, ensure_ascii=False)))
                    db.execute('UPDATE paired_jobs SET indexed_directories=indexed_directories+1 WHERE id=?', (job,))
                pending.extend(reversed(children))
            except OSError as error:
                with self.storage.connect() as db:
                    row = db.execute('SELECT data FROM paired_entries WHERE job_id=? AND side=? AND path=?',
                                     (job, side, path)).fetchone()
                    entry = json.loads(row['data'])
                    entry['error'] = str(error)
                    self._save_entry(db, job, side, path, entry)
        self._update(job, **{side + '_complete': 1})

    def _hash(self, job, side, entry, volume, counters):
        try:
            if not volume or volume['availability'] != 'online':
                raise OSError('Том отключён или недоступен')
            with open_readonly(volume, entry['path']) as descriptor:
                before = fingerprint(os.fstat(descriptor))
                if any(entry.get(k) != v for k, v in before.items()):
                    raise OSError('Файл изменился после сбора списка. Запусти новую сверку.')
                if entry.get('digest'):
                    counters['hashed_bytes'] += before['size']
                else:
                    digest = hashlib.sha256()
                    read_bytes = 0
                    while True:
                        self._check()
                        chunk = os.read(descriptor, 1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        read_bytes += len(chunk)
                        if read_bytes > before['size']:
                            raise OSError('Файл вырос во время чтения')
                        counters['hashed_bytes'] += len(chunk)
                        if time.monotonic() - self._flush_at > .5:
                            self._update(job, **counters)
                            self._flush_at = time.monotonic()
                    if before != fingerprint(os.fstat(descriptor)):
                        raise OSError('Файл изменился во время чтения')
                    value = digest.hexdigest()
            # Identity verification on context exit must succeed before keeping the hash.
            if not entry.get('digest'):
                entry.update(digest=value, checked_at=now())
        except OSError as error:
            entry.update(error=str(error), digest=None)
        counters['checked_files'] += 1
        with self.storage.connect() as db:
            self._save_entry(db, job, side, entry['relative'], entry)
        self._update(job, **counters)

    def _hash_pairs(self, job, inventories, volumes):
        candidates = []
        for path, left in inventories['left'].items():
            right = inventories['right'].get(path)
            if right and left['kind'] == right['kind'] == 'file' and not left['error'] and not right['error'] and left.get('size') == right.get('size'):
                for side, entry in (('left', left), ('right', right)):
                    candidates.append((side, dict(entry, relative=path)))
        counters = {'hashed_bytes': 0, 'checked_files': 0}
        self._update(job, phase='hash', total_bytes=sum(e['size'] for _, e in candidates), total_files=len(candidates), **counters)
        for side, entry in candidates:
            self._check()
            self._update(job, current_path=entry['path'])
            self._hash(job, side, entry, volumes.get(side), counters)
            inventories[side][entry['relative']] = entry
        # A file changed while its partner was being checked must not receive "same".
        for side, entry in candidates:
            self._check()
            if not entry.get('digest'):
                continue
            try:
                if not volumes[side] or volumes[side]['availability'] != 'online':
                    raise OSError('Том отключён или недоступен')
                with open_readonly(volumes[side], entry['path']) as descriptor:
                    if any(entry.get(k) != v for k, v in fingerprint(os.fstat(descriptor)).items()):
                        raise OSError('Файл изменился до завершения сверки')
            except OSError as error:
                entry.update(error=str(error), digest=None)
                with self.storage.connect() as db:
                    self._save_entry(db, job, side, entry['relative'], entry)

    @staticmethod
    def _status(path, left, right, failures, files, method):
        if any(e and e.get('error') for e in (left, right)):
            return 'unverified'
        for side, entry in (('left', left), ('right', right)):
            if entry is None and any(not p or path.startswith(p + '/') for p in failures[side]):
                return 'unverified'
        if any(e and e['kind'] not in ('file', 'directory') for e in (left, right)):
            return 'skipped'
        if not right:
            return 'missing_copy'
        if not left:
            return 'extra_copy'
        if left['kind'] != right['kind']:
            return 'conflict'
        if left['kind'] == 'directory':
            return 'both'
        if not files:
            return 'unverified'
        if left.get('size') is None or right.get('size') is None:
            return 'unverified'
        if left.get('size') != right.get('size'):
            return 'size_different' if method == 'size' else 'different'
        if method == 'size':
            return 'same_size'
        if left.get('digest') and right.get('digest'):
            return 'same' if left['digest'] == right['digest'] else 'different'
        return 'unverified'

    def _classify(self, job, inventories, files, method):
        with self.storage.connect() as db:
            copy_id = db.execute('SELECT copy_id FROM paired_jobs WHERE id=?', (job,)).fetchone()[0]
        incomplete = self.transfers.incomplete(copy_id) if files and self.transfers else {}
        failures = {side: {p for p, e in entries.items() if e.get('error') and e['kind'] == 'directory'}
                    for side, entries in inventories.items()}
        rows, children = {}, {}
        for path in inventories['left'].keys() | inventories['right'].keys():
            if not path:
                continue
            left, right = inventories['left'].get(path), inventories['right'].get(path)
            directory = any(e and e['kind'] == 'directory' for e in (left, right))
            if not files and not directory:
                continue
            rows[path] = {'path': path, 'name': PurePosixPath(path).name, 'depth': len(PurePosixPath(path).parts) - 1,
                          'kind': 'directory' if directory else (left or right)['kind'], 'left': left, 'right': right,
                          'status': self._status(path, left, right, failures, files, method),
                          'attention_count': 0, 'file_attention_count': 0}
            if right and path in incomplete and right.get('inode') == incomplete[path]['inode']:
                rows[path]['status'] = 'copy_incomplete'
            parent = str(PurePosixPath(path).parent)
            children.setdefault('' if parent == '.' else parent, []).append(path)
        for row in rows.values():
            if row['status'] not in ('both', 'same', 'same_size', 'skipped'):
                parent = str(PurePosixPath(row['path']).parent)
                while parent != '.':
                    if parent in rows:
                        rows[parent]['attention_count'] += 1
                        if row['kind'] != 'directory':
                            rows[parent]['file_attention_count'] += 1
                    parent = str(PurePosixPath(parent).parent)
        ordered, pending = [], list(reversed(sorted(children.get('', []), key=lambda p: (rows[p]['kind'] != 'directory', rows[p]['name'].casefold(), p))))
        while pending:
            path = pending.pop()
            ordered.append(rows[path])
            pending.extend(reversed(sorted(children.get(path, []), key=lambda p: (rows[p]['kind'] != 'directory', rows[p]['name'].casefold(), p))))
        self._check()
        with self.storage.connect() as db:
            db.execute('DELETE FROM paired_rows WHERE job_id=?', (job,))
            db.executemany('INSERT INTO paired_rows VALUES (?,?,?,?,?,?)',
                           [(job, i, r['path'], r['kind'], r['status'], json.dumps(r, ensure_ascii=False)) for i, r in enumerate(ordered)])
            base = db.execute('SELECT base_job_id FROM paired_jobs WHERE id=?', (job,)).fetchone()[0]
            if base:
                db.execute('''INSERT OR IGNORE INTO paired_decisions
                    SELECT ?,d.path,d.action,d.updated_at FROM paired_decisions d JOIN paired_rows r
                    ON r.job_id=? AND r.path=d.path AND r.status='extra_copy' WHERE d.job_id=?''', (job, job, base))
        errors = sum(bool(e.get('error')) for entries in inventories.values() for e in entries.values())
        return errors

    def run(self, job):
        try:
            report = self.job(job)
            self._update(job, state='running', phase='index')
            current = {v['id']: v for v in self.storage.refresh(True)['volumes']}
            volumes = {side: current.get(scope['volume_id']) for side, scope in report['scopes'].items()}
            for side, scope in report['scopes'].items():
                if not report[side + '_complete']:
                    self._inventory(job, side, scope, volumes[side], report['mode'] == 'files')
            inventories = {side: self._entries(job, side) for side in ('left', 'right')}
            if report['mode'] == 'files' and report['method'] == 'sha256':
                self._hash_pairs(job, inventories, volumes)
            self._update(job, phase='align', current_path='')
            errors = self._classify(job, inventories, report['mode'] == 'files', report['method'])
            self._update(job, state='completed', phase='done', errors=errors,
                         message='Есть непрочитанные элементы' if errors else 'Сверка завершена')
        except Paused:
            self._update(job, state='paused', message='Остановлено. Можно продолжить.')
        except Exception as error:
            self._update(job, state='failed', message=str(error))

    def rows(self, job, offset=0, limit=1000, differences_only=False):
        report = self.job(job)
        predicate = " AND (r.status NOT IN ('both','same','same_size','skipped') OR (r.kind='directory' AND (instr(r.path,'/')=0 OR json_extract(r.data,'$.attention_count')>0)))" if differences_only else ''
        with self.storage.connect() as db:
            rows = []
            total = db.execute('SELECT COUNT(*) FROM paired_rows r WHERE r.job_id=?' + predicate, (job,)).fetchone()[0] if differences_only else report['row_count']
            decisions = {r['path']: (r['action'], r['kind']) for r in db.execute('''SELECT d.path,d.action,r.kind
                FROM paired_decisions d JOIN paired_rows r ON r.job_id=d.job_id AND r.path=d.path WHERE d.job_id=?''', (job,))}
            for row in db.execute('''SELECT r.data,d.action FROM paired_rows r LEFT JOIN paired_decisions d
                ON d.job_id=r.job_id AND d.path=r.path WHERE r.job_id=?''' + predicate + ' ORDER BY position LIMIT ? OFFSET ?', (job, limit, offset)):
                data = json.loads(row['data'])
                action, inherited = row['action'], None
                if action is None and data['status'] == 'extra_copy':
                    parent = str(PurePosixPath(data['path']).parent)
                    while parent != '.':
                        if parent in decisions and decisions[parent][1] == 'directory':
                            action, inherited = decisions[parent][0], parent
                            break
                        parent = str(PurePosixPath(parent).parent)
                rows.append(dict(data, decision=action, own_decision=row['action'], decision_from=inherited))
        return {'rows': rows, 'total': total, 'offset': offset}

    def decide(self, job, path, action):
        path = relative_path(path)
        if action not in DECISIONS and action is not None:
            raise ValueError('Неизвестное решение')
        with self.storage.connect() as db:
            row = db.execute('SELECT status FROM paired_rows WHERE job_id=? AND path=?', (job, path)).fetchone()
            if row is None or row['status'] != 'extra_copy':
                raise ValueError('Решение можно назначить элементу «Только в копии».')
            if action is None:
                db.execute('DELETE FROM paired_decisions WHERE job_id=? AND path=?', (job, path))
            else:
                db.execute('INSERT OR REPLACE INTO paired_decisions VALUES (?,?,?,?)', (job, path, action, now()))
        return {'path': path, 'action': action}
