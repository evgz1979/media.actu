from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from media_manager.catalog import Catalog


register_heif_opener()


class ThumbnailService:
    def __init__(self, catalog: Catalog, cache_directory: str | Path) -> None:
        self.catalog = catalog
        self.cache_directory = Path(cache_directory)
        self.cache_directory.mkdir(parents=True, exist_ok=True)

    def get_or_create(self, media_id: int) -> Path | None:
        media = self.catalog.get_media(media_id)
        if not media or media["kind"] != "photo":
            return None

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
        target = self.cache_directory / f"{media_id}-{fingerprint}.jpg"
        if target.exists():
            return target

        for stale in self.cache_directory.glob(f"{media_id}-*.jpg"):
            stale.unlink(missing_ok=True)

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
