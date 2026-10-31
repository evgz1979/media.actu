"""On-demand, cached derivatives of files outside the media index."""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import uuid

from PIL import Image, ImageOps

from .comparison import open_readonly
from .scanner import media_kind
from .storage import relative_path
from .thumbnails import ThumbnailCacheUnavailable


class StoragePreviewService:
    def __init__(self, storage, cache_directory):
        self.storage = storage
        self.cache_directory = Path(cache_directory)
        self._slots = threading.Semaphore(2)
        self._native_lock = threading.Lock()

    def get_or_create(self, volume_id, path, *, large=False):
        path = relative_path(path)
        kind = media_kind(Path(path))
        if not kind:
            raise ValueError('Для этого типа файла доступна только информация о файле')
        # Use the mounted identity already maintained by discovery. Reading each
        # visible tile must not rediscover all disks or trust an old mount path.
        volume = next((v for v in self.storage.refresh(cached_only=True)['volumes'] if v['id'] == volume_id), None)
        if volume is None:
            raise KeyError('Том не найден')
        if volume['availability'] != 'online':
            raise OSError(volume.get('identity_error') or 'Том отключён или недоступен')
        with self._slots, open_readonly(volume, path) as descriptor:
            before = os.fstat(descriptor)
            fingerprint = hashlib.sha256(
                f'{volume_id}\0{path}\0{before.st_dev}\0{before.st_ino}\0{before.st_size}\0{before.st_mtime_ns}\0{before.st_ctime_ns}\0{large}'.encode()
            ).hexdigest()
            parts = self.cache_directory.parts
            if len(parts) >= 3 and parts[:2] == ('/', 'Volumes') and not Path('/Volumes', parts[2]).is_dir():
                raise ThumbnailCacheUnavailable('Том кэша превью не подключён')
            directory = self.cache_directory / 'storage' / fingerprint[:2] / fingerprint[2:4]
            target = directory / (fingerprint + '.jpg')
            if target.is_file():
                return target
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as error:
                raise ThumbnailCacheUnavailable('Кэш превью недоступен') from error
            if kind == 'video':
                image = self._video_frame(descriptor, large, Path(path).suffix[1:].lower())
            else:
                with os.fdopen(os.dup(descriptor), 'rb') as source, Image.open(source) as original:
                    image = ImageOps.exif_transpose(original)
                    image.thumbnail((1600, 1200) if large else (320, 240), Image.Resampling.LANCZOS)
                    image = image.copy()
            with image:
                if image.mode != 'RGB':
                    background = Image.new('RGB', image.size, 'white')
                    background.paste(image, mask=image.getchannel('A') if 'A' in image.getbands() else None)
                    image = background
                encoded = io.BytesIO()
                image.save(encoded, 'JPEG', quality=86 if large else 80)
            after = os.fstat(descriptor)
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise OSError('Файл изменился во время создания превью. Выбери его ещё раз.')
            # open_readonly rechecks removable identity before this exits.
        temporary = directory / (uuid.uuid4().hex + '.tmp')
        try:
            temporary.write_bytes(encoded.getvalue())
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def _native_video_command(self, descriptor, width, height, extension):
        if sys.platform != 'darwin':
            raise ValueError('Для превью видео нужен FFmpeg')
        source = Path(__file__).with_name('video_frame.m')
        version = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
        directory = self.cache_directory / 'native'
        target = directory / ('video-frame-' + version)
        with self._native_lock:
            if not target.is_file():
                directory.mkdir(parents=True, exist_ok=True)
                temporary = directory / (uuid.uuid4().hex + '.tmp')
                try:
                    subprocess.run(['/usr/bin/xcrun', 'clang', '-O2', '-fobjc-arc', '-Wno-deprecated-declarations',
                                    '-framework', 'Foundation', '-framework', 'AVFoundation', '-framework', 'ImageIO',
                                    '-framework', 'CoreMedia', '-framework', 'CoreGraphics', '-framework', 'UniformTypeIdentifiers',
                                    str(source), '-o', str(temporary)],
                                   capture_output=True, timeout=90, check=True)
                    temporary.replace(target)
                finally:
                    temporary.unlink(missing_ok=True)
        return [str(target), str(descriptor), str(width), str(height), extension]

    def _video_frame(self, descriptor, large, extension):
        ffmpeg = shutil.which('ffmpeg')
        width, height = (1600, 1200) if large else (320, 240)
        try:
            command = ([ffmpeg, '-nostdin', '-v', 'error', '-threads', '1', '-protocol_whitelist', 'file,pipe',
                 '-i', f'/dev/fd/{descriptor}', '-frames:v', '1', '-an',
                 '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease',
                 '-f', 'image2pipe', '-c:v', 'mjpeg', 'pipe:1'] if ffmpeg else self._native_video_command(descriptor, width, height, extension))
            result = subprocess.run(command, pass_fds=(descriptor,), capture_output=True, timeout=25, check=True)
            with Image.open(io.BytesIO(result.stdout)) as frame:
                return frame.copy()
        except (subprocess.SubprocessError, OSError) as error:
            raise ValueError('Не удалось получить кадр видео') from error
