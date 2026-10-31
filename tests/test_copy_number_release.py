import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from copy_groups_ui import CopyGroupsUI, sidebar_sections
from media_manager.copies import CopyCatalog
from media_manager.copy_files import MissingCopyCatalog
from media_manager.paired_comparison import PairedComparisonCatalog
from media_manager.storage import StorageCatalog
from paired_workspace_ui import PairedWorkspace
from workspace_ui import BrowserPane


class CopyNumberReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.mounted = []
        for name, folders in [('main', ['Original']), ('copy', ['Backup', 'Cloud']),
                              ('cold', ['Old', 'New', 'Other'])]:
            mount = self.root / name
            for folder in folders:
                (mount / folder).mkdir(parents=True, exist_ok=True)
            self.mounted.append(dict(id=name, name=name, kind='external', mount_path=str(mount), device=mount.stat().st_dev))
        (self.root / 'main/Original/photo.jpg').write_bytes(b'original')
        self.storage = StorageCatalog(self.root / 'data/storage.sqlite3', lambda: self.mounted)
        for volume in self.mounted:
            self.storage.directory(volume['id'])
        self.copies = CopyCatalog(self.storage)
        self.group = self.copies.create_main('main', 'Original')
        self.copies.add_copy(self.group['id'], 'copy', 'Backup')
        self.group = self.copies.add_copy(self.group['id'], 'cold', 'Old', 'cold')
        self.old = self.group['copies'][1]

    def release(self):
        self.copies.set_copy_connected(self.old['id'], False)
        return self.copies.release_copy_number(self.old['id'], self.old['number'], self.old['kind'])

    def test_reuses_number_with_a_new_identity_and_preserves_old_record_after_restart(self):
        (self.root / 'cold/Old/keep.txt').write_bytes(b'keep old files')
        before = (self.root / 'cold/Old/keep.txt').stat()
        group = self.release()
        self.assertEqual(group['next_number'], 2)
        self.assertEqual([copy['label'] for copy in group['copies']], ['01-copy'])
        archived = group['released_copies'][0]
        self.assertEqual(archived['label'], 'Прежняя 02-copy-cold')
        for key in ('id', 'volume_id', 'path', 'kind', 'number', 'created_at'):
            self.assertEqual(archived[key], self.old[key])
        self.assertFalse(archived['connected'])
        self.assertIsNone(self.storage.metadata('cold', 'Old/keep.txt')['copy'])
        group = self.copies.add_copy(group['id'], 'cold', 'New', 'cold')
        new = group['copies'][1]
        self.assertEqual(new['label'], '02-copy-cold')
        self.assertNotEqual(new['id'], self.old['id'])
        self.assertEqual(group['next_number'], 3)
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        group = reopened.group(group['id'])
        self.assertEqual(group['released_copies'][0]['id'], self.old['id'])
        self.assertEqual(group['copies'][1]['id'], new['id'])
        self.assertEqual((self.root / 'cold/Old/keep.txt').read_bytes(), b'keep old files')
        self.assertEqual((self.root / 'cold/Old/keep.txt').stat().st_mtime_ns, before.st_mtime_ns)
        with self.storage.connect() as db:
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_other_copy_numbers_stay_unchanged_when_a_middle_number_is_released(self):
        group = self.copies.add_copy(self.group['id'], 'copy', 'Cloud', 'cloud')
        third = group['copies'][2]
        group = self.release()
        self.assertEqual([c['number'] for c in group['copies']], [1, 3])
        self.assertEqual(group['numbering_changes'], [])
        self.assertEqual(group['next_number'], 2)
        group = self.copies.add_copy(group['id'], 'cold', 'New', 'cold')
        self.assertEqual([c['number'] for c in group['copies']], [1, 2, 3])
        self.assertEqual(group['copies'][2]['id'], third['id'])
        self.assertEqual(group['released_copies'][0]['number'], 2)

    def test_old_reports_and_completed_copy_journal_are_not_inherited_by_the_new_copy(self):
        pairs = PairedComparisonCatalog(self.storage, self.copies)
        transfers = MissingCopyCatalog(pairs)
        self.addCleanup(pairs.close)
        folders = pairs.create(self.old['id'], background=False)
        pairs.run(folders['id'])
        files = pairs.create(self.old['id'], 'files', folders['id'], background=False)
        pairs.run(files['id'])
        plan = transfers.plan(files['id'])
        transfers.start(plan['id'], background=False)
        transfers.run(plan['id'], recheck=False)
        self.assertEqual(transfers.job(plan['id'])['state'], 'completed')
        rows = pairs.rows(files['id'])
        old_report = pairs.job(files['id'])
        paused = pairs.create(self.old['id'], background=False)
        self.release()
        group = self.copies.add_copy(self.group['id'], 'cold', 'New', 'cold')
        new = group['copies'][1]
        self.assertEqual(pairs.job(files['id']), old_report)
        self.assertEqual(pairs.rows(files['id']), rows)
        self.assertEqual(transfers.job(plan['id'])['copy_id'], self.old['id'])
        self.assertEqual(pairs.jobs(new['id']), [])
        self.assertEqual(transfers.incomplete(new['id']), {})
        with self.assertRaisesRegex(ValueError, 'история'):
            pairs.create(self.old['id'], background=False)
        with self.assertRaisesRegex(ValueError, 'история'):
            pairs.resume(paused['id'])

    def test_can_restore_only_when_both_number_and_folder_are_free(self):
        self.release()
        group = self.copies.set_copy_connected(self.old['id'], True)
        self.assertEqual(group['released_copies'], [])
        self.assertEqual(group['copies'][1]['id'], self.old['id'])
        self.release()
        self.copies.add_copy(group['id'], 'cold', 'New', 'cold')
        with self.assertRaisesRegex(ValueError, '02.*занят'):
            self.copies.set_copy_connected(self.old['id'], True)
        self.assertEqual(len(self.copies.group(group['id'])['released_copies']), 1)
        self.assertFalse(self.copies.set_copy_connected(self.old['id'], False)['released_copies'][0]['connected'])

    def test_released_folder_can_be_rebound_without_inheriting_the_old_identity(self):
        self.release()
        group = self.copies.add_copy(self.group['id'], 'cold', 'Old', 'cold')
        self.assertEqual(group['copies'][1]['number'], 2)
        self.assertNotEqual(group['copies'][1]['id'], self.old['id'])
        self.assertEqual(group['released_copies'][0]['id'], self.old['id'])

    def test_restoration_rejects_a_folder_now_used_by_another_group(self):
        self.release()
        other = self.copies.create_main('copy', 'Cloud')
        self.copies.add_copy(other['id'], 'cold', 'Old', 'cold')
        with self.assertRaisesRegex(ValueError, 'пересекается'):
            self.copies.set_copy_connected(self.old['id'], True)
        self.assertEqual(self.copies.group(self.group['id'])['released_copies'][0]['id'], self.old['id'])

    def test_active_main_and_stale_menu_snapshots_cannot_release_a_number(self):
        for identifier, number, kind in [(self.old['id'], 2, 'cold'), (self.group['main']['id'], 0, 'main')]:
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                self.copies.release_copy_number(identifier, number, kind)
        self.copies.set_copy_connected(self.old['id'], False)
        for number, kind in [(3, 'cold'), (2, 'cloud')]:
            with self.subTest(number=number, kind=kind), self.assertRaisesRegex(ValueError, 'изменилась'):
                self.copies.release_copy_number(self.old['id'], number, kind)
        self.assertEqual(self.copies.group(self.group['id'])['released_copies'], [])

    def test_release_is_idempotent_and_group_reconnection_does_not_restore_it(self):
        self.release()
        group = self.copies.release_copy_number(self.old['id'], 2, 'cold')
        timestamp = group['released_copies'][0]['released_at']
        self.copies.set_group_connected(group['id'], False)
        group = self.copies.set_group_connected(group['id'], True)
        self.assertEqual(group['released_copies'][0]['released_at'], timestamp)
        self.assertFalse(group['released_copies'][0]['connected'])
        self.assertEqual(group['next_number'], 2)

    def test_concurrent_additions_reuse_the_released_number_once(self):
        self.release()
        other = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        def add(item):
            catalog, path = item
            return catalog.add_copy(self.group['id'], 'cold', path, 'cold')
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(add, [(self.copies, 'New'), (other, 'Other')]))
        group = self.copies.group(self.group['id'])
        self.assertEqual([c['number'] for c in group['copies']], [1, 2, 3])
        self.assertEqual(len({c['id'] for c in group['copies']}), 3)
        self.assertEqual(group['released_copies'][0]['id'], self.old['id'])

    def test_upgrade_preserves_existing_disconnections_without_releasing_any_number(self):
        self.copies.set_copy_connected(self.old['id'], False)
        with self.storage.connect() as db:
            db.execute('DROP TABLE released_copy_locations')
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        group = reopened.group(self.group['id'])
        self.assertEqual(group['released_copies'], [])
        self.assertEqual(group['copies'][1]['id'], self.old['id'])
        self.assertFalse(group['copies'][1]['connected'])
        self.assertEqual(group['next_number'], 3)

    def test_api_checks_expected_number_and_active_operations(self):
        async def exercise():
            import httpx
            with patch.dict(os.environ, {'MEDIA_ACTU_DATA_DIR': str(self.root / 'api-data')}):
                import app as core
            pairs = Mock()
            pairs.busy.return_value = False
            self.copies.set_copy_connected(self.old['id'], False)
            with patch.object(core, 'copies', self.copies), patch.object(core, 'paired_comparison', pairs):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app), base_url='http://test') as client:
                    url = '/api/storage/copy-locations/' + self.old['id'] + '/release-number'
                    self.assertEqual((await client.post(url, json={'number': '2', 'kind': 'cold'})).status_code, 422)
                    self.assertEqual((await client.post(url, json={'number': 3, 'kind': 'cold'})).status_code, 400)
                    pairs.busy.return_value = True
                    self.assertEqual((await client.post(url, json={'number': 2, 'kind': 'cold'})).status_code, 400)
                    self.assertEqual(self.copies.group(self.group['id'])['released_copies'], [])
                    pairs.busy.return_value = False
                    result = await client.post(url, json={'number': 2, 'kind': 'cold'})
                    self.assertEqual(result.status_code, 200, result.text)
                    self.assertEqual(result.json()['next_number'], 2)
                    self.assertEqual(result.json()['released_copies'][0]['id'], self.old['id'])
        asyncio.run(exercise())


class ReleasedCopyUITests(unittest.IsolatedAsyncioTestCase):
    async def test_archived_record_stays_in_disconnected_and_opens_history_without_live_folder_reads(self):
        archived = dict(id='old', number=2, number_released=True, connected=False, availability='online')
        main = dict(id='main', availability='online')
        current = dict(id='new', number=2, availability='online')
        group = dict(id='group', main=main, copies=[current], released_copies=[archived])
        active, offline, count = sidebar_sections([group])
        self.assertEqual(active[0][1], [current])
        self.assertEqual(offline[0][1], [archived])
        self.assertEqual(count, 1)
        ws = SimpleNamespace(client=nullcontext(), pair=SimpleNamespace(link=AsyncMock(), history=AsyncMock()))
        await CopyGroupsUI(ws).open_copy(group, archived)
        ws.pair.link.assert_not_awaited()
        ws.pair.history.assert_awaited_once_with(group=group, location=archived)

    async def test_history_view_rejects_queued_start_resume_and_copy_commands(self):
        ws = SimpleNamespace(request=AsyncMock())
        pair = PairedWorkspace(ws)
        pair.history_only = True
        await pair.start('folders')
        await pair.resume()
        await pair.prepare_copy()
        ws.request.assert_not_awaited()
        pane = BrowserPane.__new__(BrowserPane)
        pane.volume_id, pane.workspace = 'cold', SimpleNamespace(pair=pair)
        self.assertIsNone(pane.size_scope())

    async def test_history_view_does_not_offer_to_create_a_new_binding_from_old_report_paths(self):
        ws = SimpleNamespace(report=None, pair=SimpleNamespace(history_only=True))
        controls = CopyGroupsUI(ws)
        controls.controls = Mock()
        controls.render_controls()
        controls.controls.set_visibility.assert_called_once_with(False)


if __name__ == '__main__':
    unittest.main()
