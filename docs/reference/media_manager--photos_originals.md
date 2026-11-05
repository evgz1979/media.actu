# Сохранение оригиналов Photos: `media_manager/photos_originals.py`

Один координатор оригиналов: манифест PhotoKit, параметры файлов назначения, квитанции ресурсов, ограниченный буфер памяти, запись новых конечных файлов и зависимые копии.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/photos_originals.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_photos_copy_chain.py](tests.md#module-tests.test_photos_copy_chain), [tests/test_photos_originals.py](tests.md#module-tests.test_photos_originals), [tests/test_photos_schedule.py](tests.md#module-tests.test_photos_schedule).

## Оглавление определений

- [PhotosOriginals](#symbol-PhotosOriginals) — Сохраняет оригинальные ресурсы Photos и продолжает работу по квитанциям метаданных.
- [PhotosOriginals.__init__](#symbol-PhotosOriginals.__init__) — Инициализирует PhotosOriginals и его рабочее состояние.
- [PhotosOriginals._check](#symbol-PhotosOriginals._check) — Прерывает передачу при ручной остановке или закрытии разрешённого окна.
- [PhotosOriginals._cleanup](#symbol-PhotosOriginals._cleanup) — Удаляет подтверждённые старые временные файлы, сохраняя конечные незавершённые пути.
- [PhotosOriginals._counts](#symbol-PhotosOriginals._counts) — Пересчитывает готовые объекты и ресурсы по состояниям манифеста.
- [PhotosOriginals._create_original](#symbol-PhotosOriginals._create_original) — Исключительно создаёт свободное конечное имя и фиксирует намерение записи.
- [PhotosOriginals._db](#symbol-PhotosOriginals._db) — Предоставляет транзакционное соединение каталога с гарантированным закрытием.
- [PhotosOriginals._file](#symbol-PhotosOriginals._file) — Открывает готовый ресурс внутри папки копии только для чтения.
- [PhotosOriginals._inventory](#symbol-PhotosOriginals._inventory) — Индексирует имена и stat-параметры файлов копии без чтения содержимого.
- [PhotosOriginals._inventory.walk](#symbol-PhotosOriginals._inventory.walk) — Рекурсивно перечисляет обычные файлы и папки копии через дескрипторы.
- [PhotosOriginals._inventory_record](#symbol-PhotosOriginals._inventory_record) — Сохраняет параметры и поколение обнаруженного файла назначения.
- [PhotosOriginals._link](#symbol-PhotosOriginals._link) — Проверяет существование, медиатеку и подключение привязанной копии.
- [PhotosOriginals._log](#symbol-PhotosOriginals._log) — Добавляет событие оригиналов с уровнем, путём и временем.
- [PhotosOriginals._peer](#symbol-PhotosOriginals._peer) — Ищет квитанцию подходящего ресурса в разрешённой копии-источнике.
- [PhotosOriginals._prepare_replica](#symbol-PhotosOriginals._prepare_replica) — Подготавливает задание зависимой копии и сверяет её квитанции с манифестом.
- [PhotosOriginals._progress](#symbol-PhotosOriginals._progress) — Сохраняет промежуточный прогресс с ограничением частоты обновлений.
- [PhotosOriginals._receipt](#symbol-PhotosOriginals._receipt) — Фиксирует готовый ресурс, версию, параметры файла и завершение записи.
- [PhotosOriginals._replicate_all](#symbol-PhotosOriginals._replicate_all) — Дополняет зависимые копии готовыми ресурсами в порядке источников.
- [PhotosOriginals._restore_receipts](#symbol-PhotosOriginals._restore_receipts) — Восстанавливает готовность ресурсов по сохранённым версиям и квитанциям SQLite.
- [PhotosOriginals._reuse_receipt](#symbol-PhotosOriginals._reuse_receipt) — Принимает готовый ресурс повторно после проверки версии и параметров файла.
- [PhotosOriginals._save](#symbol-PhotosOriginals._save) — Повторно использует ресурс либо сохраняет поток в новый конечный файл.
- [PhotosOriginals._save.flush](#symbol-PhotosOriginals._save.flush) — Проверяет свободное место и записывает накопленный буфер в конечный файл.
- [PhotosOriginals._save.write](#symbol-PhotosOriginals._save.write) — Разбивает принятые данные на ограниченный буфер и публикует прогресс.
- [PhotosOriginals._stage](#symbol-PhotosOriginals._stage) — Журналирует созданный путь и его идентичность до передачи содержимого.
- [PhotosOriginals._stopped](#symbol-PhotosOriginals._stopped) — Проверяет ручной флаг остановки и временное окно медиатеки.
- [PhotosOriginals._stream_peer](#symbol-PhotosOriginals._stream_peer) — Передаёт готовый оригинал из другой копии с проверками источника.
- [PhotosOriginals._stream_peer.check](#symbol-PhotosOriginals._stream_peer.check) — Проверяет остановку, привязку, том и корень копии-источника между блоками.
- [PhotosOriginals._update](#symbol-PhotosOriginals._update) — Обновляет состояние и JSON-поля задания сохранения оригиналов.
- [PhotosOriginals._validate](#symbol-PhotosOriginals._validate) — Проверяет актуальность привязки, активность медиатеки, том и корневую папку.
- [PhotosOriginals._volume](#symbol-PhotosOriginals._volume) — Возвращает доступный том копии из уже обнаруженного состояния.
- [PhotosOriginals._write](#symbol-PhotosOriginals._write) — Полностью записывает блок через memoryview с проверкой остановки.
- [PhotosOriginals.close](#symbol-PhotosOriginals.close) — Запрашивает остановку воркера оригиналов при завершении Core.
- [PhotosOriginals.journal](#symbol-PhotosOriginals.journal) — Возвращает последние события задания и пути незавершённых конечных файлов.
- [PhotosOriginals.pause](#symbol-PhotosOriginals.pause) — Ставит корневую цепочку на паузу и при ручном вызове снимает запрос расписания.
- [PhotosOriginals.run](#symbol-PhotosOriginals.run) — Обновляет манифест, сохраняет недостающие ресурсы и обслуживает цепочку копий.
- [PhotosOriginals.run.asset_received](#symbol-PhotosOriginals.run.asset_received) — Сохраняет ресурсы поступившего объекта манифеста и восстанавливает готовность.
- [PhotosOriginals.start](#symbol-PhotosOriginals.start) — Запускает или продолжает корневую цепочку сохранения с учётом расписания.
- [PhotosOriginals.summary](#symbol-PhotosOriginals.summary) — Возвращает последнее состояние копии с незавершёнными файлами и расписанием.
- [encoded](#symbol-encoded) — Сериализует данные задания в стабильный JSON с сохранением Unicode.
- [safe_name](#symbol-safe_name) — Очищает имя ресурса от опасных символов и ограничивает длину в UTF-8.
- [same_file](#symbol-same_file) — Сравнивает размер, mtime, inode и device сохранённого файла.

## Константы и значения по умолчанию

<a id="constant-ACTIVE"></a>

### `ACTIVE`

`{'manifest', 'inventory', 'saving', 'pausing'}`

<a id="constant-COPY_BATCH_RESOURCES"></a>

### `COPY_BATCH_RESOURCES`

`256`

<a id="constant-SPACE_CHECK_SECONDS"></a>

### `SPACE_CHECK_SECONDS`

`5`

<a id="constant-SPACE_RESERVE_BYTES"></a>

### `SPACE_RESERVE_BYTES`

`64 * 1024 * 1024`

<a id="constant-WRITE_BUFFER_BYTES"></a>

### `WRITE_BUFFER_BYTES`

`64 * 1024 * 1024`


<a id="symbol-PhotosOriginals"></a>

## `PhotosOriginals`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals`

Сохраняет оригинальные ресурсы Photos и продолжает работу по квитанциям метаданных. Зависимости конструктора: libraries, adapter.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_inventories`, `_lock`, `_progress_at`, `_replicas`, `_source_id`, `_stop`, `_thread`, `_validate_at`, `_validation_link`, `adapter`, `catalog`, `libraries`, `schedule`, `storage`.

Именованные методы: `__init__`, `_restore_receipts`, `_db`, `_link`, `summary`, `journal`, `_update`, `_log`, `_volume`, `start`, `pause`, `close`, `_check`, `_stopped`, `_validate`, `_progress`, `_file`, `_inventory_record`, `_cleanup`, `_inventory`, `_receipt`, `_reuse_receipt`, `_stage`, `_create_original`, `_write`, `_peer`, `_stream_peer`, `_save`, `_counts`, `_prepare_replica`, `_replicate_all`, `run`.

<a id="symbol-PhotosOriginals.__init__"></a>

## `PhotosOriginals.__init__`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.__init__`

Инициализирует PhotosOriginals и его рабочее состояние. Изменяет SQLite-таблицы: photos_original_inventory, photos_original_jobs, photos_original_log, photos_original_resources, photos_original_staging и ещё 1.

```python
def __init__(self, libraries, adapter)
```

SQLite: чтение `photos_original_jobs`; запись/DDL `photos_original_inventory`, `photos_original_jobs`, `photos_original_log`, `photos_original_resources`, `photos_original_staging`, `photos_original_versions`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_inventories`, `_lock`, `_progress_at`, `_replicas`, `_source_id`, `_stop`, `_thread`, `_validate_at`, `_validation_link`, `adapter`, `catalog`, `libraries`, `schedule`, `storage`.

Прямые выражения вызова: `db.execute`, `db.executescript`, [encoded](media_manager--photos_originals.md#symbol-encoded), `json.loads`, `list`, `now`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._restore_receipts](media_manager--photos_originals.md#symbol-PhotosOriginals._restore_receipts), `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._check"></a>

## `PhotosOriginals._check`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._check`

Прерывает передачу при ручной остановке или закрытии разрешённого окна. Явно отклоняет недопустимое состояние через PhotosTransferStopped.

```python
def _check(self)
```

Прямые выражения вызова: `PhotosTransferStopped`, [self._stopped](media_manager--photos_originals.md#symbol-PhotosOriginals._stopped).

Явные `raise`:

- `PhotosTransferStopped('Сохранение приостановлено')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._cleanup"></a>

## `PhotosOriginals._cleanup`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._cleanup`

Удаляет подтверждённые старые временные файлы, сохраняя конечные незавершённые пути. Изменяет SQLite-таблицы: photos_original_staging.

```python
def _cleanup(self, job, link, volume)
```

SQLite: чтение `photos_original_jobs`, `photos_original_staging`; запись/DDL `photos_original_staging`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `OSError`, `PurePosixPath`, `data.get`, `db.execute`, `destination_directory`, `json.loads`, `list`, `object_id`, `os.stat`, `os.unlink`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), `stat.S_ISREG`, `str`.

Явные `raise`:

- `OSError('Промежуточный файл заменён; оставлен для ручной проверки: ' + str(path))`

Перехватываемые типы: `FileNotFoundError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._counts"></a>

## `PhotosOriginals._counts`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._counts`

Пересчитывает готовые объекты и ресурсы по состояниям манифеста. Читает SQLite-таблицы: photos_original_resources.

```python
def _counts(self, job)
```

SQLite: чтение `photos_original_resources`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT COUNT(*) total_assets,COALESCE(SUM(ready),0) done_assets FROM\n                (SELECT asset,MIN(state IN ('saved','reused')) ready FROM photos_original_resources WHERE job_id=? GROUP BY asset)", (job,)).fetchone`, `db.execute("SELECT COUNT(*) total_resources,\n                COALESCE(SUM(state IN ('saved','reused')),0) done_resources,\n                COALESCE(SUM(state='saved'),0) saved,COALESCE(SUM(state='reused'),0) reused,\n                COALESCE(SUM(state='error'),0) errors FROM photos_original_resources WHERE job_id=?", (job,)).fetchone`, `dict`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db).

Выражения возврата (ветви, без исполнения):

- `dict(row) &#124; dict(assets)`


<a id="symbol-PhotosOriginals._create_original"></a>

## `PhotosOriginals._create_original`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._create_original`

Исключительно создаёт свободное конечное имя и фиксирует намерение записи. Явно отклоняет недопустимое состояние через OSError.

```python
def _create_original(self, job, link, volume, parent, parent_path, name)
```

Прямые выражения вызова: `OSError`, `PurePosixPath`, `destination_directory`, `object_id`, `os.close`, `os.fstat`, `os.open`, `os.path.splitext`, `range`, [self._stage](media_manager--photos_originals.md#symbol-PhotosOriginals._stage), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), `str`.

Явные `raise`:

- `OSError('Целевая папка заменена')`
- `OSError('Не удалось выбрать свободное имя оригинала')`

Перехватываемые типы: `FileExistsError`, `BaseException`.

Выражения возврата (ветви, без исполнения):

- `(fd, path, identity)`


<a id="symbol-PhotosOriginals._db"></a>

## `PhotosOriginals._db`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._db`

Предоставляет транзакционное соединение каталога с гарантированным закрытием. Использует connection.close, self.catalog.connect.

```python
def _db(self)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `connection.close`, `self.catalog.connect`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-PhotosOriginals._file"></a>

## `PhotosOriginals._file`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._file`

Открывает готовый ресурс внутри папки копии только для чтения. Использует PurePosixPath, open_readonly.

```python
def _file(self, volume, link, path)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `PurePosixPath`, `open_readonly`, `str`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-PhotosOriginals._inventory"></a>

## `PhotosOriginals._inventory`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._inventory`

Индексирует имена и stat-параметры файлов копии без чтения содержимого. Изменяет SQLite-таблицы: photos_original_inventory.

```python
def _inventory(self, job, link, volume)
```

SQLite: чтение `photos_copy_files`, `photos_original_inventory`, `photos_original_jobs`, `photos_original_staging`; запись/DDL `photos_original_inventory`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `open_readonly`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), `set`, `uuid4`, `walk`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._inventory.walk"></a>

## `PhotosOriginals._inventory.walk`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._inventory.walk`

Рекурсивно перечисляет обычные файлы и папки копии через дескрипторы. Явно отклоняет недопустимое состояние через OSError.

```python
def walk(fd, prefix='')
```

Прямые выражения вызова: `OSError`, `PurePosixPath`, `entry.stat`, `fingerprint`, `inventory['names'].setdefault`, `inventory['names'].setdefault(name_key(name), []).append`, `name.startswith`, `name_key`, `os.close`, `os.fstat`, `os.open`, `os.scandir`, [self._inventory_record](media_manager--photos_originals.md#symbol-PhotosOriginals._inventory_record), [self._progress](media_manager--photos_originals.md#symbol-PhotosOriginals._progress), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), `stat.S_ISDIR`, `stat.S_ISREG`, `str`, [walk](media_manager--photos_originals.md#symbol-PhotosOriginals._inventory.walk).

Явные `raise`:

- `OSError('Переход на другой том запрещён')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._inventory_record"></a>

## `PhotosOriginals._inventory_record`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._inventory_record`

Сохраняет параметры и поколение обнаруженного файла назначения. Изменяет SQLite-таблицы: photos_original_inventory.

```python
def _inventory_record(self, link, path, fp, seen)
```

SQLite: чтение не найдено; запись/DDL `photos_original_inventory`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [encoded](media_manager--photos_originals.md#symbol-encoded), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._link"></a>

## `PhotosOriginals._link`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._link`

Проверяет существование, медиатеку и подключение привязанной копии. Явно отклоняет недопустимое состояние через KeyError, PhotosLibraryUnavailable.

```python
def _link(self, link_id, source_id=None)
```

SQLite: чтение `photos_copy_links`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `PhotosLibraryUnavailable`, `db.execute`, `db.execute('SELECT * FROM photos_copy_links WHERE id=?', (link_id,)).fetchone`, `dict`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db).

Явные `raise`:

- `KeyError('Копия медиатеки не найдена')`
- `PhotosLibraryUnavailable('Папка копии отвязана')`

Выражения возврата (ветви, без исполнения):

- `dict(row)`


<a id="symbol-PhotosOriginals._log"></a>

## `PhotosOriginals._log`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._log`

Добавляет событие оригиналов с уровнем, путём и временем. Изменяет SQLite-таблицы: photos_original_log.

```python
def _log(self, job, level, path, message)
```

SQLite: чтение не найдено; запись/DDL `photos_original_log`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `now`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._peer"></a>

## `PhotosOriginals._peer`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._peer`

Ищет квитанцию подходящего ресурса в разрешённой копии-источнике. Читает SQLite-таблицы: photos_copy_files, photos_copy_links, photos_original_versions.

```python
def _peer(self, link, item)
```

SQLite: чтение `photos_copy_files`, `photos_copy_links`, `photos_original_versions`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `list`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), `self.libraries.copy_source`.

Выражения возврата (ветви, без исполнения):

- `dict(rows[0]) if rows else None`


<a id="symbol-PhotosOriginals._prepare_replica"></a>

## `PhotosOriginals._prepare_replica`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._prepare_replica`

Подготавливает задание зависимой копии и сверяет её квитанции с манифестом. Изменяет SQLite-таблицы: photos_original_jobs, photos_original_resources.

```python
def _prepare_replica(self, parent_job, link)
```

SQLite: чтение `photos_copy_files`, `photos_original_resources`, `photos_original_versions`; запись/DDL `photos_original_jobs`, `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PhotosLibraryUnavailable`, `bool`, `db.execute`, `dict`, [encoded](media_manager--photos_originals.md#symbol-encoded), `inventory.get`, `json.loads`, `now`, `object_id`, `open_readonly`, `os.fstat`, `previous.get`, `receipts.get`, [same_file](media_manager--photos_originals.md#symbol-same_file), [self._cleanup](media_manager--photos_originals.md#symbol-PhotosOriginals._cleanup), [self._counts](media_manager--photos_originals.md#symbol-PhotosOriginals._counts), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._inventory](media_manager--photos_originals.md#symbol-PhotosOriginals._inventory), [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume), [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary), `uuid4`.

Явные `raise`:

- `PhotosLibraryUnavailable('Папка копии заменена: ' + link['path'])`

Выражения возврата (ветви, без исполнения):

- `(job, volume)`


<a id="symbol-PhotosOriginals._progress"></a>

## `PhotosOriginals._progress`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._progress`

Сохраняет промежуточный прогресс с ограничением частоты обновлений. Обновляет состояние объекта: _progress_at.

```python
def _progress(self, job, **values)
```

Присваивания полям `self`: `_progress_at`.

Прямые выражения вызова: [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), `time.monotonic`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._receipt"></a>

## `PhotosOriginals._receipt`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._receipt`

Фиксирует готовый ресурс, версию, параметры файла и завершение записи. Изменяет SQLite-таблицы: photos_copy_files, photos_original_resources, photos_original_staging, photos_original_versions.

```python
def _receipt(self, job, link, asset, resource, version, path, fp, reused)
```

SQLite: чтение `photos_original_staging`; запись/DDL `photos_copy_files`, `photos_original_resources`, `photos_original_staging`, `photos_original_versions`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [encoded](media_manager--photos_originals.md#symbol-encoded), `now`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), `self._inventories[link['id']]['recorded'].add`, [self._inventory_record](media_manager--photos_originals.md#symbol-PhotosOriginals._inventory_record), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._replicate_all"></a>

## `PhotosOriginals._replicate_all`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._replicate_all`

Дополняет зависимые копии готовыми ресурсами в порядке источников. Обрабатывает ошибки: (OSError, ValueError, PhotosAdapterError, KeyError), PhotosTransferStopped.

```python
def _replicate_all(self, master_job, master)
```

SQLite: чтение `photos_copy_files`, `photos_copy_links`, `photos_copy_sources`, `photos_original_resources`, `photos_original_versions`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `current.get`, `db.execute`, `dict`, `edges.get`, `json.loads`, `remaining.remove`, [self._check](media_manager--photos_originals.md#symbol-PhotosOriginals._check), [self._counts](media_manager--photos_originals.md#symbol-PhotosOriginals._counts), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._log](media_manager--photos_originals.md#symbol-PhotosOriginals._log), [self._prepare_replica](media_manager--photos_originals.md#symbol-PhotosOriginals._prepare_replica), [self._save](media_manager--photos_originals.md#symbol-PhotosOriginals._save), [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary), `self.summary(identifier, raw=True).get`, `set`, `sorted`, `str`.

Перехватываемые типы: `PhotosTransferStopped`, `(OSError, ValueError, PhotosAdapterError, KeyError)`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._restore_receipts"></a>

## `PhotosOriginals._restore_receipts`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._restore_receipts`

Восстанавливает готовность ресурсов по сохранённым версиям и квитанциям SQLite. Изменяет SQLite-таблицы: photos_original_resources.

```python
def _restore_receipts(self, job)
```

SQLite: чтение `photos_copy_files`, `photos_original_jobs`, `photos_original_versions`; запись/DDL `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._counts](media_manager--photos_originals.md#symbol-PhotosOriginals._counts), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._reuse_receipt"></a>

## `PhotosOriginals._reuse_receipt`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._reuse_receipt`

Принимает готовый ресурс повторно после проверки версии и параметров файла. Обрабатывает ошибки: FileNotFoundError.

```python
def _reuse_receipt(self, job, link, volume, asset, resource, version)
```

SQLite: чтение `photos_copy_files`, `photos_original_versions`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT f.*,v.version,v.fingerprint FROM photos_copy_files f JOIN photos_original_versions v\n                ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id\n                WHERE f.link_id=? AND f.asset_identifier=? AND f.resource_id=?', (link['id'], asset, resource)).fetchone`, `fingerprint`, `json.loads`, `os.fstat`, [same_file](media_manager--photos_originals.md#symbol-same_file), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._file](media_manager--photos_originals.md#symbol-PhotosOriginals._file), [self._receipt](media_manager--photos_originals.md#symbol-PhotosOriginals._receipt).

Перехватываемые типы: `FileNotFoundError`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-PhotosOriginals._save"></a>

## `PhotosOriginals._save`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._save`

Повторно использует ресурс либо сохраняет поток в новый конечный файл. Буфер ограничен 64 МиБ; после fsync проверяются размер и ID без чтения содержимого.

```python
def _save(self, job, link, volume, profile, item)
```

Прямые выражения вызова: `OSError`, `PhotosAdapterError`, `PhotosLibraryUnavailable`, `PurePosixPath`, `buffer.clear`, `bytearray`, `created.replace`, `datetime.fromisoformat`, `destination_directory`, `dict`, `fingerprint`, `flush`, `inventory['names'].get`, `item.get`, `len`, `name_key`, `object_id`, `os.close`, `os.fstat`, `os.fsync`, [safe_name](media_manager--photos_originals.md#symbol-safe_name), [same_file](media_manager--photos_originals.md#symbol-same_file), [self._check](media_manager--photos_originals.md#symbol-PhotosOriginals._check), [self._file](media_manager--photos_originals.md#symbol-PhotosOriginals._file), `self._inventories.get`, [self._peer](media_manager--photos_originals.md#symbol-PhotosOriginals._peer), [self._receipt](media_manager--photos_originals.md#symbol-PhotosOriginals._receipt), [self._reuse_receipt](media_manager--photos_originals.md#symbol-PhotosOriginals._reuse_receipt), [self._stream_peer](media_manager--photos_originals.md#symbol-PhotosOriginals._stream_peer), [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), `self.adapter.stream_original`, `self.libraries.copy_source`, `set`, `str`, `trailer.get`.

Явные `raise`:

- `PhotosLibraryUnavailable('Ожидаю готовый оригинал в копии-источнике')`
- `PhotosAdapterError('Размер переданного оригинала не совпал')`
- `OSError('Размер записанного оригинала не совпал')`
- `OSError('Записанный оригинал заменён или изменился')`

Перехватываемые типы: `ValueError`, `FileNotFoundError`.

Выражения возврата (ветви, без исполнения):

- `'reused'`
- `'saved'`


<a id="symbol-PhotosOriginals._save.flush"></a>

## `PhotosOriginals._save.flush`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._save.flush`

Проверяет свободное место и записывает накопленный буфер в конечный файл. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def flush()
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `buffer.clear`, `len`, `os.fstatvfs`, [self._create_original](media_manager--photos_originals.md#symbol-PhotosOriginals._create_original), [self._progress](media_manager--photos_originals.md#symbol-PhotosOriginals._progress), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), [self._write](media_manager--photos_originals.md#symbol-PhotosOriginals._write), `time.monotonic`.

Явные `raise`:

- `PhotosLibraryUnavailable('Недостаточно свободного места в папке копии. Освободи место и продолжи.')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotosOriginals._save.write"></a>

## `PhotosOriginals._save.write`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._save.write`

Разбивает принятые данные на ограниченный буфер и публикует прогресс. Использует buffer.extend, flush, memoryview, self._check, self._progress.

```python
def write(chunk)
```

Прямые выражения вызова: `buffer.extend`, [flush](media_manager--photos_originals.md#symbol-PhotosOriginals._save.flush), `len`, `memoryview`, `min`, [self._check](media_manager--photos_originals.md#symbol-PhotosOriginals._check), [self._progress](media_manager--photos_originals.md#symbol-PhotosOriginals._progress), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), `view.release`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._stage"></a>

## `PhotosOriginals._stage`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._stage`

Журналирует созданный путь и его идентичность до передачи содержимого. Изменяет SQLite-таблицы: photos_original_staging.

```python
def _stage(self, job, path, identity, final=False)
```

SQLite: чтение не найдено; запись/DDL `photos_original_staging`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, [encoded](media_manager--photos_originals.md#symbol-encoded), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._stopped"></a>

## `PhotosOriginals._stopped`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._stopped`

Проверяет ручной флаг остановки и временное окно медиатеки. Использует self._stop.is_set, self.schedule.blocked.

```python
def _stopped(self)
```

Прямые выражения вызова: `bool`, `self._stop.is_set`, `self.schedule.blocked`.

Выражения возврата (ветви, без исполнения):

- `self._stop.is_set() or bool(self.schedule and self._source_id is not None and self.schedule.blocked(self._source_id))`


<a id="symbol-PhotosOriginals._stream_peer"></a>

## `PhotosOriginals._stream_peer`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._stream_peer`

Передаёт готовый оригинал из другой копии с проверками источника. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _stream_peer(self, peer, write)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `check`, `dict`, `fingerprint`, `json.loads`, `len`, `os.fstat`, `os.read`, [same_file](media_manager--photos_originals.md#symbol-same_file), [self._file](media_manager--photos_originals.md#symbol-PhotosOriginals._file), [self._link](media_manager--photos_originals.md#symbol-PhotosOriginals._link), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume), [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary), `str`, `write`.

Явные `raise`:

- `PhotosLibraryUnavailable('Параметры сохранённого оригинала изменились: ' + peer['path'])`
- `PhotosLibraryUnavailable('Источник изменился во время копирования: ' + peer['path'])`
- `PhotosLibraryUnavailable('Сохранённый оригинал отсутствует в копии: ' + peer['path'])`
- `PhotosLibraryUnavailable('Не удалось передать оригинал из копии: ' + str(error))`

Перехватываемые типы: `FileNotFoundError`, `OSError`.

Выражения возврата (ветви, без исполнения):

- `dict(size=count)`


<a id="symbol-PhotosOriginals._stream_peer.check"></a>

## `PhotosOriginals._stream_peer.check`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._stream_peer.check`

Проверяет остановку, привязку, том и корень копии-источника между блоками. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def check()
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `any`, `current.get`, `job.get`, `object_id`, `open_readonly`, `os.fstat`, [self._check](media_manager--photos_originals.md#symbol-PhotosOriginals._check), [self._link](media_manager--photos_originals.md#symbol-PhotosOriginals._link), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume), `volume.get`.

Явные `raise`:

- `PhotosLibraryUnavailable('Источник копирования изменился')`
- `PhotosLibraryUnavailable('Том источника копирования изменился')`
- `PhotosLibraryUnavailable('Папка источника копирования заменена')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._update"></a>

## `PhotosOriginals._update`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._update`

Обновляет состояние и JSON-поля задания сохранения оригиналов. Изменяет SQLite-таблицы: photos_original_jobs.

```python
def _update(self, job, state=None, **values)
```

SQLite: чтение `photos_original_jobs`; запись/DDL `photos_original_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT state,data FROM photos_original_jobs WHERE id=?', (job,)).fetchone`, `dict`, [encoded](media_manager--photos_originals.md#symbol-encoded), `json.loads`, `now`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals._validate"></a>

## `PhotosOriginals._validate`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._validate`

Проверяет актуальность привязки, активность медиатеки, том и корневую папку. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _validate(self, job, link, volume, *, force=False)
```

Присваивания полям `self`: `_validate_at`, `_validation_link`.

Прямые выражения вызова: `PhotosLibraryUnavailable`, `any`, `current_volume.get`, `object_id`, `open_readonly`, `os.fstat`, [self._check](media_manager--photos_originals.md#symbol-PhotosOriginals._check), [self._link](media_manager--photos_originals.md#symbol-PhotosOriginals._link), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume), `self.libraries._require_active`, [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary), `time.monotonic`, `volume.get`.

Явные `raise`:

- `PhotosLibraryUnavailable('Привязка папки изменилась')`
- `PhotosLibraryUnavailable('Том копии изменился')`
- `PhotosLibraryUnavailable('Привязанная папка была заменена')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotosOriginals._volume"></a>

## `PhotosOriginals._volume`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._volume`

Возвращает доступный том копии из уже обнаруженного состояния. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _volume(self, link)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `next`, `self.storage.refresh`.

Явные `raise`:

- `PhotosLibraryUnavailable('Том копии отключён. Подключи его и продолжи сохранение.')`

Выражения возврата (ветви, без исполнения):

- `volume`


<a id="symbol-PhotosOriginals._write"></a>

## `PhotosOriginals._write`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals._write`

Полностью записывает блок через memoryview с проверкой остановки. Явно отклоняет недопустимое состояние через OSError.

```python
def _write(self, fd, chunk)
```

Прямые выражения вызова: `OSError`, `memoryview`, `os.write`, [self._check](media_manager--photos_originals.md#symbol-PhotosOriginals._check), `view.release`.

Явные `raise`:

- `OSError('Не удалось записать оригинал')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals.close"></a>

## `PhotosOriginals.close`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.close`

Запрашивает остановку воркера оригиналов при завершении Core. Использует self._stop.set, self._thread.join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals.journal"></a>

## `PhotosOriginals.journal`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.journal`

Возвращает последние события задания и пути незавершённых конечных файлов. Поля результата: job, items, incomplete_paths.

```python
def journal(self, link_id, source_id=None)
```

SQLite: чтение `photos_original_jobs`, `photos_original_log`, `photos_original_staging`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `job.get`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._link](media_manager--photos_originals.md#symbol-PhotosOriginals._link), [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary).

Выражения возврата (ветви, без исполнения):

- `dict(job=job, items=rows, incomplete_paths=incomplete)`


<a id="symbol-PhotosOriginals.pause"></a>

## `PhotosOriginals.pause`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.pause`

Ставит корневую цепочку на паузу и при ручном вызове снимает запрос расписания. Использует self._link, self._stop.set, self._update, self.libraries.root_copy, self.schedule.cancel.

```python
def pause(self, link_id, source_id=None, *, _scheduled=False)
```

Прямые выражения вызова: [self._link](media_manager--photos_originals.md#symbol-PhotosOriginals._link), `self._stop.set`, [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), `self.libraries.root_copy`, `self.schedule.cancel`, [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary).

Выражения возврата (ветви, без исполнения):

- `self.summary(link_id)`


<a id="symbol-PhotosOriginals.run"></a>

## `PhotosOriginals.run`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.run`

Обновляет манифест, сохраняет недостающие ресурсы и обслуживает цепочку копий. Изменяет SQLite-таблицы: photos_original_resources.

```python
def run(self, job, link)
```

SQLite: чтение `photos_copy_files`, `photos_copy_links`, `photos_original_jobs`, `photos_original_resources`, `photos_original_versions`; запись/DDL `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PhotosAdapterError`, `db.execute`, `db.execute("SELECT MIN(state IN ('saved','reused')) FROM photos_original_resources WHERE job_id=? AND asset=?", (job, item['asset'])).fetchone`, `dict`, `enumerate`, `item.get`, `json.loads`, [self._cleanup](media_manager--photos_originals.md#symbol-PhotosOriginals._cleanup), [self._counts](media_manager--photos_originals.md#symbol-PhotosOriginals._counts), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._inventory](media_manager--photos_originals.md#symbol-PhotosOriginals._inventory), [self._log](media_manager--photos_originals.md#symbol-PhotosOriginals._log), [self._replicate_all](media_manager--photos_originals.md#symbol-PhotosOriginals._replicate_all), [self._save](media_manager--photos_originals.md#symbol-PhotosOriginals._save), [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume), `self.adapter.close`, `self.adapter.original_manifest`, `self.libraries._require_active`, [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary), `self.summary(link['id']).get`, `str`, `uuid4`.

Явные `raise`:

- `PhotosAdapterError(item['error'])`

Перехватываемые типы: `(PhotosTransferStopped, PhotosLibraryUnavailable, PhotosAccessDenied)`, `(OSError, PhotosAdapterError, ValueError)`, `PhotosTransferStopped`, `(PhotosLibraryUnavailable, PhotosAccessDenied)`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals.run.asset_received"></a>

## `PhotosOriginals.run.asset_received`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.run.asset_received`

Сохраняет ресурсы поступившего объекта манифеста и восстанавливает готовность. Изменяет SQLite-таблицы: photos_original_resources.

```python
def asset_received(asset)
```

SQLite: чтение не найдено; запись/DDL `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `asset.get`, `bool`, `db.execute`, `dict`, [encoded](media_manager--photos_originals.md#symbol-encoded), `f'Обновляю список оригиналов Photos · {received:,}'.replace`, `item.get`, `json.loads`, `receipts.get`, [same_file](media_manager--photos_originals.md#symbol-same_file), [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), `self._inventories[link['id']]['files'].get`, [self._progress](media_manager--photos_originals.md#symbol-PhotosOriginals._progress), [self._validate](media_manager--photos_originals.md#symbol-PhotosOriginals._validate).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosOriginals.start"></a>

## `PhotosOriginals.start`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.start`

Запускает или продолжает корневую цепочку сохранения с учётом расписания. Изменяет SQLite-таблицы: photos_original_jobs.

```python
def start(self, link_id, source_id=None, *, background=True, _scheduled=False)
```

SQLite: чтение не найдено; запись/DDL `photos_original_jobs`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_inventories`, `_replicas`, `_source_id`, `_thread`, `_validate_at`.

Прямые выражения вызова: `PhotosLibraryUnavailable`, `ValueError`, `data.update`, `db.execute`, `dict`, [encoded](media_manager--photos_originals.md#symbol-encoded), `now`, `object_id`, `open_readonly`, `os.fstat`, `previous.get`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), [self._link](media_manager--photos_originals.md#symbol-PhotosOriginals._link), [self._log](media_manager--photos_originals.md#symbol-PhotosOriginals._log), [self._restore_receipts](media_manager--photos_originals.md#symbol-PhotosOriginals._restore_receipts), `self._stop.clear`, `self._thread.is_alive`, `self._thread.start`, [self._update](media_manager--photos_originals.md#symbol-PhotosOriginals._update), [self._volume](media_manager--photos_originals.md#symbol-PhotosOriginals._volume), `self.libraries._require_active`, `self.libraries.root_copy`, [self.run](media_manager--photos_originals.md#symbol-PhotosOriginals.run), `self.schedule.blocked`, `self.schedule.manages`, `self.schedule.request`, `self.schedule.settings`, [self.start](media_manager--photos_originals.md#symbol-PhotosOriginals.start), [self.summary](media_manager--photos_originals.md#symbol-PhotosOriginals.summary), `threading.Thread`, `uuid4`.

Явные `raise`:

- `ValueError('Сначала приостанови текущее сохранение оригиналов')`
- `PhotosLibraryUnavailable('Сохранение ожидает ночного окна')`
- `ValueError('Привязанная папка была заменена. Проверь привязку перед сохранением.')`

Выражения возврата (ветви, без исполнения):

- `self.start(root_id, source_id, background=background, _scheduled=_scheduled)`
- `self.schedule.request(link_id, source_id)`
- `self.summary(link_id)`


<a id="symbol-PhotosOriginals.summary"></a>

## `PhotosOriginals.summary`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `PhotosOriginals.summary`

Возвращает последнее состояние копии с незавершёнными файлами и расписанием. Читает SQLite-таблицы: photos_original_jobs, photos_original_staging.

```python
def summary(self, link_id, *, raw=False)
```

SQLite: чтение `photos_original_jobs`, `photos_original_staging`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT COUNT(*) FROM photos_original_staging s JOIN photos_original_jobs j ON j.id=s.job_id WHERE j.link_id=? AND json_extract(s.data,'$.final')=1", (link_id,)).fetchone`, `db.execute('SELECT * FROM photos_original_jobs WHERE link_id=? ORDER BY updated_at DESC LIMIT 1', (link_id,)).fetchone`, `dict`, `json.loads`, [self._db](media_manager--photos_originals.md#symbol-PhotosOriginals._db), `self.libraries.root_copy`, `self.schedule.decorate`.

Выражения возврата (ветви, без исполнения):

- `self.schedule.decorate(self.libraries.root_copy(link_id), result) if self.schedule and (not raw) else result`


<a id="symbol-encoded"></a>

## `encoded`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `encoded`

Сериализует данные задания в стабильный JSON с сохранением Unicode. Использует json.dumps.

```python
def encoded(value)
```

Прямые выражения вызова: `json.dumps`.

Выражения возврата (ветви, без исполнения):

- `json.dumps(value, ensure_ascii=False, sort_keys=True)`


<a id="symbol-safe_name"></a>

## `safe_name`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `safe_name`

Очищает имя ресурса от опасных символов и ограничивает длину в UTF-8. Использует (stem + ext).encode, os.path.splitext, re.sub, re.sub('[\\x00-\\x1f/\\\\:]', '_', str(value)).strip.

```python
def safe_name(value)
```

Прямые выражения вызова: `(stem + ext).encode`, `len`, `os.path.splitext`, `re.sub`, `re.sub('[\\x00-\\x1f/\\\\:]', '_', str(value)).strip`, `str`.

Выражения возврата (ветви, без исполнения):

- `stem + ext or 'original'`


<a id="symbol-same_file"></a>

## `same_file`

[media_manager/photos_originals.py](../../media_manager/photos_originals.py) · `same_file`

Сравнивает размер, mtime, inode и device сохранённого файла. ctime исключён: SMB может уточнять его после успешного завершения записи.

```python
def same_file(left, right)
```

Прямые выражения вызова: `all`, `left.get`, `right.get`.

Выражения возврата (ветви, без исполнения):

- `all((left.get(key) == right.get(key) for key in ('size', 'mtime_ns', 'inode', 'device')))`
