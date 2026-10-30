from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest

from media_manager.copies import CopyCatalog
from media_manager.storage import StorageCatalog


class CopyCatalogTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.mounted = []
        for identity in ('main-disk', 'target-disk', 'usb-disk'):
            path = self.root / identity
            path.mkdir()
            self.mounted.append({'id': identity, 'name': identity, 'mount_path': str(path),
                                 'kind': 'external', 'removable': identity == 'usb-disk'})
        for volume, folders in [('main-disk', ['Photos/Sub', 'Photos2', 'Projects']),
                                ('target-disk', ['Backups/Photos', 'Other', 'Cloud', 'D0', 'D1', 'D2', 'D3']),
                                ('usb-disk', ['Cold'])]:
            for folder in folders:
                (self.root / volume / folder).mkdir(parents=True, exist_ok=True)
        (self.root / 'main-disk/Photos/Sub/original.txt').write_text('original')
        (self.root / 'target-disk/Other/keep.txt').write_text('existing copy data')
        self.storage = StorageCatalog(self.root / 'catalog/storage.sqlite3', lambda: self.mounted)
        for volume in self.mounted:
            self.storage.directory(volume['id'])
        self.storage.directory('main-disk', 'Photos')
        self.storage.directory('target-disk', 'Backups')
        self.copies = CopyCatalog(self.storage)

    def test_numbers_span_copy_types_and_labels_inherit_with_path_boundaries(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.assertEqual(main['main']['label'], '00-main')
        for volume, path, kind in [('target-disk', 'Backups/Photos', 'copy'),
                                   ('target-disk', 'Other', 'copy'), ('usb-disk', 'Cold', 'cold'),
                                   ('target-disk', 'Cloud', 'cloud')]:
            group = self.copies.add_copy(main['id'], volume, path, kind)
        self.assertEqual([copy['label'] for copy in group['copies']],
                         ['01-copy', '02-copy', '03-copy-cold', '04-copy-cloud'])
        inherited = self.storage.metadata('main-disk', 'Photos/Sub/original.txt')['copy']
        self.assertEqual(inherited['label'], '00-main')
        self.assertEqual(inherited['inherited_from'], 'Photos')
        self.assertFalse(inherited['is_root'])
        self.assertIsNone(self.storage.metadata('main-disk', 'Photos2')['copy'])
        snapshot = self.storage.directory('main-disk', 'Photos', refresh=False)
        self.assertEqual(snapshot['entries'][0]['metadata']['copy']['label'], '00-main')
        self.assertEqual(self.storage.metadata('usb-disk', 'Cold/Year/Month')['copy']['label'], '03-copy-cold')
        second = self.copies.create_main('main-disk', 'Projects')
        self.assertEqual(second['next_number'], 1)
        self.assertNotEqual(second['id'], main['id'])

    def test_registration_changes_no_files_and_does_not_require_fresh_directory_reads(self):
        def files():
            return {str(path): (path.stat().st_mtime_ns, path.read_bytes())
                    for volume in self.mounted for path in Path(volume['mount_path']).rglob('*') if path.is_file()}
        before = files()
        from unittest.mock import patch
        with patch.object(self.storage, '_read_directory', side_effect=AssertionError('use known folder paths')):
            main = self.copies.create_main('main-disk', 'Photos')
            self.copies.add_copy(main['id'], 'target-disk', 'Other')
        self.assertEqual(files(), before)

    def test_idempotent_registration_does_not_allocate_extra_copy_numbers(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.assertEqual(self.copies.create_main('main-disk', 'Photos')['id'], main['id'])
        self.copies.add_copy(main['id'], 'target-disk', 'Other')
        repeated = self.copies.add_copy(main['id'], 'target-disk', 'Other')
        self.assertEqual(len(repeated['copies']), 1)
        self.assertEqual(repeated['next_number'], 2)

    def test_rejects_files_unknown_paths_and_unverified_disks(self):
        for path in ('', 'Photos/Sub/original.txt', 'Unknown', '../outside', '/etc', '\x00'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.copies.create_main('main-disk', path)
        self.mounted[2]['identity_status'] = 'unverified'
        self.storage.refresh(True)
        with self.assertRaises(ValueError):
            self.copies.create_main('usb-disk', 'Cold')
        self.assertEqual(self.copies.groups(), [])

    def test_overlapping_roots_cannot_give_descendants_conflicting_labels(self):
        main = self.copies.create_main('main-disk', 'Photos')
        with self.assertRaisesRegex(ValueError, 'назначения'):
            self.copies.add_copy(main['id'], 'target-disk', '')
        for action in [lambda: self.copies.create_main('main-disk', 'Photos/Sub'),
                       lambda: self.copies.add_copy(main['id'], 'main-disk', 'Photos/Sub')]:
            with self.assertRaisesRegex(ValueError, 'пересекается'):
                action()
        self.copies.add_copy(main['id'], 'target-disk', 'Backups/Photos')
        with self.assertRaisesRegex(ValueError, 'пересекается'):
            self.copies.create_main('target-disk', 'Backups')
        self.assertEqual(self.copies.group(main['id'])['next_number'], 2)

    def test_offline_locations_and_changed_mount_names_preserve_relationships_after_restart(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.copies.add_copy(main['id'], 'usb-disk', 'Cold', 'cold')
        usb = self.mounted.pop()
        reopened = StorageCatalog(self.storage.database, lambda: self.mounted)
        copies = CopyCatalog(reopened)
        location = copies.group(main['id'])['copies'][0]
        self.assertEqual(location['availability'], 'offline')
        self.assertEqual(location['label'], '01-copy-cold')
        usb.update(name='Different share name')
        self.mounted.append(usb)
        reopened.refresh(True)
        restored = copies.group(main['id'])['copies'][0]
        self.assertEqual(restored['id'], location['id'])
        self.assertEqual(restored['availability'], 'online')
        self.assertEqual(restored['volume_name'], 'Different share name')

    @staticmethod
    def number_snapshot(group):
        return [{key: copy[key] for key in ('id', 'kind', 'number')} for copy in group['copies']]

    def test_middle_deletion_requires_confirmed_renumbering_before_adding(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.copies.add_copy(main['id'], 'target-disk', 'Other')
        group = self.copies.add_copy(main['id'], 'usb-disk', 'Cold', 'cold')
        first, second = group['copies']
        edited = self.copies.change_kind(first['id'], 'cloud')
        self.assertEqual(edited['copies'][0]['label'], '01-copy-cloud')
        self.copies.remove_copy(first['id'])
        group = self.copies.group(main['id'])
        self.assertIsNone(group['next_number'])
        self.assertEqual(group['copies'][0]['number'], 2)
        self.assertEqual(group['numbering_changes'], [dict(id=second['id'], from_label='02-copy-cold',
                                                         to_label='01-copy-cold', number=1)])
        with self.assertRaisesRegex(ValueError, 'пропуски'):
            self.copies.add_copy(main['id'], 'target-disk', 'Other')
        normalized = self.copies.renumber_copies(main['id'], self.number_snapshot(group))
        self.assertEqual(normalized['next_number'], 2)
        self.assertEqual(normalized['numbering_changes'], [])
        self.assertEqual(normalized['copies'][0]['id'], second['id'])
        self.assertEqual(normalized['copies'][0]['path'], second['path'])
        self.assertEqual(normalized['copies'][0]['kind'], second['kind'])
        self.assertEqual(self.storage.metadata('usb-disk', 'Cold/Year')['copy']['label'], '01-copy-cold')
        group = self.copies.add_copy(main['id'], 'target-disk', 'Other')
        self.assertEqual([copy['number'] for copy in group['copies']], [1, 2])
        self.assertEqual(group['copies'][0]['id'], second['id'])
        self.copies.remove_group(main['id'])
        self.assertIsNone(self.storage.metadata('usb-disk', 'Cold')['copy'])
        self.assertEqual(self.copies.groups(), [])
        self.assertTrue((self.root / 'target-disk/Other/keep.txt').is_file())

    def test_last_deletion_reuses_number_and_ignores_legacy_counter(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.copies.add_copy(main['id'], 'target-disk', 'Other')
        second = self.copies.add_copy(main['id'], 'usb-disk', 'Cold', 'cold')['copies'][1]
        self.copies.remove_copy(second['id'])
        with self.storage.connect() as db:
            db.execute('UPDATE copy_groups SET next_number=99 WHERE id=?', (main['id'],))
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        group = reopened.group(main['id'])
        self.assertEqual(group['next_number'], 2)
        self.assertEqual(group['numbering_changes'], [])
        group = reopened.add_copy(main['id'], 'usb-disk', 'Cold', 'cold')
        self.assertEqual([c['label'] for c in group['copies']], ['01-copy', '02-copy-cold'])
        for copy in group['copies']:
            reopened.remove_copy(copy['id'])
        self.assertEqual(reopened.group(main['id'])['next_number'], 1)
        self.assertEqual(reopened.add_copy(main['id'], 'target-disk', 'Other')['copies'][0]['label'], '01-copy')

    def test_renumbering_compacts_multiple_gaps_atomically_without_changing_files(self):
        main = self.copies.create_main('main-disk', 'Photos')
        for i in range(4):
            group = self.copies.add_copy(main['id'], 'target-disk', f'D{i}')
        locations = group['copies']
        self.copies.remove_copy(locations[0]['id'])
        self.copies.remove_copy(locations[2]['id'])
        group = self.copies.group(main['id'])
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.glob('*-disk/**/*') if p.is_file()}
        normalized = self.copies.renumber_copies(main['id'], self.number_snapshot(group))
        self.assertEqual([(c['id'], c['number']) for c in normalized['copies']],
                         [(locations[1]['id'], 1), (locations[3]['id'], 2)])
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.glob('*-disk/**/*') if p.is_file()})
        with self.storage.connect() as db:
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_stale_renumbering_proposal_cannot_change_newer_links_or_types(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.copies.add_copy(main['id'], 'target-disk', 'Other')
        group = self.copies.add_copy(main['id'], 'usb-disk', 'Cold', 'cold')
        self.copies.remove_copy(group['copies'][0]['id'])
        group = self.copies.group(main['id'])
        proposal = self.number_snapshot(group)
        self.copies.change_kind(group['copies'][0]['id'], 'cloud')
        with self.assertRaisesRegex(ValueError, 'изменился'):
            self.copies.renumber_copies(main['id'], proposal)
        unchanged = self.copies.group(main['id'])
        self.assertEqual(unchanged['copies'][0]['label'], '02-copy-cloud')
        self.copies.remove_copy(group['copies'][0]['id'])
        self.copies.add_copy(main['id'], 'target-disk', 'Other')
        with self.assertRaisesRegex(ValueError, 'изменился'):
            self.copies.renumber_copies(main['id'], proposal)
        self.assertEqual(self.copies.group(main['id'])['copies'][0]['label'], '01-copy')

    def test_concurrent_registrations_allocate_unique_consecutive_numbers(self):
        main = self.copies.create_main('main-disk', 'Photos')
        other_storage = StorageCatalog(self.storage.database, lambda: self.mounted)
        catalogs = [self.copies, CopyCatalog(other_storage)]
        def add(number):
            return catalogs[number % 2].add_copy(main['id'], 'target-disk', f'D{number}')
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(add, range(4)))
        group = self.copies.group(main['id'])
        self.assertEqual([copy['number'] for copy in group['copies']], [1, 2, 3, 4])
        self.assertEqual(group['next_number'], 5)

    def test_old_volume_roles_do_not_create_main_folders_or_links(self):
        self.storage.annotate('main-disk', '', {'role': 'primary'})
        self.storage.annotate('target-disk', '', {'role': 'copy'})
        self.assertEqual(self.copies.groups(), [])
        self.assertIsNone(self.storage.metadata('main-disk', 'Photos')['copy'])

    def test_folder_labels_and_tracking_are_independent_and_survive_restart_and_disconnect(self):
        main = self.copies.create_main('main-disk', 'Photos')
        self.copies.add_copy(main['id'], 'usb-disk', 'Cold', 'cold')
        self.assertEqual((main['label'], main['tracking'], main['changed_at']), ('', False, None))
        self.copies.update_group(main['id'], {'tracking': True})
        for label in ('temporary', 'inbox', 'archive', ''):
            group = self.copies.update_group(main['id'], {'label': label})
            self.assertEqual((group['label'], group['tracking']), (label, True))
        self.copies.update_group(main['id'], {'label': 'temporary'})
        self.mounted.clear()
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        group = reopened.group(main['id'])
        self.assertEqual((group['label'], group['tracking']), ('temporary', True))
        self.assertEqual(group['main']['availability'], 'offline')
        self.assertEqual(group['copies'][0]['label'], '01-copy-cold')
        group = reopened.update_group(main['id'], {'tracking': False})
        self.assertEqual(group['label'], 'temporary')
        self.assertEqual((self.root / 'main-disk/Photos/Sub/original.txt').read_text(), 'original')

    def test_old_catalog_gets_empty_settings_and_deleted_groups_leave_no_settings(self):
        main = self.copies.create_main('main-disk', 'Photos')
        with self.storage.connect() as db:
            db.execute('DROP TABLE copy_group_settings')
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        self.assertEqual(reopened.group(main['id'])['label'], '')
        reopened.update_group(main['id'], {'label': 'archive', 'tracking': True})
        reopened.remove_group(main['id'])
        with self.storage.connect() as db:
            self.assertEqual(db.execute('SELECT * FROM copy_group_settings').fetchall(), [])

    def test_invalid_settings_cannot_modify_a_group_or_create_orphan_records(self):
        main = self.copies.create_main('main-disk', 'Photos')
        for changes in ({}, {'label': 'working'}, {'label': None}, {'tracking': None},
                        {'tracking': 'yes'}, {'tracking': 1}, {'path': 'Other'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.copies.update_group(main['id'], changes)
        with self.assertRaises(KeyError):
            self.copies.update_group('missing', {'label': 'archive'})
        group = self.copies.group(main['id'])
        self.assertEqual((group['label'], group['tracking']), ('', False))

    def test_only_tracked_groups_record_changes_and_stale_acknowledgements_preserve_new_changes(self):
        group = self.copies.create_main('main-disk', 'Photos')
        self.copies.mark_changed(group['id'])
        self.assertIsNone(self.copies.group(group['id'])['changed_at'])
        self.copies.update_group(group['id'], {'tracking': True})
        self.copies.mark_changed(group['id'])
        old = self.copies.group(group['id'])['changed_at']
        self.copies.mark_changed(group['id'])
        latest = self.copies.group(group['id'])['changed_at']
        self.assertNotEqual(old, latest)
        self.assertEqual(self.copies.acknowledge_changes(group['id'], old)['changed_at'], latest)
        self.assertIsNone(self.copies.acknowledge_changes(group['id'], latest)['changed_at'])
        self.copies.update_group(group['id'], {'tracking': False})
        self.copies.mark_changed(group['id'])
        self.assertIsNone(self.copies.group(group['id'])['changed_at'])


if __name__ == '__main__':
    unittest.main()
