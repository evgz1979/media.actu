from __future__ import annotations

import hashlib
import os
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from media_manager.comparison import ComparisonCatalog, open_readonly, sqlite_file_identifier
from media_manager.storage import StorageCatalog


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source, self.target, self.second = [self.root / name for name in ('usb', 'nas-one', 'nas-two')]
        for folder in (self.source, self.target, self.second):
            folder.mkdir()
        self.mounted = [dict(id=name, name=name, kind='external', mount_path=str(folder), device=folder.stat().st_dev)
                        for name, folder in [('usb', self.source), ('nas', self.target), ('copy', self.second)]]
        self.storage = StorageCatalog(self.root / 'app' / 'storage.sqlite3', lambda: self.mounted)
        self.storage.refresh(True)
        self.comparison = ComparisonCatalog(self.storage)
        self.addCleanup(self.comparison.close)

    @staticmethod
    def put(root, path, data=b'data'):
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def run_job(self, *, targets=None, source_path='', reuse_index=True):
        job = self.comparison.create(dict(volume_id='usb', path=source_path), targets or [dict(volume_id='nas')],
                                     background=False, reuse_index=reuse_index)
        self.comparison.run(job['id'])
        result = self.comparison.job(job['id'])
        self.assertEqual(result['state'], 'completed', result['message'])
        self.assertEqual(result['mode'], 'names')
        self.assertEqual(result['hashed_bytes'], 0)
        return result

    def detail(self, job, path):
        return self.comparison.detail(job['id'], path)

    def test_names_match_even_when_content_size_and_parent_location_differ(self):
        self.put(self.source, 'Album/photo.jpg', b'A')
        self.put(self.target, 'Private/Album/photo.jpg', b'entirely different data')
        job = self.run_job()
        self.assertEqual(self.detail(job, 'Album/photo.jpg')['entry']['status'], 'names_found')
        match = self.detail(job, 'Album/photo.jpg')['matches'][0]
        self.assertEqual(match['path'], 'Private/Album/photo.jpg')
        self.assertTrue(match['same_folder'])
        self.assertIsNone(self.detail(job, 'Album/photo.jpg')['entry']['digest'])
        self.assertEqual(self.detail(job, 'Album')['entry']['status'], 'names_found')

    def test_same_content_with_different_name_is_not_a_name_match(self):
        self.put(self.source, 'one.jpg', b'same bytes')
        self.put(self.target, 'renamed.jpg', b'same bytes')
        self.assertEqual(self.run_job()['counts'], {'names_missing': 1})

    def test_same_filename_in_other_folder_is_separate_status(self):
        self.put(self.source, 'Album/photo.jpg')
        self.put(self.target, 'Different/photo.jpg')
        job = self.run_job()
        detail = self.detail(job, 'Album/photo.jpg')
        self.assertEqual(detail['entry']['status'], 'other_folder')
        self.assertFalse(detail['matches'][0]['same_folder'])
        self.assertEqual(self.detail(job, 'Album')['entry']['status'], 'names_missing')

    def test_empty_directories_are_compared_and_file_directory_types_stay_distinct(self):
        (self.source / 'empty').mkdir()
        (self.target / 'nested' / 'empty').mkdir(parents=True)
        self.put(self.source, 'same-name')
        (self.target / 'same-name').mkdir()
        job = self.run_job()
        self.assertEqual(self.detail(job, 'empty')['entry']['status'], 'names_found')
        self.assertEqual(self.detail(job, 'same-name')['entry']['status'], 'names_missing')
        self.assertEqual(self.detail(job, 'empty')['matches'][0]['path'], 'nested/empty')

    def test_unicode_and_case_names_are_normalized(self):
        self.put(self.source, 'ФОТО/Caf\u00e9.JPG')
        self.put(self.target, 'фото/Cafe\u0301.jpg')
        job = self.run_job()
        self.assertEqual(self.detail(job, 'ФОТО/Caf\u00e9.JPG')['entry']['status'], 'names_found')

    def test_never_reads_file_contents_or_requests_file_stat(self):
        self.put(self.source, 'Album/a')
        self.put(self.target, 'Album/a', b'different size and contents')
        original_scandir, original_open = os.scandir, os.open
        class Entry:
            def __init__(self, entry):
                self.entry, self.name = entry, entry.name
            def __getattr__(self, key):
                return getattr(self.entry, key)
            def stat(self, **kwargs):
                raise AssertionError('file stat must not be requested')
        class Scandir:
            def __init__(self, descriptor):
                self.iterator = original_scandir(descriptor)
            def __enter__(self):
                return (Entry(e) for e in self.iterator.__enter__())
            def __exit__(self, *args):
                return self.iterator.__exit__(*args)
        def directory_open(path, flags, **kwargs):
            self.assertTrue(flags & os.O_DIRECTORY, 'a file must never be opened')
            return original_open(path, flags, **kwargs)
        with patch('media_manager.comparison.os.scandir', side_effect=Scandir), \
                patch('media_manager.comparison.os.open', side_effect=directory_open), \
                patch('media_manager.comparison.os.read', side_effect=AssertionError('must not read bytes')):
            job = self.run_job()
        self.assertEqual(self.detail(job, 'Album/a')['entry']['status'], 'names_found')

    def test_complete_lists_are_reused_offline_without_filesystem_access(self):
        self.put(self.source, 'Album/a')
        self.put(self.target, 'Album/a')
        first = self.run_job()
        self.mounted.clear()
        with patch('media_manager.comparison.open_readonly', side_effect=AssertionError('cached list must not open disk')), \
                patch('media_manager.comparison.os.scandir', side_effect=AssertionError('cached list must not scan')), \
                patch.object(self.storage, 'refresh', side_effect=AssertionError('cached lists need no discovery')):
            second = self.run_job()
        self.assertEqual(second['counts'], first['counts'])
        self.assertTrue(all(s['reused_from'] for s in second['scans']))
        self.assertEqual([s['finished_at'] for s in first['scans']], [s['finished_at'] for s in second['scans']])
        self.assertEqual(self.comparison.job(first['id'])['counts'], first['counts'])

    def test_refresh_lists_is_explicit_and_reused_lists_keep_their_dates(self):
        self.put(self.source, 'a')
        self.put(self.target, 'a')
        self.run_job()
        self.put(self.source, 'arrived-later')
        cached = self.run_job()
        self.assertEqual(cached['counts'], {'names_found': 1})
        refreshed = self.run_job(reuse_index=False)
        self.assertEqual(refreshed['counts'], {'names_found': 1, 'names_missing': 1})
        self.assertTrue(all(s['reused_from'] is None for s in refreshed['scans']))

    def test_incomplete_target_prevents_absence_claim_but_keeps_matches(self):
        self.put(self.source, 'a')
        self.put(self.source, 'unique')
        self.put(self.target, 'a')
        (self.target / 'denied').mkdir()
        original = open_readonly
        def guarded(volume, path, **kwargs):
            if volume['id'] == 'nas' and path == 'denied':
                raise PermissionError('denied')
            return original(volume, path, **kwargs)
        with patch('media_manager.comparison.open_readonly', side_effect=guarded):
            job = self.run_job()
        self.assertEqual(job['counts'], {'names_found': 1, 'unverified': 1})
        self.assertEqual(job['scans'][1]['state'], 'error')

    def test_unreadable_source_branch_is_visible_in_unverified_filter(self):
        self.put(self.source, 'parent/denied/unseen')
        original = open_readonly
        def guarded(volume, path, **kwargs):
            if volume['id'] == 'usb' and path == 'parent/denied':
                raise PermissionError('denied source')
            return original(volume, path, **kwargs)
        with patch('media_manager.comparison.open_readonly', side_effect=guarded):
            job = self.run_job()
        tree = self.comparison.tree(job['id'], status='unverified')
        self.assertEqual(tree['entries'][0]['name'], 'parent')
        branch = self.comparison.tree(job['id'], 'parent', 'unverified')['entries'][0]
        self.assertIn('denied source', branch['error'])

    def test_offline_source_without_a_complete_list_fails(self):
        self.mounted[:] = [v for v in self.mounted if v['id'] != 'usb']
        job = self.comparison.create(dict(volume_id='usb'), [dict(volume_id='nas')], background=False)
        self.comparison.run(job['id'])
        self.assertEqual(self.comparison.job(job['id'])['state'], 'failed')

    def test_legacy_resume_creates_name_job_and_preserves_old_report_and_lists(self):
        self.put(self.source, 'Album/a')
        self.put(self.target, 'Album/a')
        old = self.run_job()
        with self.storage.connect() as db:
            db.execute("UPDATE comparison_jobs SET mode='content',state='paused',phase='hash' WHERE id=?", (old['id'],))
            db.execute("UPDATE comparison_entries SET name_key='',parent_key='',error='old content read failed' WHERE kind='file'")
            db.execute("UPDATE comparison_results SET status='candidate',reason='legacy result'")
        with patch('media_manager.comparison.open_readonly', side_effect=AssertionError('reuse old inventory')):
            new = self.comparison.resume(old['id'])
            self.comparison._thread.join(5)
        report = self.comparison.job(new['id'])
        self.assertNotEqual(new['id'], old['id'])
        self.assertEqual(report['mode'], 'names')
        self.assertEqual(report['state'], 'completed', report['message'])
        self.assertEqual(self.detail(report, 'Album/a')['entry']['status'], 'names_found')
        self.assertEqual(self.comparison.job(old['id'])['mode'], 'content')
        self.assertEqual(self.comparison.job(old['id'])['counts'], {'candidate': 2})

    def test_background_pause_resume_and_single_worker(self):
        self.put(self.source, 'a')
        self.put(self.target, 'a')
        entered, release = threading.Event(), threading.Event()
        original = open_readonly
        def blocked(volume, path, **kwargs):
            entered.set()
            if not release.wait(3):
                raise TimeoutError('test wait')
            return original(volume, path, **kwargs)
        with patch('media_manager.comparison.open_readonly', side_effect=blocked):
            job = self.comparison.create(dict(volume_id='usb'), [dict(volume_id='nas')])
            try:
                self.assertTrue(entered.wait(2))
                with self.assertRaises(ValueError):
                    self.comparison.create(dict(volume_id='usb'), [dict(volume_id='nas')])
                self.comparison.pause(job['id'])
            finally:
                release.set()
                self.comparison._thread.join(3)
        self.assertEqual(self.comparison.job(job['id'])['state'], 'paused')
        self.comparison.resume(job['id'])
        self.comparison._thread.join(3)
        self.assertEqual(self.comparison.job(job['id'])['counts'], {'names_found': 1})

    def test_symlinks_special_files_and_originals_remain_untouched(self):
        self.put(self.source, 'a')
        self.put(self.target, 'a')
        (self.source / 'link').symlink_to(self.target, target_is_directory=True)
        os.mkfifo(self.source / 'pipe')
        def state():
            return {str(p): (p.lstat().st_mtime_ns, p.lstat().st_size,
                    hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() and not p.is_symlink() else None)
                    for folder in (self.source, self.target) for p in [folder, *folder.iterdir()]}
        before = state()
        self.assertEqual(self.run_job()['counts'], {'names_found': 1, 'skipped': 2})
        self.assertEqual(state(), before)
        with self.assertRaises(OSError):
            with open_readonly(self.mounted[0], 'link/a'):
                pass

    def test_name_filter_keeps_ancestors_and_paginates(self):
        self.put(self.source, '100%_folder/new')
        self.put(self.source, '100%_folder/second')
        job = self.run_job()
        tree = self.comparison.tree(job['id'], status='names_missing')
        self.assertEqual(tree['entries'][0]['name'], '100%_folder')
        nested = self.comparison.tree(job['id'], '100%_folder', 'names_missing', limit=1)
        self.assertEqual(nested['total'], 2)
        self.assertEqual(len(nested['entries']), 1)

    def test_two_target_locations_and_directory_matches_are_explained(self):
        self.put(self.source, 'Album/a')
        self.put(self.target, 'Private/Album/a')
        self.put(self.second, 'Backup/Album/a')
        job = self.run_job(targets=[dict(volume_id='nas'), dict(volume_id='copy')])
        self.assertEqual({m['volume_name'] for m in self.detail(job, 'Album/a')['matches']}, {'nas', 'copy'})
        self.assertEqual(len(self.detail(job, 'Album')['matches']), 2)

    def test_directory_list_cache_is_available_in_explorer_offline(self):
        self.put(self.source, 'Album/a')
        self.run_job()
        self.mounted.clear()
        cached = self.storage.directory('usb', 'Album')
        self.assertTrue(cached['cached'])
        self.assertEqual(cached['entries'][0]['name'], 'a')

    def test_scopes_do_not_reuse_another_directorys_list(self):
        self.put(self.source, 'Album/a')
        self.put(self.target, 'Album/a')
        self.run_job(source_path='Album')
        full = self.run_job()
        self.assertIsNone(full['scans'][0]['reused_from'])
        self.assertEqual(full['counts'], {'names_found': 2})

    def test_rejects_overlap_and_traversal_and_checks_mount_identity(self):
        for targets in ([dict(volume_id='usb')], [dict(volume_id='nas', path='../outside')]):
            with self.assertRaises(ValueError):
                self.comparison.create(dict(volume_id='usb'), targets, background=False)
        with self.assertRaises(OSError):
            with open_readonly(dict(self.mounted[0], device=-1), '', directory=True):
                pass

    def test_restart_leaves_interrupted_job_paused(self):
        job = self.comparison.create(dict(volume_id='usb'), [dict(volume_id='nas')], background=False)
        with self.storage.connect() as db:
            db.execute("UPDATE comparison_jobs SET state='running' WHERE id=?", (job['id'],))
        reopened = ComparisonCatalog(self.storage)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.job(job['id'])['state'], 'paused')

    def test_legacy_large_identifiers_still_roundtrip_without_loss(self):
        values = [(1 << 63) - 1, 9486355987990956268, 15956706424471021216]
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE ids(value INTEGER)')
            db.executemany('INSERT INTO ids VALUES (?)', [(sqlite_file_identifier(v),) for v in values])
            self.assertEqual([r[0] for r in db.execute('SELECT value FROM ids')], [sqlite_file_identifier(v) for v in values])


if __name__ == '__main__':
    unittest.main()
