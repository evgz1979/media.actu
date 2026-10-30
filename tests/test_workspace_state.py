from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from paired_workspace_ui import PairedWorkspace
from workspace_state import normalize_state, pane_snapshot
from workspace_ui import StorageWorkspace


def pane_state(volume, root):
    return dict(volume_id=volume, root_path=root, path=root, kind='directory', hidden=False)


def saved_state():
    return dict(version=1, active=1, panes=[pane_state('main', 'Original/Album'), pane_state('copy', 'Backup/Album')],
                browse=[pane_state('main', 'Original'), pane_state('copy', 'Backup')],
                pair=dict(copy_id='copy-link', job_id='job', root='Album', selected='Album/Sub',
                          differences_only=True, hidden=True, root_files_open=True, expanded=['Album']))


class WorkspaceStateTests(unittest.TestCase):
    def test_navigation_snapshot_omits_file_lists_and_preserves_paths(self):
        pane = SimpleNamespace(volume_id='disk', root_path='Private/Album', path='Private/Album/photo.jpg', kind='file',
                               hidden=SimpleNamespace(value=True), folders={'huge': ['file data']})
        snapshot = pane_snapshot(pane)
        self.assertNotIn('folders', snapshot)
        self.assertEqual(snapshot['path'], 'Private/Album/photo.jpg')
        self.assertTrue(snapshot['hidden'])

    def test_invalid_saved_paths_and_identifiers_are_ignored(self):
        for value in ('../outside', '/etc', 'Private/../../outside', '\x00'):
            state = saved_state()
            state['panes'][0]['root_path'] = value
            self.assertIsNone(normalize_state(state))
        state = saved_state()
        state['pair']['job_id'] = '../job'
        self.assertIsNone(normalize_state(state))
        self.assertIsNone(normalize_state({'version': 1, 'panes': []}))
        self.assertEqual(normalize_state(saved_state())['pair']['root'], 'Album')

    def test_running_snapshot_does_not_invent_collapsed_folders_before_rows_exist(self):
        state = saved_state()
        state['pair']['expanded'] = None
        self.assertIsNone(normalize_state(state)['pair']['expanded'])


class WorkspaceRestoreTests(unittest.IsolatedAsyncioTestCase):
    def workspace(self, report):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.restore_panes = AsyncMock(return_value=True)
        ws.request = AsyncMock(return_value=report)
        ws.pair = SimpleNamespace(link=AsyncMock(), apply=AsyncMock(), restore_view=Mock())
        ws.copies = SimpleNamespace(groups=[{'main': {'volume_id': 'main', 'path': 'Original'},
                                             'copies': [{'id': 'copy-link', 'volume_id': 'copy', 'path': 'Backup'}]}])
        ws.set_active, ws.update_scopes = Mock(), Mock()
        return ws

    async def test_running_report_is_read_without_starting_resuming_or_pausing_a_job(self):
        report = dict(id='job', copy_id='copy-link', state='running')
        ws = self.workspace(report)
        state = normalize_state(saved_state())
        self.assertTrue(await ws.restore_workspace(state))
        ws.request.assert_awaited_once_with('GET', '/api/storage/paired-comparisons/job', timeout=45)
        ws.pair.apply.assert_awaited_once_with(report)
        ws.pair.restore_view.assert_called_once_with(state['pair'])
        ws.set_active.assert_called_once_with(1)

    async def test_reload_during_create_response_recovers_the_created_job_once(self):
        report = dict(id='new-job', copy_id='copy-link', state='running')
        ws = self.workspace(report)
        state = normalize_state(saved_state())
        state['pair']['pending'] = dict(since='2026-10-30T16:00:00+00:00', mode='folders', method='size')
        jobs = [dict(id='new-job', created_at='2026-10-30T16:00:01+00:00', mode='folders', method='size'),
                dict(id='job', created_at='2026-10-29T16:00:00+00:00', mode='folders', method='size')]
        ws.request.side_effect = [{'jobs': jobs}, report]
        await ws.restore_workspace(state)
        self.assertEqual([call.args[0] for call in ws.request.await_args_list], ['GET', 'GET'])
        ws.pair.apply.assert_awaited_once_with(report)

    async def test_plain_panels_restore_both_roots_and_the_selected_file(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        states = [pane_state('main', 'Original/Album'), pane_state('copy', 'Backup/Other')]
        states[0].update(path='Original/Album/photo.jpg', kind='file', hidden=True)
        ws.volumes = [{'id': 'main'}, {'id': 'copy'}]
        ws.panes = [SimpleNamespace(hidden=Mock(), show_volume=AsyncMock(), render=Mock()) for _ in states]
        ws.set_active, ws.update_scopes = Mock(), Mock()
        await ws.restore_workspace(dict(version=1, active=1, panes=states))
        self.assertEqual([p.path for p in ws.panes], ['Original/Album/photo.jpg', 'Backup/Other'])
        ws.panes[0].show_volume.assert_awaited_once_with('main', 'Original/Album', activate=False)
        ws.panes[1].show_volume.assert_awaited_once_with('copy', 'Backup/Other', activate=False)


class PairProgressViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_polling_the_same_running_report_preserves_both_paths_and_file_selection(self):
        panes = [SimpleNamespace(path=path, kind='file', volume_select=Mock(), render=Mock())
                 for path in ('Original/Album/photo.jpg', 'Backup/Album/photo.jpg')]
        ws = SimpleNamespace(panes=panes)
        pair = PairedWorkspace(ws)
        report = dict(id='job', state='running', mode='files', scopes={'left': {'volume_id': 'main', 'path': 'Original'},
                                                                    'right': {'volume_id': 'copy', 'path': 'Backup'}})
        pair.report = report
        pair.render_rail, pair.set_hidden = Mock(), Mock()
        await pair.apply(dict(report, indexed_directories=100))
        self.assertEqual([p.path for p in panes], ['Original/Album/photo.jpg', 'Backup/Album/photo.jpg'])
        self.assertEqual([p.kind for p in panes], ['file', 'file'])

    async def test_restored_navigation_waits_for_rows_without_changing_the_report(self):
        state = normalize_state(saved_state())['pair']
        ws = SimpleNamespace(panes=[SimpleNamespace(hidden=Mock()) for _ in range(2)],
                             request=AsyncMock(), format_bytes=str)
        pair = PairedWorkspace(ws)
        pair.report = dict(id='job', mode='files')
        pair.scopes = {'left': {'volume_id': 'main', 'path': 'Original'}, 'right': {'volume_id': 'copy', 'path': 'Backup'}}
        pair.render_rail, pair.redraw = Mock(), Mock()
        pair.restore_view(state)
        rows = [dict(path=path, name=path.rsplit('/', 1)[-1], kind='directory', status='both',
                     left={'path': 'Original/' + path, 'kind': 'directory'},
                     right={'path': 'Backup/' + path, 'kind': 'directory'}, attention_count=0, file_attention_count=0)
                for path in ('Album', 'Album/Sub')]
        ws.request.return_value = {'rows': rows, 'total': len(rows)}
        await pair.load_rows('job')
        self.assertEqual((pair.root, pair.selected, pair.report['id']), ('Album', 'Album/Sub', 'job'))
        self.assertTrue(pair.show_hidden)
        self.assertTrue(pair.root_files_open)
        self.assertNotIn('Album', pair.closed)
        self.assertIsNone(pair.pending_view)
        state['expanded'] = None
        before = pair.closed.copy()
        pair.restore_view(state)
        self.assertEqual(pair.closed, before)
