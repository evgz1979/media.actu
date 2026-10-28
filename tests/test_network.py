from __future__ import annotations

import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from media_manager.network import (
    NetworkCatalog, NetworkError, discover_servers, list_server_shares,
    parse_browse, parse_resolve, parse_shares, run, validate_host,
)
from media_manager.storage import StorageCatalog, volume_key


SERVER = {'id': 'nas-one', 'name': 'TNAS-Z', 'host': 'tnas-z.local', 'port': 445,
          'aliases': ['tnas-z.local', 'tnas-z._smb._tcp.local', 'tnas-z(smb)._smb._tcp.local']}
SHARES = [{'name': 'Media-copy01', 'comment': ''}, {'name': 'Safe', 'comment': ''}, {'name': 'Мои фото', 'comment': 'Семейные'}]
BROWSE = '''Browsing for _smb._tcp.local.
Timestamp     A/R    Flags  if Domain Service Type Instance Name
22:00:00.000  Add 3 7 local. _smb._tcp. TNAS-Z
22:00:00.000  Add 3 15 local. _smb._tcp. TNAS-Z
22:00:00.000  Add 3 7 local. _smb._tcp. TNAS-Z(SMB)
22:00:01.000  Rmv 2 7 local. _smb._tcp. TNAS-Z
'''


class NetworkParsingTests(unittest.TestCase):
    def test_bonjour_keeps_other_interface_after_remove(self):
        self.assertEqual([s['name'] for s in parse_browse(BROWSE)], ['TNAS-Z', 'TNAS-Z(SMB)'])
        self.assertEqual(parse_resolve('TNAS-Z can be reached at TNAS-Z.local.:445 (interface 7)'), ('tnas-z.local', 445))

    def test_discovery_merges_two_advertisements_of_same_server(self):
        def output(command, timeout):
            return BROWSE if '-B' in command else 'name can be reached at TNAS-Z.local.:445 (interface 7)'
        with patch('media_manager.network.run', side_effect=output):
            servers = discover_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]['name'], 'TNAS-Z')
        self.assertIn('tnas-z(smb)._smb._tcp.local', servers[0]['aliases'])

    def test_lists_disk_shares_only_and_keeps_spaces_unicode(self):
        output = 'Share                                           Type    Comments\n-------------------------------\n'
        output += ''.join(f"{s['name']:<48}Disk    {s['comment']}\n" for s in SHARES)
        output += 'IPC$                                            Pipe    IPC Service\n\n4 shares listed\n'
        self.assertEqual(parse_shares(output), SHARES)
        with self.assertRaises(NetworkError):
            parse_shares('Share\n---\nMedia Disk')

    def test_no_password_prompt_or_mount_in_share_enumeration(self):
        with patch('media_manager.network.run', return_value='Share\n---\n0 shares listed\n') as command:
            self.assertEqual(list_server_shares(SERVER), [])
        self.assertEqual(command.call_args.args[0], ['/usr/bin/smbutil', 'view', '-N', '//tnas-z.local'])
        for host in ['nas/user', 'user@nas', 'nas:445', '-evil', 'smb://nas', 'nas\n.local']:
            with self.assertRaises(NetworkError):
                validate_host(host)

    def test_diagnostics_do_not_expose_account_or_password(self):
        result = subprocess.CompletedProcess([], 1, stdout='', stderr='user:private-secret@nas denied')
        with patch('media_manager.network.subprocess.run', return_value=result):
            with self.assertRaises(NetworkError) as failure:
                run(['/usr/bin/smbutil'], 1)
        self.assertNotIn('private-secret', str(failure.exception))
        with patch('media_manager.network.subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 1)):
            with self.assertRaises(NetworkError):
                run(['cmd'], 1)


class NetworkCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.mounted = []
        self.storage = StorageCatalog(self.root/'storage.sqlite3', lambda: self.mounted)
        self.network = NetworkCatalog(self.storage, lambda: [SERVER], lambda _: SHARES)
        self.network.scan()
        self.network.shares('nas-one', True)

    def test_remember_unmounted_resource_and_roles_without_os_actions(self):
        with patch('media_manager.network.subprocess.run') as command:
            volume = self.network.remember('nas-one', 'Safe')
            self.assertEqual(volume['mount_path'], '')
            self.assertEqual(volume['network_url'], 'smb://tnas-z.local/Safe')
            self.storage.annotate(volume['id'], '', {'role': 'archive'})
            result = self.storage.directory(volume['id'])
            self.assertEqual(result['volume']['availability'], 'offline')
            self.assertIsNone(result['scanned_at'])
            command.assert_not_called()
        reopened = StorageCatalog(self.storage.database, lambda: [])
        self.assertEqual(reopened.metadata(volume['id'], '')['effective']['role'], 'archive')
        self.assertEqual(reopened.get_volume(volume['id'])['network_url'], volume['network_url'])

    def test_existing_volume_keeps_identity_role_and_snapshot(self):
        mount = self.root/'mounted'; mount.mkdir(); (mount/'notes.txt').write_text('keep')
        old_id = volume_key('smbfs:tnas-z._smb._tcp.local/media-copy01')
        self.mounted.append({'id': old_id, 'name': 'Media-copy01', 'kind': 'network', 'mount_path': str(mount)})
        self.storage.directory(old_id)
        self.storage.annotate(old_id, '', {'role': 'primary'})
        remembered = self.network.remember('nas-one', 'Media-copy01')
        self.assertEqual(remembered['id'], old_id)
        self.assertEqual(len(self.storage.refresh(True)['volumes']), 1)
        self.assertEqual(self.storage.metadata(old_id, '')['effective']['role'], 'primary')
        self.assertEqual(self.storage.directory(old_id, refresh=False)['entries'][0]['name'], 'notes.txt')

    def test_resource_matches_mount_by_other_bonjour_alias_without_duplicate(self):
        volume = self.network.remember('nas-one', 'Safe')
        self.storage.annotate(volume['id'], '', {'role': 'archive'})
        self.mounted.append({'id': volume_key('smbfs:tnas-z(smb)._smb._tcp.local/safe'), 'name': 'Safe', 'kind': 'network', 'mount_path': str(self.root)})
        volumes = self.storage.refresh(True)['volumes']
        self.assertEqual(len(volumes), 1)
        self.assertEqual(volumes[0]['id'], volume['id'])
        self.assertEqual(volumes[0]['availability'], 'online')
        self.assertEqual(volumes[0]['metadata']['effective']['role'], 'archive')

    def test_auth_error_preserves_share_list(self):
        self.network.list_shares = lambda _: (_ for _ in ()).throw(NetworkError('no access'))
        data = self.network.shares('nas-one', True)
        self.assertTrue(data['cached'])
        self.assertEqual(len(data['shares']), 3)
        self.assertEqual(data['error'], 'no access')
        self.assertIsNotNone(data['server']['shares_at'])

    def test_offline_server_and_missing_resource_remain_remembered(self):
        volume = self.network.remember('nas-one', 'Safe')
        self.network.list_shares = lambda _: [SHARES[0]]
        data = self.network.shares('nas-one', True)
        old = next(s for s in data['shares'] if s['name'] == 'Safe')
        self.assertFalse(old['present'])
        self.assertEqual(old['volume_id'], volume['id'])
        self.network.discover = lambda: []
        self.network.scan()
        self.assertFalse(self.network.server('nas-one')['discovered'])
        self.assertEqual(len(self.network.shares('nas-one')['shares']), 3)

    def test_failed_scan_preserves_previous_discovery(self):
        self.network.discover = lambda: (_ for _ in ()).throw(NetworkError('failed'))
        data = self.network.scan()
        self.assertEqual(data['error'], 'failed')
        self.assertTrue(data['servers'][0]['discovered'])

    def test_unknown_share_is_rejected_and_finder_requires_explicit_command(self):
        with self.assertRaises(KeyError):
            self.network.remember('nas-one', 'not-listed')
        volume = self.network.remember('nas-one', 'Мои фото')
        with patch('media_manager.network.subprocess.run') as command:
            self.network.open_in_finder(volume['id'])
        self.assertEqual(command.call_args.args[0], ['/usr/bin/open', 'smb://tnas-z.local/%D0%9C%D0%BE%D0%B8%20%D1%84%D0%BE%D1%82%D0%BE'])

    def test_legacy_volume_table_is_not_altered(self):
        with self.storage.connect() as db:
            names = [r['name'] for r in db.execute('PRAGMA table_info(volumes)')]
        self.assertEqual(names, ['id','name','mount_path','kind','first_seen','last_seen'])
        # The previous running version can continue its six-column inserts.
        with sqlite3.connect(self.storage.database) as db:
            db.execute("INSERT INTO volumes VALUES ('legacy','Legacy','/Volumes/Legacy','network','now','now')")
        self.assertEqual(self.storage.get_volume('legacy')['name'], 'Legacy')


if __name__ == '__main__':
    unittest.main()
