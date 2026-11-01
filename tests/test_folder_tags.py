import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from media_manager.storage import StorageCatalog
from workspace_ui import StorageWorkspace


class FolderTagTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.disk = self.root / 'disk'
        (self.disk / 'Parent/Child').mkdir(parents=True)
        (self.disk / 'file.txt').write_text('user data')
        (self.disk / 'link').symlink_to(self.disk / 'Parent', target_is_directory=True)
        self.mounted = [dict(id='disk', name='Disk', kind='external', mount_path=str(self.disk), device=self.disk.stat().st_dev)]
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.mounted)
        self.storage.directory('disk')
        self.storage.directory('disk', 'Parent')

    def test_multiple_tags_persist_without_changing_annotations_or_original_files(self):
        self.storage.annotate('disk', 'Parent', dict(purpose='media', no_duplicate=True, comment='keep me'))
        before = {str(p): (p.lstat().st_mtime_ns, p.lstat().st_size) for p in self.disk.rglob('*')}
        result = self.storage.set_folder_tags('disk', 'Parent', ['check', 'old_copy', 'sort'])
        self.assertEqual(result['tags'], ['old_copy', 'sort', 'check'])
        self.assertEqual(result['own']['comment'], 'keep me')
        self.assertTrue(result['effective']['no_duplicate'])
        reopened = StorageCatalog(self.storage.database, lambda: [])
        self.assertEqual(reopened.metadata('disk', 'Parent')['tags'], result['tags'])
        self.assertEqual(before, {str(p): (p.lstat().st_mtime_ns, p.lstat().st_size) for p in self.disk.rglob('*')})

    def test_tags_apply_only_to_the_selected_folder_and_update_cached_listings(self):
        self.storage.set_folder_tags('disk', 'Parent', ['sort', 'check'])
        self.assertEqual(self.storage.metadata('disk', 'Parent/Child')['tags'], [])
        with patch.object(self.storage, '_read_directory', side_effect=AssertionError('metadata only')):
            listing = self.storage.directory('disk', refresh=False)
        parent = next(e for e in listing['entries'] if e['path'] == 'Parent')
        self.assertEqual(parent['metadata']['tags'], ['sort', 'check'])
        self.storage.annotate('disk', 'Parent', dict(comment='edited separately'))
        self.assertEqual(self.storage.metadata('disk', 'Parent')['tags'], ['sort', 'check'])
        self.assertEqual(self.storage.set_folder_tags('disk', 'Parent', [])['tags'], [])
        self.assertEqual(self.storage.metadata('disk', 'Parent')['own']['comment'], 'edited separately')

    def test_system_and_unknown_tags_are_rejected_without_changing_existing_tags(self):
        self.storage.set_folder_tags('disk', 'Parent', ['old_copy'])
        for tags in [['media_library'], ['медиатека'], ['unknown'], 'sort', [None]]:
            with self.subTest(tags=tags), self.assertRaises(ValueError):
                self.storage.set_folder_tags('disk', 'Parent', tags)
        self.assertEqual(self.storage.metadata('disk', 'Parent')['tags'], ['old_copy'])

    def test_files_symlinks_unknown_paths_and_traversal_cannot_receive_folder_tags(self):
        for path in ('file.txt', 'link', 'missing', '../escape', '/etc', '\x00'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.storage.set_folder_tags('disk', path, ['check'])
        self.assertEqual(self.storage.set_folder_tags('disk', '', ['check'])['tags'], ['check'])
        self.mounted[0]['identity_status'] = 'unverified'
        self.storage.refresh(True)
        with self.assertRaises(ValueError):
            self.storage.set_folder_tags('disk', 'Parent', ['sort'])

    def test_old_database_gains_tag_table_without_losing_existing_metadata(self):
        self.storage.annotate('disk', 'Parent', dict(comment='old metadata'))
        with self.storage.connect() as db:
            db.execute('DROP TABLE directory_tags')
        reopened = StorageCatalog(self.storage.database, lambda: self.mounted)
        self.assertEqual(reopened.metadata('disk', 'Parent')['own']['comment'], 'old metadata')
        self.assertEqual(reopened.set_folder_tags('disk', 'Parent', ['check'])['tags'], ['check'])

    def test_tags_do_not_transfer_to_another_disk_at_the_same_mount_point(self):
        self.storage.set_folder_tags('disk', 'Parent', ['old_copy'])
        self.mounted[0]['id'] = 'replacement'
        self.storage.refresh(True)
        self.assertEqual(self.storage.metadata('replacement', 'Parent')['tags'], [])
        self.assertEqual(self.storage.metadata('disk', 'Parent')['tags'], ['old_copy'])

    def test_api_supports_multiple_tags_and_forbids_the_automatic_library_tag(self):
        import asyncio
        import httpx
        with patch.dict(os.environ, MEDIA_ACTU_DATA_DIR=str(self.root / 'api-data')):
            import app as core
        async def exercise():
            with patch.object(core, 'storage', self.storage):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app), base_url='http://test') as client:
                    url = '/api/storage/volumes/disk/folder-tags'
                    response = await client.patch(url, json=dict(path='Parent', tags=['sort', 'check']))
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertEqual(response.json()['tags'], ['sort', 'check'])
                    response = await client.patch(url, json=dict(path='Parent', tags=['media_library']))
                    self.assertEqual(response.status_code, 422)
                    self.assertEqual((await client.patch(url, json=dict(path='file.txt', tags=['check']))).status_code, 400)
                    self.assertEqual((await client.patch(url.replace('/disk/', '/missing/'), json=dict(path='Parent', tags=[]))).status_code, 404)
        asyncio.run(exercise())
        self.assertEqual(self.storage.metadata('disk', 'Parent')['tags'], ['sort', 'check'])

    def test_saved_tag_changes_update_both_open_trees_without_reloading_directories(self):
        panes = [SimpleNamespace(volume_id='disk', view_mode='tree', render=Mock(),
                 folders={'': dict(path='', entries=[dict(path='Parent', metadata={'tags': []})])}) for _ in range(2)]
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.volumes, ws.panes = [dict(id='disk')], panes
        metadata = self.storage.set_folder_tags('disk', 'Parent', ['sort'])
        ws.apply_folder_tags('disk', 'Parent', metadata)
        for pane in panes:
            self.assertEqual(pane.folders['']['entries'][0]['metadata']['tags'], ['sort'])
            pane.render.assert_called_once()
