# Копии iCloud Drive: `media_manager/icloud_copies.py`

Ведёт постоянную очередь копий облачных папок. Отдельный процесс macOS запрашивает загрузку и читает содержимое с контролем задержек. Публикация защищает существующие файлы и сверяет метаданные.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/icloud_copies.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [copy_setup_ui.py](copy_setup_ui.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [paired_workspace_ui.py](paired_workspace_ui.md), [photo_libraries_ui.py](photo_libraries_ui.md), [storage_preview_ui.py](storage_preview_ui.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_directory_sizes.py](tests.md#module-tests.test_directory_sizes), [tests/test_icloud_copies.py](tests.md#module-tests.test_icloud_copies).

## Оглавление определений

- [CloudPending](#symbol-CloudPending) — Откладывает путь, пока iCloud работает или освободится место в пакете.
- [CloudPending.__init__](#symbol-CloudPending.__init__) — Передаёт причину ожидания и задержку до допустимой повторной проверки.
- [ICloudCopies](#symbol-ICloudCopies) — Хранит привязки папок iCloud Drive, очередь передачи и результат каждого пути.
- [ICloudCopies.__init__](#symbol-ICloudCopies.__init__) — Инициализирует постоянную очередь и параметры фонового исполнителя.
- [ICloudCopies._batch_local_bytes](#symbol-ICloudCopies._batch_local_bytes) — Суммирует реально выделенные блоки файлов текущего пакета по метаданным.
- [ICloudCopies._batch_usage](#symbol-ICloudCopies._batch_usage) — Возвращает общее число и логический объём загрузок, занявших пакет.
- [ICloudCopies._check](#symbol-ICloudCopies._check) — Прерывает работу при паузе выбранной копии или выходе Core.
- [ICloudCopies._cleanup](#symbol-ICloudCopies._cleanup) — Удаляет собственную незавершённую запись после сверки идентичности.
- [ICloudCopies._copy](#symbol-ICloudCopies._copy) — Возвращает привязку и проверяет её наличие в базе.
- [ICloudCopies._evict_download](#symbol-ICloudCopies._evict_download) — Освобождает загрузку приложения после проверки обеих версий файла.
- [ICloudCopies._finish_item](#symbol-ICloudCopies._finish_item) — Освобождает текущий путь и завершает привязку сразу после последнего элемента.
- [ICloudCopies._next](#symbol-ICloudCopies._next) — Сначала проверяет занятые места пакета и откладывает известные заявки без места.
- [ICloudCopies._prepare_download](#symbol-ICloudCopies._prepare_download) — Управляет явной загрузкой отсутствующего облачного файла и записывает её владельца.
- [ICloudCopies._process](#symbol-ICloudCopies._process) — Выполняет одну попытку, фиксируя временный сбой тома или выбранного пути.
- [ICloudCopies._publish](#symbol-ICloudCopies._publish) — Публикует временный путь атомарно, где это поддерживает файловая система.
- [ICloudCopies._queue_ready_sources](#symbol-ICloudCopies._queue_ready_sources) — Формирует очередь зависимой копии из завершённого прохода копии-источника.
- [ICloudCopies._read_local](#symbol-ICloudCopies._read_local) — Читает подтверждённый локальный файл из предыдущего звена по дескриптору.
- [ICloudCopies._reserve_download](#symbol-ICloudCopies._reserve_download) — Резервирует место пакета перед первым запросом загрузки заполнителя iCloud.
- [ICloudCopies._scan](#symbol-ICloudCopies._scan) — Добавляет облачные дочерние пути или создаёт папку из очереди зависимой копии.
- [ICloudCopies._scope_numbers](#symbol-ICloudCopies._scope_numbers) — Вводит независимую нумерацию копий для каждого корня iCloud.
- [ICloudCopies._source_parent](#symbol-ICloudCopies._source_parent) — Безопасно открывает подтверждённого родителя исходного файла.
- [ICloudCopies._target_volume](#symbol-ICloudCopies._target_volume) — Проверяет доступность и подтверждённую идентичность тома назначения.
- [ICloudCopies._transfer](#symbol-ICloudCopies._transfer) — Планирует запись одного отсутствующего файла с учётом существующего назначения.
- [ICloudCopies._update_copy](#symbol-ICloudCopies._update_copy) — Обновляет состояние привязки внутри переданной транзакции.
- [ICloudCopies._update_item](#symbol-ICloudCopies._update_item) — Обновляет состояние элемента очереди и его промежуточной записи.
- [ICloudCopies._validate_roots](#symbol-ICloudCopies._validate_roots) — Сопоставляет действующий источник и целевой корень с сохранённой привязкой.
- [ICloudCopies._validate_transfer](#symbol-ICloudCopies._validate_transfer) — Проверяет после записи версию источника и идентичность папки назначения.
- [ICloudCopies._work](#symbol-ICloudCopies._work) — Обходит готовые элементы и оставляет временные ошибки для последующих попыток.
- [ICloudCopies._write](#symbol-ICloudCopies._write) — Сохраняет содержимое во временный файл и публикует без перезаписи.
- [ICloudCopies._write.check](#symbol-ICloudCopies._write.check) — Проверяет активность копии во время чтения с ограничением обращения к SQLite.
- [ICloudCopies._write_network](#symbol-ICloudCopies._write_network) — Записывает готовый промежуточный файл на SMB без перезаписи существующего пути.
- [ICloudCopies.bind](#symbol-ICloudCopies.bind) — Привязывает папку назначения к облачной области или её сохранённой копии.
- [ICloudCopies.browse](#symbol-ICloudCopies.browse) — Читает метаданные папки iCloud для обычного дерева без скачивания содержимого.
- [ICloudCopies.close](#symbol-ICloudCopies.close) — Кооперативно завершает поток перед остановкой Core.
- [ICloudCopies.journal](#symbol-ICloudCopies.journal) — Возвращает страницу журнала с причинами задержек и временем повтора.
- [ICloudCopies.list](#symbol-ICloudCopies.list) — Возвращает краткое состояние копий для боковой панели.
- [ICloudCopies.pause_copy](#symbol-ICloudCopies.pause_copy) — Ставит привязку на постоянную паузу и останавливает текущую передачу.
- [ICloudCopies.source_volume](#symbol-ICloudCopies.source_volume) — Возвращает доступный путь облачного источника для просмотра и подсчёта.
- [ICloudCopies.start](#symbol-ICloudCopies.start) — Запускает обработку активных привязок, в том числе после перезапуска Core.
- [ICloudCopies.start_copy](#symbol-ICloudCopies.start_copy) — Включает передачу или начинает новый проход после завершения предыдущего.
- [ICloudCopies.unbind](#symbol-ICloudCopies.unbind) — Удаляет остановленную привязку после выхода исполнителя из текущего файла.
- [ICloudReader](#symbol-ICloudReader) — Запрашивает загрузку и ограничивает ожидание данных отдельного процесса чтения.
- [ICloudReader.__init__](#symbol-ICloudReader.__init__) — Запоминает расположение исполняемого помощника Core.
- [ICloudReader.command](#symbol-ICloudReader.command) — Собирает помощник macOS при первом запуске или изменении нативного кода.
- [ICloudReader.residency](#symbol-ICloudReader.residency) — Вызывает одну явную операцию macOS над подтверждённой версией файла.
- [ICloudReader.stream](#symbol-ICloudReader.stream) — Передаёт блоки файла до конца, паузы или тайм-аута без данных.
- [cloud_dataless](#symbol-cloud_dataless) — Читает системный признак отсутствующего содержимого из метаданных файла.
- [cloud_version](#symbol-cloud_version) — Собирает идентичность, размер и mtime файла для дальнейшей проверки.
- [free_bytes](#symbol-free_bytes) — Возвращает доступное место для новых загрузок на системном диске.
- [icloud_volume](#symbol-icloud_volume) — Возвращает виртуальный том iCloud Drive для двухпанельного дерева.

## Константы и значения по умолчанию

<a id="constant-CLOUD_BATCH_BYTES"></a>

### `CLOUD_BATCH_BYTES`

`1024 ** 3`

<a id="constant-CLOUD_BATCH_FILES"></a>

### `CLOUD_BATCH_FILES`

`8`

<a id="constant-CLOUD_DISK_RESERVE"></a>

### `CLOUD_DISK_RESERVE`

`2 * 1024 ** 3`

<a id="constant-CLOUD_IN_PROGRESS"></a>

### `CLOUD_IN_PROGRESS`

`('reserved', 'requested', 'external', 'copying', 'evict_pending')`

<a id="constant-ICLOUD_VOLUME_ID"></a>

### `ICLOUD_VOLUME_ID`

`'icloud-drive'`

<a id="constant-PUBLISH_UNSUPPORTED"></a>

### `PUBLISH_UNSUPPORTED`

`{errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS, errno.EINVAL}`

<a id="constant-READ_TIMEOUT"></a>

### `READ_TIMEOUT`

`45`


<a id="symbol-CloudPending"></a>

## `CloudPending`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `CloudPending`

Откладывает путь, пока iCloud работает или освободится место в пакете. Пауза ожидания не увеличивает интервал обработки обычных ошибок.

Базовые классы: `OSError`.


Состояние, присваиваемое конструктором: `delay`.

Именованные методы: `__init__`.

<a id="symbol-CloudPending.__init__"></a>

## `CloudPending.__init__`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `CloudPending.__init__`

Передаёт причину ожидания и задержку до допустимой повторной проверки. Нулевая задержка передаёт управление проверке вместимости в очереди.

```python
def __init__(self, message, *, delay=5)
```

Присваивания полям `self`: `delay`.

Прямые выражения вызова: `super`, `super().__init__`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies"></a>

## `ICloudCopies`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies`

Хранит привязки папок iCloud Drive, очередь передачи и результат каждого пути. Зависимости конструктора: storage, build_directory, root, reader.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_current`, `_lock`, `_stop`, `_thread`, `_wake`, `reader`, `root`, `storage`.

Именованные методы: `__init__`, `_scope_numbers`, `source_volume`, `browse`, `_copy`, `_target_volume`, `_batch_usage`, `bind`, `list`, `_batch_local_bytes`, `journal`, `start_copy`, `pause_copy`, `unbind`, `start`, `close`, `_update_copy`, `_update_item`, `_check`, `_queue_ready_sources`, `_next`, `_finish_item`, `_work`, `_validate_roots`, `_process`, `_scan`, `_cleanup`, `_source_parent`, `_reserve_download`, `_prepare_download`, `_evict_download`, `_transfer`, `_read_local`, `_write`, `_validate_transfer`, `_publish`, `_write_network`.

<a id="symbol-ICloudCopies.__init__"></a>

## `ICloudCopies.__init__`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.__init__`

Инициализирует постоянную очередь и параметры фонового исполнителя. Изменяет SQLite-таблицы: icloud_copies, icloud_copy_items.

```python
def __init__(self, storage, build_directory, *, root=None, reader=None)
```

SQLite: чтение не найдено; запись/DDL `icloud_copies`, `icloud_copy_items`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_current`, `_lock`, `_stop`, `_thread`, `_wake`, `reader`, `root`, `storage`.

Прямые выражения вызова: [ICloudReader](media_manager--icloud_copies.md#symbol-ICloudReader), `Path`, `Path.home`, `db.execute`, `db.executescript`, [self._scope_numbers](media_manager--icloud_copies.md#symbol-ICloudCopies._scope_numbers), `self.storage.connect`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._batch_local_bytes"></a>

## `ICloudCopies._batch_local_bytes`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._batch_local_bytes`

Суммирует реально выделенные блоки файлов текущего пакета по метаданным. Два задания для одного файла учитываются один раз; неполные метаданные дают неизвестный результат.

```python
def _batch_local_bytes(source, tracked)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `PurePosixPath`, [cloud_version](media_manager--icloud_copies.md#symbol-cloud_version), `json.loads`, `occupied.values`, `open_readonly`, `os.stat`, `relative_path`, `stat.S_ISREG`, `str`, `sum`.

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `None`
- `sum(occupied.values())`


<a id="symbol-ICloudCopies._batch_usage"></a>

## `ICloudCopies._batch_usage`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._batch_usage`

Возвращает общее число и логический объём загрузок, занявших пакет. Учитывает очередь всех прямых копий, включая запрошенные до ручной паузы.

```python
def _batch_usage(db)
```

Декораторы: `staticmethod`.

SQLite: чтение `icloud_copy_items`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `db.execute(f"SELECT COUNT(*) AS files, COALESCE(SUM(cloud_bytes),0) AS bytes\n                            FROM icloud_copy_items WHERE cloud_phase != '' AND cloud_phase IN ({marks})", CLOUD_IN_PROGRESS).fetchone`, `dict`.

Выражения возврата (ветви, без исполнения):

- `dict(row)`


<a id="symbol-ICloudCopies._check"></a>

## `ICloudCopies._check`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._check`

Прерывает работу при паузе выбранной копии или выходе Core. Явно отклоняет недопустимое состояние через CopyStopped.

```python
def _check(self, copy_id)
```

Прямые выражения вызова: `CopyStopped`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), `self._stop.is_set`.

Явные `raise`:

- `CopyStopped()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._cleanup"></a>

## `ICloudCopies._cleanup`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._cleanup`

Удаляет собственную незавершённую запись после сверки идентичности. Оставляет заменённый внешним процессом объект на диске.

```python
def _cleanup(self, item, target, staging)
```

Прямые выражения вызова: `object_id`, `os.stat`, `os.unlink`, [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), `staging.get`, `stat.S_ISREG`.

Перехватываемые типы: `FileNotFoundError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._copy"></a>

## `ICloudCopies._copy`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._copy`

Возвращает привязку и проверяет её наличие в базе. Явно отклоняет недопустимое состояние через KeyError.

```python
def _copy(self, copy_id)
```

SQLite: чтение `icloud_copies`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT * FROM icloud_copies WHERE id=?', (copy_id,)).fetchone`, `dict`, `self.storage.connect`.

Явные `raise`:

- `KeyError('Копия iCloud Drive не найдена')`

Выражения возврата (ветви, без исполнения):

- `dict(row, number=row['scope_number'])`


<a id="symbol-ICloudCopies._evict_download"></a>

## `ICloudCopies._evict_download`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._evict_download`

Освобождает загрузку приложения после проверки обеих версий файла. Если macOS сохраняет загрузку, причина остаётся в журнале.

```python
def _evict_download(self, item, copy, source_volume, target_volume)
```

Прямые выражения вызова: `PurePosixPath`, [cloud_version](media_manager--icloud_copies.md#symbol-cloud_version), `destination_directory`, `json.loads`, `os.stat`, `relative_path`, [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), [self._source_parent](media_manager--icloud_copies.md#symbol-ICloudCopies._source_parent), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), `self.reader.residency`, `stat.S_ISREG`, `str`, `time.time`.

Перехватываемые типы: `(OSError, subprocess.SubprocessError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ICloudCopies._finish_item"></a>

## `ICloudCopies._finish_item`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._finish_item`

Освобождает текущий путь и завершает привязку сразу после последнего элемента. Сохраняет статус ожидания при отложенных повторных попытках.

```python
def _finish_item(self, copy_id)
```

SQLite: чтение `icloud_copy_items`; запись/DDL `icloud_copies`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT 1 FROM icloud_copy_items WHERE copy_id=?\n                                    AND (state='pending' OR cloud_phase='evict_pending') LIMIT 1", (copy_id,)).fetchone`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), [self._update_copy](media_manager--icloud_copies.md#symbol-ICloudCopies._update_copy), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ICloudCopies._next"></a>

## `ICloudCopies._next`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._next`

Сначала проверяет занятые места пакета и откладывает известные заявки без места. Учитывает общий лимит файлов и байтов, затем обновляет состояние привязок.

```python
def _next(self)
```

SQLite: чтение `icloud_copies`, `icloud_copy_items`; запись/DDL `icloud_copies`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `db.execute("\n                SELECT c.id,COUNT(*) FILTER (WHERE i.state='retry') AS waiting,\n                    COUNT(*) FILTER (WHERE i.state='pending' OR i.cloud_phase='evict_pending') AS pending,\n                    COUNT(*) FILTER (WHERE i.state='conflict') AS conflicts\n                FROM icloud_copies c LEFT JOIN icloud_copy_items i ON i.copy_id=c.id\n                WHERE c.active=1 AND c.state!='waiting_source' AND c.retry_at<=? GROUP BY c.id\n            ", (current,)).fetchall`, `db.execute(f"\n                SELECT i.* FROM icloud_copy_items i JOIN icloud_copies c ON c.id=i.copy_id\n                WHERE c.active=1 AND c.retry_at<=? AND (i.state IN ('pending','retry') OR i.cloud_phase='evict_pending') AND i.retry_at<=?\n                  AND (i.cloud_phase!='waiting_space' OR (? AND (?=0 OR i.cloud_bytes<=?)))\n                ORDER BY CASE WHEN i.cloud_phase='evict_pending' THEN 0\n                              WHEN i.cloud_phase IN ({marks}) THEN 1 ELSE 2 END,\n                         c.updated_at, i.retry_at, i.path LIMIT 1\n            ", (current, current, batch['files'] < CLOUD_BATCH_FILES, batch['files'], CLOUD_BATCH_BYTES - batch['bytes'], *CLOUD_IN_PROGRESS)).fetchone`, `dict`, [self._batch_usage](media_manager--icloud_copies.md#symbol-ICloudCopies._batch_usage), [self._queue_ready_sources](media_manager--icloud_copies.md#symbol-ICloudCopies._queue_ready_sources), [self._update_copy](media_manager--icloud_copies.md#symbol-ICloudCopies._update_copy), `self.storage.connect`, `time.time`.

Выражения возврата (ветви, без исполнения):

- `dict(item)`
- `None`


<a id="symbol-ICloudCopies._prepare_download"></a>

## `ICloudCopies._prepare_download`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._prepare_download`

Управляет явной загрузкой отсутствующего облачного файла и записывает её владельца. Уже локальный файл доступен сразу; после перезапуска сохраняется прежняя заявка.

```python
def _prepare_download(self, item, original, name, source)
```

Прямые выражения вызова: [CloudPending](media_manager--icloud_copies.md#symbol-CloudPending), [cloud_dataless](media_manager--icloud_copies.md#symbol-cloud_dataless), [cloud_version](media_manager--icloud_copies.md#symbol-cloud_version), `json.loads`, [self._reserve_download](media_manager--icloud_copies.md#symbol-ICloudCopies._reserve_download), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), `self.reader.residency`, `str`.

Явные `raise`:

- `CloudPending('Ожидание загрузки из iCloud')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `'copying'`
- `phase if phase in CLOUD_IN_PROGRESS else 'local'`


<a id="symbol-ICloudCopies._process"></a>

## `ICloudCopies._process`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._process`

Выполняет одну попытку, фиксируя временный сбой тома или выбранного пути. Вычисляет паузу от 15 секунд до 15 минут по числу попыток.

```python
def _process(self, item)
```

Прямые выражения вызова: `min`, [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), [self._evict_download](media_manager--icloud_copies.md#symbol-ICloudCopies._evict_download), [self._finish_item](media_manager--icloud_copies.md#symbol-ICloudCopies._finish_item), [self._scan](media_manager--icloud_copies.md#symbol-ICloudCopies._scan), [self._target_volume](media_manager--icloud_copies.md#symbol-ICloudCopies._target_volume), [self._transfer](media_manager--icloud_copies.md#symbol-ICloudCopies._transfer), [self._update_copy](media_manager--icloud_copies.md#symbol-ICloudCopies._update_copy), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), [self._validate_roots](media_manager--icloud_copies.md#symbol-ICloudCopies._validate_roots), [self.source_volume](media_manager--icloud_copies.md#symbol-ICloudCopies.source_volume), `self.storage.connect`, `str`, `time.time`.

Перехватываемые типы: `OSError`, `CloudPending`, `(OSError, subprocess.SubprocessError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ICloudCopies._publish"></a>

## `ICloudCopies._publish`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._publish`

Публикует временный путь атомарно, где это поддерживает файловая система. Запрашивает прямую запись на сетевом томе при отсутствии поддержки.

```python
def _publish(target, temporary, name, network)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `DirectCopyRequired`, `os.link`, `publish_exclusive`.

Явные `raise`:

- `DirectCopyRequired()`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._queue_ready_sources"></a>

## `ICloudCopies._queue_ready_sources`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._queue_ready_sources`

Формирует очередь зависимой копии из завершённого прохода копии-источника. Переносит только готовые пути и журналирует расхождения предыдущего звена.

```python
def _queue_ready_sources(self, db)
```

SQLite: чтение `icloud_copies`, `icloud_copy_items`; запись/DDL `icloud_copy_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("\n            SELECT c.id,c.source_link_id FROM icloud_copies c\n            JOIN icloud_copies p ON p.id=c.source_link_id\n            WHERE c.active=1 AND c.state='waiting_source' AND p.active=0\n                AND p.state IN ('completed','completed_with_conflicts')\n                AND EXISTS (SELECT 1 FROM icloud_copy_items i WHERE i.copy_id=p.id AND i.path='')\n        ").fetchall`, `now`, [self._update_copy](media_manager--icloud_copies.md#symbol-ICloudCopies._update_copy).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._read_local"></a>

## `ICloudCopies._read_local`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._read_local`

Читает подтверждённый локальный файл из предыдущего звена по дескриптору. Сверяет файловые метаданные перед чтением и проверяет паузу между блоками.

```python
def _read_local(parent, name, source, check)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `OSError`, `check`, `fingerprint`, `os.fdopen`, `os.fstat`, `os.open`, `stream.read`.

Явные `raise`:

- `OSError('Файл в копии-источнике изменился перед чтением')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ICloudCopies._reserve_download"></a>

## `ICloudCopies._reserve_download`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._reserve_download`

Резервирует место пакета перед первым запросом загрузки заполнителя iCloud. Разрешает большой файл отдельно, если после загрузки останется резерв диска.

```python
def _reserve_download(self, item, original, source, version)
```

SQLite: чтение не найдено; запись/DDL `icloud_copy_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: [CloudPending](media_manager--icloud_copies.md#symbol-CloudPending), `db.execute`, [free_bytes](media_manager--icloud_copies.md#symbol-free_bytes), `json.dumps`, `now`, [self._batch_usage](media_manager--icloud_copies.md#symbol-ICloudCopies._batch_usage), [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), `self.storage.connect`, `str`.

Явные `raise`:

- `pending`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ICloudCopies._scan"></a>

## `ICloudCopies._scan`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._scan`

Добавляет облачные дочерние пути или создаёт папку из очереди зависимой копии. Сохраняет пустые каталоги и пропускает ссылки и специальные объекты.

```python
def _scan(self, item, copy, source_volume, target_volume)
```

SQLite: чтение не найдено; запись/DDL `icloud_copy_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `'/'.join`, `children.append`, `db.executemany`, `destination_directory`, `entry.stat`, `filter`, `now`, `open_readonly`, `os.fstat`, `os.scandir`, [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), [self._validate_roots](media_manager--icloud_copies.md#symbol-ICloudCopies._validate_roots), `self.storage.connect`, `service_file`, `stat.S_ISDIR`, `stat.S_ISREG`.

Перехватываемые типы: `FileNotFoundError`, `NotADirectoryError`.

Выражения возврата (ветви, без исполнения):

- `('conflict', 'Путь папки занят другим объектом')`
- `('done', '')`


<a id="symbol-ICloudCopies._scope_numbers"></a>

## `ICloudCopies._scope_numbers`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._scope_numbers`

Вводит независимую нумерацию копий для каждого корня iCloud. Прежний порядковый номер задаёт порядок миграции; ID, задания и файлы сохраняются.

```python
def _scope_numbers(db)
```

Декораторы: `staticmethod`.

SQLite: чтение `icloud_copies`; запись/DDL `icloud_copies`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._source_parent"></a>

## `ICloudCopies._source_parent`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._source_parent`

Безопасно открывает подтверждённого родителя исходного файла. Поля результата: дескриптор родителя и имя файла.

```python
def _source_parent(copy, source_volume, path)
```

Декораторы: `staticmethod`, `contextmanager`.

Прямые выражения вызова: `PurePosixPath`, `open_readonly`, `relative_path`, `str`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-ICloudCopies._target_volume"></a>

## `ICloudCopies._target_volume`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._target_volume`

Проверяет доступность и подтверждённую идентичность тома назначения. Явно отклоняет недопустимое состояние через OSError.

```python
def _target_volume(self, volume_id, *, force=False)
```

Прямые выражения вызова: `OSError`, `next`, `self.storage.refresh`.

Явные `raise`:

- `OSError('Том копии отключён или недоступен')`
- `OSError('Сначала подтверди том назначения')`

Выражения возврата (ветви, без исполнения):

- `volume`


<a id="symbol-ICloudCopies._transfer"></a>

## `ICloudCopies._transfer`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._transfer`

Планирует запись одного отсутствующего файла с учётом существующего назначения. Проверяет размер и не читает содержимое уже существующего файла.

```python
def _transfer(self, item, copy, source_volume, target_volume)
```

Прямые выражения вызова: [CloudPending](media_manager--icloud_copies.md#symbol-CloudPending), `PurePosixPath`, `bool`, [cloud_dataless](media_manager--icloud_copies.md#symbol-cloud_dataless), [cloud_version](media_manager--icloud_copies.md#symbol-cloud_version), `destination_directory`, `dict`, `json.dumps`, `json.loads`, `os.fstat`, `os.stat`, `relative_path`, [self._cleanup](media_manager--icloud_copies.md#symbol-ICloudCopies._cleanup), [self._prepare_download](media_manager--icloud_copies.md#symbol-ICloudCopies._prepare_download), [self._source_parent](media_manager--icloud_copies.md#symbol-ICloudCopies._source_parent), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), [self._write](media_manager--icloud_copies.md#symbol-ICloudCopies._write), `stat.S_ISREG`, `str`.

Явные `raise`:

- `CloudPending('Ожидает завершения уже запрошенной загрузки iCloud')`

Перехватываемые типы: `FileNotFoundError`, `NotADirectoryError`.

Выражения возврата (ветви, без исполнения):

- `('conflict', 'Источник изменился: ожидался обычный файл')`
- `(state, message)`
- `('existing', 'Файл уже есть в копии, размер совпадает')`
- `('conflict', 'Путь занят файлом другого размера или типа')`
- `('conflict', 'Путь к файлу занят другим объектом')`


<a id="symbol-ICloudCopies._update_copy"></a>

## `ICloudCopies._update_copy`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._update_copy`

Обновляет состояние привязки внутри переданной транзакции. Изменяет SQLite-таблицу icloud_copies.

```python
def _update_copy(db, copy_id, **values)
```

Декораторы: `staticmethod`.

SQLite: чтение не найдено; запись/DDL `icloud_copies`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._update_item"></a>

## `ICloudCopies._update_item`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._update_item`

Обновляет состояние элемента очереди и его промежуточной записи. Изменяет SQLite-таблицу icloud_copy_items.

```python
def _update_item(self, item, **values)
```

SQLite: чтение не найдено; запись/DDL `icloud_copy_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._validate_roots"></a>

## `ICloudCopies._validate_roots`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._validate_roots`

Сопоставляет действующий источник и целевой корень с сохранённой привязкой. Явно отклоняет недопустимое состояние через OSError.

```python
def _validate_roots(self, copy, source_volume, target_volume)
```

Прямые выражения вызова: `OSError`, `json.loads`, `object_id`, `open_readonly`, `os.fstat`.

Явные `raise`:

- `OSError('Папка источника или назначения заменена. Проверь привязку.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._validate_transfer"></a>

## `ICloudCopies._validate_transfer`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._validate_transfer`

Проверяет после записи версию источника и идентичность папки назначения. Явно отклоняет недопустимое состояние через OSError.

```python
def _validate_transfer(self, item, copy, source_volume, target_volume, source, parent, target, name)
```

Прямые выражения вызова: `OSError`, `destination_directory`, `fingerprint`, `object_id`, `os.fstat`, `os.stat`, [self._source_parent](media_manager--icloud_copies.md#symbol-ICloudCopies._source_parent), [self._validate_roots](media_manager--icloud_copies.md#symbol-ICloudCopies._validate_roots).

Явные `raise`:

- `OSError('Исходный файл изменился во время копирования')`
- `OSError('Целевая папка заменена во время копирования')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._work"></a>

## `ICloudCopies._work`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._work`

Обходит готовые элементы и оставляет временные ошибки для последующих попыток. Обрабатывает ошибки: CopyStopped, OSError, subprocess.SubprocessError.

```python
def _work(self)
```

Присваивания полям `self`: `_current`.

Прямые выражения вызова: [self._next](media_manager--icloud_copies.md#symbol-ICloudCopies._next), [self._process](media_manager--icloud_copies.md#symbol-ICloudCopies._process), `self._stop.is_set`, `self._wake.clear`, `self._wake.wait`.

Перехватываемые типы: `CopyStopped`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._write"></a>

## `ICloudCopies._write`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._write`

Сохраняет содержимое во временный файл и публикует без перезаписи. Перед публикацией сверяет размер, версию исходника и идентичность папки назначения.

```python
def _write(self, item, copy, source_volume, target_volume, original, source, parent, target, name)
```

Прямые выражения вызова: `OSError`, `closing`, [cloud_version](media_manager--icloud_copies.md#symbol-cloud_version), `dict`, `json.dumps`, `len`, `object_id`, `os.close`, `os.dup`, `os.fdopen`, `os.fstat`, `os.fsync`, `os.open`, `os.stat`, `os.utime`, `output.flush`, `output.write`, [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), [self._cleanup](media_manager--icloud_copies.md#symbol-ICloudCopies._cleanup), [self._publish](media_manager--icloud_copies.md#symbol-ICloudCopies._publish), [self._read_local](media_manager--icloud_copies.md#symbol-ICloudCopies._read_local), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), [self._validate_transfer](media_manager--icloud_copies.md#symbol-ICloudCopies._validate_transfer), [self._write_network](media_manager--icloud_copies.md#symbol-ICloudCopies._write_network), `self.reader.stream`, `target_volume.get`, `uuid4`.

Явные `raise`:

- `OSError('Исходный файл вырос во время копирования')`
- `OSError('Размер записанного файла не совпал с размером источника')`
- `OSError('Промежуточный файл заменён во время копирования')`

Перехватываемые типы: `DirectCopyRequired`, `FileExistsError`.

Выражения возврата (ветви, без исполнения):

- `('conflict', 'Файл появился в копии во время передачи', None)`
- `('done', 'Скопирован', written)`


<a id="symbol-ICloudCopies._write.check"></a>

## `ICloudCopies._write.check`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._write.check`

Проверяет активность копии во время чтения с ограничением обращения к SQLite. Обновляет локальное время следующей проверки.

```python
def check()
```

Прямые выражения вызова: [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), `self._stop.is_set`, `time.monotonic`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies._write_network"></a>

## `ICloudCopies._write_network`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies._write_network`

Записывает готовый промежуточный файл на SMB без перезаписи существующего пути. Журналирует незавершённое конечное имя до подтверждения размера и fsync.

```python
def _write_network(self, item, copy, source_volume, target_volume, source, parent, target, name, descriptor, staging, check)
```

Прямые выражения вызова: `OSError`, `check`, [cloud_version](media_manager--icloud_copies.md#symbol-cloud_version), `dict`, `json.dumps`, `object_id`, `os.fdopen`, `os.fstat`, `os.fsync`, `os.lseek`, `os.open`, `os.read`, `os.stat`, `output.flush`, `output.write`, [self._check](media_manager--icloud_copies.md#symbol-ICloudCopies._check), [self._update_item](media_manager--icloud_copies.md#symbol-ICloudCopies._update_item), [self._validate_transfer](media_manager--icloud_copies.md#symbol-ICloudCopies._validate_transfer), `staging.pop`.

Явные `raise`:

- `OSError('Размер записанного файла не совпал с размером источника')`
- `OSError('Файл назначения заменён во время копирования')`

Выражения возврата (ветви, без исполнения):

- `cloud_version(os.fstat(final))`


<a id="symbol-ICloudCopies.bind"></a>

## `ICloudCopies.bind`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.bind`

Привязывает папку назначения к облачной области или её сохранённой копии. Проверяет непересечение корней и сохраняет их идентичность.

```python
def bind(self, source_path, volume_id, path, source_link_id=None)
```

SQLite: чтение `icloud_copies`; запись/DDL `icloud_copies`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `(Path(destination['mount_path']) / path).resolve`, `MissingCopyCatalog._roots`, `OSError`, `Path`, `PurePosixPath`, `ValueError`, `cloud_path.is_relative_to`, `db.execute`, `db.execute('SELECT COALESCE(MAX(number),0)+1 FROM icloud_copies').fetchone`, `db.execute('SELECT COALESCE(MAX(scope_number),0)+1 FROM icloud_copies WHERE source_path=?', (source_path,)).fetchone`, `dict`, `json.dumps`, `json.loads`, `now`, `object_id`, `open_readonly`, `os.fstat`, `other.is_relative_to`, `relative_path`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), [self._target_volume](media_manager--icloud_copies.md#symbol-ICloudCopies._target_volume), `self.root.is_dir`, `self.root.resolve`, [self.source_volume](media_manager--icloud_copies.md#symbol-ICloudCopies.source_volume), `self.storage.connect`, `target.is_relative_to`, `target_path.is_relative_to`, `uuid4`.

Явные `raise`:

- `ValueError('Выбери папку назначения внутри тома')`
- `ValueError('Выбери копию той же папки iCloud Drive')`
- `ValueError('Папка назначения и iCloud Drive пересекаются.')`
- `OSError('Папка копии-источника заменена. Проверь привязку.')`
- `ValueError('Папка пересекается с уже привязанной копией iCloud Drive')`

Выражения возврата (ветви, без исполнения):

- `dict(id=copy_id, number=number)`


<a id="symbol-ICloudCopies.browse"></a>

## `ICloudCopies.browse`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.browse`

Читает метаданные папки iCloud для обычного дерева без скачивания содержимого. Поля результата: path, volume, entries, scanned_at, cached.

```python
def browse(self, path)
```

Прямые выражения вызова: `StorageCatalog._read_directory`, `dict`, [icloud_volume](media_manager--icloud_copies.md#symbol-icloud_volume), `now`, `relative_path`, [self.source_volume](media_manager--icloud_copies.md#symbol-ICloudCopies.source_volume).

Выражения возврата (ветви, без исполнения):

- `dict(path=path, volume=icloud_volume(True), entries=entries, scanned_at=now(), cached=False)`


<a id="symbol-ICloudCopies.close"></a>

## `ICloudCopies.close`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.close`

Кооперативно завершает поток перед остановкой Core. Использует _stop, _wake и join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`, `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudCopies.journal"></a>

## `ICloudCopies.journal`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.journal`

Возвращает страницу журнала с причинами задержек и временем повтора. Читает SQLite-таблицы: icloud_copy_items.

```python
def journal(self, copy_id, offset=0, limit=100)
```

SQLite: чтение `icloud_copy_items`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `db.execute(f"\n                SELECT path,kind,state,attempts,retry_at,message,updated_at,cloud_phase,cloud_bytes,cloud_message FROM icloud_copy_items\n                WHERE copy_id=? AND (state!='pending' OR cloud_phase!='')\n                ORDER BY CASE WHEN cloud_phase IN ({marks}) THEN 0 WHEN state='retry' THEN 1\n                              WHEN state='conflict' THEN 2 ELSE 3 END, updated_at DESC, path\n                LIMIT ? OFFSET ?\n            ", (copy_id, *CLOUD_IN_PROGRESS, limit + 1, offset)).fetchall`, `dict`, `len`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `dict(state=copy['state'], message=copy['message'], items=[dict(row) for row in rows[:limit]], more=len(rows) > limit)`


<a id="symbol-ICloudCopies.list"></a>

## `ICloudCopies.list`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.list`

Возвращает краткое состояние копий для боковой панели. Считает готовые файлы, ожидающие повтора пути и расхождения.

```python
def list(self)
```

SQLite: чтение `icloud_copies`, `icloud_copy_items`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `batch.update`, `copies.append`, `db.execute`, `db.execute("\n                SELECT c.id,c.scope_number AS number,c.source_path,c.source_link_id,p.scope_number AS source_number,\n                    c.volume_id,c.path,c.active,c.state,c.current_path,c.message,c.retry_at,\n                    COUNT(*) FILTER (WHERE i.kind='file') AS total,\n                    COUNT(*) FILTER (WHERE i.kind='file' AND i.state IN ('done','existing')) AS done,\n                    COUNT(*) FILTER (WHERE i.state='retry') AS waiting,\n                    COUNT(*) FILTER (WHERE i.state='conflict') AS conflicts,\n                    COUNT(*) FILTER (WHERE i.cloud_phase='evicted') AS evicted,\n                    COALESCE(SUM(i.cloud_bytes) FILTER (WHERE i.cloud_phase='evicted'),0) AS evicted_bytes,\n                    COUNT(*) FILTER (WHERE i.cloud_phase='kept') AS kept_downloads,\n                    MIN(i.retry_at) FILTER (WHERE i.state='retry' AND i.retry_at>0) AS next_attempt\n                FROM icloud_copies c LEFT JOIN icloud_copies p ON p.id=c.source_link_id\n                LEFT JOIN icloud_copy_items i ON c.id=i.copy_id\n                GROUP BY c.id ORDER BY c.number\n            ").fetchall`, `db.execute(f'SELECT c.source_path,i.path,i.cloud_phase,i.cloud_version\n                                      FROM icloud_copy_items i JOIN icloud_copies c ON c.id=i.copy_id\n                                      WHERE i.cloud_phase IN ({marks})', CLOUD_IN_PROGRESS).fetchall`, `dict`, [free_bytes](media_manager--icloud_copies.md#symbol-free_bytes), [icloud_volume](media_manager--icloud_copies.md#symbol-icloud_volume), `open_readonly`, [self._batch_local_bytes](media_manager--icloud_copies.md#symbol-ICloudCopies._batch_local_bytes), [self._batch_usage](media_manager--icloud_copies.md#symbol-ICloudCopies._batch_usage), [self.source_volume](media_manager--icloud_copies.md#symbol-ICloudCopies.source_volume), `self.storage.connect`, `self.storage.refresh`, `sum`, `volume.get`, `volumes.get`.

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `dict(volume=icloud_volume(available), copies=copies, batch=batch)`


<a id="symbol-ICloudCopies.pause_copy"></a>

## `ICloudCopies.pause_copy`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.pause_copy`

Ставит привязку на постоянную паузу и останавливает текущую передачу. Изменяет SQLite-таблицы: icloud_copies.

```python
def pause_copy(self, copy_id)
```

Прямые выражения вызова: `dict`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), [self._update_copy](media_manager--icloud_copies.md#symbol-ICloudCopies._update_copy), `self._wake.set`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `dict(id=copy_id)`


<a id="symbol-ICloudCopies.source_volume"></a>

## `ICloudCopies.source_volume`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.source_volume`

Возвращает доступный путь облачного источника для просмотра и подсчёта. Явно отклоняет недопустимое состояние через OSError.

```python
def source_volume(self)
```

Прямые выражения вызова: `OSError`, `dict`, `self.root.is_dir`, `str`.

Явные `raise`:

- `OSError('iCloud Drive недоступен на M4')`

Выражения возврата (ветви, без исполнения):

- `dict(mount_path=str(self.root))`


<a id="symbol-ICloudCopies.start"></a>

## `ICloudCopies.start`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.start`

Запускает обработку активных привязок, в том числе после перезапуска Core. Обновляет состояние объекта: _thread.

```python
def start(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._stop.clear`, `self._thread.is_alive`, `self._thread.start`, `threading.Thread`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ICloudCopies.start_copy"></a>

## `ICloudCopies.start_copy`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.start_copy`

Включает передачу или начинает новый проход после завершения предыдущего. Изменяет SQLite-таблицы: icloud_copies, icloud_copy_items.

```python
def start_copy(self, copy_id)
```

SQLite: чтение `icloud_copy_items`; запись/DDL `icloud_copy_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT 1 FROM icloud_copy_items WHERE copy_id=? LIMIT 1', (copy_id,)).fetchone`, `dict`, `now`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), [self._update_copy](media_manager--icloud_copies.md#symbol-ICloudCopies._update_copy), `self._wake.set`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `dict(id=copy_id)`


<a id="symbol-ICloudCopies.unbind"></a>

## `ICloudCopies.unbind`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudCopies.unbind`

Удаляет остановленную привязку после выхода исполнителя из текущего файла. Изменяет SQLite-таблицы: icloud_copies, icloud_copy_items.

```python
def unbind(self, copy_id)
```

SQLite: чтение `icloud_copies`, `icloud_copy_items`; запись/DDL `icloud_copies`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute("SELECT 1 FROM icloud_copy_items WHERE copy_id=? AND cloud_phase IN ('reserved','requested','external','copying','evict_pending')", (copy_id,)).fetchone`, `db.execute('SELECT 1 FROM icloud_copies WHERE source_link_id=? LIMIT 1', (copy_id,)).fetchone`, `db.execute('SELECT 1 FROM icloud_copy_items WHERE copy_id=? AND staging IS NOT NULL', (copy_id,)).fetchone`, `dict`, [self._copy](media_manager--icloud_copies.md#symbol-ICloudCopies._copy), `self.storage.connect`.

Явные `raise`:

- `ValueError('Сначала поставь копирование на паузу и дождись остановки')`
- `ValueError('Сначала отвяжи копии, которые используют это звено как источник')`
- `ValueError('Возобнови копирование, чтобы обработать незавершённую запись')`
- `ValueError('Возобнови копирование, чтобы закончить обработку запрошенных загрузок iCloud')`

Выражения возврата (ветви, без исполнения):

- `dict(id=copy_id)`


<a id="symbol-ICloudReader"></a>

## `ICloudReader`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudReader`

Запрашивает загрузку и ограничивает ожидание данных отдельного процесса чтения. Зависимость конструктора: build_directory.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `executable`.

Именованные методы: `__init__`, `command`, `stream`, `residency`.

<a id="symbol-ICloudReader.__init__"></a>

## `ICloudReader.__init__`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudReader.__init__`

Запоминает расположение исполняемого помощника Core. Обновляет состояние объекта: executable.

```python
def __init__(self, build_directory)
```

Присваивания полям `self`: `executable`.

Прямые выражения вызова: `Path`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ICloudReader.command"></a>

## `ICloudReader.command`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudReader.command`

Собирает помощник macOS при первом запуске или изменении нативного кода. Явно отклоняет недопустимое состояние через OSError.

```python
def command(self)
```

Прямые выражения вызова: `OSError`, `Path`, `Path(__file__).with_name`, `dict`, `result.stderr.strip`, `self.executable.exists`, `self.executable.parent.mkdir`, `self.executable.stat`, `self.executable.with_name`, `source.stat`, `str`, `subprocess.run`, `temporary.replace`, `temporary.unlink`, `uuid4`.

Явные `raise`:

- `OSError(result.stderr.strip() or 'Не удалось собрать помощник iCloud')`

Выражения возврата (ветви, без исполнения):

- `str(self.executable)`


<a id="symbol-ICloudReader.residency"></a>

## `ICloudReader.residency`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudReader.residency`

Вызывает одну явную операцию macOS над подтверждённой версией файла. Отдельно возвращает отказ без изменения файла и временную ошибку.

```python
def residency(self, parent, name, operation, version)
```

Прямые выражения вызова: `OSError`, `divmod`, `map`, `result.stderr.strip`, [self.command](media_manager--icloud_copies.md#symbol-ICloudReader.command), `str`, `subprocess.run`.

Явные `raise`:

- `OSError(message)`

Выражения возврата (ветви, без исполнения):

- `(True, detail)`
- `(False, message)`


<a id="symbol-ICloudReader.stream"></a>

## `ICloudReader.stream`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `ICloudReader.stream`

Передаёт блоки файла до конца, паузы или тайм-аута без данных. Сохраняет исходную ошибку помощника для журнала повторных попыток.

```python
def stream(self, parent, name, check)
```

Прямые выражения вызова: `OSError`, `TimeoutError`, `check`, `os.read`, `process.kill`, `process.poll`, `process.stderr.read`, `process.stderr.read().decode`, `process.stdout.fileno`, `process.wait`, `select.select`, [self.command](media_manager--icloud_copies.md#symbol-ICloudReader.command), `str`, `subprocess.Popen`, `time.monotonic`.

Явные `raise`:

- `TimeoutError('iCloud слишком долго не передаёт данные')`
- `OSError(process.stderr.read().decode(errors='replace') or 'Ошибка чтения файла iCloud')`

Перехватываемые типы: `subprocess.TimeoutExpired`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-cloud_dataless"></a>

## `cloud_dataless`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `cloud_dataless`

Читает системный признак отсутствующего содержимого из метаданных файла. Использует значение Darwin SF_DATALESS из sys/stat.h.

```python
def cloud_dataless(info)
```

Прямые выражения вызова: `bool`, `getattr`.

Выражения возврата (ветви, без исполнения):

- `bool(getattr(info, 'st_flags', 0) & 1073741824)`


<a id="symbol-cloud_version"></a>

## `cloud_version`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `cloud_version`

Собирает идентичность, размер и mtime файла для дальнейшей проверки. Не использует ctime, который может измениться после загрузки из облака.

```python
def cloud_version(info)
```

Выражения возврата (ветви, без исполнения):

- `[info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]`


<a id="symbol-free_bytes"></a>

## `free_bytes`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `free_bytes`

Возвращает доступное место для новых загрузок на системном диске. Использует метаданные файловой системы открытого каталога.

```python
def free_bytes(descriptor)
```

Прямые выражения вызова: `os.fstatvfs`.

Выражения возврата (ветви, без исполнения):

- `capacity.f_bavail * capacity.f_frsize`


<a id="symbol-icloud_volume"></a>

## `icloud_volume`

[media_manager/icloud_copies.py](../../media_manager/icloud_copies.py) · `icloud_volume`

Возвращает виртуальный том iCloud Drive для двухпанельного дерева. Поля результата: id, name, display_name, kind, availability, identity_status, mounted, mount_path.

```python
def icloud_volume(available)
```

Прямые выражения вызова: `dict`.

Выражения возврата (ветви, без исполнения):

- `dict(id=ICLOUD_VOLUME_ID, name='iCloud Drive', display_name='iCloud Drive', kind='icloud', availability='online' if available else 'offline', identity_status='virtual', mounted=False, mount_path=None)`
