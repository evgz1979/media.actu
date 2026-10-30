import asyncio
from contextlib import nullcontext
import os
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from media_manager.directory_sizes import DirectorySizeService
from media_manager.storage import StorageCatalog
from workspace_ui import BrowserPane, StorageWorkspace


class DirectorySizeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.volume = self.root / 'volume'
        (self.volume / 'Album' / 'Nested').mkdir(parents=True)
        (self.volume / 'Album' / 'Empty').mkdir()
        (self.volume / 'Album' / 'photo.jpg').write_bytes(b'12345')
        (self.volume / 'Album' / 'Nested' / '.hidden').write_bytes(b'1234567')
        self.mounted = [dict(id='disk', name='Disk', kind='external', mount_path=str(self.volume),
                             device=self.volume.stat().st_dev)]
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.mounted)
        self.service = DirectorySizeService(self.storage)
        self.addCleanup(self.service.close)

    def size(self, path='Album'):
        return self.service.request('disk', [path], start=False)['sizes'][path]

    def wait(self):
        deadline = time.monotonic() + 3
        while self.service._jobs and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertFalse(self.service._jobs)

    def test_recursive_totals_include_hidden_files_and_empty_folders_without_opening_contents(self):
        (self.root / 'outside').write_bytes(b'1234567890')
        (self.volume / 'Album' / 'link').symlink_to(self.root, target_is_directory=True)
        os.mkfifo(self.volume / 'Album' / 'pipe')
        with patch('builtins.open', side_effect=AssertionError('File contents must stay closed')):
            self.service.calculate('disk', 'Album')
        total = self.size()
        self.assertEqual((total['bytes'], total['files'], total['complete']), (12, 2, True))
        self.assertEqual(self.size('Album/Nested')['bytes'], 7)
        self.assertEqual(self.size('Album/Empty')['bytes'], 0)
        self.assertEqual((self.volume / 'Album/photo.jpg').read_bytes(), b'12345')

    def test_refresh_recomputes_and_cached_result_survives_restart_and_disconnect(self):
        self.service.calculate('disk', 'Album')
        (self.volume / 'Album/photo.jpg').write_bytes(b'123456789')
        self.service.request('disk', ['Album'], refresh=True)
        self.wait()
        self.assertEqual(self.size()['bytes'], 16)
        self.mounted.clear()
        self.storage.refresh(True)
        reopened = DirectorySizeService(self.storage)
        self.addCleanup(reopened.close)
        result = reopened.request('disk', ['Album'])['sizes']['Album']
        self.assertEqual((result['bytes'], result['state']), (16, 'offline'))
        self.assertFalse(reopened._jobs)

    def test_changed_child_invalidates_ancestor_until_it_is_recalculated(self):
        self.service.calculate('disk', '')
        (self.volume / 'Album/photo.jpg').write_bytes(b'1')
        self.service.calculate('disk', 'Album')
        self.assertEqual(self.size()['bytes'], 8)
        self.assertEqual(self.size('')['state'], 'stale')
        self.service.request('disk', [''])
        self.wait()
        self.assertEqual((self.size('')['bytes'], self.size('')['state']), (8, 'ready'))

    def test_reopening_old_cached_size_does_not_scan_again_or_discover_disks(self):
        self.service.calculate('disk', 'Album')
        with self.storage.connect() as db:
            db.execute("UPDATE directory_sizes SET calculated_at='2000-01-01T00:00:00+00:00'")
        with patch.object(self.storage, 'discover', side_effect=AssertionError('Polling must not inspect disks')), \
             patch.object(self.service, 'calculate', side_effect=AssertionError('Do not repeat a full traversal')):
            for _ in range(3):
                self.assertEqual(self.service.request('disk', ['Album'])['sizes']['Album']['bytes'], 12)
        self.assertFalse(self.service._jobs)

    def test_parent_request_covers_child_without_blocking_or_duplicate_traversals(self):
        started, release = threading.Event(), threading.Event()
        calculate = self.service.calculate

        def blocked(*args):
            started.set()
            release.wait(3)
            calculate(*args)

        with patch.object(self.service, 'calculate', side_effect=blocked) as scan:
            result = self.service.request('disk', ['Album', 'Album/Nested'])
            self.assertIn(result['sizes']['Album']['state'], ('queued', 'running'))
            self.assertTrue(started.wait(1))
            self.service.request('disk', ['Album/Nested'], refresh=True)
            self.assertEqual(scan.call_count, 1)
            release.set()
            self.wait()
        self.assertEqual(self.size()['bytes'], 12)

    def test_partial_scan_is_not_reported_as_a_complete_folder(self):
        scandir = os.scandir

        def checked(descriptor):
            if os.fstat(descriptor).st_ino == (self.volume / 'Album/Nested').stat().st_ino:
                raise PermissionError('No access to Nested')
            return scandir(descriptor)

        with patch('media_manager.directory_sizes.os.scandir', side_effect=checked):
            self.service.calculate('disk', 'Album')
        result = self.size()
        self.assertEqual((result['bytes'], result['complete'], result['state']), (5, False, 'partial'))
        self.assertIn('No access', result['error'])
        self.assertEqual(self.size('Album/Nested')['state'], 'error')

    def test_failed_refresh_preserves_previous_size(self):
        self.service.calculate('disk', 'Album')
        with patch('media_manager.directory_sizes.open_readonly', side_effect=PermissionError('No access')):
            self.service.request('disk', ['Album'], refresh=True)
            self.wait()
        result = self.size()
        self.assertEqual((result['bytes'], result['state']), (12, 'error'))

    def test_paths_links_and_replaced_volumes_are_rejected(self):
        for path in ('../outside', '/etc', 'Album/../../outside', '\x00'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.service.request('disk', [path])
        (self.volume / 'link').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            self.service.calculate('disk', 'link/volume')
        self.mounted[0]['device'] = -1
        with self.assertRaises(OSError):
            self.service.calculate('disk', 'Album')
        self.assertIsNone(self.size()['bytes'])


class DirectorySizeDisplayTests(unittest.TestCase):
    def workspace(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.format_bytes = lambda size: f'{size} Б'
        ws.format_date = lambda date: '30.10.2026 19:00'
        ws.directory_sizes = {'disk': {'Album': dict(bytes=0, complete=True, state='ready')}}
        return ws

    def test_zero_partial_refresh_and_offline_values_are_distinct(self):
        ws = self.workspace()
        record = ws.directory_sizes['disk']['Album']
        self.assertEqual(ws.directory_size_text('disk', 'Album'), '0 Б')
        record.update(bytes=12, complete=False, state='partial')
        self.assertEqual(ws.directory_size_text('disk', 'Album'), '≥ 12 Б')
        self.assertIn('частично', ws.directory_size_text('disk', 'Album', detail=True))
        record.update(state='running')
        self.assertIn('считаю', ws.directory_size_text('disk', 'Album', detail=True))
        record.update(state='offline', calculated_at='2026-10-30T16:00:00+00:00')
        self.assertIn('сохранено 30.10.2026', ws.directory_size_text('disk', 'Album', detail=True))

    def test_header_follows_folder_navigation_and_file_parent_and_hides_missing_side(self):
        ws = self.workspace()
        ws.pair = SimpleNamespace(active=False)
        ws.report = None
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.index, pane.volume_id = ws, 0, 'disk'
        pane.path, pane.kind = 'Album', 'directory'
        pane.folder_size = SimpleNamespace(set_visibility=Mock())
        pane.update_size_header()
        self.assertEqual(pane.folder_size.text, 'Размер папки: 0 Б')
        pane.path, pane.kind = 'Album/photo.jpg', 'file'
        self.assertEqual(pane.size_scope(), ('disk', 'Album'))
        ws.pair = SimpleNamespace(active=True, report=True, selected='Album', by_path={'Album': {'left': None}})
        self.assertIsNone(pane.size_scope())

    def test_deleted_rows_are_not_updated_while_a_folder_is_loading(self):
        ws = self.workspace()
        ws.client = SimpleNamespace(is_deleted=False)
        deleted, alive = Mock(is_deleted=True), SimpleNamespace(is_deleted=False, text='')
        pane = SimpleNamespace(update_size_header=Mock(), size_cells={('disk', 'deleted'): deleted, ('disk', 'Album'): alive})
        ws.panes, ws.pair = [pane], SimpleNamespace(views={})
        ws.update_size_labels()
        self.assertNotIn(('disk', 'deleted'), pane.size_cells)
        self.assertEqual(alive.text, '0 Б')


class FolderLoadingTests(unittest.IsolatedAsyncioTestCase):
    async def test_folder_list_does_not_wait_for_a_blocked_size_request(self):
        blocked = asyncio.Event()

        async def delayed_sizes(*args, **kwargs):
            await blocked.wait()

        ws = SimpleNamespace(request=AsyncMock(return_value={'entries': [{'path': 'Album', 'kind': 'directory'}]}),
                             load_directory_sizes=delayed_sizes)
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.generation, pane.volume_id, pane.scan, pane.folders = ws, 1, 'disk', None, {}
        await asyncio.wait_for(pane.load_folder(''), timeout=.2)
        self.assertEqual(pane.folders['']['entries'][0]['path'], 'Album')

    async def test_cached_tree_is_rendered_before_slow_live_directory_read(self):
        started, release = asyncio.Event(), asyncio.Event()
        cached = {'entries': [{'path': 'Album', 'kind': 'directory'}], 'scanned_at': '2026-10-30T16:00:00+00:00'}

        async def request(*args, params, **kwargs):
            if params['refresh']:
                started.set()
                await release.wait()
            return cached

        client = nullcontext()
        client.is_deleted = False
        ws = SimpleNamespace(request=request, client=client, volumes=[{'id': 'disk', 'availability': 'online'}],
                             set_active=Mock(), render_volumes=Mock(), update_scopes=Mock(),
                             context_menu_open=False, editing=False)
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace, pane.index, pane.generation = ws, 0, 0
        pane.folders, pane.loading_folders, pane.limits, pane.matches, pane.size_cells = {}, set(), {}, set(), {}
        pane.result_filter, pane.volume_select, pane.tree = Mock(), Mock(), MagicMock()
        pane.render, pane.update_header = Mock(), Mock()
        tasks = []

        def schedule(coroutine):
            task = asyncio.create_task(coroutine)
            tasks.append(task)
            return task

        try:
            with patch('workspace_ui.ui.spinner') as spinner, patch('workspace_ui.background_tasks.create', side_effect=schedule):
                await asyncio.wait_for(pane.show_volume('disk'), timeout=.2)
                pane.render.assert_called_once()
                self.assertEqual(pane.folders['']['entries'][0]['path'], 'Album')
                await asyncio.wait_for(started.wait(), timeout=.2)
            release.set()
            await asyncio.gather(*tasks)
            self.assertNotIn('', pane.loading_folders)
        finally:
            release.set()
            for task in tasks:
                task.cancel()
