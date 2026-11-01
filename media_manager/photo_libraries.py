"""Separate Photos catalogues and copy destinations; never store originals here."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import PurePosixPath
import threading
import uuid

from .comparison import open_readonly
from .photos_adapter import PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable
from .storage import relative_path


def now():
    return datetime.now(timezone.utc).isoformat()


def matches(anchors, found):
    return bool(anchors) and len(set(anchors).intersection(found)) >= min(3, len(anchors))


class PhotoLibraries:
    def __init__(self, catalog, storage, adapter):
        self.catalog, self.storage, self.adapter = catalog, storage, adapter
        self._lock = threading.RLock()
        self.connection = dict(state='unknown')
        self.polling = False
        self.originals = None
        self._migrate()

    def _migrate(self):
        # Preserve legacy media IDs: their 3,410 cached previews remain valid.
        if getattr(self.adapter, 'supported', True) and not any(s['kind'] == 'photos' for s in self.catalog.list_sources()):
            self.catalog.add_system_photos_source()
        with self.catalog._write_lock, self.catalog.connect() as db:
            for source in db.execute("SELECT id FROM sources WHERE kind='photos'").fetchall():
                anchors = [r[0] for r in db.execute('SELECT relative_path FROM media_files WHERE source_id=? ORDER BY id LIMIT 12', (source['id'],))]
                db.execute('INSERT OR IGNORE INTO photos_libraries(source_id,library_id,anchors) VALUES (?,?,?)',
                           (source['id'], uuid.uuid4().hex, json.dumps(anchors)))
            db.execute("UPDATE photos_libraries SET active=0,state='unknown'")

    def _profiles(self):
        with self.catalog.connect() as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM photos_libraries ORDER BY source_id')]
        for row in rows:
            row['anchors'] = json.loads(row['anchors'])
        return rows

    def profile(self, source_id):
        profile = next((p for p in self._profiles() if p['source_id'] == source_id), None)
        if not profile:
            raise KeyError('Медиатека не найдена')
        return profile

    def _unavailable(self, state, error):
        with self.catalog._write_lock, self.catalog.connect() as db:
            db.execute('UPDATE photos_libraries SET active=0,state=?,error=?,checked_at=?', (state, str(error), now()))
            db.execute("UPDATE sources SET status=?,error=? WHERE kind='photos'", ('no_access' if state == 'no_access' else 'offline', str(error)))
        self.connection = dict(state=state, error=str(error))

    def refresh_connection(self, *, restart=True):
        with self._lock:
            profiles = self._profiles()
            identifiers = [a for p in profiles for a in p['anchors']]
            try:
                probe = self.adapter.probe(identifiers, restart=restart)
            except PhotosAccessDenied as error:
                self._unavailable('no_access', error)
                return self.connection
            except PhotosAdapterError as error:
                self._unavailable('offline', error)
                return self.connection
            found = set(probe.get('matched', []))
            matched = [p for p in profiles if matches(p['anchors'], found)]
            # An empty, never-indexed legacy placeholder can adopt the first
            # library; populated catalogues always require identity evidence.
            if not matched and len(profiles) == 1 and not profiles[0]['anchors']:
                source = next(s for s in self.catalog.list_sources() if s['id'] == profiles[0]['source_id'])
                if not source['media_count']:
                    profiles[0]['anchors'] = probe.get('sample', [])
                    matched = profiles
            if len(matched) != 1:
                self._unavailable('unregistered', 'Текущая медиатека не зарегистрирована. Добавь её отдельной записью.')
                self.connection.update(count=probe.get('count', 0))
                return self.connection
            profile = matched[0]
            with self.catalog._write_lock, self.catalog.connect() as db:
                db.execute("UPDATE photos_libraries SET active=0,state='offline',error=NULL")
                db.execute("UPDATE photos_libraries SET active=1,state='ready',anchors=?,error=NULL,checked_at=? WHERE source_id=?",
                           (json.dumps(profile['anchors']), now(), profile['source_id']))
                db.execute("UPDATE sources SET status=CASE WHEN status='scanning' THEN status ELSE 'idle' END,error=NULL WHERE id=?", (profile['source_id'],))
            self.connection = dict(state='ready', source_id=profile['source_id'], count=probe.get('count', 0))
            return self.connection

    def authorize(self):
        self.adapter.status(request_authorization=True)
        return self.refresh_connection()

    def register(self, label):
        label = label.strip()
        if not label or len(label) > 120:
            raise ValueError('Задай название медиатеки до 120 символов')
        with self._lock:
            profiles = self._profiles()
            probe = self.adapter.probe([a for p in profiles for a in p['anchors']], restart=True)
            if any(matches(p['anchors'], probe.get('matched', [])) for p in profiles):
                raise ValueError('Эта медиатека уже сохранена. Для другого Apple ID открой отдельную системную медиатеку в Photos.')
            if not probe.get('sample'):
                raise ValueError('В текущей медиатеке пока нет объектов. Дождись её загрузки в Photos.')
            library_id = uuid.uuid4().hex
            with self.catalog._write_lock, self.catalog.connect() as db:
                cursor = db.execute("INSERT INTO sources(path,kind,role,label,comment,created_at) VALUES (?,'photos','source',?,'',?)",
                                    ('photos://' + library_id, label, now()))
                source_id = cursor.lastrowid
                db.execute("UPDATE photos_libraries SET active=0,state='offline'")
                db.execute("INSERT INTO photos_libraries(source_id,library_id,anchors,active,state,checked_at) VALUES (?,?,?,1,'ready',?)",
                           (source_id, library_id, json.dumps(probe.get('sample', [])), now()))
            self.connection = dict(state='ready', source_id=source_id, count=probe.get('count', 0))
            return self.profile(source_id)

    def rename(self, source_id, label):
        self.profile(source_id)
        if not label.strip() or len(label.strip()) > 120:
            raise ValueError('Задай название медиатеки до 120 символов')
        with self.catalog._write_lock, self.catalog.connect() as db:
            db.execute('UPDATE sources SET label=? WHERE id=?', (label.strip(), source_id))

    def set_paused(self, source_id, paused):
        with self._lock:
            self.profile(source_id)
            if not paused:
                connection = self.refresh_connection()
                if connection.get('source_id') != source_id:
                    raise PhotosLibraryUnavailable(connection.get('error') or 'Открой эту системную медиатеку на M4 и повтори подключение.')
                self.catalog.enqueue_source_thumbnails(source_id)
            with self.catalog._write_lock, self.catalog.connect() as db:
                db.execute('UPDATE photos_libraries SET paused=? WHERE source_id=?', (int(paused), source_id))
                if not paused:
                    db.execute('DELETE FROM thumbnail_waits WHERE media_id IN (SELECT id FROM media_files WHERE source_id=?)', (source_id,))

    def _require_active(self, source_id):
        profile = self.profile(source_id)
        if not profile['active'] or profile['state'] != 'ready':
            raise PhotosLibraryUnavailable('Эта медиатека сейчас не подключена. Сохранённые превью доступны.')
        return profile

    def scan(self, source_id):
        with self._lock:
            profile = self._require_active(source_id)
            assets = self.adapter.scan(profile['anchors'])
            self.catalog.replace_photos_scan(source_id, assets)
            self.catalog.enqueue_source_thumbnails(source_id)
            self.catalog.set_source_status(source_id, 'idle')
            if assets and not profile['anchors']:
                with self.catalog._write_lock, self.catalog.connect() as db:
                    db.execute('UPDATE photos_libraries SET anchors=? WHERE source_id=?',
                               (json.dumps([a['id'] for a in assets[:12]]), source_id))
            return assets

    def create_thumbnail(self, source_id, asset_identifier, target):
        with self._lock:
            profile = self._require_active(source_id)
            try:
                return self.adapter.create_thumbnail(asset_identifier, target, anchors=profile['anchors'])
            except (PhotosAccessDenied, PhotosLibraryUnavailable) as error:
                self._unavailable('no_access' if isinstance(error, PhotosAccessDenied) else 'offline', error)
                raise

    def open_asset(self, source_id, identifier):
        with self._lock:
            profile = self._require_active(source_id)
            probe = self.adapter.probe(profile['anchors'])
            if profile['anchors'] and not matches(profile['anchors'], probe.get('matched', [])):
                self._unavailable('offline', 'Открыта другая медиатека Photos')
                raise PhotosLibraryUnavailable('Открыта другая медиатека Photos')
            self.adapter.open_asset(identifier)

    def list(self):
        profiles = {p['source_id']: p for p in self._profiles()}
        try:
            volumes = {v['id']: v for v in self.storage.refresh(cached_only=True)['volumes']}
        except OSError:
            volumes = {}
        result = []
        with self.catalog.connect() as db:
            links = [dict(r) for r in db.execute('SELECT * FROM photos_copy_links WHERE connected=1 ORDER BY source_id,number')]
            waits = dict(db.execute('SELECT m.source_id,COUNT(*) FROM thumbnail_waits w JOIN media_files m ON m.id=w.media_id GROUP BY m.source_id'))
        for source in self.catalog.list_sources():
            if source['id'] not in profiles:
                continue
            profile = profiles[source['id']]
            copies = []
            for link in links:
                if link['source_id'] != source['id']:
                    continue
                volume = volumes.get(link['volume_id'], {})
                copies.append(dict(link, volume_name=volume.get('display_name') or volume.get('name') or 'Том недоступен',
                                   availability=volume.get('availability', 'unknown'),
                                   originals=self.originals.summary(link['id']) if self.originals else None))
            result.append(dict(source, library_id=profile['library_id'], active=bool(profile['active']),
                               paused=bool(profile['paused']), connection_state=profile['state'],
                               connection_error=profile['error'], waiting=waits.get(source['id'], 0), copies=copies))
        return dict(libraries=result, connection=self.connection)

    def bind_copy(self, source_id, volume_id, path):
        self.profile(source_id)
        path = relative_path(path)
        if not path:
            raise ValueError('Выбери отдельную папку копии, не корень диска')
        volume = next((v for v in self.storage.refresh(cached_only=True)['volumes'] if v['id'] == volume_id), None)
        if not volume or volume['availability'] != 'online':
            raise ValueError('Том копии должен быть подключён')
        # Only verify the destination; binding writes no marker or original.
        with open_readonly(volume, path, directory=True):
            pass
        with self.catalog._write_lock, self.catalog.connect() as db:
            existing = db.execute('SELECT * FROM photos_copy_links WHERE volume_id=? AND path=?', (volume_id, path)).fetchone()
            if existing and existing['source_id'] == source_id:
                db.execute('UPDATE photos_copy_links SET connected=1 WHERE id=?', (existing['id'],))
                return dict(existing, connected=1)
            for item in db.execute('SELECT * FROM photos_copy_links WHERE volume_id=?', (volume_id,)):
                if item['path'] == path or path.startswith(item['path'] + '/') or item['path'].startswith(path + '/'):
                    raise ValueError('Эта папка пересекается с другой копией медиатеки. Выбери отдельную папку.')
            number = db.execute('SELECT COALESCE(MAX(number),0)+1 FROM photos_copy_links WHERE source_id=?', (source_id,)).fetchone()[0]
            link = dict(id=uuid.uuid4().hex, source_id=source_id, volume_id=volume_id, path=path, number=number, created_at=now(), connected=1)
            db.execute('INSERT INTO photos_copy_links VALUES (:id,:source_id,:volume_id,:path,:number,:created_at,:connected)', link)
        return link

    def unbind_copy(self, source_id, link_id):
        self.profile(source_id)
        with self.catalog._write_lock, self.catalog.connect() as db:
            if not db.execute('UPDATE photos_copy_links SET connected=0 WHERE id=? AND source_id=?', (link_id, source_id)).rowcount:
                raise KeyError('Копия медиатеки не найдена')
