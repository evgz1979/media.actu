"""Folder copy relationships. This catalog never copies or changes source files."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from pathlib import PurePosixPath
from uuid import uuid4


COPY_KINDS = {'copy': 'Обычная копия', 'cold': 'Сменный носитель', 'cloud': 'Облако'}
FOLDER_LABELS = {'': 'Без метки', 'temporary': 'Временная', 'inbox': 'На разбор', 'archive': 'Архив'}
COPY_SCHEMA = '''
CREATE TABLE IF NOT EXISTS copy_groups (
    id TEXT PRIMARY KEY, next_number INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS copy_locations (
    id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES copy_groups(id) ON DELETE CASCADE,
    volume_id TEXT NOT NULL REFERENCES volumes(id),
    path TEXT NOT NULL, kind TEXT NOT NULL, number INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(group_id,number), UNIQUE(volume_id,path),
    CHECK ((kind='main' AND number=0) OR (kind IN ('copy','cold','cloud') AND number>0))
);
CREATE INDEX IF NOT EXISTS copy_locations_volume ON copy_locations(volume_id,path);
CREATE TABLE IF NOT EXISTS copy_group_settings (
    group_id TEXT PRIMARY KEY REFERENCES copy_groups(id) ON DELETE CASCADE,
    tracking INTEGER NOT NULL DEFAULT 0 CHECK(tracking IN (0,1)),
    label TEXT NOT NULL DEFAULT '' CHECK(label IN ('','temporary','inbox','archive')),
    changed_at TEXT
);
CREATE TABLE IF NOT EXISTS disconnected_copy_groups (
    group_id TEXT PRIMARY KEY REFERENCES copy_groups(id) ON DELETE CASCADE,
    disconnected_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS disconnected_copy_locations (
    location_id TEXT PRIMARY KEY REFERENCES copy_locations(id) ON DELETE CASCADE,
    disconnected_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS released_copy_locations (
    id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES copy_groups(id) ON DELETE CASCADE,
    volume_id TEXT NOT NULL REFERENCES volumes(id),
    path TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('copy','cold','cloud')),
    number INTEGER NOT NULL CHECK(number>0), created_at TEXT NOT NULL,
    disconnected_at TEXT NOT NULL, released_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS released_copy_locations_group ON released_copy_locations(group_id,number);
'''


def copy_label(kind, number):
    suffix = {'main': 'main', 'copy': 'copy', 'cold': 'copy-cold', 'cloud': 'copy-cloud'}[kind]
    return f'{number:02d}-{suffix}'


def numbering_changes(copies, released_numbers=()):
    reusable = set(released_numbers) - {location['number'] for location in copies}
    numbers = (number for number in count(1) if number not in reusable)
    return [{'id': location['id'], 'from_label': copy_label(location['kind'], location['number']),
             'to_label': copy_label(location['kind'], number), 'number': number}
            for number, location in zip(numbers, copies) if location['number'] != number]


def next_copy_number(copies, released_numbers=()):
    if numbering_changes(copies, released_numbers):
        return None
    occupied = {location['number'] for location in copies}
    return min((set(released_numbers) - occupied) | {max(occupied, default=0) + 1})


def inherited_location(path, locations):
    parents = [location for location in locations
               if not location['path'] or path == location['path'] or path.startswith(location['path'] + '/')]
    if not parents:
        return None
    location = max(parents, key=lambda row: len(row['path']))
    return {**location, 'label': copy_label(location['kind'], location['number']),
            'is_root': path == location['path'], 'inherited_from': None if path == location['path'] else location['path']}


class CopyCatalog:
    def __init__(self, storage):
        self.storage = storage

    def _folder(self, volume_id, path):
        # metadata validates the relative path and remembered volume without touching files.
        self.storage.metadata(volume_id, path)
        path = str(PurePosixPath(path))
        path = '' if path == '.' else path
        volume = self.storage.get_volume(volume_id)
        if volume['identity_status'] in ('unverified', 'legacy'):
            raise ValueError('Сначала подтверди подключённый диск.')
        if path:
            with self.storage.connect() as db:
                known = db.execute('SELECT 1 FROM directories WHERE volume_id=? AND path=?', (volume_id, path)).fetchone()
                parent = str(PurePosixPath(path).parent)
                snapshot = self.storage._snapshot(db, volume_id, '' if parent == '.' else parent)
            if not known and not any(e['path'] == path and e['kind'] == 'directory' for e in snapshot['entries']):
                raise ValueError('Выбери известную папку в дереве.')
        return path

    @staticmethod
    def _check_overlap(db, volume_id, path):
        for location in db.execute('SELECT path,kind,number FROM copy_locations WHERE volume_id=?', (volume_id,)):
            other = location['path']
            if not path or not other or path == other or path.startswith(other + '/') or other.startswith(path + '/'):
                raise ValueError('Папка пересекается с областью ' + copy_label(location['kind'], location['number']) +
                                 '. Метка должна однозначно распространяться на все вложенные папки.')

    def groups(self):
        volumes = {v['id']: v for v in self.storage.refresh()['volumes']}
        with self.storage.connect() as db:
            groups = [dict(row, main=None, copies=[], released_copies=[]) for row in db.execute('''
                SELECT g.*, COALESCE(s.tracking,0) AS tracking, COALESCE(s.label,'') AS label, s.changed_at,
                       d.disconnected_at
                FROM copy_groups g LEFT JOIN copy_group_settings s ON s.group_id=g.id
                LEFT JOIN disconnected_copy_groups d ON d.group_id=g.id
                ORDER BY g.created_at,g.id''')]
            by_id = {group['id']: group for group in groups}
            for row in db.execute('''SELECT l.*,d.disconnected_at FROM copy_locations l
                                     LEFT JOIN disconnected_copy_locations d ON d.location_id=l.id ORDER BY l.number'''):
                location = dict(row)
                location['connected'] = not (location['disconnected_at'] or by_id[location['group_id']]['disconnected_at'])
                volume = volumes.get(location['volume_id']) or self.storage.get_volume(location['volume_id'])
                location.update(label=copy_label(location['kind'], location['number']),
                                volume_name=volume.get('display_name') or volume['name'],
                                availability=volume.get('availability', 'unknown'), removable=volume.get('removable', False))
                if location['number'] == 0:
                    by_id[location['group_id']]['main'] = location
                else:
                    by_id[location['group_id']]['copies'].append(location)
            for row in db.execute('SELECT * FROM released_copy_locations ORDER BY released_at,id'):
                location = dict(row)
                volume = volumes.get(location['volume_id']) or self.storage.get_volume(location['volume_id'])
                location.update(connected=False, number_released=True,
                                label='Прежняя ' + copy_label(location['kind'], location['number']),
                                volume_name=volume.get('display_name') or volume['name'],
                                availability=volume.get('availability', 'unknown'), removable=volume.get('removable', False))
                by_id[location['group_id']]['released_copies'].append(location)
            for group in groups:
                group['connected'] = not bool(group['disconnected_at'])
                group['tracking'] = bool(group['tracking'])
                released = [copy['number'] for copy in group['released_copies']]
                group['numbering_changes'] = numbering_changes(group['copies'], released)
                # Derive from current links, including catalogs written by older versions.
                group['next_number'] = next_copy_number(group['copies'], released)
        return groups

    def group(self, group_id):
        group = next((group for group in self.groups() if group['id'] == group_id), None)
        if group is None:
            raise KeyError('Группа копий не найдена')
        return group

    def create_main(self, volume_id, path):
        with self.storage._lock:
            path = self._folder(volume_id, path)
            if not path:
                raise ValueError('Выбери конкретную основную папку внутри тома.')
            with self.storage.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                existing = db.execute('SELECT * FROM copy_locations WHERE volume_id=? AND path=?', (volume_id, path)).fetchone()
                if existing and existing['number'] == 0:
                    group_id = existing['group_id']
                else:
                    self._check_overlap(db, volume_id, path)
                    group_id, timestamp = uuid4().hex, datetime.now(timezone.utc).isoformat()
                    db.execute('INSERT INTO copy_groups VALUES (?,1,?)', (group_id, timestamp))
                    db.execute('INSERT INTO copy_locations VALUES (?,?,?,?,?,?,?)',
                               (uuid4().hex, group_id, volume_id, path, 'main', 0, timestamp))
        return self.group(group_id)

    def update_group(self, group_id, changes):
        if not changes or set(changes) - {'tracking', 'label'}:
            raise ValueError('Нужна метка папки или настройка отслеживания')
        if 'label' in changes and changes['label'] not in FOLDER_LABELS:
            raise ValueError('Неизвестная метка папки')
        if 'tracking' in changes and type(changes['tracking']) is not bool:
            raise ValueError('Отслеживание должно быть включено или выключено')
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone():
                raise KeyError('Основная папка не найдена')
            db.execute('INSERT OR IGNORE INTO copy_group_settings(group_id) VALUES (?)', (group_id,))
            for key, value in changes.items():
                db.execute(f'UPDATE copy_group_settings SET {key}=? WHERE group_id=?', (value, group_id))
        return self.group(group_id)

    def mark_changed(self, group_id):
        with self.storage.connect() as db:
            db.execute('''UPDATE copy_group_settings SET changed_at=? WHERE group_id=? AND tracking=1
                          AND NOT EXISTS (SELECT 1 FROM disconnected_copy_groups WHERE group_id=copy_group_settings.group_id)''',
                       (datetime.now(timezone.utc).isoformat(), group_id))

    def set_group_connected(self, group_id, connected):
        if type(connected) is not bool:
            raise ValueError('Нужно включить или отключить связь')
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone():
                raise KeyError('Основная папка не найдена')
            if connected:
                db.execute('DELETE FROM disconnected_copy_groups WHERE group_id=?', (group_id,))
            else:
                db.execute('INSERT OR IGNORE INTO disconnected_copy_groups VALUES (?,?)',
                           (group_id, datetime.now(timezone.utc).isoformat()))
        return self.group(group_id)

    def set_copy_connected(self, location_id, connected):
        if type(connected) is not bool:
            raise ValueError('Нужно включить или отключить связь')
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            location = db.execute('SELECT group_id,number FROM copy_locations WHERE id=?', (location_id,)).fetchone()
            released = location is None
            if location is None:
                archived = db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone()
                if archived is None:
                    raise KeyError('Ссылка на копию не найдена')
                if connected:
                    if db.execute('SELECT 1 FROM copy_locations WHERE group_id=? AND number=?',
                                  (archived['group_id'], archived['number'])).fetchone():
                        raise ValueError(f"Номер {archived['number']:02d} уже занят другой привязкой. Прежняя история сохранена.")
                    self._check_overlap(db, archived['volume_id'], archived['path'])
                    db.execute('INSERT INTO copy_locations(id,group_id,volume_id,path,kind,number,created_at) VALUES (?,?,?,?,?,?,?)',
                               tuple(archived[key] for key in ('id','group_id','volume_id','path','kind','number','created_at')))
                    db.execute('DELETE FROM released_copy_locations WHERE id=?', (location_id,))
                location = archived
            if location['number'] == 0:
                raise ValueError('Основную папку отключают вместе с её набором')
            if connected:
                db.execute('DELETE FROM disconnected_copy_locations WHERE location_id=?', (location_id,))
            elif not released:
                db.execute('INSERT OR IGNORE INTO disconnected_copy_locations VALUES (?,?)',
                           (location_id, datetime.now(timezone.utc).isoformat()))
        return self.group(location['group_id'])

    def release_copy_number(self, location_id, number, kind):
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            location = db.execute('''SELECT l.*,d.disconnected_at,g.disconnected_at AS group_disconnected_at
                FROM copy_locations l LEFT JOIN disconnected_copy_locations d ON d.location_id=l.id
                LEFT JOIN disconnected_copy_groups g ON g.group_id=l.group_id WHERE l.id=?''', (location_id,)).fetchone()
            if location is None:
                location = db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone()
                if location is None:
                    raise KeyError('Ссылка на копию не найдена')
                if (location['number'], location['kind']) != (number, kind):
                    raise ValueError('Метка копии изменилась. Обнови список и повтори действие.')
            else:
                if location['number'] == 0:
                    raise ValueError('Номер основной папки нельзя освобождать')
                if (location['number'], location['kind']) != (number, kind):
                    raise ValueError('Метка копии изменилась. Обнови список и повтори действие.')
                if not (location['disconnected_at'] or location['group_disconnected_at']):
                    raise ValueError('Сначала отключи эту копию')
                timestamp = datetime.now(timezone.utc).isoformat()
                db.execute('INSERT INTO released_copy_locations VALUES (?,?,?,?,?,?,?,?,?)',
                           (*tuple(location[key] for key in ('id','group_id','volume_id','path','kind','number','created_at')),
                            location['disconnected_at'] or location['group_disconnected_at'], timestamp))
                db.execute('DELETE FROM copy_locations WHERE id=?', (location_id,))
        return self.group(location['group_id'])

    def acknowledge_changes(self, group_id, changed_at):
        with self.storage.connect() as db:
            if not db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone():
                raise KeyError('Основная папка не найдена')
            # A newer event must survive a click from an older sidebar snapshot.
            db.execute('UPDATE copy_group_settings SET changed_at=NULL WHERE group_id=? AND changed_at=?',
                       (group_id, changed_at))
        return self.group(group_id)

    def add_copy(self, group_id, volume_id, path, kind='copy'):
        if kind not in COPY_KINDS:
            raise ValueError('Неизвестный тип копии')
        with self.storage._lock:
            path = self._folder(volume_id, path)
            if not path:
                raise ValueError('Выбери папку назначения внутри тома.')
            with self.storage.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                group = db.execute('SELECT * FROM copy_groups WHERE id=?', (group_id,)).fetchone()
                if group is None:
                    raise KeyError('Основная папка не найдена')
                existing = db.execute('SELECT * FROM copy_locations WHERE volume_id=? AND path=?', (volume_id, path)).fetchone()
                if existing and existing['group_id'] == group_id and existing['number'] > 0:
                    if existing['kind'] != kind:
                        raise ValueError('Эта папка уже связана. Тип можно изменить в меню её ссылки.')
                else:
                    locations = db.execute('SELECT * FROM copy_locations WHERE group_id=? AND number>0 ORDER BY number',
                                           (group_id,)).fetchall()
                    released = [row['number'] for row in db.execute('SELECT number FROM released_copy_locations WHERE group_id=?', (group_id,))]
                    number = next_copy_number(locations, released)
                    if number is None:
                        raise ValueError('В нумерации есть пропуски. Сначала согласуй переименование меток копий.')
                    self._check_overlap(db, volume_id, path)
                    timestamp = datetime.now(timezone.utc).isoformat()
                    db.execute('INSERT INTO copy_locations VALUES (?,?,?,?,?,?,?)',
                               (uuid4().hex, group_id, volume_id, path, kind, number, timestamp))
                    db.execute('UPDATE copy_groups SET next_number=? WHERE id=?', (number + 1, group_id))
        return self.group(group_id)

    def change_kind(self, location_id, kind):
        if kind not in COPY_KINDS:
            raise ValueError('Неизвестный тип копии')
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            location = db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone()
            if location is None:
                raise KeyError('Действующая ссылка на копию не найдена')
            if location['number'] == 0:
                raise ValueError('Основная папка всегда имеет метку 00-main')
            db.execute('UPDATE copy_locations SET kind=? WHERE id=?', (kind, location_id))
        return self.group(location['group_id'])

    def remove_copy(self, location_id):
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            location = db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone()
            if location is None:
                archived = db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone()
                if archived is None:
                    raise KeyError('Ссылка на копию не найдена')
                db.execute('DELETE FROM released_copy_locations WHERE id=?', (location_id,))
                return
            if location['number'] == 0:
                raise ValueError('Основную папку убирают вместе с её списком копий')
            db.execute('DELETE FROM copy_locations WHERE id=?', (location_id,))
            next_number = db.execute('SELECT COALESCE(MAX(number),0)+1 FROM copy_locations WHERE group_id=?',
                                     (location['group_id'],)).fetchone()[0]
            db.execute('UPDATE copy_groups SET next_number=? WHERE id=?', (next_number, location['group_id']))

    def renumber_copies(self, group_id, expected_copies):
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone():
                raise KeyError('Основная папка не найдена')
            locations = [dict(row) for row in db.execute(
                'SELECT id,kind,number FROM copy_locations WHERE group_id=? AND number>0 ORDER BY number', (group_id,))]
            if locations != expected_copies:
                raise ValueError('Список копий изменился. Проверь и подтверди новое предложение переименования.')
            # Moving numbers down in ascending order cannot collide with an existing number.
            released = [row['number'] for row in db.execute('SELECT number FROM released_copy_locations WHERE group_id=?', (group_id,))]
            for change in numbering_changes(locations, released):
                db.execute('UPDATE copy_locations SET number=? WHERE id=?', (change['number'], change['id']))
            db.execute('UPDATE copy_groups SET next_number=? WHERE id=?', (len(locations) + 1, group_id))
        return self.group(group_id)

    def remove_group(self, group_id):
        with self.storage._lock, self.storage.connect() as db:
            if not db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone():
                raise KeyError('Основная папка не найдена')
            db.execute('DELETE FROM copy_groups WHERE id=?', (group_id,))
