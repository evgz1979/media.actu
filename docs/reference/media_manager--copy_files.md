# Копирование отсутствующего: `media_manager/copy_files.py`

Составляет неизменяемый план отсутствующих элементов по завершённой сверке, исполняет его без замены существующих путей и хранит незавершённые прямые записи.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/copy_files.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [app.py](app.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/photos_originals.py](media_manager--photos_originals.md).
Тестовые модули с прямым импортом: [tests/test_copy_files.py](tests.md#module-tests.test_copy_files), [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_folder_markers.py](tests.md#module-tests.test_folder_markers).

## Оглавление определений

- [CopyStopped](#symbol-CopyStopped) — Обозначает кооперативную остановку копирования отсутствующих элементов.
- [DirectCopyRequired](#symbol-DirectCopyRequired) — Запрашивает переход к исключительному созданию конечного файла на SMB.
- [MissingCopyCatalog](#symbol-MissingCopyCatalog) — Ведёт планы, исполнение и журнал создания отсутствующих копий.
- [MissingCopyCatalog.__init__](#symbol-MissingCopyCatalog.__init__) — Инициализирует MissingCopyCatalog и его рабочее состояние.
- [MissingCopyCatalog._binding](#symbol-MissingCopyCatalog._binding) — Проверяет соответствие текущей связи областям сохранённого плана.
- [MissingCopyCatalog._check](#symbol-MissingCopyCatalog._check) — Прерывает текущий шаг при установленном флаге остановки.
- [MissingCopyCatalog._cleanup_staging](#symbol-MissingCopyCatalog._cleanup_staging) — Удаляет только собственные подтверждённые промежуточные файлы операции.
- [MissingCopyCatalog._copy_file](#symbol-MissingCopyCatalog._copy_file) — Пробует атомарную публикацию файла и при необходимости включает прямую запись.
- [MissingCopyCatalog._item](#symbol-MissingCopyCatalog._item) — Обновляет результат отдельного элемента плана копирования.
- [MissingCopyCatalog._roots](#symbol-MissingCopyCatalog._roots) — Открывает корни обеих областей и проверяет отсутствие пересечения.
- [MissingCopyCatalog._update](#symbol-MissingCopyCatalog._update) — Сохраняет поля и время изменения операции копирования.
- [MissingCopyCatalog._validate](#symbol-MissingCopyCatalog._validate) — Повторно проверяет связь и идентичность корней во время копирования.
- [MissingCopyCatalog._volumes](#symbol-MissingCopyCatalog._volumes) — Проверяет доступность и идентичность томов обеих сторон операции.
- [MissingCopyCatalog._write_file](#symbol-MissingCopyCatalog._write_file) — Копирует файл с проверками источника, назначения и исключительного создания.
- [MissingCopyCatalog.busy](#symbol-MissingCopyCatalog.busy) — Сообщает, работает ли поток копирования отсутствующих элементов.
- [MissingCopyCatalog.candidates](#symbol-MissingCopyCatalog.candidates) — Выбирает отсутствующие в копии элементы из завершённой файловой сверки.
- [MissingCopyCatalog.close](#symbol-MissingCopyCatalog.close) — Останавливает копирование при завершении Core и запрещает финальную пересверку.
- [MissingCopyCatalog.incomplete](#symbol-MissingCopyCatalog.incomplete) — Собирает незавершённые прямые записи выбранной копии.
- [MissingCopyCatalog.items](#symbol-MissingCopyCatalog.items) — Возвращает страницу элементов зафиксированного плана копирования.
- [MissingCopyCatalog.job](#symbol-MissingCopyCatalog.job) — Возвращает план, прогресс и количество незавершённых файлов операции.
- [MissingCopyCatalog.latest](#symbol-MissingCopyCatalog.latest) — Возвращает последнюю операцию копирования по отчёту сверки.
- [MissingCopyCatalog.plan](#symbol-MissingCopyCatalog.plan) — Фиксирует состав копирования, версии исходников и идентичность корней.
- [MissingCopyCatalog.run](#symbol-MissingCopyCatalog.run) — Исполняет элементы плана и создаёт итоговую сверку по имени и размеру.
- [MissingCopyCatalog.start](#symbol-MissingCopyCatalog.start) — Запускает подтверждённый план после проверки связи, томов и состояния служб.
- [MissingCopyCatalog.stop](#symbol-MissingCopyCatalog.stop) — Запрашивает остановку операции после текущего шага.
- [destination_directory](#symbol-destination_directory) — Открывает или создаёт дочерние каталоги внутри проверенного корня копии.
- [object_id](#symbol-object_id) — Возвращает сериализуемую пару device/inode файлового объекта.
- [publish_exclusive](#symbol-publish_exclusive) — Атомарно публикует подготовленный файл с запретом замены существующего пути.

<a id="symbol-CopyStopped"></a>

## `CopyStopped`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `CopyStopped`

Обозначает кооперативную остановку копирования отсутствующих элементов. Базовые типы: Exception.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет.

<a id="symbol-DirectCopyRequired"></a>

## `DirectCopyRequired`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `DirectCopyRequired`

Запрашивает переход к исключительному созданию конечного файла на SMB. Базовые типы: Exception.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет.

<a id="symbol-MissingCopyCatalog"></a>

## `MissingCopyCatalog`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog`

Ведёт планы, исполнение и журнал создания отсутствующих копий. Зависимости конструктора: pairs.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_closing`, `_progress_at`, `_stop`, `_thread`, `pairs`, `storage`.

Именованные методы: `__init__`, `busy`, `_update`, `job`, `incomplete`, `latest`, `items`, `_volumes`, `_roots`, `_binding`, `candidates`, `plan`, `start`, `_validate`, `stop`, `close`, `_check`, `_item`, `_cleanup_staging`, `_copy_file`, `_write_file`, `run`.

<a id="symbol-MissingCopyCatalog.__init__"></a>

## `MissingCopyCatalog.__init__`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.__init__`

Инициализирует MissingCopyCatalog и его рабочее состояние. Изменяет SQLite-таблицы: copy_operation_items, copy_operations.

```python
def __init__(self, pairs)
```

SQLite: чтение не найдено; запись/DDL `copy_operation_items`, `copy_operations`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_closing`, `_progress_at`, `_stop`, `_thread`, `pairs`, `storage`.

Прямые выражения вызова: `db.execute`, `db.executescript`, `now`, `self.storage.connect`, `threading.Event`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._binding"></a>

## `MissingCopyCatalog._binding`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._binding`

Проверяет соответствие текущей связи областям сохранённого плана. Явно отклоняет недопустимое состояние через ValueError.

```python
def _binding(self, job)
```

Прямые выражения вызова: `ValueError`, `any`, `self.pairs._pair`.

Явные `raise`:

- `ValueError('Связь папок изменилась. Заново сверь файлы.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._check"></a>

## `MissingCopyCatalog._check`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._check`

Прерывает текущий шаг при установленном флаге остановки. Явно отклоняет недопустимое состояние через CopyStopped.

```python
def _check(self)
```

Прямые выражения вызова: [CopyStopped](media_manager--copy_files.md#symbol-CopyStopped), `self._stop.is_set`.

Явные `raise`:

- `CopyStopped()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._cleanup_staging"></a>

## `MissingCopyCatalog._cleanup_staging`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._cleanup_staging`

Удаляет только собственные подтверждённые промежуточные файлы операции. Явно отклоняет недопустимое состояние через OSError.

```python
def _cleanup_staging(self, job, volumes)
```

SQLite: чтение `copy_operation_items`, `copy_operations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `OSError`, `PurePosixPath`, `db.execute`, [destination_directory](media_manager--copy_files.md#symbol-destination_directory), `json.loads`, `list`, [object_id](media_manager--copy_files.md#symbol-object_id), `os.stat`, `os.unlink`, [self._item](media_manager--copy_files.md#symbol-MissingCopyCatalog._item), `self.storage.connect`, `staging.get`, `stat.S_ISREG`, `str`.

Явные `raise`:

- `OSError('Промежуточный файл был заменён; он оставлен на диске.')`

Перехватываемые типы: `FileNotFoundError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._copy_file"></a>

## `MissingCopyCatalog._copy_file`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._copy_file`

Пробует атомарную публикацию файла и при необходимости включает прямую запись. Обрабатывает ошибки: DirectCopyRequired.

```python
def _copy_file(self, job, item, volumes, completed_bytes)
```

Прямые выражения вызова: [self._write_file](media_manager--copy_files.md#symbol-MissingCopyCatalog._write_file), `volumes['right'].get`.

Перехватываемые типы: `DirectCopyRequired`.

Выражения возврата (ветви, без исполнения):

- `self._write_file(job, item, volumes, completed_bytes, direct=direct)`
- `self._write_file(job, item, volumes, completed_bytes, direct=True)`


<a id="symbol-MissingCopyCatalog._item"></a>

## `MissingCopyCatalog._item`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._item`

Обновляет результат отдельного элемента плана копирования. Изменяет SQLite-таблицы: copy_operation_items.

```python
def _item(self, operation, path, **values)
```

SQLite: чтение не найдено; запись/DDL `copy_operation_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._roots"></a>

## `MissingCopyCatalog._roots`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._roots`

Открывает корни обеих областей и проверяет отсутствие пересечения. Явно отклоняет недопустимое состояние через ValueError.

```python
def _roots(scopes, volumes)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `ExitStack`, `ValueError`, [object_id](media_manager--copy_files.md#symbol-object_id), `open_readonly`, `os.close`, `os.dup`, `os.fstat`, `os.open`, `scopes.items`, `stack.enter_context`.

Явные `raise`:

- `ValueError('Основная папка и копия пересекаются.')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-MissingCopyCatalog._update"></a>

## `MissingCopyCatalog._update`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._update`

Сохраняет поля и время изменения операции копирования. Изменяет SQLite-таблицы: copy_operations.

```python
def _update(self, operation, **values)
```

SQLite: чтение не найдено; запись/DDL `copy_operations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._validate"></a>

## `MissingCopyCatalog._validate`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._validate`

Повторно проверяет связь и идентичность корней во время копирования. Явно отклоняет недопустимое состояние через OSError.

```python
def _validate(self, job, volumes)
```

Прямые выражения вызова: `OSError`, `any`, `job['volumes'][side].get`, [self._binding](media_manager--copy_files.md#symbol-MissingCopyCatalog._binding), [self._roots](media_manager--copy_files.md#symbol-MissingCopyCatalog._roots), `volume.get`, `volumes.items`.

Явные `raise`:

- `OSError('Основная папка или папка копии была заменена. Заново сверь файлы.')`
- `OSError('Том изменился после подготовки плана. Заново сверь файлы.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog._volumes"></a>

## `MissingCopyCatalog._volumes`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._volumes`

Проверяет доступность и идентичность томов обеих сторон операции. Явно отклоняет недопустимое состояние через ValueError.

```python
def _volumes(self, scopes)
```

Прямые выражения вызова: `ValueError`, `current.get`, `scopes.items`, `self.storage.refresh`.

Явные `raise`:

- `ValueError('Оба тома должны быть подключены.')`
- `ValueError('Сначала подтверди подключённые диски.')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-MissingCopyCatalog._write_file"></a>

## `MissingCopyCatalog._write_file`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog._write_file`

Копирует файл с проверками источника, назначения и исключительного создания. Явно отклоняет недопустимое состояние через DirectCopyRequired, OSError.

```python
def _write_file(self, job, item, volumes, completed_bytes, *, direct)
```

Присваивания полям `self`: `_progress_at`.

Прямые выражения вызова: [DirectCopyRequired](media_manager--copy_files.md#symbol-DirectCopyRequired), `OSError`, `PurePosixPath`, `any`, [destination_directory](media_manager--copy_files.md#symbol-destination_directory), `expected.items`, `fingerprint`, `json.dumps`, `len`, `memoryview`, [object_id](media_manager--copy_files.md#symbol-object_id), `open_readonly`, `os.close`, `os.fchmod`, `os.fstat`, `os.fstatvfs`, `os.fsync`, `os.open`, `os.read`, `os.stat`, `os.unlink`, `os.utime`, `os.write`, [publish_exclusive](media_manager--copy_files.md#symbol-publish_exclusive), [self._check](media_manager--copy_files.md#symbol-MissingCopyCatalog._check), [self._item](media_manager--copy_files.md#symbol-MissingCopyCatalog._item), [self._update](media_manager--copy_files.md#symbol-MissingCopyCatalog._update), [self._validate](media_manager--copy_files.md#symbol-MissingCopyCatalog._validate), `source.get`, `str`, `time.monotonic`, `uuid4`.

Явные `raise`:

- `OSError('Исходный файл изменился после сверки. Заново сверь файлы.')`
- `OSError('Недостаточно свободного места в копии')`
- `OSError('Исходный файл вырос во время копирования')`
- `OSError('Не удалось записать файл')`
- `OSError('Исходный файл изменился во время копирования')`
- `OSError('Размер записанного файла не совпал')`
- `OSError('Исходный файл заменён во время копирования')`
- `OSError('Целевая папка заменена во время копирования')`
- `OSError('Промежуточный файл был заменён')`
- `DirectCopyRequired()`

Перехватываемые типы: `FileNotFoundError`, `FileExistsError`, `OSError`.

Выражения возврата (ветви, без исполнения):

- `('skipped', 'Уже существует в копии')`
- `('skipped', 'Уже появился в копии; существующий файл сохранён')`
- `('done', '')`


<a id="symbol-MissingCopyCatalog.busy"></a>

## `MissingCopyCatalog.busy`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.busy`

Сообщает, работает ли поток копирования отсутствующих элементов. Использует self._thread.is_alive.

```python
def busy(self)
```

Прямые выражения вызова: `self._thread.is_alive`.

Выражения возврата (ветви, без исполнения):

- `self._thread is not None and self._thread.is_alive()`


<a id="symbol-MissingCopyCatalog.candidates"></a>

## `MissingCopyCatalog.candidates`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.candidates`

Выбирает отсутствующие в копии элементы из завершённой файловой сверки. Читает SQLite-таблицы: paired_rows.

```python
def candidates(self, report_id)
```

SQLite: чтение `paired_rows`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `any`, `db.execute`, `dict`, `items.append`, `json.loads`, `relative_path`, `self.storage.connect`, `source.get`, `str`.

Выражения возврата (ветви, без исполнения):

- `items`


<a id="symbol-MissingCopyCatalog.close"></a>

## `MissingCopyCatalog.close`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.close`

Останавливает копирование при завершении Core и запрещает финальную пересверку. Обновляет состояние объекта: _closing.

```python
def close(self)
```

Присваивания полям `self`: `_closing`.

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog.incomplete"></a>

## `MissingCopyCatalog.incomplete`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.incomplete`

Собирает незавершённые прямые записи выбранной копии. Читает SQLite-таблицы: copy_operation_items, copy_operations.

```python
def incomplete(self, copy_id)
```

SQLite: чтение `copy_operation_items`, `copy_operations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `(value := json.loads(row['staging'])).get`, `db.execute`, `json.loads`, `result.pop`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-MissingCopyCatalog.items"></a>

## `MissingCopyCatalog.items`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.items`

Возвращает страницу элементов зафиксированного плана копирования. Поля результата: items, total, offset.

```python
def items(self, operation, offset=0, limit=200)
```

SQLite: чтение `copy_operation_items`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `dict`, `json.loads`, `json.loads(r['staging']).get`, [self.job](media_manager--copy_files.md#symbol-MissingCopyCatalog.job), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `{'items': rows, 'total': job['total_files'] + job['total_directories'], 'offset': offset}`


<a id="symbol-MissingCopyCatalog.job"></a>

## `MissingCopyCatalog.job`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.job`

Возвращает план, прогресс и количество незавершённых файлов операции. Явно отклоняет недопустимое состояние через KeyError.

```python
def job(self, operation)
```

SQLite: чтение `copy_operation_items`, `copy_operations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `bool`, `db.execute`, `db.execute('SELECT * FROM copy_operations WHERE id=?', (operation,)).fetchone`, `dict`, `json.loads`, `json.loads(r['staging']).get`, `result.pop`, `result.update`, `self.storage.connect`, `sum`.

Явные `raise`:

- `KeyError('Копирование не найдено')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-MissingCopyCatalog.latest"></a>

## `MissingCopyCatalog.latest`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.latest`

Возвращает последнюю операцию копирования по отчёту сверки. Читает SQLite-таблицы: copy_operations.

```python
def latest(self, report)
```

SQLite: чтение `copy_operations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT id FROM copy_operations WHERE report_id=? OR verification_id=?\n                                ORDER BY created_at DESC LIMIT 1', (report, report)).fetchone`, [self.job](media_manager--copy_files.md#symbol-MissingCopyCatalog.job), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `self.job(row[0]) if row else None`


<a id="symbol-MissingCopyCatalog.plan"></a>

## `MissingCopyCatalog.plan`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.plan`

Фиксирует состав копирования, версии исходников и идентичность корней. Изменяет SQLite-таблицы: copy_operation_items, copy_operations.

```python
def plan(self, report_id)
```

SQLite: чтение не найдено; запись/DDL `copy_operation_items`, `copy_operations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.executemany`, `enumerate`, `fingerprint`, `item['source'].update`, `json.dumps`, `now`, `open_readonly`, `os.fstat`, [self._binding](media_manager--copy_files.md#symbol-MissingCopyCatalog._binding), [self._roots](media_manager--copy_files.md#symbol-MissingCopyCatalog._roots), [self._volumes](media_manager--copy_files.md#symbol-MissingCopyCatalog._volumes), [self.candidates](media_manager--copy_files.md#symbol-MissingCopyCatalog.candidates), [self.job](media_manager--copy_files.md#symbol-MissingCopyCatalog.job), `self.pairs._idle`, `self.pairs.job`, `self.storage.connect`, `sum`, `uuid4`, `v.get`, `volumes.items`.

Явные `raise`:

- `ValueError('Сначала заверши сверку файлов.')`
- `ValueError('Отсутствующих элементов для копирования нет.')`

Выражения возврата (ветви, без исполнения):

- `self.job(operation)`


<a id="symbol-MissingCopyCatalog.run"></a>

## `MissingCopyCatalog.run`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.run`

Исполняет элементы плана и создаёт итоговую сверку по имени и размеру. Обновляет состояние объекта: _thread.

```python
def run(self, operation, *, recheck=True)
```

SQLite: чтение `copy_operation_items`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `db.execute`, [destination_directory](media_manager--copy_files.md#symbol-destination_directory), `dict`, `json.loads`, `open_readonly`, [self._check](media_manager--copy_files.md#symbol-MissingCopyCatalog._check), [self._cleanup_staging](media_manager--copy_files.md#symbol-MissingCopyCatalog._cleanup_staging), [self._copy_file](media_manager--copy_files.md#symbol-MissingCopyCatalog._copy_file), [self._item](media_manager--copy_files.md#symbol-MissingCopyCatalog._item), [self._update](media_manager--copy_files.md#symbol-MissingCopyCatalog._update), [self._validate](media_manager--copy_files.md#symbol-MissingCopyCatalog._validate), [self._volumes](media_manager--copy_files.md#symbol-MissingCopyCatalog._volumes), [self.job](media_manager--copy_files.md#symbol-MissingCopyCatalog.job), `self.pairs.create`, `self.storage.connect`, `str`.

Перехватываемые типы: `FileNotFoundError`, `OSError`, `CopyStopped`, `Exception`, `(KeyError, ValueError, OSError)`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-MissingCopyCatalog.start"></a>

## `MissingCopyCatalog.start`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.start`

Запускает подтверждённый план после проверки связи, томов и состояния служб. Явно отклоняет недопустимое состояние через ValueError.

```python
def start(self, operation, *, background=True)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `ValueError`, [self._binding](media_manager--copy_files.md#symbol-MissingCopyCatalog._binding), `self._stop.clear`, `self._thread.start`, [self._update](media_manager--copy_files.md#symbol-MissingCopyCatalog._update), [self._validate](media_manager--copy_files.md#symbol-MissingCopyCatalog._validate), [self._volumes](media_manager--copy_files.md#symbol-MissingCopyCatalog._volumes), [self.job](media_manager--copy_files.md#symbol-MissingCopyCatalog.job), `self.pairs._idle`, `threading.Thread`.

Явные `raise`:

- `ValueError('Этот план уже запускался. Заново сверь файлы перед повтором.')`

Выражения возврата (ветви, без исполнения):

- `self.job(operation)`


<a id="symbol-MissingCopyCatalog.stop"></a>

## `MissingCopyCatalog.stop`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `MissingCopyCatalog.stop`

Запрашивает остановку операции после текущего шага. Использует self._stop.set, self._update, self.job.

```python
def stop(self, operation)
```

Прямые выражения вызова: `self._stop.set`, [self._update](media_manager--copy_files.md#symbol-MissingCopyCatalog._update), [self.job](media_manager--copy_files.md#symbol-MissingCopyCatalog.job).

Выражения возврата (ветви, без исполнения):

- `self.job(operation)`


<a id="symbol-destination_directory"></a>

## `destination_directory`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `destination_directory`

Открывает или создаёт дочерние каталоги внутри проверенного корня копии. Явно отклоняет недопустимое состояние через OSError.

```python
def destination_directory(volume, scope, path, *, create=False)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `OSError`, `PurePosixPath`, `descriptors.append`, `open_readonly`, `os.close`, `os.fstat`, `os.mkdir`, `os.open`, `relative_path`, `reversed`.

Явные `raise`:

- `OSError('Переход на другой том запрещён')`

Перехватываемые типы: `FileExistsError`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-object_id"></a>

## `object_id`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `object_id`

Возвращает сериализуемую пару device/inode файлового объекта. Использует fingerprint.

```python
def object_id(info)
```

Прямые выражения вызова: `fingerprint`.

Выражения возврата (ветви, без исполнения):

- `{key: data[key] for key in ('device', 'inode')}`


<a id="symbol-publish_exclusive"></a>

## `publish_exclusive`

[media_manager/copy_files.py](../../media_manager/copy_files.py) · `publish_exclusive`

Атомарно публикует подготовленный файл с запретом замены существующего пути. Явно отклоняет недопустимое состояние через OSError.

```python
def publish_exclusive(parent, temporary, name)
```

Прямые выражения вызова: `OSError`, `ctypes.CDLL`, `ctypes.get_errno`, `function`, `getattr`, `os.fsencode`, `os.link`, `os.strerror`, `os.unlink`.

Явные `raise`:

- `OSError(code, os.strerror(code), name)`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
