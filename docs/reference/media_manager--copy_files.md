# Копирование отсутствующего: `media_manager/copy_files.py`

Составляет неизменяемый план отсутствующих элементов по завершённой сверке, исполняет его без замены существующих путей и хранит незавершённые прямые записи.

[Исходный модуль](../../media_manager/copy_files.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [app.py](app.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/photos_originals.py](media_manager--photos_originals.md).
Тестовые модули с прямым импортом: [tests/test_copy_files.py](../../tests/test_copy_files.py#L11), [tests/test_copy_number_release.py](../../tests/test_copy_number_release.py#L13), [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L12).

## Оглавление определений

- [CopyStopped](#symbol-copystopped) — Обозначает кооперативную остановку копирования отсутствующих элементов.
- [DirectCopyRequired](#symbol-directcopyrequired) — Запрашивает переход к исключительному созданию конечного файла на SMB.
- [object_id](#symbol-object-id) — Возвращает сериализуемую пару device/inode файлового объекта.
- [publish_exclusive](#symbol-publish-exclusive) — Атомарно публикует подготовленный файл с запретом замены существующего пути.
- [destination_directory](#symbol-destination-directory) — Открывает или создаёт дочерние каталоги внутри проверенного корня копии.
- [MissingCopyCatalog](#symbol-missingcopycatalog) — Ведёт планы, исполнение и журнал создания отсутствующих копий.
- [MissingCopyCatalog.__init__](#symbol-missingcopycatalog---init--) — Инициализирует MissingCopyCatalog и его рабочее состояние.
- [MissingCopyCatalog.busy](#symbol-missingcopycatalog-busy) — Сообщает, работает ли поток копирования отсутствующих элементов.
- [MissingCopyCatalog._update](#symbol-missingcopycatalog--update) — Сохраняет поля и время изменения операции копирования.
- [MissingCopyCatalog.job](#symbol-missingcopycatalog-job) — Возвращает план, прогресс и количество незавершённых файлов операции.
- [MissingCopyCatalog.incomplete](#symbol-missingcopycatalog-incomplete) — Собирает незавершённые прямые записи выбранной копии.
- [MissingCopyCatalog.latest](#symbol-missingcopycatalog-latest) — Возвращает последнюю операцию копирования по отчёту сверки.
- [MissingCopyCatalog.items](#symbol-missingcopycatalog-items) — Возвращает страницу элементов зафиксированного плана копирования.
- [MissingCopyCatalog._volumes](#symbol-missingcopycatalog--volumes) — Проверяет доступность и идентичность томов обеих сторон операции.
- [MissingCopyCatalog._roots](#symbol-missingcopycatalog--roots) — Открывает корни обеих областей и проверяет отсутствие пересечения.
- [MissingCopyCatalog._binding](#symbol-missingcopycatalog--binding) — Проверяет соответствие текущей связи областям сохранённого плана.
- [MissingCopyCatalog.candidates](#symbol-missingcopycatalog-candidates) — Выбирает отсутствующие в копии элементы из завершённой файловой сверки.
- [MissingCopyCatalog.plan](#symbol-missingcopycatalog-plan) — Фиксирует состав копирования, версии исходников и идентичность корней.
- [MissingCopyCatalog.start](#symbol-missingcopycatalog-start) — Запускает подтверждённый план после проверки связи, томов и состояния служб.
- [MissingCopyCatalog._validate](#symbol-missingcopycatalog--validate) — Повторно проверяет связь и идентичность корней во время копирования.
- [MissingCopyCatalog.stop](#symbol-missingcopycatalog-stop) — Запрашивает остановку операции после текущего шага.
- [MissingCopyCatalog.close](#symbol-missingcopycatalog-close) — Останавливает копирование при завершении Core и запрещает финальную пересверку.
- [MissingCopyCatalog._check](#symbol-missingcopycatalog--check) — Прерывает текущий шаг при установленном флаге остановки.
- [MissingCopyCatalog._item](#symbol-missingcopycatalog--item) — Обновляет результат отдельного элемента плана копирования.
- [MissingCopyCatalog._cleanup_staging](#symbol-missingcopycatalog--cleanup-staging) — Удаляет только собственные подтверждённые промежуточные файлы операции.
- [MissingCopyCatalog._copy_file](#symbol-missingcopycatalog--copy-file) — Пробует атомарную публикацию файла и при необходимости включает прямую запись.
- [MissingCopyCatalog._write_file](#symbol-missingcopycatalog--write-file) — Копирует файл с проверками источника, назначения и исключительного создания.
- [MissingCopyCatalog.run](#symbol-missingcopycatalog-run) — Исполняет элементы плана и создаёт итоговую сверку по имени и размеру.

<a id="symbol-copystopped"></a>

## `CopyStopped`

[media_manager/copy_files.py:23](../../media_manager/copy_files.py#L23)

Обозначает кооперативную остановку копирования отсутствующих элементов. Базовые типы: Exception.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-directcopyrequired"></a>

## `DirectCopyRequired`

[media_manager/copy_files.py:29](../../media_manager/copy_files.py#L29)

Запрашивает переход к исключительному созданию конечного файла на SMB. Базовые типы: Exception.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-object-id"></a>

## `object_id`

[media_manager/copy_files.py:35](../../media_manager/copy_files.py#L35)

Возвращает сериализуемую пару device/inode файлового объекта. Использует fingerprint.

```python
def object_id(info)
```

Прямые выражения вызова: `fingerprint`.

Выражения возврата (ветви, без исполнения):

- `{key: data[key] for key in ('device', 'inode')}`


<a id="symbol-publish-exclusive"></a>

## `publish_exclusive`

[media_manager/copy_files.py:42](../../media_manager/copy_files.py#L42)

Атомарно публикует подготовленный файл с запретом замены существующего пути. Явно отклоняет недопустимое состояние через OSError.

```python
def publish_exclusive(parent, temporary, name)
```

Прямые выражения вызова: `OSError`, `ctypes.CDLL`, `ctypes.get_errno`, `function`, `getattr`, `os.fsencode`, `os.link`, `os.strerror`, `os.unlink`.

Явные `raise`:

- `OSError(code, os.strerror(code), name)`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-destination-directory"></a>

## `destination_directory`

[media_manager/copy_files.py:61](../../media_manager/copy_files.py#L61)

Открывает или создаёт дочерние каталоги внутри проверенного корня копии. Явно отклоняет недопустимое состояние через OSError.

```python
def destination_directory(volume, scope, path, *, create=False)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `OSError`, `PurePosixPath`, `descriptors.append`, `open_readonly`, `os.close`, `os.fstat`, `os.mkdir`, `os.open`, `relative_path`, `reversed`.

Явные `raise`:

- `OSError('Переход на другой том запрещён')`

Перехватываемые типы: `FileExistsError`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-missingcopycatalog"></a>

## `MissingCopyCatalog`

[media_manager/copy_files.py:86](../../media_manager/copy_files.py#L86)

Ведёт планы, исполнение и журнал создания отсутствующих копий. Зависимости конструктора: pairs.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_closing`, `_progress_at`, `_stop`, `_thread`, `pairs`, `storage`.

Именованные методы: `__init__`, `busy`, `_update`, `job`, `incomplete`, `latest`, `items`, `_volumes`, `_roots`, `_binding`, `candidates`, `plan`, `start`, `_validate`, `stop`, `close`, `_check`, `_item`, `_cleanup_staging`, `_copy_file`, `_write_file`, `run`.

<a id="symbol-missingcopycatalog---init--"></a>

## `MissingCopyCatalog.__init__`

[media_manager/copy_files.py:89](../../media_manager/copy_files.py#L89)

Инициализирует MissingCopyCatalog и его рабочее состояние. Изменяет SQLite-таблицы: copy_operation_items, copy_operations.

```python
def __init__(self, pairs)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `copy_operation_items`, `copy_operations`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_closing`, `_progress_at`, `_stop`, `_thread`, `pairs`, `storage`.

Прямые выражения вызова: `db.execute`, `db.executescript`, `now`, `self.storage.connect`, `threading.Event`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog-busy"></a>

## `MissingCopyCatalog.busy`

[media_manager/copy_files.py:122](../../media_manager/copy_files.py#L122)

Сообщает, работает ли поток копирования отсутствующих элементов. Использует self._thread.is_alive.

```python
def busy(self)
```

Прямые выражения вызова: `self._thread.is_alive`.

Выражения возврата (ветви, без исполнения):

- `self._thread is not None and self._thread.is_alive()`


<a id="symbol-missingcopycatalog--update"></a>

## `MissingCopyCatalog._update`

[media_manager/copy_files.py:127](../../media_manager/copy_files.py#L127)

Сохраняет поля и время изменения операции копирования. Изменяет SQLite-таблицы: copy_operations.

```python
def _update(self, operation, **values)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `copy_operations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog-job"></a>

## `MissingCopyCatalog.job`

[media_manager/copy_files.py:135](../../media_manager/copy_files.py#L135)

Возвращает план, прогресс и количество незавершённых файлов операции. Явно отклоняет недопустимое состояние через KeyError.

```python
def job(self, operation)
```

SQLite: чтение `copy_operation_items`, `copy_operations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `bool`, `db.execute`, `db.execute('SELECT * FROM copy_operations WHERE id=?', (operation,)).fetchone`, `dict`, `json.loads`, `json.loads(r['staging']).get`, `result.pop`, `result.update`, `self.storage.connect`, `sum`.

Явные `raise`:

- `KeyError('Копирование не найдено')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-missingcopycatalog-incomplete"></a>

## `MissingCopyCatalog.incomplete`

[media_manager/copy_files.py:149](../../media_manager/copy_files.py#L149)

Собирает незавершённые прямые записи выбранной копии. Читает SQLite-таблицы: copy_operation_items, copy_operations.

```python
def incomplete(self, copy_id)
```

SQLite: чтение `copy_operation_items`, `copy_operations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `(value := json.loads(row['staging'])).get`, `db.execute`, `json.loads`, `result.pop`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-missingcopycatalog-latest"></a>

## `MissingCopyCatalog.latest`

[media_manager/copy_files.py:164](../../media_manager/copy_files.py#L164)

Возвращает последнюю операцию копирования по отчёту сверки. Читает SQLite-таблицы: copy_operations.

```python
def latest(self, report)
```

SQLite: чтение `copy_operations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT id FROM copy_operations WHERE report_id=? OR verification_id=?\n                                ORDER BY created_at DESC LIMIT 1', (report, report)).fetchone`, [self.job](../../media_manager/copy_files.py#L135), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `self.job(row[0]) if row else None`


<a id="symbol-missingcopycatalog-items"></a>

## `MissingCopyCatalog.items`

[media_manager/copy_files.py:172](../../media_manager/copy_files.py#L172)

Возвращает страницу элементов зафиксированного плана копирования. Поля результата: items, total, offset.

```python
def items(self, operation, offset=0, limit=200)
```

SQLite: чтение `copy_operation_items`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `dict`, `json.loads`, `json.loads(r['staging']).get`, [self.job](../../media_manager/copy_files.py#L135), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `{'items': rows, 'total': job['total_files'] + job['total_directories'], 'offset': offset}`


<a id="symbol-missingcopycatalog--volumes"></a>

## `MissingCopyCatalog._volumes`

[media_manager/copy_files.py:183](../../media_manager/copy_files.py#L183)

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


<a id="symbol-missingcopycatalog--roots"></a>

## `MissingCopyCatalog._roots`

[media_manager/copy_files.py:198](../../media_manager/copy_files.py#L198)

Открывает корни обеих областей и проверяет отсутствие пересечения. Явно отклоняет недопустимое состояние через ValueError.

```python
def _roots(scopes, volumes)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `ExitStack`, `ValueError`, [object_id](../../media_manager/copy_files.py#L35), `open_readonly`, `os.close`, `os.dup`, `os.fstat`, `os.open`, `scopes.items`, `stack.enter_context`.

Явные `raise`:

- `ValueError('Основная папка и копия пересекаются.')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-missingcopycatalog--binding"></a>

## `MissingCopyCatalog._binding`

[media_manager/copy_files.py:225](../../media_manager/copy_files.py#L225)

Проверяет соответствие текущей связи областям сохранённого плана. Явно отклоняет недопустимое состояние через ValueError.

```python
def _binding(self, job)
```

Прямые выражения вызова: `ValueError`, `any`, `self.pairs._pair`.

Явные `raise`:

- `ValueError('Связь папок изменилась. Заново сверь файлы.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog-candidates"></a>

## `MissingCopyCatalog.candidates`

[media_manager/copy_files.py:233](../../media_manager/copy_files.py#L233)

Выбирает отсутствующие в копии элементы из завершённой файловой сверки. Читает SQLite-таблицы: paired_rows.

```python
def candidates(self, report_id)
```

SQLite: чтение `paired_rows`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `any`, `db.execute`, `dict`, `items.append`, `json.loads`, `relative_path`, `self.storage.connect`, `source.get`, `str`.

Выражения возврата (ветви, без исполнения):

- `items`


<a id="symbol-missingcopycatalog-plan"></a>

## `MissingCopyCatalog.plan`

[media_manager/copy_files.py:251](../../media_manager/copy_files.py#L251)

Фиксирует состав копирования, версии исходников и идентичность корней. Изменяет SQLite-таблицы: copy_operation_items, copy_operations.

```python
def plan(self, report_id)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `copy_operation_items`, `copy_operations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.executemany`, `enumerate`, `fingerprint`, `item['source'].update`, `json.dumps`, `now`, `open_readonly`, `os.fstat`, [self._binding](../../media_manager/copy_files.py#L225), [self._roots](../../media_manager/copy_files.py#L198), [self._volumes](../../media_manager/copy_files.py#L183), [self.candidates](../../media_manager/copy_files.py#L233), [self.job](../../media_manager/copy_files.py#L135), `self.pairs._idle`, `self.pairs.job`, `self.storage.connect`, `sum`, `uuid4`, `v.get`, `volumes.items`.

Явные `raise`:

- `ValueError('Сначала заверши сверку файлов.')`
- `ValueError('Отсутствующих элементов для копирования нет.')`

Выражения возврата (ветви, без исполнения):

- `self.job(operation)`


<a id="symbol-missingcopycatalog-start"></a>

## `MissingCopyCatalog.start`

[media_manager/copy_files.py:288](../../media_manager/copy_files.py#L288)

Запускает подтверждённый план после проверки связи, томов и состояния служб. Явно отклоняет недопустимое состояние через ValueError.

```python
def start(self, operation, *, background=True)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `ValueError`, [self._binding](../../media_manager/copy_files.py#L225), `self._stop.clear`, `self._thread.start`, [self._update](../../media_manager/copy_files.py#L127), [self._validate](../../media_manager/copy_files.py#L306), [self._volumes](../../media_manager/copy_files.py#L183), [self.job](../../media_manager/copy_files.py#L135), `self.pairs._idle`, `threading.Thread`.

Явные `raise`:

- `ValueError('Этот план уже запускался. Заново сверь файлы перед повтором.')`

Выражения возврата (ветви, без исполнения):

- `self.job(operation)`


<a id="symbol-missingcopycatalog--validate"></a>

## `MissingCopyCatalog._validate`

[media_manager/copy_files.py:306](../../media_manager/copy_files.py#L306)

Повторно проверяет связь и идентичность корней во время копирования. Явно отклоняет недопустимое состояние через OSError.

```python
def _validate(self, job, volumes)
```

Прямые выражения вызова: `OSError`, `any`, `job['volumes'][side].get`, [self._binding](../../media_manager/copy_files.py#L225), [self._roots](../../media_manager/copy_files.py#L198), `volume.get`, `volumes.items`.

Явные `raise`:

- `OSError('Основная папка или папка копии была заменена. Заново сверь файлы.')`
- `OSError('Том изменился после подготовки плана. Заново сверь файлы.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog-stop"></a>

## `MissingCopyCatalog.stop`

[media_manager/copy_files.py:316](../../media_manager/copy_files.py#L316)

Запрашивает остановку операции после текущего шага. Использует self._stop.set, self._update, self.job.

```python
def stop(self, operation)
```

Прямые выражения вызова: `self._stop.set`, [self._update](../../media_manager/copy_files.py#L127), [self.job](../../media_manager/copy_files.py#L135).

Выражения возврата (ветви, без исполнения):

- `self.job(operation)`


<a id="symbol-missingcopycatalog-close"></a>

## `MissingCopyCatalog.close`

[media_manager/copy_files.py:325](../../media_manager/copy_files.py#L325)

Останавливает копирование при завершении Core и запрещает финальную пересверку. Обновляет состояние объекта: _closing.

```python
def close(self)
```

Присваивания полям `self`: `_closing`.

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog--check"></a>

## `MissingCopyCatalog._check`

[media_manager/copy_files.py:333](../../media_manager/copy_files.py#L333)

Прерывает текущий шаг при установленном флаге остановки. Явно отклоняет недопустимое состояние через CopyStopped.

```python
def _check(self)
```

Прямые выражения вызова: [CopyStopped](../../media_manager/copy_files.py#L23), `self._stop.is_set`.

Явные `raise`:

- `CopyStopped()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog--item"></a>

## `MissingCopyCatalog._item`

[media_manager/copy_files.py:339](../../media_manager/copy_files.py#L339)

Обновляет результат отдельного элемента плана копирования. Изменяет SQLite-таблицы: copy_operation_items.

```python
def _item(self, operation, path, **values)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `copy_operation_items`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog--cleanup-staging"></a>

## `MissingCopyCatalog._cleanup_staging`

[media_manager/copy_files.py:346](../../media_manager/copy_files.py#L346)

Удаляет только собственные подтверждённые промежуточные файлы операции. Явно отклоняет недопустимое состояние через OSError.

```python
def _cleanup_staging(self, job, volumes)
```

SQLite: чтение `copy_operation_items`, `copy_operations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `OSError`, `PurePosixPath`, `db.execute`, [destination_directory](../../media_manager/copy_files.py#L61), `json.loads`, `list`, [object_id](../../media_manager/copy_files.py#L35), `os.stat`, `os.unlink`, [self._item](../../media_manager/copy_files.py#L339), `self.storage.connect`, `staging.get`, `stat.S_ISREG`, `str`.

Явные `raise`:

- `OSError('Промежуточный файл был заменён; он оставлен на диске.')`

Перехватываемые типы: `FileNotFoundError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-missingcopycatalog--copy-file"></a>

## `MissingCopyCatalog._copy_file`

[media_manager/copy_files.py:368](../../media_manager/copy_files.py#L368)

Пробует атомарную публикацию файла и при необходимости включает прямую запись. Обрабатывает ошибки: DirectCopyRequired.

```python
def _copy_file(self, job, item, volumes, completed_bytes)
```

Прямые выражения вызова: [self._write_file](../../media_manager/copy_files.py#L377), `volumes['right'].get`.

Перехватываемые типы: `DirectCopyRequired`.

Выражения возврата (ветви, без исполнения):

- `self._write_file(job, item, volumes, completed_bytes, direct=direct)`
- `self._write_file(job, item, volumes, completed_bytes, direct=True)`


<a id="symbol-missingcopycatalog--write-file"></a>

## `MissingCopyCatalog._write_file`

[media_manager/copy_files.py:377](../../media_manager/copy_files.py#L377)

Копирует файл с проверками источника, назначения и исключительного создания. Явно отклоняет недопустимое состояние через DirectCopyRequired, OSError.

```python
def _write_file(self, job, item, volumes, completed_bytes, *, direct)
```

Присваивания полям `self`: `_progress_at`.

Прямые выражения вызова: [DirectCopyRequired](../../media_manager/copy_files.py#L29), `OSError`, `PurePosixPath`, `any`, [destination_directory](../../media_manager/copy_files.py#L61), `expected.items`, `fingerprint`, `json.dumps`, `len`, `memoryview`, [object_id](../../media_manager/copy_files.py#L35), `open_readonly`, `os.close`, `os.fchmod`, `os.fstat`, `os.fstatvfs`, `os.fsync`, `os.open`, `os.read`, `os.stat`, `os.unlink`, `os.utime`, `os.write`, [publish_exclusive](../../media_manager/copy_files.py#L42), [self._check](../../media_manager/copy_files.py#L333), [self._item](../../media_manager/copy_files.py#L339), [self._update](../../media_manager/copy_files.py#L127), [self._validate](../../media_manager/copy_files.py#L306), `source.get`, `str`, `time.monotonic`, `uuid4`.

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


<a id="symbol-missingcopycatalog-run"></a>

## `MissingCopyCatalog.run`

[media_manager/copy_files.py:466](../../media_manager/copy_files.py#L466)

Исполняет элементы плана и создаёт итоговую сверку по имени и размеру. Обновляет состояние объекта: _thread.

```python
def run(self, operation, *, recheck=True)
```

SQLite: чтение `copy_operation_items`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `db.execute`, [destination_directory](../../media_manager/copy_files.py#L61), `dict`, `json.loads`, `open_readonly`, [self._check](../../media_manager/copy_files.py#L333), [self._cleanup_staging](../../media_manager/copy_files.py#L346), [self._copy_file](../../media_manager/copy_files.py#L368), [self._item](../../media_manager/copy_files.py#L339), [self._update](../../media_manager/copy_files.py#L127), [self._validate](../../media_manager/copy_files.py#L306), [self._volumes](../../media_manager/copy_files.py#L183), [self.job](../../media_manager/copy_files.py#L135), `self.pairs.create`, `self.storage.connect`, `str`.

Перехватываемые типы: `FileNotFoundError`, `OSError`, `CopyStopped`, `Exception`, `(KeyError, ValueError, OSError)`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
