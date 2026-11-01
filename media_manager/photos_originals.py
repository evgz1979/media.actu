"""Verified PhotoKit streams written exclusively into a bound copy.

SQLite contains manifests, hashes and receipts, never original media bytes.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import errno
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import stat
import threading
import time
from uuid import uuid4

from .comparison import fingerprint, open_readonly
from .copy_files import destination_directory, object_id, publish_exclusive
from .photo_libraries import now
from .photos_adapter import PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable, PhotosTransferStopped


ACTIVE = {'manifest', 'inventory', 'saving', 'pausing'}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def safe_name(value):
    value = re.sub(r'[\x00-\x1f/\\:]', '_', str(value)).strip(' .')
    # Leave room for a deterministic collision suffix on common filesystems.
    stem, ext = os.path.splitext(value)
    while len((stem + ext).encode()) > 190:
        stem = stem[:-1]
        if not stem:
            ext = ext[:30]
    return (stem + ext) or 'original'


class PhotosOriginals:
    def __init__(self, libraries, adapter):
        self.libraries, self.catalog, self.storage = libraries, libraries.catalog, libraries.storage
        self.adapter = adapter
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self._progress_at = self._validate_at = 0
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
                CREATE INDEX IF NOT EXISTS photos_original_inventory_hash ON photos_original_inventory(link_id,sha256,size);
                CREATE TABLE IF NOT EXISTS photos_original_staging (
                    job_id TEXT NOT NULL, path TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(job_id,path));
                CREATE TABLE IF NOT EXISTS photos_original_log (
                    id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    level TEXT NOT NULL, path TEXT NOT NULL, message TEXT NOT NULL);
            ''')
            rows = list(db.execute('SELECT id,data FROM photos_original_jobs WHERE state IN (\'manifest\',\'inventory\',\'saving\',\'pausing\')'))
            for row in rows:
                data = json.loads(row['data'])
                data['message'] = 'Сохранение прервано перезапуском. Можно продолжить.'
                db.execute("UPDATE photos_original_jobs SET state='paused',data=?,updated_at=? WHERE id=?", (encoded(data), now(), row['id']))

    @contextmanager
    def _db(self):
        connection = self.catalog.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _link(self, link_id, source_id=None):
        with self._db() as db:
            row = db.execute('SELECT * FROM photos_copy_links WHERE id=?', (link_id,)).fetchone()
        if not row or (source_id is not None and row['source_id'] != source_id):
            raise KeyError('Копия медиатеки не найдена')
        if not row['connected']:
            raise PhotosLibraryUnavailable('Папка копии отвязана')
        return dict(row)

    def summary(self, link_id):
        with self._db() as db:
            row = db.execute('SELECT * FROM photos_original_jobs WHERE link_id=? ORDER BY updated_at DESC LIMIT 1', (link_id,)).fetchone()
        if not row:
            return dict(state='idle', done_assets=0, total_assets=0, message='Сохранение ещё не запускалось')
        with self._db() as db:
            incomplete = db.execute("SELECT COUNT(*) FROM photos_original_staging s JOIN photos_original_jobs j ON j.id=s.job_id WHERE j.link_id=? AND json_extract(s.data,'$.final')=1", (link_id,)).fetchone()[0]
        return dict(json.loads(row['data']), id=row['id'], state=row['state'], updated_at=row['updated_at'], incomplete_files=incomplete)

    def journal(self, link_id, source_id=None):
        self._link(link_id, source_id)
        job = self.summary(link_id)
        with self._db() as db:
            rows = [dict(r) for r in db.execute('SELECT created_at,level,path,message FROM photos_original_log WHERE job_id=? ORDER BY id DESC LIMIT 200', (job.get('id', ''),))]
            incomplete = [r[0] for r in db.execute("SELECT s.path FROM photos_original_staging s JOIN photos_original_jobs j ON j.id=s.job_id WHERE j.link_id=? AND json_extract(s.data,'$.final')=1 ORDER BY s.path", (link_id,))]
        return dict(job=job, items=rows, incomplete_paths=incomplete)

    def _update(self, job, state=None, **values):
        with self.catalog._write_lock, self._db() as db:
            row = db.execute('SELECT state,data FROM photos_original_jobs WHERE id=?', (job,)).fetchone()
            data = dict(json.loads(row['data']), **values)
            db.execute('UPDATE photos_original_jobs SET state=?,data=?,updated_at=? WHERE id=?', (state or row['state'], encoded(data), now(), job))

    def _log(self, job, level, path, message):
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT INTO photos_original_log(job_id,created_at,level,path,message) VALUES (?,?,?,?,?)', (job, now(), level, path, message))

    def _volume(self, link):
        volume = next((v for v in self.storage.refresh(cached_only=True)['volumes'] if v['id'] == link['volume_id']), None)
        if not volume or volume['availability'] != 'online':
            raise PhotosLibraryUnavailable('Том копии отключён. Подключи его и продолжи сохранение.')
        return volume

    def start(self, link_id, source_id=None, *, background=True):
        with self._lock:
            if self._thread and self._thread.is_alive():
                raise ValueError('Сначала приостанови текущее сохранение оригиналов')
            link = self._link(link_id, source_id)
            self.libraries._require_active(link['source_id'])
            volume = self._volume(link)
            with open_readonly(volume, link['path'], directory=True) as fd:
                root = object_id(os.fstat(fd))
            previous = self.summary(link_id)
            if previous['state'] in {'paused', 'waiting', 'failed', 'completed_with_errors'}:
                job = previous['id']
                if previous['root'] != root:
                    raise ValueError('Привязанная папка была заменена. Проверь привязку перед сохранением.')
                self._update(job, state='manifest', message='Читаю список оригиналов Photos', current_path='', current_bytes=0, fraction=0, errors=0)
            else:
                job = uuid4().hex
                data = dict(root=root, done_assets=0, total_assets=0, done_resources=0, total_resources=0,
                            saved=0, reused=0, errors=0, checked_files=0, checked_bytes=0,
                            current_path='', current_bytes=0, fraction=0, message='Читаю список оригиналов Photos')
                with self.catalog._write_lock, self._db() as db:
                    db.execute('INSERT INTO photos_original_jobs VALUES (?,?,?,?,?)', (job, link_id, 'manifest', now(), encoded(data)))
            self._stop.clear()
            self._validate_at = 0
            self._log(job, 'info', '', 'Начато сохранение оригиналов в привязанную копию')
            if background:
                self._thread = threading.Thread(target=self.run, args=(job, link), name='photos-originals', daemon=True)
                self._thread.start()
        if not background:
            self.run(job, link)
        return self.summary(link_id)

    def pause(self, link_id, source_id=None):
        with self._lock:
            self._link(link_id, source_id)
            job = self.summary(link_id)
            if job['state'] in ACTIVE:
                self._stop.set()
                self._update(job['id'], state='pausing', message='Приостанавливаю сохранение…')
        return self.summary(link_id)

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)
        # The worker closes its own channel after cancellation. Never block on
        # its operation lock while an unavailable network disk is unwinding.

    def _check(self):
        if self._stop.is_set():
            raise PhotosTransferStopped('Сохранение приостановлено')

    def _validate(self, job, link, volume, *, force=False):
        self._check()
        if not force and time.monotonic() - self._validate_at < .5:
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

    def _progress(self, job, **values):
        if time.monotonic() - self._progress_at > .5:
            self._update(job, **values)
            self._progress_at = time.monotonic()

    @contextmanager
    def _file(self, volume, link, path):
        with open_readonly(volume, str(PurePosixPath(link['path']) / path)) as fd:
            yield fd

    def _hash(self, fd, check=lambda: None):
        before = fingerprint(os.fstat(fd))
        digest = hashlib.sha256()
        os.lseek(fd, 0, os.SEEK_SET)
        while chunk := os.read(fd, 1024 * 1024):
            check()
            digest.update(chunk)
        if fingerprint(os.fstat(fd)) != before:
            raise OSError('Файл изменился во время проверки')
        return digest.hexdigest(), before

    def _inventory_record(self, link, path, fp, sha, seen):
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_original_inventory VALUES (?,?,?,?,?,?)',
                       (link['id'], path, encoded(fp), fp['size'], sha, seen))

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

    def _inventory(self, job, link, volume):
        self._update(job, state='inventory', message='Проверяю уже сохранённые файлы', checked_files=0, checked_bytes=0)
        with self._db() as db:
            incomplete = {r['path'] for r in db.execute('SELECT path FROM photos_original_staging WHERE job_id IN (SELECT id FROM photos_original_jobs WHERE link_id=?)', (link['id'],))}
        count = size = 0
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
                        with self._file(volume, link, path) as original:
                            fp = fingerprint(os.fstat(original))
                            with self._db() as db:
                                cached = db.execute('SELECT * FROM photos_original_inventory WHERE link_id=? AND path=?', (link['id'], path)).fetchone()
                            if cached and cached['fingerprint'] == encoded(fp):
                                sha = cached['sha256']
                            else:
                                sha, fp = self._hash(original, lambda: self._validate(job, link, volume))
                        self._inventory_record(link, path, fp, sha, job)
                        count += 1; size += fp['size']
                        self._progress(job, checked_files=count, checked_bytes=size, current_path=path)
        with open_readonly(volume, link['path'], directory=True) as fd:
            walk(fd)
        with self.catalog._write_lock, self._db() as db:
            db.execute('DELETE FROM photos_original_inventory WHERE link_id=? AND seen<>?', (link['id'], job))
        self._update(job, checked_files=count, checked_bytes=size)

    def _receipt(self, job, link, asset, resource, version, path, fp, sha, reused):
        self._validate(job, link, self._volume(link), force=True)
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_copy_files VALUES (?,?,?,?,?,?,?)', (link['id'], asset, resource, path, fp['size'], sha, now()))
            db.execute('INSERT OR REPLACE INTO photos_original_versions VALUES (?,?,?,?,?)', (link['id'], asset, resource, version, encoded(fp)))
            db.execute("UPDATE photos_original_resources SET state=? WHERE job_id=? AND asset=? AND resource=?", ('reused' if reused else 'saved', job, asset, resource))
        self._inventory_record(link, path, fp, sha, job)

    def _reuse_receipt(self, job, link, volume, asset, resource, version):
        with self._db() as db:
            row = db.execute('''SELECT f.*,v.version FROM photos_copy_files f JOIN photos_original_versions v
                ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id
                JOIN photos_original_inventory i ON i.link_id=f.link_id AND i.path=f.path
                WHERE f.link_id=? AND f.asset_identifier=? AND f.resource_id=? AND i.sha256=f.sha256 AND i.size=f.size''', (link['id'], asset, resource)).fetchone()
        if not row or row['version'] != version:
            return False
        with self._file(volume, link, row['path']) as fd:
            sha, fp = self._hash(fd, lambda: self._validate(job, link, volume))
        if sha != row['sha256'] or fp['size'] != row['size']:
            return False
        self._receipt(job, link, asset, resource, version, row['path'], fp, sha, True)
        return True

    def _stage(self, job, path, identity, final=False):
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_original_staging VALUES (?,?,?)', (job, path, encoded(dict(identity=identity, final=final))))

    def _unstage(self, job, path):
        with self.catalog._write_lock, self._db() as db:
            db.execute('DELETE FROM photos_original_staging WHERE job_id=? AND path=?', (job, path))

    def _publish(self, job, link, volume, parent, parent_path, temporary, name, sha, size):
        # Collision names do not depend on a file's position in an enumeration.
        for index in range(10000):
            candidate = name if index == 0 else f'{os.path.splitext(name)[0]}-{index}{os.path.splitext(name)[1]}'
            path = str(PurePosixPath(parent_path) / candidate)
            self._validate(job, link, volume, force=True)
            with destination_directory(volume, link, parent_path) as current:
                if object_id(os.fstat(current)) != object_id(os.fstat(parent)):
                    raise OSError('Целевая папка заменена')
            try:
                publish_exclusive(parent, temporary, candidate)
            except FileExistsError:
                continue
            except OSError as error:
                if error.errno not in (errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS, errno.EINVAL):
                    raise
                # SMB may lack exclusive rename. Create a new final path only;
                # interrupted final files are journalled and never overwritten.
                try:
                    target = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=parent)
                except FileExistsError:
                    continue
                self._stage(job, path, object_id(os.fstat(target)), final=True)
                try:
                    source = os.open(temporary, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
                    try:
                        while chunk := os.read(source, 1024 * 1024):
                            self._write(target, chunk)
                        os.fsync(target)
                    finally:
                        os.close(source)
                finally:
                    os.close(target)
            with self._file(volume, link, path) as fd:
                verified, fp = self._hash(fd)
            if verified != sha or fp['size'] != size:
                raise OSError('Проверка опубликованного оригинала не совпала')
            return path, fp
        raise OSError('Не удалось выбрать свободное имя оригинала')

    @staticmethod
    def _write(fd, chunk):
        view = memoryview(chunk)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError('Не удалось записать оригинал')
            view = view[written:]

    def _save(self, job, link, volume, profile, item):
        asset, resource, version = item['asset'], item['resource'], item['version']
        if self._reuse_receipt(job, link, volume, asset, resource, version):
            return 'reused'
        created = item.get('created_at', '')
        try:
            date = datetime.fromisoformat(created.replace('Z', '+00:00'))
            parent_path = f'{date.year:04d}/{date.year:04d}-{date.month:02d}'
        except ValueError:
            parent_path = 'Без даты'
        name = safe_name(item['name'])
        temporary = '.media-actu-copy-' + job + '-' + uuid4().hex + '.part'
        stage_path = str(PurePosixPath(parent_path) / temporary)
        with destination_directory(volume, link, parent_path, create=True) as parent:
            fd = os.open(temporary, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
            identity = object_id(os.fstat(fd))
            self._stage(job, stage_path, identity)
            count = 0
            digest = hashlib.sha256()
            def write(chunk):
                nonlocal count
                self._validate(job, link, volume)
                capacity = os.fstatvfs(parent)
                if capacity.f_bavail * (capacity.f_frsize or capacity.f_bsize) < len(chunk) + 64 * 1024 * 1024:
                    raise PhotosLibraryUnavailable('Недостаточно свободного места в папке копии. Освободи место и продолжи.')
                self._write(fd, chunk)
                digest.update(chunk); count += len(chunk)
                self._progress(job, current_bytes=count)
            try:
                trailer = self.adapter.stream_original(asset, resource, version, profile['anchors'], write,
                    lambda fraction: self._progress(job, fraction=fraction, current_bytes=count), self._stop.is_set)
                if trailer.get('size') != count or trailer.get('sha256') != digest.hexdigest() or count == 0:
                    raise PhotosAdapterError('Размер или SHA-256 переданного оригинала не совпал')
                os.fsync(fd)
                sha, fp = self._hash(fd, lambda: self._validate(job, link, volume))
                if sha != digest.hexdigest() or fp['size'] != count:
                    raise OSError('Проверка записанного оригинала не совпала')
                self._validate(job, link, volume, force=True)
                if object_id(os.stat(temporary, dir_fd=parent, follow_symlinks=False)) != identity:
                    raise OSError('Промежуточный файл заменён')
                with self._db() as db:
                    candidates = list(db.execute('SELECT * FROM photos_original_inventory WHERE link_id=? AND sha256=? AND size=?', (link['id'], sha, count)))
                for candidate in candidates:
                    try:
                        with self._file(volume, link, candidate['path']) as existing:
                            existing_sha, existing_fp = self._hash(existing, lambda: self._validate(job, link, volume))
                        if existing_sha == sha and existing_fp['size'] == count:
                            self._receipt(job, link, asset, resource, version, candidate['path'], existing_fp, sha, True)
                            return 'reused'
                    except FileNotFoundError:
                        continue
                os.fchmod(fd, 0o644)
                path, final_fp = self._publish(job, link, volume, parent, parent_path, temporary, name, sha, count)
                self._receipt(job, link, asset, resource, version, path, final_fp, sha, False)
                self._unstage(job, path)
                return 'saved'
            finally:
                os.close(fd)
                try:
                    if object_id(os.stat(temporary, dir_fd=parent, follow_symlinks=False)) == identity:
                        os.unlink(temporary, dir_fd=parent)
                    else:
                        raise OSError('Промежуточный файл заменён; он оставлен на диске')
                except FileNotFoundError:
                    pass
                self._unstage(job, stage_path)

    def _counts(self, job):
        with self._db() as db:
            row = db.execute('''SELECT COUNT(*) total_resources,
                COALESCE(SUM(state IN ('saved','reused')),0) done_resources,
                COALESCE(SUM(state='saved'),0) saved,COALESCE(SUM(state='reused'),0) reused,
                COALESCE(SUM(state='error'),0) errors FROM photos_original_resources WHERE job_id=?''', (job,)).fetchone()
            assets = db.execute('''SELECT COUNT(*) total_assets,COALESCE(SUM(ready),0) done_assets FROM
                (SELECT asset,MIN(state IN ('saved','reused')) ready FROM photos_original_resources WHERE job_id=? GROUP BY asset)''', (job,)).fetchone()
        return dict(row) | dict(assets)

    def run(self, job, link):
        state, message = 'completed', 'Оригиналы сохранены и проверены'
        try:
            volume = self._volume(link)
            self._validate(job, link, volume, force=True)
            profile = self.libraries._require_active(link['source_id'])
            self._cleanup(job, link, volume)
            # Replace only the working manifest; verified receipts are permanent.
            with self.catalog._write_lock, self._db() as db:
                db.execute('DELETE FROM photos_original_resources WHERE job_id=?', (job,))
            received = 0
            def asset_received(asset):
                nonlocal received
                self._validate(job, link, volume)
                resources = asset.get('resources') or [dict(id='missing', name=asset.get('name', 'original'), error='Photos не вернула оригинальные ресурсы')]
                with self.catalog._write_lock, self._db() as db:
                    for resource in resources:
                        item = dict(resource, asset=asset['id'], resource=resource['id'], version=asset['version'], created_at=asset.get('created_at', ''))
                        db.execute('INSERT INTO photos_original_resources(job_id,asset,resource,data) VALUES (?,?,?,?)', (job, asset['id'], resource['id'], encoded(item)))
                received += 1
                self._progress(job, total_assets=received)
            self.adapter.original_manifest(profile['anchors'], asset_received, self._stop.is_set)
            counters = self._counts(job)
            self._update(job, **counters)
            self._inventory(job, link, volume)
            self._update(job, state='saving', message='Сохраняю и проверяю оригиналы', current_path='')
            # Iterate IDs with a short-lived connection; never keep a write/read
            # transaction open while waiting for iCloud or the destination.
            position = ('', '')
            while True:
                self._validate(job, link, volume)
                with self._db() as db:
                    row = db.execute('SELECT asset,resource,data FROM photos_original_resources WHERE job_id=? AND (asset,resource)>(?,?) ORDER BY asset,resource LIMIT 1', (job, *position)).fetchone()
                if not row:
                    break
                position = (row['asset'], row['resource'])
                item = json.loads(row['data'])
                self._update(job, current_path=item['name'], current_bytes=0, fraction=0)
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
                        db.execute("UPDATE photos_original_resources SET state='error' WHERE job_id=? AND asset=? AND resource=?", (job, *position))
                    self._log(job, 'error', item['name'], str(error))
                    counters['errors'] += 1
                self._update(job, **counters)
            if self._counts(job)['errors']:
                state, message = 'completed_with_errors', 'Часть оригиналов не сохранена. Ошибки — в журнале; можно повторить.'
        except PhotosTransferStopped:
            state, message = 'paused', 'Сохранение приостановлено. Проверенные оригиналы сохранены.'
        except (PhotosLibraryUnavailable, PhotosAccessDenied) as error:
            state, message = 'waiting', str(error)
        except Exception as error:
            state, message = 'failed', str(error)
        finally:
            self.adapter.close()
            incomplete = self.summary(link['id']).get('incomplete_files', 0)
            if incomplete:
                message += f' · Незавершённых файлов в копии: {incomplete}; пути — в журнале.'
            self._update(job, state=state, message=message, current_path='', current_bytes=0, fraction=0, **self._counts(job))
            self._log(job, 'error' if state in ('failed', 'waiting', 'completed_with_errors') else 'info', '', message)
