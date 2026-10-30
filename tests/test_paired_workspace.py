"""File differences stay hidden until the user expands their folder."""
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from copy_groups_ui import CopyGroupsUI
from paired_workspace_ui import PairedWorkspace
from workspace_ui import BrowserPane, StorageWorkspace


class PairedWorkspaceTests(unittest.TestCase):
    def workspace(self):
        workspace = PairedWorkspace(None)
        workspace.report = {'mode': 'files'}
        workspace.differences_only = True
        workspace.rows = [
            dict(path='Album', kind='directory', status='both', depth=0),
            dict(path='Album/Sub', kind='directory', status='both', depth=1),
            dict(path='Album/Sub/different', kind='file', status='size_different', depth=2),
            dict(path='Album/different', kind='file', status='missing_copy', depth=1),
            dict(path='Album/same', kind='file', status='same_size', depth=1),
            dict(path='Matching', kind='directory', status='both', depth=0),
            dict(path='Matching/Sub', kind='directory', status='both', depth=1),
            dict(path='Matching/Sub/file', kind='file', status='same_size', depth=2),
            dict(path='root-file', kind='file', status='extra_copy', depth=0),
        ]
        workspace.closed = {'Album', 'Album/Sub', 'Matching', 'Matching/Sub'}
        return workspace

    def test_expanding_one_folder_reveals_only_its_differing_files(self):
        workspace = self.workspace()
        paths = lambda: [r['path'] for r in workspace.visible_rows()]
        self.assertEqual(paths(), ['Album', 'Matching'])
        workspace.closed.remove('Album')
        self.assertEqual(paths(), ['Album', 'Album/Sub', 'Album/different', 'Matching'])
        workspace.closed.remove('Album/Sub')
        self.assertEqual(paths(), ['Album', 'Album/Sub', 'Album/Sub/different', 'Album/different', 'Matching'])

    def test_fully_matching_report_keeps_root_folders_collapsed(self):
        workspace = self.workspace()
        workspace.rows = [row for row in workspace.rows if row['path'].startswith('Matching')]
        rows = workspace.visible_rows()
        self.assertEqual([row['path'] for row in rows], ['Matching'])
        self.assertTrue(rows[0]['collapsed'])
        workspace.closed.remove('Matching')
        self.assertEqual([row['path'] for row in workspace.visible_rows()], ['Matching'])

    def test_root_files_require_explicit_disclosure_even_after_navigation(self):
        workspace = self.workspace()
        workspace.root = 'Album'
        workspace.closed.remove('Album')
        paths = lambda: [r['path'] for r in workspace.visible_rows()]
        self.assertEqual(paths(), ['Album/Sub'])
        workspace.root_files_open = True
        self.assertEqual(paths(), ['Album/Sub', 'Album/different'])


class ReportExpansionTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self, mode='folders'):
        rows = [dict(path=path, name=path.rsplit('/', 1)[-1], kind='directory', status=status,
                     depth=path.count('/'), attention_count=count, file_attention_count=0)
                for path, status, count in [('Same', 'both', 0), ('Same/Child', 'both', 0),
                                            ('Changed', 'both', 1), ('Changed/Matching', 'both', 0),
                                            ('Changed/Matching/Deep', 'both', 0), ('Changed/Absent', 'missing_copy', 0)]]
        ws = SimpleNamespace(request=AsyncMock(return_value={'rows': rows, 'total': len(rows)}), panes=[])
        pair = PairedWorkspace(ws)
        pair.report = {'id': 'report', 'mode': mode}
        pair.render_rail, pair.redraw = Mock(), Mock()
        return pair

    async def test_only_branches_with_differences_expand_and_manual_changes_survive_reload(self):
        pair = self.workspace()
        await pair.load_rows('report')
        self.assertNotIn('Changed', pair.closed)
        self.assertEqual([r['path'] for r in pair.visible_rows()],
                         ['Same', 'Changed', 'Changed/Matching', 'Changed/Absent'])
        pair.closed.remove('Same')
        await pair.load_rows('report')
        self.assertNotIn('Same', pair.closed)
        self.assertIn('Same/Child', [r['path'] for r in pair.visible_rows()])

    async def test_file_stage_still_leaves_every_folder_closed_until_manual_expansion(self):
        pair = self.workspace('files')
        await pair.load_rows('report')
        self.assertEqual(pair.closed, {r['path'] for r in pair.rows})
        self.assertEqual([r['path'] for r in pair.visible_rows()], ['Same', 'Changed'])


class PairedContextMenuTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self):
        ws = SimpleNamespace(client=nullcontext(), open_in_finder=AsyncMock(), show_properties=AsyncMock(),
                             context_menu_open=False)
        pair = PairedWorkspace(ws)
        pair.scopes = {'left': {'volume_id': 'main'}, 'right': {'volume_id': 'copy'}}
        pair.by_path = {'photo.jpg': {'path': 'photo.jpg', 'status': 'extra_copy', 'left': None,
                                      'right': {'path': 'Backup/photo.jpg', 'kind': 'file'}}}
        pair.decide = AsyncMock()
        return ws, pair

    async def test_finder_uses_the_clicked_side_and_its_full_volume_path(self):
        ws, pair = self.workspace()
        pair.by_path['photo.jpg']['left'] = {'path': 'Original/photo.jpg', 'kind': 'file'}
        for side, volume, path in [('left', 'main', 'Original/photo.jpg'), ('right', 'copy', 'Backup/photo.jpg')]:
            await pair.on_context(SimpleNamespace(args={'side': side, 'path': 'photo.jpg', 'action': 'finder'}))
            ws.open_in_finder.assert_awaited_with(volume, path)
        pair.decide.assert_not_awaited()
        ws.show_properties.assert_not_awaited()

    async def test_properties_and_decisions_remain_separate_menu_actions(self):
        ws, pair = self.workspace()
        await pair.on_context(SimpleNamespace(args={'side': 'right', 'path': 'photo.jpg', 'action': 'properties'}))
        ws.show_properties.assert_awaited_once_with('copy', pair.by_path['photo.jpg']['right'])
        pair.decide.assert_not_awaited()
        await pair.on_context(SimpleNamespace(args={'side': 'right', 'path': 'photo.jpg', 'action': 'decide'}))
        pair.decide.assert_awaited_once_with(pair.by_path['photo.jpg'])

    async def test_missing_side_does_not_open_another_sides_file(self):
        ws, pair = self.workspace()
        await pair.on_context(SimpleNamespace(args={'side': 'left', 'path': 'photo.jpg', 'action': 'finder'}))
        ws.open_in_finder.assert_not_awaited()

    async def test_open_menu_blocks_background_refresh_until_closed(self):
        ws, pair = self.workspace()
        pair.on_menu_state(SimpleNamespace(args={'open': True}))
        self.assertTrue(ws.context_menu_open)
        pair.on_menu_state(SimpleNamespace(args={'open': False}))
        self.assertFalse(ws.context_menu_open)


class BreadcrumbNavigationTests(unittest.IsolatedAsyncioTestCase):
    async def test_delayed_selector_event_cannot_reset_the_clicked_parent(self):
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace = SimpleNamespace(open_volume=AsyncMock(), client=SimpleNamespace(is_deleted=False))
        pane.volume_id, pane.index = 'copy', 1
        pane.volume_select = SimpleNamespace(value='copy')
        await pane.volume_changed(SimpleNamespace(value='previous-volume'))
        pane.workspace.open_volume.assert_not_awaited()
        pane.volume_select.value = 'selected-volume'
        await pane.volume_changed(SimpleNamespace(value='selected-volume'))
        pane.workspace.open_volume.assert_awaited_once_with('selected-volume', 1)

    async def test_parent_and_volume_root_leave_the_pair_on_the_clicked_side(self):
        ws = SimpleNamespace(open_volume=AsyncMock())
        pair = PairedWorkspace(ws)
        pair.scopes = {'left': {'volume_id': 'main', 'path': 'Private'},
                       'right': {'volume_id': 'copy', 'path': 'Media-copy03/Private'}}
        pair.report = {'id': 'saved-report'}
        pair.navigate = Mock()
        await pair.navigate_path(1, 'Media-copy03/Private/Sub')
        pair.navigate.assert_called_once_with('Sub')
        ws.open_volume.assert_not_awaited()
        for path in ('Media-copy03', ''):
            await pair.navigate_path(1, path)
            ws.open_volume.assert_awaited_with('copy', 1, path=path)
        self.assertEqual(pair.report['id'], 'saved-report')

    async def test_source_report_parent_opens_normal_browsing(self):
        ws = SimpleNamespace(pair=SimpleNamespace(active=False), open_volume=AsyncMock())
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.volume_id, pane.index = ws, 'main', 0
        pane.scan = {'root_path': 'Private/Album'}
        await pane.open_path('Private')
        ws.open_volume.assert_awaited_once_with('main', 0, path='Private')

    async def test_opening_parent_uses_existing_unlink_without_removing_records(self):
        ws = SimpleNamespace(client=nullcontext(), active_index=0, report=None,
                             pair=SimpleNamespace(active=True, unlink=AsyncMock()),
                             panes=[SimpleNamespace(show_volume=AsyncMock()) for _ in range(2)])
        await StorageWorkspace.open_volume(ws, 'copy', 1, path='Media-copy03')
        ws.pair.unlink.assert_awaited_once()
        ws.panes[1].show_volume.assert_awaited_once_with('copy', 'Media-copy03')
        ws.panes[0].show_volume.assert_not_awaited()


class ComparisonToolbarTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_three_actions_ignore_queued_clicks_in_any_comparison_state(self):
        for mode in ('pair', 'legacy'):
            for state in ('running', 'pausing', 'paused', 'completed', 'failed'):
                with self.subTest(mode=mode, state=state):
                    report = {'id': 'report', 'state': state}
                    ws = SimpleNamespace(report=report if mode == 'legacy' else None, size_force=set(),
                                         pair=SimpleNamespace(active=mode == 'pair', report=report if mode == 'pair' else None,
                                                              navigate_path=AsyncMock()), request=AsyncMock())
                    pane = BrowserPane.__new__(BrowserPane)
                    pane.workspace = ws
                    pane.load_folder, pane.show_volume = AsyncMock(), AsyncMock()
                    await pane.go_parent()
                    await pane.go_root()
                    await pane.refresh()
                    self.assertEqual(ws.size_force, set())
                    ws.request.assert_not_awaited()
                    ws.pair.navigate_path.assert_not_awaited()
                    pane.load_folder.assert_not_awaited()
                    pane.show_volume.assert_not_awaited()

    async def test_linked_browsing_without_a_report_keeps_navigation_available(self):
        ws = SimpleNamespace(report=None)
        ws.pair = PairedWorkspace(ws)
        ws.pair.active = True
        ws.pair.scopes = {'left': {'path': 'Original'}}
        ws.pair.navigate_path = AsyncMock()
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.index, pane.path = ws, 0, 'Original/Sub'
        await pane.go_parent()
        ws.pair.navigate_path.assert_awaited_once_with(0, 'Original')
        await pane.go_root()
        self.assertEqual(ws.pair.navigate_path.await_count, 2)


class PanelUnlinkTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self, state='completed'):
        panes = [SimpleNamespace(tree=SimpleNamespace(classes=Mock()), restore_browse_state=Mock()) for _ in range(2)]
        ws = SimpleNamespace(client=nullcontext(), panes=panes, set_active=Mock(), update_scopes=Mock(), request=AsyncMock())
        pair = PairedWorkspace(ws)
        pair.active = True
        pair.report = {'id': 'report', 'state': state}
        pair.saved = [{'path': 'before-left'}, {'path': 'before-right'}]
        pair.saved_active = 1
        pair.render_rail = Mock()
        pair.stop = AsyncMock()
        return ws, pair

    async def test_panel_unlink_restores_browsing_without_removing_copy_records(self):
        ws, pair = self.workspace()
        await pair.unlink()
        self.assertFalse(pair.active)
        self.assertIsNone(pair.report)
        ws.panes[0].restore_browse_state.assert_called_once_with({'path': 'before-left'})
        ws.panes[1].restore_browse_state.assert_called_once_with({'path': 'before-right'})
        ws.set_active.assert_called_once_with(1)
        ws.request.assert_not_awaited()

    async def test_leaving_a_running_comparison_stops_it_before_restoring_the_panels(self):
        ws, pair = self.workspace('running')
        await pair.unlink()
        pair.stop.assert_awaited_once()
        self.assertFalse(pair.active)
        ws.request.assert_not_awaited()


class MainFolderOpeningTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self, copies):
        ws = SimpleNamespace(client=nullcontext(), pair=SimpleNamespace(active=True, link=AsyncMock(), unlink=AsyncMock()),
                             report=None, browse=AsyncMock(), panes=[SimpleNamespace(show_volume=AsyncMock())])
        group = {'main': {'volume_id': 'main-volume', 'path': 'Apple'}, 'copies': copies}
        return ws, CopyGroupsUI(ws), group

    async def test_main_opens_the_first_numbered_copy_in_linked_panels(self):
        first = {'id': 'first', 'number': 1}
        ws, controls, group = self.workspace([{'id': 'second', 'number': 2}, first])
        await controls.open_main(group)
        ws.pair.link.assert_awaited_once_with(group, first)
        ws.pair.unlink.assert_not_awaited()
        ws.panes[0].show_volume.assert_not_awaited()

    async def test_main_without_copies_opens_only_the_main_folder(self):
        ws, controls, group = self.workspace([])
        await controls.open_main(group)
        ws.pair.link.assert_not_awaited()
        ws.pair.unlink.assert_awaited_once()
        ws.panes[0].show_volume.assert_awaited_once_with('main-volume', 'Apple')


class CopyRemovalConfirmationTests(unittest.IsolatedAsyncioTestCase):
    def controls(self, confirmed):
        pair = SimpleNamespace(active=True, copy_id='copy', unlink=AsyncMock())
        ws = SimpleNamespace(client=nullcontext(), editing=False, pair=pair, request=AsyncMock(), notice=Mock())
        controls = CopyGroupsUI(ws)
        main = dict(id='main', label='00-main', volume_name='NAS 1', path='Original')
        copy = dict(id='copy', group_id='group', label='01-copy', volume_name='NAS 2', path='Backup')
        controls.groups = [dict(id='group', main=main, copies=[copy], numbering_changes=[])]
        controls.refresh = AsyncMock()
        controls.changed = AsyncMock()
        controls.confirm_remove = AsyncMock(return_value=confirmed)
        return ws, controls, main, copy

    async def test_cancel_shows_both_locations_without_deleting_the_link(self):
        ws, controls, main, copy = self.controls(False)
        await controls.remove_copy(copy)
        self.assertEqual(controls.confirm_remove.await_args.kwargs['locations'], (main, copy))
        ws.request.assert_not_awaited()
        ws.pair.unlink.assert_not_awaited()
        self.assertFalse(ws.editing)

    async def test_confirm_removes_only_the_chosen_link_then_closes_its_pair(self):
        ws, controls, main, copy = self.controls(True)
        await controls.remove_copy(copy)
        ws.request.assert_awaited_once_with('DELETE', '/api/storage/copy-locations/copy')
        ws.pair.unlink.assert_awaited_once()
        controls.changed.assert_awaited_once()
