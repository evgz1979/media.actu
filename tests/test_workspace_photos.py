from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from workspace_ui import BrowserPane, StorageWorkspace


class WorkspacePhotosTests(unittest.IsolatedAsyncioTestCase):
    async def test_library_button_opens_the_active_tree_without_changing_preview_mode(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.open_volume = AsyncMock()
        ws.panes = [SimpleNamespace(view_mode='tree'), SimpleNamespace(view_mode='preview')]
        ws.active_index = 1
        await ws.open_library(5)
        ws.open_volume.assert_awaited_once_with('photos-5', 0)
        ws.open_volume.reset_mock()
        ws.panes[1].view_mode = 'tree'
        await ws.open_library(6)
        ws.open_volume.assert_awaited_once_with('photos-6', 1)

    async def test_photos_browse_never_uses_mounted_directory_or_comparison_apis(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.request = AsyncMock(return_value={'entries': []})
        ws.pair = SimpleNamespace(active=False)
        await ws.read_directory('photos-5', '2026/2026-08', offset=150)
        self.assertEqual(ws.request.await_args.args, ('GET', '/api/photos/libraries/5/browse'))
        self.assertEqual(ws.request.await_args.kwargs['params']['offset'], 150)
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.volume_id, pane.view_mode = ws, 'photos-5', 'tree'
        self.assertIsNone(pane.scope())
        self.assertIsNone(pane.size_scope())
        pane.view_mode, pane.preview = 'preview', SimpleNamespace(volume_id='photos-5')
        self.assertIsNone(pane.scope())
