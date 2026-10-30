import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from media_manager.service_runtime import ServiceLogStream


class ServiceRuntimeTests(unittest.TestCase):
    def run_service(self, directory, *arguments):
        process = subprocess.Popen([sys.executable, '-m', 'media_manager.service_runtime', 'ui', *arguments],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env={**os.environ, 'MEDIA_ACTU_DATA_DIR': directory})
        try:
            # Do not drain the pipes: this reproduces the real Launcher's behavior.
            self.assertEqual(process.wait(timeout=10), 0)
            self.assertEqual(process.stdout.read(), b'')
            self.assertEqual(process.stderr.read(), b'')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            process.stderr.close()

    def test_large_stdout_and_stderr_do_not_block_the_launcher_pipe(self):
        with tempfile.TemporaryDirectory() as directory:
            self.run_service(directory, '-c',
                             "import sys; print('Начало'); print('x' * 300000); sys.stderr.write('Ошибка в журнале\\n')")
            text = (Path(directory) / 'logs/ui.log').read_text()
            self.assertIn('Начало', text)
            self.assertIn('Ошибка в журнале', text)

    def test_module_arguments_still_work(self):
        with tempfile.TemporaryDirectory() as directory:
            self.run_service(directory, '-m', 'json.tool', '--help')
            self.assertIn('usage:', (Path(directory) / 'logs/ui.log').read_text())

    def test_logs_rotate_and_keep_utf8_text(self):
        with tempfile.TemporaryDirectory() as directory:
            stream = ServiceLogStream(Path(directory) / 'ui.log', max_bytes=512, backups=2)
            try:
                for index in range(150):
                    stream.write(f'{index}: Строка журнала\n')
                stream.flush()
                files = list(Path(directory).glob('ui.log*'))
                self.assertLessEqual(len(files), 3)
                self.assertTrue(all(path.stat().st_size <= 512 for path in files))
                self.assertIn('149: Строка журнала', (Path(directory) / 'ui.log').read_text())
            finally:
                stream.handler.close()

    def test_failed_log_write_does_not_recurse_into_stderr(self):
        with tempfile.TemporaryDirectory() as directory:
            stream = ServiceLogStream(Path(directory) / 'ui.log')
            try:
                with patch.object(stream.handler.stream, 'write', side_effect=OSError('disk full')):
                    self.assertEqual(stream.write('entry'), 5)
                self.assertTrue(stream.handler.failed)
                self.assertEqual(stream.write('next entry'), 10)
            finally:
                stream.handler.close()
