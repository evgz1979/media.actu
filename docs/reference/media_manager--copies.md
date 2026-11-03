# Учёт основных папок и копий: `media_manager/copies.py`

Описывает наборы папок, нумерацию, отключение, освобождение номеров и источники копирования. Сам каталог не переносит пользовательские файлы, но ставит запись маркеров в постоянную очередь.

[Исходный модуль](../../media_manager/copies.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/folder_markers.py](media_manager--folder_markers.md).
Импортируется модулями: [app.py](app.md), [copy_groups_ui.py](copy_groups_ui.md), [media_manager/storage.py](media_manager--storage.md).
Тестовые модули с прямым импортом: [tests/test_copies.py](../../tests/test_copies.py#L6), [tests/test_copy_connections.py](../../tests/test_copy_connections.py#L11), [tests/test_copy_files.py](../../tests/test_copy_files.py#L12), [tests/test_copy_number_release.py](../../tests/test_copy_number_release.py#L12), [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L11), [tests/test_folder_tracking.py](../../tests/test_folder_tracking.py#L12), [tests/test_paired_comparison.py](../../tests/test_paired_comparison.py#L9), [tests/test_volume_identity.py](../../tests/test_volume_identity.py#L15).

## Оглавление определений

- [copy_label](#symbol-copy-label) — Формирует метку main, copy, copy-cold или copy-cloud с номером.
- [numbering_changes](#symbol-numbering-changes) — Рассчитывает необходимые изменения нумерации с учётом освобождённых номеров.
- [next_copy_number](#symbol-next-copy-number) — Выбирает свободный номер либо требует предварительного устранения пропусков.
- [inherited_location](#symbol-inherited-location) — Находит наиболее глубокую зарегистрированную область, содержащую путь.
- [active_locations](#symbol-active-locations) — Возвращает только подключённые области для наследования ролей в дереве.
- [CopyCatalog](#symbol-copycatalog) — Управляет связями основных папок и копий в каталоге хранилищ.
- [CopyCatalog.__init__](#symbol-copycatalog---init--) — Инициализирует CopyCatalog и его рабочее состояние.
- [CopyCatalog._queue_folder_markers](#symbol-copycatalog--queue-folder-markers) — Ставит актуальные описания папок набора в транзакционную очередь маркеров.
- [CopyCatalog.queue_folder_markers](#symbol-copycatalog-queue-folder-markers) — Обновляет очередь служебных описаний всех зарегистрированных папок.
- [CopyCatalog._queue_removed_marker](#symbol-copycatalog--queue-removed-marker) — Ставит отметку удаления связи в описание прежней папки.
- [CopyCatalog._folder](#symbol-copycatalog--folder) — Проверяет том и известность папки перед регистрацией связи.
- [CopyCatalog._check_overlap](#symbol-copycatalog--check-overlap) — Запрещает пересечение зарегистрированных областей на одном томе.
- [CopyCatalog.groups](#symbol-copycatalog-groups) — Собирает наборы папок, доступность, источники, маркеры и состояние нумерации.
- [CopyCatalog.set_copy_source](#symbol-copycatalog-set-copy-source) — Меняет источник копии внутри набора с проверкой доступности и циклов.
- [CopyCatalog.group](#symbol-copycatalog-group) — Возвращает набор папок по ID либо поднимает KeyError.
- [CopyCatalog.create_main](#symbol-copycatalog-create-main) — Создаёт набор с основной папкой 00-main и очередью её маркера.
- [CopyCatalog.update_group](#symbol-copycatalog-update-group) — Обновляет отслеживание изменений и смысловую метку основной папки.
- [CopyCatalog.mark_changed](#symbol-copycatalog-mark-changed) — Фиксирует время замеченного изменения основной папки.
- [CopyCatalog.set_group_connected](#symbol-copycatalog-set-group-connected) — Подключает или отключает набор без удаления его истории и файлов.
- [CopyCatalog.set_copy_connected](#symbol-copycatalog-set-copy-connected) — Меняет подключение отдельной копии с проверкой зависимых источников.
- [CopyCatalog.release_copy_number](#symbol-copycatalog-release-copy-number) — Архивирует отключённую привязку и освобождает подтверждённый номер.
- [CopyCatalog.acknowledge_changes](#symbol-copycatalog-acknowledge-changes) — Снимает уведомление об изменениях только для ожидаемой версии отметки.
- [CopyCatalog.add_copy](#symbol-copycatalog-add-copy) — Регистрирует непересекающуюся папку копии со следующим допустимым номером.
- [CopyCatalog.change_kind](#symbol-copycatalog-change-kind) — Меняет тип существующей копии с обновлением служебного описания.
- [CopyCatalog.remove_copy](#symbol-copycatalog-remove-copy) — Удаляет связь копии из учёта и ставит маркер removed.
- [CopyCatalog.renumber_copies](#symbol-copycatalog-renumber-copies) — Перенумеровывает копии после проверки переданного снимка текущих связей.
- [CopyCatalog.remove_group](#symbol-copycatalog-remove-group) — Удаляет набор из учёта, сохраняя пользовательские файлы.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [COPY_KINDS](../../media_manager/copies.py#L13) | `{'copy': 'Обычная копия', 'cold': 'Сменный носитель', 'cloud': 'Облако'}` |
| [FOLDER_LABELS](../../media_manager/copies.py#L14) | `{'': 'Без метки', 'temporary': 'Временная', 'inbox': 'На разбор', 'archive': 'Архив'}` |

<a id="symbol-copy-label"></a>

## `copy_label`

[media_manager/copies.py:62](../../media_manager/copies.py#L62)

Формирует метку main, copy, copy-cold или copy-cloud с номером. Параметры: kind, number.

```python
def copy_label(kind, number)
```

Выражения возврата (ветви, без исполнения):

- `f'{number:02d}-{suffix}'`


<a id="symbol-numbering-changes"></a>

## `numbering_changes`

[media_manager/copies.py:69](../../media_manager/copies.py#L69)

Рассчитывает необходимые изменения нумерации с учётом освобождённых номеров. Использует copy_label, count, zip.

```python
def numbering_changes(copies, released_numbers=())
```

Прямые выражения вызова: [copy_label](../../media_manager/copies.py#L62), `count`, `set`, `zip`.

Выражения возврата (ветви, без исполнения):

- `[{'id': location['id'], 'from_label': copy_label(location['kind'], location['number']), 'to_label': copy_label(location['kind'], number), 'number': number} for (number, location) in zip(numbers, copies) if location['number'] != number]`


<a id="symbol-next-copy-number"></a>

## `next_copy_number`

[media_manager/copies.py:79](../../media_manager/copies.py#L79)

Выбирает свободный номер либо требует предварительного устранения пропусков. Использует numbering_changes.

```python
def next_copy_number(copies, released_numbers=())
```

Прямые выражения вызова: `max`, `min`, [numbering_changes](../../media_manager/copies.py#L69), `set`.

Выражения возврата (ветви, без исполнения):

- `None`
- `min(set(released_numbers) - occupied &#124; {max(occupied, default=0) + 1})`


<a id="symbol-inherited-location"></a>

## `inherited_location`

[media_manager/copies.py:88](../../media_manager/copies.py#L88)

Находит наиболее глубокую зарегистрированную область, содержащую путь. Поля результата: label, is_root, inherited_from.

```python
def inherited_location(path, locations)
```

Прямые выражения вызова: [copy_label](../../media_manager/copies.py#L62), `max`, `path.startswith`.

Выражения возврата (ветви, без исполнения):

- `None`
- `{**location, 'label': copy_label(location['kind'], location['number']), 'is_root': path == location['path'], 'inherited_from': None if path == location['path'] else location['path']}`


<a id="symbol-active-locations"></a>

## `active_locations`

[media_manager/copies.py:100](../../media_manager/copies.py#L100)

Возвращает только подключённые области для наследования ролей в дереве. Читает SQLite-таблицы: copy_locations, disconnected_copy_groups, disconnected_copy_locations.

```python
def active_locations(db, volume_id)
```

SQLite: чтение `copy_locations`, `disconnected_copy_groups`, `disconnected_copy_locations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`.

Выражения возврата (ветви, без исполнения):

- `[dict(row) for row in db.execute('\n        SELECT l.* FROM copy_locations l\n        WHERE l.volume_id=?\n          AND NOT EXISTS (SELECT 1 FROM disconnected_copy_groups g WHERE g.group_id=l.group_id)\n          AND NOT EXISTS (SELECT 1 FROM disconnected_copy_locations d WHERE d.location_id=l.id)\n    ', (volume_id,))]`


<a id="symbol-copycatalog"></a>

## `CopyCatalog`

[media_manager/copies.py:112](../../media_manager/copies.py#L112)

Управляет связями основных папок и копий в каталоге хранилищ. Зависимости конструктора: storage.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `storage`.

Именованные методы: `__init__`, `_queue_folder_markers`, `queue_folder_markers`, `_queue_removed_marker`, `_folder`, `_check_overlap`, `groups`, `set_copy_source`, `group`, `create_main`, `update_group`, `mark_changed`, `set_group_connected`, `set_copy_connected`, `release_copy_number`, `acknowledge_changes`, `add_copy`, `change_kind`, `remove_copy`, `renumber_copies`, `remove_group`.

<a id="symbol-copycatalog---init--"></a>

## `CopyCatalog.__init__`

[media_manager/copies.py:115](../../media_manager/copies.py#L115)

Инициализирует CopyCatalog и его рабочее состояние. Обновляет состояние объекта: storage.

```python
def __init__(self, storage)
```

Присваивания полям `self`: `storage`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-copycatalog--queue-folder-markers"></a>

## `CopyCatalog._queue_folder_markers`

[media_manager/copies.py:121](../../media_manager/copies.py#L121)

Ставит актуальные описания папок набора в транзакционную очередь маркеров. Читает SQLite-таблицы: copy_locations, disconnected_copy_groups, disconnected_copy_locations, released_copy_locations.

```python
def _queue_folder_markers(db, group_id=None)
```

Декораторы: `staticmethod`.

SQLite: чтение `copy_locations`, `disconnected_copy_groups`, `disconnected_copy_locations`, `released_copy_locations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, [copy_label](../../media_manager/copies.py#L62), `db.execute`, `dict`, `location.get`, `queue_marker`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-copycatalog-queue-folder-markers"></a>

## `CopyCatalog.queue_folder_markers`

[media_manager/copies.py:142](../../media_manager/copies.py#L142)

Обновляет очередь служебных описаний всех зарегистрированных папок. Использует db.execute, self._queue_folder_markers, self.storage.connect.

```python
def queue_folder_markers(self)
```

Прямые выражения вызова: `db.execute`, [self._queue_folder_markers](../../media_manager/copies.py#L121), `self.storage.connect`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-copycatalog--queue-removed-marker"></a>

## `CopyCatalog._queue_removed_marker`

[media_manager/copies.py:150](../../media_manager/copies.py#L150)

Ставит отметку удаления связи в описание прежней папки. Читает SQLite-таблицы: folder_marker_jobs.

```python
def _queue_removed_marker(db, location_id)
```

Декораторы: `staticmethod`.

SQLite: чтение `folder_marker_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT payload FROM folder_marker_jobs WHERE location_id=?', (location_id,)).fetchone`, `json.loads`, `payload.pop`, `queue_marker`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-copycatalog--folder"></a>

## `CopyCatalog._folder`

[media_manager/copies.py:160](../../media_manager/copies.py#L160)

Проверяет том и известность папки перед регистрацией связи. Явно отклоняет недопустимое состояние через ValueError.

```python
def _folder(self, volume_id, path)
```

SQLite: чтение `directories`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `ValueError`, `any`, `db.execute`, `db.execute('SELECT 1 FROM directories WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, `self.storage._snapshot`, `self.storage.connect`, `self.storage.get_volume`, `self.storage.metadata`, `str`.

Явные `raise`:

- `ValueError('Сначала подтверди подключённый диск.')`
- `ValueError('Выбери известную папку в дереве.')`

Выражения возврата (ветви, без исполнения):

- `path`


<a id="symbol-copycatalog--check-overlap"></a>

## `CopyCatalog._check_overlap`

[media_manager/copies.py:180](../../media_manager/copies.py#L180)

Запрещает пересечение зарегистрированных областей на одном томе. Явно отклоняет недопустимое состояние через ValueError.

```python
def _check_overlap(db, volume_id, path)
```

Декораторы: `staticmethod`.

SQLite: чтение `copy_locations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, [copy_label](../../media_manager/copies.py#L62), `db.execute`, `other.startswith`, `path.startswith`.

Явные `raise`:

- `ValueError('Папка пересекается с областью ' + copy_label(location['kind'], location['number']) + '. Метка должна однозначно распространяться на все вложенные папки.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-copycatalog-groups"></a>

## `CopyCatalog.groups`

[media_manager/copies.py:189](../../media_manager/copies.py#L189)

Собирает наборы папок, доступность, источники, маркеры и состояние нумерации. Читает SQLite-таблицы: copy_group_settings, copy_groups, copy_locations, copy_sources, disconnected_copy_groups, disconnected_copy_locations и ещё 2.

```python
def groups(self)
```

SQLite: чтение `copy_group_settings`, `copy_groups`, `copy_locations`, `copy_sources`, `disconnected_copy_groups`, `disconnected_copy_locations`, `folder_marker_jobs`, `released_copy_locations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `by_id[location['group_id']]['copies'].append`, `by_id[location['group_id']]['released_copies'].append`, [copy_label](../../media_manager/copies.py#L62), `db.execute`, `dict`, `location.update`, `locations.get`, `markers.get`, [next_copy_number](../../media_manager/copies.py#L79), [numbering_changes](../../media_manager/copies.py#L69), `self.storage.connect`, `self.storage.get_volume`, `self.storage.refresh`, `sources.get`, `volume.get`, `volumes.get`.

Выражения возврата (ветви, без исполнения):

- `groups`


<a id="symbol-copycatalog-set-copy-source"></a>

## `CopyCatalog.set_copy_source`

[media_manager/copies.py:240](../../media_manager/copies.py#L240)

Меняет источник копии внутри набора с проверкой доступности и циклов. Изменяет SQLite-таблицы: copy_sources.

```python
def set_copy_source(self, location_id, source_id)
```

SQLite: чтение `copy_locations`, `copy_sources`; запись/DDL `copy_sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone`, `dict`, `next`, `nodes.values`, [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `set`, `visited.add`.

Явные `raise`:

- `ValueError('Выбери действующую копию')`
- `ValueError('Источник должен быть папкой того же набора')`
- `ValueError('Циклические связи копирования запрещены')`

Выражения возврата (ветви, без исполнения):

- `self.group(target['group_id'])`


<a id="symbol-copycatalog-group"></a>

## `CopyCatalog.group`

[media_manager/copies.py:266](../../media_manager/copies.py#L266)

Возвращает набор папок по ID либо поднимает KeyError. Явно отклоняет недопустимое состояние через KeyError.

```python
def group(self, group_id)
```

Прямые выражения вызова: `KeyError`, `next`, [self.groups](../../media_manager/copies.py#L189).

Явные `raise`:

- `KeyError('Группа копий не найдена')`

Выражения возврата (ветви, без исполнения):

- `group`


<a id="symbol-copycatalog-create-main"></a>

## `CopyCatalog.create_main`

[media_manager/copies.py:274](../../media_manager/copies.py#L274)

Создаёт набор с основной папкой 00-main и очередью её маркера. Изменяет SQLite-таблицы: copy_groups, copy_locations.

```python
def create_main(self, volume_id, path)
```

SQLite: чтение `copy_locations`; запись/DDL `copy_groups`, `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, [self._check_overlap](../../media_manager/copies.py#L180), [self._folder](../../media_manager/copies.py#L160), [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `uuid4`.

Явные `raise`:

- `ValueError('Выбери конкретную основную папку внутри тома.')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-copycatalog-update-group"></a>

## `CopyCatalog.update_group`

[media_manager/copies.py:295](../../media_manager/copies.py#L295)

Обновляет отслеживание изменений и смысловую метку основной папки. Изменяет SQLite-таблицы: copy_group_settings.

```python
def update_group(self, group_id, changes)
```

SQLite: чтение `copy_groups`; запись/DDL `copy_group_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `changes.items`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `set`, `type`.

Явные `raise`:

- `ValueError('Нужна метка папки или настройка отслеживания')`
- `ValueError('Неизвестная метка папки')`
- `ValueError('Отслеживание должно быть включено или выключено')`
- `KeyError('Основная папка не найдена')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-copycatalog-mark-changed"></a>

## `CopyCatalog.mark_changed`

[media_manager/copies.py:313](../../media_manager/copies.py#L313)

Фиксирует время замеченного изменения основной папки. Изменяет SQLite-таблицы: copy_group_settings.

```python
def mark_changed(self, group_id)
```

SQLite: чтение `disconnected_copy_groups`; запись/DDL `copy_group_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `self.storage.connect`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-copycatalog-set-group-connected"></a>

## `CopyCatalog.set_group_connected`

[media_manager/copies.py:321](../../media_manager/copies.py#L321)

Подключает или отключает набор без удаления его истории и файлов. Изменяет SQLite-таблицы: disconnected_copy_groups.

```python
def set_group_connected(self, group_id, connected)
```

SQLite: чтение `copy_groups`, `disconnected_copy_groups`; запись/DDL `disconnected_copy_groups`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `type`.

Явные `raise`:

- `ValueError('Нужно включить или отключить связь')`
- `KeyError('Основная папка не найдена')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-copycatalog-set-copy-connected"></a>

## `CopyCatalog.set_copy_connected`

[media_manager/copies.py:338](../../media_manager/copies.py#L338)

Меняет подключение отдельной копии с проверкой зависимых источников. Изменяет SQLite-таблицы: copy_locations, disconnected_copy_locations, released_copy_locations.

```python
def set_copy_connected(self, location_id, connected)
```

SQLite: чтение `copy_locations`, `disconnected_copy_locations`, `released_copy_locations`; запись/DDL `copy_locations`, `disconnected_copy_locations`, `released_copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT 1 FROM copy_locations WHERE group_id=? AND number=?', (archived['group_id'], archived['number'])).fetchone`, `db.execute('SELECT group_id,number FROM copy_locations WHERE id=?', (location_id,)).fetchone`, [self._check_overlap](../../media_manager/copies.py#L180), [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `tuple`, `type`.

Явные `raise`:

- `ValueError('Нужно включить или отключить связь')`
- `KeyError('Ссылка на копию не найдена')`
- `ValueError(f"Номер {archived['number']:02d} уже занят другой привязкой. Прежняя история сохранена.")`
- `ValueError('Основную папку отключают вместе с её набором')`

Выражения возврата (ветви, без исполнения):

- `self.group(location['group_id'])`


<a id="symbol-copycatalog-release-copy-number"></a>

## `CopyCatalog.release_copy_number`

[media_manager/copies.py:370](../../media_manager/copies.py#L370)

Архивирует отключённую привязку и освобождает подтверждённый номер. Изменяет SQLite-таблицы: copy_locations, released_copy_locations.

```python
def release_copy_number(self, location_id, number, kind)
```

SQLite: чтение `copy_locations`, `disconnected_copy_groups`, `disconnected_copy_locations`, `released_copy_locations`; запись/DDL `copy_locations`, `released_copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT l.*,d.disconnected_at,g.disconnected_at AS group_disconnected_at\n                FROM copy_locations l LEFT JOIN disconnected_copy_locations d ON d.location_id=l.id\n                LEFT JOIN disconnected_copy_groups g ON g.group_id=l.group_id WHERE l.id=?', (location_id,)).fetchone`, [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `tuple`.

Явные `raise`:

- `KeyError('Ссылка на копию не найдена')`
- `ValueError('Метка копии изменилась. Обнови список и повтори действие.')`
- `ValueError('Номер основной папки нельзя освобождать')`
- `ValueError('Сначала отключи эту копию')`

Выражения возврата (ветви, без исполнения):

- `self.group(location['group_id'])`


<a id="symbol-copycatalog-acknowledge-changes"></a>

## `CopyCatalog.acknowledge_changes`

[media_manager/copies.py:399](../../media_manager/copies.py#L399)

Снимает уведомление об изменениях только для ожидаемой версии отметки. Изменяет SQLite-таблицы: copy_group_settings.

```python
def acknowledge_changes(self, group_id, changed_at)
```

SQLite: чтение `copy_groups`; запись/DDL `copy_group_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, [self.group](../../media_manager/copies.py#L266), `self.storage.connect`.

Явные `raise`:

- `KeyError('Основная папка не найдена')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-copycatalog-add-copy"></a>

## `CopyCatalog.add_copy`

[media_manager/copies.py:410](../../media_manager/copies.py#L410)

Регистрирует непересекающуюся папку копии со следующим допустимым номером. Изменяет SQLite-таблицы: copy_groups, copy_locations.

```python
def add_copy(self, group_id, volume_id, path, kind='copy')
```

SQLite: чтение `copy_groups`, `copy_locations`, `released_copy_locations`; запись/DDL `copy_groups`, `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `db.execute`, `db.execute('SELECT * FROM copy_groups WHERE id=?', (group_id,)).fetchone`, `db.execute('SELECT * FROM copy_locations WHERE group_id=? AND number>0 ORDER BY number', (group_id,)).fetchall`, `db.execute('SELECT * FROM copy_locations WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, [next_copy_number](../../media_manager/copies.py#L79), [self._check_overlap](../../media_manager/copies.py#L180), [self._folder](../../media_manager/copies.py#L160), [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`, `uuid4`.

Явные `raise`:

- `ValueError('Неизвестный тип копии')`
- `ValueError('Выбери папку назначения внутри тома.')`
- `KeyError('Основная папка не найдена')`
- `ValueError('Эта папка уже связана. Тип можно изменить в меню её ссылки.')`
- `ValueError('В нумерации есть пропуски. Сначала согласуй переименование меток копий.')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-copycatalog-change-kind"></a>

## `CopyCatalog.change_kind`

[media_manager/copies.py:443](../../media_manager/copies.py#L443)

Меняет тип существующей копии с обновлением служебного описания. Изменяет SQLite-таблицы: copy_locations.

```python
def change_kind(self, location_id, kind)
```

SQLite: чтение `copy_locations`; запись/DDL `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone`, [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`.

Явные `raise`:

- `ValueError('Неизвестный тип копии')`
- `KeyError('Действующая ссылка на копию не найдена')`
- `ValueError('Основная папка всегда имеет метку 00-main')`

Выражения возврата (ветви, без исполнения):

- `self.group(location['group_id'])`


<a id="symbol-copycatalog-remove-copy"></a>

## `CopyCatalog.remove_copy`

[media_manager/copies.py:459](../../media_manager/copies.py#L459)

Удаляет связь копии из учёта и ставит маркер removed. Изменяет SQLite-таблицы: copy_groups, copy_locations, released_copy_locations.

```python
def remove_copy(self, location_id)
```

SQLite: чтение `copy_locations`, `released_copy_locations`; запись/DDL `copy_groups`, `copy_locations`, `released_copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute('SELECT * FROM copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT * FROM released_copy_locations WHERE id=?', (location_id,)).fetchone`, `db.execute('SELECT COALESCE(MAX(number),0)+1 FROM copy_locations WHERE group_id=?', (location['group_id'],)).fetchone`, [self._queue_folder_markers](../../media_manager/copies.py#L121), [self._queue_removed_marker](../../media_manager/copies.py#L150), `self.storage.connect`.

Явные `raise`:

- `KeyError('Ссылка на копию не найдена')`
- `ValueError('Основную папку убирают вместе с её списком копий')`

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-copycatalog-renumber-copies"></a>

## `CopyCatalog.renumber_copies`

[media_manager/copies.py:482](../../media_manager/copies.py#L482)

Перенумеровывает копии после проверки переданного снимка текущих связей. Изменяет SQLite-таблицы: copy_groups, copy_locations.

```python
def renumber_copies(self, group_id, expected_copies)
```

SQLite: чтение `copy_groups`, `copy_locations`, `released_copy_locations`; запись/DDL `copy_groups`, `copy_locations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, `dict`, `len`, [numbering_changes](../../media_manager/copies.py#L69), [self._queue_folder_markers](../../media_manager/copies.py#L121), [self.group](../../media_manager/copies.py#L266), `self.storage.connect`.

Явные `raise`:

- `KeyError('Основная папка не найдена')`
- `ValueError('Список копий изменился. Проверь и подтверди новое предложение переименования.')`

Выражения возврата (ветви, без исполнения):

- `self.group(group_id)`


<a id="symbol-copycatalog-remove-group"></a>

## `CopyCatalog.remove_group`

[media_manager/copies.py:501](../../media_manager/copies.py#L501)

Удаляет набор из учёта, сохраняя пользовательские файлы. Изменяет SQLite-таблицы: copy_groups.

```python
def remove_group(self, group_id)
```

SQLite: чтение `copy_groups`, `folder_marker_jobs`; запись/DDL `copy_groups`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT 1 FROM copy_groups WHERE id=?', (group_id,)).fetchone`, `db.execute('SELECT location_id FROM folder_marker_jobs WHERE group_id=?', (group_id,)).fetchall`, [self._queue_folder_markers](../../media_manager/copies.py#L121), [self._queue_removed_marker](../../media_manager/copies.py#L150), `self.storage.connect`.

Явные `raise`:

- `KeyError('Основная папка не найдена')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
