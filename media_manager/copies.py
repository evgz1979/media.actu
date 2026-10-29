"""Folder copy relationships. This catalog never copies or changes source files."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import PurePosixPath
from uuid import uuid4


COPY_KINDS = {'copy': 'Обычная копия', 'cold': 'Сменный носитель', 'cloud': 'Облако'}
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
'''


def copy_label(kind, number):
    suffix = {'main': 'main', 'copy': 'copy', 'cold': 'copy-cold', 'cloud': 'copy-cloud'}[kind]
    return f'{number:02d}-{suffix}'


def numbering_changes(copies):
    return [{'id': location['id'], 'from_label': copy_label(location['kind'], location['number']),
             'to_label': copy_label(location['kind'], number), 'number': number}
            for number, location in enumerate(copies, 1) if location['number'] != number]


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
            groups = [dict(row, main=None, copies=[]) for row in db.execute('SELECT * FROM copy_groups ORDER BY created_at,id')]
            by_id = {group['id']: group for group in groups}
            for row in db.execute('SELECT * FROM copy_locations ORDER BY number'):
                location = dict(row)
                volume = volumes.get(location['volume_id']) or self.storage.get_volume(location['volume_id'])
                location.update(label=copy_label(location['kind'], location['number']),
                                volume_name=volume.get('display_name') or volume['name'],
                                availability=volume.get('availability', 'unknown'), removable=volume.get('removable', False))
                if location['number'] == 0:
                    by_id[location['group_id']]['main'] = location
                else:
                    by_id[location['group_id']]['copies'].append(location)
            for group in groups:
                group['numbering_changes'] = numbering_changes(group['copies'])
                # Derive from current links, including catalogs written by older versions.
                group['next_number'] = None if group['numbering_changes'] else len(group['copies']) + 1
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
                    if numbering_changes(locations):
                        raise ValueError('В нумерации есть пропуски. Сначала согласуй переименование меток копий.')
                    self._check_overlap(db, volume_id, path)
                    number, timestamp = len(locations) + 1, datetime.now(timezone.utc).isoformat()
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
                raise KeyError('Ссылка на копию не найдена')
            if location['number'] == 0:
                raise ValueError('Основная папка всегда имеет метку 00-main')
            db.execute('UPDATE copy_locations SET kind=? WHERE id=?', (kind, location_id))
        return self.group(location['group_id'])

    def remove_copy(self, location_id):
        with self.storage._lock, self.storage.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            location = db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone()
            if location is None:
                raise KeyError('Ссылка на копию не найдена')
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
            for change in numbering_changes(locations):
                db.execute('UPDATE copy_locations SET number=? WHERE id=?', (change['number'], change['id']))
            db.execute('UPDATE copy_groups SET next_number=? WHERE id=?', (len(locations) + 1, group_id))
        return self.group(group_id)

    def remove_group(self, group_id):
        with self.storage._lock, self.storage.connect() as db:
            if not db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone():
                raise KeyError('Основная папка не найдена')
            db.execute('DELETE FROM copy_groups WHERE id=?', (group_id,))
