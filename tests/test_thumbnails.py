from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from media_manager.catalog import Catalog
from media_manager.scanner import scan_sources
from media_manager.thumbnails import ThumbnailService


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ThumbnailTests(unittest.TestCase):
    def test_thumbnail_is_written_only_to_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            original = source / "photo.jpg"
            Image.new("RGB", (1200, 800), "navy").save(original)
            original_digest = digest(original)
            original_stat = original.stat()

            catalog = Catalog(root / "catalog.sqlite3")
            source_id = int(catalog.add_source(source)["id"])
            catalog.replace_source_scan(source_id, scan_sources([source]))
            media_id = int(catalog.list_files(source_id)[0]["id"])
            service = ThumbnailService(catalog, root / "cache")

            thumbnail = service.get_or_create(media_id)

            self.assertIsNotNone(thumbnail)
            assert thumbnail is not None
            self.assertTrue(thumbnail.is_file())
            self.assertTrue(thumbnail.is_relative_to(root / "cache"))
            self.assertEqual(digest(original), original_digest)
            self.assertEqual(original.stat().st_size, original_stat.st_size)
            self.assertEqual(original.stat().st_mtime_ns, original_stat.st_mtime_ns)

    def test_reused_media_id_does_not_reuse_another_files_thumbnail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_source = root / "first"
            second_source = root / "second"
            first_source.mkdir()
            second_source.mkdir()
            first = first_source / "photo.jpg"
            second = second_source / "photo.jpg"
            Image.new("RGB", (100, 100), "navy").save(first)
            Image.new("RGB", (100, 100), "orange").save(second)
            shared_time = 1_700_000_000_000_000_000
            os.utime(first, ns=(shared_time, shared_time))
            os.utime(second, ns=(shared_time, shared_time))

            catalog = Catalog(root / "catalog.sqlite3")
            first_source_id = int(catalog.add_source(first_source)["id"])
            catalog.replace_source_scan(first_source_id, scan_sources([first_source]))
            first_media_id = int(catalog.list_files(first_source_id)[0]["id"])
            service = ThumbnailService(catalog, root / "cache")
            first_thumbnail = service.get_or_create(first_media_id)

            catalog.remove_source(first_source_id)
            second_source_id = int(catalog.add_source(second_source)["id"])
            catalog.replace_source_scan(second_source_id, scan_sources([second_source]))
            second_media_id = int(catalog.list_files(second_source_id)[0]["id"])
            second_thumbnail = service.get_or_create(second_media_id)

            self.assertEqual(second_media_id, first_media_id)
            self.assertNotEqual(first_thumbnail, second_thumbnail)
            assert second_thumbnail is not None
            with Image.open(second_thumbnail) as preview:
                red, green, blue = preview.getpixel((50, 50))
            self.assertGreater(red, blue)
            self.assertGreater(green, blue)
