"""Portable folder descriptions, with durable retries and bounded metadata-only writes."""
from __future__ import annotations

import errno
import json
import logging
import os
import stat
import threading
import time
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .volume_identity import FOLDER_MARKER_NAME


FOLDER_MARKER_LIMIT = 16384
FOLDER_MARKER_SCHEMA = '''
CREATE TABLE IF NOT EXISTS folder_marker_jobs (
    location_id TEXT PRIMARY KEY, group_id TEXT NOT NULL, volume_id TEXT NOT NULL,
    path TEXT NOT NULL, payload TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
    state TEXT NOT NULL DEFAULT 'pending', error TEXT, synced_at TEXT,
    next_check REAL NOT NULL DEFAULT 0
);
'''


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def queue_marker(db, payload):
    """Call in the catalog's transaction so a changed role cannot lose its update."""
    previous = db.execute('SELECT payload FROM folder_marker_jobs WHERE location_id=?', (payload['folder_id'],)).fetchone()
    if previous:
        saved = json.loads(previous['payload'])
        saved.pop('updated_at', None)
        if saved == payload:
            return
    document = {**payload, 'updated_at': timestamp()}
    db.execute('''INSERT INTO folder_marker_jobs(location_id,group_id,volume_id,path,payload)
                  VALUES (?,?,?,?,?) ON CONFLICT(location_id) DO UPDATE SET
                  group_id=excluded.group_id,volume_id=excluded.volume_id,path=excluded.path,payload=excluded.payload,
                  revision=folder_marker_jobs.revision+1,state='pending',error=NULL,next_check=0''',
               (payload['folder_id'],payload['group_id'],payload['volume_id'],payload['path'],json.dumps(document,ensure_ascii=False,sort_keys=True)))


def read_folder_marker(root):
    try:
        descriptor = os.open(FOLDER_MARKER_NAME, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_dev != os.fstat(root).st_dev or info.st_size > FOLDER_MARKER_LIMIT:
            raise OSError('Некорректный служебный файл папки')
        with os.fdopen(descriptor,'rb',closefd=False) as stream:
            raw = stream.read(FOLDER_MARKER_LIMIT + 1)
        if len(raw) > FOLDER_MARKER_LIMIT:
            raise OSError('Служебный файл папки слишком большой')
        try:
            document = json.loads(raw)
            if not isinstance(document,dict) or type(document.get('version')) is not int or document['version'] != 1:
                raise ValueError('version')
            for key in ('group_id','folder_id'):
                identifier = UUID(document[key])
                if not identifier.int:
                    raise ValueError(key)
            if document['status'] not in {'active','disconnected','released','removed'}:
                raise ValueError('status')
            number, kind = document['number'], document['type']
            if type(number) is not int or not ((number == 0 and kind == 'main') or (number > 0 and kind in {'copy','cold','cloud'})):
                raise ValueError('number')
            if document['role'] != ('main' if number == 0 else 'copy'):
                raise ValueError('role')
            for key in ('label','name','volume_id','created_at','updated_at','path'):
                value = document[key]
                if not isinstance(value,str) or not value or any(ord(char) < 32 for char in value):
                    raise ValueError(key)
        except (ValueError,TypeError,KeyError,AttributeError) as error:
            raise OSError('Не удалось подтвердить служебный файл папки') from error
        return document
    finally:
        os.close(descriptor)


def write_folder_marker(root, payload, *, may_replace=lambda previous: False, before_publish=lambda: None):
    # Import at use time: copy catalogs enqueue descriptions before file services
    # are constructed, and must not acquire filesystem dependencies on import.
    from .copy_files import publish_exclusive

    previous = read_folder_marker(root)
    if previous and previous['folder_id'] != payload['folder_id']:
        if not may_replace(previous):
            raise OSError('В папке уже есть служебный файл другой привязки. Он сохранён.')
        document = payload
    else:
        if previous and (previous['group_id'],previous['volume_id']) != (payload['group_id'],payload['volume_id']):
            raise OSError('Служебный файл папки относится к другому набору или тому')
        document = {**(previous or {}), **payload}
    if document == previous:
        return False
    content = (json.dumps(document,ensure_ascii=False,indent=2) + '\n').encode()
    if len(content) > FOLDER_MARKER_LIMIT:
        raise ValueError('Описание папки не помещается в служебный файл')
    temporary = f'.media-actu-copy-{uuid4().hex}-{uuid4().hex}.part'
    descriptor = os.open(temporary,os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,0o644,dir_fd=root)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        before_publish()
        if read_folder_marker(root) != previous:
            raise OSError('Служебный файл папки изменился во время записи')
        if previous:
            os.replace(temporary,FOLDER_MARKER_NAME,src_dir_fd=root,dst_dir_fd=root)
        else:
            try:
                publish_exclusive(root,temporary,FOLDER_MARKER_NAME)
            except OSError as error:
                if error.errno not in (errno.ENOTSUP,errno.EOPNOTSUPP,errno.ENOSYS,errno.EINVAL):
                    raise
                # Some SMB servers lack exclusive rename. Exclusive creation
                # still protects a marker another client created in the meantime.
                final = os.open(FOLDER_MARKER_NAME,os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,0o644,dir_fd=root)
                identity = os.fstat(final)
                try:
                    with os.fdopen(final,'wb') as stream:
                        stream.write(content)
                        stream.flush()
                        os.fsync(stream.fileno())
                except BaseException:
                    current = os.stat(FOLDER_MARKER_NAME,dir_fd=root,follow_symlinks=False)
                    if (current.st_dev,current.st_ino) == (identity.st_dev,identity.st_ino):
                        os.unlink(FOLDER_MARKER_NAME,dir_fd=root)
                    raise
        if read_folder_marker(root) != document:
            raise OSError('Не удалось подтвердить запись служебного файла папки')
        return True
    finally:
        try:
            os.unlink(temporary,dir_fd=root)
        except FileNotFoundError:
            pass


class FolderMarkerService:
    def __init__(self,copies):
        self.copies, self.storage = copies, copies.storage
        self._stop, self._wake = threading.Event(), threading.Event()
        self._thread = None
        self._sync_lock = threading.Lock()

    def start(self):
        self.copies.queue_folder_markers()
        self._thread = threading.Thread(target=self._run,daemon=True,name='folder-markers')
        self._thread.start()

    def wake(self):
        self._wake.set()

    def close(self):
        self._stop.set()
        self._wake.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self):
        while not self._stop.is_set():
            self._wake.clear()
            try:
                self.reconcile()
            except Exception:
                logging.exception('Unable to synchronize folder descriptions')
            self._wake.wait(30)

    def _current(self,job):
        with self.storage.connect() as db:
            row = db.execute('SELECT revision FROM folder_marker_jobs WHERE location_id=?',(job['location_id'],)).fetchone()
            return bool(row and row['revision'] == job['revision'])

    def _may_replace(self,previous,payload):
        if previous['volume_id'] != payload['volume_id']:
            return False
        with self.storage.connect() as db:
            row = db.execute('SELECT payload FROM folder_marker_jobs WHERE location_id=?',(previous['folder_id'],)).fetchone()
        known = json.loads(row['payload']) if row else None
        return bool(known and known['status'] in {'released','removed'}
                    and (known['group_id'],known['volume_id']) == (previous['group_id'],previous['volume_id']))

    def _owns_path(self,job):
        with self.storage.connect() as db:
            owner = db.execute('SELECT id FROM copy_locations WHERE volume_id=? AND path=?',
                               (job['volume_id'],job['path'])).fetchone()
            if owner:
                return owner['id'] == job['location_id']
            owner = db.execute('''SELECT id FROM released_copy_locations WHERE volume_id=? AND path=?
                                  ORDER BY released_at DESC,id DESC LIMIT 1''',(job['volume_id'],job['path'])).fetchone()
            if owner:
                return owner['id'] == job['location_id']
            owner = db.execute('''SELECT location_id FROM folder_marker_jobs WHERE volume_id=? AND path=?
                                  ORDER BY json_extract(payload,'$.created_at') DESC,location_id DESC LIMIT 1''',
                               (job['volume_id'],job['path'])).fetchone()
            return bool(owner and owner['location_id'] == job['location_id'])

    def reconcile(self):
        from .comparison import open_readonly

        if not self._sync_lock.acquire(blocking=False):
            return
        try:
            with self.storage.connect() as db:
                jobs = [dict(row) for row in db.execute('''SELECT * FROM folder_marker_jobs WHERE next_check<=?
                    AND state!='superseded' ORDER BY CASE WHEN json_extract(payload,'$.status')='active' THEN 0 ELSE 1 END,location_id''',(time.time(),))]
            if not jobs:
                return
            if not self.storage._checked:
                self.storage.refresh()
            volumes = {v['id']:v for v in self.storage.refresh(cached_only=True)['volumes']}
            for job in jobs:
                if self._stop.is_set():
                    return
                payload = json.loads(job['payload'])
                state, error = 'pending', None
                volume = volumes.get(job['volume_id'])
                try:
                    if not self._owns_path(job):
                        state = 'superseded'
                    elif volume and volume.get('identity_status') in {'unverified','legacy'}:
                        error = 'Ожидает подтверждения носителя'
                    elif not volume or not volume.get('mounted') or volume['availability'] != 'online':
                        error = 'Ожидает подключения тома'
                    elif self._current(job):
                        with open_readonly(volume,job['path'],directory=True) as root:
                            identity = os.fstat(root)
                            def before_publish():
                                if self._stop.is_set() or not self._current(job) or not self._owns_path(job):
                                    raise OSError('Описание папки изменилось. Запись будет повторена.')
                                with open_readonly(volume,job['path'],directory=True) as current:
                                    info = os.fstat(current)
                                    if (info.st_dev,info.st_ino) != (identity.st_dev,identity.st_ino):
                                        raise OSError('Папка заменена во время записи')
                            write_folder_marker(root,payload,may_replace=lambda old:self._may_replace(old,payload),
                                                before_publish=before_publish)
                            state = 'ready'
                except (OSError,ValueError) as problem:
                    if isinstance(problem,OSError) and problem.errno in (errno.ENOENT,errno.ENOTDIR):
                        state, error = 'pending', 'Папка по прежнему пути недоступна. Ожидает подключения или обновления привязки.'
                    else:
                        state, error = 'error', str(problem)
                with self.storage.connect() as db:
                    db.execute('''UPDATE folder_marker_jobs SET state=?,error=?,synced_at=CASE WHEN ?='ready' THEN ? ELSE synced_at END,
                                  next_check=? WHERE location_id=? AND revision=?''',
                               (state,error,state,timestamp(),time.time()+(60 if state=='ready' else 30),job['location_id'],job['revision']))
        finally:
            self._sync_lock.release()

    def status(self):
        with self.storage.connect() as db:
            rows = [dict(row) for row in db.execute('SELECT location_id,group_id,volume_id,path,state,error,synced_at FROM folder_marker_jobs ORDER BY group_id,location_id')]
        return {'folders':rows,'counts':{state:sum(row['state']==state for row in rows)
                                       for state in ('ready','pending','error','superseded')}}
