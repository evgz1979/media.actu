from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from media_manager.catalog import Catalog
from media_manager.scanner import scan_sources


class CatalogTests(unittest.TestCase):
    def test_scan_is_persistent_and_reconciles_removed_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            nested = source / "nested"
            nested.mkdir(parents=True)
            first = source / "first.jpg"
            second = nested / "second.mov"
            first.write_bytes(b"photo")
            second.write_bytes(b"video")

            catalog = Catalog(root / "catalog.sqlite3")
            source_row = catalog.add_source(source)
            source_id = int(source_row["id"])
            catalog.replace_source_scan(source_id, scan_sources([source]))

            initial = catalog.summary()
            self.assertEqual(initial["total"], 2)
            self.assertEqual(initial["photos"], 1)
            self.assertEqual(initial["videos"], 1)
            media_id = catalog.list_files(source_id, "")[0]["id"]

            second.unlink()
            first.write_bytes(b"updated photo")
            catalog.replace_source_scan(source_id, scan_sources([source]))

            updated = catalog.summary()
            self.assertEqual(updated["total"], 1)
            self.assertGreater(updated["revision"], initial["revision"])
            self.assertEqual(catalog.list_files(source_id, "")[0]["id"], media_id)

    def test_folder_tree_contains_nested_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            nested = source / "2026" / "trip"
            nested.mkdir(parents=True)
            (nested / "photo.jpg").write_bytes(b"photo")

            catalog = Catalog(root / "catalog.sqlite3")
            source_id = int(catalog.add_source(source)["id"])
            catalog.replace_source_scan(source_id, scan_sources([source]))

            tree = catalog.folder_tree(source_id)
            self.assertEqual(tree[0]["id"], "__root__")
            self.assertEqual(tree[0]["label"], "Корень")
            self.assertEqual(tree[0]["children"][0]["label"], "2026")
            self.assertEqual(
                tree[0]["children"][0]["children"][0]["label"], "trip"
            )

    def test_resolve_source_folder_stays_inside_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            nested = source / "year" / "day"
            nested.mkdir(parents=True)

            catalog = Catalog(root / "catalog.sqlite3")
            source_id = int(catalog.add_source(source)["id"])

            self.assertEqual(
                catalog.resolve_source_folder(source_id, "year/day"),
                nested.resolve(),
            )
            with self.assertRaises(PermissionError):
                catalog.resolve_source_folder(source_id, "../outside")

    def test_resolve_media_file_returns_scanned_original(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            original = source / "photo.jpg"
            original.write_bytes(b"photo")

            catalog = Catalog(root / "catalog.sqlite3")
            source_id = int(catalog.add_source(source)["id"])
            catalog.replace_source_scan(source_id, scan_sources([source]))
            media_id = int(catalog.list_files(source_id)[0]["id"])

            self.assertEqual(catalog.resolve_media_file(media_id), original.resolve())

    def test_source_role_label_and_comment_can_be_updated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "storage"
            source.mkdir()
            catalog = Catalog(root / "catalog.sqlite3")

            created = catalog.add_source(
                source,
                role="storage",
                label="NAS — MediaCopy1",
                comment="Первая независимая копия",
            )
            self.assertEqual(created["role"], "storage")
            self.assertEqual(created["label"], "NAS — MediaCopy1")

            updated = catalog.update_source_metadata(
                int(created["id"]),
                role="storage",
                label="NAS — MediaCopy01",
                comment="Стойка 1",
            )
            self.assertEqual(updated["label"], "NAS — MediaCopy01")
            self.assertEqual(updated["comment"], "Стойка 1")
