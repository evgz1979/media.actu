# Учёт основных папок и копий: `media_manager/copies.py`

Описывает наборы папок, нумерацию, отключение, освобождение номеров и источники копирования. Сам каталог не переносит пользовательские файлы, но ставит запись маркеров в постоянную очередь.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/copies.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/folder_markers.py](media_manager--folder_markers.md).
Импортируется модулями: [app.py](app.md), [copy_groups_ui.py](copy_groups_ui.md), [media_manager/storage.py](media_manager--storage.md).
Тестовые модули с прямым импортом: [tests/test_copies.py](tests.md#module-tests.test_copies), [tests/test_copy_connections.py](tests.md#module-tests.test_copy_connections), [tests/test_copy_files.py](tests.md#module-tests.test_copy_files), [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_folder_markers.py](tests.md#module-tests.test_folder_markers), [tests/test_folder_tracking.py](tests.md#module-tests.test_folder_tracking), [tests/test_paired_comparison.py](tests.md#module-tests.test_paired_comparison), [tests/test_volume_identity.py](tests.md#module-tests.test_volume_identity).

## Оглавление определений

- [CopyCatalog](#symbol-CopyCatalog) — Управляет связями основных папок и копий в каталоге хранилищ.
- [CopyCatalog.__init__](#symbol-CopyCatalog.__init__) — Инициализирует CopyCatalog и его рабочее состояние.
- [CopyCatalog._check_overlap](#symbol-CopyCatalog._check_overlap) — Запрещает пересечение зарегистрированных областей на одном томе.
- [CopyCatalog._folder](#symbol-CopyCatalog._folder) — Проверяет том и известность папки перед регистрацией связи.
- [CopyCatalog._queue_folder_markers](#symbol-CopyCatalog._queue_folder_markers) — Ставит актуальные описания папок набора в транзакционную очередь маркеров.
- [CopyCatalog._queue_removed_marker](#symbol-CopyCatalog._queue_removed_marker) — Ставит отметку удаления связи в описание прежней папки.
- [CopyCatalog.acknowledge_changes](#symbol-CopyCatalog.acknowledge_changes) — Снимает уведомление об изменениях только для ожидаемой версии отметки.
- [CopyCatalog.add_copy](#symbol-CopyCatalog.add_copy) — Регистрирует непересекающуюся папку копии со следующим допустимым номером.
- [CopyCatalog.change_kind](#symbol-CopyCatalog.change_kind) — Меняет тип существующей копии с обновлением служебного описания.
- [CopyCatalog.create_main](#symbol-CopyCatalog.create_main) — Создаёт набор с основной папкой 00-main и очередью её маркера.
- [CopyCatalog.group](#symbol-CopyCatalog.group) — Возвращает набор папок по ID либо поднимает KeyError.
- [CopyCatalog.groups](#symbol-CopyCatalog.groups) — Собирает наборы папок, доступность, источники, маркеры и состояние нумерации.
- [CopyCatalog.mark_changed](#symbol-CopyCatalog.mark_changed) — Фиксирует время замеченного изменения основной папки.
- [CopyCatalog.queue_folder_markers](#symbol-CopyCatalog.queue_folder_markers) — Обновляет очередь служебных описаний всех зарегистрированных папок.
- [CopyCatalog.release_copy_number](#symbol-CopyCatalog.release_copy_number) — Архивирует отключённую привязку и освобождает подтверждённый номер.
- [CopyCatalog.remove_copy](#symbol-CopyCatalog.remove_copy) — Удаляет связь копии из учёта и ставит маркер removed.
- [CopyCatalog.remove_group](#symbol-CopyCatalog.remove_group) — Удаляет набор из учёта, сохраняя пользовательские файлы.
- [CopyCatalog.renumber_copies](#symbol-CopyCatalog.renumber_copies) — Перенумеровывает копии после проверки переданного снимка текущих связей.
- [CopyCatalog.set_copy_connected](#symbol-CopyCatalog.set_copy_connected) — Меняет подключение отдельной копии с проверкой зависимых источников.
- [CopyCatalog.set_copy_source](#symbol-CopyCatalog.set_copy_source) — Меняет источник копии внутри набора с проверкой доступности и циклов.
- [CopyCatalog.set_group_connected](#symbol-CopyCatalog.set_group_connected) — Подключает или отключает набор без удаления его истории и файлов.
- [CopyCatalog.update_group](#symbol-CopyCatalog.update_group) — Обновляет отслеживание изменений и смысловую метку основной папки.
- [active_locations](#symbol-active_locations) — Возвращает только подключённые области для наследования ролей в дереве.
- [copy_label](#symbol-copy_label) — Формирует метку main, copy, copy-cold или copy-cloud с номером.
- [inherited_location](#symbol-inherited_location) — Находит наиболее глубокую зарегистрированную область, содержащую путь.
- [next_copy_number](#symbol-next_copy_number) — Выбирает свободный номер либо требует предварительного устранения пропусков.
- [numbering_changes](#symbol-numbering_changes) — Рассчитывает необходимые изменения нумерации с учётом освобождённых номеров.

## Константы и значения по умолчанию

<a id="constant-COPY_KINDS"></a>

### `COPY_KINDS`

`{'copy': 'Обычная копия', 'cold': 'Сменный носитель', 'cloud': 'Облако'}`

<a id="constant-COPY_SCHEMA"></a>

### `COPY_SCHEMA`

`Объёмное значение см. в исходном модуле`

<a id="constant-FOLDER_LABELS"></a>

### `FOLDER_LABELS`

`{'': 'Без метки', 'temporary': 'Временная', 'inbox': 'На разбор', 'archive': 'Архив'}`


<a id="symbol-CopyCatalog"></a>

## `CopyCatalog`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog`

Управляет связями основных папок и копий в каталоге хранилищ. Зависимости конструктора: storage.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `storage`.

Именованные методы: `__init__`, `_queue_folder_markers`, `queue_folder_markers`, `_queue_removed_marker`, `_folder`, `_check_overlap`, `groups`, `set_copy_source`, `group`, `create_main`, `update_group`, `mark_changed`, `set_group_connected`, `set_copy_connected`, `release_copy_number`, `acknowledge_changes`, `add_copy`, `change_kind`, `remove_copy`, `renumber_copies`, `remove_group`.

<a id="symbol-CopyCatalog.__init__"></a>

## `CopyCatalog.__init__`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.__init__`

Инициализирует CopyCatalog и его рабочее состояние. Обновляет состояние объекта: storage.

```python
def __init__(self, storage)
```

Присваивания полям `self`: `storage`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog._check_overlap"></a>

## `CopyCatalog._check_overlap`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog._check_overlap`

Запрещает пересечение зарегистрированных областей на одном томе. Явно отклоняет недопустимое состояние через ValueError.

```python
def _check_overlap(db, volume_id, path)
```

Декораторы: `staticmethod`.

SQLite: чтение `copy_locations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, [copy_label](media_manager--copies.md#symbol-copy_label), `db.execute`, `other.startswith`, `path.startswith`.

Явные `raise`:

- `ValueError('Папка пересекается с областью ' + copy_label(location['kind'], location['number']) + '. Метка должна однозначно распространяться на все вложенные папки.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog._folder"></a>

## `CopyCatalog._folder`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog._folder`

Проверяет том и известность папки перед регистрацией связи. Явно отклоняет недопустимое состояние через ValueError.

```python
def _folder(self, volume_id, path)
```

SQLite: чтение `directories`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `ValueError`, `any`, `db.execute`, `db.execute('SELECT 1 FROM directories WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, `self.storage._snapshot`, `self.storage.connect`, `self.storage.get_volume`, `self.storage.metadata`, `str`.

Явные `raise`:

- `ValueError('Сначала подтверди подключённый диск.')`
- `ValueError('Выбери известную папку в дереве.')`

Выражения возврата (ветви, без исполнения):

- `path`


<a id="symbol-CopyCatalog._queue_folder_markers"></a>

## `CopyCatalog._queue_folder_markers`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog._queue_folder_markers`

Ставит актуальные описания папок набора в транзакционную очередь маркеров. Читает SQLite-таблицы: copy_locations, disconnected_copy_groups, disconnected_copy_locations, released_copy_locations.

```python
def _queue_folder_markers(db, group_id=None)
```

Декораторы: `staticmethod`.

SQLite: чтение `copy_locations`, `disconnected_copy_groups`, `disconnected_copy_locations`, `released_copy_locations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, [copy_label](media_manager--copies.md#symbol-copy_label), `db.execute`, `dict`, `location.get`, `queue_marker`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog._queue_removed_marker"></a>

## `CopyCatalog._queue_removed_marker`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog._queue_removed_marker`

Ставит отметку удаления связи в описание прежней папки. Читает SQLite-таблицы: folder_marker_jobs.

```python
def _queue_removed_marker(db, location_id)
```

Декораторы: `staticmethod`.

SQLite: чтение `folder_marker_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT payload FROM folder_marker_jobs WHERE location_id=?', (location_id,)).fetchone`, `json.loads`, `payload.pop`, `queue_marker`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog.acknowledge_changes"></a>

## `CopyCatalog.acknowledge_changes`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.acknowledge_changes`

Снимает уведомление об изменениях только для ожидаемой версии отметки. Изменяет SQLite-таблицы: copy_group_settings.

```python
def acknowledge_changes(self, group_id, changed_at)
```

SQLite: чтение `copy_groups`; запись/DDL `copy_group_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`.

Явные `raise`:

- `KeyError('Основная папка не найдена')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-CopyCatalog.add_copy"></a>

## `CopyCatalog.add_copy`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.add_copy`

Регистрирует непересекающуюся папку копии со следующим допустимым номером. Изменяет SQLite-таблицы: copy_groups, copy_locations.

```python
def add_copy(self, group_id, volume_id, path, kind='copy')
```

SQLite: чтение `copy_groups`, `copy_locations`, `released_copy_locations`; запись/DDL `copy_groups`, `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM copy_groups WHERE id=?', (group_id,)).fetchone`, `db.execute('SELECT * FROM copy_locations WHERE group_id=? AND number>0 ORDER BY number', (group_id,)).fetchall`, `db.execute('SELECT * FROM copy_locations WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, [next_copy_number](media_manager--copies.md#symbol-next_copy_number), [self._check_overlap](media_manager--copies.md#symbol-CopyCatalog._check_overlap), [self._folder](media_manager--copies.md#symbol-CopyCatalog._folder), [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `uuid4`.

Явные `raise`:

- `ValueError('Неизвестный тип копии')`
- `ValueError('Выбери папку назначения внутри тома.')`
- `KeyError('Основная папка не найдена')`
- `ValueError('Эта папка уже связана. Тип можно изменить в меню её ссылки.')`
- `ValueError('В нумерации есть пропуски. Сначала согласуй переименование меток копий.')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-CopyCatalog.change_kind"></a>

## `CopyCatalog.change_kind`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.change_kind`

Меняет тип существующей копии с обновлением служебного описания. Изменяет SQLite-таблицы: copy_locations.

```python
def change_kind(self, location_id, kind)
```

SQLite: чтение `copy_locations`; запись/DDL `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone`, [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`.

Явные `raise`:

- `ValueError('Неизвестный тип копии')`
- `KeyError('Действующая ссылка на копию не найдена')`
- `ValueError('Основная папка всегда имеет метку 00-main')`

Выражения возврата (ветви, без исполнения):

- `self.group(location['group_id'])`


<a id="symbol-CopyCatalog.create_main"></a>

## `CopyCatalog.create_main`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.create_main`

Создаёт набор с основной папкой 00-main и очередью её маркера. Изменяет SQLite-таблицы: copy_groups, copy_locations.

```python
def create_main(self, volume_id, path)
```

SQLite: чтение `copy_locations`; запись/DDL `copy_groups`, `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, [self._check_overlap](media_manager--copies.md#symbol-CopyCatalog._check_overlap), [self._folder](media_manager--copies.md#symbol-CopyCatalog._folder), [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `uuid4`.

Явные `raise`:

- `ValueError('Выбери конкретную основную папку внутри тома.')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-CopyCatalog.group"></a>

## `CopyCatalog.group`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.group`

Возвращает набор папок по ID либо поднимает KeyError. Явно отклоняет недопустимое состояние через KeyError.

```python
def group(self, group_id)
```

Прямые выражения вызова: `KeyError`, `next`, [self.groups](media_manager--copies.md#symbol-CopyCatalog.groups).

Явные `raise`:

- `KeyError('Группа копий не найдена')`

Выражения возврата (ветви, без исполнения):

- `group`


<a id="symbol-CopyCatalog.groups"></a>

## `CopyCatalog.groups`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.groups`

Собирает наборы папок, доступность, источники, маркеры и состояние нумерации. Читает SQLite-таблицы: copy_group_settings, copy_groups, copy_locations, copy_sources, disconnected_copy_groups, disconnected_copy_locations и ещё 2.

```python
def groups(self)
```

SQLite: чтение `copy_group_settings`, `copy_groups`, `copy_locations`, `copy_sources`, `disconnected_copy_groups`, `disconnected_copy_locations`, `folder_marker_jobs`, `released_copy_locations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `by_id[location['group_id']]['copies'].append`, `by_id[location['group_id']]['released_copies'].append`, [copy_label](media_manager--copies.md#symbol-copy_label), `db.execute`, `dict`, `location.update`, `locations.get`, `markers.get`, [next_copy_number](media_manager--copies.md#symbol-next_copy_number), [numbering_changes](media_manager--copies.md#symbol-numbering_changes), `self.storage.connect`, `self.storage.get_volume`, `self.storage.refresh`, `sources.get`, `volume.get`, `volumes.get`.

Выражения возврата (ветви, без исполнения):

- `groups`


<a id="symbol-CopyCatalog.mark_changed"></a>

## `CopyCatalog.mark_changed`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.mark_changed`

Фиксирует время замеченного изменения основной папки. Изменяет SQLite-таблицы: copy_group_settings.

```python
def mark_changed(self, group_id)
```

SQLite: чтение `disconnected_copy_groups`; запись/DDL `copy_group_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `self.storage.connect`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog.queue_folder_markers"></a>

## `CopyCatalog.queue_folder_markers`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.queue_folder_markers`

Обновляет очередь служебных описаний всех зарегистрированных папок. Использует db.execute, self._queue_folder_markers, self.storage.connect.

```python
def queue_folder_markers(self)
```

Прямые выражения вызова: `db.execute`, [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), `self.storage.connect`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog.release_copy_number"></a>

## `CopyCatalog.release_copy_number`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.release_copy_number`

Архивирует отключённую привязку и освобождает подтверждённый номер. Изменяет SQLite-таблицы: copy_locations, released_copy_locations.

```python
def release_copy_number(self, location_id, number, kind)
```

SQLite: чтение `copy_locations`, `disconnected_copy_groups`, `disconnected_copy_locations`, `released_copy_locations`; запись/DDL `copy_locations`, `released_copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT l.*,d.disconnected_at,g.disconnected_at AS group_disconnected_at\n                FROM copy_locations l LEFT JOIN disconnected_copy_locations d ON d.location_id=l.id\n                LEFT JOIN disconnected_copy_groups g ON g.group_id=l.group_id WHERE l.id=?', (location_id,)).fetchone`, [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `tuple`.

Явные `raise`:

- `KeyError('Ссылка на копию не найдена')`
- `ValueError('Метка копии изменилась. Обнови список и повтори действие.')`
- `ValueError('Номер основной папки нельзя освобождать')`
- `ValueError('Сначала отключи эту копию')`

Выражения возврата (ветви, без исполнения):

- `self.group(location['group_id'])`


<a id="symbol-CopyCatalog.remove_copy"></a>

## `CopyCatalog.remove_copy`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.remove_copy`

Удаляет связь копии из учёта и ставит маркер removed. Изменяет SQLite-таблицы: copy_groups, copy_locations, released_copy_locations.

```python
def remove_copy(self, location_id)
```

SQLite: чтение `copy_locations`, `released_copy_locations`; запись/DDL `copy_groups`, `copy_locations`, `released_copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT COALESCE(MAX(number),0)+1 FROM copy_locations WHERE group_id=?', (location['group_id'],)).fetchone`, [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self._queue_removed_marker](media_manager--copies.md#symbol-CopyCatalog._queue_removed_marker), `self.storage.connect`.

Явные `raise`:

- `KeyError('Ссылка на копию не найдена')`
- `ValueError('Основную папку убирают вместе с её списком копий')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopyCatalog.remove_group"></a>

## `CopyCatalog.remove_group`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.remove_group`

Удаляет набор из учёта, сохраняя пользовательские файлы. Изменяет SQLite-таблицы: copy_groups.

```python
def remove_group(self, group_id)
```

SQLite: чтение `copy_groups`, `folder_marker_jobs`; запись/DDL `copy_groups`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, `db.execute('SELECT location_id FROM folder_marker_jobs WHERE group_id=?', (group_id,)).fetchall`, [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self._queue_removed_marker](media_manager--copies.md#symbol-CopyCatalog._queue_removed_marker), `self.storage.connect`.

Явные `raise`:

- `KeyError('Основная папка не найдена')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyCatalog.renumber_copies"></a>

## `CopyCatalog.renumber_copies`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.renumber_copies`

Перенумеровывает копии после проверки переданного снимка текущих связей. Изменяет SQLite-таблицы: copy_groups, copy_locations.

```python
def renumber_copies(self, group_id, expected_copies)
```

SQLite: чтение `copy_groups`, `copy_locations`, `released_copy_locations`; запись/DDL `copy_groups`, `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, `dict`, `len`, [numbering_changes](media_manager--copies.md#symbol-numbering_changes), [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`.

Явные `raise`:

- `KeyError('Основная папка не найдена')`
- `ValueError('Список копий изменился. Проверь и подтверди новое предложение переименования.')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-CopyCatalog.set_copy_connected"></a>

## `CopyCatalog.set_copy_connected`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.set_copy_connected`

Меняет подключение отдельной копии с проверкой зависимых источников. Изменяет SQLite-таблицы: copy_locations, disconnected_copy_locations, released_copy_locations.

```python
def set_copy_connected(self, location_id, connected)
```

SQLite: чтение `copy_locations`, `disconnected_copy_locations`, `released_copy_locations`; запись/DDL `copy_locations`, `disconnected_copy_locations`, `released_copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT 1 FROM copy_locations WHERE group_id=? AND number=?', (archived['group_id'], archived['number'])).fetchone`, `db.execute('SELECT group_id,number FROM copy_locations WHERE id=?', (location_id,)).fetchone`, [self._check_overlap](media_manager--copies.md#symbol-CopyCatalog._check_overlap), [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `tuple`, `type`.

Явные `raise`:

- `ValueError('Нужно включить или отключить связь')`
- `KeyError('Ссылка на копию не найдена')`
- `ValueError(f"Номер {archived['number']:02d} уже занят другой привязкой. Прежняя история сохранена.")`
- `ValueError('Основную папку отключают вместе с её набором')`

Выражения возврата (ветви, без исполнения):

- `self.group(location['group_id'])`


<a id="symbol-CopyCatalog.set_copy_source"></a>

## `CopyCatalog.set_copy_source`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.set_copy_source`

Меняет источник копии внутри набора с проверкой доступности и циклов. Изменяет SQLite-таблицы: copy_sources.

```python
def set_copy_source(self, location_id, source_id)
```

SQLite: чтение `copy_locations`, `copy_sources`; запись/DDL `copy_sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone`, `dict`, `next`, `nodes.values`, [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `set`, `visited.add`.

Явные `raise`:

- `ValueError('Выбери действующую копию')`
- `ValueError('Источник должен быть папкой того же набора')`
- `ValueError('Циклические связи копирования запрещены')`

Выражения возврата (ветви, без исполнения):

- `self.group(target['group_id'])`


<a id="symbol-CopyCatalog.set_group_connected"></a>

## `CopyCatalog.set_group_connected`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.set_group_connected`

Подключает или отключает набор без удаления его истории и файлов. Изменяет SQLite-таблицы: disconnected_copy_groups.

```python
def set_group_connected(self, group_id, connected)
```

SQLite: чтение `copy_groups`, `disconnected_copy_groups`; запись/DDL `disconnected_copy_groups`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, [self._queue_folder_markers](media_manager--copies.md#symbol-CopyCatalog._queue_folder_markers), [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `type`.

Явные `raise`:

- `ValueError('Нужно включить или отключить связь')`
- `KeyError('Основная папка не найдена')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-CopyCatalog.update_group"></a>

## `CopyCatalog.update_group`

[media_manager/copies.py](../../media_manager/copies.py) · `CopyCatalog.update_group`

Обновляет отслеживание изменений и смысловую метку основной папки. Изменяет SQLite-таблицы: copy_group_settings.

```python
def update_group(self, group_id, changes)
```

SQLite: чтение `copy_groups`; запись/DDL `copy_group_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `changes.items`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, [self.group](media_manager--copies.md#symbol-CopyCatalog.group), `self.storage.connect`, `set`, `type`.

Явные `raise`:

- `ValueError('Нужна метка папки или настройка отслеживания')`
- `ValueError('Неизвестная метка папки')`
- `ValueError('Отслеживание должно быть включено или выключено')`
- `KeyError('Основная папка не найдена')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-active_locations"></a>

## `active_locations`

[media_manager/copies.py](../../media_manager/copies.py) · `active_locations`

Возвращает только подключённые области для наследования ролей в дереве. Читает SQLite-таблицы: copy_locations, disconnected_copy_groups, disconnected_copy_locations.

```python
def active_locations(db, volume_id)
```

SQLite: чтение `copy_locations`, `disconnected_copy_groups`, `disconnected_copy_locations`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`.

Выражения возврата (ветви, без исполнения):

- `[dict(row) for row in db.execute('\n        SELECT l.* FROM copy_locations l\n        WHERE l.volume_id=?\n          AND NOT EXISTS (SELECT 1 FROM disconnected_copy_groups g WHERE g.group_id=l.group_id)\n          AND NOT EXISTS (SELECT 1 FROM disconnected_copy_locations d WHERE d.location_id=l.id)\n    ', (volume_id,))]`


<a id="symbol-copy_label"></a>

## `copy_label`

[media_manager/copies.py](../../media_manager/copies.py) · `copy_label`

Формирует метку main, copy, copy-cold или copy-cloud с номером. Параметры: kind, number.

```python
def copy_label(kind, number)
```

Выражения возврата (ветви, без исполнения):

- `f'{number:02d}-{suffix}'`


<a id="symbol-inherited_location"></a>

## `inherited_location`

[media_manager/copies.py](../../media_manager/copies.py) · `inherited_location`

Находит наиболее глубокую зарегистрированную область, содержащую путь. Поля результата: label, is_root, inherited_from.

```python
def inherited_location(path, locations)
```

Прямые выражения вызова: [copy_label](media_manager--copies.md#symbol-copy_label), `max`, `path.startswith`.

Выражения возврата (ветви, без исполнения):

- `None`
- `{**location, 'label': copy_label(location['kind'], location['number']), 'is_root': path == location['path'], 'inherited_from': None if path == location['path'] else location['path']}`


<a id="symbol-next_copy_number"></a>

## `next_copy_number`

[media_manager/copies.py](../../media_manager/copies.py) · `next_copy_number`

Выбирает свободный номер либо требует предварительного устранения пропусков. Использует numbering_changes.

```python
def next_copy_number(copies, released_numbers=())
```

Прямые выражения вызова: `max`, `min`, [numbering_changes](media_manager--copies.md#symbol-numbering_changes), `set`.

Выражения возврата (ветви, без исполнения):

- `None`
- `min(set(released_numbers) - occupied &#124; {max(occupied, default=0) + 1})`


<a id="symbol-numbering_changes"></a>

## `numbering_changes`

[media_manager/copies.py](../../media_manager/copies.py) · `numbering_changes`

Рассчитывает необходимые изменения нумерации с учётом освобождённых номеров. Использует copy_label, count, zip.

```python
def numbering_changes(copies, released_numbers=())
```

Прямые выражения вызова: [copy_label](media_manager--copies.md#symbol-copy_label), `count`, `set`, `zip`.

Выражения возврата (ветви, без исполнения):

- `[{'id': location['id'], 'from_label': copy_label(location['kind'], location['number']), 'to_label': copy_label(location['kind'], number), 'number': number} for number, location in zip(numbers, copies) if location['number'] != number]`
