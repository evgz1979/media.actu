# Сохранение оригиналов Photos: `media_manager/photos_originals.py`

Один координатор оригиналов: манифест PhotoKit, параметры файлов назначения, квитанции ресурсов, ограниченный буфер памяти, запись новых конечных файлов и зависимые копии.

[Исходный модуль](../../media_manager/photos_originals.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_photos_copy_chain.py](../../tests/test_photos_copy_chain.py#L6), [tests/test_photos_originals.py](../../tests/test_photos_originals.py#L11), [tests/test_photos_schedule.py](../../tests/test_photos_schedule.py#L9).

## Оглавление определений

- [encoded](#symbol-encoded) — Сериализует данные задания в стабильный JSON с сохранением Unicode.
- [same_file](#symbol-same-file) — Сравнивает размер, mtime, inode и device сохранённого файла.
- [safe_name](#symbol-safe-name) — Очищает имя ресурса от опасных символов и ограничивает длину в UTF-8.
- [PhotosOriginals](#symbol-photosoriginals) — Сохраняет оригинальные ресурсы Photos и продолжает работу по квитанциям метаданных.
- [PhotosOriginals.__init__](#symbol-photosoriginals---init--) — Инициализирует PhotosOriginals и его рабочее состояние.
- [PhotosOriginals._restore_receipts](#symbol-photosoriginals--restore-receipts) — Восстанавливает готовность ресурсов по сохранённым версиям и квитанциям SQLite.
- [PhotosOriginals._db](#symbol-photosoriginals--db) — Предоставляет транзакционное соединение каталога с гарантированным закрытием.
- [PhotosOriginals._link](#symbol-photosoriginals--link) — Проверяет существование, медиатеку и подключение привязанной копии.
- [PhotosOriginals.summary](#symbol-photosoriginals-summary) — Возвращает последнее состояние копии с незавершёнными файлами и расписанием.
- [PhotosOriginals.journal](#symbol-photosoriginals-journal) — Возвращает последние события задания и пути незавершённых конечных файлов.
- [PhotosOriginals._update](#symbol-photosoriginals--update) — Обновляет состояние и JSON-поля задания сохранения оригиналов.
- [PhotosOriginals._log](#symbol-photosoriginals--log) — Добавляет событие оригиналов с уровнем, путём и временем.
- [PhotosOriginals._volume](#symbol-photosoriginals--volume) — Возвращает доступный том копии из уже обнаруженного состояния.
- [PhotosOriginals.start](#symbol-photosoriginals-start) — Запускает или продолжает корневую цепочку сохранения с учётом расписания.
- [PhotosOriginals.pause](#symbol-photosoriginals-pause) — Ставит корневую цепочку на паузу и при ручном вызове снимает запрос расписания.
- [PhotosOriginals.close](#symbol-photosoriginals-close) — Запрашивает остановку воркера оригиналов при завершении Core.
- [PhotosOriginals._check](#symbol-photosoriginals--check) — Прерывает передачу при ручной остановке или закрытии разрешённого окна.
- [PhotosOriginals._stopped](#symbol-photosoriginals--stopped) — Проверяет ручной флаг остановки и временное окно медиатеки.
- [PhotosOriginals._validate](#symbol-photosoriginals--validate) — Проверяет актуальность привязки, активность медиатеки, том и корневую папку.
- [PhotosOriginals._progress](#symbol-photosoriginals--progress) — Сохраняет промежуточный прогресс с ограничением частоты обновлений.
- [PhotosOriginals._file](#symbol-photosoriginals--file) — Открывает готовый ресурс внутри папки копии только для чтения.
- [PhotosOriginals._inventory_record](#symbol-photosoriginals--inventory-record) — Сохраняет параметры и поколение обнаруженного файла назначения.
- [PhotosOriginals._cleanup](#symbol-photosoriginals--cleanup) — Удаляет подтверждённые старые временные файлы, сохраняя конечные незавершённые пути.
- [PhotosOriginals._inventory](#symbol-photosoriginals--inventory) — Индексирует имена и stat-параметры файлов копии без чтения содержимого.
- [PhotosOriginals._inventory.walk](#symbol-photosoriginals--inventory-walk) — Рекурсивно перечисляет обычные файлы и папки копии через дескрипторы.
- [PhotosOriginals._receipt](#symbol-photosoriginals--receipt) — Фиксирует готовый ресурс, версию, параметры файла и завершение записи.
- [PhotosOriginals._reuse_receipt](#symbol-photosoriginals--reuse-receipt) — Принимает готовый ресурс повторно после проверки версии и параметров файла.
- [PhotosOriginals._stage](#symbol-photosoriginals--stage) — Журналирует созданный путь и его идентичность до передачи содержимого.
- [PhotosOriginals._create_original](#symbol-photosoriginals--create-original) — Исключительно создаёт свободное конечное имя и фиксирует намерение записи.
- [PhotosOriginals._write](#symbol-photosoriginals--write) — Полностью записывает блок через memoryview с проверкой остановки.
- [PhotosOriginals._peer](#symbol-photosoriginals--peer) — Ищет квитанцию подходящего ресурса в разрешённой копии-источнике.
- [PhotosOriginals._stream_peer](#symbol-photosoriginals--stream-peer) — Передаёт готовый оригинал из другой копии с проверками источника.
- [PhotosOriginals._stream_peer.check](#symbol-photosoriginals--stream-peer-check) — Проверяет остановку, привязку, том и корень копии-источника между блоками.
- [PhotosOriginals._save](#symbol-photosoriginals--save) — Повторно использует ресурс либо сохраняет поток в новый конечный файл.
- [PhotosOriginals._save.flush](#symbol-photosoriginals--save-flush) — Проверяет свободное место и записывает накопленный буфер в конечный файл.
- [PhotosOriginals._save.write](#symbol-photosoriginals--save-write) — Разбивает принятые данные на ограниченный буфер и публикует прогресс.
- [PhotosOriginals._counts](#symbol-photosoriginals--counts) — Пересчитывает готовые объекты и ресурсы по состояниям манифеста.
- [PhotosOriginals._prepare_replica](#symbol-photosoriginals--prepare-replica) — Подготавливает задание зависимой копии и сверяет её квитанции с манифестом.
- [PhotosOriginals._replicate_all](#symbol-photosoriginals--replicate-all) — Дополняет зависимые копии готовыми ресурсами в порядке источников.
- [PhotosOriginals.run](#symbol-photosoriginals-run) — Обновляет манифест, сохраняет недостающие ресурсы и обслуживает цепочку копий.
- [PhotosOriginals.run.asset_received](#symbol-photosoriginals-run-asset-received) — Сохраняет ресурсы поступившего объекта манифеста и восстанавливает готовность.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [ACTIVE](../../media_manager/photos_originals.py#L24) | `{'manifest', 'inventory', 'saving', 'pausing'}` |
| [WRITE_BUFFER_BYTES](../../media_manager/photos_originals.py#L25) | `64 * 1024 * 1024` |
| [SPACE_CHECK_SECONDS](../../media_manager/photos_originals.py#L26) | `5` |
| [SPACE_RESERVE_BYTES](../../media_manager/photos_originals.py#L27) | `64 * 1024 * 1024` |
| [COPY_BATCH_RESOURCES](../../media_manager/photos_originals.py#L28) | `256` |

<a id="symbol-encoded"></a>

## `encoded`

[media_manager/photos_originals.py:33](../../media_manager/photos_originals.py#L33)

Сериализует данные задания в стабильный JSON с сохранением Unicode. Использует json.dumps.

```python
def encoded(value)
```

Прямые выражения вызова: `json.dumps`.

Выражения возврата (ветви, без исполнения):

- `json.dumps(value, ensure_ascii=False, sort_keys=True)`


<a id="symbol-same-file"></a>

## `same_file`

[media_manager/photos_originals.py:39](../../media_manager/photos_originals.py#L39)

Сравнивает размер, mtime, inode и device сохранённого файла. ctime исключён: SMB может уточнять его после успешного завершения записи.

```python
def same_file(left, right)
```

Прямые выражения вызова: `all`, `left.get`, `right.get`.

Выражения возврата (ветви, без исполнения):

- `all((left.get(key) == right.get(key) for key in ('size', 'mtime_ns', 'inode', 'device')))`


<a id="symbol-safe-name"></a>

## `safe_name`

[media_manager/photos_originals.py:46](../../media_manager/photos_originals.py#L46)

Очищает имя ресурса от опасных символов и ограничивает длину в UTF-8. Использует (stem + ext).encode, os.path.splitext, re.sub, re.sub('[\\x00-\\x1f/\\\\:]', '_', str(value)).strip.

```python
def safe_name(value)
```

Прямые выражения вызова: `(stem + ext).encode`, `len`, `os.path.splitext`, `re.sub`, `re.sub('[\\x00-\\x1f/\\\\:]', '_', str(value)).strip`, `str`.

Выражения возврата (ветви, без исполнения):

- `stem + ext or 'original'`


<a id="symbol-photosoriginals"></a>

## `PhotosOriginals`

[media_manager/photos_originals.py:59](../../media_manager/photos_originals.py#L59)

Сохраняет оригинальные ресурсы Photos и продолжает работу по квитанциям метаданных. Зависимости конструктора: libraries, adapter.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_inventories`, `_lock`, `_progress_at`, `_replicas`, `_source_id`, `_stop`, `_thread`, `_validate_at`, `_validation_link`, `adapter`, `catalog`, `libraries`, `schedule`, `storage`.

Именованные методы: `__init__`, `_restore_receipts`, `_db`, `_link`, `summary`, `journal`, `_update`, `_log`, `_volume`, `start`, `pause`, `close`, `_check`, `_stopped`, `_validate`, `_progress`, `_file`, `_inventory_record`, `_cleanup`, `_inventory`, `_receipt`, `_reuse_receipt`, `_stage`, `_create_original`, `_write`, `_peer`, `_stream_peer`, `_save`, `_counts`, `_prepare_replica`, `_replicate_all`, `run`.

<a id="symbol-photosoriginals---init--"></a>

## `PhotosOriginals.__init__`

[media_manager/photos_originals.py:62](../../media_manager/photos_originals.py#L62)

Инициализирует PhotosOriginals и его рабочее состояние. Изменяет SQLite-таблицы: photos_original_inventory, photos_original_jobs, photos_original_log, photos_original_resources, photos_original_staging и ещё 1.

```python
def __init__(self, libraries, adapter)
```

SQLite: чтение `photos_original_jobs`; запись/DDL `photos_original_inventory`, `photos_original_jobs`, `photos_original_log`, `photos_original_resources`, `photos_original_staging`, `photos_original_versions`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_inventories`, `_lock`, `_progress_at`, `_replicas`, `_source_id`, `_stop`, `_thread`, `_validate_at`, `_validation_link`, `adapter`, `catalog`, `libraries`, `schedule`, `storage`.

Прямые выражения вызова: `db.execute`, `db.executescript`, [encoded](../../media_manager/photos_originals.py#L33), `json.loads`, `list`, `now`, [self._db](../../media_manager/photos_originals.py#L133), [self._restore_receipts](../../media_manager/photos_originals.py#L119), `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--restore-receipts"></a>

## `PhotosOriginals._restore_receipts`

[media_manager/photos_originals.py:119](../../media_manager/photos_originals.py#L119)

Восстанавливает готовность ресурсов по сохранённым версиям и квитанциям SQLite. Изменяет SQLite-таблицы: photos_original_resources.

```python
def _restore_receipts(self, job)
```

SQLite: чтение `photos_copy_files`, `photos_original_jobs`, `photos_original_versions`; запись/DDL `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._counts](../../media_manager/photos_originals.py#L641), [self._db](../../media_manager/photos_originals.py#L133), [self._update](../../media_manager/photos_originals.py#L177).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--db"></a>

## `PhotosOriginals._db`

[media_manager/photos_originals.py:133](../../media_manager/photos_originals.py#L133)

Предоставляет транзакционное соединение каталога с гарантированным закрытием. Использует connection.close, self.catalog.connect.

```python
def _db(self)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `connection.close`, `self.catalog.connect`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-photosoriginals--link"></a>

## `PhotosOriginals._link`

[media_manager/photos_originals.py:143](../../media_manager/photos_originals.py#L143)

Проверяет существование, медиатеку и подключение привязанной копии. Явно отклоняет недопустимое состояние через KeyError, PhotosLibraryUnavailable.

```python
def _link(self, link_id, source_id=None)
```

SQLite: чтение `photos_copy_links`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `PhotosLibraryUnavailable`, `db.execute`, `db.execute('SELECT * FROM photos_copy_links WHERE id=?', (link_id,)).fetchone`, `dict`, [self._db](../../media_manager/photos_originals.py#L133).

Явные `raise`:

- `KeyError('Копия медиатеки не найдена')`
- `PhotosLibraryUnavailable('Папка копии отвязана')`

Выражения возврата (ветви, без исполнения):

- `dict(row)`


<a id="symbol-photosoriginals-summary"></a>

## `PhotosOriginals.summary`

[media_manager/photos_originals.py:154](../../media_manager/photos_originals.py#L154)

Возвращает последнее состояние копии с незавершёнными файлами и расписанием. Читает SQLite-таблицы: photos_original_jobs, photos_original_staging.

```python
def summary(self, link_id, *, raw=False)
```

SQLite: чтение `photos_original_jobs`, `photos_original_staging`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT COUNT(*) FROM photos_original_staging s JOIN photos_original_jobs j ON j.id=s.job_id WHERE j.link_id=? AND json_extract(s.data,'$.final')=1", (link_id,)).fetchone`, `db.execute('SELECT * FROM photos_original_jobs WHERE link_id=? ORDER BY updated_at DESC LIMIT 1', (link_id,)).fetchone`, `dict`, `json.loads`, [self._db](../../media_manager/photos_originals.py#L133), `self.libraries.root_copy`, `self.schedule.decorate`.

Выражения возврата (ветви, без исполнения):

- `self.schedule.decorate(self.libraries.root_copy(link_id), result) if self.schedule and (not raw) else result`


<a id="symbol-photosoriginals-journal"></a>

## `PhotosOriginals.journal`

[media_manager/photos_originals.py:167](../../media_manager/photos_originals.py#L167)

Возвращает последние события задания и пути незавершённых конечных файлов. Поля результата: job, items, incomplete_paths.

```python
def journal(self, link_id, source_id=None)
```

SQLite: чтение `photos_original_jobs`, `photos_original_log`, `photos_original_staging`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `job.get`, [self._db](../../media_manager/photos_originals.py#L133), [self._link](../../media_manager/photos_originals.py#L143), [self.summary](../../media_manager/photos_originals.py#L154).

Выражения возврата (ветви, без исполнения):

- `dict(job=job, items=rows, incomplete_paths=incomplete)`


<a id="symbol-photosoriginals--update"></a>

## `PhotosOriginals._update`

[media_manager/photos_originals.py:177](../../media_manager/photos_originals.py#L177)

Обновляет состояние и JSON-поля задания сохранения оригиналов. Изменяет SQLite-таблицы: photos_original_jobs.

```python
def _update(self, job, state=None, **values)
```

SQLite: чтение `photos_original_jobs`; запись/DDL `photos_original_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT state,data FROM photos_original_jobs WHERE id=?', (job,)).fetchone`, `dict`, [encoded](../../media_manager/photos_originals.py#L33), `json.loads`, `now`, [self._db](../../media_manager/photos_originals.py#L133).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--log"></a>

## `PhotosOriginals._log`

[media_manager/photos_originals.py:185](../../media_manager/photos_originals.py#L185)

Добавляет событие оригиналов с уровнем, путём и временем. Изменяет SQLite-таблицы: photos_original_log.

```python
def _log(self, job, level, path, message)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_original_log`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `now`, [self._db](../../media_manager/photos_originals.py#L133).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--volume"></a>

## `PhotosOriginals._volume`

[media_manager/photos_originals.py:191](../../media_manager/photos_originals.py#L191)

Возвращает доступный том копии из уже обнаруженного состояния. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _volume(self, link)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `next`, `self.storage.refresh`.

Явные `raise`:

- `PhotosLibraryUnavailable('Том копии отключён. Подключи его и продолжи сохранение.')`

Выражения возврата (ветви, без исполнения):

- `volume`


<a id="symbol-photosoriginals-start"></a>

## `PhotosOriginals.start`

[media_manager/photos_originals.py:199](../../media_manager/photos_originals.py#L199)

Запускает или продолжает корневую цепочку сохранения с учётом расписания. Изменяет SQLite-таблицы: photos_original_jobs.

```python
def start(self, link_id, source_id=None, *, background=True, _scheduled=False)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_original_jobs`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_inventories`, `_replicas`, `_source_id`, `_thread`, `_validate_at`.

Прямые выражения вызова: `PhotosLibraryUnavailable`, `ValueError`, `data.update`, `db.execute`, `dict`, [encoded](../../media_manager/photos_originals.py#L33), `now`, `object_id`, `open_readonly`, `os.fstat`, `previous.get`, [self._db](../../media_manager/photos_originals.py#L133), [self._link](../../media_manager/photos_originals.py#L143), [self._log](../../media_manager/photos_originals.py#L185), [self._restore_receipts](../../media_manager/photos_originals.py#L119), `self._stop.clear`, `self._thread.is_alive`, `self._thread.start`, [self._update](../../media_manager/photos_originals.py#L177), [self._volume](../../media_manager/photos_originals.py#L191), `self.libraries._require_active`, `self.libraries.root_copy`, [self.run](../../media_manager/photos_originals.py#L744), `self.schedule.blocked`, `self.schedule.manages`, `self.schedule.request`, `self.schedule.settings`, [self.start](../../media_manager/photos_originals.py#L199), [self.summary](../../media_manager/photos_originals.py#L154), `threading.Thread`, `uuid4`.

Явные `raise`:

- `ValueError('Сначала приостанови текущее сохранение оригиналов')`
- `PhotosLibraryUnavailable('Сохранение ожидает ночного окна')`
- `ValueError('Привязанная папка была заменена. Проверь привязку перед сохранением.')`

Выражения возврата (ветви, без исполнения):

- `self.start(root_id, source_id, background=background, _scheduled=_scheduled)`
- `self.schedule.request(link_id, source_id)`
- `self.summary(link_id)`


<a id="symbol-photosoriginals-pause"></a>

## `PhotosOriginals.pause`

[media_manager/photos_originals.py:249](../../media_manager/photos_originals.py#L249)

Ставит корневую цепочку на паузу и при ручном вызове снимает запрос расписания. Использует self._link, self._stop.set, self._update, self.libraries.root_copy, self.schedule.cancel.

```python
def pause(self, link_id, source_id=None, *, _scheduled=False)
```

Прямые выражения вызова: [self._link](../../media_manager/photos_originals.py#L143), `self._stop.set`, [self._update](../../media_manager/photos_originals.py#L177), `self.libraries.root_copy`, `self.schedule.cancel`, [self.summary](../../media_manager/photos_originals.py#L154).

Выражения возврата (ветви, без исполнения):

- `self.summary(link_id)`


<a id="symbol-photosoriginals-close"></a>

## `PhotosOriginals.close`

[media_manager/photos_originals.py:263](../../media_manager/photos_originals.py#L263)

Запрашивает остановку воркера оригиналов при завершении Core. Использует self._stop.set, self._thread.join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--check"></a>

## `PhotosOriginals._check`

[media_manager/photos_originals.py:272](../../media_manager/photos_originals.py#L272)

Прерывает передачу при ручной остановке или закрытии разрешённого окна. Явно отклоняет недопустимое состояние через PhotosTransferStopped.

```python
def _check(self)
```

Прямые выражения вызова: `PhotosTransferStopped`, [self._stopped](../../media_manager/photos_originals.py#L278).

Явные `raise`:

- `PhotosTransferStopped('Сохранение приостановлено')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--stopped"></a>

## `PhotosOriginals._stopped`

[media_manager/photos_originals.py:278](../../media_manager/photos_originals.py#L278)

Проверяет ручной флаг остановки и временное окно медиатеки. Использует self._stop.is_set, self.schedule.blocked.

```python
def _stopped(self)
```

Прямые выражения вызова: `bool`, `self._stop.is_set`, `self.schedule.blocked`.

Выражения возврата (ветви, без исполнения):

- `self._stop.is_set() or bool(self.schedule and self._source_id is not None and self.schedule.blocked(self._source_id))`


<a id="symbol-photosoriginals--validate"></a>

## `PhotosOriginals._validate`

[media_manager/photos_originals.py:284](../../media_manager/photos_originals.py#L284)

Проверяет актуальность привязки, активность медиатеки, том и корневую папку. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _validate(self, job, link, volume, *, force=False)
```

Присваивания полям `self`: `_validate_at`, `_validation_link`.

Прямые выражения вызова: `PhotosLibraryUnavailable`, `any`, `current_volume.get`, `object_id`, `open_readonly`, `os.fstat`, [self._check](../../media_manager/photos_originals.py#L272), [self._link](../../media_manager/photos_originals.py#L143), [self._volume](../../media_manager/photos_originals.py#L191), `self.libraries._require_active`, [self.summary](../../media_manager/photos_originals.py#L154), `time.monotonic`, `volume.get`.

Явные `raise`:

- `PhotosLibraryUnavailable('Привязка папки изменилась')`
- `PhotosLibraryUnavailable('Том копии изменился')`
- `PhotosLibraryUnavailable('Привязанная папка была заменена')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photosoriginals--progress"></a>

## `PhotosOriginals._progress`

[media_manager/photos_originals.py:303](../../media_manager/photos_originals.py#L303)

Сохраняет промежуточный прогресс с ограничением частоты обновлений. Обновляет состояние объекта: _progress_at.

```python
def _progress(self, job, **values)
```

Присваивания полям `self`: `_progress_at`.

Прямые выражения вызова: [self._update](../../media_manager/photos_originals.py#L177), `time.monotonic`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--file"></a>

## `PhotosOriginals._file`

[media_manager/photos_originals.py:311](../../media_manager/photos_originals.py#L311)

Открывает готовый ресурс внутри папки копии только для чтения. Использует PurePosixPath, open_readonly.

```python
def _file(self, volume, link, path)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `PurePosixPath`, `open_readonly`, `str`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-photosoriginals--inventory-record"></a>

## `PhotosOriginals._inventory_record`

[media_manager/photos_originals.py:317](../../media_manager/photos_originals.py#L317)

Сохраняет параметры и поколение обнаруженного файла назначения. Изменяет SQLite-таблицы: photos_original_inventory.

```python
def _inventory_record(self, link, path, fp, seen)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_original_inventory`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [encoded](../../media_manager/photos_originals.py#L33), [self._db](../../media_manager/photos_originals.py#L133).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--cleanup"></a>

## `PhotosOriginals._cleanup`

[media_manager/photos_originals.py:324](../../media_manager/photos_originals.py#L324)

Удаляет подтверждённые старые временные файлы, сохраняя конечные незавершённые пути. Изменяет SQLite-таблицы: photos_original_staging.

```python
def _cleanup(self, job, link, volume)
```

SQLite: чтение `photos_original_jobs`, `photos_original_staging`; запись/DDL `photos_original_staging`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `OSError`, `PurePosixPath`, `data.get`, `db.execute`, `destination_directory`, `json.loads`, `list`, `object_id`, `os.stat`, `os.unlink`, [self._db](../../media_manager/photos_originals.py#L133), [self._validate](../../media_manager/photos_originals.py#L284), `stat.S_ISREG`, `str`.

Явные `raise`:

- `OSError('Промежуточный файл заменён; оставлен для ручной проверки: ' + str(path))`

Перехватываемые типы: `FileNotFoundError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--inventory"></a>

## `PhotosOriginals._inventory`

[media_manager/photos_originals.py:346](../../media_manager/photos_originals.py#L346)

Индексирует имена и stat-параметры файлов копии без чтения содержимого. Изменяет SQLite-таблицы: photos_original_inventory.

```python
def _inventory(self, job, link, volume)
```

SQLite: чтение `photos_copy_files`, `photos_original_inventory`, `photos_original_jobs`, `photos_original_staging`; запись/DDL `photos_original_inventory`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `open_readonly`, [self._db](../../media_manager/photos_originals.py#L133), [self._update](../../media_manager/photos_originals.py#L177), `set`, `uuid4`, `walk`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--inventory-walk"></a>

## `PhotosOriginals._inventory.walk`

[media_manager/photos_originals.py:357](../../media_manager/photos_originals.py#L357)

Рекурсивно перечисляет обычные файлы и папки копии через дескрипторы. Явно отклоняет недопустимое состояние через OSError.

```python
def walk(fd, prefix='')
```

Прямые выражения вызова: `OSError`, `PurePosixPath`, `entry.stat`, `fingerprint`, `inventory['names'].setdefault`, `inventory['names'].setdefault(name_key(name), []).append`, `name.startswith`, `name_key`, `os.close`, `os.fstat`, `os.open`, `os.scandir`, [self._inventory_record](../../media_manager/photos_originals.py#L317), [self._progress](../../media_manager/photos_originals.py#L303), [self._validate](../../media_manager/photos_originals.py#L284), `stat.S_ISDIR`, `stat.S_ISREG`, `str`, [walk](../../media_manager/photos_originals.py#L357).

Явные `raise`:

- `OSError('Переход на другой том запрещён')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--receipt"></a>

## `PhotosOriginals._receipt`

[media_manager/photos_originals.py:394](../../media_manager/photos_originals.py#L394)

Фиксирует готовый ресурс, версию, параметры файла и завершение записи. Изменяет SQLite-таблицы: photos_copy_files, photos_original_resources, photos_original_staging, photos_original_versions.

```python
def _receipt(self, job, link, asset, resource, version, path, fp, reused)
```

SQLite: чтение `photos_original_staging`; запись/DDL `photos_copy_files`, `photos_original_resources`, `photos_original_staging`, `photos_original_versions`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [encoded](../../media_manager/photos_originals.py#L33), `now`, [self._db](../../media_manager/photos_originals.py#L133), `self._inventories[link['id']]['recorded'].add`, [self._inventory_record](../../media_manager/photos_originals.py#L317), [self._validate](../../media_manager/photos_originals.py#L284), [self._volume](../../media_manager/photos_originals.py#L191).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--reuse-receipt"></a>

## `PhotosOriginals._reuse_receipt`

[media_manager/photos_originals.py:407](../../media_manager/photos_originals.py#L407)

Принимает готовый ресурс повторно после проверки версии и параметров файла. Обрабатывает ошибки: FileNotFoundError.

```python
def _reuse_receipt(self, job, link, volume, asset, resource, version)
```

SQLite: чтение `photos_copy_files`, `photos_original_versions`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT f.*,v.version,v.fingerprint FROM photos_copy_files f JOIN photos_original_versions v\n                ON v.link_id=f.link_id AND v.asset=f.asset_identifier AND v.resource=f.resource_id\n                WHERE f.link_id=? AND f.asset_identifier=? AND f.resource_id=?', (link['id'], asset, resource)).fetchone`, `fingerprint`, `json.loads`, `os.fstat`, [same_file](../../media_manager/photos_originals.py#L39), [self._db](../../media_manager/photos_originals.py#L133), [self._file](../../media_manager/photos_originals.py#L311), [self._receipt](../../media_manager/photos_originals.py#L394).

Перехватываемые типы: `FileNotFoundError`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-photosoriginals--stage"></a>

## `PhotosOriginals._stage`

[media_manager/photos_originals.py:426](../../media_manager/photos_originals.py#L426)

Журналирует созданный путь и его идентичность до передачи содержимого. Изменяет SQLite-таблицы: photos_original_staging.

```python
def _stage(self, job, path, identity, final=False)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_original_staging`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, [encoded](../../media_manager/photos_originals.py#L33), [self._db](../../media_manager/photos_originals.py#L133).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--create-original"></a>

## `PhotosOriginals._create_original`

[media_manager/photos_originals.py:432](../../media_manager/photos_originals.py#L432)

Исключительно создаёт свободное конечное имя и фиксирует намерение записи. Явно отклоняет недопустимое состояние через OSError.

```python
def _create_original(self, job, link, volume, parent, parent_path, name)
```

Прямые выражения вызова: `OSError`, `PurePosixPath`, `destination_directory`, `object_id`, `os.close`, `os.fstat`, `os.open`, `os.path.splitext`, `range`, [self._stage](../../media_manager/photos_originals.py#L426), [self._validate](../../media_manager/photos_originals.py#L284), `str`.

Явные `raise`:

- `OSError('Целевая папка заменена')`
- `OSError('Не удалось выбрать свободное имя оригинала')`

Перехватываемые типы: `FileExistsError`, `BaseException`.

Выражения возврата (ветви, без исполнения):

- `(fd, path, identity)`


<a id="symbol-photosoriginals--write"></a>

## `PhotosOriginals._write`

[media_manager/photos_originals.py:457](../../media_manager/photos_originals.py#L457)

Полностью записывает блок через memoryview с проверкой остановки. Явно отклоняет недопустимое состояние через OSError.

```python
def _write(self, fd, chunk)
```

Прямые выражения вызова: `OSError`, `memoryview`, `os.write`, [self._check](../../media_manager/photos_originals.py#L272), `view.release`.

Явные `raise`:

- `OSError('Не удалось записать оригинал')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--peer"></a>

## `PhotosOriginals._peer`

[media_manager/photos_originals.py:473](../../media_manager/photos_originals.py#L473)

Ищет квитанцию подходящего ресурса в разрешённой копии-источнике. Читает SQLite-таблицы: photos_copy_files, photos_copy_links, photos_original_versions.

```python
def _peer(self, link, item)
```

SQLite: чтение `photos_copy_files`, `photos_copy_links`, `photos_original_versions`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `list`, [self._db](../../media_manager/photos_originals.py#L133), `self.libraries.copy_source`.

Выражения возврата (ветви, без исполнения):

- `dict(rows[0]) if rows else None`


<a id="symbol-photosoriginals--stream-peer"></a>

## `PhotosOriginals._stream_peer`

[media_manager/photos_originals.py:486](../../media_manager/photos_originals.py#L486)

Передаёт готовый оригинал из другой копии с проверками источника. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _stream_peer(self, peer, write)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `check`, `dict`, `fingerprint`, `json.loads`, `len`, `os.fstat`, `os.read`, [same_file](../../media_manager/photos_originals.py#L39), [self._file](../../media_manager/photos_originals.py#L311), [self._link](../../media_manager/photos_originals.py#L143), [self._volume](../../media_manager/photos_originals.py#L191), [self.summary](../../media_manager/photos_originals.py#L154), `str`, `write`.

Явные `raise`:

- `PhotosLibraryUnavailable('Параметры сохранённого оригинала изменились: ' + peer['path'])`
- `PhotosLibraryUnavailable('Источник изменился во время копирования: ' + peer['path'])`
- `PhotosLibraryUnavailable('Сохранённый оригинал отсутствует в копии: ' + peer['path'])`
- `PhotosLibraryUnavailable('Не удалось передать оригинал из копии: ' + str(error))`

Перехватываемые типы: `FileNotFoundError`, `OSError`.

Выражения возврата (ветви, без исполнения):

- `dict(size=count)`


<a id="symbol-photosoriginals--stream-peer-check"></a>

## `PhotosOriginals._stream_peer.check`

[media_manager/photos_originals.py:493](../../media_manager/photos_originals.py#L493)

Проверяет остановку, привязку, том и корень копии-источника между блоками. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def check()
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `any`, `current.get`, `job.get`, `object_id`, `open_readonly`, `os.fstat`, [self._check](../../media_manager/photos_originals.py#L272), [self._link](../../media_manager/photos_originals.py#L143), [self._volume](../../media_manager/photos_originals.py#L191), `volume.get`.

Явные `raise`:

- `PhotosLibraryUnavailable('Источник копирования изменился')`
- `PhotosLibraryUnavailable('Том источника копирования изменился')`
- `PhotosLibraryUnavailable('Папка источника копирования заменена')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--save"></a>

## `PhotosOriginals._save`

[media_manager/photos_originals.py:524](../../media_manager/photos_originals.py#L524)

Повторно использует ресурс либо сохраняет поток в новый конечный файл. Буфер ограничен 64 МиБ; после fsync проверяются размер и ID без чтения содержимого.

```python
def _save(self, job, link, volume, profile, item)
```

Прямые выражения вызова: `OSError`, `PhotosAdapterError`, `PhotosLibraryUnavailable`, `PurePosixPath`, `buffer.clear`, `bytearray`, `created.replace`, `datetime.fromisoformat`, `destination_directory`, `dict`, `fingerprint`, `flush`, `inventory['names'].get`, `item.get`, `len`, `name_key`, `object_id`, `os.close`, `os.fstat`, `os.fsync`, [safe_name](../../media_manager/photos_originals.py#L46), [same_file](../../media_manager/photos_originals.py#L39), [self._check](../../media_manager/photos_originals.py#L272), [self._file](../../media_manager/photos_originals.py#L311), `self._inventories.get`, [self._peer](../../media_manager/photos_originals.py#L473), [self._receipt](../../media_manager/photos_originals.py#L394), [self._reuse_receipt](../../media_manager/photos_originals.py#L407), [self._stream_peer](../../media_manager/photos_originals.py#L486), [self._update](../../media_manager/photos_originals.py#L177), [self._validate](../../media_manager/photos_originals.py#L284), `self.adapter.stream_original`, `self.libraries.copy_source`, `set`, `str`, `trailer.get`.

Явные `raise`:

- `PhotosLibraryUnavailable('Ожидаю готовый оригинал в копии-источнике')`
- `PhotosAdapterError('Размер переданного оригинала не совпал')`
- `OSError('Размер записанного оригинала не совпал')`
- `OSError('Записанный оригинал заменён или изменился')`

Перехватываемые типы: `ValueError`, `FileNotFoundError`.

Выражения возврата (ветви, без исполнения):

- `'reused'`
- `'saved'`


<a id="symbol-photosoriginals--save-flush"></a>

## `PhotosOriginals._save.flush`

[media_manager/photos_originals.py:552](../../media_manager/photos_originals.py#L552)

Проверяет свободное место и записывает накопленный буфер в конечный файл. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def flush()
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `buffer.clear`, `len`, `os.fstatvfs`, [self._create_original](../../media_manager/photos_originals.py#L432), [self._progress](../../media_manager/photos_originals.py#L303), [self._validate](../../media_manager/photos_originals.py#L284), [self._write](../../media_manager/photos_originals.py#L457), `time.monotonic`.

Явные `raise`:

- `PhotosLibraryUnavailable('Недостаточно свободного места в папке копии. Освободи место и продолжи.')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photosoriginals--save-write"></a>

## `PhotosOriginals._save.write`

[media_manager/photos_originals.py:575](../../media_manager/photos_originals.py#L575)

Разбивает принятые данные на ограниченный буфер и публикует прогресс. Использует buffer.extend, flush, memoryview, self._check, self._progress.

```python
def write(chunk)
```

Прямые выражения вызова: `buffer.extend`, [flush](../../media_manager/photos_originals.py#L552), `len`, `memoryview`, `min`, [self._check](../../media_manager/photos_originals.py#L272), [self._progress](../../media_manager/photos_originals.py#L303), [self._validate](../../media_manager/photos_originals.py#L284), `view.release`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals--counts"></a>

## `PhotosOriginals._counts`

[media_manager/photos_originals.py:641](../../media_manager/photos_originals.py#L641)

Пересчитывает готовые объекты и ресурсы по состояниям манифеста. Читает SQLite-таблицы: photos_original_resources.

```python
def _counts(self, job)
```

SQLite: чтение `photos_original_resources`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT COUNT(*) total_assets,COALESCE(SUM(ready),0) done_assets FROM\n                (SELECT asset,MIN(state IN ('saved','reused')) ready FROM photos_original_resources WHERE job_id=? GROUP BY asset)", (job,)).fetchone`, `db.execute("SELECT COUNT(*) total_resources,\n                COALESCE(SUM(state IN ('saved','reused')),0) done_resources,\n                COALESCE(SUM(state='saved'),0) saved,COALESCE(SUM(state='reused'),0) reused,\n                COALESCE(SUM(state='error'),0) errors FROM photos_original_resources WHERE job_id=?", (job,)).fetchone`, `dict`, [self._db](../../media_manager/photos_originals.py#L133).

Выражения возврата (ветви, без исполнения):

- `dict(row) &#124; dict(assets)`


<a id="symbol-photosoriginals--prepare-replica"></a>

## `PhotosOriginals._prepare_replica`

[media_manager/photos_originals.py:653](../../media_manager/photos_originals.py#L653)

Подготавливает задание зависимой копии и сверяет её квитанции с манифестом. Изменяет SQLite-таблицы: photos_original_jobs, photos_original_resources.

```python
def _prepare_replica(self, parent_job, link)
```

SQLite: чтение `photos_copy_files`, `photos_original_resources`, `photos_original_versions`; запись/DDL `photos_original_jobs`, `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PhotosLibraryUnavailable`, `bool`, `db.execute`, `dict`, [encoded](../../media_manager/photos_originals.py#L33), `inventory.get`, `json.loads`, `now`, `object_id`, `open_readonly`, `os.fstat`, `previous.get`, `receipts.get`, [same_file](../../media_manager/photos_originals.py#L39), [self._cleanup](../../media_manager/photos_originals.py#L324), [self._counts](../../media_manager/photos_originals.py#L641), [self._db](../../media_manager/photos_originals.py#L133), [self._inventory](../../media_manager/photos_originals.py#L346), [self._update](../../media_manager/photos_originals.py#L177), [self._volume](../../media_manager/photos_originals.py#L191), [self.summary](../../media_manager/photos_originals.py#L154), `uuid4`.

Явные `raise`:

- `PhotosLibraryUnavailable('Папка копии заменена: ' + link['path'])`

Выражения возврата (ветви, без исполнения):

- `(job, volume)`


<a id="symbol-photosoriginals--replicate-all"></a>

## `PhotosOriginals._replicate_all`

[media_manager/photos_originals.py:693](../../media_manager/photos_originals.py#L693)

Дополняет зависимые копии готовыми ресурсами в порядке источников. Обрабатывает ошибки: (OSError, ValueError, PhotosAdapterError, KeyError), PhotosTransferStopped.

```python
def _replicate_all(self, master_job, master)
```

SQLite: чтение `photos_copy_files`, `photos_copy_links`, `photos_copy_sources`, `photos_original_resources`, `photos_original_versions`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `current.get`, `db.execute`, `dict`, `edges.get`, `json.loads`, `remaining.remove`, [self._check](../../media_manager/photos_originals.py#L272), [self._counts](../../media_manager/photos_originals.py#L641), [self._db](../../media_manager/photos_originals.py#L133), [self._log](../../media_manager/photos_originals.py#L185), [self._prepare_replica](../../media_manager/photos_originals.py#L653), [self._save](../../media_manager/photos_originals.py#L524), [self._update](../../media_manager/photos_originals.py#L177), [self._validate](../../media_manager/photos_originals.py#L284), [self.summary](../../media_manager/photos_originals.py#L154), `self.summary(identifier, raw=True).get`, `set`, `sorted`, `str`.

Перехватываемые типы: `PhotosTransferStopped`, `(OSError, ValueError, PhotosAdapterError, KeyError)`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals-run"></a>

## `PhotosOriginals.run`

[media_manager/photos_originals.py:744](../../media_manager/photos_originals.py#L744)

Обновляет манифест, сохраняет недостающие ресурсы и обслуживает цепочку копий. Изменяет SQLite-таблицы: photos_original_resources.

```python
def run(self, job, link)
```

SQLite: чтение `photos_copy_files`, `photos_copy_links`, `photos_original_jobs`, `photos_original_resources`, `photos_original_versions`; запись/DDL `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PhotosAdapterError`, `db.execute`, `db.execute("SELECT MIN(state IN ('saved','reused')) FROM photos_original_resources WHERE job_id=? AND asset=?", (job, item['asset'])).fetchone`, `dict`, `enumerate`, `item.get`, `json.loads`, [self._cleanup](../../media_manager/photos_originals.py#L324), [self._counts](../../media_manager/photos_originals.py#L641), [self._db](../../media_manager/photos_originals.py#L133), [self._inventory](../../media_manager/photos_originals.py#L346), [self._log](../../media_manager/photos_originals.py#L185), [self._replicate_all](../../media_manager/photos_originals.py#L693), [self._save](../../media_manager/photos_originals.py#L524), [self._update](../../media_manager/photos_originals.py#L177), [self._validate](../../media_manager/photos_originals.py#L284), [self._volume](../../media_manager/photos_originals.py#L191), `self.adapter.close`, `self.adapter.original_manifest`, `self.libraries._require_active`, [self.summary](../../media_manager/photos_originals.py#L154), `self.summary(link['id']).get`, `str`, `uuid4`.

Явные `raise`:

- `PhotosAdapterError(item['error'])`

Перехватываемые типы: `(PhotosTransferStopped, PhotosLibraryUnavailable, PhotosAccessDenied)`, `(OSError, PhotosAdapterError, ValueError)`, `PhotosTransferStopped`, `(PhotosLibraryUnavailable, PhotosAccessDenied)`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photosoriginals-run-asset-received"></a>

## `PhotosOriginals.run.asset_received`

[media_manager/photos_originals.py:764](../../media_manager/photos_originals.py#L764)

Сохраняет ресурсы поступившего объекта манифеста и восстанавливает готовность. Изменяет SQLite-таблицы: photos_original_resources.

```python
def asset_received(asset)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_original_resources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `asset.get`, `bool`, `db.execute`, `dict`, [encoded](../../media_manager/photos_originals.py#L33), `f'Обновляю список оригиналов Photos · {received:,}'.replace`, `item.get`, `json.loads`, `receipts.get`, [same_file](../../media_manager/photos_originals.py#L39), [self._db](../../media_manager/photos_originals.py#L133), `self._inventories[link['id']]['files'].get`, [self._progress](../../media_manager/photos_originals.py#L303), [self._validate](../../media_manager/photos_originals.py#L284).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
