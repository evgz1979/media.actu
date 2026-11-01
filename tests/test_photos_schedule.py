from datetime import datetime, timezone
import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

from media_manager.photos_adapter import PhotosLibraryUnavailable
from media_manager.photos_originals import PhotosOriginals
from media_manager.photos_schedule import PhotosSyncSchedule, in_window, window_key
from photo_libraries_ui import library_state, schedule_text
from tests import test_photos_originals as originals_fixture


class PhotosWindowTests(unittest.TestCase):
    def test_moscow_window_uses_local_time_and_exact_boundaries(self):
        settings = dict(night_only=True, start_hour=0, end_hour=7, timezone='Europe/Moscow')
        for value, allowed in [('2026-11-01T20:59:59+00:00', False),
                               ('2026-11-01T21:00:00+00:00', True),
                               ('2026-11-02T03:59:59+00:00', True),
                               ('2026-11-02T04:00:00+00:00', False)]:
            with self.subTest(value=value):
                self.assertEqual(in_window(settings, datetime.fromisoformat(value)), allowed)
        settings['night_only'] = False
        self.assertTrue(in_window(settings, datetime.fromisoformat('2026-11-02T12:00:00+00:00')))

    def test_window_crossing_midnight_has_one_daily_identity(self):
        settings = dict(night_only=True, start_hour=23, end_hour=6, timezone='Europe/Moscow')
        start = datetime.fromisoformat('2026-11-01T23:00:00+03:00')
        after_midnight = datetime.fromisoformat('2026-11-02T05:59:00+03:00')
        self.assertTrue(in_window(settings, start))
        self.assertTrue(in_window(settings, after_midnight))
        self.assertEqual(window_key(settings, start), window_key(settings, after_midnight))
        self.assertFalse(in_window(settings, datetime.fromisoformat('2026-11-02T06:00:00+03:00')))


class PhotosScheduleTests(unittest.TestCase):
    def setUp(self):
        originals_fixture.PhotosOriginalsTests.setUp(self)
        self.instant = datetime.fromisoformat('2026-11-01T15:00:00+03:00')
        self.schedule = PhotosSyncSchedule(self.libraries, self.service, clock=lambda: self.instant)
        self.addCleanup(self.schedule.close)
        self.catalog.replace_photos_scan(self.source_id, [dict(id='a', name='a.JPG', kind='photo', created_at='2020-02-01T10:00:00Z')])
        self.catalog.enqueue_source_thumbnails(self.source_id)

    def night(self):
        self.instant = datetime.fromisoformat('2026-11-02T00:00:00+03:00')

    def enable(self):
        return self.schedule.configure(self.source_id, True)

    def wait_worker(self):
        thread = self.service._thread
        if thread:
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())

    def test_daytime_request_is_queued_without_opening_or_scanning_the_copy(self):
        self.enable()
        with patch.object(self.service, '_volume', side_effect=AssertionError('no destination IO by day')):
            result = self.service.start(self.link['id'])
            self.schedule.tick()
        self.assertEqual(result['state'], 'scheduled')
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['state'], 'idle')
        self.assertEqual(self.adapter.requests, [])
        self.assertFalse(any(p.is_file() for p in self.copy.rglob('*')))

    def test_thumbnail_claims_scan_and_new_thumbnail_generation_wait_for_night(self):
        self.enable()
        self.assertTrue(self.catalog.photos_queue_paused())
        self.assertIsNone(self.catalog.claim_thumbnail_job('photos'))
        with self.assertRaises(PhotosLibraryUnavailable):
            self.libraries.scan(self.source_id)
        with self.assertRaises(PhotosLibraryUnavailable):
            self.libraries.create_thumbnail(self.source_id, 'a', self.root/'cache.jpg')
        self.assertFalse((self.root/'cache.jpg').exists())
        self.night()
        self.assertFalse(self.catalog.photos_queue_paused())
        self.assertIsNotNone(self.catalog.claim_thumbnail_job('photos'))

    def test_scheduler_starts_at_midnight_and_does_not_repeat_a_finished_run(self):
        self.enable()
        self.adapter.original_manifest = Mock(wraps=self.adapter.original_manifest)
        self.service.start(self.link['id'])
        self.night()
        self.schedule.tick()
        self.wait_worker()
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['state'], 'completed')
        self.assertEqual(len(self.adapter.requests), 3)
        job = self.service.summary(self.link['id'], raw=True)['id']
        self.schedule.tick()
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['id'], job)
        self.assertEqual(len(self.adapter.requests), 3)
        # The next night reads the manifest and reuses receipts by metadata.
        self.instant = datetime.fromisoformat('2026-11-03T00:00:00+03:00')
        self.schedule.tick()
        self.wait_worker()
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['id'], job)
        self.assertEqual(self.adapter.original_manifest.call_count, 2)
        self.assertEqual(len(self.adapter.requests), 3)

    def test_window_end_cancels_current_resource_and_resumes_the_next_night(self):
        self.enable()
        self.night()
        self.schedule._arm(self.link['id'])
        def close_window():
            if len(self.adapter.requests) == 2:
                self.instant = datetime.fromisoformat('2026-11-02T07:00:00+03:00')
        self.adapter.before_write = close_window
        result = self.service.start(self.link['id'], background=False, _scheduled=True)
        self.assertEqual(result['state'], 'scheduled')
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['state'], 'paused')
        self.assertEqual(result['done_resources'], 1)
        self.assertEqual(list(self.copy.rglob('*.part')), [])
        self.assertTrue(self.schedule.manages(self.link['id']))
        self.adapter.before_write = lambda: None
        self.instant = datetime.fromisoformat('2026-11-03T00:00:00+03:00')
        self.schedule.tick()
        self.wait_worker()
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['done_assets'], 2)

    def test_manual_pause_cancels_automatic_resume_even_after_changing_hours(self):
        self.enable()
        self.service.start(self.link['id'])
        self.service.pause(self.link['id'])
        self.assertFalse(self.schedule.manages(self.link['id']))
        self.schedule.configure(self.source_id, True, 1, 8)
        self.schedule.configure(self.source_id, False, 1, 8)
        self.schedule.configure(self.source_id, True, 1, 8)
        self.instant = datetime.fromisoformat('2026-11-02T02:00:00+03:00')
        self.schedule.tick()
        self.assertEqual(self.adapter.requests, [])
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['state'], 'idle')

    def test_manual_preview_pause_survives_the_night_window(self):
        self.enable()
        self.libraries.set_paused(self.source_id, True)
        self.night()
        self.schedule.tick()
        self.assertTrue(self.catalog.photos_queue_paused())
        self.assertIsNone(self.catalog.claim_thumbnail_job('photos'))
        self.libraries.set_paused(self.source_id, False)
        self.assertFalse(self.catalog.photos_queue_paused())

    def test_settings_and_queued_requests_survive_a_core_restart(self):
        self.enable()
        self.service.start(self.link['id'])
        reopened_originals = PhotosOriginals(self.libraries, self.adapter)
        reopened = PhotosSyncSchedule(self.libraries, reopened_originals, clock=lambda: self.instant)
        self.addCleanup(reopened_originals.close)
        self.addCleanup(reopened.close)
        self.assertTrue(reopened.describe(self.source_id)['night_only'])
        self.assertEqual(reopened_originals.summary(self.link['id'])['state'], 'scheduled')
        self.night()
        reopened.tick()
        reopened_originals._thread.join(timeout=5)
        self.assertEqual(reopened_originals.summary(self.link['id'], raw=True)['state'], 'completed')

    def test_interrupted_night_run_resumes_after_restart_within_the_same_window(self):
        self.enable()
        self.night()
        self.schedule._arm(self.link['id'])
        self.adapter.before_write = lambda: self.service._stop.set()
        self.service.start(self.link['id'], background=False, _scheduled=True)
        job = self.service.summary(self.link['id'], raw=True)
        self.service._update(job['id'], state='saving')  # a process stopped during its run
        self.adapter.before_write = lambda: None
        reopened_originals = PhotosOriginals(self.libraries, self.adapter)
        reopened = PhotosSyncSchedule(self.libraries, reopened_originals, clock=lambda: self.instant)
        self.addCleanup(reopened_originals.close)
        self.addCleanup(reopened.close)
        reopened.tick()
        reopened_originals._thread.join(timeout=5)
        self.assertEqual(reopened_originals.summary(self.link['id'], raw=True)['done_assets'], 2)

    def test_daytime_enable_defers_started_work_and_disabling_allows_continuation(self):
        self.adapter.before_write = lambda: self.service.pause(self.link['id'])
        self.service.start(self.link['id'], background=False)
        self.adapter.before_write = lambda: None
        settings = self.enable()
        self.assertTrue(settings['blocked'])
        self.assertEqual(self.service.summary(self.link['id'])['state'], 'scheduled')
        self.schedule.configure(self.source_id, False)
        self.schedule.tick()
        self.wait_worker()
        self.assertEqual(self.service.summary(self.link['id'], raw=True)['state'], 'completed')

    def test_unbound_copy_or_another_account_cannot_start_from_the_timer(self):
        self.enable()
        self.service.start(self.link['id'])
        self.night()
        self.libraries.unbind_copy(self.source_id, self.link['id'])
        self.schedule.tick()
        self.assertEqual(self.adapter.requests, [])
        self.libraries.bind_copy(self.source_id, 'disk', 'Copy')
        with self.catalog.connect() as db:
            db.execute('UPDATE photos_libraries SET active=0')
        self.schedule.tick()
        self.assertEqual(self.adapter.requests, [])

    def test_invalid_windows_are_rejected_without_changing_the_policy(self):
        for start, end, zone in [(7,7,'Europe/Moscow'), (-1,7,'Europe/Moscow'), (0,24,'Europe/Moscow'), (0,7,'UTC')]:
            with self.subTest(start=start,end=end,zone=zone), self.assertRaises(ValueError):
                self.schedule.configure(self.source_id, True, start, end, zone)
        self.assertFalse(self.schedule.settings(self.source_id)['night_only'])

    def test_inactive_window_does_not_pause_ordinary_folder_previews(self):
        self.catalog.set_thumbnail_queue_paused(False)
        self.enable()
        self.assertFalse(self.catalog.thumbnail_queue_paused())
        self.assertTrue(self.catalog.photos_queue_paused())

    def test_source_card_distinguishes_manual_pause_and_waiting_for_night(self):
        library = dict(active=True,paused=False,sync_schedule=self.enable())
        self.assertIn('ночного окна',library_state(library))
        self.assertIn('00:00–07:00 МСК',schedule_text(library))
        library['paused'] = True
        self.assertEqual(library_state(library), 'Пауза')

    def test_schedule_api_persists_window_and_original_start_respects_it(self):
        import asyncio
        import httpx
        with patch.dict(os.environ, MEDIA_ACTU_DATA_DIR=str(self.root/'api-data')):
            import app as core
        async def exercise():
            with patch.object(core,'photos_schedule',self.schedule), patch.object(core,'photo_libraries',self.libraries), \
                 patch.object(core,'photos_originals',self.service):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=core.app),base_url='http://test') as client:
                    url=f'/api/photos/libraries/{self.source_id}/sync-schedule'
                    response=await client.patch(url,json=dict(night_only=True,start_hour=0,end_hour=7))
                    self.assertEqual(response.status_code,200,response.text)
                    self.assertTrue(response.json()['libraries'][0]['sync_schedule']['blocked'])
                    response=await client.post(f'/api/photos/libraries/{self.source_id}/copies/{self.link["id"]}/originals/start')
                    self.assertEqual(response.status_code,200,response.text)
                    self.assertEqual(response.json()['state'],'scheduled')
                    self.assertEqual((await client.patch(url,json=dict(night_only=True,start_hour=7,end_hour=7))).status_code,400)
                    self.assertEqual((await client.patch(url,json=dict(night_only='yes'))).status_code,422)
        asyncio.run(exercise())
        self.assertEqual(self.adapter.requests, [])
