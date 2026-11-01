from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from media_manager.catalog import Catalog
from media_manager.photo_libraries import PhotoLibraries
from media_manager.photos_browser import PhotosBrowser
from media_manager.storage import StorageCatalog
from tests.test_photo_libraries import FakePhotos, assets


class PhotosBrowserTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.catalog = Catalog(root / 'catalog.sqlite3')
        storage = StorageCatalog(root / 'storage.sqlite3', lambda: [])
        self.adapter = FakePhotos()
        self.source_id = self.catalog.add_system_photos_source()['id']
        self.catalog.replace_photos_scan(self.source_id, assets('first'))
        self.libraries = PhotoLibraries(self.catalog, storage, self.adapter)
        self.browser = PhotosBrowser(self.libraries)

    def test_offline_catalogue_opens_as_year_month_and_file_without_calling_photos(self):
        self.adapter.probe = Mock(side_effect=AssertionError('No live Photos access'))
        root = self.browser.browse(self.source_id)
        self.assertEqual([(e['name'], e['count']) for e in root['entries']], [('2026', 4)])
        self.assertTrue(root['cached'])
        year = self.browser.browse(self.source_id, '2026')
        self.assertEqual(year['entries'][0]['path'], '2026/2026-08')
        month = self.browser.browse(self.source_id, '2026/2026-08')
        self.assertEqual(len(month['entries']), 4)
        video = next(e for e in month['entries'] if e['media_kind'] == 'video')
        self.assertEqual(self.browser.browse(self.source_id, video['path'])['entry'], video)
        self.adapter.probe.assert_not_called()

    def test_pagination_includes_every_object_even_with_duplicate_filenames(self):
        items = assets('large', 1007)
        for item in items:
            item['name'] = 'same.JPG'
        self.catalog.replace_photos_scan(self.source_id, items)
        gathered = []
        while True:
            page = self.browser.browse(self.source_id, '2026/2026-08', offset=len(gathered), limit=150)
            gathered.extend(page['entries'])
            if not page['has_more']:
                break
        self.assertEqual(len(gathered), 1007)
        self.assertEqual(len({e['path'] for e in gathered}), 1007)
        self.assertEqual(page['total'], 1007)

    def test_paths_and_preview_status_are_scoped_to_the_chosen_library(self):
        own = self.browser.browse(self.source_id, '2026/2026-08')['entries'][0]
        self.adapter.assets = assets('second')
        second = self.libraries.register('Second')['source_id']
        self.libraries.scan(second)
        other = self.browser.browse(second, '2026/2026-08')['entries'][0]
        with self.catalog.connect() as db:
            db.execute("UPDATE thumbnail_jobs SET status='done'")
        self.assertEqual(self.browser.preview_status(self.source_id, [own['media_id'], other['media_id']])['ready'], [own['media_id']])
        for path in ('../outside', other['path'], '2026/missing', '2026/2026-08/not-a-file'):
            with self.subTest(path=path), self.assertRaises((KeyError, ValueError)):
                self.browser.browse(self.source_id, path)

    def test_empty_and_undated_catalogues_remain_browsable(self):
        self.catalog.replace_photos_scan(self.source_id, [])
        self.assertEqual(self.browser.browse(self.source_id)['entries'], [])
        items = assets('undated', 1)
        items[0]['created_at'] = ''
        self.catalog.replace_photos_scan(self.source_id, items)
        root = self.browser.browse(self.source_id)
        self.assertEqual(root['entries'][0]['name'], 'Без даты')
        self.assertEqual(self.browser.browse(self.source_id, 'Без даты')['total'], 1)
