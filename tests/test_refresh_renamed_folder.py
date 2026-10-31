import errno
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch

from media_manager.storage import StorageCatalog
from workspace_ui import BrowserPane,StorageWorkspace


class RefreshRenamedFolderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.disk = self.root/'disk'
        (self.disk/'Old/Sub').mkdir(parents=True)
        (self.disk/'Sibling').mkdir()
        (self.disk/'Old/Sub/photo.jpg').write_bytes(b'photo')
        volumes = [dict(id='disk',name='Disk',kind='external',mount_path=str(self.disk),device=self.disk.stat().st_dev)]
        self.storage = StorageCatalog(self.root/'storage.sqlite3',lambda:volumes)
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.client,ws.pair,ws.report = SimpleNamespace(is_deleted=False),SimpleNamespace(active=False,views={}),None
        ws.size_force,ws.directory_sizes = set(),{'disk':{}}
        ws.format_bytes,ws.format_date = str,str
        ws.set_active,ws.update_scopes = Mock(),Mock()
        self.requested = []
        async def request(method,url,*,params,**kwargs):
            self.requested.append(params['path'])
            return self.storage.directory('disk',params['path'],refresh=params['refresh'],discover=params.get('discover',True))
        ws.request,ws.error_text = request,str
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace,pane.index,pane.volume_id = ws,1,'disk'
        pane.root_path,pane.path,pane.kind,pane.entry = '','Old','directory',None
        pane.scan,pane.generation,pane.refreshing = None,1,False
        pane.folders = {path:self.storage.directory('disk',path) for path in ('','Old','Old/Sub')}
        pane.expanded,pane.size_cells = {'','Old','Old/Sub'},{}
        pane.folder_size,pane.refresh_button,pane.render = Mock(),Mock(),Mock()
        ws.panes = [pane]
        self.pane,self.ws = pane,ws
        self.notify = patch('workspace_ui.ui.notify').start()
        self.addCleanup(patch.stopall)

    async def test_refresh_shows_new_names_and_leaves_the_missing_selection_at_its_parent(self):
        before = self.storage.directory('disk','Old',refresh=False)
        (self.disk/'Old').rename(self.disk/'New')
        (self.disk/'Sibling').rename(self.disk/'RenamedSibling')
        await self.pane.refresh()
        self.assertEqual([e['name'] for e in self.pane.folders['']['entries']],['New','RenamedSibling'])
        self.assertEqual((self.pane.path,self.pane.kind),('','directory'))
        self.assertNotIn('Old',self.requested)
        self.assertFalse(self.ws.size_force)
        self.assertEqual(self.storage.directory('disk','Old',refresh=False)['scanned_at'],before['scanned_at'])
        self.assertTrue(any('родительский' in call.args[0] for call in self.notify.call_args_list))
        self.ws.update_scopes.assert_called()

    async def test_a_renamed_browser_root_falls_back_to_a_readable_parent(self):
        self.pane.root_path = 'Old'
        (self.disk/'Old').rename(self.disk/'New')
        await self.pane.refresh()
        self.assertEqual((self.pane.root_path,self.pane.path),('',''))
        self.assertEqual(self.requested,['Old',''])
        self.assertIn('New',[entry['name'] for entry in self.pane.folders['']['entries']])

    async def test_renamed_nested_parent_falls_back_to_nearest_existing_ancestor(self):
        self.pane.path = 'Old/Sub'
        (self.disk/'Old/Sub').rename(self.disk/'Old/Renamed')
        await self.pane.refresh()
        self.assertEqual(self.pane.path,'Old')
        self.assertEqual(self.requested,['','Old'])
        self.assertEqual(self.pane.folders['Old']['entries'][0]['name'],'Renamed')

    async def test_refresh_of_an_existing_folder_also_updates_its_parent_listing(self):
        (self.disk/'Sibling').rename(self.disk/'NewSibling')
        with patch.object(self.storage,'discover',wraps=self.storage.discover) as discover:
            await self.pane.refresh()
        self.assertEqual(discover.call_count,1)
        self.assertEqual(self.pane.path,'Old')
        self.assertEqual(self.requested,['','Old'])
        self.assertIn('NewSibling',[entry['name'] for entry in self.pane.folders['']['entries']])
        self.assertEqual(self.ws.size_force,{('disk','Old')})

    async def test_permissions_failure_keeps_cached_entries_and_does_not_claim_the_folder_disappeared(self):
        with patch.object(self.storage,'_read_directory',side_effect=PermissionError(errno.EACCES,'No access')):
            await self.pane.refresh()
        self.assertEqual(self.pane.path,'Old')
        self.assertEqual(self.pane.folders['']['error_code'],'read_failed')
        self.assertTrue(self.pane.folders['']['cached'])
        self.assertFalse(self.ws.size_force)
        self.assertIn('No access',self.notify.call_args.args[0])

    async def test_a_renamed_file_clears_old_selection_and_updates_the_list(self):
        self.pane.path,self.pane.kind = 'Old/Sub/photo.jpg','file'
        (self.disk/'Old/Sub/photo.jpg').rename(self.disk/'Old/Sub/new.jpg')
        await self.pane.refresh()
        self.assertEqual((self.pane.path,self.pane.kind),('Old/Sub','directory'))
        self.assertEqual(self.pane.folders['Old/Sub']['entries'][0]['name'],'new.jpg')
