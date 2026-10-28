"""Remembered volumes and directory snapshots. Originals are only opened read-only."""
from __future__ import annotations

import hashlib
import json
import os
import plistlib
import re
import sqlite3
import stat
import subprocess
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import quote, urlsplit


PURPOSES = {"": "Не назначено", "media": "Медиа", "documents": "Документы", "projects": "Проекты", "mixed": "Разные данные"}
ROLES = {"": "Не назначено", "primary": "Основное хранение", "copy": "Вторая копия", "archive": "Архив", "temporary": "Временное"}
FLAGS = {"no_duplicate": "Не дублировать", "planned_move": "Планируется перенос"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relative_path(value: str) -> str:
    if "\x00" in value or value.startswith("/") or ".." in value.split("/"):
        raise ValueError("Нужен путь внутри выбранного тома")
    path = str(PurePosixPath(value))
    return "" if path == "." else path


def volume_key(identity: str) -> str:
    return hashlib.sha256(identity.encode()).hexdigest()[:24]


def discover_volumes() -> list[dict[str, Any]]:
    """Use mount identity, never just a mount-point name. No mounting or automounting."""
    result = subprocess.run(["/sbin/mount"], capture_output=True, text=True, timeout=8, check=True)
    volumes = []
    for line in result.stdout.splitlines():
        match = re.match(r"^(.*?) on (.*?) \((.*?)\)$", line)
        if not match:
            continue
        device, mount_path, options = match.groups()
        mount_path = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), mount_path)
        parts = options.split(", ")
        if mount_path != "/System/Volumes/Data" and not (
            mount_path.startswith("/Volumes/") and "nobrowse" not in parts
        ):
            continue
        filesystem = parts[0]
        network = filesystem in {"smbfs", "nfs", "afpfs", "webdav"}
        name = Path(mount_path).name
        server_host = None
        if network:
            # Do not retain credentials or account names from mount output.
            endpoint = device.removeprefix("//").split("@", 1)[-1]
            server_host = endpoint.split("/", 1)[0].rstrip(":")
            identity = f"{filesystem}:{endpoint.casefold()}"
            kind = "network"
        else:
            info_result = subprocess.run(
                ["/usr/sbin/diskutil", "info", "-plist", mount_path],
                capture_output=True, timeout=5, check=True,
            )
            info = plistlib.loads(info_result.stdout)
            identifier = info.get("VolumeUUID")
            if not identifier:
                # An unstable device identifier must not inherit another disk's roles.
                continue
            identity = f"volume:{identifier}"
            name = info.get("VolumeName") or name
            kind = "internal" if info.get("Internal") else "external"
        volumes.append({"id": volume_key(identity), "name": name, "mount_path": mount_path, "kind": kind, "server_host": server_host, "device": os.stat(mount_path, follow_symlinks=False).st_dev})
    return volumes


class StorageCatalog:
    def __init__(self, database: Path, discover: Callable = discover_volumes) -> None:
        self.database = database
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.discover = discover
        self._lock = threading.RLock()
        self._mounted: dict[str, dict] = {}
        self._checked = 0.0
        self._discovery_error: str | None = None
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS volumes (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, mount_path TEXT NOT NULL,
                    kind TEXT NOT NULL, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS directories (
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, scanned_at TEXT NOT NULL,
                    entries TEXT NOT NULL, PRIMARY KEY(volume_id, path)
                );
                CREATE TABLE IF NOT EXISTS annotations (
                    volume_id TEXT NOT NULL, path TEXT NOT NULL, purpose TEXT, role TEXT,
                    no_duplicate INTEGER, planned_move INTEGER, comment TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY(volume_id, path)
                );
            """)
            db.execute('CREATE TABLE IF NOT EXISTS network_volume_links (volume_id TEXT PRIMARY KEY, url TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS volume_aliases (alias_id TEXT PRIMARY KEY, volume_id TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS volume_origins (volume_id TEXT PRIMARY KEY, host TEXT NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=30)
        try:
            db.row_factory = sqlite3.Row
            with db:
                yield db
        finally:
            db.close()

    def refresh(self, force: bool = False) -> dict:
        with self._lock:
            if force or time.monotonic() - self._checked > 10:
                try:
                    discovered = self.discover()
                    timestamp = now()
                    with self.connect() as db:
                        for volume in discovered:
                            alias = db.execute('SELECT volume_id FROM volume_aliases WHERE alias_id=?', (volume['id'],)).fetchone()
                            if alias:
                                volume['id'] = alias['volume_id']
                            db.execute("""
                                INSERT INTO volumes (id,name,mount_path,kind,first_seen,last_seen) VALUES (?, ?, ?, ?, ?, ?)
                                ON CONFLICT(id) DO UPDATE SET name=excluded.name,
                                  mount_path=excluded.mount_path, kind=excluded.kind, last_seen=excluded.last_seen
                            """, (volume["id"], volume["name"], volume["mount_path"], volume["kind"], timestamp, timestamp))
                            if volume.get('server_host'):
                                db.execute('INSERT OR REPLACE INTO volume_origins VALUES (?,?)', (volume['id'], volume['server_host']))
                    self._mounted = {v["id"]: v for v in discovered}
                    self._discovery_error = None
                except (OSError, ValueError, subprocess.SubprocessError) as error:
                    # A failed discovery is unknown availability, not mass disconnection.
                    self._discovery_error = str(error)
                self._checked = time.monotonic()
            with self.connect() as db:
                rows = [dict(row) for row in db.execute("SELECT v.*, l.url AS network_url FROM volumes v LEFT JOIN network_volume_links l ON l.volume_id=v.id ORDER BY v.name COLLATE NOCASE")]
                origins = {r['volume_id']: r['host'] for r in db.execute('SELECT * FROM volume_origins')}
                servers = []
                if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='network_servers'").fetchone():
                    servers = [dict(r) for r in db.execute('SELECT id,name,host,aliases FROM network_servers')]
            for row in rows:
                row['group'] = self.volume_group(row, origins.get(row['id']), servers)
                row["availability"] = "unknown" if self._discovery_error else ("online" if row["id"] in self._mounted else "offline")
                row["device"] = self._mounted.get(row["id"], {}).get("device")
                row["metadata"] = self.metadata(row["id"], "")
            return {"volumes": rows, "error": self._discovery_error, "checked_at": now(), "purposes": PURPOSES, "roles": ROLES}

    @staticmethod
    def volume_group(volume: dict, origin: str | None, servers: list[dict]) -> dict:
        if volume['kind'] != 'network':
            return {'id': 'm4', 'name': 'M4', 'kind': 'local'}
        host = urlsplit(volume.get('network_url') or '').hostname or origin
        if not host:
            # Old offline entries have no mount origin. Match only by identity,
            # never by a share name which might exist on several NAS devices.
            for server in servers:
                if volume['id'] in StorageCatalog.network_keys(json.loads(server['aliases']), volume['name']):
                    host = server['host']
                    break
        if not host:
            return {'id': 'network-unknown', 'name': 'Сетевые тома', 'kind': 'network'}
        normalized = host.rstrip('.').casefold()
        for server in servers:
            aliases = {a.rstrip('.').casefold() for a in json.loads(server['aliases'])}
            if normalized in aliases or normalized == server['host'].rstrip('.').casefold():
                return {'id': 'nas:' + server['host'].rstrip('.').casefold(), 'name': server['name'], 'kind': 'network'}
        name = host.rstrip('.')
        suffix = '._smb._tcp.local'
        if normalized.endswith(suffix):
            name = name[:-len(suffix)]
            normalized = name.casefold() + '.local'
        elif normalized.endswith('.local'):
            name = name[:-len('.local')]
        return {'id': 'nas:' + normalized, 'name': name, 'kind': 'network'}

    @staticmethod
    def network_keys(hosts: list[str], share: str) -> list[str]:
        return list(dict.fromkeys(volume_key(f"smbfs:{host.rstrip('.').casefold()}/{name.casefold()}")
                                  for host in hosts for name in (share, quote(share, safe=''))))

    def find_network_volume(self, hosts: list[str], share: str) -> dict | None:
        with self.connect() as db:
            for candidate in self.network_keys(hosts, share):
                alias = db.execute('SELECT volume_id FROM volume_aliases WHERE alias_id=?', (candidate,)).fetchone()
                row = db.execute('SELECT * FROM volumes WHERE id=?', (alias['volume_id'] if alias else candidate,)).fetchone()
                if row:
                    return dict(row)
        return None

    def remember_network_volume(self, host: str, aliases: list[str], share: str) -> dict:
        with self._lock:
            hosts = list(dict.fromkeys([host, *aliases]))
            existing = self.find_network_volume(hosts, share)
            keys = self.network_keys(hosts, share)
            volume_id = existing['id'] if existing else keys[0]
            url = f"smb://{host}/{quote(share, safe='')}"
            timestamp = now()
            with self.connect() as db:
                db.execute("""
                    INSERT INTO volumes (id,name,mount_path,kind,first_seen,last_seen)
                    VALUES (?,?,'','network',?,?) ON CONFLICT(id) DO NOTHING
                """, (volume_id, share, timestamp, timestamp))
                db.execute('INSERT OR REPLACE INTO network_volume_links VALUES (?,?)', (volume_id, url))
                for key in keys:
                    # Existing independent records are not merged or overwritten.
                    collision = db.execute('SELECT id FROM volumes WHERE id=? AND id!=?', (key, volume_id)).fetchone()
                    if not collision:
                        db.execute('INSERT OR IGNORE INTO volume_aliases VALUES (?,?)', (key, volume_id))
            return self.get_volume(volume_id)

    def get_volume(self, volume_id: str) -> dict:
        with self.connect() as db:
            row = db.execute("SELECT v.*, l.url AS network_url FROM volumes v LEFT JOIN network_volume_links l ON l.volume_id=v.id WHERE v.id=?", (volume_id,)).fetchone()
        if row is None:
            raise KeyError("Том не найден")
        return dict(row)

    def metadata(self, volume_id: str, path: str) -> dict:
        path = relative_path(path)
        self.get_volume(volume_id)
        with self.connect() as db:
            annotations = {r["path"]: dict(r) for r in db.execute("SELECT * FROM annotations WHERE volume_id=?", (volume_id,))}
        return self._metadata(path, annotations)

    @staticmethod
    def _metadata(path: str, annotations: dict) -> dict:
        ancestors = [path]
        while ancestors[-1]:
            ancestors.append(relative_path(str(PurePosixPath(ancestors[-1]).parent)))
        own = annotations.get(path, {})
        effective = {}
        inherited_from = {}
        for field in ("purpose", "role", *FLAGS):
            effective[field] = False if field in FLAGS else ""
            for ancestor in ancestors:
                value = annotations.get(ancestor, {}).get(field)
                if value is not None:
                    effective[field] = bool(value) if field in FLAGS else value
                    inherited_from[field] = ancestor if ancestor != path else None
                    break
        return {"own": {key: own.get(key) for key in ("purpose", "role", *FLAGS, "comment")}, "effective": effective, "inherited_from": inherited_from}

    def annotate(self, volume_id: str, path: str, values: dict) -> dict:
        path = relative_path(path)
        self.get_volume(volume_id)
        if values.get("purpose") is not None and values["purpose"] not in PURPOSES:
            raise ValueError("Неизвестное назначение")
        if values.get("role") is not None and values["role"] not in ROLES:
            raise ValueError("Неизвестная роль")
        with self.connect() as db:
            if path:
                parent = relative_path(str(PurePosixPath(path).parent))
                snapshot = self._snapshot(db, volume_id, parent)
                if not any(e["path"] == path and e["kind"] == "directory" for e in snapshot.get("entries", [])):
                    raise ValueError("Роли можно назначать только известным каталогам")
            db.execute("""
                INSERT INTO annotations VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(volume_id,path) DO UPDATE SET purpose=excluded.purpose,
                  role=excluded.role, no_duplicate=excluded.no_duplicate,
                  planned_move=excluded.planned_move, comment=excluded.comment
            """, (volume_id, path, values.get("purpose"), values.get("role"), values.get("no_duplicate"), values.get("planned_move"), values.get("comment", "")))
        return self.metadata(volume_id, path)

    @staticmethod
    def _snapshot(db, volume_id: str, path: str) -> dict:
        import json
        row = db.execute("SELECT * FROM directories WHERE volume_id=? AND path=?", (volume_id, path)).fetchone()
        return {"entries": json.loads(row["entries"]), "scanned_at": row["scanned_at"]} if row else {"entries": [], "scanned_at": None}

    def directory(self, volume_id: str, path: str = "", refresh: bool = True) -> dict:
        import json
        path = relative_path(path)
        volumes = self.refresh(force=refresh)
        volume = next((v for v in volumes["volumes"] if v["id"] == volume_id), None)
        if volume is None:
            raise KeyError("Том не найден")
        with self.connect() as db:
            snapshot = self._snapshot(db, volume_id, path)
        cached = True
        error = None
        if refresh and volume["availability"] == "online":
            try:
                entries = self._read_directory(volume, path)
                snapshot = {"entries": entries, "scanned_at": now()}
                with self.connect() as db:
                    db.execute("INSERT OR REPLACE INTO directories VALUES (?, ?, ?, ?)", (volume_id, path, snapshot["scanned_at"], json.dumps(entries, ensure_ascii=False)))
                cached = False
            except OSError as failure:
                error = f"Не удалось прочитать папку: {failure.strerror or str(failure)}"
        with self.connect() as db:
            annotations = {r["path"]: dict(r) for r in db.execute("SELECT * FROM annotations WHERE volume_id=?", (volume_id,))}
        for entry in snapshot["entries"]:
            entry["metadata"] = self._metadata(entry["path"], annotations)
        return {**snapshot, "path": path, "volume": volume, "cached": cached, "error": error, "metadata": self.metadata(volume_id, path)}

    @staticmethod
    def _read_directory(volume: dict, path: str) -> list[dict]:
        """Read through directory descriptors: no symlinks, no crossing into another volume."""
        descriptors = []
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            descriptor = os.open(volume["mount_path"], flags)
            descriptors.append(descriptor)
            device = os.fstat(descriptor).st_dev
            if volume.get("device") is not None and device != volume["device"]:
                raise OSError("Том был отключён или заменён во время чтения")
            for part in PurePosixPath(path).parts:
                descriptor = os.open(part, flags, dir_fd=descriptor)
                descriptors.append(descriptor)
                if os.fstat(descriptor).st_dev != device:
                    raise OSError("Каталог относится к другому тому")
            entries = []
            with os.scandir(descriptor) as iterator:
                for item in iterator:
                    kind = "symlink" if item.is_symlink() else "directory" if item.is_dir(follow_symlinks=False) else "file"
                    entry = {"name": item.name, "path": f"{path}/{item.name}".lstrip("/"), "kind": kind, "size": None, "modified_at": None}
                    try:
                        info = item.stat(follow_symlinks=False)
                        entry.update(size=info.st_size if stat.S_ISREG(info.st_mode) else None, modified_at=datetime.fromtimestamp(info.st_mtime, timezone.utc).isoformat())
                        if info.st_dev != device:
                            entry["kind"] = "mount"
                    except OSError as failure:
                        entry["error"] = str(failure)
                    entries.append(entry)
            return sorted(entries, key=lambda e: (e["kind"] != "directory", e["name"].casefold()))
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)
