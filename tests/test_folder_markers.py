import errno
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from media_manager.comparison import ComparisonCatalog
from media_manager.copies import CopyCatalog
from media_manager.copy_files import MissingCopyCatalog
from media_manager.directory_sizes import DirectorySizeService
from media_manager.folder_markers import FOLDER_MARKER_LIMIT,FolderMarkerService,read_folder_marker,write_folder_marker
from media_manager.paired_comparison import PairedComparisonCatalog
from media_manager.storage import StorageCatalog
from media_manager.volume_identity import FOLDER_MARKER_NAME,mounted_root


class FolderMarkerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.mounted = []
        for name,folder in [('main','Original'),('copy','Backup'),('cold','Cold')]:
            mount = self.root/name
            (mount/folder).mkdir(parents=True)
            self.mounted.append(dict(id=name,name=name,kind='external',mount_path=str(mount),device=mount.stat().st_dev))
        (self.root/'main/Original/photo.jpg').write_bytes(b'photo')
        self.storage = StorageCatalog(self.root/'data/storage.sqlite3',lambda:self.mounted)
        for volume in self.mounted:
            self.storage.directory(volume['id'])
        self.copies = CopyCatalog(self.storage)
        self.group = self.copies.create_main('main','Original')
        self.copies.add_copy(self.group['id'],'copy','Backup')
        self.group = self.copies.add_copy(self.group['id'],'cold','Cold','cold')
        self.service = FolderMarkerService(self.copies)
        self.addCleanup(self.service.close)

    def sync(self):
        with self.storage.connect() as db:
            db.execute('UPDATE folder_marker_jobs SET next_check=0')
        self.service.reconcile()

    def marker(self,volume,path):
        with mounted_root(str(self.root/volume/path)) as root:
            return read_folder_marker(root)

    def job(self,identifier):
        with self.storage.connect() as db:
            return dict(db.execute('SELECT * FROM folder_marker_jobs WHERE location_id=?',(identifier,)).fetchone())

    def test_all_registered_roots_get_own_ids_and_readable_roles_without_changing_data(self):
        original = (self.root/'main/Original/photo.jpg').stat()
        self.sync()
        documents = [self.marker('main','Original'),self.marker('copy','Backup'),self.marker('cold','Cold')]
        locations = [self.group['main'],*self.group['copies']]
        self.assertEqual([d['label'] for d in documents],['00-main','01-copy','02-copy-cold'])
        self.assertEqual({d['group_id'] for d in documents},{self.group['id']})
        self.assertEqual([d['folder_id'] for d in documents],[location['id'] for location in locations])
        self.assertEqual(len({d['folder_id'] for d in documents}),3)
        self.assertEqual([d['role'] for d in documents],['main','copy','copy'])
        self.assertTrue(all(d['status']=='active' and d['name']=='Original' and d['updated_at'] for d in documents))
        self.assertEqual((self.root/'main/Original/photo.jpg').stat().st_mtime_ns,original.st_mtime_ns)
        self.assertEqual(self.service.status()['counts']['ready'],3)

    def test_rechecking_unchanged_markers_does_not_rewrite_the_files(self):
        self.sync()
        path = self.root/'main/Original'/FOLDER_MARKER_NAME
        before = path.stat().st_mtime_ns,path.read_bytes()
        self.copies.queue_folder_markers()
        self.sync()
        self.assertEqual((path.stat().st_mtime_ns,path.read_bytes()),before)

    def test_connection_kind_and_release_changes_reach_the_same_folder_marker(self):
        self.sync()
        first,cold = self.group['copies']
        self.copies.set_copy_connected(first['id'],False)
        self.copies.change_kind(first['id'],'cloud')
        self.copies.set_copy_connected(cold['id'],False)
        self.copies.release_copy_number(cold['id'],2,'cold')
        self.sync()
        self.assertEqual(self.marker('copy','Backup')['label'],'01-copy-cloud')
        self.assertEqual(self.marker('copy','Backup')['status'],'disconnected')
        self.assertEqual(self.marker('cold','Cold')['status'],'released')
        self.copies.set_copy_connected(cold['id'],True)
        self.sync()
        self.assertEqual(self.marker('cold','Cold')['status'],'active')
        self.assertEqual(self.marker('cold','Cold')['folder_id'],cold['id'])

    def test_offline_or_missing_folder_is_retried_without_creating_directories(self):
        cold = self.mounted.pop()
        self.storage.refresh(True)
        self.sync()
        identifier = self.group['copies'][1]['id']
        self.assertEqual(self.job(identifier)['state'],'pending')
        self.assertFalse((self.root/'cold/Cold'/FOLDER_MARKER_NAME).exists())
        (self.root/'cold/Cold').rmdir()
        self.mounted.append(cold)
        self.storage.refresh(True)
        self.sync()
        self.assertEqual(self.job(identifier)['state'],'pending')
        self.assertFalse((self.root/'cold/Cold').exists())
        (self.root/'cold/Cold').mkdir()
        self.sync()
        self.assertEqual(self.marker('cold','Cold')['folder_id'],identifier)

    def test_foreign_marker_symlink_fifo_and_oversized_file_are_preserved(self):
        identifier = self.group['copies'][0]['id']
        payload = json.loads(self.job(identifier)['payload'])
        foreign = json.dumps({**payload,'folder_id':uuid4().hex}).encode()
        path = self.root/'copy/Backup'/FOLDER_MARKER_NAME
        for content in (foreign,b'invalid JSON',b'x'*(FOLDER_MARKER_LIMIT+1)):
            with self.subTest(content=content[:20]):
                path.write_bytes(content)
                self.sync()
                self.assertEqual(self.job(identifier)['state'],'error')
                self.assertEqual(path.read_bytes(),content)
        path.unlink()
        target = self.root/'private'
        target.write_bytes(b'private')
        path.symlink_to(target)
        self.sync()
        self.assertEqual(target.read_bytes(),b'private')
        self.assertTrue(path.is_symlink())
        path.unlink()
        os.mkfifo(path)
        self.sync()
        self.assertEqual(self.job(identifier)['state'],'error')

    def test_failed_atomic_update_preserves_the_previous_document_and_cleans_temporary_files(self):
        self.sync()
        path = self.root/'copy/Backup'/FOLDER_MARKER_NAME
        before = path.read_bytes()
        self.copies.change_kind(self.group['copies'][0]['id'],'cloud')
        with patch('media_manager.folder_markers.os.replace',side_effect=PermissionError('No write access')):
            self.sync()
        self.assertEqual(path.read_bytes(),before)
        self.assertFalse(list(path.parent.glob('.media-actu-copy-*.part')))
        self.sync()
        self.assertEqual(self.marker('copy','Backup')['type'],'cloud')

    def test_metadata_change_during_a_write_keeps_the_newer_revision_pending(self):
        from media_manager import folder_markers
        original = folder_markers.write_folder_marker
        identifier = self.group['copies'][0]['id']
        changed = False
        def raced(root,payload,**kwargs):
            nonlocal changed
            if payload['folder_id']==identifier and not changed:
                changed = True
                self.copies.change_kind(identifier,'cloud')
            return original(root,payload,**kwargs)
        with patch.object(folder_markers,'write_folder_marker',side_effect=raced):
            self.sync()
        self.assertEqual(self.job(identifier)['state'],'pending')
        self.sync()
        self.assertEqual(self.marker('copy','Backup')['label'],'01-copy-cloud')

    def test_a_marker_appearing_during_creation_is_not_overwritten(self):
        payload = json.loads(self.job(self.group['copies'][0]['id'])['payload'])
        path = self.root/'copy/Backup'/FOLDER_MARKER_NAME
        foreign = json.dumps({**payload,'folder_id':uuid4().hex})
        with mounted_root(str(path.parent)) as root:
            with self.assertRaises(OSError):
                write_folder_marker(root,payload,before_publish=lambda:path.write_text(foreign))
        self.assertEqual(path.read_text(),foreign)
        self.assertFalse(list(path.parent.glob('.media-actu-copy-*.part')))

    def test_smb_exclusive_creation_fallback_still_never_overwrites_existing_files(self):
        with patch('media_manager.copy_files.publish_exclusive',side_effect=OSError(errno.ENOTSUP,'Unsupported')):
            self.sync()
        self.assertEqual(self.service.status()['counts']['ready'],3)
        self.assertFalse(list(self.root.rglob('.media-actu-copy-*.part')))

    def test_reusing_a_released_path_writes_the_new_identity_without_old_job_overwriting_it(self):
        self.sync()
        cold = self.group['copies'][1]
        self.copies.set_copy_connected(cold['id'],False)
        self.copies.release_copy_number(cold['id'],2,'cold')
        new = self.copies.add_copy(self.group['id'],'cold','Cold','cold')['copies'][1]
        self.sync()
        self.assertNotEqual(cold['id'],new['id'])
        self.assertEqual(self.marker('cold','Cold')['folder_id'],new['id'])
        self.assertEqual(self.job(cold['id'])['state'],'superseded')
        self.assertEqual(self.job(new['id'])['state'],'ready')

    def test_existing_catalog_backfill_and_pending_changes_survive_restart(self):
        with self.storage.connect() as db:
            db.execute('DELETE FROM folder_marker_jobs')
        reopened = CopyCatalog(StorageCatalog(self.storage.database,lambda:self.mounted))
        reopened.queue_folder_markers()
        reopened.storage.refresh(True)
        service = FolderMarkerService(reopened)
        self.addCleanup(service.close)
        service.reconcile()
        self.assertEqual(service.status()['counts']['ready'],3)

    def test_only_the_latest_binding_can_describe_a_path_with_several_old_generations(self):
        self.sync()
        old = self.group['copies'][1]
        self.copies.set_copy_connected(old['id'],False)
        self.copies.release_copy_number(old['id'],2,'cold')
        new = self.copies.add_copy(self.group['id'],'cold','Cold','cold')['copies'][1]
        self.copies.set_copy_connected(new['id'],False)
        self.copies.release_copy_number(new['id'],2,'cold')
        self.sync()
        self.assertEqual(self.marker('cold','Cold')['folder_id'],new['id'])
        self.assertEqual(self.marker('cold','Cold')['status'],'released')
        self.assertEqual(self.job(old['id'])['state'],'superseded')

    def test_deleted_bindings_are_marked_removed_without_deleting_source_files(self):
        self.sync()
        self.copies.remove_group(self.group['id'])
        self.sync()
        self.assertEqual(self.marker('main','Original')['status'],'removed')
        self.assertEqual(self.marker('copy','Backup')['status'],'removed')
        self.assertEqual((self.root/'main/Original/photo.jpg').read_bytes(),b'photo')

    def test_unverified_volume_never_receives_folder_writes(self):
        self.mounted[2]['identity_status'] = 'unverified'
        self.storage.refresh(True)
        self.sync()
        job = self.job(self.group['copies'][1]['id'])
        self.assertEqual(job['state'],'pending')
        self.assertIn('подтверждения',job['error'])
        self.assertFalse((self.root/'cold/Cold'/FOLDER_MARKER_NAME).exists())

    def test_service_files_are_excluded_from_lists_sizes_both_comparisons_and_data_copying(self):
        (self.root/'main/Original/Sub').mkdir()
        (self.root/'main/Original/Sub/data.txt').write_bytes(b'data')
        self.sync()
        document = (self.root/'main/Original'/FOLDER_MARKER_NAME).read_bytes()
        for name in (FOLDER_MARKER_NAME,'._'+FOLDER_MARKER_NAME):
            (self.root/'main/Original/Sub'/name).write_bytes(document)
        self.assertEqual([entry['name'] for entry in self.storage.directory('main','Original/Sub')['entries']],['data.txt'])
        sizes = DirectorySizeService(self.storage)
        self.addCleanup(sizes.close)
        sizes.calculate('main','Original')
        self.assertEqual(sizes.request('main',['Original'],start=False)['sizes']['Original']['bytes'],9)
        legacy = ComparisonCatalog(self.storage)
        self.addCleanup(legacy.close)
        job = legacy.create({'volume_id':'main','path':'Original'},[{'volume_id':'copy','path':'Backup'}],background=False,reuse_index=False)
        legacy.run(job['id'])
        with self.storage.connect() as db:
            self.assertFalse(any('media-actu-folder' in row['name'] for row in db.execute('SELECT name FROM comparison_entries')))
        pairs = PairedComparisonCatalog(self.storage,self.copies)
        self.addCleanup(pairs.close)
        transfers = MissingCopyCatalog(pairs)
        copy = self.group['copies'][0]
        folders = pairs.create(copy['id'],background=False)
        pairs.run(folders['id'])
        files = pairs.create(copy['id'],'files',folders['id'],background=False)
        pairs.run(files['id'])
        plan = transfers.plan(files['id'])
        transfers.start(plan['id'],background=False)
        transfers.run(plan['id'],recheck=False)
        self.assertEqual(transfers.job(plan['id'])['errors'],0)
        self.assertEqual(self.marker('copy','Backup')['folder_id'],copy['id'])
        self.assertNotEqual(self.marker('copy','Backup')['folder_id'],self.marker('main','Original')['folder_id'])
        self.assertEqual((self.root/'copy/Backup/Sub/data.txt').read_bytes(),b'data')
        self.assertFalse((self.root/'copy/Backup/Sub'/FOLDER_MARKER_NAME).exists())
