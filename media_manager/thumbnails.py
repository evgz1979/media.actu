from __future__ import annotations

import hashlib
import threading
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from media_manager.catalog import Catalog
from media_manager.photos_adapter import SystemPhotosAdapter


register_heif_opener()


class ThumbnailCacheUnavailable(RuntimeError):
    pass


class ThumbnailService:
    def __init__(
        self,
        catalog: Catalog,
        cache_directory: str | Path,
        photos_adapter: SystemPhotosAdapter | None = None,
    ) -> None:
        self.catalog = catalog
        self.cache_directory = Path(cache_directory)
        self.photos_adapter = photos_adapter
        self._folder_slots = threading.Semaphore(2)
        self._photos_slots = threading.Semaphore(1)
        self._locks_guard = threading.Lock()
        self._media_locks: dict[int, threading.Lock] = {}

    def get_or_create(self, media_id: int) -> Path | None:
        with self._locks_guard:
            media_lock = self._media_locks.setdefault(media_id, threading.Lock())
        with media_lock:
            return self._get_or_create(media_id)

    def get_cached(self, media_id: int) -> Path | None:
        media = self.catalog.get_media(media_id)
        if not media or media["kind"] != "photo":
            return None
        if media.get("source_kind") == "photos":
            fingerprint = hashlib.sha256(
                f"{media['relative_path']}\0{media['modified_at']}".encode()
            ).hexdigest()[:20]
        else:
            source = Path(str(media["source_path"])).resolve(strict=True)
            candidate = source / str(media["relative_path"])
            if candidate.is_symlink():
                return None
            original = candidate.resolve(strict=True)
            if not original.is_relative_to(source):
                return None
            stat = original.stat()
            fingerprint = hashlib.sha256(
                f"{original}\0{stat.st_size}\0{stat.st_mtime_ns}".encode()
            ).hexdigest()[:20]
        target = self._cache_target(media_id, fingerprint)
        return target if target.is_file() else None

    def _cache_target(self, media_id: int, fingerprint: str) -> Path:
        parts = self.cache_directory.parts
        if len(parts) >= 3 and parts[:2] == ("/", "Volumes"):
            volume = Path("/Volumes") / parts[2]
            if not volume.is_dir():
                raise ThumbnailCacheUnavailable(
                    f"Том кэша превью не подключён: {volume}"
                )
        directory = self.cache_directory / fingerprint[:2] / fingerprint[2:4]
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ThumbnailCacheUnavailable(
                f"Кэш превью недоступен: {self.cache_directory}"
            ) from error
        return directory / f"{media_id}-{fingerprint}.jpg"

    def _get_or_create(self, media_id: int) -> Path | None:
        media = self.catalog.get_media(media_id)
        if not media or media["kind"] != "photo":
            return None

        if media.get("source_kind") == "photos":
            if self.photos_adapter is None:
                return None
            fingerprint = hashlib.sha256(
                f"{media['relative_path']}\0{media['modified_at']}".encode()
            ).hexdigest()[:20]
            target = self._cache_target(media_id, fingerprint)
            if target.exists():
                return target
            with self._photos_slots:
                if target.exists():
                    return target
                return self.photos_adapter.create_thumbnail(
                    str(media["relative_path"]), target
                )

        source = Path(str(media["source_path"])).resolve(strict=True)
        candidate = source / str(media["relative_path"])
        if candidate.is_symlink():
            return None
        original = candidate.resolve(strict=True)
        if not original.is_relative_to(source):
            return None

        stat = original.stat()
        fingerprint = hashlib.sha256(
            f"{original}\0{stat.st_size}\0{stat.st_mtime_ns}".encode()
        ).hexdigest()[:20]
        target = self._cache_target(media_id, fingerprint)
        if target.exists():
            return target

        with self._folder_slots:
            if target.exists():
                return target
            with Image.open(original) as image:
                image = ImageOps.exif_transpose(image)
                image.thumbnail((640, 480), Image.Resampling.LANCZOS)
                if image.mode != "RGB":
                    background = Image.new("RGB", image.size, "white")
                    if "A" in image.getbands():
                        background.paste(image, mask=image.getchannel("A"))
                    else:
                        background.paste(image)
                    image = background
                image.save(target, "JPEG", quality=82, optimize=True)
        return target
