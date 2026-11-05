from __future__ import annotations

import json
import base64
import os
import selectors
import shutil
import socket
import stat
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from media_manager.scanner import PHOTO_EXTENSIONS, VIDEO_EXTENSIONS


#: Обозначает ошибку сборки, транспорта или ответа адаптера Photos.
#: Базовые типы: RuntimeError.
class PhotosAdapterError(RuntimeError):
    pass


#: Обозначает отсутствие системного разрешения на чтение Photos.
#: Базовые типы: PhotosAdapterError.
class PhotosAccessDenied(PhotosAdapterError):
    pass


#: Обозначает смену или временную недоступность нужной медиатеки.
#: Базовые типы: PhotosAdapterError.
class PhotosLibraryUnavailable(PhotosAdapterError):
    pass


#: Обозначает отсутствие локальной миниатюры без загрузки оригинала.
#: Базовые типы: PhotosAdapterError.
class PhotosThumbnailPending(PhotosAdapterError):
    pass


#: Обозначает кооперативную остановку потоковой передачи оригинала.
#: Базовые типы: PhotosAdapterError.
class PhotosTransferStopped(PhotosAdapterError):
    pass


#: Обозначает превышение времени ожидания ответа локального helper.
#: Базовые типы: PhotosAdapterError.
class PhotosResponseTimeout(PhotosAdapterError):
    pass


#: Обменивается запросами с локальным PhotoKit-helper и открывает объекты в Photos.
#: Зависимости конструктора: source_directory, build_directory.
class SystemPhotosAdapter:
    BUNDLE_IDENTIFIER = "actu.media.photos-adapter"

    #: Инициализирует SystemPhotosAdapter и его рабочее состояние.
    #: Обновляет состояние объекта: _backend, _buffer, _build_lock, _gui_pid, _operation_lock, _process, _socket, _socket_directory, _socket_path, app_directory и ещё 4.
    def __init__(self, source_directory: Path, build_directory: Path) -> None:
        self.source_directory = source_directory
        self.build_directory = build_directory
        self.app_directory = build_directory / "media-actu-photos.app"
        self.executable = self.app_directory / "Contents" / "MacOS" / "media-actu-photos"
        self._build_lock = threading.Lock()
        self._operation_lock = threading.RLock()
        self._backend: str | None = None
        self._process = None
        self._buffer = b''
        self.use_gui = os.uname().sysname == 'Darwin'
        self._socket = None
        self._socket_path = None
        self._socket_directory = None
        self._gui_pid = None

    #: Проверяет доступность macOS и компилятора clang для нативного адаптера.
    #: Использует os.uname, shutil.which.
    @property
    def supported(self) -> bool:
        return os.uname().sysname == "Darwin" and shutil.which("clang") is not None

    #: Сбрасывает прежнее поле выбора backend; вызовов в текущем проекте не найдено.
    #: Обновляет состояние объекта: _backend.
    def reuse_indexed_backend(self) -> None:
        self._backend = None

    #: Собирает и локально подписывает app-bundle при изменении исходников helper.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def ensure_built(self) -> None:
        if not self.supported:
            raise PhotosAdapterError("PhotoKit доступен только на macOS")
        source = self.source_directory / "main.m"
        plist = self.source_directory / "Info.plist"
        if self.executable.exists() and self.executable.stat().st_mtime_ns >= max(
            source.stat().st_mtime_ns, plist.stat().st_mtime_ns
        ):
            return

        with self._build_lock:
            contents = self.app_directory / "Contents"
            macos = contents / "MacOS"
            macos.mkdir(parents=True, exist_ok=True)
            shutil.copy2(plist, contents / "Info.plist")
            environment = os.environ.copy()
            environment["CLANG_MODULE_CACHE_PATH"] = str(
                self.build_directory / "clang-module-cache"
            )
            command = [
                "clang",
                "-fobjc-arc",
                "-fblocks",
                str(source),
                "-o",
                str(self.executable),
                "-framework",
                "Foundation",
                "-framework",
                "AppKit",
                "-framework",
                "Photos",
                "-Wl,-sectcreate,__TEXT,__info_plist," + str(plist),
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=environment,
                timeout=120,
                check=False,
            )
            if result.returncode != 0:
                raise PhotosAdapterError(result.stderr.strip() or "Не удалось собрать PhotoKit-адаптер")
            subprocess.run(
                [
                    "codesign",
                    "--force",
                    "--sign",
                    "-",
                    "--identifier",
                    self.BUNDLE_IDENTIFIER,
                    str(self.app_directory),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

    #: Исполняет одноразовую команду helper и разбирает её JSON-ответ.
    #: Явно отклоняет недопустимое состояние через PhotosAccessDenied, PhotosAdapterError.
    def _run(self, *arguments: str, timeout: int = 120) -> dict[str, Any]:
        self.ensure_built()
        result = subprocess.run(
            [str(self.executable), *arguments],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = result.stdout.strip() or result.stderr.strip()
        try:
            payload = json.loads(output) if output else {}
        except json.JSONDecodeError as error:
            raise PhotosAdapterError(output or "PhotoKit-адаптер не вернул JSON") from error
        if result.returncode == 2:
            raise PhotosAccessDenied(str(payload.get("status") or payload.get("error")))
        if result.returncode != 0:
            raise PhotosAdapterError(str(payload.get("error") or output))
        return payload

    #: Проверяет или запрашивает разрешение PhotoKit без scripting fallback.
    #: Явно отклоняет недопустимое состояние через PhotosAccessDenied.
    def status(self, *, request_authorization: bool = False) -> dict[str, Any]:
        if self.use_gui:
            payload = self._request(dict(op='authorize' if request_authorization else 'probe'), timeout=305)
            self._backend = 'photokit'
            return dict(payload, backend='photokit')
        payload = self._run("check")
        if payload.get("status") == "not_determined" and request_authorization:
            subprocess.run(
                ["open", "-W", "-n", str(self.app_directory), "--args", "status"],
                capture_output=True,
                text=True,
                timeout=305,
                check=False,
            )
            payload = self._run("check")
        if payload.get("status") in {"authorized", "limited"}:
            self._backend = "photokit"
            return {**payload, "backend": self._backend}
        raise PhotosAccessDenied('Разреши доступ media.actu Photos adapter в macOS → Конфиденциальность → Фото')

    #: Закрывает клиентский канал и принадлежащий клиенту дочерний процесс.
    #: Обновляет состояние объекта: _buffer, _gui_pid, _process, _socket, _socket_directory, _socket_path.
    def close(self):
        with self._operation_lock:
            connection, self._socket = self._socket, None
            if connection is not None:
                try:
                    connection.sendall(b'{"op":"quit"}\n')
                except OSError:
                    pass
                connection.close()
            # Each socket is an independent client of the GUI service. Closing
            # an originals stream must not terminate the preview connection.
            self._gui_pid = None
            # The helper owns its socket and lock. Never unlink another
            # connection's endpoint during a reconnect.
            self._socket_path = None
            self._socket_directory = None
            process, self._process = self._process, None
            self._buffer = b''
            if process is not None:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=3)
                for stream in (process.stdin, process.stdout):
                    if stream:
                        stream.close()

    #: Возвращает отдельный каталог Unix-сокета для текущего пользователя.
    #: Использует Path, os.getuid, os.uname, tempfile.gettempdir.
    def _ipc_directory(self):
        return Path('/private/tmp' if os.uname().sysname == 'Darwin' else tempfile.gettempdir()) / f'media-actu-photos-v2-{os.getuid()}'

    #: Подключает клиент к GUI-службе после проверки приватности IPC-каталога.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def _connect_gui(self):
        self.close()
        self.ensure_built()
        # Launch Services ignores argv from a sandboxed caller. The helper
        # therefore starts its fixed, read-only service without arguments.
        directory = self._ipc_directory()
        directory.mkdir(mode=0o700, exist_ok=True)
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise PhotosAdapterError('Небезопасный каталог связи с PhotoKit')
        self._socket_directory = directory
        self._socket_path = directory / 'photos.sock'
        subprocess.run(['/usr/bin/open', '-g', '-n', str(self.app_directory)],
                       capture_output=True, timeout=15, check=True)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                connection.connect(str(self._socket_path))
                self._socket = connection
                return
            except (FileNotFoundError, ConnectionRefusedError):
                connection.close()
                time.sleep(.05)
        raise PhotosAdapterError('Не удалось подключить GUI-помощник PhotoKit')

    #: Подготавливает GUI-соединение или stdin/stdout-процесс и отправляет запрос.
    #: Обновляет состояние объекта: _process.
    def _begin(self, request):
        if self.use_gui:
            if self._socket is None:
                self._connect_gui()
        elif self._process is None or self._process.poll() is not None:
            self.close()
            self.ensure_built()
            self._process = subprocess.Popen([str(self.executable), 'serve'], stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
        self._send(request)

    #: Передаёт один JSON-запрос с разделителем строки в текущий канал.
    #: Использует (json.dumps(request) + '\n').encode, json.dumps, self._process.stdin.flush, self._process.stdin.write, self._socket.sendall.
    def _send(self, request):
        data = (json.dumps(request) + '\n').encode()
        if self.use_gui:
            self._socket.sendall(data)
        else:
            self._process.stdin.write(data)
            self._process.stdin.flush()

    #: Читает ограниченную строку ответа с тайм-аутом и сохранением остатка буфера.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError, PhotosResponseTimeout.
    def _receive(self, timeout, *, limit=128 * 1024 * 1024):
        stream = self._socket if self.use_gui else self._process.stdout
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(stream, selectors.EVENT_READ)
            while b'\n' not in self._buffer:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not selector.select(remaining):
                    raise PhotosResponseTimeout('PhotoKit не ответил вовремя')
                chunk = os.read(stream.fileno(), 65536)
                if not chunk:
                    raise PhotosAdapterError('PhotoKit завершил соединение')
                self._buffer += chunk
                if len(self._buffer) > limit:
                    raise PhotosAdapterError('Слишком большой ответ PhotoKit')
        line, self._buffer = self._buffer.split(b'\n', 1)
        if len(line) > limit:
            raise PhotosAdapterError('Слишком большой ответ PhotoKit')
        payload = json.loads(line)
        if payload.get('pid'):
            self._gui_pid = payload['pid']
        return payload

    #: Преобразует статус helper в подходящий тип исключения Python.
    #: Явно отклоняет недопустимое состояние через PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable, PhotosThumbnailPending и ещё 1.
    @staticmethod
    def _check_response(payload):
        status = payload.get('status')
        if status in ('not_determined', 'denied', 'restricted'):
            raise PhotosAccessDenied('PhotoKit: требуется разрешение macOS на чтение Фото')
        if status in ('unavailable', 'library_mismatch'):
            raise PhotosLibraryUnavailable('Открыта другая медиатека Photos. Подключи нужную запись.')
        if status == 'cloud':
            raise PhotosThumbnailPending('Миниатюра пока недоступна локально в Photos')
        if status == 'cancelled':
            raise PhotosTransferStopped('Сохранение приостановлено')
        if payload.get('error'):
            raise PhotosAdapterError(str(payload['error']))

    #: Выполняет сериализованный запрос и закрывает клиентский канал при транспортном сбое.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def _request(self, request, *, timeout=30):
        with self._operation_lock:
            try:
                self._begin(request)
                payload = self._receive(timeout)
            except (OSError, ValueError, subprocess.SubprocessError, PhotosAdapterError) as error:
                self.close()
                raise PhotosAdapterError(str(error)) from error
            self._check_response(payload)
            return payload

    #: Принимает события потока до завершающего ответа с поддержкой отмены.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError, PhotosTransferStopped.
    def _stream_request(self, request, receive, stopped):
        with self._operation_lock:
            token = uuid.uuid4().hex
            cancel_at = None
            try:
                self._begin(dict(request, token=token))
                activity = time.monotonic()
                while True:
                    if stopped() and cancel_at is None:
                        self._send(dict(op='cancel', token=token))
                        cancel_at = time.monotonic()
                    if cancel_at and time.monotonic() - cancel_at > 5:
                        raise PhotosTransferStopped('Сохранение приостановлено')
                    try:
                        payload = self._receive(.25, limit=2 * 1024 * 1024)
                    except PhotosResponseTimeout:
                        if time.monotonic() - activity > 300:
                            raise PhotosAdapterError('Photos долго не передаёт данные. Повтори сохранение позже.')
                        continue
                    activity = time.monotonic()
                    self._check_response(payload)
                    if payload.get('event') == 'complete':
                        if cancel_at:
                            raise PhotosTransferStopped('Сохранение приостановлено')
                        return payload
                    if not cancel_at:
                        receive(payload)
            except BaseException:
                # Closing only this channel also cancels a producer whose consumer
                # failed (disk full, disconnected destination, invalid data).
                self.close()
                raise

    #: Запрашивает поток манифеста оригиналов и передаёт объекты обработчику.
    #: Использует self._stream_request.
    def original_manifest(self, anchors, receive_asset, stopped):
        #: Передаёт объект события манифеста вызывающему обработчику.
        #: Использует payload.get, receive_asset.
        def receive(payload):
            if payload.get('event') == 'asset':
                receive_asset(payload['asset'])
        return self._stream_request(dict(op='original_manifest', anchors=list(anchors)), receive, stopped)

    #: Декодирует ограниченные блоки оригинала и передаёт данные и прогресс в Core.
    #: Использует self._stream_request.
    def stream_original(self, identifier, resource_id, version, anchors, write, progress, stopped):
        #: Проверяет размер декодированного блока и распределяет события данных и прогресса.
        #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
        def receive(payload):
            if payload.get('event') == 'chunk':
                chunk = base64.b64decode(payload['data'], validate=True)
                if not chunk or len(chunk) > 256 * 1024:
                    raise PhotosAdapterError('Некорректный блок оригинала')
                write(chunk)
            elif payload.get('event') == 'progress':
                progress(max(0, min(1, float(payload.get('fraction', 0)))))
        return self._stream_request(dict(op='original_resource', identifier=identifier,
            resource_id=resource_id, version=version, anchors=list(anchors)), receive, stopped)

    #: Проверяет текущую медиатеку по якорным ID с возможностью переподключения.
    #: Использует self._request, self.close.
    def probe(self, identifiers=(), *, restart=False):
        with self._operation_lock:
            if restart:
                self.close()
            return self._request(dict(op='probe', identifiers=list(identifiers)))

    #: Получает индекс объектов подтверждённой медиатеки через постоянный helper.
    #: Использует self._request, self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get.
    def scan(self, anchors=()) -> list[dict[str, Any]]:
        return list(self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get('assets', []))

    #: Получает JPEG-превью PhotoKit и атомарно сохраняет его в кэш.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def create_thumbnail(
        self, asset_identifier: str, target: Path, width: int = 640, height: int = 480, *, anchors=()
    ) -> Path:
        with self._operation_lock:
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = self._request(dict(op='thumbnail', identifier=asset_identifier,
                                         width=width, height=height, anchors=list(anchors)))
            try:
                jpeg = base64.b64decode(payload['jpeg'], validate=True)
            except (KeyError, TypeError, ValueError) as error:
                raise PhotosAdapterError('PhotoKit не вернул JPEG-превью') from error
            if not jpeg or len(jpeg) > 16 * 1024 * 1024:
                raise PhotosAdapterError('Некорректный размер JPEG-превью')
            temporary = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
            try:
                temporary.write_bytes(jpeg)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
            return target

    #: Выделяет объект в Photos через действующий open.applescript.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def open_asset(self, asset_identifier: str) -> None:
        result = subprocess.run(
            [
                "osascript",
                str(self.source_directory / "open.applescript"),
                asset_identifier,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            raise PhotosAdapterError(
                result.stderr.strip() or "Не удалось открыть объект в Photos"
            )

    #: Сохраняет прежнюю проверку Photos через scripting API без текущих вызовов.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def _applescript_status(self) -> dict[str, Any]:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Photos" to count media items'],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            raise PhotosAdapterError(result.stderr.strip() or "Нет доступа к Photos")
        return {"status": "authorized", "count": int(result.stdout.strip() or 0)}

    #: Сохраняет прежнее чтение каталога через scan.js без текущих вызовов.
    #: Явно отклоняет недопустимое состояние через PhotosAdapterError.
    def _applescript_scan(self) -> list[dict[str, Any]]:
        result = subprocess.run(
            [
                "osascript",
                "-l",
                "JavaScript",
                str(self.source_directory / "scan.js"),
            ],
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
        if result.returncode != 0:
            raise PhotosAdapterError(result.stderr.strip() or "Не удалось прочитать Photos")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise PhotosAdapterError("Photos вернул некорректный каталог") from error

        assets = []
        for asset in payload.get("assets", []):
            extension = Path(str(asset.get("name") or "")).suffix.lower()
            if extension in PHOTO_EXTENSIONS:
                kind = "photo"
            elif extension in VIDEO_EXTENSIONS:
                kind = "video"
            else:
                continue
            assets.append({**asset, "kind": kind})
        return assets
