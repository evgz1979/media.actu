# Python-клиент PhotoKit: `media_manager/photos_adapter.py`

Собирает локальный helper, подключается к Unix-сокету GUI-службы, передаёт JSON-запросы и ограниченные потоки ресурсов. Старые scripting-методы сохранены, но не входят в текущий путь вызовов.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/photos_adapter.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/scanner.py](media_manager--scanner.md).
Импортируется модулями: [app.py](app.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_originals.py](media_manager--photos_originals.md), [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md), [media_manager/thumbnails.py](media_manager--thumbnails.md), [scripts/build_documentation.py](scripts--build_documentation.md).
Тестовые модули с прямым импортом: [tests/test_photo_libraries.py](tests.md#module-tests.test_photo_libraries), [tests/test_photos_adapter.py](tests.md#module-tests.test_photos_adapter), [tests/test_photos_copy_chain.py](tests.md#module-tests.test_photos_copy_chain), [tests/test_photos_originals.py](tests.md#module-tests.test_photos_originals), [tests/test_photos_schedule.py](tests.md#module-tests.test_photos_schedule).

## Оглавление определений

- [PhotosAccessDenied](#symbol-PhotosAccessDenied) — Обозначает отсутствие системного разрешения на чтение Photos.
- [PhotosAdapterError](#symbol-PhotosAdapterError) — Обозначает ошибку сборки, транспорта или ответа адаптера Photos.
- [PhotosLibraryUnavailable](#symbol-PhotosLibraryUnavailable) — Обозначает смену или временную недоступность нужной медиатеки.
- [PhotosResponseTimeout](#symbol-PhotosResponseTimeout) — Обозначает превышение времени ожидания ответа локального helper.
- [PhotosThumbnailPending](#symbol-PhotosThumbnailPending) — Обозначает отсутствие локальной миниатюры без загрузки оригинала.
- [PhotosTransferStopped](#symbol-PhotosTransferStopped) — Обозначает кооперативную остановку потоковой передачи оригинала.
- [SystemPhotosAdapter](#symbol-SystemPhotosAdapter) — Обменивается запросами с локальным PhotoKit-helper и открывает объекты в Photos.
- [SystemPhotosAdapter.__init__](#symbol-SystemPhotosAdapter.__init__) — Инициализирует SystemPhotosAdapter и его рабочее состояние.
- [SystemPhotosAdapter._applescript_scan](#symbol-SystemPhotosAdapter._applescript_scan) — Сохраняет прежнее чтение каталога через scan.js без текущих вызовов.
- [SystemPhotosAdapter._applescript_status](#symbol-SystemPhotosAdapter._applescript_status) — Сохраняет прежнюю проверку Photos через scripting API без текущих вызовов.
- [SystemPhotosAdapter._begin](#symbol-SystemPhotosAdapter._begin) — Подготавливает GUI-соединение или stdin/stdout-процесс и отправляет запрос.
- [SystemPhotosAdapter._check_response](#symbol-SystemPhotosAdapter._check_response) — Преобразует статус helper в подходящий тип исключения Python.
- [SystemPhotosAdapter._connect_gui](#symbol-SystemPhotosAdapter._connect_gui) — Подключает клиент к GUI-службе после проверки приватности IPC-каталога.
- [SystemPhotosAdapter._ipc_directory](#symbol-SystemPhotosAdapter._ipc_directory) — Возвращает отдельный каталог Unix-сокета для текущего пользователя.
- [SystemPhotosAdapter._receive](#symbol-SystemPhotosAdapter._receive) — Читает ограниченную строку ответа с тайм-аутом и сохранением остатка буфера.
- [SystemPhotosAdapter._request](#symbol-SystemPhotosAdapter._request) — Выполняет сериализованный запрос и закрывает клиентский канал при транспортном сбое.
- [SystemPhotosAdapter._run](#symbol-SystemPhotosAdapter._run) — Исполняет одноразовую команду helper и разбирает её JSON-ответ.
- [SystemPhotosAdapter._send](#symbol-SystemPhotosAdapter._send) — Передаёт один JSON-запрос с разделителем строки в текущий канал.
- [SystemPhotosAdapter._stream_request](#symbol-SystemPhotosAdapter._stream_request) — Принимает события потока до завершающего ответа с поддержкой отмены.
- [SystemPhotosAdapter.close](#symbol-SystemPhotosAdapter.close) — Закрывает клиентский канал и принадлежащий клиенту дочерний процесс.
- [SystemPhotosAdapter.create_thumbnail](#symbol-SystemPhotosAdapter.create_thumbnail) — Получает JPEG-превью PhotoKit и атомарно сохраняет его в кэш.
- [SystemPhotosAdapter.ensure_built](#symbol-SystemPhotosAdapter.ensure_built) — Собирает и локально подписывает app-bundle при изменении исходников helper.
- [SystemPhotosAdapter.open_asset](#symbol-SystemPhotosAdapter.open_asset) — Выделяет объект в Photos через действующий open.applescript.
- [SystemPhotosAdapter.original_manifest](#symbol-SystemPhotosAdapter.original_manifest) — Запрашивает поток манифеста оригиналов и передаёт объекты обработчику.
- [SystemPhotosAdapter.original_manifest.receive](#symbol-SystemPhotosAdapter.original_manifest.receive) — Передаёт объект события манифеста вызывающему обработчику.
- [SystemPhotosAdapter.probe](#symbol-SystemPhotosAdapter.probe) — Проверяет текущую медиатеку по якорным ID с возможностью переподключения.
- [SystemPhotosAdapter.reuse_indexed_backend](#symbol-SystemPhotosAdapter.reuse_indexed_backend) — Сбрасывает прежнее поле выбора backend; вызовов в текущем проекте не найдено.
- [SystemPhotosAdapter.scan](#symbol-SystemPhotosAdapter.scan) — Получает индекс объектов подтверждённой медиатеки через постоянный helper.
- [SystemPhotosAdapter.status](#symbol-SystemPhotosAdapter.status) — Проверяет или запрашивает разрешение PhotoKit без scripting fallback.
- [SystemPhotosAdapter.stream_original](#symbol-SystemPhotosAdapter.stream_original) — Декодирует ограниченные блоки оригинала и передаёт данные и прогресс в Core.
- [SystemPhotosAdapter.stream_original.receive](#symbol-SystemPhotosAdapter.stream_original.receive) — Проверяет размер декодированного блока и распределяет события данных и прогресса.
- [SystemPhotosAdapter.supported](#symbol-SystemPhotosAdapter.supported) — Проверяет доступность macOS и компилятора clang для нативного адаптера.

<a id="symbol-PhotosAccessDenied"></a>

## `PhotosAccessDenied`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `PhotosAccessDenied`

Обозначает отсутствие системного разрешения на чтение Photos. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет.

<a id="symbol-PhotosAdapterError"></a>

## `PhotosAdapterError`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `PhotosAdapterError`

Обозначает ошибку сборки, транспорта или ответа адаптера Photos. Базовые типы: RuntimeError.

Базовые классы: `RuntimeError`.


Именованные методы: собственных методов нет.

<a id="symbol-PhotosLibraryUnavailable"></a>

## `PhotosLibraryUnavailable`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `PhotosLibraryUnavailable`

Обозначает смену или временную недоступность нужной медиатеки. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет.

<a id="symbol-PhotosResponseTimeout"></a>

## `PhotosResponseTimeout`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `PhotosResponseTimeout`

Обозначает превышение времени ожидания ответа локального helper. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет.

<a id="symbol-PhotosThumbnailPending"></a>

## `PhotosThumbnailPending`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `PhotosThumbnailPending`

Обозначает отсутствие локальной миниатюры без загрузки оригинала. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет.

<a id="symbol-PhotosTransferStopped"></a>

## `PhotosTransferStopped`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `PhotosTransferStopped`

Обозначает кооперативную остановку потоковой передачи оригинала. Базовые типы: PhotosAdapterError.

Базовые классы: `PhotosAdapterError`.


Именованные методы: собственных методов нет.

<a id="symbol-SystemPhotosAdapter"></a>

## `SystemPhotosAdapter`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter`

Обменивается запросами с локальным PhotoKit-helper и открывает объекты в Photos. Зависимости конструктора: source_directory, build_directory.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_backend`, `_buffer`, `_build_lock`, `_gui_pid`, `_operation_lock`, `_process`, `_socket`, `_socket_directory`, `_socket_path`, `app_directory`, `build_directory`, `executable`, `source_directory`, `use_gui`.

Именованные методы: `__init__`, `supported`, `reuse_indexed_backend`, `ensure_built`, `_run`, `status`, `close`, `_ipc_directory`, `_connect_gui`, `_begin`, `_send`, `_receive`, `_check_response`, `_request`, `_stream_request`, `original_manifest`, `stream_original`, `probe`, `scan`, `create_thumbnail`, `open_asset`, `_applescript_status`, `_applescript_scan`.

<a id="symbol-SystemPhotosAdapter.__init__"></a>

## `SystemPhotosAdapter.__init__`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.__init__`

Инициализирует SystemPhotosAdapter и его рабочее состояние. Обновляет состояние объекта: _backend, _buffer, _build_lock, _gui_pid, _operation_lock, _process, _socket, _socket_directory, _socket_path, app_directory и ещё 4.

```python
def __init__(self, source_directory: Path, build_directory: Path) -> None
```

Присваивания полям `self`: `_backend`, `_buffer`, `_build_lock`, `_gui_pid`, `_operation_lock`, `_process`, `_socket`, `_socket_directory`, `_socket_path`, `app_directory`, `build_directory`, `executable`, `source_directory`, `use_gui`.

Прямые выражения вызова: `os.uname`, `threading.Lock`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter._applescript_scan"></a>

## `SystemPhotosAdapter._applescript_scan`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._applescript_scan`

Сохраняет прежнее чтение каталога через scan.js без текущих вызовов. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _applescript_scan(self) -> list[dict[str, Any]]
```

Прямые выражения вызова: `Path`, `Path(str(asset.get('name') or '')).suffix.lower`, [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `asset.get`, `assets.append`, `json.loads`, `payload.get`, `result.stderr.strip`, `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(result.stderr.strip() or 'Не удалось прочитать Photos')`
- `PhotosAdapterError('Photos вернул некорректный каталог')`

Перехватываемые типы: `json.JSONDecodeError`.

Выражения возврата (ветви, без исполнения):

- `assets`


<a id="symbol-SystemPhotosAdapter._applescript_status"></a>

## `SystemPhotosAdapter._applescript_status`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._applescript_status`

Сохраняет прежнюю проверку Photos через scripting API без текущих вызовов. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _applescript_status(self) -> dict[str, Any]
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `int`, `result.stderr.strip`, `result.stdout.strip`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(result.stderr.strip() or 'Нет доступа к Photos')`

Выражения возврата (ветви, без исполнения):

- `{'status': 'authorized', 'count': int(result.stdout.strip() or 0)}`


<a id="symbol-SystemPhotosAdapter._begin"></a>

## `SystemPhotosAdapter._begin`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._begin`

Подготавливает GUI-соединение или stdin/stdout-процесс и отправляет запрос. Обновляет состояние объекта: _process.

```python
def _begin(self, request)
```

Присваивания полям `self`: `_process`.

Прямые выражения вызова: [self._connect_gui](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._connect_gui), `self._process.poll`, [self._send](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._send), [self.close](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.close), [self.ensure_built](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.ensure_built), `str`, `subprocess.Popen`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter._check_response"></a>

## `SystemPhotosAdapter._check_response`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._check_response`

Преобразует статус helper в подходящий тип исключения Python. Явно отклоняет недопустимое состояние через PhotosAccessDenied, PhotosAdapterError, PhotosLibraryUnavailable, PhotosThumbnailPending и ещё 1.

```python
def _check_response(payload)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: [PhotosAccessDenied](media_manager--photos_adapter.md#symbol-PhotosAccessDenied), [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), [PhotosLibraryUnavailable](media_manager--photos_adapter.md#symbol-PhotosLibraryUnavailable), [PhotosThumbnailPending](media_manager--photos_adapter.md#symbol-PhotosThumbnailPending), [PhotosTransferStopped](media_manager--photos_adapter.md#symbol-PhotosTransferStopped), `payload.get`, `str`.

Явные `raise`:

- `PhotosAccessDenied('PhotoKit: требуется разрешение macOS на чтение Фото')`
- `PhotosLibraryUnavailable('Открыта другая медиатека Photos. Подключи нужную запись.')`
- `PhotosThumbnailPending('Миниатюра пока недоступна локально в Photos')`
- `PhotosTransferStopped('Сохранение приостановлено')`
- `PhotosAdapterError(str(payload['error']))`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter._connect_gui"></a>

## `SystemPhotosAdapter._connect_gui`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._connect_gui`

Подключает клиент к GUI-службе после проверки приватности IPC-каталога. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _connect_gui(self)
```

Присваивания полям `self`: `_socket`, `_socket_directory`, `_socket_path`.

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `connection.close`, `connection.connect`, `directory.lstat`, `directory.mkdir`, `os.getuid`, [self._ipc_directory](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._ipc_directory), [self.close](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.close), [self.ensure_built](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.ensure_built), `socket.socket`, `stat.S_IMODE`, `stat.S_ISDIR`, `str`, `subprocess.run`, `time.monotonic`, `time.sleep`.

Явные `raise`:

- `PhotosAdapterError('Небезопасный каталог связи с PhotoKit')`
- `PhotosAdapterError('Не удалось подключить GUI-помощник PhotoKit')`

Перехватываемые типы: `(FileNotFoundError, ConnectionRefusedError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-SystemPhotosAdapter._ipc_directory"></a>

## `SystemPhotosAdapter._ipc_directory`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._ipc_directory`

Возвращает отдельный каталог Unix-сокета для текущего пользователя. Использует Path, os.getuid, os.uname, tempfile.gettempdir.

```python
def _ipc_directory(self)
```

Прямые выражения вызова: `Path`, `os.getuid`, `os.uname`, `tempfile.gettempdir`.

Выражения возврата (ветви, без исполнения):

- `Path('/private/tmp' if os.uname().sysname == 'Darwin' else tempfile.gettempdir()) / f'media-actu-photos-v2-{os.getuid()}'`


<a id="symbol-SystemPhotosAdapter._receive"></a>

## `SystemPhotosAdapter._receive`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._receive`

Читает ограниченную строку ответа с тайм-аутом и сохранением остатка буфера. Явно отклоняет недопустимое состояние через PhotosAdapterError, PhotosResponseTimeout.

```python
def _receive(self, timeout, *, limit=128 * 1024 * 1024)
```

Присваивания полям `self`: `_buffer`, `_gui_pid`.

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), [PhotosResponseTimeout](media_manager--photos_adapter.md#symbol-PhotosResponseTimeout), `json.loads`, `len`, `os.read`, `payload.get`, `selector.register`, `selector.select`, `selectors.DefaultSelector`, `self._buffer.split`, `stream.fileno`, `time.monotonic`.

Явные `raise`:

- `PhotosResponseTimeout('PhotoKit не ответил вовремя')`
- `PhotosAdapterError('PhotoKit завершил соединение')`
- `PhotosAdapterError('Слишком большой ответ PhotoKit')`

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-SystemPhotosAdapter._request"></a>

## `SystemPhotosAdapter._request`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._request`

Выполняет сериализованный запрос и закрывает клиентский канал при транспортном сбое. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def _request(self, request, *, timeout=30)
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), [self._begin](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._begin), [self._check_response](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._check_response), [self._receive](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._receive), [self.close](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.close), `str`.

Явные `raise`:

- `PhotosAdapterError(str(error))`

Перехватываемые типы: `(OSError, ValueError, subprocess.SubprocessError, PhotosAdapterError)`.

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-SystemPhotosAdapter._run"></a>

## `SystemPhotosAdapter._run`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._run`

Исполняет одноразовую команду helper и разбирает её JSON-ответ. Явно отклоняет недопустимое состояние через PhotosAccessDenied, PhotosAdapterError.

```python
def _run(self, *arguments: str, timeout: int=120) -> dict[str, Any]
```

Прямые выражения вызова: [PhotosAccessDenied](media_manager--photos_adapter.md#symbol-PhotosAccessDenied), [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `json.loads`, `payload.get`, `result.stderr.strip`, `result.stdout.strip`, [self.ensure_built](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.ensure_built), `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(output or 'PhotoKit-адаптер не вернул JSON')`
- `PhotosAccessDenied(str(payload.get('status') or payload.get('error')))`
- `PhotosAdapterError(str(payload.get('error') or output))`

Перехватываемые типы: `json.JSONDecodeError`.

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-SystemPhotosAdapter._send"></a>

## `SystemPhotosAdapter._send`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._send`

Передаёт один JSON-запрос с разделителем строки в текущий канал. Использует (json.dumps(request) + '\n').encode, json.dumps, self._process.stdin.flush, self._process.stdin.write, self._socket.sendall.

```python
def _send(self, request)
```

Прямые выражения вызова: `(json.dumps(request) + '\n').encode`, `json.dumps`, `self._process.stdin.flush`, `self._process.stdin.write`, `self._socket.sendall`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter._stream_request"></a>

## `SystemPhotosAdapter._stream_request`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter._stream_request`

Принимает события потока до завершающего ответа с поддержкой отмены. Явно отклоняет недопустимое состояние через PhotosAdapterError, PhotosTransferStopped.

```python
def _stream_request(self, request, receive, stopped)
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), [PhotosTransferStopped](media_manager--photos_adapter.md#symbol-PhotosTransferStopped), `dict`, `payload.get`, `receive`, [self._begin](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._begin), [self._check_response](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._check_response), [self._receive](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._receive), [self._send](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._send), [self.close](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.close), `stopped`, `time.monotonic`, `uuid.uuid4`.

Явные `raise`:

- `PhotosTransferStopped('Сохранение приостановлено')`
- `PhotosAdapterError('Photos долго не передаёт данные. Повтори сохранение позже.')`

Перехватываемые типы: `PhotosResponseTimeout`, `BaseException`.

Выражения возврата (ветви, без исполнения):

- `payload`


<a id="symbol-SystemPhotosAdapter.close"></a>

## `SystemPhotosAdapter.close`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.close`

Закрывает клиентский канал и принадлежащий клиенту дочерний процесс. Обновляет состояние объекта: _buffer, _gui_pid, _process, _socket, _socket_directory, _socket_path.

```python
def close(self)
```

Присваивания полям `self`: `_buffer`, `_gui_pid`, `_process`, `_socket`, `_socket_directory`, `_socket_path`.

Прямые выражения вызова: `connection.close`, `connection.sendall`, `process.kill`, `process.poll`, `process.terminate`, `process.wait`, `stream.close`.

Перехватываемые типы: `OSError`, `subprocess.TimeoutExpired`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter.create_thumbnail"></a>

## `SystemPhotosAdapter.create_thumbnail`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.create_thumbnail`

Получает JPEG-превью PhotoKit и атомарно сохраняет его в кэш. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def create_thumbnail(self, asset_identifier: str, target: Path, width: int=640, height: int=480, *, anchors=()) -> Path
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `base64.b64decode`, `dict`, `len`, `list`, [self._request](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._request), `target.parent.mkdir`, `target.with_name`, `temporary.replace`, `temporary.unlink`, `temporary.write_bytes`, `uuid.uuid4`.

Явные `raise`:

- `PhotosAdapterError('PhotoKit не вернул JPEG-превью')`
- `PhotosAdapterError('Некорректный размер JPEG-превью')`

Перехватываемые типы: `(KeyError, TypeError, ValueError)`.

Выражения возврата (ветви, без исполнения):

- `target`


<a id="symbol-SystemPhotosAdapter.ensure_built"></a>

## `SystemPhotosAdapter.ensure_built`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.ensure_built`

Собирает и локально подписывает app-bundle при изменении исходников helper. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def ensure_built(self) -> None
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `macos.mkdir`, `max`, `os.environ.copy`, `plist.stat`, `result.stderr.strip`, `self.executable.exists`, `self.executable.stat`, `shutil.copy2`, `source.stat`, `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError('PhotoKit доступен только на macOS')`
- `PhotosAdapterError(result.stderr.strip() or 'Не удалось собрать PhotoKit-адаптер')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-SystemPhotosAdapter.open_asset"></a>

## `SystemPhotosAdapter.open_asset`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.open_asset`

Выделяет объект в Photos через действующий open.applescript. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def open_asset(self, asset_identifier: str) -> None
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `result.stderr.strip`, `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAdapterError(result.stderr.strip() or 'Не удалось открыть объект в Photos')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter.original_manifest"></a>

## `SystemPhotosAdapter.original_manifest`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.original_manifest`

Запрашивает поток манифеста оригиналов и передаёт объекты обработчику. Использует self._stream_request.

```python
def original_manifest(self, anchors, receive_asset, stopped)
```

Прямые выражения вызова: `dict`, `list`, [self._stream_request](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._stream_request).

Выражения возврата (ветви, без исполнения):

- `self._stream_request(dict(op='original_manifest', anchors=list(anchors)), receive, stopped)`


<a id="symbol-SystemPhotosAdapter.original_manifest.receive"></a>

## `SystemPhotosAdapter.original_manifest.receive`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.original_manifest.receive`

Передаёт объект события манифеста вызывающему обработчику. Использует payload.get, receive_asset.

```python
def receive(payload)
```

Прямые выражения вызова: `payload.get`, `receive_asset`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter.probe"></a>

## `SystemPhotosAdapter.probe`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.probe`

Проверяет текущую медиатеку по якорным ID с возможностью переподключения. Использует self._request, self.close.

```python
def probe(self, identifiers=(), *, restart=False)
```

Прямые выражения вызова: `dict`, `list`, [self._request](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._request), [self.close](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter.close).

Выражения возврата (ветви, без исполнения):

- `self._request(dict(op='probe', identifiers=list(identifiers)))`


<a id="symbol-SystemPhotosAdapter.reuse_indexed_backend"></a>

## `SystemPhotosAdapter.reuse_indexed_backend`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.reuse_indexed_backend`

Сбрасывает прежнее поле выбора backend; вызовов в текущем проекте не найдено. Обновляет состояние объекта: _backend.

```python
def reuse_indexed_backend(self) -> None
```

Присваивания полям `self`: `_backend`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter.scan"></a>

## `SystemPhotosAdapter.scan`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.scan`

Получает индекс объектов подтверждённой медиатеки через постоянный helper. Использует self._request, self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get.

```python
def scan(self, anchors=()) -> list[dict[str, Any]]
```

Прямые выражения вызова: `dict`, `list`, [self._request](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._request), `self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get`.

Выражения возврата (ветви, без исполнения):

- `list(self._request(dict(op='scan', anchors=list(anchors)), timeout=600).get('assets', []))`


<a id="symbol-SystemPhotosAdapter.status"></a>

## `SystemPhotosAdapter.status`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.status`

Проверяет или запрашивает разрешение PhotoKit без scripting fallback. Явно отклоняет недопустимое состояние через PhotosAccessDenied.

```python
def status(self, *, request_authorization: bool=False) -> dict[str, Any]
```

Присваивания полям `self`: `_backend`.

Прямые выражения вызова: [PhotosAccessDenied](media_manager--photos_adapter.md#symbol-PhotosAccessDenied), `dict`, `payload.get`, [self._request](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._request), [self._run](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._run), `str`, `subprocess.run`.

Явные `raise`:

- `PhotosAccessDenied('Разреши доступ media.actu Photos adapter в macOS → Конфиденциальность → Фото')`

Выражения возврата (ветви, без исполнения):

- `dict(payload, backend='photokit')`
- `{**payload, 'backend': self._backend}`


<a id="symbol-SystemPhotosAdapter.stream_original"></a>

## `SystemPhotosAdapter.stream_original`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.stream_original`

Декодирует ограниченные блоки оригинала и передаёт данные и прогресс в Core. Использует self._stream_request.

```python
def stream_original(self, identifier, resource_id, version, anchors, write, progress, stopped)
```

Прямые выражения вызова: `dict`, `list`, [self._stream_request](media_manager--photos_adapter.md#symbol-SystemPhotosAdapter._stream_request).

Выражения возврата (ветви, без исполнения):

- `self._stream_request(dict(op='original_resource', identifier=identifier, resource_id=resource_id, version=version, anchors=list(anchors)), receive, stopped)`


<a id="symbol-SystemPhotosAdapter.stream_original.receive"></a>

## `SystemPhotosAdapter.stream_original.receive`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.stream_original.receive`

Проверяет размер декодированного блока и распределяет события данных и прогресса. Явно отклоняет недопустимое состояние через PhotosAdapterError.

```python
def receive(payload)
```

Прямые выражения вызова: [PhotosAdapterError](media_manager--photos_adapter.md#symbol-PhotosAdapterError), `base64.b64decode`, `float`, `len`, `max`, `min`, `payload.get`, `progress`, `write`.

Явные `raise`:

- `PhotosAdapterError('Некорректный блок оригинала')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SystemPhotosAdapter.supported"></a>

## `SystemPhotosAdapter.supported`

[media_manager/photos_adapter.py](../../media_manager/photos_adapter.py) · `SystemPhotosAdapter.supported`

Проверяет доступность macOS и компилятора clang для нативного адаптера. Использует os.uname, shutil.which.

```python
def supported(self) -> bool
```

Декораторы: `property`.

Прямые выражения вызова: `os.uname`, `shutil.which`.

Выражения возврата (ветви, без исполнения):

- `os.uname().sysname == 'Darwin' and shutil.which('clang') is not None`
