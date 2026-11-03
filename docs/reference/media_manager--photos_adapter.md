# Python-клиент PhotoKit: `media_manager/photos_adapter.py`

Собирает локальный helper, подключается к Unix-сокету GUI-службы, передаёт JSON-запросы и ограниченные потоки ресурсов. Старые scripting-методы сохранены, но не входят в текущий путь вызовов.

[Исходный модуль](../../media_manager/photos_adapter.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/scanner.py](media_manager--scanner.md).
Импортируется модулями: [app.py](app.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_originals.py](media_manager--photos_originals.md), [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md), [media_manager/thumbnails.py](media_manager--thumbnails.md).
Тестовые модули с прямым импортом: [tests/test_photo_libraries.py](../../tests/test_photo_libraries.py#L10), [tests/test_photos_adapter.py](../../tests/test_photos_adapter.py#L7), [tests/test_photos_adapter.py](../../tests/test_photos_adapter.py#L130), [tests/test_photos_copy_chain.py](../../tests/test_photos_copy_chain.py#L7), [tests/test_photos_originals.py](../../tests/test_photos_originals.py#L12), [tests/test_photos_schedule.py](../../tests/test_photos_schedule.py#L8).

## Оглавление определений

- [PhotosAdapterError](#symbol-photosadaptererror) — Обозначает ошибку сборки, транспорта или ответа адаптера Photos.
- [PhotosAccessDenied](#symbol-photosaccessdenied) — Обозначает отсутствие системного разрешения на чтение Photos.
- [PhotosLibraryUnavailable](#symbol-photoslibraryunavailable) — Обозначает смену или временную недоступность нужной медиатеки.
- [PhotosThumbnailPending](#symbol-photosthumbnailpending) — Обозначает отсутствие локальной миниатюры без загрузки оригинала.
- [PhotosTransferStopped](#symbol-photostransferstopped) — Обозначает кооперативную остановку потоковой передачи оригинала.
- [PhotosResponseTimeout](#symbol-photosresponsetimeout) — Обозначает превышение времени ожидания ответа локального helper.
- [SystemPhotosAdapter](#symbol-systemphotosadapter) — Обменивается запросами с локальным PhotoKit-helper и открывает объекты в Photos.
- [SystemPhotosAdapter.__init__](#symbol-systemphotosadapter---init--) — Инициализирует SystemPhotosAdapter и его рабочее состояние.
- [SystemPhotosAdapter.supported](#symbol-systemphotosadapter-supported) — Проверяет доступность macOS и компилятора clang для нативного адаптера.
- [SystemPhotosAdapter.reuse_indexed_backend](#symbol-systemphotosadapter-reuse-indexed-backend) — Сбрасывает прежнее поле выбора backend; вызовов в текущем проекте не найдено.
- [SystemPhotosAdapter.ensure_built](#symbol-systemphotosadapter-ensure-built) — Собирает и локально подписывает app-bundle при изменении исходников helper.
- [SystemPhotosAdapter._run](#symbol-systemphotosadapter--run) — Исполняет одноразовую команду helper и разбирает её JSON-ответ.
- [SystemPhotosAdapter.status](#symbol-systemphotosadapter-status) — Проверяет или запрашивает разрешение PhotoKit без scripting fallback.
- [SystemPhotosAdapter.close](#symbol-systemphotosadapter-close) — Закрывает клиентский канал и принадлежащий клиенту дочерний процесс.
- [SystemPhotosAdapter._ipc_directory](#symbol-systemphotosadapter--ipc-directory) — Возвращает отдельный каталог Unix-сокета для текущего пользователя.
- [SystemPhotosAdapter._connect_gui](#symbol-systemphotosadapter--connect-gui) — Подключает клиент к GUI-службе после проверки приватности IPC-каталога.
- [SystemPhotosAdapter._begin](#symbol-systemphotosadapter--begin) — Подготавливает GUI-соединение или stdin/stdout-процесс и отправляет запрос.
- [SystemPhotosAdapter._send](#symbol-systemphotosadapter--send) — Передаёт один JSON-запрос с разделителем строки в текущий канал.
- [SystemPhotosAdapter._receive](#symbol-systemphotosadapter--receive) — Читает ограниченную строку ответа с тайм-аутом и сохранением остатка буфера.
- [SystemPhotosAdapter._check_response](#symbol-systemphotosadapter--check-response) — Преобразует статус helper в подходящий тип исключения Python.
- [SystemPhotosAdapter._request](#symbol-systemphotosadapter--request) — Выполняет сериализованный запрос и закрывает клиентский канал при транспортном сбое.
- [SystemPhotosAdapter._stream_request](#symbol-systemphotosadapter--stream-request) — Принимает события потока до завершающего ответа с поддержкой отмены.
- [SystemPhotosAdapter.original_manifest](#symbol-systemphotosadapter-original-manifest) — Запрашивает поток манифеста оригиналов и передаёт объекты обработчику.
- [SystemPhotosAdapter.original_manifest.receive](#symbol-systemphotosadapter-original-manifest-receive) — Передаёт объект события манифеста вызывающему обработчику.
- [SystemPhotosAdapter.stream_original](#symbol-systemphotosadapter-stream-original) — Декодирует ограниченные блоки оригинала и передаёт данные и прогресс в Core.
- [SystemPhotosAdapter.stream_original.receive](#symbol-systemphotosadapter-stream-original-receive) — Проверяет размер декодированного блока и распределяет события данных и прогресса.
- [SystemPhotosAdapter.probe](#symbol-systemphotosadapter-probe) — Проверяет текущую медиатеку по якорным ID с возможностью переподключения.
- [SystemPhotosAdapter.scan](#symbol-systemphotosadapter-scan) — Получает индекс объектов подтверждённой медиатеки через постоянный helper.
- [SystemPhotosAdapter.create_thumbnail](#symbol-systemphotosadapter-create-thumbnail) — Получает JPEG-превью PhotoKit и атомарно сохраняет его в кэш.
- [SystemPhotosAdapter.open_asset](#symbol-systemphotosadapter-open-asset) — Выделяет объект в Photos через действующий open.applescript.
- [SystemPhotosAdapter._applescript_status](#symbol-systemphotosadapter--applescript-status) — Сохраняет прежнюю проверку Photos через scripting API без текущих вызовов.
- [SystemPhotosAdapter._applescript_scan](#symbol-systemphotosadapter--applescript-scan) — Сохраняет прежнее чтение каталога через scan.js без текущих вызовов.

<a id="symbol-photosadaptererror"></a>

## `PhotosAdapterError`

[media_manager/photos_adapter.py:23](../../media_manager/photos_adapter.py#L23)

Обозначает ошибку сборки, транспорта или ответа адаптера Photos. Базовые типы: RuntimeError.

Базовые классы: `RuntimeError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-photosaccessdenied"></a>

## `PhotosAccessDenied`

[media_manager/photos_adapter.py:29](../../media_manager/photos_adapter.py#L29)

Обозначает отсутствие системного разрешения на чтение Photos. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-photoslibraryunavailable"></a>

## `PhotosLibraryUnavailable`

[media_manager/photos_adapter.py:35](../../media_manager/photos_adapter.py#L35)

Обозначает смену или временную недоступность нужной медиатеки. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-photosthumbnailpending"></a>

## `PhotosThumbnailPending`

[media_manager/photos_adapter.py:41](../../media_manager/photos_adapter.py#L41)

Обозначает отсутствие локальной миниатюры без загрузки оригинала. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-photostransferstopped"></a>

## `PhotosTransferStopped`

[media_manager/photos_adapter.py:47](../../media_manager/photos_adapter.py#L47)

Обозначает кооперативную остановку потоковой передачи оригинала. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-photosresponsetimeout"></a>

## `PhotosResponseTimeout`

[media_manager/photos_adapter.py:53](../../media_manager/photos_adapter.py#L53)

Обозначает превышение времени ожидания ответа локального helper. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-systemphotosadapter"></a>

## `SystemPhotosAdapter`

[media_manager/photos_adapter.py:59](../../media_manager/photos_adapter.py#L59)

Обменивается запросами с локальным PhotoKit-helper и открывает объекты в Photos. Зависимости конструктора: source_directory, build_directory.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_backend`, `_buffer`, `_build_lock`, `_gui_pid`, `_operation_lock`, `_process`, `_socket`, `_socket_directory`, `_socket_path`, `app_directory`, `build_directory`, `executable`, `source_directory`, `use_gui`.

Именованные методы: `__init__`, `supported`, `reuse_indexed_backend`, `ensure_built`, `_run`, `status`, `close`, `_ipc_directory`, `_connect_gui`, `_begin`, `_send`, `_receive`, `_check_response`, `_request`, `_stream_request`, `original_manifest`, `stream_original`, `probe`, `scan`, `create_thumbnail`, `open_asset`, `_applescript_status`, `_applescript_scan`.

<a id="symbol-systemphotosadapter---init--"></a>

## `SystemPhotosAdapter.__init__`

[media_manager/photos_adapter.py:64](../../media_manager/photos_adapter.py#L64)

Инициализирует SystemPhotosAdapter и его рабочее состояние. Обновляет состояние объекта: _backend, _buffer, _build_lock, _gui_pid, _operation_lock, _process, _socket, _socket_directory, _socket_path, app_directory и ещё 4.

```python
def __init__(self, source_directory: Path, build_directory: Path) -> None
```

Присваивания полям `self`: `_backend`, `_buffer`, `_build_lock`, `_gui_pid`, `_operation_lock`, `_process`, `_socket`, `_socket_directory`, `_socket_path`, `app_directory`, `build_directory`, `executable`, `source_directory`, `use_gui`.

Прямые выражения вызова: `os.uname`, `threading.Lock`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter-supported"></a>

## `SystemPhotosAdapter.supported`

[media_manager/photos_adapter.py:83](../../media_manager/photos_adapter.py#L83)

Проверяет доступность macOS и компилятора clang для нативного адаптера. Использует os.uname, shutil.which.

```python
def supported(self) -> bool
```

Декораторы: `property`.

Прямые выражения вызова: `os.uname`, `shutil.which`.

Выражения возврата (ветви, без исполнения):

- `os.uname().sysname == 'Darwin' and shutil.which('clang') is not None`


<a id="symbol-systemphotosadapter-reuse-indexed-backend"></a>

## `SystemPhotosAdapter.reuse_indexed_backend`

[media_manager/photos_adapter.py:88](../../media_manager/photos_adapter.py#L88)

Сбрасывает прежнее поле выбора backend; вызовов в текущем проекте не найдено. Обновляет состояние объекта: _backend.

```python
def reuse_indexed_backend(self) -> None
```

Присваивания полям `self`: `_backend`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter-ensure-built"></a>

## `SystemPhotosAdapter.ensure_built`

[media_manager/photos_adapter.py:93](../../media_manager/photos_adapter.py#L93)

Собирает и локально подписывает app-bundle при изменении исходников helper. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def ensure_built(self) -> None
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `macos.mkdir`, `max`, `os.environ.copy`, `plist.stat`, `result.stderr.strip`, `self.executable.exists`, `self.executable.stat`, `shutil.copy2`, `source.stat`, `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError('PhotoKit доступен только на macOS')`
- `PhotosAdapterError(result.stderr.strip() or 'Не удалось собрать PhotoKit-адаптер')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-systemphotosadapter--run"></a>

## `SystemPhotosAdapter._run`

[media_manager/photos_adapter.py:155](../../media_manager/photos_adapter.py#L155)

Исполняет одноразовую команду helper и разбирает её JSON-ответ. Явно отклоняет недопустимое состояние через PhotosAccessDenied, PhotosAdapterError.

```python
def _run(self, *arguments: str, timeout: int=120) -> dict[str, Any]
```

Прямые выражения вызова: [PhotosAccessDenied](../../media_manager/photos_adapter.py#L29), [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `json.loads`, `payload.get`, `result.stderr.strip`, `result.stdout.strip`, [self.ensure_built](../../media_manager/photos_adapter.py#L93), `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(output or 'PhotoKit-адаптер не вернул JSON')`
- `PhotosAccessDenied(str(payload.get('status') or payload.get('error')))`
- `PhotosAdapterError(str(payload.get('error') or output))`

Перехватываемые типы: `json.JSONDecodeError`.

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-systemphotosadapter-status"></a>

## `SystemPhotosAdapter.status`

[media_manager/photos_adapter.py:177](../../media_manager/photos_adapter.py#L177)

Проверяет или запрашивает разрешение PhotoKit без scripting fallback. Явно отклоняет недопустимое состояние через PhotosAccessDenied.

```python
def status(self, *, request_authorization: bool=False) -> dict[str, Any]
```

Присваивания полям `self`: `_backend`.

Прямые выражения вызова: [PhotosAccessDenied](../../media_manager/photos_adapter.py#L29), `dict`, `payload.get`, [self._request](../../media_manager/photos_adapter.py#L328), [self._run](../../media_manager/photos_adapter.py#L155), `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAccessDenied('Разреши доступ media.actu Photos adapter в macOS → Конфиденциальность → Фото')`

Выражения возврата (ветви, без исполнения):

- `dict(payload, backend='photokit')`
- `{**payload, 'backend': self._backend}`


<a id="symbol-systemphotosadapter-close"></a>

## `SystemPhotosAdapter.close`

[media_manager/photos_adapter.py:199](../../media_manager/photos_adapter.py#L199)

Закрывает клиентский канал и принадлежащий клиенту дочерний процесс. Обновляет состояние объекта: _buffer, _gui_pid, _process, _socket, _socket_directory, _socket_path.

```python
def close(self)
```

Присваивания полям `self`: `_buffer`, `_gui_pid`, `_process`, `_socket`, `_socket_directory`, `_socket_path`.

Прямые выражения вызова: `connection.close`, `connection.sendall`, `process.kill`, `process.poll`, `process.terminate`, `process.wait`, `stream.close`.

Перехватываемые типы: `OSError`, `subprocess.TimeoutExpired`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter--ipc-directory"></a>

## `SystemPhotosAdapter._ipc_directory`

[media_manager/photos_adapter.py:231](../../media_manager/photos_adapter.py#L231)

Возвращает отдельный каталог Unix-сокета для текущего пользователя. Использует Path, os.getuid, os.uname, tempfile.gettempdir.

```python
def _ipc_directory(self)
```

Прямые выражения вызова: `Path`, `os.getuid`, `os.uname`, `tempfile.gettempdir`.

Выражения возврата (ветви, без исполнения):

- `Path('/private/tmp' if os.uname().sysname == 'Darwin' else tempfile.gettempdir()) / f'media-actu-photos-v2-{os.getuid()}'`


<a id="symbol-systemphotosadapter--connect-gui"></a>

## `SystemPhotosAdapter._connect_gui`

[media_manager/photos_adapter.py:236](../../media_manager/photos_adapter.py#L236)

Подключает клиент к GUI-службе после проверки приватности IPC-каталога. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _connect_gui(self)
```

Присваивания полям `self`: `_socket`, `_socket_directory`, `_socket_path`.

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `connection.close`, `connection.connect`, `directory.lstat`, `directory.mkdir`, `os.getuid`, [self._ipc_directory](../../media_manager/photos_adapter.py#L231), [self.close](../../media_manager/photos_adapter.py#L199), [self.ensure_built](../../media_manager/photos_adapter.py#L93), `socket.socket`, `stat.S_IMODE`, `stat.S_ISDIR`, `str`, `subprocess.run`, `time.monotonic`, `time.sleep`.

Явные `raise`:

- `PhotosAdapterError('Небезопасный каталог связи с PhotoKit')`
- `PhotosAdapterError('Не удалось подключить GUI-помощник PhotoKit')`

Перехватываемые типы: `(FileNotFoundError, ConnectionRefusedError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-systemphotosadapter--begin"></a>

## `SystemPhotosAdapter._begin`

[media_manager/photos_adapter.py:264](../../media_manager/photos_adapter.py#L264)

Подготавливает GUI-соединение или stdin/stdout-процесс и отправляет запрос. Обновляет состояние объекта: _process.

```python
def _begin(self, request)
```

Присваивания полям `self`: `_process`.

Прямые выражения вызова: [self._connect_gui](../../media_manager/photos_adapter.py#L236), `self._process.poll`, [self._send](../../media_manager/photos_adapter.py#L277), [self.close](../../media_manager/photos_adapter.py#L199), [self.ensure_built](../../media_manager/photos_adapter.py#L93), `str`, `subprocess.Popen`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter--send"></a>

## `SystemPhotosAdapter._send`

[media_manager/photos_adapter.py:277](../../media_manager/photos_adapter.py#L277)

Передаёт один JSON-запрос с разделителем строки в текущий канал. Использует (json.dumps(request) + '\n').encode, json.dumps, self._process.stdin.flush, self._process.stdin.write, self._socket.sendall.

```python
def _send(self, request)
```

Прямые выражения вызова: `(json.dumps(request) + '\n').encode`, `json.dumps`, `self._process.stdin.flush`, `self._process.stdin.write`, `self._socket.sendall`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter--receive"></a>

## `SystemPhotosAdapter._receive`

[media_manager/photos_adapter.py:287](../../media_manager/photos_adapter.py#L287)

Читает ограниченную строку ответа с тайм-аутом и сохранением остатка буфера. Явно отклоняет недопустимое состояние через PhotosAdapterError, PhotosResponseTimeout.

```python
def _receive(self, timeout, *, limit=128 * 1024 * 1024)
```

Присваивания полям `self`: `_buffer`, `_gui_pid`.

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), [PhotosResponseTimeout](../../media_manager/photos_adapter.py#L53), `json.loads`, `len`, `os.read`, `payload.get`, `selector.register`, `selector.select`, `selectors.DefaultSelector`, `self._buffer.split`, `stream.fileno`, `time.monotonic`.

Явные `raise`:

- `PhotosResponseTimeout('PhotoKit не ответил вовремя')`
- `PhotosAdapterError('PhotoKit завершил соединение')`
- `PhotosAdapterError('Слишком большой ответ PhotoKit')`

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-systemphotosadapter--check-response"></a>

## `SystemPhotosAdapter._check_response`

[media_manager/photos_adapter.py:313](../../media_manager/photos_adapter.py#L313)

Преобразует статус helper в подходящий тип исключения Python. Явно отклоняет недопустимое состояние через PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable, PhotosThumbnailPending и ещё 1.

```python
def _check_response(payload)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: [PhotosAccessDenied](../../media_manager/photos_adapter.py#L29), [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), [PhotosLibraryUnavailable](../../media_manager/photos_adapter.py#L35), [PhotosThumbnailPending](../../media_manager/photos_adapter.py#L41), [PhotosTransferStopped](../../media_manager/photos_adapter.py#L47), `payload.get`, `str`.

Явные `raise`:

- `PhotosAccessDenied('PhotoKit: требуется разрешение macOS на чтение Фото')`
- `PhotosLibraryUnavailable('Открыта другая медиатека Photos. Подключи нужную запись.')`
- `PhotosThumbnailPending('Миниатюра пока недоступна локально в Photos')`
- `PhotosTransferStopped('Сохранение приостановлено')`
- `PhotosAdapterError(str(payload['error']))`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter--request"></a>

## `SystemPhotosAdapter._request`

[media_manager/photos_adapter.py:328](../../media_manager/photos_adapter.py#L328)

Выполняет сериализованный запрос и закрывает клиентский канал при транспортном сбое. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _request(self, request, *, timeout=30)
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), [self._begin](../../media_manager/photos_adapter.py#L264), [self._check_response](../../media_manager/photos_adapter.py#L313), [self._receive](../../media_manager/photos_adapter.py#L287), [self.close](../../media_manager/photos_adapter.py#L199), `str`.

Явные `raise`:

- `PhotosAdapterError(str(error))`

Перехватываемые типы: `(OSError, ValueError, subprocess.SubprocessError, PhotosAdapterError)`.

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-systemphotosadapter--stream-request"></a>

## `SystemPhotosAdapter._stream_request`

[media_manager/photos_adapter.py:341](../../media_manager/photos_adapter.py#L341)

Принимает события потока до завершающего ответа с поддержкой отмены. Явно отклоняет недопустимое состояние через PhotosAdapterError, PhotosTransferStopped.

```python
def _stream_request(self, request, receive, stopped)
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), [PhotosTransferStopped](../../media_manager/photos_adapter.py#L47), `dict`, `payload.get`, `receive`, [self._begin](../../media_manager/photos_adapter.py#L264), [self._check_response](../../media_manager/photos_adapter.py#L313), [self._receive](../../media_manager/photos_adapter.py#L287), [self._send](../../media_manager/photos_adapter.py#L277), [self.close](../../media_manager/photos_adapter.py#L199), `stopped`, `time.monotonic`, `uuid.uuid4`.

Явные `raise`:

- `PhotosTransferStopped('Сохранение приостановлено')`
- `PhotosAdapterError('Photos долго не передаёт данные. Повтори сохранение позже.')`

Перехватываемые типы: `PhotosResponseTimeout`, `BaseException`.

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-systemphotosadapter-original-manifest"></a>

## `SystemPhotosAdapter.original_manifest`

[media_manager/photos_adapter.py:376](../../media_manager/photos_adapter.py#L376)

Запрашивает поток манифеста оригиналов и передаёт объекты обработчику. Использует self._stream_request.

```python
def original_manifest(self, anchors, receive_asset, stopped)
```

Прямые выражения вызова: `dict`, `list`, [self._stream_request](../../media_manager/photos_adapter.py#L341).

Выражения возврата (ветви, без исполнения):

- `self._stream_request(dict(op='original_manifest', anchors=list(anchors)), receive, stopped)`


<a id="symbol-systemphotosadapter-original-manifest-receive"></a>

## `SystemPhotosAdapter.original_manifest.receive`

[media_manager/photos_adapter.py:379](../../media_manager/photos_adapter.py#L379)

Передаёт объект события манифеста вызывающему обработчику. Использует payload.get, receive_asset.

```python
def receive(payload)
```

Прямые выражения вызова: `payload.get`, `receive_asset`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter-stream-original"></a>

## `SystemPhotosAdapter.stream_original`

[media_manager/photos_adapter.py:386](../../media_manager/photos_adapter.py#L386)

Декодирует ограниченные блоки оригинала и передаёт данные и прогресс в Core. Использует self._stream_request.

```python
def stream_original(self, identifier, resource_id, version, anchors, write, progress, stopped)
```

Прямые выражения вызова: `dict`, `list`, [self._stream_request](../../media_manager/photos_adapter.py#L341).

Выражения возврата (ветви, без исполнения):

- `self._stream_request(dict(op='original_resource', identifier=identifier, resource_id=resource_id, version=version, anchors=list(anchors)), receive, stopped)`


<a id="symbol-systemphotosadapter-stream-original-receive"></a>

## `SystemPhotosAdapter.stream_original.receive`

[media_manager/photos_adapter.py:389](../../media_manager/photos_adapter.py#L389)

Проверяет размер декодированного блока и распределяет события данных и прогресса. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def receive(payload)
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `base64.b64decode`, `float`, `len`, `max`, `min`, `payload.get`, `progress`, `write`.

Явные `raise`:

- `PhotosAdapterError('Некорректный блок оригинала')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter-probe"></a>

## `SystemPhotosAdapter.probe`

[media_manager/photos_adapter.py:402](../../media_manager/photos_adapter.py#L402)

Проверяет текущую медиатеку по якорным ID с возможностью переподключения. Использует self._request, self.close.

```python
def probe(self, identifiers=(), *, restart=False)
```

Прямые выражения вызова: `dict`, `list`, [self._request](../../media_manager/photos_adapter.py#L328), [self.close](../../media_manager/photos_adapter.py#L199).

Выражения возврата (ветви, без исполнения):

- `self._request(dict(op='probe', identifiers=list(identifiers)))`


<a id="symbol-systemphotosadapter-scan"></a>

## `SystemPhotosAdapter.scan`

[media_manager/photos_adapter.py:410](../../media_manager/photos_adapter.py#L410)

Получает индекс объектов подтверждённой медиатеки через постоянный helper. Использует self._request, self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get.

```python
def scan(self, anchors=()) -> list[dict[str, Any]]
```

Прямые выражения вызова: `dict`, `list`, [self._request](../../media_manager/photos_adapter.py#L328), `self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get`.

Выражения возврата (ветви, без исполнения):

- `list(self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get('assets', []))`


<a id="symbol-systemphotosadapter-create-thumbnail"></a>

## `SystemPhotosAdapter.create_thumbnail`

[media_manager/photos_adapter.py:415](../../media_manager/photos_adapter.py#L415)

Получает JPEG-превью PhotoKit и атомарно сохраняет его в кэш. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def create_thumbnail(self, asset_identifier: str, target: Path, width: int=640, height: int=480, *, anchors=()) -> Path
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `base64.b64decode`, `dict`, `len`, `list`, [self._request](../../media_manager/photos_adapter.py#L328), `target.parent.mkdir`, `target.with_name`, `temporary.replace`, `temporary.unlink`, `temporary.write_bytes`, `uuid.uuid4`.

Явные `raise`:

- `PhotosAdapterError('PhotoKit не вернул JPEG-превью')`
- `PhotosAdapterError('Некорректный размер JPEG-превью')`

Перехватываемые типы: `(KeyError, TypeError, ValueError)`.

Выражения возврата (ветви, без исполнения):

- `target`


<a id="symbol-systemphotosadapter-open-asset"></a>

## `SystemPhotosAdapter.open_asset`

[media_manager/photos_adapter.py:438](../../media_manager/photos_adapter.py#L438)

Выделяет объект в Photos через действующий open.applescript. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def open_asset(self, asset_identifier: str) -> None
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `result.stderr.strip`, `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(result.stderr.strip() or 'Не удалось открыть объект в Photos')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-systemphotosadapter--applescript-status"></a>

## `SystemPhotosAdapter._applescript_status`

[media_manager/photos_adapter.py:457](../../media_manager/photos_adapter.py#L457)

Сохраняет прежнюю проверку Photos через scripting API без текущих вызовов. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _applescript_status(self) -> dict[str, Any]
```

Прямые выражения вызова: [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `int`, `result.stderr.strip`, `result.stdout.strip`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(result.stderr.strip() or 'Нет доступа к Photos')`

Выражения возврата (ветви, без исполнения):

- `{'status': 'authorized', 'count': int(result.stdout.strip() or 0)}`


<a id="symbol-systemphotosadapter--applescript-scan"></a>

## `SystemPhotosAdapter._applescript_scan`

[media_manager/photos_adapter.py:471](../../media_manager/photos_adapter.py#L471)

Сохраняет прежнее чтение каталога через scan.js без текущих вызовов. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _applescript_scan(self) -> list[dict[str, Any]]
```

Прямые выражения вызова: `Path`, `Path(str(asset.get('name') or '')).suffix.lower`, [PhotosAdapterError](../../media_manager/photos_adapter.py#L23), `asset.get`, `assets.append`, `json.loads`, `payload.get`, `result.stderr.strip`, `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(result.stderr.strip() or 'Не удалось прочитать Photos')`
- `PhotosAdapterError('Photos вернул некорректный каталог')`

Перехватываемые типы: `json.JSONDecodeError`.

Выражения возврата (ветви, без исполнения):

- `assets`
