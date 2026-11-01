import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from media_manager.photos_adapter import PhotosAccessDenied, PhotosLibraryUnavailable, PhotosThumbnailPending, SystemPhotosAdapter


class PhotosAdapterTests(unittest.TestCase):
    def adapter(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        helper = root / 'fake-helper'
        import sys
        helper.write_text('#!' + sys.executable + '\n' + '''
import json,os,sys,socket,base64
if len(sys.argv)>2 and sys.argv[1]=='serve-socket':
 server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
 server.bind(sys.argv[2]);os.chmod(sys.argv[2],0o600);server.listen(1)
 client,_=server.accept()
 stream=client.makefile('rwb')
 lines=iter(stream.readline,b'')
else:
 stream=None
 lines=sys.stdin
for line in lines:
 request=json.loads(line)
 if request['op']=='quit':break
 response=json.dumps({'status':'authorized','pid':os.getpid(),'matched':request.get('identifiers',[]),'jpeg':base64.b64encode(b'JPEG derivative').decode()})+'\\n'
 if stream:stream.write(response.encode());stream.flush()
 else:print(response,end='',flush=True)
''')
        helper.chmod(0o755)
        adapter = SystemPhotosAdapter(root, root)
        adapter.use_gui = False
        adapter.executable = helper
        adapter.ensure_built = Mock()
        adapter._ipc_directory = lambda: root / 'ipc'
        self.addCleanup(adapter.close)
        return adapter, root

    def test_preview_requests_reuse_one_process_and_do_not_export_an_original(self):
        adapter, root = self.adapter()
        first = adapter.probe(['asset'])
        target = root / 'preview.jpg'
        adapter.create_thumbnail('asset', target, anchors=['asset'])
        second = adapter.probe(['asset'])
        self.assertEqual(first['pid'], second['pid'])
        self.assertEqual(target.read_bytes(), b'JPEG derivative')
        self.assertEqual(adapter.ensure_built.call_count, 1)

    def test_missing_photokit_permission_never_falls_back_to_full_image_export(self):
        adapter, root = self.adapter()
        adapter._run = Mock(return_value={'status':'not_determined'})
        adapter._applescript_status = Mock()
        with self.assertRaises(PhotosAccessDenied):
            adapter.status()
        adapter._applescript_status.assert_not_called()

    def test_gui_socket_transport_reuses_the_launched_app_and_keeps_socket_private(self):
        import subprocess
        adapter, root = self.adapter()
        adapter.use_gui = True
        children = []

        def launch(command, **kwargs):
            self.assertEqual(command[:3], ['/usr/bin/open', '-g', '-n'])
            self.assertEqual(len(command), 4)  # macOS drops argv from sandboxed launchers.
            children.append(subprocess.Popen([str(adapter.executable), 'serve-socket', str(adapter._socket_path)],
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            return subprocess.CompletedProcess(command, 0)

        try:
            with patch('media_manager.photos_adapter.subprocess.run', side_effect=launch) as opener:
                first = adapter.probe(['asset'])
                second = adapter.probe(['asset'])
                self.assertEqual(first['pid'], second['pid'])
                self.assertEqual(adapter._socket_path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(adapter._socket_path.parent.stat().st_mode & 0o777, 0o700)
                self.assertEqual(opener.call_count, 1)
        finally:
            adapter.close()
            for child in children:
                child.wait(timeout=3)

    def test_gui_refuses_an_insecure_or_symlinked_ipc_directory(self):
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                adapter, root = self.adapter()
                adapter.use_gui = True
                target = root / 'ipc'
                if symlink:
                    (root / 'elsewhere').mkdir(mode=0o700)
                    target.symlink_to(root / 'elsewhere', target_is_directory=True)
                else:
                    target.mkdir(mode=0o755)
                    target.chmod(0o755)
                with patch('media_manager.photos_adapter.subprocess.run') as opener:
                    with self.assertRaisesRegex(RuntimeError, 'Небезопасный каталог'):
                        adapter.probe()
                    opener.assert_not_called()

    def test_transport_statuses_distinguish_account_change_permission_and_cloud_wait(self):
        for status, error in [('library_mismatch', PhotosLibraryUnavailable), ('cloud', PhotosThumbnailPending), ('denied', PhotosAccessDenied)]:
            with self.subTest(status=status):
                adapter, root = self.adapter()
                adapter.executable.write_text(adapter.executable.read_text().replace("'status':'authorized'", "'status':"+repr(status)))
                with self.assertRaises(error):
                    adapter.probe()

    def test_original_stream_decodes_bounded_chunks_and_verifies_protocol_trailer(self):
        import base64
        adapter, root = self.adapter()
        adapter._begin = Mock()
        adapter._receive = Mock(side_effect=[
            dict(event='begin'), dict(event='progress', fraction=.4),
            dict(event='chunk', data=base64.b64encode(b'original bytes').decode()),
            dict(event='complete', size=14, sha256='source hash')])
        chunks, progress = [], []
        result = adapter.stream_original('asset', '1:0', 'v1', ['anchor'], chunks.append, progress.append, lambda: False)
        self.assertEqual(chunks, [b'original bytes'])
        self.assertEqual(progress, [.4])
        self.assertEqual(result['size'], 14)
        self.assertEqual(adapter._begin.call_args.args[0]['op'], 'original_resource')
        self.assertEqual(list(root.iterdir()), [adapter.executable])

    def test_stream_cancellation_sends_matching_token_and_stops_consumer(self):
        from media_manager.photos_adapter import PhotosTransferStopped
        adapter, _ = self.adapter()
        adapter._begin = Mock()
        adapter._send = Mock()
        adapter._receive = Mock(return_value=dict(status='cancelled'))
        with self.assertRaises(PhotosTransferStopped):
            adapter.stream_original('asset', '1:0', 'v1', [], Mock(), Mock(), lambda: True)
        start = adapter._begin.call_args.args[0]
        adapter._send.assert_called_once_with(dict(op='cancel', token=start['token']))

    def test_consumer_error_closes_only_its_transport_and_rejects_oversized_chunks(self):
        import base64
        adapter, _ = self.adapter()
        adapter._begin = Mock()
        adapter._receive = Mock(return_value=dict(event='chunk', data=base64.b64encode(b'x' * (256*1024+1)).decode()))
        writer = Mock()
        with patch.object(adapter, 'close') as close:
            with self.assertRaisesRegex(RuntimeError, 'Некорректный блок'):
                adapter.stream_original('asset', '1:0', 'v1', [], writer, Mock(), lambda: False)
            close.assert_called_once()
        writer.assert_not_called()
        adapter._receive = Mock(return_value=dict(event='chunk', data=base64.b64encode(b'bytes').decode()))
        with patch.object(adapter, 'close') as close:
            with self.assertRaisesRegex(OSError, 'Disk full'):
                adapter.stream_original('asset', '1:0', 'v1', [], Mock(side_effect=OSError('Disk full')), Mock(), lambda: False)
            close.assert_called_once()
