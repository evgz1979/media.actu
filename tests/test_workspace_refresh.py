from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from workspace_ui import BrowserPane, StorageWorkspace


class WorkspaceRefreshTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.volumes = [dict(id='disk', kind='external', availability='online', mounted=True,
                           identity_status='verified', capacity={'used_bytes': 100})]
        ws.photo_libraries = SimpleNamespace(volumes=lambda: [dict(id='photos-5', kind='photos',
            availability='online', mounted=False, identity_status='virtual')])
        ws.client = SimpleNamespace(is_deleted=False, has_socket_connection=True)
        ws.context_menu_open = ws.editing = False
        ws.refresh_button = Mock()
        ws.render_volumes, ws.update_scopes, ws.notice = Mock(), Mock(), Mock()
        ws.copies = SimpleNamespace(refresh=AsyncMock())
        ws.request = AsyncMock(return_value={'volumes': [dict(ws.volumes[0], capacity={'used_bytes': 200})]})
        ws.panes = []
        for volume_id in ('disk', 'photos-5'):
            pane = BrowserPane.__new__(BrowserPane)
            pane.workspace, pane.volume_id = ws, volume_id
            pane.update_header, pane.render = Mock(), Mock()
            pane.folders = {'Album': {'entries': ['existing rows']}}
            ws.panes.append(pane)
        return ws

    async def test_capacity_poll_preserves_existing_disk_and_photos_trees(self):
        ws = self.workspace()
        folders = [p.folders for p in ws.panes]
        await ws.refresh_volumes()
        self.assertEqual(ws.volumes[0]['capacity']['used_bytes'], 200)
        for pane, original in zip(ws.panes, folders):
            pane.render.assert_not_called()
            pane.update_header.assert_called_once()
            self.assertIs(pane.folders, original)
        ws.notice.assert_not_called()

    async def test_volume_access_change_updates_only_the_affected_tree(self):
        ws = self.workspace()
        ws.request.return_value = {'volumes': [dict(ws.volumes[0], availability='offline', mounted=False)]}
        await ws.refresh_volumes()
        ws.panes[0].render.assert_called_once()
        ws.panes[1].render.assert_not_called()

    async def test_explicit_volume_refresh_can_redraw_both_trees(self):
        ws = self.workspace()
        await ws.refresh_volumes(True)
        for pane in ws.panes:
            pane.render.assert_called_once()

    async def test_background_polling_stops_until_the_same_client_reconnects(self):
        ws = self.workspace()
        callback = AsyncMock()
        ws.client.has_socket_connection = False
        await ws.poll_connected(callback)
        callback.assert_not_awaited()
        ws.client.has_socket_connection = True
        await ws.poll_connected(callback)
        callback.assert_awaited_once()
        callback.reset_mock()
        ws.client.is_deleted = True
        await ws.poll_connected(callback)
        callback.assert_not_awaited()
