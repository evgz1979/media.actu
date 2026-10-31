import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from media_manager.sandbox_rules import copy_write_rules, folder_marker_write_rules, marker_write_rules


@unittest.skipUnless(sys.platform == 'darwin', 'macOS sandbox integration')
class CopySandboxTests(unittest.TestCase):
    def test_folder_marker_write_exception_covers_only_its_service_filename(self):
        with tempfile.TemporaryDirectory(prefix='media-actu-folder-marker-sandbox-') as temporary:
            root = Path(temporary).resolve()
            folder = root/'volumes/disk/Main/Sub'
            folder.mkdir(parents=True)
            (folder/'original').write_bytes(b'keep')
            profile = ('(version 1) (allow default) (deny file-write* (subpath '
                       + json.dumps(str(root/'volumes')) + ')) ' + folder_marker_write_rules(str(root/'volumes'))
                       + ' ' + copy_write_rules(str(root/'volumes')))
            code = '''
import sys
from pathlib import Path
from uuid import uuid4
from media_manager.folder_markers import write_folder_marker,read_folder_marker
from media_manager.volume_identity import mounted_root
folder=Path(sys.argv[1]); payload=dict(version=1,group_id=uuid4().hex,folder_id=uuid4().hex,volume_id='disk',path='Main/Sub',name='Main',role='main',type='main',number=0,label='00-main',status='active',created_at='now',updated_at='now')
with mounted_root(str(folder)) as root:
 write_folder_marker(root,payload)
 write_folder_marker(root,{**payload,'status':'disconnected'})
 assert read_folder_marker(root)['status']=='disconnected'
for action in (lambda:(folder/'original').write_bytes(b'overwrite'), lambda:(folder/'original').unlink()):
 try:action()
 except PermissionError:pass
 else:raise AssertionError('Original was writable')
'''
            result = subprocess.run(['/usr/bin/sandbox-exec','-p',profile,sys.executable,'-c',code,str(folder)],capture_output=True,text=True)
            if 'sandbox_apply: Operation not permitted' in result.stderr:
                self.skipTest('Host does not allow nested sandbox-exec')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_marker_rename_is_atomic_and_keeps_originals_protected(self):
        with tempfile.TemporaryDirectory(prefix='media-actu-marker-sandbox-') as temporary:
            root = Path(temporary).resolve()
            volumes = root / 'volumes'
            disk = volumes / 'disk'
            disk.mkdir(parents=True)
            (disk / 'original').write_bytes(b'keep')
            profile = ('(version 1) (allow default) (deny file-write* (subpath '
                       + json.dumps(str(volumes)) + ')) ' + marker_write_rules(str(volumes))
                       + ' ' + copy_write_rules(str(volumes)))
            code = '''
import sys
from pathlib import Path
from media_manager.volume_identity import create_marker, rename_marker
disk=Path(sys.argv[1]); device=disk.stat().st_dev
marker=create_marker(str(disk), device, 'before')
renamed=rename_marker(str(disk), device, marker['id'], 'after')
assert renamed == {'id':marker['id'], 'name':'after'}
assert not list(disk.glob('.media-actu-copy-*.part'))
for action in (lambda:(disk/'original').write_bytes(b'overwrite'), lambda:(disk/'original').unlink()):
 try:action()
 except PermissionError:pass
 else:raise AssertionError('Original was writable')
'''
            result = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, sys.executable, '-c', code, str(disk)],
                                    capture_output=True, text=True)
            if 'sandbox_apply: Operation not permitted' in result.stderr:
                self.skipTest('Host does not allow nested sandbox-exec')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_atomic_copy_keeps_existing_files_write_protected(self):
        self.exercise('external')

    def test_network_direct_copy_keeps_existing_files_write_protected(self):
        self.exercise('network')

    def exercise(self, kind):
        with tempfile.TemporaryDirectory(prefix='media-actu-sandbox-') as temporary:
            root = Path(temporary).resolve()
            volumes = root/'volumes'
            for folder in (volumes/'main/Original', volumes/'copy/Backup'):
                folder.mkdir(parents=True)
            (volumes/'main/Original/new').write_bytes(b'copy this')
            (volumes/'copy/Backup/existing').write_bytes(b'keep this')
            profile = '(version 1) (allow default) (deny file-write* (subpath ' + json.dumps(str(volumes)) + ')) ' + copy_write_rules(str(volumes))
            code = '''
import os,sys
from pathlib import Path
from media_manager.storage import StorageCatalog
from media_manager.copies import CopyCatalog
from media_manager.paired_comparison import PairedComparisonCatalog
from media_manager.copy_files import MissingCopyCatalog
root=Path(sys.argv[1]); volumes=root/'volumes'
mounted=[dict(id=n,name=n,kind=sys.argv[2] if n=='copy' else 'external',mount_path=str(volumes/n),device=(volumes/n).stat().st_dev) for n in ('main','copy')]
storage=StorageCatalog(root/'db.sqlite3',lambda:mounted)
for v in mounted:storage.directory(v['id'])
copies=CopyCatalog(storage);group=copies.create_main('main','Original');copy=copies.add_copy(group['id'],'copy','Backup')['copies'][0]
pairs=PairedComparisonCatalog(storage,copies);transfers=MissingCopyCatalog(pairs)
folder=pairs.create(copy['id'],background=False);pairs.run(folder['id'])
files=pairs.create(copy['id'],'files',folder['id'],background=False);pairs.run(files['id'])
plan=transfers.plan(files['id']);transfers.start(plan['id'],background=False);transfers.run(plan['id'],recheck=False)
result=transfers.job(plan['id']);assert result['errors']==0,result
assert (volumes/'copy/Backup/new').read_bytes()==b'copy this'
for path in (volumes/'main/Original/new',volumes/'copy/Backup/existing',volumes/'copy/Backup/new'):
 try:path.write_bytes(b'overwrite')
 except PermissionError:pass
 else:raise AssertionError('Existing file was writable: '+str(path))
 try:path.unlink()
 except PermissionError:pass
 else:raise AssertionError('Existing file was removable: '+str(path))
assert not list(volumes.rglob('.media-actu-copy-*.part'))
'''
            result = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, sys.executable, '-c', code, str(root), kind], capture_output=True, text=True)
            if 'sandbox_apply: Operation not permitted' in result.stderr:
                self.skipTest('Host does not allow nested sandbox-exec')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
