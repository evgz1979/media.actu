import asyncio
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from watchdog.events import FileCreatedEvent, FileMovedEvent, FileOpenedEvent

from media_manager.copies import CopyCatalog
from media_manager.folder_tracking import FolderChangeHandler, FolderTrackingService
from media_manager.storage import StorageCatalog


class FolderTrackingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.volume = self.root / 'disk'
        (self.volume / 'Main' / 'Nested').mkdir(parents=True)
        self.mounted = [dict(id='disk', name='Disk', kind='external', mount_path=str(self.volume),
                             device=self.volume.stat().st_dev)]
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: self.mounted)
        self.storage.directory('disk')
        self.copies = CopyCatalog(self.storage)
        self.group = self.copies.create_main('disk', 'Main')
        self.service = FolderTrackingService(self.copies)
        self.service.observer = Mock()
        self.service.observer.emitters = []
        self.service.observer.schedule.side_effect = lambda *args, **kwargs: self.record_watch()
        self.addCleanup(self.service.close)

    def record_watch(self):
        watch = object()
        self.service.observer.emitters.append(SimpleNamespace(watch=watch, is_alive=lambda: True))
        return watch

    def enable(self):
        self.copies.update_group(self.group['id'], {'tracking': True})
        self.service.reconcile()
        return self.service._watches[self.group['id']]['handler']

    def test_only_opted_in_folders_subscribe_and_events_persist_after_restart(self):
        self.service.reconcile()
        self.service.observer.schedule.assert_not_called()
        handler = self.enable()
        self.assertEqual(self.service.status(self.group['id'])['tracking_state'], 'watching')
        self.service.observer.schedule.assert_called_once_with(handler, str(self.volume / 'Main'), recursive=True)
        handler.callback()
        reopened = CopyCatalog(StorageCatalog(self.storage.database, lambda: self.mounted))
        self.assertIsNotNone(reopened.group(self.group['id'])['changed_at'])
        self.assertEqual(list((self.volume / 'Main/Nested').iterdir()), [])

    def test_read_events_and_copy_temporaries_do_not_trigger_a_change(self):
        callback = Mock()
        handler = FolderChangeHandler(callback, delay=.01)
        self.addCleanup(handler.cancel)
        temporary = '/Main/.media-actu-copy-' + 'a' * 32 + '-' + 'b' * 32 + '.part'
        handler.on_any_event(FileOpenedEvent('/Main/photo.jpg'))
        handler.on_any_event(FileCreatedEvent(temporary))
        self.assertIsNone(handler._timer)
        handler.on_any_event(FileMovedEvent(temporary, '/Main/photo.jpg'))
        handler._timer.join(1)
        callback.assert_called_once()

    def test_offline_and_disabled_folders_detach_and_stale_events_are_ignored(self):
        handler = self.enable()
        self.mounted.clear()
        self.storage.refresh(True)
        self.service.reconcile()
        self.assertEqual(self.service.status(self.group['id'])['tracking_state'], 'offline')
        self.service.observer.unschedule.assert_called_once()
        handler.callback()
        self.assertIsNone(self.copies.group(self.group['id'])['changed_at'])
        self.copies.update_group(self.group['id'], {'tracking': False})
        self.service.reconcile()
        self.assertFalse(self.service._watches)

    def test_manual_group_disconnect_stops_tracking_until_reconnected(self):
        handler = self.enable()
        self.copies.set_group_connected(self.group['id'], False)
        handler.callback()
        self.assertIsNone(self.copies.group(self.group['id'])['changed_at'])
        self.service.reconcile()
        self.assertFalse(self.service._watches)
        self.copies.set_group_connected(self.group['id'], True)
        self.service.reconcile()
        self.assertEqual(self.service.status(self.group['id'])['tracking_state'], 'watching')

    def test_reconnect_restores_tracking_and_replaced_or_symlink_roots_are_rejected(self):
        self.enable()
        volume = self.mounted.pop()
        self.storage.refresh(True)
        self.service.reconcile()
        self.mounted.append(volume)
        self.storage.refresh(True)
        self.service.reconcile()
        self.assertEqual(self.service.observer.schedule.call_count, 2)
        (self.volume / 'Main').rename(self.volume / 'Original')
        (self.volume / 'Main').symlink_to(self.root, target_is_directory=True)
        self.service.reconcile()
        self.assertEqual(self.service.status(self.group['id'])['tracking_state'], 'error')
        self.assertFalse(self.service._watches)
        (self.volume / 'Main').unlink()
        (self.volume / 'Original').rename(self.volume / 'Main')
        volume['device'] = -1
        self.storage.refresh(True)
        self.service.reconcile()
        self.assertEqual(self.service.status(self.group['id'])['tracking_state'], 'error')

    def test_actual_observer_detects_nested_file_changes(self):
        from watchdog.observers.polling import PollingObserver
        service = FolderTrackingService(self.copies)
        service.observer = PollingObserver(timeout=.05)
        self.addCleanup(service.close)
        self.copies.update_group(self.group['id'], {'tracking': True})
        service.start()
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline and service.status(self.group['id'])['tracking_state'] != 'watching':
            time.sleep(.02)
        self.assertEqual(service.status(self.group['id'])['tracking_state'], 'watching')
        (self.volume / 'Main/Nested/photo.jpg').write_bytes(b'new photo')
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline and not self.copies.group(self.group['id'])['changed_at']:
            time.sleep(.05)
        self.assertIsNotNone(self.copies.group(self.group['id'])['changed_at'])

    def test_api_settings_validation_and_partial_updates(self):
        async def exercise():
            import httpx
            with patch.dict(os.environ, {'MEDIA_ACTU_DATA_DIR': str(self.root / 'api-data')}):
                import app as core
            with patch.object(core, 'copies', self.copies), patch.object(core, 'folder_tracking', self.service):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app), base_url='http://test') as client:
                    url = '/api/storage/copy-groups/' + self.group['id']
                    response = await client.patch(url, json={'tracking': True, 'label': 'temporary'})
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertTrue(response.json()['tracking'])
                    response = await client.patch(url, json={'label': 'archive'})
                    self.assertEqual((response.json()['label'], response.json()['tracking']), ('archive', True))
                    for data in ({'label': 'unknown'}, {'tracking': 'yes'}, {'tracking': True, 'path': 'Elsewhere'}):
                        self.assertEqual((await client.patch(url, json=data)).status_code, 422)
                    self.assertEqual((await client.patch(url, json={'tracking': None})).status_code, 400)
                    self.assertEqual((await client.patch(url, json={})).status_code, 400)
                    self.assertEqual((await client.patch('/api/storage/copy-groups/missing', json={'label': ''})).status_code, 404)
                    self.copies.mark_changed(self.group['id'])
                    response = await client.get('/api/storage/copy-groups')
                    group = response.json()['groups'][0]
                    self.assertEqual(group['label'], 'archive')
                    self.assertIn('tracking_state', group)
                    self.assertIn('inbox', response.json()['labels'])
                    response = await client.post(url + '/acknowledge', json={'changed_at': group['changed_at']})
                    self.assertIsNone(response.json()['changed_at'])
        asyncio.run(exercise())


if __name__ == '__main__':
    unittest.main()
