import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from media_manager.catalog import Catalog
from media_manager.storage import StorageCatalog
from media_manager.photo_libraries import PhotoLibraries
from media_manager.photos_originals import PhotosOriginals
from media_manager.photos_adapter import PhotosLibraryUnavailable, PhotosTransferStopped


class StreamingPhotos:
    supported = True
    def __init__(self):
        self.content = {('a', '1:0'): b'photo original' * 120, ('a', '9:0'): b'Live Photo video' * 80,
                        ('b', '1:0'): b'other photo' * 200}
        self.requests = []
        self.before_write = lambda: None
        self.bad_size = False
        self.version = 'v1'
        self.chunk_size = 31
        self.after_chunk = lambda: None
    def probe(self, identifiers=(), **kwargs):
        return dict(sample=['a', 'b', 'c'], matched=list(identifiers), count=2)
    def original_manifest(self, anchors, receive, stopped):
        for asset, names in [('a', [('1:0', 'IMG_1.JPG'), ('9:0', 'IMG_1.MOV')]), ('b', [('1:0', 'IMG_2.JPG')])]:
            receive(dict(id=asset, version=self.version, created_at='2020-02-01T10:30:00Z',
                         resources=[dict(id=r, name=name) for r, name in names]))
        return dict(count=2)
    def stream_original(self, asset, resource, version, anchors, write, progress, stopped):
        self.requests.append((asset, resource))
        self.before_write()
        data = self.content[(asset, resource)]
        for i in range(0, len(data), self.chunk_size):
            if stopped():
                raise PhotosTransferStopped()
            write(data[i:i+self.chunk_size])
            self.after_chunk()
        return dict(size=len(data) + int(self.bad_size))
    def close(self):
        pass


class PhotosOriginalsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.disk = self.root / 'disk'
        self.copy = self.disk / 'Copy'
        self.copy.mkdir(parents=True)
        self.mounted = [dict(id='disk', name='Disk', kind='external', mount_path=str(self.disk), device=self.disk.stat().st_dev)]
        self.catalog = Catalog(self.root / 'catalog.sqlite3')
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.mounted)
        self.storage.refresh(True)
        self.source_id = self.catalog.add_system_photos_source()['id']
        self.adapter = StreamingPhotos()
        self.libraries = PhotoLibraries(self.catalog, self.storage, self.adapter)
        self.libraries.refresh_connection()
        self.link = self.libraries.bind_copy(self.source_id, 'disk', 'Copy')
        self.service = PhotosOriginals(self.libraries, self.adapter)
        self.libraries.originals = self.service
        self.addCleanup(self.service.close)

    def run_copy(self):
        return self.service.start(self.link['id'], self.source_id, background=False)

    def receipts(self):
        with self.catalog.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM photos_copy_files')]

    def test_streams_all_live_photo_resources_and_keeps_only_metadata_in_database(self):
        result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertEqual((result['done_assets'], result['done_resources']), (2, 3))
        self.assertEqual({p.name for p in self.copy.rglob('*') if p.is_file()}, {'IMG_1.JPG', 'IMG_1.MOV', 'IMG_2.JPG'})
        self.assertEqual(len(self.receipts()), 3)
        for receipt in self.receipts():
            data = (self.copy / receipt['path']).read_bytes()
            self.assertEqual(data, self.adapter.content[(receipt['asset_identifier'], receipt['resource_id'])])
            self.assertEqual(receipt['size'], len(data))
            self.assertEqual(receipt['sha256'], '')  # legacy column is unused
        self.assertEqual(list(self.copy.rglob('*.part')), [])
        with self.catalog.connect() as db:
            for table in ('photos_copy_files', 'photos_original_resources', 'photos_original_jobs'):
                self.assertNotIn('BLOB', [r['type'] for r in db.execute('PRAGMA table_info(' + table + ')')])

    def test_adopts_manual_copy_by_name_size_and_metadata_and_preserves_name_collision(self):
        manual = self.copy / 'manual/IMG_1.JPG'
        manual.parent.mkdir()
        manual.write_bytes(self.adapter.content[('a', '1:0')])
        target = self.copy / '2020/2020-02/IMG_2.JPG'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'Unrelated user file')
        result = self.run_copy()
        self.assertEqual((result['reused'], result['saved']), (1, 2), result)
        self.assertEqual(target.read_bytes(), b'Unrelated user file')
        photo = next(r for r in self.receipts() if r['asset_identifier'] == 'a' and r['resource_id'] == '1:0')
        self.assertEqual(photo['path'], 'manual/IMG_1.JPG')
        self.assertFalse((self.copy / '2020/2020-02/IMG_1.JPG').exists())

    def test_first_and_second_runs_never_read_media_for_verification(self):
        with patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            self.run_copy()
            self.adapter.requests.clear()
            result = self.run_copy()
        self.assertEqual(result['done_assets'], 2)
        self.assertEqual(result['reused'], 3)
        self.assertEqual(self.adapter.requests, [])

    def test_changed_existing_original_is_preserved_and_downloaded_to_a_free_name(self):
        self.run_copy()
        target = self.copy / '2020/2020-02/IMG_1.JPG'
        target.write_bytes(b'user replacement')
        self.adapter.requests.clear()
        result = self.run_copy()
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(target.read_bytes(), b'user replacement')
        self.assertEqual(self.adapter.requests, [('a', '1:0')])

    def test_stream_size_mismatch_never_creates_receipts_or_completed_assets(self):
        self.adapter.bad_size = True
        result = self.run_copy()
        self.assertEqual(result['state'], 'completed_with_errors')
        self.assertEqual(result['done_assets'], 0)
        self.assertEqual(result['errors'], 3)
        self.assertEqual(self.receipts(), [])
        self.assertFalse(any(p.is_file() for p in self.copy.rglob('*')))

    def test_pause_mid_stream_and_resume_preserve_finished_resources(self):
        def pause():
            if len(self.adapter.requests) == 2:
                self.service.pause(self.link['id'])
        self.adapter.before_write = pause
        result = self.run_copy()
        self.assertEqual(result['state'], 'paused', result)
        self.assertEqual(result['done_resources'], 1)
        self.assertEqual(result['done_assets'], 0)  # Live Photo motion still missing
        self.adapter.before_write = lambda: None
        self.adapter.requests.clear()
        result = self.run_copy()
        self.assertEqual(result['done_assets'], 2, result)
        self.assertNotIn(('a', '1:0'), self.adapter.requests)
        self.assertEqual(list(self.copy.rglob('*.part')), [])

    def test_unbinding_or_account_change_stops_before_any_final_file(self):
        for change in ('unbind', 'account'):
            with self.subTest(change=change):
                if change == 'unbind':
                    self.adapter.before_write = lambda: self.libraries.unbind_copy(self.source_id, self.link['id'])
                else:
                    self.link = self.libraries.bind_copy(self.source_id, 'disk', 'Copy')
                    def switch():
                        with self.catalog.connect() as db:
                            db.execute('UPDATE photos_libraries SET active=0')
                    self.adapter.before_write = switch
                self.service._validate_at = 0
                with patch('media_manager.photos_originals.time.monotonic', side_effect=lambda: __import__('time').perf_counter() + 1):
                    result = self.run_copy()
                # Validation is throttled during streaming; publication always validates.
                self.assertEqual(result['state'], 'waiting', result)
                self.assertEqual(self.receipts(), [])
                self.assertEqual(list(self.copy.rglob('*.part')), [])

    def test_symlinked_destination_cannot_escape_the_bound_copy(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.copy / '2020').symlink_to(outside, target_is_directory=True)
        result = self.run_copy()
        self.assertEqual(result['done_resources'], 0)
        self.assertEqual(list(outside.iterdir()), [])

    def test_copy_writes_once_without_rename_readback_or_temporary_media(self):
        original_open = os.open
        created = []
        def track(path, flags, mode=0o777, *, dir_fd=None):
            if flags & os.O_CREAT and str(path).startswith('IMG_'):
                created.append((str(path), flags))
            return original_open(path, flags, mode, dir_fd=dir_fd)
        with patch('media_manager.copy_files.publish_exclusive', side_effect=AssertionError('No rename')), \
             patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media reread')), \
             patch('media_manager.photos_originals.os.open', side_effect=track):
            result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertEqual(len(self.receipts()), 3)
        self.assertEqual(list(self.copy.rglob('*.part')), [])
        self.assertEqual(len(created), 3)
        self.assertTrue(all(flags & os.O_EXCL and flags & os.O_WRONLY for _,flags in created))

    def test_disk_full_does_not_publish_or_count_an_original(self):
        class Full:
            f_bavail = 0
            f_frsize = f_bsize = 4096
        with patch('media_manager.photos_originals.os.fstatvfs', return_value=Full()):
            result = self.run_copy()
        self.assertEqual(result['done_assets'], 0)
        self.assertEqual(self.receipts(), [])
        self.assertEqual(list(self.copy.rglob('*.part')), [])

    def test_restart_turns_active_job_into_resumable_pause(self):
        self.run_copy()
        job = self.service.summary(self.link['id'])
        self.service._update(job['id'], state='saving')
        reopened = PhotosOriginals(self.libraries, self.adapter)
        self.assertEqual(reopened.summary(self.link['id'])['state'], 'paused')
        self.assertEqual(reopened.start(self.link['id'], background=False)['done_assets'], 2)

    def test_replaced_root_is_rejected_on_resume(self):
        self.adapter.before_write = lambda: self.service.pause(self.link['id'])
        self.assertEqual(self.run_copy()['state'], 'paused')
        self.copy.rename(self.disk / 'old')
        self.copy.mkdir()
        with self.assertRaisesRegex(ValueError, 'заменена'):
            self.run_copy()

    def test_interrupted_smb_final_is_preserved_and_reported_on_retry(self):
        original_write = self.service._write
        calls = 0
        def fail_final(fd, chunk):
            nonlocal calls
            if len(chunk) > 1000 and calls == 0:
                calls += 1
                os.write(fd, chunk[:17])
                raise OSError('Disconnected during direct write')
            original_write(fd, chunk)
        with patch.object(self.service, '_write', side_effect=fail_final):
            result = self.run_copy()
        self.assertEqual(result['state'], 'completed_with_errors', result)
        partial = self.copy / '2020/2020-02/IMG_1.JPG'
        self.assertEqual(partial.stat().st_size, 17)
        self.assertIn('2020/2020-02/IMG_1.JPG',self.service.journal(self.link['id'])['incomplete_paths'])
        result = self.run_copy()
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(partial.stat().st_size, 17)
        self.assertNotIn('2020/2020-02/IMG_1.JPG', [r['path'] for r in self.receipts()])

    def test_file_appearing_before_exclusive_creation_is_never_replaced(self):
        original_open = os.open
        called = False
        def race(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal called
            if not called and flags & os.O_CREAT and str(path) == 'IMG_1.JPG':
                called = True
                fd = original_open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=dir_fd)
                os.write(fd, b'appeared concurrently')
                os.close(fd)
            return original_open(path, flags, mode, dir_fd=dir_fd)
        with patch('media_manager.photos_originals.os.open', side_effect=race):
            result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertEqual((self.copy / '2020/2020-02/IMG_1.JPG').read_bytes(), b'appeared concurrently')

    def test_changed_written_size_never_creates_a_receipt(self):
        original_write = self.service._write
        def truncate(fd, chunk):
            original_write(fd, chunk)
            os.ftruncate(fd, 1)
        with patch.object(self.service, '_write', side_effect=truncate):
            result = self.run_copy()
        self.assertEqual(result['done_resources'], 0)
        self.assertEqual(self.receipts(), [])
        self.assertEqual(list(self.copy.rglob('*.part')), [])
        self.assertEqual(result['incomplete_files'], 3)

    def test_chunks_are_combined_into_bounded_blocks_and_tail_is_flushed_once(self):
        block = 1024 * 1024
        self.adapter.chunk_size = 256 * 1024
        self.adapter.content[('a', '1:0')] = b'x' * (2 * block + 113)
        writes = []
        write = self.service._write
        def track(fd, data):
            writes.append((self.adapter.requests[-1], len(data)))
            write(fd, data)
        with patch('media_manager.photos_originals.WRITE_BUFFER_BYTES', block), \
             patch.object(self.service, '_write', side_effect=track), \
             patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media read')):
            result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertEqual([length for resource,length in writes if resource == ('a','1:0')], [block,block,113])
        self.assertTrue(all(length <= block for _,length in writes))
        self.assertEqual(sum(length for _,length in writes), sum(map(len,self.adapter.content.values())))
        self.assertEqual((self.copy/'2020/2020-02/IMG_1.JPG').read_bytes(),self.adapter.content[('a','1:0')])

    def test_pause_before_buffer_flush_creates_no_incomplete_file(self):
        self.adapter.after_chunk = lambda:self.service.pause(self.link['id'])
        result = self.run_copy()
        self.assertEqual(result['state'], 'paused', result)
        self.assertEqual(result['done_resources'], 0)
        self.assertFalse(any(p.is_file() for p in self.copy.rglob('*')))
        self.assertEqual(result['incomplete_files'], 0)
        self.adapter.after_chunk = lambda:None
        self.assertEqual(self.run_copy()['done_resources'], 3)

    def test_pause_after_one_block_preserves_partial_file_and_resume_uses_free_name(self):
        write = self.service._write
        def pause(fd, data):
            write(fd, data)
            self.service.pause(self.link['id'])
        with patch('media_manager.photos_originals.WRITE_BUFFER_BYTES', 1024), \
             patch.object(self.service,'_write',side_effect=pause):
            result = self.run_copy()
        self.assertEqual(result['state'], 'paused', result)
        self.assertEqual(result['done_resources'], 0)
        partial = self.copy/'2020/2020-02/IMG_1.JPG'
        self.assertEqual(partial.stat().st_size, 1024)
        self.assertEqual(self.receipts(), [])
        self.assertEqual(self.run_copy()['done_resources'], 3)
        self.assertEqual(partial.stat().st_size, 1024)
        self.assertTrue((self.copy/'2020/2020-02/IMG_1-1.JPG').exists())

    def test_short_os_writes_still_save_every_byte(self):
        original_write = os.write
        with patch('media_manager.photos_originals.os.write',side_effect=lambda fd,data:original_write(fd,data[:17])):
            result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertEqual((self.copy/'2020/2020-02/IMG_1.JPG').read_bytes(),self.adapter.content[('a','1:0')])

    def test_fsync_failure_is_journalled_even_when_size_matches(self):
        with patch('media_manager.photos_originals.os.fsync',side_effect=OSError('Disconnected on flush')):
            result = self.run_copy()
        self.assertEqual(result['done_resources'], 0)
        self.assertEqual(result['incomplete_files'], 3)
        self.assertEqual(self.receipts(), [])
        result = self.run_copy()
        self.assertEqual(result['done_resources'], 3)
        self.assertTrue(all('-1.' in r['path'] for r in self.receipts()))

    def test_resume_keeps_progress_during_inventory_and_partial_manifest(self):
        self.run_copy()
        self.adapter.requests.clear()
        read_manifest = self.adapter.original_manifest
        observations = []
        def interrupted(anchors, receive, stopped):
            def one_asset(asset):
                observations.append(self.service.summary(self.link['id']))
                receive(asset)
                raise PhotosTransferStopped()
            return read_manifest(anchors, one_asset, stopped)
        with patch.object(self.adapter, 'original_manifest', side_effect=interrupted), \
             patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            result = self.run_copy()
        self.assertEqual(result['state'], 'paused', result)
        self.assertEqual(result['done_assets'], 2)
        self.assertEqual(result['total_assets'], 2)
        self.assertEqual(observations[0]['done_assets'], 2)
        self.assertEqual(observations[0]['total_assets'], 2)
        self.assertEqual(self.adapter.requests, [])
        self.assertEqual(self.run_copy()['done_resources'], 3)

    def test_legacy_reset_manifest_recovers_all_receipts_before_resume(self):
        self.run_copy()
        job = self.service.summary(self.link['id'])
        with self.catalog.connect() as db:
            db.execute("UPDATE photos_original_resources SET state='pending'")
        self.service._update(job['id'], state='paused', done_assets=0, done_resources=0)
        with patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            reopened = PhotosOriginals(self.libraries, self.adapter)
            result = reopened.summary(self.link['id'])
        self.assertEqual(result['done_assets'], 2)
        self.assertEqual(result['done_resources'], 3)

    def test_changed_mtime_even_at_same_size_is_saved_to_a_free_name(self):
        self.run_copy()
        target = self.copy / '2020/2020-02/IMG_1.JPG'
        before = target.stat()
        target.write_bytes(b'x' * before.st_size)
        os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns + 2_000_000_000))
        self.adapter.requests.clear()
        self.assertEqual(self.run_copy()['state'], 'completed')
        self.assertEqual(self.adapter.requests, [('a', '1:0')])
        self.assertEqual(target.read_bytes(), b'x' * before.st_size)

    def test_missing_receipt_file_is_downloaded_again_without_rereading_other_files(self):
        self.run_copy()
        (self.copy / '2020/2020-02/IMG_1.JPG').unlink()
        self.adapter.requests.clear()
        with patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertEqual(self.adapter.requests, [('a', '1:0')])

    def test_changed_photos_version_does_not_reuse_an_old_receipt_or_overwrite_it(self):
        self.run_copy()
        self.adapter.version = 'v2'
        self.adapter.requests.clear()
        with patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            result = self.run_copy()
        self.assertEqual(result['saved'], 3)
        self.assertEqual(len(self.adapter.requests), 3)
        self.assertEqual(len(list(self.copy.rglob('*.JPG'))), 4)

    def test_metadata_preserving_changes_are_not_read_or_content_compared(self):
        self.run_copy()
        target = self.copy / '2020/2020-02/IMG_1.JPG'
        before = target.stat()
        target.write_bytes(b'x' * before.st_size)
        os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.adapter.requests.clear()
        with patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            self.assertEqual(self.run_copy()['done_assets'], 2)
        self.assertEqual(self.adapter.requests, [])

    def test_ambiguous_manual_names_are_not_adopted(self):
        for directory in ('first', 'second'):
            path = self.copy / directory / 'IMG_1.JPG'
            path.parent.mkdir()
            path.write_bytes(self.adapter.content[('a', '1:0')])
        with patch('media_manager.photos_originals.os.read', side_effect=AssertionError('No media readback')):
            result = self.run_copy()
        self.assertEqual(result['saved'], 3, result)
        self.assertEqual(result['reused'], 0)

    def test_manual_file_changed_after_inventory_is_not_adopted(self):
        manual = self.copy / 'IMG_1.JPG'
        manual.write_bytes(self.adapter.content[('a', '1:0')])
        def change():
            if len(self.adapter.requests) == 1:
                before = manual.stat()
                os.utime(manual, ns=(before.st_atime_ns, before.st_mtime_ns + 2_000_000_000))
        self.adapter.before_write = change
        result = self.run_copy()
        photo = next(r for r in self.receipts() if r['asset_identifier'] == 'a' and r['resource_id'] == '1:0')
        self.assertNotEqual(photo['path'], 'IMG_1.JPG')
        self.assertEqual(result['saved'], 3, result)

    def test_unknown_staging_file_is_never_deleted(self):
        unknown = self.copy / ('.media-actu-copy-' + 'a'*32 + '-' + 'b'*32 + '.part')
        unknown.write_bytes(b'not owned by this service')
        result = self.run_copy()
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(unknown.read_bytes(), b'not owned by this service')


    def test_original_worker_closes_every_database_connection(self):
        import sqlite3
        opened = []
        class Tracked(sqlite3.Connection):
            closed = False
            def close(self):
                self.closed = True
                super().close()
        def connection():
            db = sqlite3.connect(self.catalog.database_path, factory=Tracked)
            db.row_factory = sqlite3.Row
            opened.append(db)
            return db
        with patch.object(self.catalog, 'connect', side_effect=connection):
            # Other project services use their own connection convention. Keep
            # this assertion focused on the originals worker's scoped handles.
            with patch.object(self.service, '_validate'), patch.object(self.libraries, '_require_active', return_value={'anchors': ['a']}):
                result = self.run_copy()
        self.assertEqual(result['state'], 'completed', result)
        self.assertTrue(opened)
        self.assertTrue(all(db.closed for db in opened))
