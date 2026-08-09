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

INSERT OR IGNORE INTO metadata(key, value) VALUES ('catalog_revision', '0');
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
                   COALESCE(SUM(media_files.size), 0) AS total_size
            FROM sources
            LEFT JOIN media_files ON media_files.source_id = sources.id
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
            error_text = "\n".join(error.message for error in report.errors[:20]) or None
            status = "warning" if report.errors else "idle"
            connection.execute(
                """
                UPDATE sources
                SET last_scan_at = ?, status = ?, error = ?
                WHERE id = ?
                """,
                (now, status, error_text, source_id),
            )
            connection.execute(
                """
                UPDATE metadata
                SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT)
                WHERE key = 'catalog_revision'
                """
            )

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
                SELECT media_files.*, sources.path AS source_path
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
