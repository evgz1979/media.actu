"""Remembered volumes and directory snapshots. Originals are only opened read-only."""
from __future__ import annotations

import hashlib
import errno
import json
import os
import plistlib
import re
import sqlite3
import stat
import subprocess
import threading
import time
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import quote, unquote, urlsplit

from .copies import COPY_SCHEMA, inherited_location
from .volume_identity import (
    canonical_host, create_marker, mounted_root, read_capacity,
    read_marker, rename_marker, service_file, usb_share, verify_identity,
)


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
        try:
            volume = _inspect_volume(device, mount_path, parts[0])
        except (OSError, ValueError, subprocess.SubprocessError):
            # A removed SMB share can leave an unreadable mount behind. Its saved
            # record becomes offline; discovery must still inspect the other mounts.
            continue
        if volume is not None:
            volumes.append(volume)
    return volumes


def _inspect_volume(device: str, mount_path: str, filesystem: str) -> dict[str, Any] | None:
    network = filesystem in {"smbfs", "nfs", "afpfs", "webdav"}
    name = Path(mount_path).name
    server_host = None
    share_name = None
    marker = None
    identity_error = None
    if network:
        # Do not retain credentials or account names from mount output.
        endpoint = device.removeprefix("//").split("@", 1)[-1]
        server_host = endpoint.split("/", 1)[0].rstrip(":")
        share_name = unquote(endpoint.split('/', 1)[-1])
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
            return None
        identity = f"volume:{identifier}"
        name = info.get("VolumeName") or name
        kind = "internal" if info.get("Internal") else "external"
    device_number = os.stat(mount_path, follow_symlinks=False).st_dev
    removable = kind == 'external' or (network and usb_share(share_name))
    capacity = None
    capacity_error = None
    with mounted_root(mount_path, device_number) as root:
        if kind != 'internal':
            try:
                marker = read_marker(root)
            except OSError:
                identity_error = 'Служебный файл носителя недоступен или повреждён'
        try:
            capacity = read_capacity(root)
        except OSError:
            capacity_error = 'Не удалось обновить сведения о месте на томе'
        if marker:
            try:
                if read_marker(root) != marker:
                    raise OSError('identity changed')
            except OSError:
                marker = None
                identity_error = 'Диск изменился во время определения носителя'
    status = 'resource' if network else 'verified'
    if marker:
        identity = 'media-actu:' + marker['id']
        name = marker['name']
        removable, status = True, 'verified'
    elif network and (removable or identity_error):
        identity = 'unverified:' + canonical_host(server_host) + '/' + share_name.casefold()
        name = 'Сменный диск · ' + share_name
        removable, status = True, 'unverified'
        identity_error = identity_error or 'Носитель не подтверждён. Зарегистрируй подключённый диск.'
    elif identity_error:
        # A damaged marker must not silently fall back to a different identity.
        identity = 'unverified:' + identity
        status = 'unverified'
    volume = {"id": volume_key(identity), "name": name, "mount_path": mount_path,
              "kind": kind, "server_host": server_host, "device": device_number,
              "removable": bool(removable), "identity_status": status,
              "marker_id": marker['id'] if marker else None, "share_name": share_name,
              "identity_error": identity_error, "capacity": capacity, "capacity_error": capacity_error}
    if network:
        volume['network_url'] = f'smb://{server_host}/{quote(share_name, safe="")}'
    return volume


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
            db.execute('''CREATE TABLE IF NOT EXISTS volume_details (
                volume_id TEXT PRIMARY KEY, removable INTEGER NOT NULL, identity_status TEXT NOT NULL,
                marker_id TEXT, share_name TEXT, identity_error TEXT)''')
            db.execute('''CREATE TABLE IF NOT EXISTS volume_capacity (
                volume_id TEXT PRIMARY KEY, total_bytes INTEGER NOT NULL, used_bytes INTEGER NOT NULL,
                free_bytes INTEGER NOT NULL, available_bytes INTEGER NOT NULL, checked_at TEXT NOT NULL)''')
            db.executescript(COPY_SCHEMA)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=30)
        db.execute('PRAGMA foreign_keys=ON')
        try:
            db.row_factory = sqlite3.Row
            with db:
                yield db
        finally:
            db.close()

    def refresh(self, force: bool = False, *, cached_only: bool = False) -> dict:
        # Saved lists remain readable while another thread discovers slow mounts.
        with nullcontext() if cached_only else self._lock:
            if not cached_only and (force or time.monotonic() - self._checked > 10):
                try:
                    discovered = [dict(v) for v in self.discover()]
                    duplicates = {v['id'] for v in discovered if sum(other['id'] == v['id'] for other in discovered) > 1}
                    for volume in discovered:
                        if volume['id'] in duplicates:
                            volume.update(id=volume_key('duplicate:' + volume['id'] + ':' + volume['mount_path']),
                                          identity_status='unverified',
                                          identity_error='Один ID обнаружен на нескольких томах. Носитель не подтверждён.')
                    timestamp = now()
                    with self.connect() as db:
                        for volume in discovered:
                            status = volume.get('identity_status', 'resource' if volume['kind'] == 'network' else 'verified')
                            alias = (db.execute('SELECT volume_id FROM volume_aliases WHERE alias_id=?', (volume['id'],)).fetchone()
                                     if status == 'resource' else None)
                            if alias:
                                volume['id'] = alias['volume_id']
                            db.execute("""
                                INSERT INTO volumes (id,name,mount_path,kind,first_seen,last_seen) VALUES (?, ?, ?, ?, ?, ?)
                                ON CONFLICT(id) DO UPDATE SET name=excluded.name,
                                  mount_path=excluded.mount_path, kind=excluded.kind, last_seen=excluded.last_seen
                            """, (volume["id"], volume["name"], volume["mount_path"], volume["kind"], timestamp, timestamp))
                            if volume.get('server_host'):
                                db.execute('INSERT OR REPLACE INTO volume_origins VALUES (?,?)', (volume['id'], volume['server_host']))
                            db.execute('INSERT OR REPLACE INTO volume_details VALUES (?,?,?,?,?,?)',
                                       (volume['id'], int(volume.get('removable', volume['kind'] == 'external')), status,
                                        volume.get('marker_id'), volume.get('share_name'), volume.get('identity_error')))
                            if volume.get('network_url'):
                                db.execute('INSERT OR IGNORE INTO network_volume_links VALUES (?,?)', (volume['id'], volume['network_url']))
                            if volume.get('capacity'):
                                capacity = volume['capacity']
                                db.execute('INSERT OR REPLACE INTO volume_capacity VALUES (?,?,?,?,?,?)',
                                           (volume['id'], capacity['total_bytes'], capacity['used_bytes'], capacity['free_bytes'],
                                            capacity['available_bytes'], capacity['checked_at']))
                    self._mounted = {v["id"]: v for v in discovered}
                    self._discovery_error = None
                except (OSError, ValueError, subprocess.SubprocessError) as error:
                    # A failed discovery is unknown availability, not mass disconnection.
                    self._discovery_error = str(error)
                self._checked = time.monotonic()
            with self.connect() as db:
                rows = [dict(row) for row in db.execute("SELECT v.*, l.url AS network_url FROM volumes v LEFT JOIN network_volume_links l ON l.volume_id=v.id ORDER BY v.name COLLATE NOCASE")]
                origins = {r['volume_id']: r['host'] for r in db.execute('SELECT * FROM volume_origins')}
                details = {r['volume_id']: dict(r) for r in db.execute('SELECT * FROM volume_details')}
                capacities = {r['volume_id']: dict(r) for r in db.execute('SELECT * FROM volume_capacity')}
                servers = []
                if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='network_servers'").fetchone():
                    servers = [dict(r) for r in db.execute('SELECT id,name,host,aliases FROM network_servers')]
            for row in rows:
                row.update(self._volume_details(row, details.get(row['id'])))
                row['group'] = self.volume_group(row, origins.get(row['id']), servers)
                row["availability"] = "unknown" if self._discovery_error else ("online" if row["id"] in self._mounted else "offline")
                if row['id'] in self._mounted and row['identity_status'] == 'unverified':
                    row['availability'] = 'unknown'
                mounted = self._mounted.get(row['id'], {})
                row['mounted'] = bool(mounted) and not self._discovery_error
                row["device"] = self._mounted.get(row["id"], {}).get("device")
                row['capacity'] = capacities.get(row['id'])
                row['capacity_cached'] = bool(row['capacity']) and (bool(self._discovery_error) or not mounted.get('capacity'))
                row['capacity_error'] = mounted.get('capacity_error')
                row["metadata"] = self.metadata(row["id"], "")
            # An unconfirmed endpoint is a registration placeholder, not a remembered disk.
            rows = [row for row in rows if row['identity_status'] != 'unverified' or row['id'] in self._mounted or not row['mount_path']]
            return {"volumes": rows, "error": self._discovery_error, "checked_at": now(), "purposes": PURPOSES, "roles": ROLES}

    @staticmethod
    def _volume_details(volume: dict, details: dict | None) -> dict:
        if details:
            result = {key: details[key] for key in ('removable', 'identity_status', 'marker_id', 'share_name', 'identity_error')}
            result['removable'] = bool(result['removable'])
        else:
            legacy_usb = volume['kind'] == 'network' and usb_share(volume['name'])
            result = dict(removable=legacy_usb or volume['kind'] == 'external',
                          identity_status='legacy' if legacy_usb else 'resource' if volume['kind'] == 'network' else 'verified',
                          marker_id=None, share_name=volume['name'] if volume['kind'] == 'network' else None,
                          identity_error='Старая привязка по имени ресурса; носитель не был подтверждён' if legacy_usb else None)
        result['display_name'] = volume['name'] + (' · прежняя привязка' if result['identity_status'] == 'legacy' else '')
        return result

    def register_removable(self, volume_id: str, name: str) -> dict:
        with self._lock:
            volumes = self.refresh(True)['volumes']
            volume = next((v for v in volumes if v['id'] == volume_id), None)
            if not volume or not volume['mounted']:
                raise ValueError('Носитель отключён или заменён. Обнови список томов.')
            if volume['identity_status'] != 'unverified' or not volume['removable']:
                raise ValueError('Этот том уже определён или не является сменным носителем')
            marker = create_marker(volume['mount_path'], volume['device'], name)
            identity = volume_key('media-actu:' + marker['id'])
            registered = next((v for v in self.refresh(True)['volumes'] if v['id'] == identity), None)
            if registered is None or registered['identity_status'] != 'verified':
                raise ValueError('Файл ID создан, но подтвердить носитель не удалось. Обнови список томов.')
            return registered

    def rename_removable(self, volume_id: str, name: str) -> dict:
        with self._lock:
            volume = next((v for v in self.refresh(True)['volumes'] if v['id'] == volume_id), None)
            if not volume or not volume['mounted'] or volume['availability'] != 'online':
                raise ValueError('Диск отключён или недоступен. Подключи его и обнови список томов.')
            if volume['identity_status'] != 'verified' or not volume.get('marker_id'):
                raise ValueError('Переименовать можно только зарегистрированный сменный диск')
            marker = rename_marker(volume['mount_path'], volume['device'], volume['marker_id'], name)
            renamed = next((v for v in self.refresh(True)['volumes'] if v['id'] == volume_id), None)
            if not renamed or not renamed['mounted'] or renamed['name'] != marker['name']:
                raise ValueError('Имя записано на диск, но обновить сведения не удалось. Обнови список томов.')
            return renamed

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
        normalized = {canonical_host(host) for host in hosts}
        for mounted in self._mounted.values():
            if (mounted.get('identity_status') != 'unverified'
                    and (mounted.get('share_name') or '').casefold() == share.casefold()
                    and canonical_host(mounted.get('server_host') or '') in normalized):
                return self.get_volume(mounted['id'])
        with self.connect() as db:
            if usb_share(share):
                for host in hosts:
                    placeholder = volume_key('unverified:' + canonical_host(host) + '/' + share.casefold())
                    if db.execute('SELECT 1 FROM volumes WHERE id=?', (placeholder,)).fetchone():
                        return self.get_volume(placeholder)
                return None
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
            removable = usb_share(share)
            volume_id = existing['id'] if existing else (volume_key('unverified:' + canonical_host(host) + '/' + share.casefold()) if removable else keys[0])
            url = f"smb://{host}/{quote(share, safe='')}"
            timestamp = now()
            with self.connect() as db:
                db.execute("""
                    INSERT INTO volumes (id,name,mount_path,kind,first_seen,last_seen)
                    VALUES (?,?,'','network',?,?) ON CONFLICT(id) DO NOTHING
                """, (volume_id, share, timestamp, timestamp))
                db.execute('INSERT OR REPLACE INTO network_volume_links VALUES (?,?)', (volume_id, url))
                if removable and not existing:
                    db.execute('INSERT OR REPLACE INTO volume_details VALUES (?,?,?,?,?,?)',
                               (volume_id, 1, 'unverified', None, share, 'Носитель не подтверждён. Подключи и зарегистрируй диск.'))
                for key in ([] if removable else keys):
                    # Existing independent records are not merged or overwritten.
                    collision = db.execute('SELECT id FROM volumes WHERE id=? AND id!=?', (key, volume_id)).fetchone()
                    if not collision:
                        db.execute('INSERT OR IGNORE INTO volume_aliases VALUES (?,?)', (key, volume_id))
            return self.get_volume(volume_id)

    def get_volume(self, volume_id: str) -> dict:
        with self.connect() as db:
            row = db.execute("SELECT v.*, l.url AS network_url FROM volumes v LEFT JOIN network_volume_links l ON l.volume_id=v.id WHERE v.id=?", (volume_id,)).fetchone()
            details = db.execute('SELECT * FROM volume_details WHERE volume_id=?', (volume_id,)).fetchone()
        if row is None:
            raise KeyError("Том не найден")
        volume = dict(row)
        volume.update(self._volume_details(volume, dict(details) if details else None))
        return volume

    def open_in_finder(self, volume_id: str, path: str = '') -> dict:
        path = relative_path(path)
        volume = next((v for v in self.refresh(True)['volumes'] if v['id'] == volume_id), None)
        if volume is None:
            raise KeyError('Том не найден')
        if volume['availability'] != 'online':
            raise ValueError(volume.get('identity_error') or 'Том недоступен. Подключи его и повтори.')
        parts = PurePosixPath(path).parts
        target = Path(volume['mount_path']).joinpath(*parts)
        with mounted_root(volume['mount_path'], volume.get('device')) as root:
            verify_identity(root, volume)
            descriptors = []
            parent = root
            device = os.fstat(root).st_dev
            try:
                for part in parts[:-1]:
                    parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                    descriptors.append(parent)
                    if os.fstat(parent).st_dev != device:
                        raise OSError('Переход на другой том запрещён')
                info = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False) if parts else os.fstat(root)
                # Reveal links and nested mounts themselves without following them.
                reveal = not stat.S_ISDIR(info.st_mode) or info.st_dev != device
                verify_identity(root, volume)
                try:
                    subprocess.run(
                        ['/usr/bin/open', *(['-R'] if reveal else ['-a', 'Finder']), str(target)],
                        check=True, capture_output=True, text=True, timeout=8, stdin=subprocess.DEVNULL,
                    )
                except subprocess.SubprocessError as error:
                    raise ValueError('Не удалось открыть Finder') from error
            finally:
                for descriptor in reversed(descriptors):
                    os.close(descriptor)
        return {'path': str(target)}

    def metadata(self, volume_id: str, path: str) -> dict:
        path = relative_path(path)
        self.get_volume(volume_id)
        with self.connect() as db:
            annotations = {r["path"]: dict(r) for r in db.execute("SELECT * FROM annotations WHERE volume_id=?", (volume_id,))}
            locations = [dict(r) for r in db.execute('SELECT * FROM copy_locations WHERE volume_id=?', (volume_id,))]
        return {**self._metadata(path, annotations), 'copy': inherited_location(path, locations)}

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
        volume = self.get_volume(volume_id)
        if volume['identity_status'] == 'unverified':
            raise ValueError('Сначала зарегистрируй сменный диск; отметки должны относиться к конкретному носителю')
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

    def directory(self, volume_id: str, path: str = "", refresh: bool = True, *, discover: bool = True) -> dict:
        import json
        path = relative_path(path)
        volumes = self.refresh(force=refresh and discover, cached_only=not (refresh and discover))
        volume = next((v for v in volumes["volumes"] if v["id"] == volume_id), None)
        if volume is None:
            raise KeyError("Том не найден")
        with self.connect() as db:
            snapshot = self._snapshot(db, volume_id, path)
        cached = True
        error = volume.get('identity_error')
        error_code = None
        if refresh and volume["availability"] == "online":
            try:
                entries = self._read_directory(volume, path)
                snapshot = {"entries": entries, "scanned_at": now()}
                with self.connect() as db:
                    db.execute("INSERT OR REPLACE INTO directories VALUES (?, ?, ?, ?)", (volume_id, path, snapshot["scanned_at"], json.dumps(entries, ensure_ascii=False)))
                cached = False
            except OSError as failure:
                error = f"Не удалось прочитать папку: {failure.strerror or str(failure)}"
                error_code = 'missing' if failure.errno in (errno.ENOENT, errno.ENOTDIR) else 'read_failed'
        with self.connect() as db:
            annotations = {r["path"]: dict(r) for r in db.execute("SELECT * FROM annotations WHERE volume_id=?", (volume_id,))}
            locations = [dict(r) for r in db.execute('SELECT * FROM copy_locations WHERE volume_id=?', (volume_id,))]
        for entry in snapshot["entries"]:
            entry["metadata"] = {**self._metadata(entry["path"], annotations), 'copy': inherited_location(entry['path'], locations)}
        return {**snapshot, "path": path, "volume": volume, "cached": cached, "error": error,
                "error_code": error_code, "metadata": self.metadata(volume_id, path)}

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
            verify_identity(descriptor, volume)
            for part in PurePosixPath(path).parts:
                descriptor = os.open(part, flags, dir_fd=descriptor)
                descriptors.append(descriptor)
                if os.fstat(descriptor).st_dev != device:
                    raise OSError("Каталог относится к другому тому")
            entries = []
            with os.scandir(descriptor) as iterator:
                for item in iterator:
                    if service_file(item.name,volume_root=not path):
                        continue
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
            verify_identity(descriptors[0], volume)
            return sorted(entries, key=lambda e: (e["kind"] != "directory", e["name"].casefold()))
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)
