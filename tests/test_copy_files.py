import os
import asyncio
import errno
from pathlib import Path
from types import SimpleNamespace
import tempfile
import threading
import unittest
from unittest.mock import patch

from media_manager.copy_files import MissingCopyCatalog, object_id, publish_exclusive
from media_manager.copies import CopyCatalog
from media_manager.paired_comparison import PairedComparisonCatalog
from media_manager.storage import StorageCatalog


class MissingCopyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.main, self.copy = self.root/'main', self.root/'copy'
        for path in (self.main/'Original', self.copy/'Backup'):
            path.mkdir(parents=True)
        self.mounted = [dict(id=name, name=name, kind='external', mount_path=str(path), device=path.stat().st_dev)
                        for name, path in [('main', self.main), ('copy', self.copy)]]
        self.storage = StorageCatalog(self.root/'data/storage.sqlite3', lambda: self.mounted)
        for volume in self.mounted:
            self.storage.directory(volume['id'])
        self.copies = CopyCatalog(self.storage)
        self.group = self.copies.create_main('main', 'Original')
        self.copy_location = self.copies.add_copy(self.group['id'], 'copy', 'Backup')['copies'][0]
        self.pairs = PairedComparisonCatalog(self.storage, self.copies)
        self.transfers = MissingCopyCatalog(self.pairs)
        self.addCleanup(self.pairs.close)
        self.addCleanup(self.transfers.close)

    def put(self, side, path, data=b'example'):
        target = (self.main/'Original' if side == 'left' else self.copy/'Backup')/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def compare(self, files=True):
        folder = self.pairs.create(self.copy_location['id'], background=False)
        self.pairs.run(folder['id'])
        if not files:
            return folder['id']
        report = self.pairs.create(self.copy_location['id'], 'files', folder['id'], background=False)
        self.pairs.run(report['id'])
        self.assertEqual(self.pairs.job(report['id'])['state'], 'completed')
        return report['id']

    def run_plan(self, plan, *, recheck=False):
        self.transfers.start(plan['id'], background=False)
        self.transfers.run(plan['id'], recheck=recheck)
        return self.transfers.job(plan['id'])

    def staging_files(self):
        return list(self.copy.rglob('.media-actu-copy-*.part'))

    def test_preview_is_readonly_and_requires_a_completed_file_report(self):
        self.put('left', 'new')
        with self.assertRaises(ValueError):
            self.transfers.plan(self.compare(files=False))
        plan = self.transfers.plan(self.compare())
        self.assertEqual(plan['state'], 'planned')
        self.assertEqual(plan['total_files'], 1)
        self.assertFalse((self.copy/'Backup/new').exists())
        self.assertEqual(self.transfers.items(plan['id'])['items'][0]['path'], 'new')

    def test_only_missing_files_and_directories_are_created(self):
        original = self.put('left', 'Nested/new', b'copy me')
        self.put('left', 'empty', b'')
        self.put('left', '.Hidden/inside')
        (self.main/'Original/EmptyDirectory').mkdir()
        for side, data in [('left', b'a'), ('right', b'longer')]:
            self.put(side, 'different-size', data)
        for side in ('left', 'right'):
            self.put(side, 'same')
        extra = self.put('right', 'extra')
        before = original.read_bytes(), original.stat().st_mtime_ns
        plan = self.transfers.plan(self.compare())
        paths = {i['path'] for i in self.transfers.items(plan['id'])['items']}
        self.assertFalse({'different-size', 'same', 'extra'} & paths)
        result = self.run_plan(plan)
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['copied_files'], 3)
        self.assertEqual((self.copy/'Backup/Nested/new').read_bytes(), b'copy me')
        self.assertTrue((self.copy/'Backup/EmptyDirectory').is_dir())
        self.assertEqual((self.copy/'Backup/empty').read_bytes(), b'')
        self.assertEqual((self.copy/'Backup/different-size').read_bytes(), b'longer')
        self.assertEqual(extra.read_bytes(), b'example')
        self.assertEqual(before, (original.read_bytes(), original.stat().st_mtime_ns))
        self.assertEqual(self.staging_files(), [])

    def test_existing_target_created_after_preview_is_skipped(self):
        self.put('left', 'new', b'original')
        plan = self.transfers.plan(self.compare())
        target = self.put('right', 'new', b'arrived later')
        result = self.run_plan(plan)
        self.assertEqual(result['skipped'], 1)
        self.assertEqual(target.read_bytes(), b'arrived later')

    def test_target_appearing_at_publication_is_never_overwritten(self):
        self.put('left', 'new', b'original')
        plan = self.transfers.plan(self.compare())
        target = self.copy/'Backup/new'

        def concurrent_target(parent, temporary, name):
            target.write_bytes(b'concurrent writer')
            return publish_exclusive(parent, temporary, name)

        with patch('media_manager.copy_files.publish_exclusive', side_effect=concurrent_target):
            result = self.run_plan(plan)
        self.assertEqual(result['skipped'], 1)
        self.assertEqual(target.read_bytes(), b'concurrent writer')
        self.assertEqual(self.staging_files(), [])

    def test_changed_source_since_report_is_not_copied(self):
        source = self.put('left', 'new', b'old')
        plan = self.transfers.plan(self.compare())
        source.write_bytes(b'changed')
        result = self.run_plan(plan)
        self.assertEqual(result['errors'], 1)
        self.assertFalse((self.copy/'Backup/new').exists())

    def test_preview_freezes_fresh_source_metadata_without_reading_file_contents(self):
        source = self.put('left', 'new', b'old')
        report = self.compare()
        source.write_bytes(b'current version')
        with patch('media_manager.copy_files.os.read', side_effect=AssertionError('Preview must not read bytes')):
            plan = self.transfers.plan(report)
        self.assertEqual(plan['total_bytes'], len(b'current version'))
        result = self.run_plan(plan)
        self.assertEqual(result['errors'], 0)
        self.assertEqual((self.copy/'Backup/new').read_bytes(), b'current version')

    def test_source_replaced_by_fifo_does_not_block_or_copy(self):
        source = self.put('left', 'new')
        plan = self.transfers.plan(self.compare())
        source.unlink()
        os.mkfifo(source)
        result = self.run_plan(plan)
        self.assertEqual(result['errors'], 1)
        self.assertFalse((self.copy/'Backup/new').exists())

    def test_source_changing_while_reading_leaves_no_final_or_partial_file(self):
        source = self.put('left', 'new', b'a'*2048)
        plan = self.transfers.plan(self.compare())
        read = os.read

        def changed(descriptor, size):
            chunk = read(descriptor, size)
            if chunk:
                source.write_bytes(b'b'*2048)
            return chunk

        with patch('media_manager.copy_files.os.read', side_effect=changed):
            result = self.run_plan(plan)
        self.assertEqual(result['errors'], 1)
        self.assertFalse((self.copy/'Backup/new').exists())
        self.assertEqual(self.staging_files(), [])

    def test_stop_removes_only_the_incomplete_staging_file(self):
        self.put('left', 'new', b'a'*2048)
        extra = self.put('right', 'keep')
        plan = self.transfers.plan(self.compare())
        read = os.read

        def stopped(descriptor, size):
            chunk = read(descriptor, size)
            self.transfers._stop.set()
            return chunk

        with patch('media_manager.copy_files.os.read', side_effect=stopped):
            result = self.run_plan(plan)
        self.assertEqual(result['state'], 'stopped')
        self.assertFalse((self.copy/'Backup/new').exists())
        self.assertEqual(self.staging_files(), [])
        self.assertEqual(extra.read_bytes(), b'example')

    def test_symlink_target_parent_is_not_followed(self):
        self.put('left', 'Nested/new')
        plan = self.transfers.plan(self.compare())
        outside = self.root/'outside'
        outside.mkdir()
        (self.copy/'Backup/Nested').symlink_to(outside, target_is_directory=True)
        result = self.run_plan(plan)
        self.assertGreater(result['errors'], 0)
        self.assertEqual(list(outside.iterdir()), [])

    def test_target_root_replaced_after_preview_requires_new_preview(self):
        self.put('left', 'new')
        plan = self.transfers.plan(self.compare())
        (self.copy/'Backup').rename(self.copy/'OldBackup')
        (self.copy/'Backup').mkdir()
        with self.assertRaises(OSError):
            self.transfers.start(plan['id'], background=False)
        self.assertEqual(list((self.copy/'Backup').iterdir()), [])

    def test_parent_replaced_during_copy_is_detected_before_publication(self):
        self.put('left', 'Nested/new', b'a'*2048)
        (self.copy/'Backup/Nested').mkdir()
        plan = self.transfers.plan(self.compare())
        read, replaced = os.read, False

        def replaced_parent(descriptor, size):
            nonlocal replaced
            chunk = read(descriptor, size)
            if chunk and not replaced:
                (self.copy/'Backup/Nested').rename(self.copy/'Backup/Moved')
                (self.copy/'Backup/Nested').mkdir()
                replaced = True
            return chunk

        with patch('media_manager.copy_files.os.read', side_effect=replaced_parent):
            result = self.run_plan(plan)
        self.assertEqual(result['errors'], 1)
        self.assertFalse((self.copy/'Backup/Nested/new').exists())
        self.assertFalse((self.copy/'Backup/Moved/new').exists())
        self.assertEqual(self.staging_files(), [])

    def test_conflicting_parent_and_its_descendants_are_not_in_plan(self):
        self.put('left', 'Conflict/inside')
        self.put('right', 'Conflict', b'keep this file')
        self.put('left', 'new')
        report = self.compare()
        self.assertEqual(self.pairs.job(report)['copyable_count'], 1)
        plan = self.transfers.plan(report)
        self.assertEqual([i['path'] for i in self.transfers.items(plan['id'])['items']], ['new'])
        result = self.run_plan(plan, recheck=True)
        self.pairs._thread.join(timeout=10)
        self.assertEqual(self.pairs.job(result['verification_id'])['copyable_count'], 0)

    def test_removed_link_and_offline_volume_cannot_start_a_plan(self):
        self.put('left', 'new')
        plan = self.transfers.plan(self.compare())
        self.mounted.pop()
        with self.assertRaises(ValueError):
            self.transfers.start(plan['id'], background=False)
        self.copies.remove_copy(self.copy_location['id'])
        with self.assertRaises(KeyError):
            self.transfers.start(plan['id'], background=False)

    def test_no_space_fails_without_publishing_a_file(self):
        self.put('left', 'new')
        plan = self.transfers.plan(self.compare())
        with patch('media_manager.copy_files.os.fstatvfs', return_value=SimpleNamespace(f_bavail=0, f_frsize=4096)):
            result = self.run_plan(plan)
        self.assertEqual(result['errors'], 1)
        self.assertFalse((self.copy/'Backup/new').exists())
        self.assertEqual(self.staging_files(), [])

    def test_completed_copy_creates_new_comparison_and_keeps_other_marks_and_old_report(self):
        self.put('left', 'new')
        self.put('left', 'different', b'a')
        self.put('right', 'different', b'bb')
        self.put('right', 'extra')
        report = self.compare()
        self.pairs.decide(report, 'extra', 'keep')
        plan = self.transfers.plan(report)
        result = self.run_plan(plan, recheck=True)
        self.assertIsNotNone(result['verification_id'])
        self.pairs._thread.join(timeout=10)
        updated = self.pairs.job(result['verification_id'])
        self.assertEqual(updated['state'], 'completed', updated['message'])
        self.assertEqual(updated['method'], 'size')
        self.assertNotIn('missing_copy', updated['counts'])
        self.assertEqual(updated['counts']['size_different'], 1)
        self.assertEqual(self.pairs.job(report)['counts']['missing_copy'], 1)
        extra = next(r for r in self.pairs.rows(updated['id'])['rows'] if r['path'] == 'extra')
        self.assertEqual(extra['decision'], 'keep')

    def test_restart_records_interruption_and_next_explicit_copy_cleans_owned_staging(self):
        self.put('left', 'new')
        report = self.compare()
        old = self.transfers.plan(report)
        self.transfers.start(old['id'], background=False)
        name = '.media-actu-copy-' + old['id'] + '-' + 'a'*32 + '.part'
        temporary = self.copy/'Backup'/name
        temporary.write_bytes(b'incomplete')
        import json
        self.transfers._item(old['id'], 'new', staging=json.dumps({'name': name, 'identity': object_id(temporary.stat())}))
        reopened = MissingCopyCatalog(self.pairs)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.job(old['id'])['state'], 'interrupted')
        self.assertTrue(temporary.exists(), 'Startup must not silently write to disks')
        self.transfers = reopened
        current = reopened.plan(report)
        result = self.run_plan(current)
        self.assertEqual(result['errors'], 0)
        self.assertFalse(temporary.exists())
        self.assertEqual((self.copy/'Backup/new').read_bytes(), b'example')

    def test_registered_aliases_cannot_make_a_nested_copy_inside_the_source(self):
        self.put('left', 'new')
        (self.main/'Original/Backup').mkdir()
        report = self.compare()
        with self.storage.connect() as db:
            db.execute("UPDATE copy_locations SET volume_id='main',path='Original/Backup' WHERE id=?", (self.copy_location['id'],))
        with self.assertRaises(ValueError):
            self.transfers.plan(report)
        overlapping = self.compare()
        with self.assertRaisesRegex(ValueError, 'пересекаются'):
            self.transfers.plan(overlapping)

    def test_api_preview_and_execution_use_only_the_registered_direction(self):
        self.put('left', 'new')
        report = self.compare()

        async def exercise():
            import httpx
            with patch.dict(os.environ, {'MEDIA_ACTU_DATA_DIR': str(self.root/'api-data')}):
                import app as core
            with patch.object(core, 'missing_copies', self.transfers), patch.object(core, 'paired_comparison', self.pairs):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app), base_url='http://test') as client:
                    response = await client.post(f'/api/storage/paired-comparisons/{report}/copy-plan')
                    self.assertEqual(response.status_code, 201, response.text)
                    operation = response.json()
                    self.assertEqual(operation['scopes']['left']['id'], self.group['main']['id'])
                    self.assertEqual(operation['scopes']['right']['id'], self.copy_location['id'])
                    self.assertFalse((self.copy/'Backup/new').exists())
                    items = await client.get('/api/storage/copy-operations/' + operation['id'] + '/items')
                    self.assertEqual(items.json()['total'], 1)
                    response = await client.post('/api/storage/copy-operations/' + operation['id'] + '/start')
                    self.assertEqual(response.status_code, 200, response.text)
                    thread = self.transfers._thread
                    if thread:
                        thread.join(timeout=10)
                    if self.pairs._thread:
                        self.pairs._thread.join(timeout=10)
                    self.assertEqual((self.copy/'Backup/new').read_bytes(), b'example')
                    response = await client.post('/api/storage/copy-operations/' + operation['id'] + '/start')
                    self.assertEqual(response.status_code, 400)

        asyncio.run(exercise())

    def test_running_copy_excludes_another_comparison_and_can_be_stopped(self):
        self.put('left', 'new')
        plan = self.transfers.plan(self.compare())
        entered, release = threading.Event(), threading.Event()
        copy_file = self.transfers._copy_file

        def wait_for_stop(*args):
            entered.set()
            release.wait(timeout=5)
            return copy_file(*args)

        with patch.object(self.transfers, '_copy_file', side_effect=wait_for_stop):
            self.transfers.start(plan['id'])
            thread = self.transfers._thread
            try:
                self.assertTrue(entered.wait(timeout=3))
                with self.assertRaises(ValueError):
                    self.pairs.create(self.copy_location['id'], background=False)
                self.transfers.stop(plan['id'])
            finally:
                release.set()
                thread.join(timeout=5)
        self.assertEqual(self.transfers.job(plan['id'])['state'], 'stopped')
        self.assertFalse((self.copy/'Backup/new').exists())

    def test_network_copy_uses_exclusive_creation_without_atomic_rename(self):
        self.put('left', 'new', b'network copy')
        self.mounted[1]['kind'] = 'network'
        plan = self.transfers.plan(self.compare())
        with patch('media_manager.copy_files.publish_exclusive', side_effect=AssertionError('SMB has no atomic rename')):
            result = self.run_plan(plan)
        self.assertEqual(result['errors'], 0)
        self.assertEqual((self.copy/'Backup/new').read_bytes(), b'network copy')
        self.assertEqual(result['incomplete_files'], 0)

    def test_unsupported_atomic_publication_falls_back_without_overwriting(self):
        self.put('left', 'new')
        plan = self.transfers.plan(self.compare())
        with patch('media_manager.copy_files.publish_exclusive', side_effect=OSError(errno.ENOTSUP, 'unsupported')):
            result = self.run_plan(plan)
        self.assertEqual(result['errors'], 0)
        self.assertEqual((self.copy/'Backup/new').read_bytes(), b'example')
        self.assertEqual(self.staging_files(), [])

    def test_interrupted_network_copy_is_marked_even_when_its_size_already_matches(self):
        source = self.put('left', 'new', b'a'*2048)
        self.mounted[1]['kind'] = 'network'
        plan = self.transfers.plan(self.compare())
        read = os.read

        def stopped(descriptor, size):
            chunk = read(descriptor, size)
            self.transfers._stop.set()
            return chunk

        with patch('media_manager.copy_files.os.read', side_effect=stopped):
            result = self.run_plan(plan)
        self.assertEqual(result['state'], 'stopped')
        self.assertEqual(result['incomplete_files'], 1)
        target = self.copy/'Backup/new'
        self.assertEqual(target.stat().st_size, source.stat().st_size)
        report = self.compare()
        row = self.pairs.rows(report)['rows'][0]
        self.assertEqual(row['status'], 'copy_incomplete')
        self.assertEqual(self.pairs.job(report)['copyable_count'], 0)
        self.assertTrue(self.transfers.items(plan['id'])['items'][0]['incomplete'])
        # A manual removal allows a fresh confirmed plan; old journal entries stay historical.
        target.unlink()
        current = self.transfers.plan(self.compare())
        self.run_plan(current)
        self.assertEqual(self.pairs.rows(self.compare())['rows'][0]['status'], 'same_size')

    def test_network_target_appearing_before_exclusive_open_is_skipped(self):
        self.put('left', 'new')
        self.mounted[1]['kind'] = 'network'
        plan = self.transfers.plan(self.compare())
        open_file = os.open
        target = self.copy/'Backup/new'

        def appeared(path, flags, *args, **kwargs):
            if path == 'new' and flags & os.O_EXCL:
                target.write_bytes(b'concurrent')
            return open_file(path, flags, *args, **kwargs)

        with patch('media_manager.copy_files.os.open', side_effect=appeared):
            result = self.run_plan(plan)
        self.assertEqual(result['skipped'], 1)
        self.assertEqual(target.read_bytes(), b'concurrent')

