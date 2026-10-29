import hashlib
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from media_manager.copies import CopyCatalog
from media_manager.paired_comparison import PairedComparisonCatalog
from media_manager.storage import StorageCatalog


class PairedComparisonTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.main, self.copy = self.root/'main', self.root/'copy'
        for folder in (self.main/'Original', self.copy/'Backup'):
            folder.mkdir(parents=True)
        self.mounted = [dict(id=name, name=name, kind='external', mount_path=str(folder), device=folder.stat().st_dev)
                        for name, folder in [('main', self.main), ('copy', self.copy)]]
        self.storage = StorageCatalog(self.root/'data/storage.sqlite3', lambda: self.mounted)
        for volume in self.mounted:
            self.storage.directory(volume['id'])
        self.copies = CopyCatalog(self.storage)
        group = self.copies.create_main('main', 'Original')
        self.location = self.copies.add_copy(group['id'], 'copy', 'Backup')['copies'][0]
        self.pairs = PairedComparisonCatalog(self.storage, self.copies)
        self.addCleanup(self.pairs.close)

    def put(self, side, path, data=b'data'):
        target = (self.main/'Original' if side == 'left' else self.copy/'Backup')/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def run_job(self, mode='folders', base=None, method='size'):
        job = self.pairs.create(self.location['id'], mode, base, method=method, background=False)
        self.pairs.run(job['id'])
        report = self.pairs.job(job['id'])
        self.assertEqual(report['state'], 'completed', report['message'])
        return report, {row['path']: row for row in self.pairs.rows(job['id'])['rows']}

    def test_folder_comparison_uses_relative_paths_and_reports_both_directions(self):
        for side, paths in [('left', ['Photos/2025/a', 'Docs/2025/b']),
                            ('right', ['Photos/2025/a', 'Moved/2025/b', 'Unique/empty'])]:
            for path in paths:
                self.put(side, path)
        (self.main/'Original/Empty').mkdir()
        (self.copy/'Backup/Empty').mkdir()
        report, rows = self.run_job()
        self.assertEqual(rows['Photos/2025']['status'], 'both')
        self.assertEqual(rows['Docs/2025']['status'], 'missing_copy')
        self.assertEqual(rows['Moved/2025']['status'], 'extra_copy')
        self.assertEqual(rows['Empty']['status'], 'both')
        self.assertTrue(all(r['kind'] == 'directory' for r in rows.values()))
        self.assertEqual(report['hashed_bytes'], 0)

    def test_folder_stage_never_opens_file_contents(self):
        self.put('left', 'Folder/a')
        self.put('right', 'Folder/a', b'different')
        original_open = os.open

        def directory_only(path, flags, **kwargs):
            self.assertTrue(flags & os.O_DIRECTORY)
            return original_open(path, flags, **kwargs)

        with patch('media_manager.comparison.os.open', side_effect=directory_only), \
                patch('media_manager.paired_comparison.os.read', side_effect=AssertionError('no file reads')):
            self.run_job()

    def test_full_stage_checks_content_and_keeps_files_original(self):
        files = [self.put('left', 'same', b'abcdef'), self.put('right', 'same', b'abcdef'),
                 self.put('left', 'changed', b'AAAA'), self.put('right', 'changed', b'BBBB'),
                 self.put('left', 'size', b'x'), self.put('right', 'size', b'xx'),
                 self.put('left', 'missing'), self.put('right', 'extra'),
                 self.put('left', 'empty', b''), self.put('right', 'empty', b'')]
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
        folders, _ = self.run_job()
        report, rows = self.run_job('files', folders['id'], method='sha256')
        self.assertEqual(rows['same']['status'], 'same')
        self.assertEqual(rows['same']['left']['digest'], hashlib.sha256(b'abcdef').hexdigest())
        self.assertEqual(rows['changed']['status'], 'different')
        self.assertEqual(rows['size']['status'], 'different')
        self.assertEqual(rows['empty']['status'], 'same')
        self.assertEqual(rows['missing']['status'], 'missing_copy')
        self.assertEqual(rows['extra']['status'], 'extra_copy')
        self.assertEqual(report['checked_files'], 6)
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files})

    def test_default_file_check_compares_names_and_sizes_without_reading_contents(self):
        for side, data in [('left', b'AAAA'), ('right', b'BBBB')]:
            self.put(side, 'Folder/same-size', data)
            self.put(side, 'Folder/empty', b'')
        self.put('left', 'Folder/size', b'x')
        self.put('right', 'Folder/size', b'xx')
        self.put('left', 'Folder/old-name', b'abc')
        self.put('right', 'Folder/new-name', b'abc')
        folders, _ = self.run_job()
        original_open = os.open

        def directory_only(path, flags, **kwargs):
            self.assertTrue(flags & os.O_DIRECTORY, 'Name/size must never open a regular file')
            return original_open(path, flags, **kwargs)

        with patch('media_manager.comparison.os.open', side_effect=directory_only), \
                patch('media_manager.paired_comparison.os.read', side_effect=AssertionError('no content reads')):
            report, rows = self.run_job('files', folders['id'])
        self.assertEqual(report['method'], 'size')
        self.assertEqual(report['hashed_bytes'], 0)
        self.assertEqual(rows['Folder/same-size']['status'], 'same_size')
        self.assertEqual(rows['Folder/empty']['status'], 'same_size')
        self.assertNotIn('digest', rows['Folder/same-size']['left'])
        self.assertEqual(rows['Folder/size']['status'], 'size_different')
        self.assertEqual(rows['Folder/old-name']['status'], 'missing_copy')
        self.assertEqual(rows['Folder/new-name']['status'], 'extra_copy')
        self.assertEqual(rows['Folder']['attention_count'], 3)
        self.assertEqual(rows['Folder']['file_attention_count'], 3)

    def test_difference_pages_keep_only_differences_and_their_parent_folders(self):
        for side in ('left', 'right'):
            self.put(side, 'Album/Trips/same', b'abc')
            self.put(side, 'Matching/file', b'abc')
        self.put('left', 'Album/Trips/changed', b'a')
        self.put('right', 'Album/Trips/changed', b'aa')
        self.put('right', 'Extra/file')
        folders, _ = self.run_job()
        report, _ = self.run_job('files', folders['id'])
        pages = [self.pairs.rows(report['id'], offset=i, limit=2, differences_only=True) for i in (0, 2, 4)]
        paths = [r['path'] for page in pages for r in page['rows']]
        self.assertEqual(paths, ['Album', 'Album/Trips', 'Album/Trips/changed', 'Extra', 'Extra/file'])
        self.assertTrue(all(page['total'] == 5 for page in pages))
        self.assertGreater(report['row_count'], 5)

    def test_matching_files_leave_no_difference_rows_for_both_methods(self):
        for side in ('left', 'right'):
            self.put(side, 'Folder/Sub/file')
        folders, _ = self.run_job()
        for method in ('size', 'sha256'):
            report, _ = self.run_job('files', folders['id'], method=method)
            self.assertEqual(self.pairs.rows(report['id'], differences_only=True)['rows'], [])
            self.assertEqual(self.pairs.rows(report['id'], differences_only=True)['total'], 0)

    def test_upgrade_preserves_old_reports_as_sha256(self):
        folders, _ = self.run_job()
        old, _ = self.run_job('files', folders['id'], method='sha256')
        with self.storage.connect() as db:
            db.execute('ALTER TABLE paired_jobs DROP COLUMN method')
        reopened = PairedComparisonCatalog(self.storage, self.copies)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.job(old['id'])['method'], 'sha256')
        new = reopened.create(self.location['id'], 'files', folders['id'], background=False)
        self.assertEqual(new['method'], 'size')

    def test_full_stage_requires_finished_folder_check_for_same_pair(self):
        with self.assertRaises(KeyError):
            self.pairs.create(self.location['id'], 'files', None)
        pending = self.pairs.create(self.location['id'], background=False)
        with self.assertRaises(ValueError):
            self.pairs.create(self.location['id'], 'files', pending['id'])

    def test_failed_directory_does_not_turn_unknown_data_into_absence(self):
        self.put('left', 'Known/Sub/a')
        self.put('right', 'Known/Sub/a')
        from media_manager.paired_comparison import open_readonly

        def unreadable(volume, path, **kwargs):
            if volume['id'] == 'copy' and path == 'Backup/Known':
                raise PermissionError('denied')
            return open_readonly(volume, path, **kwargs)

        with patch('media_manager.paired_comparison.open_readonly', side_effect=unreadable):
            report, rows = self.run_job()
        self.assertEqual(rows['Known']['status'], 'unverified')
        self.assertEqual(rows['Known/Sub']['status'], 'unverified')
        self.assertGreater(report['errors'], 0)

    def test_symlinks_and_special_files_are_not_followed_and_type_conflicts_are_visible(self):
        self.put('left', 'Conflict/inside')
        self.put('right', 'Conflict', b'file')
        outside = self.root/'outside'
        outside.mkdir()
        (self.main/'Original/Link').symlink_to(outside, target_is_directory=True)
        os.mkfifo(self.copy/'Backup/FIFO')
        folders, rows = self.run_job()
        self.assertEqual(rows['Conflict']['status'], 'conflict')
        _, full = self.run_job('files', folders['id'])
        self.assertEqual(full['Link']['status'], 'skipped')
        self.assertEqual(full['FIFO']['status'], 'skipped')

    def test_extra_copy_decisions_are_records_and_do_not_change_disks(self):
        extra = self.put('right', 'Unique/keep')
        report, rows = self.run_job()
        for action in ('keep', 'add_main', 'move', 'remove'):
            self.pairs.decide(report['id'], 'Unique', action)
            row = next(r for r in self.pairs.rows(report['id'])['rows'] if r['path'] == 'Unique')
            self.assertEqual(row['decision'], action)
            self.assertEqual(extra.read_bytes(), b'data')
            self.assertFalse((self.main/'Original/Unique').exists())
        self.pairs.decide(report['id'], 'Unique', None)
        self.assertIsNone(self.pairs.rows(report['id'])['rows'][0]['decision'])
        with self.assertRaises(ValueError):
            self.pairs.decide(report['id'], '../outside', 'remove')

    def test_file_changed_while_hashing_is_unverified(self):
        self.put('left', 'file', b'A'*1024)
        right = self.put('right', 'file', b'A'*1024)
        folders, _ = self.run_job()
        original_read = os.read
        changed = False

        def change_after_read(descriptor, size):
            nonlocal changed
            chunk = original_read(descriptor, size)
            if chunk and not changed:
                right.write_bytes(b'B'*1024)
                changed = True
            return chunk

        with patch('media_manager.paired_comparison.os.read', side_effect=change_after_read):
            _, rows = self.run_job('files', folders['id'], method='sha256')
        self.assertEqual(rows['file']['status'], 'unverified')

    def test_folder_decisions_inherit_and_survive_the_file_stage(self):
        self.put('right', 'Unique/Sub/file')
        folders, _ = self.run_job()
        self.pairs.decide(folders['id'], 'Unique', 'keep')
        rows = {r['path']: r for r in self.pairs.rows(folders['id'])['rows']}
        self.assertEqual(rows['Unique/Sub']['decision'], 'keep')
        self.assertEqual(rows['Unique/Sub']['decision_from'], 'Unique')
        files, rows = self.run_job('files', folders['id'])
        self.assertEqual(rows['Unique/Sub/file']['decision'], 'keep')
        self.pairs.decide(files['id'], 'Unique/Sub', 'add_main')
        rows = {r['path']: r for r in self.pairs.rows(files['id'])['rows']}
        self.assertEqual(rows['Unique/Sub/file']['decision'], 'add_main')
        self.assertEqual(rows['Unique']['decision'], 'keep')
        self.pairs.decide(files['id'], 'Unique/Sub', None)
        self.assertEqual(self.pairs.rows(files['id'])['rows'][-1]['decision'], 'keep')

    def test_offline_side_is_unknown_and_interrupted_jobs_can_be_resumed(self):
        self.put('left', 'Folder/file')
        self.mounted.pop()
        report, rows = self.run_job()
        self.assertEqual(rows['Folder']['status'], 'unverified')
        self.assertGreater(report['errors'], 0)
        self.assertIn('right', report['root_errors'])
        with self.storage.connect() as db:
            db.execute("UPDATE paired_jobs SET state='running' WHERE id=?", (report['id'],))
        reopened = PairedComparisonCatalog(self.storage, self.copies)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.job(report['id'])['state'], 'paused')
        self.assertEqual(reopened.rows(report['id'])['rows'][0]['status'], 'unverified')

    def test_pause_resume_restart_and_saved_results(self):
        for side in ('left', 'right'):
            self.put(side, 'Folder/file', b'x'*2048)
        folders, _ = self.run_job()
        job = self.pairs.create(self.location['id'], 'files', folders['id'], method='sha256', background=False)
        read = os.read

        def stop_after_chunk(descriptor, size):
            chunk = read(descriptor, size)
            self.pairs._stop.set()
            return chunk

        with patch('media_manager.paired_comparison.os.read', side_effect=stop_after_chunk):
            self.pairs.run(job['id'])
        self.assertEqual(self.pairs.job(job['id'])['state'], 'paused')
        self.pairs._stop.clear()
        self.pairs.run(job['id'])
        reopened = PairedComparisonCatalog(self.storage, self.copies)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.job(job['id'])['state'], 'completed')
        self.assertEqual(reopened.rows(job['id'])['rows'][-1]['status'], 'same')


if __name__ == '__main__':
    unittest.main()
