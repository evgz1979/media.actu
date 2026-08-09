from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path, PurePath

from media_manager.scanner import ScanReport, normalize_source


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL DEFAULT 'folder',
    role TEXT NOT NULL DEFAULT 'source',
    label TEXT,
    comment TEXT,
    created_at TEXT NOT NULL,
    last_scan_at TEXT,
    status TEXT NOT NULL DEFAULT 'idle',
    error TEXT
);

CREATE TABLE IF NOT EXISTS media_files (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    relative_path TEXT NOT NULL,
    parent_path TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('photo', 'video')),
    size INTEGER NOT NULL,
    modified_at TEXT NOT NULL,
    seen_token TEXT NOT NULL,
    UNIQUE(source_id, relative_path)
);

CREATE INDEX IF NOT EXISTS media_files_source_parent
ON media_files(source_id, parent_path);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS thumbnail_jobs (
    media_id INTEGER PRIMARY KEY REFERENCES media_files(id) ON DELETE CASCADE,
    media_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'done', 'error')),
    priority INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    queued_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
);

CREATE INDEX IF NOT EXISTS thumbnail_jobs_status_priority
ON thumbnail_jobs(status, priority DESC, queued_at);

INSERT OR IGNORE INTO metadata(key, value) VALUES ('catalog_revision', '0');
INSERT OR IGNORE INTO metadata(key, value) VALUES ('thumbnail_queue_paused', '0');
"""


class Catalog:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = threading.RLock()
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(sources)").fetchall()
            }
            if "role" not in columns:
                connection.execute(
                    "ALTER TABLE sources ADD COLUMN role TEXT NOT NULL DEFAULT 'source'"
                )
            if "label" not in columns:
                connection.execute("ALTER TABLE sources ADD COLUMN label TEXT")
            if "comment" not in columns:
                connection.execute("ALTER TABLE sources ADD COLUMN comment TEXT")
            if "kind" not in columns:
                connection.execute(
                    "ALTER TABLE sources ADD COLUMN kind TEXT NOT NULL DEFAULT 'folder'"
                )

    def add_source(
        self,
        raw_path: str | Path,
        *,
        role: str = "source",
        label: str = "",
        comment: str = "",
    ) -> dict[str, object]:
        if role not in {"source", "storage"}:
            raise ValueError(f"Неизвестная роль папки: {role}")
        source = normalize_source(raw_path)
        now = datetime.now().astimezone().isoformat()
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sources(path, role, label, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(source), role, label.strip() or source.name, comment.strip(), now),
            )
            row = connection.execute(
                "SELECT * FROM sources WHERE path = ?", (str(source),)
            ).fetchone()
        assert row is not None
        return dict(row)

    def add_system_photos_source(self) -> dict[str, object]:
        now = datetime.now().astimezone().isoformat()
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sources(
                    path, kind, role, label, comment, created_at
                ) VALUES ('photos://system', 'photos', 'source', ?, ?, ?)
                """,
                (
                    "Системная медиатека Photos",
                    "Системный адаптер Photos · только чтение",
                    now,
                ),
            )
            connection.execute(
                """
                UPDATE sources
                SET kind = 'photos',
                    label = 'Системная медиатека Photos',
                    comment = 'Системный адаптер Photos · только чтение'
                WHERE path = 'photos://system'
                """
            )
            row = connection.execute(
                "SELECT * FROM sources WHERE path = 'photos://system'"
            ).fetchone()
        assert row is not None
        return dict(row)

    def update_source_metadata(
        self, source_id: int, *, role: str, label: str, comment: str
    ) -> dict[str, object]:
        if role not in {"source", "storage"}:
            raise ValueError(f"Неизвестная роль папки: {role}")
        with self._write_lock, self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE sources SET role = ?, label = ?, comment = ? WHERE id = ?
                """,
                (role, label.strip(), comment.strip(), source_id),
            )
            if cursor.rowcount == 0:
                raise KeyError(source_id)
        source = self.get_source(source_id)
        assert source is not None
        return source

    def remove_source(self, source_id: int) -> None:
        with self._write_lock, self.connect() as connection:
            connection.execute("DELETE FROM sources WHERE id = ?", (source_id,))

    def get_source(self, source_id: int) -> dict[str, object] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM sources WHERE id = ?", (source_id,)
            ).fetchone()
        return dict(row) if row else None

    def resolve_source_folder(self, source_id: int, folder: str = "") -> Path:
        source = self.get_source(source_id)
        if source is None:
            raise KeyError(source_id)
        if source.get("kind") != "folder":
            raise PermissionError("Виртуальный источник нельзя открыть в Finder")

        source_path = Path(str(source["path"])).resolve()
        relative = PurePath(folder)
        if relative.is_absolute() or ".." in relative.parts:
            raise PermissionError("Каталог находится вне выбранного источника")

        target = (source_path / relative).resolve()
        if target != source_path and source_path not in target.parents:
            raise PermissionError("Каталог находится вне выбранного источника")
        if not target.is_dir():
            raise FileNotFoundError(target)
        return target

    def list_sources(self) -> list[dict[str, object]]:
        query = """
            SELECT sources.*, COUNT(media_files.id) AS media_count,
                   COALESCE(SUM(media_files.size), 0) AS total_size,
                   COALESCE(SUM(media_files.kind = 'photo'), 0) AS thumbnail_total,
                   COALESCE(SUM(thumbnail_jobs.status = 'done'), 0) AS thumbnail_done,
                   COALESCE(SUM(thumbnail_jobs.status = 'pending'), 0) AS thumbnail_pending,
                   COALESCE(SUM(thumbnail_jobs.status = 'running'), 0) AS thumbnail_running,
                   COALESCE(SUM(thumbnail_jobs.status = 'error'), 0) AS thumbnail_error
            FROM sources
            LEFT JOIN media_files ON media_files.source_id = sources.id
            LEFT JOIN thumbnail_jobs ON thumbnail_jobs.media_id = media_files.id
            GROUP BY sources.id
            ORDER BY sources.role, sources.path COLLATE NOCASE
        """
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query).fetchall()]

    def set_source_status(self, source_id: int, status: str, error: str | None = None) -> None:
        with self._write_lock, self.connect() as connection:
            connection.execute(
                "UPDATE sources SET status = ?, error = ? WHERE id = ?",
                (status, error, source_id),
            )

    def replace_source_scan(self, source_id: int, report: ScanReport) -> None:
        token = uuid.uuid4().hex
        now = datetime.now().astimezone().isoformat()
        rows = []
        for item in report.files:
            relative = PurePath(item.relative_path)
            parent = "" if str(relative.parent) == "." else str(relative.parent)
            rows.append(
                (
                    source_id,
                    item.relative_path,
                    parent,
                    relative.name,
                    item.kind,
                    item.size,
                    item.modified_at,
                    token,
                )
            )

        with self._write_lock, self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO media_files(
                    source_id, relative_path, parent_path, name, kind,
                    size, modified_at, seen_token
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, relative_path) DO UPDATE SET
                    parent_path = excluded.parent_path,
                    name = excluded.name,
                    kind = excluded.kind,
                    size = excluded.size,
                    modified_at = excluded.modified_at,
                    seen_token = excluded.seen_token
                """,
                rows,
            )
            connection.execute(
                "DELETE FROM media_files WHERE source_id = ? AND seen_token != ?",
                (source_id, token),
            )
            connection.execute(
                """
                UPDATE sources
                SET last_scan_at = ?,
                    status = CASE
                        WHEN status = 'scanning' THEN 'scanning'
                        ELSE 'idle'
                    END,
                    error = NULL
                WHERE id = ?
                """,
                (now, source_id),
            )
            connection.execute(
                """
                UPDATE metadata
                SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT)
                WHERE key = 'catalog_revision'
                """
            )

    def replace_photos_scan(
        self, source_id: int, assets: list[dict[str, object]]
    ) -> None:
        token = uuid.uuid4().hex
        now = datetime.now().astimezone().isoformat()
        rows = []
        for asset in assets:
            created_at = str(asset.get("created_at") or "")
            if created_at:
                created = datetime.fromisoformat(created_at)
                parent = f"{created.year:04d}/{created.year:04d}-{created.month:02d}"
                modified_at = created.astimezone().isoformat()
            else:
                parent = "Без даты"
                modified_at = now
            rows.append(
                (
                    source_id,
                    str(asset["id"]),
                    parent,
                    str(asset.get("name") or asset["id"]),
                    str(asset["kind"]),
                    int(asset.get("size") or 0),
                    modified_at,
                    token,
                )
            )

        with self._write_lock, self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO media_files(
                    source_id, relative_path, parent_path, name, kind,
                    size, modified_at, seen_token
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, relative_path) DO UPDATE SET
                    parent_path = excluded.parent_path,
                    name = excluded.name,
                    kind = excluded.kind,
                    size = excluded.size,
                    modified_at = excluded.modified_at,
                    seen_token = excluded.seen_token
                """,
                rows,
            )
            connection.execute(
                "DELETE FROM media_files WHERE source_id = ? AND seen_token != ?",
                (source_id, token),
            )
            connection.execute(
                """
                UPDATE sources
                SET last_scan_at = ?,
                    status = CASE
                        WHEN status = 'scanning' THEN 'scanning'
                        ELSE 'idle'
                    END,
                    error = NULL
                WHERE id = ?
                """,
                (now, source_id),
            )
            connection.execute(
                """
                UPDATE metadata
                SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT)
                WHERE key = 'catalog_revision'
                """
            )

    def enqueue_source_thumbnails(self, source_id: int, priority: int = 0) -> int:
        now = datetime.now().astimezone().isoformat()
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                INSERT INTO thumbnail_jobs(
                    media_id, media_version, status, priority, attempts,
                    error, queued_at, started_at, finished_at
                )
                SELECT id, CAST(size AS TEXT) || ':' || modified_at,
                       'pending', ?, 0, NULL, ?, NULL, NULL
                FROM media_files
                WHERE source_id = ? AND kind = 'photo'
                ON CONFLICT(media_id) DO UPDATE SET
                    media_version = excluded.media_version,
                    status = CASE
                        WHEN thumbnail_jobs.media_version != excluded.media_version
                            THEN 'pending'
                        WHEN thumbnail_jobs.status = 'error' THEN 'pending'
                        ELSE thumbnail_jobs.status
                    END,
                    priority = MAX(thumbnail_jobs.priority, excluded.priority),
                    error = CASE
                        WHEN thumbnail_jobs.status = 'error' THEN NULL
                        ELSE thumbnail_jobs.error
                    END,
                    queued_at = CASE
                        WHEN thumbnail_jobs.media_version != excluded.media_version
                             OR thumbnail_jobs.status = 'error'
                            THEN excluded.queued_at
                        ELSE thumbnail_jobs.queued_at
                    END
                """,
                (priority, now, source_id),
            )
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM thumbnail_jobs
                JOIN media_files ON media_files.id = thumbnail_jobs.media_id
                WHERE media_files.source_id = ?
                  AND thumbnail_jobs.status IN ('pending', 'running')
                """,
                (source_id,),
            ).fetchone()
        return int(row["count"]) if row else 0

    def enqueue_all_thumbnails(self) -> None:
        for source in self.list_sources():
            self.enqueue_source_thumbnails(int(source["id"]))

    def prioritize_folder_thumbnails(
        self, source_id: int, folder: str, priority: int = 100
    ) -> None:
        now = datetime.now().astimezone().isoformat()
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                INSERT INTO thumbnail_jobs(
                    media_id, media_version, status, priority, attempts,
                    error, queued_at, started_at, finished_at
                )
                SELECT id, CAST(size AS TEXT) || ':' || modified_at,
                       'pending', ?, 0, NULL, ?, NULL, NULL
                FROM media_files
                WHERE source_id = ? AND parent_path = ? AND kind = 'photo'
                ON CONFLICT(media_id) DO UPDATE SET
                    priority = CASE
                        WHEN thumbnail_jobs.status = 'pending'
                            THEN MAX(thumbnail_jobs.priority, excluded.priority)
                        ELSE thumbnail_jobs.priority
                    END
                """,
                (priority, now, source_id, folder),
            )

    def enqueue_media_thumbnail(self, media_id: int, priority: int = 200) -> None:
        media = self.get_media(media_id)
        if media is None or media.get("kind") != "photo":
            return
        now = datetime.now().astimezone().isoformat()
        version = f"{media['size']}:{media['modified_at']}"
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                INSERT INTO thumbnail_jobs(
                    media_id, media_version, status, priority, attempts,
                    error, queued_at, started_at, finished_at
                ) VALUES (?, ?, 'pending', ?, 0, NULL, ?, NULL, NULL)
                ON CONFLICT(media_id) DO UPDATE SET
                    status = CASE
                        WHEN thumbnail_jobs.status = 'running' THEN 'running'
                        ELSE 'pending'
                    END,
                    priority = MAX(thumbnail_jobs.priority, excluded.priority),
                    error = NULL,
                    queued_at = CASE
                        WHEN thumbnail_jobs.status = 'running'
                            THEN thumbnail_jobs.queued_at
                        ELSE excluded.queued_at
                    END
                """,
                (media_id, version, priority, now),
            )

    def reset_stale_source_scans(self) -> None:
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                UPDATE sources SET status = 'idle', error = NULL
                WHERE status = 'scanning'
                """
            )

    def reset_running_thumbnail_jobs(self) -> None:
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                UPDATE thumbnail_jobs
                SET status = 'pending', started_at = NULL
                WHERE status = 'running'
                """
            )

    def claim_thumbnail_job(self, source_kind: str) -> int | None:
        now = datetime.now().astimezone().isoformat()
        with self._write_lock, self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT thumbnail_jobs.media_id
                FROM thumbnail_jobs
                JOIN media_files ON media_files.id = thumbnail_jobs.media_id
                JOIN sources ON sources.id = media_files.source_id
                WHERE thumbnail_jobs.status = 'pending'
                  AND sources.kind = ?
                  AND sources.status != 'scanning'
                ORDER BY thumbnail_jobs.priority DESC,
                         thumbnail_jobs.queued_at,
                         thumbnail_jobs.media_id
                LIMIT 1
                """,
                (source_kind,),
            ).fetchone()
            if row is None:
                return None
            media_id = int(row["media_id"])
            connection.execute(
                """
                UPDATE thumbnail_jobs
                SET status = 'running', attempts = attempts + 1,
                    started_at = ?, error = NULL
                WHERE media_id = ?
                """,
                (now, media_id),
            )
        return media_id

    def finish_thumbnail_job(
        self, media_id: int, *, error: str | None = None
    ) -> None:
        now = datetime.now().astimezone().isoformat()
        status = "error" if error else "done"
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                UPDATE thumbnail_jobs
                SET status = ?, error = ?, finished_at = ?, priority = 0
                WHERE media_id = ?
                """,
                (status, error, now, media_id),
            )

    def release_thumbnail_job(self, media_id: int) -> None:
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                UPDATE thumbnail_jobs
                SET status = 'pending', started_at = NULL
                WHERE media_id = ?
                """,
                (media_id,),
            )

    def thumbnail_queue_summary(self) -> dict[str, int | bool]:
        with self.connect() as connection:
            counts = {
                str(row["status"]): int(row["count"])
                for row in connection.execute(
                    "SELECT status, COUNT(*) AS count FROM thumbnail_jobs GROUP BY status"
                ).fetchall()
            }
            paused_row = connection.execute(
                "SELECT value FROM metadata WHERE key = 'thumbnail_queue_paused'"
            ).fetchone()
        return {
            "total": sum(counts.values()),
            "pending": counts.get("pending", 0),
            "running": counts.get("running", 0),
            "done": counts.get("done", 0),
            "error": counts.get("error", 0),
            "paused": bool(int(paused_row["value"])) if paused_row else False,
        }

    def set_thumbnail_queue_paused(self, paused: bool) -> None:
        with self._write_lock, self.connect() as connection:
            connection.execute(
                """
                UPDATE metadata SET value = ? WHERE key = 'thumbnail_queue_paused'
                """,
                ("1" if paused else "0",),
            )

    def thumbnail_queue_paused(self) -> bool:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT value FROM metadata WHERE key = 'thumbnail_queue_paused'"
            ).fetchone()
        return bool(int(row["value"])) if row else False

    def revision(self) -> int:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT value FROM metadata WHERE key = 'catalog_revision'"
            ).fetchone()
        return int(row["value"]) if row else 0

    def summary(self) -> dict[str, int]:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total,
                       COALESCE(SUM(kind = 'photo'), 0) AS photos,
                       COALESCE(SUM(kind = 'video'), 0) AS videos,
                       COALESCE(SUM(size), 0) AS bytes
                FROM media_files
                """
            ).fetchone()
        assert row is not None
        result = {key: int(row[key]) for key in row.keys()}
        result["revision"] = self.revision()
        return result

    def folder_tree(self, source_id: int) -> list[dict[str, object]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT parent_path FROM media_files WHERE source_id = ?",
                (source_id,),
            ).fetchall()

        folders: set[str] = {""}
        for row in rows:
            parent = PurePath(row["parent_path"])
            if str(parent) == ".":
                continue
            parts = parent.parts
            for index in range(1, len(parts) + 1):
                folders.add(str(PurePath(*parts[:index])))

        children: dict[str, list[str]] = {folder: [] for folder in folders}
        for folder in folders:
            if not folder:
                continue
            parent = str(PurePath(folder).parent)
            if parent == ".":
                parent = ""
            children.setdefault(parent, []).append(folder)

        def build(parent: str) -> list[dict[str, object]]:
            result = []
            for folder in sorted(children.get(parent, []), key=str.casefold):
                result.append(
                    {
                        "id": folder,
                        "label": PurePath(folder).name,
                        "children": build(folder),
                    }
                )
            return result

        return [{"id": "__root__", "label": "Корень", "children": build("")}]

    def list_files(
        self, source_id: int, folder: str = "", limit: int = 300
    ) -> list[dict[str, object]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, relative_path, parent_path, name, kind, size, modified_at
                FROM media_files
                WHERE source_id = ? AND parent_path = ?
                ORDER BY kind, name COLLATE NOCASE
                LIMIT ?
                """,
                (source_id, folder, min(max(limit, 1), 1000)),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_media(self, media_id: int) -> dict[str, object] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT media_files.*, sources.path AS source_path,
                       sources.kind AS source_kind
                FROM media_files
                JOIN sources ON sources.id = media_files.source_id
                WHERE media_files.id = ?
                """,
                (media_id,),
            ).fetchone()
        return dict(row) if row else None

    def resolve_media_file(self, media_id: int) -> Path:
        media = self.get_media(media_id)
        if media is None:
            raise KeyError(media_id)
        if media.get("source_kind") != "folder":
            raise PermissionError("У виртуального источника нет прямого пути к оригиналу")

        source = Path(str(media["source_path"])).resolve(strict=True)
        candidate = source / str(media["relative_path"])
        if candidate.is_symlink():
            raise PermissionError("Символические ссылки не открываются")
        original = candidate.resolve(strict=True)
        if not original.is_relative_to(source):
            raise PermissionError("Файл находится вне выбранного источника")
        if not original.is_file():
            raise FileNotFoundError(original)
        return original
