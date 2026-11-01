"""Read-only, virtual folders over a saved Photos catalogue."""
from pathlib import PurePosixPath

from .storage import relative_path


def photo_entry(row):
    return dict(path='/'.join(filter(None, (row['parent_path'], str(row['id'])))),
                name=row['name'], kind='file', media_kind=row['kind'], media_id=row['id'],
                size=row['size'] or None, modified_at=row['modified_at'],
                preview_ready=row['thumbnail_status'] == 'done')


class PhotosBrowser:
    def __init__(self, libraries):
        self.libraries = libraries
        self.catalog = libraries.catalog

    def browse(self, source_id, path='', *, offset=0, limit=150):
        profile = self.libraries.profile(source_id)
        source = self.catalog.get_source(source_id)
        path = relative_path(path)
        offset, limit = max(0, offset), min(1000, max(1, limit))
        with self.catalog.connect() as db:
            # A numeric leaf identifies a catalogue object, never an original path.
            leaf = PurePosixPath(path).name
            if path and leaf.isascii() and leaf.isdigit() and len(leaf) <= 18:
                row = db.execute('''SELECT m.*,j.status AS thumbnail_status
                    FROM media_files m LEFT JOIN thumbnail_jobs j ON j.media_id=m.id
                    WHERE m.source_id=? AND m.id=?''', (source_id, int(leaf))).fetchone()
                if row and photo_entry(row)['path'] == path:
                    return dict(entry=photo_entry(row), kind='file')
            groups = db.execute('''SELECT parent_path,COUNT(*) AS count,SUM(size) AS size
                FROM media_files WHERE source_id=? GROUP BY parent_path''', (source_id,)).fetchall()
            children = {}
            found = not path
            for group in groups:
                parent = group['parent_path']
                if parent == path:
                    found = True
                prefix = path + '/' if path else ''
                if parent.startswith(prefix) and parent != path:
                    found = True
                    name = parent[len(prefix):].split('/')[0]
                    child = children.setdefault(name, dict(name=name, path=prefix + name,
                        kind='directory', count=0, size=0))
                    child['count'] += group['count']
                    child['size'] += group['size'] or 0
            if not found:
                raise KeyError('Папка медиатеки не найдена')
            folders = sorted(children.values(), key=lambda e: e['name'].casefold())
            file_count = db.execute('SELECT COUNT(*) FROM media_files WHERE source_id=? AND parent_path=?',
                                    (source_id, path)).fetchone()[0]
            entries = folders[offset:offset + limit]
            remaining = limit - len(entries)
            if remaining:
                rows = db.execute('''SELECT m.*,j.status AS thumbnail_status
                    FROM media_files m LEFT JOIN thumbnail_jobs j ON j.media_id=m.id
                    WHERE m.source_id=? AND m.parent_path=?
                    ORDER BY m.name COLLATE NOCASE,m.id LIMIT ? OFFSET ?''',
                    (source_id, path, remaining, max(0, offset - len(folders)))).fetchall()
                entries.extend(photo_entry(row) for row in rows)
        self.catalog.prioritize_folder_thumbnails(source_id, path)
        total = len(folders) + file_count
        return dict(path=path, kind='directory', entries=entries, total=total,
                    has_more=offset + len(entries) < total,
                    scanned_at=source.get('last_scan_at') or source['created_at'],
                    cached=not bool(profile['active']), source_id=source_id)

    def preview_status(self, source_id, ids):
        self.libraries.profile(source_id)
        ids = list(dict.fromkeys(ids))[:1000]
        if not ids:
            return dict(ready=[])
        with self.catalog.connect() as db:
            ready = [r[0] for r in db.execute('''SELECT m.id FROM media_files m
                JOIN thumbnail_jobs j ON j.media_id=m.id
                WHERE m.source_id=? AND j.status='done' AND m.id IN (''' + ','.join('?' for _ in ids) + ')',
                (source_id, *ids))]
        return dict(ready=ready)
