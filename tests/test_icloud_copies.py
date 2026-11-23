import errno
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from media_manager.icloud_copies import ICloudCopies, ICloudReader
from media_manager.storage import StorageCatalog


class TestReader:
    def __init__(self):
        self.unavailable = set()
        self.calls = []

    def stream(self, parent, name, check):
        self.calls.append(name)
        check()
        with os.fdopen(os.open(name, os.O_RDONLY, dir_fd=parent), 'rb') as source:
            yield source.read(1)
            if name in self.unavailable:
                raise TimeoutError('iCloud недоступен')
            yield source.read()


class ICloudCopiesTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'iCloud Drive'
        self.disk = self.root / 'Disk'
        self.target = self.disk / 'Backup'
        self.source.mkdir()
        self.target.mkdir(parents=True)
        self.volume = dict(id='disk', name='Disk', kind='external', mount_path=str(self.disk),
                           device=self.disk.stat().st_dev)
        self.storage = StorageCatalog(self.root / 'storage.sqlite3', lambda: [self.volume])
        self.reader = TestReader()
        self.copies = self.service()

    def service(self):
        return ICloudCopies(self.storage, self.root / 'native', root=self.source, reader=self.reader)

    def read_pending(self):
        while item := self.copies._next():
            self.copies._process(item)

    def test_retries_partial_transfer_after_restart_and_continues_other_files(self):
        (self.source / 'a-delayed').write_bytes(b'delayed')
        (self.source / 'b-ready').write_bytes(b'ready')
        self.reader.unavailable.add('a-delayed')
        copy_id = self.copies.bind('', 'disk', 'Backup')['id']
        self.copies.start_copy(copy_id)
        self.read_pending()

        self.assertEqual((self.target / 'b-ready').read_bytes(), b'ready')
        self.assertFalse((self.target / 'a-delayed').exists())
        self.assertEqual(list(self.target.glob('*.part')), [])
        copy = self.copies.list()['copies'][0]
        self.assertEqual((copy['state'], copy['done'], copy['waiting']), ('waiting', 1, 1))
        delayed = self.copies.journal(copy_id)['items'][0]
        self.assertEqual(delayed['message'], 'iCloud недоступен')
        self.assertGreater(delayed['retry_at'], 0)

        self.copies = self.service()
        self.assertTrue(self.copies.list()['copies'][0]['active'])
        self.reader.unavailable.clear()
        with self.storage.connect() as db:
            db.execute("UPDATE icloud_copy_items SET retry_at=0 WHERE state='retry'")
        self.read_pending()
        self.assertEqual((self.target / 'a-delayed').read_bytes(), b'delayed')
        self.assertEqual(self.copies.list()['copies'][0]['state'], 'completed')
        self.assertEqual(self.reader.calls, ['a-delayed', 'b-ready', 'a-delayed'])

    def test_scope_is_read_only_and_preserves_existing_files_and_structure(self):
        (self.source / 'Scope' / 'Empty').mkdir(parents=True)
        (self.source / 'Outside').write_bytes(b'outside')
        (self.source / 'Scope' / 'new').write_bytes(b'')
        (self.source / 'Scope' / 'existing').write_bytes(b'original')
        (self.source / 'Scope' / 'link').symlink_to(self.source / 'Outside')
        (self.target / 'existing').write_bytes(b'different size')
        copy_id = self.copies.bind('Scope', 'disk', 'Backup')['id']
        entries = self.copies.browse('Scope')['entries']
        self.assertEqual({entry['name'] for entry in entries}, {'Empty', 'new', 'existing', 'link'})
        self.assertEqual(self.reader.calls, [])
        self.copies.start_copy(copy_id)
        self.read_pending()
        self.assertEqual({path.name for path in self.target.iterdir()}, {'Empty', 'new', 'existing'})
        self.assertEqual((self.target / 'existing').read_bytes(), b'different size')
        self.assertEqual((self.source / 'Scope' / 'existing').read_bytes(), b'original')
        self.assertEqual(self.reader.calls, ['new'])
        result = self.copies.list()['copies'][0]
        self.assertEqual((result['state'], result['done'], result['conflicts']), ('completed_with_conflicts', 1, 1))

    def test_manual_pause_survives_restart_and_copies_have_independent_destinations(self):
        (self.source / 'file').write_bytes(b'123')
        (self.disk / 'Other').mkdir()
        first = self.copies.bind('', 'disk', 'Backup')['id']
        second = self.copies.bind('', 'disk', 'Other')['id']
        self.copies.start_copy(first)
        self.copies.pause_copy(first)
        self.copies.start_copy(second)
        self.copies = self.service()
        self.read_pending()
        self.assertEqual((self.disk / 'Other' / 'file').read_bytes(), b'123')
        self.assertFalse((self.target / 'file').exists())
        self.copies.start_copy(first)
        self.read_pending()
        self.assertEqual((self.target / 'file').read_bytes(), b'123')

    def test_refuses_to_copy_into_cloud_or_into_an_overlapping_destination(self):
        (self.target / 'Subfolder').mkdir()
        self.copies.bind('', 'disk', 'Backup')
        with self.assertRaisesRegex(ValueError, 'пересекается'):
            self.copies.bind('', 'disk', 'Backup/Subfolder')
        self.volume.update(mount_path=str(self.source))
        (self.source / 'Scope').mkdir()
        with self.assertRaisesRegex(ValueError, 'пересекаются'):
            self.copies.bind('', 'disk', 'Scope')

    def test_network_fallback_writes_an_exclusive_final_file(self):
        (self.source / 'file').write_bytes(b'network')
        self.volume.update(kind='network')
        copy_id = self.copies.bind('', 'disk', 'Backup')['id']
        self.copies.start_copy(copy_id)
        unsupported = OSError(errno.ENOTSUP, 'не поддерживается')
        with (patch('media_manager.icloud_copies.publish_exclusive', side_effect=unsupported),
              patch('media_manager.icloud_copies.os.link', side_effect=unsupported)):
            self.read_pending()
        self.assertEqual((self.target / 'file').read_bytes(), b'network')
        self.assertEqual(list(self.target.glob('*.part')), [])
        self.assertEqual(self.copies.list()['copies'][0]['state'], 'completed')

    def test_reader_ends_on_silent_process(self):
        reader = ICloudReader(self.root)
        reader.executable.write_text('#!/bin/sh\nexec /bin/sleep 30\n')
        reader.executable.chmod(0o700)
        with (patch.object(reader, 'command', return_value=str(reader.executable)),
              patch('media_manager.icloud_copies.READ_TIMEOUT', .01), self.assertRaises(TimeoutError)):
            descriptor = os.open(self.source, os.O_RDONLY | os.O_DIRECTORY)
            try:
                list(reader.stream(descriptor, 'file', lambda: None))
            finally:
                os.close(descriptor)
