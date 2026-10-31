from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from PIL import Image

from media_manager.catalog import Catalog
from media_manager.photo_libraries import PhotoLibraries
from media_manager.photos_adapter import PhotosAccessDenied, PhotosLibraryUnavailable, PhotosThumbnailPending
from media_manager.storage import StorageCatalog
from media_manager.thumbnails import ThumbnailService
from photo_libraries_ui import library_state, progress_text


def assets(prefix, count=4):
    return [dict(id=f'{prefix}-{i}/L0/001', name=f'IMG_{i}.JPG', kind='photo' if i else 'video',
                 created_at='2026-08-09T12:30:00+03:00', size=1024) for i in range(count)]


class FakePhotos:
    def __init__(self, prefix='first'):
        self.assets = assets(prefix)
        self.denied = False
        self.fail_thumbnail = None
        self.thumbnail_requests = []

    def probe(self, identifiers=(), **kwargs):
        if self.denied:
            raise PhotosAccessDenied('No permission')
        current = [a['id'] for a in self.assets]
        return dict(count=len(current), sample=current[:12], matched=[i for i in identifiers if i in current])

    def scan(self, anchors=()):
        if anchors and len(set(anchors).intersection(a['id'] for a in self.assets)) < min(3, len(anchors)):
            raise PhotosLibraryUnavailable('Wrong library')
        return self.assets

    def create_thumbnail(self, identifier, target, **kwargs):
        self.scan(kwargs['anchors'])
        if self.fail_thumbnail:
            raise self.fail_thumbnail
        self.thumbnail_requests.append(identifier)
        Image.new('RGB', (20, 20), 'blue').save(target)
        return target


class PhotoLibrariesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        disk = self.root / 'disk'
        (disk / 'CopyA' / 'Nested').mkdir(parents=True)
        (disk / 'CopyB').mkdir()
        self.disk = disk
        self.mounted = [dict(id='disk', name='Disk', kind='external', mount_path=str(disk), device=disk.stat().st_dev)]
        self.catalog = Catalog(self.root / 'catalog.sqlite3')
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.mounted)
        self.storage.refresh(True)
        self.source = self.catalog.add_system_photos_source()
        self.source_id = self.source['id']
        self.catalog.replace_photos_scan(self.source_id, assets('first'))
        self.adapter = FakePhotos()
        self.libraries = PhotoLibraries(self.catalog, self.storage, self.adapter)

    def test_migration_preserves_media_ids_and_existing_cached_previews_without_access(self):
        media = self.catalog.list_files(self.source_id, '2026/2026-08')[0]
        thumbnails = ThumbnailService(self.catalog, self.root / 'cache', self.adapter, self.libraries)
        self.libraries.refresh_connection()
        cached = thumbnails.get_or_create(media['id'])
        self.adapter.denied = True
        reopened = PhotoLibraries(self.catalog, self.storage, self.adapter)
        self.assertEqual(reopened.refresh_connection()['state'], 'no_access')
        self.assertEqual(thumbnails.get_cached(media['id']), cached)
        self.assertEqual(self.catalog.get_media(media['id'])['source_id'], self.source_id)

    def test_switching_accounts_keeps_old_catalogue_and_copy_associations(self):
        self.libraries.refresh_connection()
        old_ids = [a['id'] for a in self.catalog.list_files(self.source_id, '2026/2026-08')]
        copy = self.libraries.bind_copy(self.source_id, 'disk', 'CopyA')
        self.adapter.assets = assets('second')
        self.assertEqual(self.libraries.refresh_connection()['state'], 'unregistered')
        with self.assertRaises(PhotosLibraryUnavailable):
            self.libraries.scan(self.source_id)
        second = self.libraries.register('Other Apple ID')
        self.libraries.scan(second['source_id'])
        self.assertNotEqual(second['source_id'], self.source_id)
        self.assertEqual([a['id'] for a in self.catalog.list_files(self.source_id, '2026/2026-08')], old_ids)
        old = next(p for p in self.libraries.list()['libraries'] if p['id'] == self.source_id)
        self.assertFalse(old['active'])
        self.assertEqual(old['copies'][0]['id'], copy['id'])
        self.adapter.assets = assets('first')
        self.assertEqual(self.libraries.refresh_connection()['source_id'], self.source_id)

    def test_thumbnail_identity_guard_stops_a_changed_library_before_writing(self):
        self.libraries.refresh_connection()
        self.adapter.assets = assets('second')
        target = self.root / 'preview.jpg'
        with self.assertRaises(PhotosLibraryUnavailable):
            self.libraries.create_thumbnail(self.source_id, 'first-1/L0/001', target)
        self.assertFalse(target.exists())
        self.assertTrue(self.catalog.photos_queue_paused())

    def test_small_photokit_preview_stays_visible_while_waiting_for_a_larger_local_image(self):
        self.libraries.refresh_connection()
        media = self.catalog.list_files(self.source_id, '2026/2026-08')[0]
        thumbnails = ThumbnailService(self.catalog, self.root / 'cache', self.adapter, self.libraries)
        target = thumbnails.get_or_create(media['id'])
        Image.new('RGB', (64, 48), 'blue').save(target)
        previous = target.read_bytes()
        self.adapter.fail_thumbnail = PhotosThumbnailPending('Larger thumbnail unavailable locally')
        with self.assertRaises(PhotosThumbnailPending):
            thumbnails.get_or_create(media['id'])
        self.assertEqual(thumbnails.get_cached(media['id']).read_bytes(), previous)
        def larger(identifier, target, **kwargs):
            Image.new('RGB', (640, 480), 'green').save(target)
            return target
        self.adapter.create_thumbnail = Mock(side_effect=larger)
        thumbnails.get_or_create(media['id'])
        with Image.open(thumbnails.get_cached(media['id'])) as image:
            self.assertEqual(image.size, (640, 480))
        self.adapter.create_thumbnail.reset_mock()
        thumbnails.get_or_create(media['id'])
        self.adapter.create_thumbnail.assert_not_called()

    def test_resuming_photos_does_not_resume_the_paused_folder_queue_and_includes_video(self):
        self.catalog.set_thumbnail_queue_paused(True)
        self.libraries.set_paused(self.source_id, False)
        self.assertTrue(self.catalog.thumbnail_queue_paused())
        self.assertFalse(self.catalog.photos_queue_paused())
        claimed = []
        while (media_id := self.catalog.claim_thumbnail_job('photos')) is not None:
            claimed.append(self.catalog.get_media(media_id))
            self.catalog.finish_thumbnail_job(media_id)
        self.assertEqual(len(claimed), 4)
        self.assertIn('video', [m['kind'] for m in claimed])
        self.libraries.set_paused(self.source_id, True)
        self.assertTrue(self.catalog.photos_queue_paused())

    def test_cloud_waits_do_not_block_the_next_asset_or_count_as_errors(self):
        self.libraries.refresh_connection()
        self.catalog.enqueue_source_thumbnails(self.source_id)
        first = self.catalog.claim_thumbnail_job('photos')
        self.catalog.defer_thumbnail_job(first, 'Cloud only', seconds=3600)
        second = self.catalog.claim_thumbnail_job('photos')
        self.assertNotEqual(first, second)
        state = self.libraries.list()['libraries'][0]
        self.assertEqual(state['waiting'], 1)
        self.assertEqual(state['thumbnail_error'], 0)
        self.assertEqual(state['thumbnail_pending'], 3)

    def test_copy_binding_and_unbinding_never_write_originals_or_touch_destination_files(self):
        existing = self.disk / 'CopyA' / 'existing.jpg'
        existing.write_bytes(b'untouched original')
        before = {str(p.relative_to(self.disk)): p.read_bytes() for p in self.disk.rglob('*') if p.is_file()}
        link = self.libraries.bind_copy(self.source_id, 'disk', 'CopyA')
        self.libraries.unbind_copy(self.source_id, link['id'])
        self.assertEqual(self.libraries.list()['libraries'][0]['copies'], [])
        same = self.libraries.bind_copy(self.source_id, 'disk', 'CopyA')
        self.assertEqual(same['id'], link['id'])
        self.assertEqual(before, {str(p.relative_to(self.disk)): p.read_bytes() for p in self.disk.rglob('*') if p.is_file()})

    def test_copy_targets_reject_symlinks_parent_traversal_and_overlapping_libraries(self):
        (self.disk / 'Link').symlink_to(self.disk / 'CopyA', target_is_directory=True)
        for path in ('', '../outside', 'Link'):
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                self.libraries.bind_copy(self.source_id, 'disk', path)
        self.libraries.bind_copy(self.source_id, 'disk', 'CopyA')
        self.adapter.assets = assets('second')
        second = self.libraries.register('Second')
        for path in ('CopyA', 'CopyA/Nested'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.libraries.bind_copy(second['source_id'], 'disk', path)
        self.assertEqual(self.libraries.bind_copy(second['source_id'], 'disk', 'CopyB')['number'], 1)

    def test_renaming_survives_legacy_source_registration_and_restart(self):
        self.libraries.rename(self.source_id, 'My Apple ID')
        self.catalog.add_system_photos_source()
        reopened = PhotoLibraries(self.catalog, self.storage, self.adapter)
        self.assertEqual(reopened.list()['libraries'][0]['label'], 'My Apple ID')

    def test_photokit_scan_without_resource_sizes_preserves_known_original_sizes(self):
        self.libraries.refresh_connection()
        self.adapter.assets = [{k: v for k, v in a.items() if k != 'size'} for a in self.adapter.assets]
        self.libraries.scan(self.source_id)
        self.assertEqual([a['size'] for a in self.catalog.list_files(self.source_id, '2026/2026-08')], [1024]*4)

    def test_copy_receipts_are_metadata_only_and_survive_removed_photos(self):
        link = self.libraries.bind_copy(self.source_id, 'disk', 'CopyA')
        identifier = assets('first')[0]['id']
        with self.catalog.connect() as db:
            db.execute('INSERT INTO photos_copy_files VALUES (?,?,?,?,?,?,?)',
                       (link['id'], identifier, 'original', 'asset/original.mov', 123, 'abc', '2026-10-31'))
        self.catalog.replace_photos_scan(self.source_id, [])
        with self.catalog.connect() as db:
            self.assertEqual(db.execute('SELECT asset_identifier FROM photos_copy_files').fetchone()[0], identifier)
            types = [r['type'] for r in db.execute('PRAGMA table_info(photos_copy_files)')]
            self.assertNotIn('BLOB', types)

    def test_sidebar_progress_and_cloud_wait_states_are_separate(self):
        library = dict(thumbnail_done=3410, thumbnail_total=46189, active=True, paused=False,
                       thumbnail_pending=20, thumbnail_running=0, waiting=20, connection_state='ready')
        self.assertIn('7.4%', progress_text(library))
        self.assertIn('20', library_state(library))
        library['paused'] = True
        self.assertEqual(library_state(library), 'Пауза')
