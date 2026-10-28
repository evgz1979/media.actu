from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from media_manager.storage import StorageCatalog, discover_volumes


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.volume = self.root / 'volume'
        (self.volume / 'Фотографии' / 'пустая').mkdir(parents=True)
        (self.volume / 'Фотографии' / 'notes.txt').write_bytes(b'original document')
        (self.volume / 'archive.zip').write_bytes(b'original archive')
        self.mounted = [{'id': 'disk-one', 'name': 'Disk', 'kind': 'external', 'mount_path': str(self.volume)}]
        self.catalog = StorageCatalog(self.root / 'app' / 'storage.sqlite3', lambda: self.mounted)
        self.catalog.refresh(True)

    def test_lists_all_types_and_empty_directories_without_writing_originals(self):
        def state():
            return {str(p.relative_to(self.volume)): (p.lstat().st_mtime_ns, p.lstat().st_size, hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None) for p in [self.volume, *self.volume.rglob('*')]}
        before = state()
        root = self.catalog.directory('disk-one')
        self.assertEqual([e['name'] for e in root['entries']], ['Фотографии', 'archive.zip'])
        nested = self.catalog.directory('disk-one', 'Фотографии')
        self.assertEqual([e['name'] for e in nested['entries']], ['пустая', 'notes.txt'])
        self.assertEqual(self.catalog.directory('disk-one', 'Фотографии/пустая')['entries'], [])
        self.catalog.annotate('disk-one', 'Фотографии', {'role': 'primary', 'purpose': 'media'})
        self.assertEqual(state(), before)

    def test_disconnected_tree_and_roles_survive_restart(self):
        self.catalog.directory('disk-one')
        self.catalog.directory('disk-one', 'Фотографии')
        self.catalog.annotate('disk-one', '', {'role': 'primary', 'purpose': 'mixed'})
        self.mounted.clear()
        reopened = StorageCatalog(self.catalog.database, lambda: [])
        with patch.object(reopened, '_read_directory', side_effect=AssertionError('must not read offline volume')):
            root = reopened.directory('disk-one')
            self.assertTrue(root['cached'])
            self.assertEqual(root['volume']['availability'], 'offline')
            self.assertEqual(len(root['entries']), 2)
            self.assertEqual(reopened.directory('disk-one', 'Фотографии')['entries'][0]['name'], 'пустая')
            self.assertEqual(reopened.directory('disk-one', 'not-opened')['scanned_at'], None)
        self.assertEqual(root['metadata']['effective']['role'], 'primary')

    def test_new_disk_at_same_mount_path_does_not_inherit_roles_or_snapshots(self):
        self.catalog.directory('disk-one')
        self.catalog.annotate('disk-one', '', {'role': 'primary'})
        self.mounted = [{**self.mounted[0], 'id': 'different-uuid'}]
        result = self.catalog.refresh(True)
        old = next(v for v in result['volumes'] if v['id'] == 'disk-one')
        new = next(v for v in result['volumes'] if v['id'] == 'different-uuid')
        self.assertEqual(old['availability'], 'offline')
        self.assertEqual(new['metadata']['effective']['role'], '')
        self.assertIsNone(self.catalog.directory('different-uuid', refresh=False)['scanned_at'])

    def test_directory_refresh_rechecks_identity_even_within_discovery_cache(self):
        self.catalog.directory('disk-one')
        self.mounted = [{**self.mounted[0], 'id': 'another-disk'}]
        cached = self.catalog.directory('disk-one')
        self.assertTrue(cached['cached'])
        self.assertEqual(cached['volume']['availability'], 'offline')

    def test_mount_replaced_between_discovery_and_open_preserves_snapshot(self):
        self.catalog.directory('disk-one')
        self.mounted[0]['device'] = -1
        cached = self.catalog.directory('disk-one')
        self.assertTrue(cached['cached'])
        self.assertIn('заменён', cached['error'])

    def test_roles_inherit_and_can_be_cleared_or_overridden(self):
        self.catalog.directory('disk-one')
        self.catalog.directory('disk-one', 'Фотографии')
        self.catalog.annotate('disk-one', '', {'role': 'primary', 'purpose': 'media', 'no_duplicate': True})
        inherited = self.catalog.metadata('disk-one', 'Фотографии/пустая')
        self.assertEqual(inherited['effective']['role'], 'primary')
        self.assertEqual(inherited['inherited_from']['role'], '')
        self.catalog.annotate('disk-one', 'Фотографии', {'role': 'copy', 'purpose': '', 'no_duplicate': False})
        overridden = self.catalog.metadata('disk-one', 'Фотографии/пустая')
        self.assertEqual(overridden['effective']['role'], 'copy')
        self.assertEqual(overridden['effective']['purpose'], '')
        self.assertFalse(overridden['effective']['no_duplicate'])
        self.assertEqual(overridden['inherited_from']['role'], 'Фотографии')
        self.catalog.annotate('disk-one', 'Фотографии', {'role': None})
        self.assertEqual(self.catalog.metadata('disk-one', 'Фотографии')['effective']['role'], 'primary')

    def test_rejects_traversal_symlinks_and_roles_for_arbitrary_paths(self):
        (self.volume / 'link').symlink_to(self.root, target_is_directory=True)
        snapshot = self.catalog.directory('disk-one')
        self.assertEqual(next(e for e in snapshot['entries'] if e['name'] == 'link')['kind'], 'symlink')
        for path in ['../outside', '/etc', 'a/../../outside', '\x00']:
            with self.assertRaises(ValueError):
                self.catalog.directory('disk-one', path)
        self.assertIsNotNone(self.catalog.directory('disk-one', 'link')['error'])
        with self.assertRaises(ValueError):
            self.catalog.annotate('disk-one', 'archive.zip', {'role': 'copy'})
        with self.assertRaises(ValueError):
            self.catalog.annotate('disk-one', 'imaginary', {'role': 'copy'})

    def test_read_failure_preserves_last_successful_snapshot(self):
        first = self.catalog.directory('disk-one')
        with patch.object(self.catalog, '_read_directory', side_effect=PermissionError('denied')):
            failed = self.catalog.directory('disk-one')
        self.assertTrue(failed['cached'])
        self.assertIsNotNone(failed['error'])
        self.assertEqual(first['scanned_at'], failed['scanned_at'])
        self.assertEqual(first['entries'], failed['entries'])

    def test_discovery_failure_is_unknown_not_offline(self):
        self.catalog.discover = lambda: (_ for _ in ()).throw(OSError('mount failed'))
        result = self.catalog.refresh(True)
        self.assertEqual(result['volumes'][0]['availability'], 'unknown')
        self.assertIsNotNone(result['error'])

    def test_network_identity_ignores_username_and_mount_point(self):
        def discovery(account, mount):
            output = f'//{account}@nas.local/Media-copy01 on /Volumes/{mount} (smbfs, nodev, nosuid)\n'
            with patch('media_manager.storage.subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout=output)), patch('media_manager.storage.os.stat') as mock_stat:
                mock_stat.return_value.st_dev = 42
                return discover_volumes()[0]
        first, second = discovery('alice', 'Media-copy01'), discovery('bob', 'Media-copy01-1')
        self.assertEqual(first['id'], second['id'])
        self.assertNotIn('alice', str(first))


if __name__ == '__main__':
    unittest.main()
