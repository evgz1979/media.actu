"""Run Launcher services without writing into its undrained stdout/stderr pipe."""
from __future__ import annotations

import faulthandler
import io
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import runpy
import signal
import sys


class ServiceFileHandler(RotatingFileHandler):
    def handleError(self, record):
        # logging's default error handler writes to stderr, which is this sink.
        # A full/unavailable log disk must not recurse through logging forever.
        self.failed = True


class ServiceLogStream(io.TextIOBase):
    def __init__(self, path, *, max_bytes=2 * 1024 * 1024, backups=3):
        self.handler = ServiceFileHandler(path, maxBytes=max_bytes, backupCount=backups, encoding='utf-8')
        self.handler.failed = False
        self.handler.setFormatter(logging.Formatter('%(message)s'))
        self.handler.terminator = ''
        self.chunk_size = min(4096, max(1, max_bytes // 4))

    @property
    def encoding(self):
        return 'utf-8'

    def writable(self):
        return True

    def write(self, text):
        for start in range(0, len(text), self.chunk_size):
            if self.handler.failed:
                break
            self.handler.handle(logging.LogRecord('service', logging.INFO, '', 0,
                                                 text[start:start + self.chunk_size], (), None))
        return len(text)

    def flush(self):
        self.handler.flush()


_diagnostic_files = []


def configure_logging(service):
    if service not in ('core', 'ui'):
        raise ValueError('Expected core or ui service')
    default = Path(__file__).resolve().parents[1] / 'data'
    directory = Path(os.environ.get('MEDIA_ACTU_DATA_DIR', str(default))).expanduser() / 'logs'
    directory.mkdir(parents=True, exist_ok=True)
    stream = ServiceLogStream(directory / f'{service}.log')
    sys.stdout = sys.stderr = stream
    stacks = directory / f'{service}-stacks.log'
    if stacks.exists() and stacks.stat().st_size > 2 * 1024 * 1024:
        stacks.replace(stacks.with_suffix('.log.1'))
    diagnostic = stacks.open('a', encoding='utf-8')
    _diagnostic_files.append(diagnostic)
    faulthandler.enable(file=diagnostic)
    if hasattr(signal, 'SIGUSR1'):
        faulthandler.register(signal.SIGUSR1, file=diagnostic, all_threads=True)
    return stream


def main():
    if len(sys.argv) < 4 or sys.argv[2] not in ('-m', '-c'):
        raise SystemExit('Usage: service_runtime core|ui -m MODULE [ARGS] | -c CODE [ARGS]')
    service, mode, target, *arguments = sys.argv[1:]
    configure_logging(service)
    if mode == '-m':
        sys.argv = [target, *arguments]
        runpy.run_module(target, run_name='__main__', alter_sys=True)
    else:
        sys.argv = ['-c', *arguments]
        exec(compile(target, '<launcher>', 'exec'), {'__name__': '__main__'})


if __name__ == '__main__':
    main()
