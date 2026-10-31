import asyncio
from contextlib import nullcontext
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from copy_groups_ui import CopyGroupsUI, sidebar_sections
from media_manager.copies import CopyCatalog
from media_manager.paired_comparison import PairedComparisonCatalog
from media_manager.storage import StorageCatalog


class CopyConnectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.mounted = []
        for name, folder in [('main', 'Original'), ('copy', 'Backup'), ('cold', 'Cold')]:
            mount = self.root / name
            (mount / folder).mkdir(parents=True)
            self.mounted.append(dict(id=name, name=name, kind='external', mount_path=str(mount), device=mount.stat().st_dev))
        self.storage = StorageCatalog(self.root / 'data/storage.sqlite3', lambda: self.mounted)
        for volume in self.mounted:
            self.storage.directory(volume['id'])
        self.copies = CopyCatalog(self.storage)
        self.group = self.copies.create_main('main', 'Original')
        self.copies.add_copy(self.group['id'], 'copy', 'Backup')
        self.group = self.copies.add_copy(self.group['id'], 'cold', 'Cold', 'cold')

    def test_disconnected_group_preserves_labels_numbers_and_history_after_restart(self):
        self.copies.update_group(self.group['id'], {'label': 'temporary', 'tracking': True})
        pairs = PairedComparisonCatalog(self.storage, self.copies)
        self.addCleanup(pairs.close)
        report = pairs.create(self.group['copies'][0]['id'], background=False)
        self.copies.set_group_connected(self.group['id'], False)
        self.copies.mark_changed(self.group['id'])
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        group = reopened.group(self.group['id'])
        self.assertFalse(group['connected'])
        self.assertTrue(group['tracking'])
        self.assertIsNone(group['changed_at'])
        self.assertEqual(group['label'], 'temporary')
        self.assertEqual([c['id'] for c in group['copies']], [c['id'] for c in self.group['copies']])
        self.assertEqual([c['label'] for c in group['copies']], ['01-copy', '02-copy-cold'])
        self.assertFalse(any(c['connected'] for c in [group['main'], *group['copies']]))
        self.assertEqual(pairs.jobs()[0]['id'], report['id'])
        with self.assertRaisesRegex(ValueError, 'отключена'):
            pairs.create(group['copies'][0]['id'], background=False)
        with self.assertRaisesRegex(ValueError, 'отключена'):
            pairs.resume(report['id'])
        group = reopened.set_group_connected(group['id'], True)
        self.assertTrue(all(c['connected'] for c in [group['main'], *group['copies']]))
        self.assertEqual(group['next_number'], 3)

    def test_individual_disconnect_survives_whole_group_round_trip_without_renumbering(self):
        location = self.group['copies'][0]
        group = self.copies.set_copy_connected(location['id'], False)
        self.assertTrue(group['connected'])
        self.assertFalse(group['copies'][0]['connected'])
        self.assertTrue(group['copies'][1]['connected'])
        self.assertEqual(group['numbering_changes'], [])
        self.copies.set_group_connected(group['id'], False)
        group = self.copies.set_group_connected(group['id'], True)
        self.assertFalse(group['copies'][0]['connected'])
        group = self.copies.set_copy_connected(location['id'], True)
        self.assertTrue(group['copies'][0]['connected'])
        self.assertEqual(group['copies'][0]['id'], location['id'])
        self.assertEqual(group['copies'][0]['number'], 1)
        self.assertEqual(list((self.root / 'copy/Backup').iterdir()), [])

    def test_invalid_connections_and_explicit_deletion(self):
        with self.assertRaises(ValueError):
            self.copies.set_copy_connected(self.group['main']['id'], False)
        with self.assertRaises(ValueError):
            self.copies.set_group_connected(self.group['id'], 'false')
        with self.assertRaises(KeyError):
            self.copies.set_copy_connected('missing', False)
        with self.assertRaises(KeyError):
            self.copies.set_group_connected('missing', False)
        self.copies.set_copy_connected(self.group['copies'][0]['id'], False)
        self.copies.set_group_connected(self.group['id'], False)
        self.copies.remove_group(self.group['id'])
        with self.storage.connect() as db:
            self.assertEqual(db.execute('SELECT * FROM disconnected_copy_groups').fetchall(), [])
            self.assertEqual(db.execute('SELECT * FROM disconnected_copy_locations').fetchall(), [])

    def test_api_can_disconnect_and_reconnect_but_will_not_interrupt_copying(self):
        async def exercise():
            import httpx
            with patch.dict(os.environ, {'MEDIA_ACTU_DATA_DIR': str(self.root / 'api-data')}):
                import app as core
            transfers = Mock()
            transfers.busy.return_value = False
            with patch.object(core, 'copies', self.copies), patch.object(core, 'missing_copies', transfers), \
                 patch.object(core, 'folder_tracking', Mock()):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app), base_url='http://test') as client:
                    group_url = f"/api/storage/copy-groups/{self.group['id']}/connection"
                    copy_url = f"/api/storage/copy-locations/{self.group['copies'][0]['id']}/connection"
                    response = await client.patch(copy_url, json={'connected': False})
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertFalse(response.json()['copies'][0]['connected'])
                    response = await client.patch(group_url, json={'connected': False})
                    self.assertFalse(response.json()['connected'])
                    response = await client.patch(group_url, json={'connected': True})
                    self.assertTrue(response.json()['connected'])
                    self.assertFalse(response.json()['copies'][0]['connected'])
                    self.assertEqual((await client.patch(group_url, json={'connected': 'false'})).status_code, 422)
                    transfers.busy.return_value = True
                    self.assertEqual((await client.patch(group_url, json={'connected': False})).status_code, 400)
                    self.assertTrue(self.copies.group(self.group['id'])['connected'])
        asyncio.run(exercise())


class SidebarSectionsTests(unittest.TestCase):
    def group(self, main='online', copy='online', cold='offline', connected=True):
        return dict(id='group', connected=connected,
                    main=dict(id='main', availability=main, connected=True),
                    copies=[dict(id='copy', availability=copy, connected=True),
                            dict(id='cold', availability=cold, connected=True)])

    def test_offline_copy_keeps_its_group_and_online_siblings_visible(self):
        group = self.group()
        active, offline, count = sidebar_sections([group])
        self.assertEqual([c['id'] for c in active[0][1]], ['copy'])
        self.assertEqual([c['id'] for c in offline[0][1]], ['cold'])
        self.assertIs(active[0][0], group)
        self.assertIs(offline[0][0], group)
        self.assertEqual(count, 1)

    def test_offline_main_does_not_hide_online_copy_and_all_offline_moves_whole_group(self):
        active, offline, count = sidebar_sections([self.group(main='offline')])
        self.assertEqual(len(active), 1)
        self.assertEqual(count, 2)
        active, offline, count = sidebar_sections([self.group(main='offline', copy='offline')])
        self.assertEqual(active, [])
        self.assertEqual(len(offline[0][1]), 2)
        self.assertEqual(count, 3)

    def test_manual_disconnect_remains_visible_while_unknown_availability_stays_active(self):
        active, offline, count = sidebar_sections([self.group(connected=False)])
        self.assertEqual(active, [])
        self.assertEqual(count, 3)
        active, offline, count = sidebar_sections([self.group(main='unknown', cold='unknown')])
        self.assertEqual(len(active), 1)
        self.assertEqual(offline, [])
        self.assertEqual(count, 0)


class ConnectionActionsTests(unittest.IsolatedAsyncioTestCase):
    async def test_disconnect_uses_reversible_api_unlinks_pair_and_opens_section(self):
        pair = SimpleNamespace(active=True, copy_id='copy', copy_running=False, unlink=AsyncMock())
        ws = SimpleNamespace(client=nullcontext(), editing=False, pair=pair, request=AsyncMock(), notice=Mock())
        controls = CopyGroupsUI(ws)
        controls.changed = AsyncMock()
        controls.disconnected = Mock()
        group = dict(id='group', copies=[dict(id='copy')])
        await controls.set_connection(group, False)
        ws.request.assert_awaited_once_with('PATCH', '/api/storage/copy-groups/group/connection', json={'connected': False})
        pair.unlink.assert_awaited_once()
        controls.disconnected.open.assert_called_once()
        self.assertFalse(ws.editing)
        ws.notice.assert_not_called()

    async def test_copying_blocks_disconnect_without_changing_any_state(self):
        ws = SimpleNamespace(client=nullcontext(), editing=False,
                             pair=SimpleNamespace(active=True, copy_id='copy', copy_running=True),
                             request=AsyncMock(), notice=Mock())
        controls = CopyGroupsUI(ws)
        await controls.set_connection(dict(id='group', copies=[dict(id='copy')]), False)
        ws.request.assert_not_awaited()
        ws.notice.assert_called_once()
        self.assertFalse(ws.editing)


if __name__ == '__main__':
    unittest.main()
