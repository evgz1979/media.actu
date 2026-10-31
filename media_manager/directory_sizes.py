"""Background logical folder sizes, with persistent results for offline volumes."""
from __future__ import annotations

from collections import deque
import os
from pathlib import PurePosixPath
import stat
import threading

from .comparison import open_readonly
from .storage import now, relative_path
from .volume_identity import service_file


def within(path, root):
    return not root or path == root or path.startswith(root + '/')


class DirectorySizeService:
    def __init__(self, storage):
        self.storage = storage
        self._condition = threading.Condition(threading.RLock())
        self._queue = deque()
        self._jobs = {}
        self._failures = {}
        self._workers = []
        self._stop = threading.Event()
        with storage.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS directory_sizes (
                volume_id TEXT NOT NULL, path TEXT NOT NULL, bytes INTEGER,
                files INTEGER NOT NULL, calculated_at TEXT NOT NULL,
                complete INTEGER NOT NULL, error TEXT, stale INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(volume_id,path))''')
            if 'stale' not in {r['name'] for r in db.execute('PRAGMA table_info(directory_sizes)')}:
                db.execute('ALTER TABLE directory_sizes ADD COLUMN stale INTEGER NOT NULL DEFAULT 0')

    def close(self):
        self._stop.set()
        with self._condition:
            self._condition.notify_all()
        for worker in self._workers:
            worker.join(timeout=1)

    def request(self, volume_id, paths, *, start=True, refresh=False):
        paths = sorted({relative_path(path) for path in paths}, key=lambda p: (p.count('/'), len(p), p))
        # Polling cached sizes must not discover disks or wait for NAS metadata.
        if not self.storage._checked:
            self.storage.refresh()
        volume = self.storage.get_volume(volume_id)
        mounted = self.storage._mounted.get(volume_id)
        volume['availability'] = ('unknown' if self.storage._discovery_error or volume.get('identity_status') == 'unverified'
                                  else 'online' if mounted else 'offline')
        with self.storage.connect() as db:
            records = {r['path']: dict(r) for r in db.execute(
                'SELECT * FROM directory_sizes WHERE volume_id=? AND path IN (' + ','.join('?' for _ in paths) + ')',
                (volume_id, *paths))} if paths else {}
        with self._condition:
            if start and volume['availability'] == 'online' and volume.get('identity_status') not in ('unverified', 'legacy'):
                for path in paths:
                    record = records.get(path)
                    reusable = record and not record['stale']
                    covered = any(v == volume_id and within(path, root) for v, root in self._jobs)
                    if not covered and (refresh or not reusable):
                        key = volume_id, path
                        self._jobs[key] = {'state': 'queued', 'started_at': now()}
                        self._failures.pop(key, None)
                        self._queue.append(key)
                if self._queue and not self._workers:
                    self._workers = [threading.Thread(target=self._worker, daemon=True, name=f'folder-size-{i}') for i in range(2)]
                    for worker in self._workers:
                        worker.start()
                self._condition.notify_all()
            sizes = {}
            for path in paths:
                record = records.get(path)
                value = dict(record or dict(bytes=None, files=0, calculated_at=None, complete=False, error=None))
                job = next((job for (v, root), job in self._jobs.items() if v == volume_id and within(path, root)), None)
                failure = self._failures.get((volume_id, path))
                if volume['availability'] != 'online':
                    value.update(state='offline', error=volume.get('identity_error') or 'Том недоступен')
                elif job and (not record or record['calculated_at'] < job['started_at']):
                    value['state'] = job['state']
                elif failure:
                    value.update(state='error', error=failure)
                else:
                    value['state'] = ('stale' if record['stale'] else 'ready' if record['complete'] else 'partial') if record else 'unknown'
                value['complete'] = bool(value['complete'])
                sizes[path] = value
            return {'sizes': sizes}

    def _worker(self):
        while not self._stop.is_set():
            with self._condition:
                self._condition.wait_for(lambda: self._queue or self._stop.is_set())
                if self._stop.is_set():
                    return
                key = self._queue.popleft()
                self._jobs[key]['state'] = 'running'
            try:
                self.calculate(*key)
            except Exception as error:
                with self._condition:
                    self._failures[key] = str(error)
            finally:
                with self._condition:
                    self._jobs.pop(key, None)

    def calculate(self, volume_id, path):
        """One traversal supplies totals for every descendant; file contents stay closed."""
        path = relative_path(path)
        volume = next((v for v in self.storage.refresh(True)['volumes'] if v['id'] == volume_id), None)
        if not volume or volume['availability'] != 'online':
            raise OSError('Том отключён или недоступен')
        with open_readonly(volume, path, directory=True) as descriptor:
            info = os.fstat(descriptor)
            identity = info.st_dev, info.st_ino
        pending, totals = [(path, False)], {}
        while pending:
            if self._stop.is_set():
                return
            current, visited = pending.pop()
            if not visited:
                total = dict(bytes=0, files=0, complete=True, error=None, children=[])
                try:
                    with open_readonly(volume, current, directory=True) as descriptor:
                        device = os.fstat(descriptor).st_dev
                        with os.scandir(descriptor) as entries:
                            for entry in entries:
                                if self._stop.is_set():
                                    return
                                if service_file(entry.name,volume_root=not current):
                                    continue
                                try:
                                    info = entry.stat(follow_symlinks=False)
                                    if info.st_dev != device:
                                        continue
                                    if stat.S_ISDIR(info.st_mode):
                                        total['children'].append('/'.join(filter(None, (current, entry.name))))
                                    elif stat.S_ISREG(info.st_mode):
                                        total['bytes'] += info.st_size
                                        total['files'] += 1
                                except OSError as error:
                                    total.update(complete=False, error=str(error))
                except OSError as error:
                    total.update(bytes=None, complete=False, error=str(error))
                totals[current] = total
                pending.append((current, True))
                pending.extend((child, False) for child in reversed(total['children']))
            else:
                total = totals[current]
                for child in total.pop('children'):
                    result = totals.pop(child)
                    if result['bytes'] is not None:
                        total['bytes'] = (total['bytes'] or 0) + result['bytes']
                        total['files'] += result['files']
                    if not result['complete']:
                        total.update(complete=False, error=result['error'])
                if current == path:
                    # Do not publish a completed total if this scope or disk was replaced.
                    with open_readonly(volume, path, directory=True) as descriptor:
                        info = os.fstat(descriptor)
                        if (info.st_dev, info.st_ino) != identity:
                            raise OSError('Папка была заменена во время подсчёта')
                    latest = next((v for v in self.storage.refresh(True)['volumes'] if v['id'] == volume_id), None)
                    if not latest or latest['availability'] != 'online':
                        raise OSError('Том был отключён или заменён во время подсчёта')
                if total['bytes'] is None:
                    with self._condition:
                        self._failures[volume_id, current] = total['error']
                    continue
                with self.storage.connect() as db:
                    previous = db.execute('SELECT bytes,files,complete FROM directory_sizes WHERE volume_id=? AND path=?',
                                          (volume_id, current)).fetchone()
                    if previous is None or tuple(previous) != (total['bytes'], total['files'], total['complete']):
                        # A refreshed child can make a previously measured ancestor obsolete.
                        for parent in PurePosixPath(current).parents:
                            parent = '' if str(parent) == '.' else str(parent)
                            db.execute('UPDATE directory_sizes SET stale=1 WHERE volume_id=? AND path=?', (volume_id, parent))
                    db.execute('INSERT OR REPLACE INTO directory_sizes VALUES (?,?,?,?,?,?,?,0)',
                               (volume_id, current, total['bytes'], total['files'], now(), total['complete'], total['error']))
                with self._condition:
                    self._failures.pop((volume_id, current), None)
