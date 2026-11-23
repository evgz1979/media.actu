from contextlib import nullcontext
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from copy_panels import copy_heading
from photo_libraries_ui import PhotoLibrariesUI
from workspace_ui import BrowserPane, StorageWorkspace


class WorkspacePhotosTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.client = nullcontext()
        ws.panes = [SimpleNamespace(view_mode='tree', set_mode=AsyncMock(), show_volume=AsyncMock(),
                                    focus_tree=Mock()) for _ in range(2)]
        ws.pair = SimpleNamespace(active=False, unlink=AsyncMock())
        ws.report = None
        ws.active_index = 1
        ws.source_open_generation = 0
        ws.set_active = Mock(side_effect=lambda i: setattr(ws, 'active_index', i))
        ws.photo_libraries = PhotoLibrariesUI(ws)
        return ws

    async def test_opening_photos_selects_the_first_available_copy_and_restores_the_destination_tree(self):
        ws = self.workspace()
        ws.panes[1].view_mode = 'preview'
        ws.pair.active = True
        ws.photo_libraries.libraries = [dict(id=5, copies=[
            dict(number=3, volume_id='later', path='Later', availability='online'),
            dict(number=1, volume_id='old', path='Old', availability='offline'),
            dict(number=2, volume_id='disk', path='Archive/Photos', availability='online'),
        ])]
        await ws.open_library(5)
        ws.pair.unlink.assert_awaited_once()
        ws.panes[1].set_mode.assert_awaited_once_with('tree')
        ws.panes[0].show_volume.assert_awaited_once_with('photos-5', '', activate=False)
        ws.panes[1].show_volume.assert_awaited_once_with('disk', 'Archive/Photos', activate=False)
        self.assertEqual(ws.active_index, 0)

    async def test_opening_photos_without_copies_uses_only_the_left_tree(self):
        ws = self.workspace()
        ws.photo_libraries.libraries = [dict(id=6, copies=[])]
        await ws.open_library(6)
        ws.panes[0].show_volume.assert_awaited_once_with('photos-6', '', activate=False)
        ws.panes[1].show_volume.assert_not_awaited()

    async def test_icloud_opens_the_bound_source_path_even_when_all_copies_are_offline(self):
        ws = self.workspace()
        ws.photo_libraries.cloud = dict(volume={'availability': 'online'}, copies=[
            dict(number=2, volume_id='other', path='Archive', source_path='', availability='offline'),
            dict(number=1, volume_id='saved', path='Backups', source_path='Документы/Медиа', availability='offline'),
        ])
        await ws.photo_libraries.open_cloud()
        ws.panes[0].show_volume.assert_awaited_once_with('icloud-drive', 'Документы/Медиа', activate=False)
        ws.panes[1].show_volume.assert_awaited_once_with('saved', 'Backups', activate=False)

    def test_common_heading_preserves_folder_copy_and_history_captions(self):
        self.assertEqual(copy_heading(dict(label='00-main', number=0)), '00-main (источник копирования)')
        self.assertEqual(copy_heading(dict(label='01-copy', number=1), target=True), '01-copy (копия №1)')
        self.assertEqual(copy_heading(dict(label='01-copy', number=1), target=True, historical=True), 'Прежняя 01-copy')

    def test_heading_shows_the_actual_photos_chain_and_clears_outside_the_copy(self):
        ws = self.workspace()
        ws.photo_libraries.libraries = [dict(id=5, label='Системная медиатека Photos', copies=[
            dict(id='first', number=1, volume_id='nvme', path='Photos', volume_name='NVMe'),
            dict(id='second', number=2, volume_id='hdd', path='Photos', source_link_id='first'),
        ])]
        left, right = ws.panes
        left.volume_id, left.path, left.title, left.heading = 'photos-5', '2026', 'Левая', SimpleNamespace()
        right.volume_id, right.path, right.title, right.heading = 'hdd', 'Photos/2026', 'Правая', SimpleNamespace()
        ws.refresh_browse_headings()
        self.assertEqual(left.heading.text, 'Photos (источник копирования)')
        self.assertEqual(right.heading.text, '02-copy (копия №2) · из 01-copy на NVMe')
        right.path = 'Photos-old/2026'
        ws.refresh_browse_headings()
        self.assertEqual((left.heading.text, right.heading.text), ('Левая панель', 'Правая панель'))

    def test_icloud_headings_use_the_bound_source_and_destination_scopes(self):
        ws = self.workspace()
        ws.photo_libraries.cloud = dict(copies=[dict(number=1, volume_id='disk', path='Backups', source_path='Docs')])
        left, right = ws.panes
        left.volume_id, left.path, left.title, left.heading = 'icloud-drive', 'Docs/Sub', 'Левая', SimpleNamespace()
        right.volume_id, right.path, right.title, right.heading = 'disk', 'Backups', 'Правая', SimpleNamespace()
        ws.refresh_browse_headings()
        self.assertEqual(left.heading.text, 'iCloud Drive (источник копирования)')
        self.assertEqual(right.heading.text, '01-copy (копия №1)')
        left.path = 'Docs-old'
        ws.refresh_browse_headings()
        self.assertEqual((left.heading.text, right.heading.text), ('Левая панель', 'Правая панель'))

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
