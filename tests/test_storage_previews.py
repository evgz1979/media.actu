import asyncio
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from PIL import Image

from media_manager.storage import StorageCatalog
from media_manager.storage_previews import StoragePreviewService
from storage_preview_ui import StoragePreview
from workspace_state import normalize_state, pane_snapshot
from workspace_ui import BrowserPane, StorageWorkspace


class StoragePreviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.disk = self.root / 'disk'
        self.disk.mkdir()
        self.mounted = [dict(id='disk', name='Disk', kind='external', mount_path=str(self.disk), device=self.disk.stat().st_dev)]
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.mounted)
        self.storage.refresh(True)
        self.service = StoragePreviewService(self.storage, self.root / 'cache')
        self.original = self.disk / 'photo.jpg'
        Image.new('RGB', (2000, 1000), 'navy').save(self.original)

    def test_derivatives_have_two_sizes_reuse_cache_and_leave_original_unchanged(self):
        before = self.original.stat()
        digest = hashlib.sha256(self.original.read_bytes()).hexdigest()
        small = self.service.get_or_create('disk', 'photo.jpg')
        large = self.service.get_or_create('disk', 'photo.jpg', large=True)
        with Image.open(small) as image:
            self.assertEqual(image.size, (320, 160))
        with Image.open(large) as image:
            self.assertEqual(image.size, (1600, 800))
        with patch('media_manager.storage_previews.Image.open', side_effect=AssertionError('Cache must be reused')):
            self.assertEqual(self.service.get_or_create('disk', 'photo.jpg'), small)
        self.assertTrue(small.is_relative_to(self.root / 'cache'))
        self.assertEqual(self.original.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(hashlib.sha256(self.original.read_bytes()).hexdigest(), digest)
        self.assertEqual(list(self.disk.iterdir()), [self.original])

    def test_replacement_invalidates_cache_and_tiles_do_not_discover_all_disks(self):
        first = self.service.get_or_create('disk', 'photo.jpg')
        Image.new('RGB', (2000, 1000), 'red').save(self.original)
        with patch.object(self.storage, 'discover', side_effect=AssertionError('Do not discover per tile')):
            second = self.service.get_or_create('disk', 'photo.jpg')
        self.assertNotEqual(first, second)
        with Image.open(second) as image:
            red, green, blue = image.getpixel((20, 20))
            self.assertGreater(red, blue)

    def test_absolute_paths_parent_traversal_symlinks_and_fifos_are_refused(self):
        outside = self.root / 'outside'
        outside.mkdir()
        Image.new('RGB', (20, 20)).save(outside / 'outside.jpg')
        (self.disk / 'linked.jpg').symlink_to(outside / 'outside.jpg')
        (self.disk / 'linked-folder').symlink_to(outside, target_is_directory=True)
        os.mkfifo(self.disk / 'pipe.jpg')
        for path in ('../outside/outside.jpg', str(outside / 'outside.jpg'), 'linked.jpg', 'linked-folder/outside.jpg', 'pipe.jpg'):
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                self.service.get_or_create('disk', path)
        self.assertFalse((self.root / 'cache').exists())

    def test_offline_or_replaced_disk_is_not_read_even_when_a_derivative_exists(self):
        self.service.get_or_create('disk', 'photo.jpg')
        self.mounted.clear()
        self.storage.refresh(True)
        with self.assertRaises(OSError):
            self.service.get_or_create('disk', 'photo.jpg')

    @unittest.skipUnless(shutil.which('ffmpeg'), 'Video fixture needs FFmpeg')
    def test_video_frame_from_checked_descriptor_and_macos_fallback(self):
        video = self.disk / 'clip.mp4'
        subprocess.run([shutil.which('ffmpeg'), '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=640x360:d=0.2',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(video)], check=True, capture_output=True)
        result = self.service.get_or_create('disk', 'clip.mp4')
        with Image.open(result) as image:
            self.assertEqual(image.size, (320, 180))
        if sys.platform == 'darwin':
            with patch('media_manager.storage_previews.shutil.which', return_value=None):
                native = self.service.get_or_create('disk', 'clip.mp4', large=True)
            with Image.open(native) as image:
                self.assertLessEqual(image.width, 1600)
                self.assertGreater(image.getpixel((10, 10))[2], 150)


class PreviewNavigationTests(unittest.IsolatedAsyncioTestCase):
    def preview(self):
        preview = StoragePreview.__new__(StoragePreview)
        preview.ws = SimpleNamespace(client=SimpleNamespace(is_deleted=False), persist_workspace=Mock(), error_text=str)
        preview.pane = SimpleNamespace(view_mode='preview', path_signature=None)
        preview.generation, preview.render = 0, Mock()
        return preview

    async def test_slow_folder_response_cannot_replace_a_newer_file_selection(self):
        preview = self.preview()
        started, release = asyncio.Event(), asyncio.Event()

        async def request(*args, **kwargs):
            started.set()
            await release.wait()
            return dict(entries=[{'name': 'old'}], volume={'availability': 'offline'})

        preview.ws.request = request
        task = asyncio.create_task(preview.show('disk', dict(path='Album', kind='directory')))
        await started.wait()
        await preview.show('disk', dict(path='Other/photo.jpg', kind='file'))
        release.set()
        await task
        self.assertEqual((preview.path, preview.kind, preview.data), ('Other/photo.jpg', 'file', None))
        self.assertFalse(preview.loading)

    async def test_only_opposite_preview_receives_selection_and_keeps_its_tree_state(self):
        source = SimpleNamespace(index=0, view_mode='tree', volume_id='disk', path='Album', kind='directory', entry=None)
        target = SimpleNamespace(view_mode='preview', volume_id='other', path='Saved/tree', expanded={'Saved/tree'},
                                 preview=SimpleNamespace(show=AsyncMock()))
        ws = SimpleNamespace(panes=[source, target])
        await StorageWorkspace.preview_selection(ws, source)
        target.preview.show.assert_awaited_once_with('disk', dict(path='Album', kind='directory', name='Album'))
        self.assertEqual((target.volume_id, target.path, target.expanded), ('other', 'Saved/tree', {'Saved/tree'}))
        target.view_mode = 'tree'
        target.preview.show.reset_mock()
        await StorageWorkspace.preview_selection(ws, source)
        target.preview.show.assert_not_awaited()

    async def test_modes_restore_without_changing_saved_tree_position(self):
        panes = [SimpleNamespace(view_mode='tree', index=i, volume_id='disk', root_path='Saved', path='Saved/file.jpg',
                                 kind='file', entry=None, mode_switch=Mock(), tree=Mock(), path_signature=None,
                                 volume_select=Mock(), render=Mock(),
                                 preview=SimpleNamespace(content=Mock(), generation=0, show=AsyncMock())) for i in range(2)]
        ws = SimpleNamespace(panes=panes, pair=SimpleNamespace(render_rail=Mock()), persist_workspace=Mock(), update_scopes=Mock())
        ws.client = SimpleNamespace(run_javascript=AsyncMock(return_value=None))
        for pane in panes:
            pane.workspace = ws
            pane.set_mode = lambda mode, p=pane: BrowserPane.set_mode(p, mode)
        await panes[1].set_mode('preview')
        self.assertEqual(panes[1].path, 'Saved/file.jpg')
        await panes[0].set_mode('preview')
        self.assertEqual([p.view_mode for p in panes], ['preview', 'tree'])
        self.assertEqual([p.path for p in panes], ['Saved/file.jpg', 'Saved/file.jpg'])

    def test_preview_path_is_saved_separately_and_validated(self):
        pane = dict(volume_id='disk', root_path='Saved', path='Saved/file.jpg', kind='file', view_mode='preview',
                    preview=dict(volume_id='other', path='Album/Photo.jpg', kind='file'))
        state = dict(version=1, panes=[pane_snapshot(pane), pane_snapshot({})])
        normalized = normalize_state(state)
        self.assertEqual(normalized['panes'][0]['path'], 'Saved/file.jpg')
        self.assertEqual(normalized['panes'][0]['preview']['path'], 'Album/Photo.jpg')
        state['panes'][0]['preview']['path'] = '../outside'
        self.assertIsNone(normalize_state(state))
