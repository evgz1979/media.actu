from __future__ import annotations

import json
import asyncio
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from media_manager.comparison import ComparisonCatalog, open_readonly
from media_manager.copies import CopyCatalog
from media_manager.storage import StorageCatalog, discover_volumes, volume_key
from media_manager.volume_identity import (
    MARKER_FILES, MARKER_LIMIT, MARKER_NAME, create_marker, mounted_root, read_capacity, read_marker, rename_marker,
)


class VolumeIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.disk = self.root / 'disk'
        self.disk.mkdir()
        (self.disk / 'photo.jpg').write_bytes(b'original')
        self.active = []
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.active)

    def discover(self, disk=None, share='usbshare1', host='TNAS-Z._smb._tcp.local'):
        disk = disk or self.disk
        output = f'//alice@{host}/{share} on /Volumes/{share} (smbfs, nodev, nosuid)\n'
        device = disk.stat().st_dev
        with patch('media_manager.storage.subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout=output)), \
                patch('media_manager.storage.os.stat', return_value=SimpleNamespace(st_dev=device)), \
                patch('media_manager.storage.mounted_root', side_effect=lambda *_: mounted_root(str(disk), device)):
            volume = discover_volumes()[0]
        volume['mount_path'] = str(disk)
        return volume

    def register(self, name='Архив фото'):
        self.active = [self.discover()]
        # Production discovery rereads the file after creation, just like this provider.
        self.storage.discover = lambda: [self.discover()]
        return self.storage.register_removable(self.active[0]['id'], name)

    def test_registration_writes_only_marker_and_survives_share_alias_restart(self):
        original = (self.disk / 'photo.jpg').stat()
        registered = self.register()
        self.assertTrue(registered['removable'])
        self.assertEqual(registered['identity_status'], 'verified')
        self.assertEqual(registered['name'], 'Архив фото')
        self.assertEqual({p.name for p in self.disk.iterdir()}, {'photo.jpg', MARKER_NAME})
        self.assertEqual((self.disk / 'photo.jpg').read_bytes(), b'original')
        self.assertEqual((self.disk / 'photo.jpg').stat().st_mtime_ns, original.st_mtime_ns)
        self.storage.directory(registered['id'])
        self.storage.annotate(registered['id'], '', {'role': 'archive'})
        moved = self.discover(share='usbshare2', host='tnas-z.local')
        self.assertEqual(moved['id'], registered['id'])
        reopened = StorageCatalog(self.storage.database, lambda: [moved])
        self.assertEqual(reopened.refresh(True)['volumes'][0]['metadata']['effective']['role'], 'archive')
        self.assertEqual([e['name'] for e in reopened.directory(registered['id'])['entries']], ['photo.jpg'])

    def test_other_disk_at_same_share_cannot_inherit_history(self):
        first = self.register()
        self.storage.directory(first['id'])
        self.storage.annotate(first['id'], '', {'role': 'archive'})
        second_disk = self.root / 'second'
        second_disk.mkdir()
        create_marker(str(second_disk), second_disk.stat().st_dev, 'Другой диск')
        second = self.discover(second_disk)
        with self.storage.connect() as db:
            db.execute('INSERT INTO volume_aliases VALUES (?,?)', (second['id'], first['id']))
        self.storage.discover = lambda: [second]
        volumes = {v['id']: v for v in self.storage.refresh(True)['volumes']}
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual(volumes[first['id']]['availability'], 'offline')
        self.assertEqual(volumes[second['id']]['metadata']['effective']['role'], '')
        self.assertIsNone(self.storage.directory(second['id'], refresh=False)['scanned_at'])
        self.storage.discover = lambda: [self.discover()]
        returned = {v['id']: v for v in self.storage.refresh(True)['volumes']}
        self.assertEqual(returned[first['id']]['availability'], 'online')
        self.assertEqual(returned[first['id']]['metadata']['effective']['role'], 'archive')

    def test_rename_preserves_marker_history_and_folder_connections_after_restart(self):
        registered = self.register()
        marker_path = self.disk / MARKER_NAME
        document = json.loads(marker_path.read_text())
        document['custom'] = {'keep': True}
        marker_path.write_text(json.dumps(document))
        (self.disk / 'Album').mkdir()
        snapshot = self.storage.directory(registered['id'])
        self.storage.annotate(registered['id'], '', {'role': 'archive', 'comment': 'keep'})
        copies = CopyCatalog(self.storage)
        group = copies.create_main(registered['id'], 'Album')
        copies.set_group_connected(group['id'], False)
        original = (self.disk / 'photo.jpg').stat()

        renamed = self.storage.rename_removable(registered['id'], '  WD_old_2Tb  ')

        self.assertEqual(renamed['id'], registered['id'])
        self.assertEqual(renamed['name'], 'WD_old_2Tb')
        self.assertEqual(json.loads(marker_path.read_text()), {**document, 'name': 'WD_old_2Tb'})
        self.assertEqual({p.name for p in self.disk.iterdir()}, {'photo.jpg', 'Album', MARKER_NAME})
        self.assertEqual((self.disk / 'photo.jpg').stat().st_mtime_ns, original.st_mtime_ns)
        reopened = StorageCatalog(self.storage.database, lambda: [self.discover(share='usbshare2')])
        remembered = next(v for v in reopened.refresh(True)['volumes'] if v['id'] == registered['id'])
        self.assertEqual(remembered['name'], 'WD_old_2Tb')
        self.assertEqual(remembered['metadata']['effective']['role'], 'archive')
        self.assertEqual(remembered['metadata']['own']['comment'], 'keep')
        self.assertEqual(reopened.directory(registered['id'], refresh=False)['scanned_at'], snapshot['scanned_at'])
        remembered_group = CopyCatalog(reopened).groups()[0]
        self.assertEqual(remembered_group['id'], group['id'])
        self.assertEqual(remembered_group['main']['volume_name'], 'WD_old_2Tb')
        self.assertFalse(remembered_group['connected'])
        reopened.discover = lambda: []
        offline = next(v for v in reopened.refresh(True)['volumes'] if v['id'] == registered['id'])
        self.assertEqual(offline['name'], 'WD_old_2Tb')

    def test_rename_rejects_offline_unregistered_and_duplicate_disks(self):
        pending = self.discover()
        self.active = [pending]
        with self.assertRaises(ValueError):
            self.storage.rename_removable(pending['id'], 'new name')
        self.assertFalse((self.disk / MARKER_NAME).exists())
        registered = self.register()
        original = (self.disk / MARKER_NAME).read_bytes()
        self.storage.discover = lambda: []
        with self.assertRaises(ValueError):
            self.storage.rename_removable(registered['id'], 'new name')
        duplicate = self.root / 'duplicate'
        duplicate.mkdir()
        shutil.copyfile(self.disk / MARKER_NAME, duplicate / MARKER_NAME)
        self.storage.discover = lambda: [self.discover(), self.discover(duplicate, share='usbshare2')]
        with self.assertRaises(ValueError):
            self.storage.rename_removable(registered['id'], 'new name')
        self.assertEqual((self.disk / MARKER_NAME).read_bytes(), original)

    def test_failed_rename_leaves_original_marker_intact_and_removes_temporary(self):
        registered = self.register()
        original = (self.disk / MARKER_NAME).read_bytes()
        for operation in ('fsync', 'replace'):
            with self.subTest(operation=operation), \
                    patch('media_manager.volume_identity.os.' + operation, side_effect=OSError('write failed')):
                with self.assertRaises(OSError):
                    rename_marker(str(self.disk), self.disk.stat().st_dev, registered['marker_id'], 'new name')
            self.assertEqual((self.disk / MARKER_NAME).read_bytes(), original)
            self.assertEqual({p.name for p in self.disk.iterdir()}, {'photo.jpg', MARKER_NAME})

    def test_rename_rejects_changed_identity_symlink_and_invalid_names(self):
        registered = self.register()
        original = (self.disk / MARKER_NAME).read_bytes()
        for name in ('', '   ', 'bad\nname', 'x' * 121):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.storage.rename_removable(registered['id'], name)
        self.assertEqual((self.disk / MARKER_NAME).read_bytes(), original)
        (self.disk / MARKER_NAME).unlink()
        replacement = create_marker(str(self.disk), self.disk.stat().st_dev, 'other disk')
        with self.assertRaises(OSError):
            rename_marker(str(self.disk), self.disk.stat().st_dev, registered['marker_id'], 'new name')
        target = self.root / 'private-marker'
        (self.disk / MARKER_NAME).rename(target)
        (self.disk / MARKER_NAME).symlink_to(target)
        with self.assertRaises(OSError):
            rename_marker(str(self.disk), self.disk.stat().st_dev, replacement['id'], 'new name')
        self.assertEqual(json.loads(target.read_text())['name'], 'other disk')

    def test_concurrent_marker_change_is_not_overwritten(self):
        registered = self.register()
        from media_manager import volume_identity
        read_document = volume_identity._read_marker_document
        calls = 0

        def change_before_publication(root):
            nonlocal calls
            calls += 1
            if calls == 2:
                marker_path = self.disk / MARKER_NAME
                document = json.loads(marker_path.read_text())
                marker_path.write_text(json.dumps({**document, 'name': 'from another client'}))
            return read_document(root)

        with patch.object(volume_identity, '_read_marker_document', side_effect=change_before_publication):
            with self.assertRaises(OSError):
                rename_marker(str(self.disk), self.disk.stat().st_dev, registered['marker_id'], 'new name')
        self.assertEqual(json.loads((self.disk / MARKER_NAME).read_text())['name'], 'from another client')
        self.assertEqual({p.name for p in self.disk.iterdir()}, {'photo.jpg', MARKER_NAME})

    def test_rename_api_validates_requests_and_updates_the_same_volume(self):
        import httpx
        with patch.dict(os.environ, {'MEDIA_ACTU_DATA_DIR': str(self.root / 'api-data')}):
            import app as core
        registered = self.register()

        async def exercise():
            with patch.object(core, 'storage', self.storage):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app), base_url='http://test') as client:
                    url = '/api/storage/volumes/' + registered['id'] + '/name'
                    for payload, status in [({'name': ''}, 422), ({'name': '   '}, 400),
                                            ({'name': 'new', 'id': 'replace'}, 422)]:
                        response = await client.patch(url, json=payload)
                        self.assertEqual(response.status_code, status, response.text)
                    self.assertEqual(json.loads((self.disk / MARKER_NAME).read_text())['name'], registered['name'])
                    response = await client.patch(url, json={'name': 'Новое имя'})
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertEqual(response.json()['id'], registered['id'])
                    self.assertEqual(response.json()['name'], 'Новое имя')
                    self.storage.discover = lambda: []
                    response = await client.patch(url, json={'name': 'Отключён'})
                    self.assertEqual(response.status_code, 400, response.text)
                    self.assertEqual(json.loads((self.disk / MARKER_NAME).read_text())['name'], 'Новое имя')

        asyncio.run(exercise())

    def test_unregistered_disk_does_not_use_legacy_share_history(self):
        old_id = volume_key('smbfs:tnas-z._smb._tcp.local/usbshare1')
        with self.storage.connect() as db:
            db.execute('INSERT INTO volumes VALUES (?,?,?,?,?,?)', (old_id, 'usbshare1', str(self.disk), 'network', 'before', 'before'))
            db.execute('INSERT INTO directories VALUES (?,?,?,?)', (old_id, '', 'before', '[]'))
            db.execute('INSERT INTO annotations VALUES (?,?,?,?,?,?,?)', (old_id, '', '', 'archive', None, None, 'keep'))
        current = self.discover()
        self.active = [current]
        volumes = {v['id']: v for v in self.storage.refresh(True)['volumes']}
        self.assertEqual(volumes[old_id]['availability'], 'offline')
        self.assertEqual(volumes[old_id]['identity_status'], 'legacy')
        self.assertEqual(volumes[current['id']]['identity_status'], 'unverified')
        self.assertTrue(volumes[current['id']]['mounted'])
        self.assertEqual(volumes[current['id']]['availability'], 'unknown')
        with patch.object(self.storage, '_read_directory', side_effect=AssertionError('must not read unregistered disk')):
            result = self.storage.directory(current['id'])
        self.assertIsNone(result['scanned_at'])
        self.assertIn('не подтверждён', result['error'])
        with self.assertRaises(ValueError):
            self.storage.annotate(current['id'], '', {'role': 'copy'})
        self.assertEqual(self.storage.directory(old_id)['scanned_at'], 'before')
        self.assertEqual(self.storage.metadata(old_id, '')['effective']['role'], 'archive')
        comparison = ComparisonCatalog(self.storage)
        with self.assertRaises(ValueError):
            comparison.create({'volume_id': current['id']}, [{'volume_id': old_id}], background=False)

    def test_identity_rechecked_before_and_after_directory_read(self):
        registered = self.register()
        baseline = self.storage.directory(registered['id'])
        stale = self.discover()
        self.storage.discover = lambda: [stale]
        (self.disk / MARKER_NAME).unlink()
        create_marker(str(self.disk), self.disk.stat().st_dev, 'Подмена')
        result = self.storage.directory(registered['id'])
        self.assertTrue(result['cached'])
        self.assertEqual(result['scanned_at'], baseline['scanned_at'])
        self.assertIn('заменён', result['error'])
        with self.assertRaises(OSError):
            with open_readonly(stale, '', directory=True):
                self.fail('stale identity must not be opened')

    def test_swap_during_read_rejects_result(self):
        registered = self.register()
        stale = self.discover()
        with self.assertRaises(OSError):
            with open_readonly(stale, '', directory=True):
                (self.disk / MARKER_NAME).unlink()
                create_marker(str(self.disk), self.disk.stat().st_dev, 'Подмена')

    def test_duplicate_markers_block_both_mounts(self):
        registered = self.register()
        second = self.root / 'copy'
        second.mkdir()
        shutil.copyfile(self.disk / MARKER_NAME, second / MARKER_NAME)
        self.storage.discover = lambda: [self.discover(), self.discover(second, share='usbshare2')]
        volumes = self.storage.refresh(True)['volumes']
        pending = [v for v in volumes if v['identity_status'] == 'unverified']
        self.assertEqual(len(pending), 2)
        self.assertTrue(all(v['availability'] == 'unknown' for v in pending))
        self.assertEqual(next(v for v in volumes if v['id'] == registered['id'])['availability'], 'offline')

    def test_capacity_keeps_last_successful_measurement_offline_and_on_failure(self):
        current = self.discover()
        self.active = [current]
        first = self.storage.refresh(True)['volumes'][0]
        capacity = first['capacity']
        self.assertGreater(capacity['total_bytes'], 0)
        self.assertEqual(capacity['used_bytes'] + capacity['free_bytes'], capacity['total_bytes'])
        self.assertFalse(first['capacity_cached'])
        self.active = [{**current, 'capacity': None, 'capacity_error': 'no response'}]
        failed = self.storage.refresh(True)['volumes'][0]
        self.assertEqual(failed['capacity'], capacity)
        self.assertTrue(failed['capacity_cached'])
        # Use a confirmed disk for an actual remembered offline entry.
        registered = self.register()
        reopened = StorageCatalog(self.storage.database, lambda: [])
        offline = next(v for v in reopened.refresh(True)['volumes'] if v['id'] == registered['id'])
        self.assertEqual(offline['capacity'], registered['capacity'])
        self.assertTrue(offline['capacity_cached'])

    def test_registration_refuses_existing_file_and_symlink_without_overwrite(self):
        target = self.root / 'private'
        target.write_text('do not change')
        (self.disk / MARKER_NAME).symlink_to(target)
        with self.assertRaises(FileExistsError):
            create_marker(str(self.disk), self.disk.stat().st_dev, 'Диск')
        self.assertEqual(target.read_text(), 'do not change')
        volume = self.discover()
        self.assertEqual(volume['identity_status'], 'unverified')

    def test_invalid_oversized_or_special_marker_never_becomes_verified(self):
        for content in [b'not json', b'[]', json.dumps({'version': 1, 'id': 'invalid', 'name': 'x'}).encode(), b'x' * (MARKER_LIMIT + 1)]:
            with self.subTest(content=content[:40]):
                (self.disk / MARKER_NAME).write_bytes(content)
                self.assertEqual(self.discover()['identity_status'], 'unverified')
        (self.disk / MARKER_NAME).unlink()
        os.mkfifo(self.disk / MARKER_NAME)
        self.assertEqual(self.discover()['identity_status'], 'unverified')

    def test_capacity_uses_all_free_blocks_and_reports_user_available_separately(self):
        info = SimpleNamespace(f_frsize=4096, f_bsize=4096, f_blocks=1000, f_bfree=400, f_bavail=300)
        with patch('media_manager.volume_identity.os.fstatvfs', return_value=info):
            capacity = read_capacity(42)
        self.assertEqual(capacity['total_bytes'], 4096000)
        self.assertEqual(capacity['used_bytes'], 2457600)
        self.assertEqual(capacity['free_bytes'], 1638400)
        self.assertEqual(capacity['available_bytes'], 1228800)

    def test_remembered_usb_resource_does_not_alias_legacy_disk(self):
        old_id = volume_key('smbfs:tnas-z.local/usbshare1')
        with self.storage.connect() as db:
            db.execute('INSERT INTO volumes VALUES (?,?,?,?,?,?)', (old_id, 'usbshare1', str(self.disk), 'network', 'before', 'before'))
        remembered = self.storage.remember_network_volume('tnas-z.local', ['tnas-z._smb._tcp.local'], 'usbshare1')
        self.assertNotEqual(remembered['id'], old_id)
        self.assertEqual(remembered['identity_status'], 'unverified')
        self.assertIn(remembered['id'], {v['id'] for v in self.storage.refresh(True)['volumes']})
        registered = self.register()
        again = self.storage.remember_network_volume('tnas-z.local', ['tnas-z._smb._tcp.local'], 'usbshare1')
        self.assertEqual(again['id'], registered['id'])

    def test_marker_is_excluded_from_comparison_inventory(self):
        registered = self.register()
        (self.disk / ('._' + MARKER_NAME)).write_bytes(b'AppleDouble metadata')
        self.assertFalse(MARKER_FILES.intersection(e['name'] for e in self.storage.directory(registered['id'])['entries']))
        target = self.root / 'target'
        target.mkdir()
        source = self.discover()
        self.storage.discover = lambda: [source, dict(id='target', name='NAS', kind='network', mount_path=str(target))]
        self.storage.refresh(True)
        comparison = ComparisonCatalog(self.storage)
        job = comparison.create({'volume_id': registered['id']}, [{'volume_id': 'target'}], background=False, reuse_index=False)
        comparison.run(job['id'])
        self.assertEqual(comparison.job(job['id'])['state'], 'completed')
        with self.storage.connect() as db:
            names = [r['name'] for r in db.execute('SELECT name FROM comparison_entries')]
        self.assertFalse(MARKER_FILES.intersection(names))
        self.assertIn('photo.jpg', names)


if __name__ == '__main__':
    unittest.main()
