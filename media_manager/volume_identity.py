"""Small volume markers; writing requires explicit registration or renaming."""
from __future__ import annotations

import json
import os
import re
import stat
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone


MARKER_NAME = '.media-actu-volume.json'
MARKER_FILES = frozenset((MARKER_NAME, '._' + MARKER_NAME))
FOLDER_MARKER_NAME = '.media-actu-folder.json'
FOLDER_MARKER_FILES = frozenset((FOLDER_MARKER_NAME, '._' + FOLDER_MARKER_NAME))
MARKER_LIMIT = 4096
COPY_TEMP_PATTERN = re.compile(r'\.media-actu-copy-[a-f0-9]{32}-[a-f0-9]{32}\.part\Z')


def copy_temporary(name: str) -> bool:
    return bool(COPY_TEMP_PATTERN.fullmatch(name))


def service_file(name: str, *, volume_root: bool = False) -> bool:
    return copy_temporary(name) or name in FOLDER_MARKER_FILES or (volume_root and name in MARKER_FILES)


def usb_share(name: str) -> bool:
    return bool(re.fullmatch(r'usbshare\d+(?:[-_].*)?', name, re.IGNORECASE))


def canonical_host(host: str) -> str:
    host = host.rstrip('.').casefold()
    suffix = '._smb._tcp.local'
    if host.endswith(suffix):
        host = host[:-len(suffix)].removesuffix('(smb)') + '.local'
    return host


@contextmanager
def mounted_root(path: str, device: int | None = None):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if device is not None and os.fstat(descriptor).st_dev != device:
            raise OSError('Том был отключён или заменён')
        yield descriptor
    finally:
        os.close(descriptor)


def _read_marker_document(root: int) -> dict | None:
    try:
        descriptor = os.open(MARKER_NAME, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_dev != os.fstat(root).st_dev or info.st_size > MARKER_LIMIT:
            raise OSError('Некорректный служебный файл носителя')
        with os.fdopen(descriptor, 'rb', closefd=False) as stream:
            raw = stream.read(MARKER_LIMIT + 1)
        if len(raw) > MARKER_LIMIT:
            raise OSError('Служебный файл носителя слишком большой')
        try:
            marker = json.loads(raw)
            if not isinstance(marker, dict) or type(marker.get('version')) is not int or marker['version'] != 1:
                raise ValueError('version')
            identifier = str(uuid.UUID(marker['id']))
            if uuid.UUID(identifier).int == 0:
                raise ValueError('empty UUID')
            name = marker['name']
            validate_name(name)
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            raise OSError('Не удалось подтвердить ID в служебном файле носителя') from error
        return marker
    finally:
        os.close(descriptor)


def read_marker(root: int) -> dict | None:
    marker = _read_marker_document(root)
    return {'id': str(uuid.UUID(marker['id'])), 'name': marker['name'].strip()} if marker else None


def validate_name(name: str) -> None:
    if not isinstance(name, str) or not name.strip() or len(name) > 120 or any(ord(c) < 32 for c in name):
        raise ValueError('Нужно имя носителя длиной от 1 до 120 символов без управляющих знаков')


def verify_identity(root: int, volume: dict) -> None:
    if volume.get('identity_status') in {'unverified', 'legacy'}:
        raise OSError('Носитель не подтверждён. Сначала зарегистрируй сменный диск.')
    if volume.get('marker_id'):
        marker = read_marker(root)
        if marker is None or marker['id'] != volume['marker_id']:
            raise OSError('Сменный диск был отключён или заменён')


def create_marker(path: str, device: int | None, name: str) -> dict:
    validate_name(name)
    marker = {'version': 1, 'id': str(uuid.uuid4()), 'name': name.strip(),
              'created_at': datetime.now(timezone.utc).isoformat()}
    content = (json.dumps(marker, ensure_ascii=False, indent=2) + '\n').encode()
    with mounted_root(path, device) as root:
        # Exclusive creation also prevents replacing a marker made by another client.
        descriptor = os.open(MARKER_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o644, dir_fd=root)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        confirmed = read_marker(root)
        if confirmed is None or confirmed['id'] != marker['id']:
            raise OSError('Диск изменился во время регистрации')
    return marker


def rename_marker(path: str, device: int | None, marker_id: str, name: str) -> dict:
    validate_name(name)
    with mounted_root(path, device) as root:
        original = _read_marker_document(root)
        if original is None or str(uuid.UUID(original['id'])) != marker_id:
            raise OSError('Сменный диск был отключён или заменён')
        updated = {**original, 'name': name.strip()}
        content = (json.dumps(updated, ensure_ascii=False, indent=2) + '\n').encode()
        if len(content) > MARKER_LIMIT:
            raise ValueError('Новое имя не помещается в служебный файл носителя')
        # Reuse the app's protected, excluded temporary-file namespace. Publish
        # only a complete JSON document so a failed write cannot destroy the ID.
        temporary = f'.media-actu-copy-{uuid.uuid4().hex}-{uuid.uuid4().hex}.part'
        mode = stat.S_IMODE(os.stat(MARKER_NAME, dir_fd=root, follow_symlinks=False).st_mode) & 0o777
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             mode, dir_fd=root)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            if _read_marker_document(root) != original:
                raise OSError('Служебный файл диска изменился во время переименования')
            os.replace(temporary, MARKER_NAME, src_dir_fd=root, dst_dir_fd=root)
        finally:
            try:
                os.unlink(temporary, dir_fd=root)
            except FileNotFoundError:
                pass
        confirmed = read_marker(root)
        if confirmed != {'id': marker_id, 'name': updated['name']}:
            raise OSError('Не удалось подтвердить новое имя диска')
        return confirmed


def read_capacity(root: int) -> dict:
    info = os.fstatvfs(root)
    block = info.f_frsize or info.f_bsize
    total = info.f_blocks * block
    free = info.f_bfree * block
    available = info.f_bavail * block
    if total <= 0 or not 0 <= available <= free <= total:
        raise OSError('Том не сообщил корректные сведения о свободном месте')
    return {'total_bytes': total, 'used_bytes': total - free, 'free_bytes': free,
            'available_bytes': available, 'checked_at': datetime.now(timezone.utc).isoformat()}
