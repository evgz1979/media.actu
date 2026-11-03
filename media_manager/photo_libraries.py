"""Separate Photos catalogues and copy destinations; never store originals here."""
from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
import json
from pathlib import PurePosixPath
import threading
import uuid

from .comparison import open_readonly
from .photos_adapter import PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable
from .storage import relative_path


# Возвращает текущее время UTC для записей профиля и журнала.
# Использует datetime.now, datetime.now(timezone.utc).isoformat.
def now():
    return datetime.now(timezone.utc).isoformat()


# Проверяет совпадение найденных ID с якорями сохранённой медиатеки.
# Использует set(anchors).intersection.
def matches(anchors, found):
    return bool(anchors) and len(set(anchors).intersection(found)) >= min(3, len(anchors))


# Управляет идентичностью, доступностью и привязанными копиями медиатек Photos.
# Зависимости конструктора: catalog, storage, adapter.
class PhotoLibraries:
    # Инициализирует PhotoLibraries и его рабочее состояние.
    # Обновляет состояние объекта: _lock, adapter, catalog, connection, originals, polling, schedule, storage.
    def __init__(self, catalog, storage, adapter):
        self.catalog, self.storage, self.adapter = catalog, storage, adapter
        self._lock = threading.RLock()
        self.connection = dict(state='unknown')
        self.polling = False
        self.originals = None
        self.schedule = None
        self._migrate()

    # Предоставляет транзакционное соединение медиаиндекса с гарантированным закрытием.
    # Использует db.close, self.catalog.connect.
    @contextmanager
    def _db(self):
        db = self.catalog.connect()
        try:
            with db:
                yield db
        finally:
            db.close()

    # Создаёт профили для прежних Photos-источников и сбрасывает активность до проверки.
    # Изменяет SQLite-таблицы: photos_copy_sources, photos_libraries.
    def _migrate(self):
        # Preserve legacy media IDs: their 3,410 cached previews remain valid.
        if getattr(self.adapter, 'supported', True) and not any(s['kind'] == 'photos' for s in self.catalog.list_sources()):
            self.catalog.add_system_photos_source()
        with self.catalog._write_lock, self._db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS photos_copy_sources (
                link_id TEXT PRIMARY KEY REFERENCES photos_copy_links(id) ON DELETE CASCADE,
                source_link_id TEXT NOT NULL)''')
            for source in db.execute("SELECT id FROM sources WHERE kind='photos'").fetchall():
                anchors = [r[0] for r in db.execute('SELECT relative_path FROM media_files WHERE source_id=? ORDER BY id LIMIT 12', (source['id'],))]
                db.execute('INSERT OR IGNORE INTO photos_libraries(source_id,library_id,anchors) VALUES (?,?,?)',
                           (source['id'], uuid.uuid4().hex, json.dumps(anchors)))
            db.execute("UPDATE photos_libraries SET active=0,state='unknown'")

    # Читает все профили и декодирует сохранённые якорные идентификаторы.
    # Читает SQLite-таблицы: photos_libraries.
    def _profiles(self):
        with self._db() as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM photos_libraries ORDER BY source_id')]
        for row in rows:
            row['anchors'] = json.loads(row['anchors'])
        return rows

    # Возвращает профиль медиатеки по ID источника либо поднимает KeyError.
    # Явно отклоняет недопустимое состояние через KeyError.
    def profile(self, source_id):
        profile = next((p for p in self._profiles() if p['source_id'] == source_id), None)
        if not profile:
            raise KeyError('Медиатека не найдена')
        return profile

    # Помечает медиатеки неактивными и сохраняет причину недоступности.
    # Изменяет SQLite-таблицы: photos_libraries, sources.
    def _unavailable(self, state, error):
        with self.catalog._write_lock, self._db() as db:
            db.execute('UPDATE photos_libraries SET active=0,state=?,error=?,checked_at=?', (state, str(error), now()))
            db.execute("UPDATE sources SET status=?,error=? WHERE kind='photos'", ('no_access' if state == 'no_access' else 'offline', str(error)))
        self.connection = dict(state=state, error=str(error))

    # Сопоставляет системную медиатеку с одним профилем через PhotoKit probe.
    # Изменяет SQLite-таблицы: photos_libraries, sources.
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
            with self.catalog._write_lock, self._db() as db:
                db.execute("UPDATE photos_libraries SET active=0,state='offline',error=NULL")
                db.execute("UPDATE photos_libraries SET active=1,state='ready',anchors=?,error=NULL,checked_at=? WHERE source_id=?",
                           (json.dumps(profile['anchors']), now(), profile['source_id']))
                db.execute("UPDATE sources SET status=CASE WHEN status='scanning' THEN status ELSE 'idle' END,error=NULL WHERE id=?", (profile['source_id'],))
            self.connection = dict(state='ready', source_id=profile['source_id'], count=probe.get('count', 0))
            return self.connection

    # Запрашивает системное разрешение Photos и повторяет сопоставление профиля.
    # Использует self.adapter.status, self.refresh_connection.
    def authorize(self):
        self.adapter.status(request_authorization=True)
        return self.refresh_connection()

    # Регистрирует текущую непустую медиатеку отдельным виртуальным источником.
    # Изменяет SQLite-таблицы: photos_libraries, sources.
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
            with self.catalog._write_lock, self._db() as db:
                cursor = db.execute("INSERT INTO sources(path,kind,role,label,comment,created_at) VALUES (?,'photos','source',?,'',?)",
                                    ('photos://' + library_id, label, now()))
                source_id = cursor.lastrowid
                db.execute("UPDATE photos_libraries SET active=0,state='offline'")
                db.execute("INSERT INTO photos_libraries(source_id,library_id,anchors,active,state,checked_at) VALUES (?,?,?,1,'ready',?)",
                           (source_id, library_id, json.dumps(probe.get('sample', [])), now()))
            self.connection = dict(state='ready', source_id=source_id, count=probe.get('count', 0))
            return self.profile(source_id)

    # Меняет пользовательское название сохранённой медиатеки.
    # Изменяет SQLite-таблицы: sources.
    def rename(self, source_id, label):
        self.profile(source_id)
        if not label.strip() or len(label.strip()) > 120:
            raise ValueError('Задай название медиатеки до 120 символов')
        with self.catalog._write_lock, self._db() as db:
            db.execute('UPDATE sources SET label=? WHERE id=?', (label.strip(), source_id))

    # Сохраняет ручную паузу превью медиатеки и обновляет очередь при продолжении.
    # Изменяет SQLite-таблицы: photos_libraries, thumbnail_waits.
    def set_paused(self, source_id, paused):
        with self._lock:
            self.profile(source_id)
            if not paused:
                connection = self.refresh_connection()
                if connection.get('source_id') != source_id:
                    raise PhotosLibraryUnavailable(connection.get('error') or 'Открой эту системную медиатеку на M4 и повтори подключение.')
                self.catalog.enqueue_source_thumbnails(source_id)
            with self.catalog._write_lock, self._db() as db:
                db.execute('UPDATE photos_libraries SET paused=? WHERE source_id=?', (int(paused), source_id))
                if not paused:
                    db.execute('DELETE FROM thumbnail_waits WHERE media_id IN (SELECT id FROM media_files WHERE source_id=?)', (source_id,))

    # Требует активную медиатеку в состоянии ready для обращения к PhotoKit.
    # Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
    def _require_active(self, source_id):
        profile = self.profile(source_id)
        if not profile['active'] or profile['state'] != 'ready':
            raise PhotosLibraryUnavailable('Эта медиатека сейчас не подключена. Сохранённые превью доступны.')
        return profile

    # Получает каталог активной медиатеки и обновляет индекс и якоря.
    # Изменяет SQLite-таблицы: photos_libraries.
    def scan(self, source_id):
        with self._lock:
            if self.schedule and self.schedule.blocked(source_id):
                raise PhotosLibraryUnavailable('Синхронизация разрешена только ночью: ' + self.schedule.describe(source_id)['window'])
            profile = self._require_active(source_id)
            assets = self.adapter.scan(profile['anchors'])
            self.catalog.replace_photos_scan(source_id, assets)
            self.catalog.enqueue_source_thumbnails(source_id)
            self.catalog.set_source_status(source_id, 'idle')
            if assets and not profile['anchors']:
                with self.catalog._write_lock, self._db() as db:
                    db.execute('UPDATE photos_libraries SET anchors=? WHERE source_id=?',
                               (json.dumps([a['id'] for a in assets[:12]]), source_id))
            return assets

    # Создаёт превью объекта только из подтверждённой активной медиатеки.
    # Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
    def create_thumbnail(self, source_id, asset_identifier, target):
        with self._lock:
            if self.schedule and self.schedule.blocked(source_id):
                raise PhotosLibraryUnavailable('Превью ожидают ночного окна')
            profile = self._require_active(source_id)
            try:
                return self.adapter.create_thumbnail(asset_identifier, target, anchors=profile['anchors'])
            except (PhotosAccessDenied, PhotosLibraryUnavailable) as error:
                self._unavailable('no_access' if isinstance(error, PhotosAccessDenied) else 'offline', error)
                raise

    # Выделяет объект активной медиатеки в системном приложении Photos.
    # Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.
    def open_asset(self, source_id, identifier):
        with self._lock:
            profile = self._require_active(source_id)
            probe = self.adapter.probe(profile['anchors'])
            if profile['anchors'] and not matches(profile['anchors'], probe.get('matched', [])):
                self._unavailable('offline', 'Открыта другая медиатека Photos')
                raise PhotosLibraryUnavailable('Открыта другая медиатека Photos')
            self.adapter.open_asset(identifier)

    # Собирает профили, виртуальные тома, прогресс превью, копии и расписание.
    # Поля результата: libraries, connection.
    def list(self):
        profiles = {p['source_id']: p for p in self._profiles()}
        try:
            volumes = {v['id']: v for v in self.storage.refresh(cached_only=True)['volumes']}
        except OSError:
            volumes = {}
        result = []
        with self._db() as db:
            links = [dict(r) for r in db.execute('SELECT * FROM photos_copy_links WHERE connected=1 ORDER BY source_id,number')]
            sources = dict(db.execute('SELECT link_id,source_link_id FROM photos_copy_sources'))
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
                upstream = next((c for c in links if c['id'] == sources.get(link['id'])), None)
                copies.append(dict(link, volume_name=volume.get('display_name') or volume.get('name') or 'Том недоступен',
                                   availability=volume.get('availability', 'unknown'),
                                   source_link_id=sources.get(link['id']),
                                   source_label=(f"{upstream['number']:02d}-copy" if upstream else
                                                 'Источник недоступен' if sources.get(link['id']) else 'Photos'),
                                   originals=self.originals.summary(link['id']) if self.originals else None))
            result.append(dict(source, library_id=profile['library_id'], active=bool(profile['active']),
                               paused=bool(profile['paused']), connection_state=profile['state'],
                               connection_error=profile['error'], waiting=waits.get(source['id'], 0), copies=copies,
                               sync_schedule=self.schedule.describe(source['id']) if self.schedule else None))
        return dict(libraries=result, connection=self.connection)

    # Возвращает ID копии-источника либо None для прямого источника Photos.
    # Читает SQLite-таблицы: photos_copy_sources.
    def copy_source(self, link_id):
        with self._db() as db:
            row = db.execute('SELECT source_link_id FROM photos_copy_sources WHERE link_id=?', (link_id,)).fetchone()
        return row[0] if row else None

    # Поднимается по цепочке источников к первой копии и проверяет циклы.
    # Явно отклоняет недопустимое состояние через ValueError.
    def root_copy(self, link_id):
        visited = set()
        while True:
            if link_id in visited:
                raise ValueError('Циклическая связь копий медиатеки')
            visited.add(link_id)
            source = self.copy_source(link_id)
            if source is None:
                return link_id
            link_id = source

    # Меняет источник копии медиатеки с проверкой связей и отсутствия циклов.
    # Изменяет SQLite-таблицы: photos_copy_sources, photos_sync_requests.
    def set_copy_source(self, source_id, link_id, source_link_id):
        self.profile(source_id)
        with self.catalog._write_lock, self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if self.originals and db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone():
                raise ValueError('Сначала приостанови сохранение оригиналов')
            nodes = {r['id']:dict(r) for r in db.execute('SELECT * FROM photos_copy_links WHERE source_id=?', (source_id,))}
            if link_id not in nodes or (source_link_id is not None and source_link_id not in nodes):
                raise ValueError('Источник должен быть копией этой медиатеки')
            edges = dict(db.execute('SELECT link_id,source_link_id FROM photos_copy_sources'))
            if source_link_id is None:
                edges.pop(link_id, None)
            else:
                edges[link_id] = source_link_id
            current, visited = link_id, set()
            while current in edges:
                if current in visited:
                    raise ValueError('Циклические связи копирования запрещены')
                visited.add(current)
                current = edges[current]
            if source_link_id is None:
                db.execute('DELETE FROM photos_copy_sources WHERE link_id=?', (link_id,))
            else:
                db.execute('INSERT OR REPLACE INTO photos_copy_sources VALUES (?,?)', (link_id, source_link_id))
                if db.execute("SELECT 1 FROM sqlite_master WHERE name='photos_sync_requests'").fetchone():
                    db.execute('UPDATE photos_sync_requests SET enabled=0 WHERE link_id=?', (link_id,))

    # Перенумеровывает копии медиатеки, ставя выбранную первой без изменения маршрутов.
    # Изменяет SQLite-таблицы: photos_copy_links.
    def make_first_copy(self, source_id, link_id):
        self.profile(source_id)
        with self.catalog._write_lock, self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if self.originals and db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone():
                raise ValueError('Сначала приостанови сохранение оригиналов')
            links = [r['id'] for r in db.execute('SELECT id FROM photos_copy_links WHERE source_id=? ORDER BY number', (source_id,))]
            if link_id not in links:
                raise KeyError('Копия медиатеки не найдена')
            links.remove(link_id)
            links.insert(0, link_id)
            db.execute('UPDATE photos_copy_links SET number=-number WHERE source_id=?', (source_id,))
            for number, identifier in enumerate(links, 1):
                db.execute('UPDATE photos_copy_links SET number=? WHERE id=?', (number, identifier))

    # Привязывает доступную проверенную папку к медиатеке с отдельным номером.
    # Изменяет SQLite-таблицы: photos_copy_links.
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
        with self.catalog._write_lock, self._db() as db:
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

    # Отключает привязку копии медиатеки, сохраняя запись и квитанции ресурсов.
    # Изменяет SQLite-таблицы: photos_copy_links.
    def unbind_copy(self, source_id, link_id):
        self.profile(source_id)
        with self.catalog._write_lock, self._db() as db:
            if not db.execute('UPDATE photos_copy_links SET connected=0 WHERE id=? AND source_id=?', (link_id, source_id)).rowcount:
                raise KeyError('Копия медиатеки не найдена')
