from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from media_manager.scanner import scan_sources


class ScannerTests(unittest.TestCase):
    def test_scans_nested_media_and_ignores_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            nested = source / "year" / "event"
            nested.mkdir(parents=True)
            (source / "cover.JPG").write_bytes(b"photo")
            (nested / "clip.MOV").write_bytes(b"video")
            (nested / "notes.txt").write_text("ignore", encoding="utf-8")

            report = scan_sources([source])

            self.assertEqual(report.photo_count, 1)
            self.assertEqual(report.video_count, 1)
            self.assertEqual(
                [item.relative_path for item in report.files],
                ["cover.JPG", os.path.join("year", "event", "clip.MOV")],
            )
            self.assertEqual(report.errors, [])

    def test_does_not_follow_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            outside = Path(directory) / "outside"
            source.mkdir()
            outside.mkdir()
            (outside / "hidden.jpg").write_bytes(b"outside")
            (source / "linked").symlink_to(outside, target_is_directory=True)

            report = scan_sources([source])

            self.assertEqual(report.files, [])


if __name__ == "__main__":
    unittest.main()
