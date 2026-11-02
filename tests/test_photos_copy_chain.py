import json
import os
import unittest
from unittest.mock import patch

from media_manager.photos_originals import PhotosOriginals
from media_manager.photos_adapter import PhotosLibraryUnavailable
from tests import test_photos_originals as fixture


class PhotosCopyChainTests(unittest.TestCase):
    def setUp(self):
        fixture.PhotosOriginalsTests.setUp(self)
        self.hdd = self.link
        self.original = fixture.PhotosOriginalsTests.run_copy(self)
        self.nvme_disk = self.root/'nvme'
        self.nvme_copy = self.nvme_disk/'Apple/evgz'
        self.nvme_copy.mkdir(parents=True)
        self.mounted.append(dict(id='nvme',name='NVMe',kind='external',mount_path=str(self.nvme_disk),device=self.nvme_disk.stat().st_dev))
        self.storage.refresh(True)
        self.nvme = self.libraries.bind_copy(self.source_id,'nvme','Apple/evgz')
        self.libraries.make_first_copy(self.source_id,self.nvme['id'])
        self.libraries.set_copy_source(self.source_id,self.hdd['id'],self.nvme['id'])
        self.adapter.requests.clear()

    def run_chain(self):
        return self.service.start(self.nvme['id'],background=False)

    def test_existing_hdd_originals_seed_nvme_without_photos_download_or_hdd_rewrite(self):
        before = {p.name:(p.stat().st_mtime_ns,p.read_bytes()) for p in self.copy.rglob('*') if p.is_file()}
        result = self.run_chain()
        self.assertEqual(result['state'],'completed',result)
        self.assertEqual(self.adapter.requests,[])
        self.assertEqual(result['done_resources'],3)
        self.assertEqual({p.name:(p.stat().st_mtime_ns,p.read_bytes()) for p in self.copy.rglob('*') if p.is_file()},before)
        self.assertEqual(len([p for p in self.nvme_copy.rglob('*') if p.is_file()]),3)
        copies = self.libraries.list()['libraries'][0]['copies']
        self.assertEqual([(c['volume_id'],c['number'],c['source_label']) for c in copies],[('nvme',1,'Photos'),('disk',2,'01-copy')])

    def test_new_original_downloaded_once_then_copied_to_hdd_and_restart_preserves_progress(self):
        self.run_chain()
        manifest = self.adapter.original_manifest
        self.adapter.content[('c','1:0')] = b'new original'
        def added(anchors,receive,stopped):
            manifest(anchors,receive,stopped)
            receive(dict(id='c',version='v1',created_at='2021-01-01T00:00:00Z',resources=[dict(id='1:0',name='NEW.JPG')]))
        self.adapter.original_manifest = added
        result = self.run_chain()
        self.assertEqual(result['done_assets'],3,result)
        self.assertEqual(self.adapter.requests,[('c','1:0')])
        self.assertEqual((self.copy/'2021/2021-01/NEW.JPG').read_bytes(),b'new original')
        self.assertEqual(self.service.summary(self.hdd['id'],raw=True)['done_assets'],3)
        reopened = PhotosOriginals(self.libraries,self.adapter)
        self.addCleanup(reopened.close)
        self.adapter.requests.clear()
        self.assertEqual(reopened.start(self.hdd['id'],background=False)['done_assets'],3)
        self.assertEqual(self.adapter.requests,[])

    def test_missing_known_hdd_file_waits_instead_of_redownloading_it(self):
        (self.copy/'2020/2020-02/IMG_1.JPG').unlink()
        result = self.run_chain()
        self.assertEqual(result['state'],'waiting',result)
        self.assertEqual(self.adapter.requests,[])

    def test_cycle_is_rejected_and_receipts_keep_their_ids_when_renumbered(self):
        with self.assertRaises(ValueError):
            self.libraries.set_copy_source(self.source_id,self.nvme['id'],self.hdd['id'])
        with self.catalog.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM photos_copy_files WHERE link_id=?',(self.hdd['id'],)).fetchone()[0],3)

    def test_pause_during_hdd_to_nvme_transfer_recovers_without_network(self):
        write = self.service._write
        def pause(fd,data):
            write(fd,data)
            self.service.pause(self.nvme['id'])
        with patch.object(self.service,'_write',side_effect=pause):
            result = self.run_chain()
        self.assertEqual(result['state'],'paused',result)
        self.assertEqual(self.adapter.requests,[])
        result = self.run_chain()
        self.assertEqual(result['done_resources'],3,result)
        self.assertEqual(self.adapter.requests,[])

    def add_assets(self, identifiers):
        manifest = self.adapter.original_manifest
        for identifier in identifiers:
            self.adapter.content[(identifier,'1:0')] = ('original '+identifier).encode()
        def added(anchors,receive,stopped):
            manifest(anchors,receive,stopped)
            for identifier in identifiers:
                receive(dict(id=identifier,version='v1',created_at='2021-01-01T00:00:00Z',resources=[dict(id='1:0',name=identifier+'.JPG')]))
        self.adapter.original_manifest = added

    def test_replication_happens_before_all_photos_downloads_finish(self):
        self.run_chain()
        self.add_assets(['c','d'])
        def before():
            if self.adapter.requests[-1]==('d','1:0'):
                self.assertTrue((self.copy/'2021/2021-01/c.JPG').exists())
        self.adapter.before_write = before
        with patch('media_manager.photos_originals.COPY_BATCH_RESOURCES',1):
            result = self.run_chain()
        self.assertEqual(result['done_assets'],4,result)
        self.assertEqual(self.adapter.requests,[('c','1:0'),('d','1:0')])
        self.assertEqual(self.service.summary(self.hdd['id'],raw=True)['done_assets'],4)

    def test_offline_second_copy_does_not_redirect_downloads_or_block_first_copy(self):
        self.run_chain()
        self.add_assets(['c'])
        hdd = self.mounted.pop(0)
        self.storage.refresh(True)
        result = self.run_chain()
        self.assertEqual(result['state'],'completed',result)
        self.assertEqual(self.adapter.requests,[('c','1:0')])
        self.assertEqual(self.service.summary(self.hdd['id'],raw=True)['state'],'waiting')
        self.mounted.append(hdd)
        self.storage.refresh(True)
        self.adapter.requests.clear()
        result = self.run_chain()
        self.assertEqual(self.adapter.requests,[])
        self.assertEqual((self.copy/'2021/2021-01/c.JPG').read_bytes(),b'original c')

    def test_source_metadata_change_blocks_seed_without_photos_fallback(self):
        target = self.copy/'2020/2020-02/IMG_1.JPG'
        target.write_bytes(b'changed by user')
        result = self.run_chain()
        self.assertEqual(result['state'],'waiting',result)
        self.assertEqual(self.adapter.requests,[])

    def test_pause_during_replica_inventory_leaves_no_stuck_running_job(self):
        inventory = self.service._inventory
        def stop(job,link,volume):
            if link['id']==self.hdd['id']:
                self.service.pause(self.nvme['id'])
            return inventory(job,link,volume)
        with patch.object(self.service,'_inventory',side_effect=stop):
            result = self.run_chain()
        self.assertEqual(result['state'],'paused',result)
        with self.catalog.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone()[0],0)
        self.assertEqual(self.run_chain()['done_resources'],3)
        self.assertEqual(self.adapter.requests,[])
