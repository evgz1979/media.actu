# UI наборов копий: `copy_groups_ui.py`

Боковая панель основных папок и копий, контекстные команды связей, настройка источников, номера, архив и уведомления об изменениях.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../copy_groups_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [copy_panels.py](copy_panels.md), [media_manager/copies.py](media_manager--copies.md), [sidebar_ui.py](sidebar_ui.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_connections.py](tests.md#module-tests.test_copy_connections), [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_paired_workspace.py](tests.md#module-tests.test_paired_workspace), [tests/test_sidebar_state.py](tests.md#module-tests.test_sidebar_state).

## Оглавление определений

- [CopyGroupsUI](#symbol-CopyGroupsUI) — Показывает наборы папок и выполняет команды учёта через Core API.
- [CopyGroupsUI.__init__](#symbol-CopyGroupsUI.__init__) — Инициализирует CopyGroupsUI и его рабочее состояние.
- [CopyGroupsUI.acknowledge_changes](#symbol-CopyGroupsUI.acknowledge_changes) — Подтверждает просмотр конкретной отметки изменения основной папки.
- [CopyGroupsUI.build_controls](#symbol-CopyGroupsUI.build_controls) — Создаёт контейнер команд назначения основной папки и копии.
- [CopyGroupsUI.build_sidebar](#symbol-CopyGroupsUI.build_sidebar) — Создаёт боковые секции основных папок и отключённых связей.
- [CopyGroupsUI.changed](#symbol-CopyGroupsUI.changed) — Обновляет наборы, тома, медиатеки и видимые метки после изменения связей.
- [CopyGroupsUI.choose_source](#symbol-CopyGroupsUI.choose_source) — Показывает выбор основной или другой копии как источника назначения.
- [CopyGroupsUI.confirm_remove](#symbol-CopyGroupsUI.confirm_remove) — Показывает подтверждение удаления связей с явными путями папок.
- [CopyGroupsUI.context_actions](#symbol-CopyGroupsUI.context_actions) — Предоставляет команды учёта для контекстного меню выбранной папки.
- [CopyGroupsUI.copy_row](#symbol-CopyGroupsUI.copy_row) — Показывает короткий адрес, метку и действия отдельной обычной копии.
- [CopyGroupsUI.edit_kind](#symbol-CopyGroupsUI.edit_kind) — Показывает смену типа обычной, сменной или облачной копии.
- [CopyGroupsUI.folder_menu](#symbol-CopyGroupsUI.folder_menu) — Создаёт команды настройки основной папки и отслеживания изменений.
- [CopyGroupsUI.location_name](#symbol-CopyGroupsUI.location_name) — Возвращает короткое название зарегистрированной папки.
- [CopyGroupsUI.location_path](#symbol-CopyGroupsUI.location_path) — Формирует подпись расположения с томом и относительным путём.
- [CopyGroupsUI.main_group](#symbol-CopyGroupsUI.main_group) — Определяет набор основной папки в текущей выбранной области.
- [CopyGroupsUI.main_row](#symbol-CopyGroupsUI.main_row) — Формирует компактную строку основной папки и её контекстные действия.
- [CopyGroupsUI.membership](#symbol-CopyGroupsUI.membership) — Находит наследуемую принадлежность пути зарегистрированной области.
- [CopyGroupsUI.open_copy](#symbol-CopyGroupsUI.open_copy) — Открывает зарегистрированную пару источника и копии.
- [CopyGroupsUI.open_main](#symbol-CopyGroupsUI.open_main) — Открывает основную папку в рабочем пространстве.
- [CopyGroupsUI.refresh](#symbol-CopyGroupsUI.refresh) — Загружает актуальные наборы, типы копий и смысловые метки через API.
- [CopyGroupsUI.register_main](#symbol-CopyGroupsUI.register_main) — Регистрирует выбранную папку как новую основную область 00-main.
- [CopyGroupsUI.release_number](#symbol-CopyGroupsUI.release_number) — Запрашивает подтверждение освобождения номера отключённой копии.
- [CopyGroupsUI.remove_copy](#symbol-CopyGroupsUI.remove_copy) — Удаляет подтверждённую связь копии из учёта через API.
- [CopyGroupsUI.remove_group](#symbol-CopyGroupsUI.remove_group) — Удаляет подтверждённый набор из учёта через API.
- [CopyGroupsUI.render_controls](#symbol-CopyGroupsUI.render_controls) — Обновляет быстрые команды учёта в правой колонке операций.
- [CopyGroupsUI.render_group](#symbol-CopyGroupsUI.render_group) — Показывает заголовок основной папки и раскрываемые строки её копий.
- [CopyGroupsUI.render_sidebar](#symbol-CopyGroupsUI.render_sidebar) — Перерисовывает подключённые и архивные наборы папок.
- [CopyGroupsUI.renumber](#symbol-CopyGroupsUI.renumber) — Показывает и подтверждает рассчитанные изменения номеров копий.
- [CopyGroupsUI.set_connection](#symbol-CopyGroupsUI.set_connection) — Подключает или отключает набор либо отдельную копию через API.
- [CopyGroupsUI.set_folder_settings](#symbol-CopyGroupsUI.set_folder_settings) — Сохраняет настройки набора и обновляет связанные сведения UI.
- [CopyGroupsUI.update_sidebar_title](#symbol-CopyGroupsUI.update_sidebar_title) — Показывает общий счётчик наборов папок с дисков и iCloud.
- [sidebar_sections](#symbol-sidebar_sections) — Разделяет наборы и копии на подключённые и архивные секции.

<a id="symbol-CopyGroupsUI"></a>

## `CopyGroupsUI`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI`

Показывает наборы папок и выполняет команды учёта через Core API. Зависимости конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `control_signature`, `controls`, `expanded`, `groups`, `workspace`.

Именованные методы: `__init__`, `build_sidebar`, `build_controls`, `location_name`, `location_path`, `membership`, `main_group`, `refresh`, `render_sidebar`, `update_sidebar_title`, `render_group`, `main_row`, `copy_row`, `folder_menu`, `set_folder_settings`, `acknowledge_changes`, `set_connection`, `render_controls`, `context_actions`, `changed`, `register_main`, `open_main`, `open_copy`, `choose_source`, `release_number`, `edit_kind`, `confirm_remove`, `renumber`, `remove_group`, `remove_copy`.

<a id="symbol-CopyGroupsUI.__init__"></a>

## `CopyGroupsUI.__init__`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.__init__`

Инициализирует CopyGroupsUI и его рабочее состояние. Обновляет состояние объекта: control_signature, controls, expanded, groups, workspace.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `control_signature`, `controls`, `expanded`, `groups`, `workspace`.

Прямые выражения вызова: `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.acknowledge_changes"></a>

## `CopyGroupsUI.acknowledge_changes`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.acknowledge_changes`

Подтверждает просмотр конкретной отметки изменения основной папки. Обрабатывает ошибки: Exception.

```python
async def acknowledge_changes(self, group)
```

Прямые выражения вызова: [self.refresh](copy_groups_ui.md#symbol-CopyGroupsUI.refresh), `ws.notice`, `ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.build_controls"></a>

## `CopyGroupsUI.build_controls`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.build_controls`

Создаёт контейнер команд назначения основной папки и копии. Обновляет состояние объекта: controls.

```python
def build_controls(self)
```

Присваивания полям `self`: `controls`.

Прямые выражения вызова: `ui.column`, `ui.column().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.build_sidebar"></a>

## `CopyGroupsUI.build_sidebar`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.build_sidebar`

Создаёт боковые секции основных папок и отключённых связей. Обновляет состояние объекта: disconnected, disconnected_list, list, section.

```python
def build_sidebar(self)
```

Присваивания полям `self`: `disconnected`, `disconnected_list`, `list`, `section`.

Прямые выражения вызова: `self.workspace.photo_libraries.build_cloud_groups`, `self.workspace.sidebar_expansion`, `ui.column`, `ui.column().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.changed"></a>

## `CopyGroupsUI.changed`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.changed`

Обновляет наборы, тома, медиатеки и видимые метки после изменения связей. Асинхронно ожидает: self.refresh.

```python
async def changed(self)
```

Прямые выражения вызова: `pane.render`, [self.refresh](copy_groups_ui.md#symbol-CopyGroupsUI.refresh), `self.workspace.update_scopes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.choose_source"></a>

## `CopyGroupsUI.choose_source`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.choose_source`

Показывает выбор основной или другой копии как источника назначения. Обрабатывает ошибки: Exception.

```python
async def choose_source(self, group, location)
```

Прямые выражения вызова: `c.get`, `location.get`, [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), [self.location_path](copy_groups_ui.md#symbol-CopyGroupsUI.location_path), `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.button('Сохранить', on_click=lambda: dialog.submit(selected.value)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Источник для ' + location['label']).classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(choices, value=current if current in choices else None, label='Копировать из').classes`, `ui.select(choices, value=current if current in choices else None, label='Копировать из').classes('w-full').props`, `ws.notice`, `ws.pair.unlink`, `ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.confirm_remove"></a>

## `CopyGroupsUI.confirm_remove`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.confirm_remove`

Показывает подтверждение удаления связей с явными путями папок. Использует self.location_path, ui.button, ui.button('Отмена', on_click=lambda : dialog.submit(False)).props и ещё 2.

```python
async def confirm_remove(self, title, *, locations=(), button_label='Удалить из учёта')
```

Прямые выражения вызова: [self.location_path](copy_groups_ui.md#symbol-CopyGroupsUI.location_path), `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button(button_label, on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Запись будет удалена из учёта приложения. Папки и файлы на дисках останутся.').classes`, `ui.label(location['label']).classes`, `ui.label(self.location_path(location)).classes`, `ui.label(title).classes`, `ui.row`, `ui.row().classes`.

Выражения возврата (ветви, без исполнения):

- `await dialog`


<a id="symbol-CopyGroupsUI.context_actions"></a>

## `CopyGroupsUI.context_actions`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.context_actions`

Предоставляет команды учёта для контекстного меню выбранной папки. Использует self.membership.

```python
def context_actions(self, volume_id, entry, *, index=None)
```

Прямые выражения вызова: `actions.append`, [self.membership](copy_groups_ui.md#symbol-CopyGroupsUI.membership), `ws.copy_setup.source`.

Выражения возврата (ветви, без исполнения):

- `[]`
- `actions`


<a id="symbol-CopyGroupsUI.copy_row"></a>

## `CopyGroupsUI.copy_row`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.copy_row`

Показывает короткий адрес, метку и действия отдельной обычной копии. Сохраняет историю и управление архивными привязками.

```python
def copy_row(self, group, location, *, depth=0, origin='')
```

Прямые выражения вызова: `actions.append`, `actions.extend`, `actions.insert`, `bool`, `disconnected`, `getattr`, `group.get`, `location.get`, [self.location_path](copy_groups_ui.md#symbol-CopyGroupsUI.location_path), `sidebar_line`, `ui.label`, `ui.label('Офлайн').classes`, `ws.property_menu`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.edit_kind"></a>

## `CopyGroupsUI.edit_kind`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.edit_kind`

Показывает смену типа обычной, сменной или облачной копии. Обрабатывает ошибки: Exception.

```python
async def edit_kind(self, location)
```

Прямые выражения вызова: [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Сохранить', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Тип копии · ' + location['label']).classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(COPY_KINDS, value=location['kind'], label='Тип копии').props`, `ui.select(COPY_KINDS, value=location['kind'], label='Тип копии').props('outlined dense').classes`, `ws.notice`, `ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.folder_menu"></a>

## `CopyGroupsUI.folder_menu`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.folder_menu`

Создаёт команды настройки основной папки и отслеживания изменений. Использует FOLDER_LABELS.items, action, group.get, str(bool(group.get('tracking'))).lower, str(group.get('label', '') == value).lower.

```python
def folder_menu(self, group, action)
```

Прямые выражения вызова: `FOLDER_LABELS.items`, `action`, `bool`, `group.get`, `str`, `str(bool(group.get('tracking'))).lower`, `str(group.get('label', '') == value).lower`, `ui.icon`, `ui.item_section`, `ui.item_section().props`, `ui.label`, `ui.label('Метка папки').classes`, `ui.menu_item`, `ui.menu_item(on_click=action(lambda v=value: self.set_folder_settings(group, label=v))).props`, `ui.menu_item(on_click=action(lambda: self.set_folder_settings(group, tracking=not group.get('tracking', False)))).props`, `ui.separator`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.location_name"></a>

## `CopyGroupsUI.location_name`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.location_name`

Возвращает короткое название зарегистрированной папки. Использует PurePosixPath.

```python
def location_name(location)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `PurePosixPath`.

Выражения возврата (ветви, без исполнения):

- `PurePosixPath(location['path']).name if location['path'] else location['volume_name']`


<a id="symbol-CopyGroupsUI.location_path"></a>

## `CopyGroupsUI.location_path`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.location_path`

Формирует подпись расположения с томом и относительным путём. Параметры: location.

```python
def location_path(location)
```

Декораторы: `staticmethod`.

Выражения возврата (ветви, без исполнения):

- `location['volume_name'] + ' /' + location['path']`


<a id="symbol-CopyGroupsUI.main_group"></a>

## `CopyGroupsUI.main_group`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.main_group`

Определяет набор основной папки в текущей выбранной области. Использует next.

```python
def main_group(self)
```

Прямые выражения вызова: `next`.

Выражения возврата (ветви, без исполнения):

- `None`
- `next((g for g in self.groups if g['main']['volume_id'] == left.volume_id and g['main']['path'] == left.path), None)`


<a id="symbol-CopyGroupsUI.main_row"></a>

## `CopyGroupsUI.main_row`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.main_row`

Формирует компактную строку основной папки и её контекстные действия. Подробности отслеживания и полный путь доступны в подсказке.

```python
def main_row(self, group, copies, toggle)
```

Прямые выражения вызова: `' · '.join`, `actions.insert`, `bool`, `detail.append`, `disconnected`, `getattr`, `group.get`, `len`, [self.location_name](copy_groups_ui.md#symbol-CopyGroupsUI.location_name), [self.location_path](copy_groups_ui.md#symbol-CopyGroupsUI.location_path), [self.membership](copy_groups_ui.md#symbol-CopyGroupsUI.membership), `sidebar_line`, `ui.label`, `ui.label(status).classes`, `ui.label(status).classes('sidebar-readout truncate').tooltip`, `ws.format_date`, `ws.property_menu`, `{'watching': 'Отслеживается', 'offline': 'Ожидает подключения', 'error': 'Отслеживание недоступно'}.get`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.membership"></a>

## `CopyGroupsUI.membership`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.membership`

Находит наследуемую принадлежность пути зарегистрированной области. Использует group.get, inherited_location, location.get.

```python
def membership(self, volume_id, path)
```

Прямые выражения вызова: `group.get`, `inherited_location`, `location.get`.

Выражения возврата (ветви, без исполнения):

- `inherited_location(path, locations)`


<a id="symbol-CopyGroupsUI.open_copy"></a>

## `CopyGroupsUI.open_copy`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.open_copy`

Открывает зарегистрированную пару источника и копии. Асинхронно ожидает: ws.pair.history, ws.pair.link.

```python
async def open_copy(self, group, location)
```

Прямые выражения вызова: `location.get`, `ws.pair.history`, `ws.pair.link`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.open_main"></a>

## `CopyGroupsUI.open_main`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.open_main`

Открывает основную папку в рабочем пространстве. Асинхронно ожидает: ws.browse, ws.pair.link, ws.pair.unlink, ws.panes[0].show_volume.

```python
async def open_main(self, group)
```

Прямые выражения вызова: `first_copy`, `ws.browse`, `ws.pair.link`, `ws.pair.unlink`, `ws.panes[0].show_volume`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopyGroupsUI.refresh"></a>

## `CopyGroupsUI.refresh`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.refresh`

Загружает актуальные наборы, типы копий и смысловые метки через API. Обновляет состояние объекта: groups.

```python
async def refresh(self)
```

Присваивания полям `self`: `groups`.

Прямые выражения вызова: [self.render_controls](copy_groups_ui.md#symbol-CopyGroupsUI.render_controls), [self.render_sidebar](copy_groups_ui.md#symbol-CopyGroupsUI.render_sidebar), `self.workspace.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.register_main"></a>

## `CopyGroupsUI.register_main`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.register_main`

Регистрирует выбранную папку как новую основную область 00-main. Обрабатывает ошибки: Exception.

```python
async def register_main(self, volume_id, path)
```

Прямые выражения вызова: [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), [self.open_main](copy_groups_ui.md#symbol-CopyGroupsUI.open_main), `self.section.open`, `ui.notify`, `ws.notice`, `ws.request`, `ws.volumes_section.close`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.release_number"></a>

## `CopyGroupsUI.release_number`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.release_number`

Запрашивает подтверждение освобождения номера отключённой копии. Обрабатывает ошибки: Exception.

```python
async def release_number(self, location)
```

Прямые выражения вызова: [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), `self.disconnected.open`, [self.location_path](copy_groups_ui.md#symbol-CopyGroupsUI.location_path), `ui.button`, `ui.button('Освободить номер', on_click=lambda: dialog.submit(True)).props`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Прежняя привязка и её история останутся в «Отключённых». Номер можно будет использовать для новой папки.').classes`, `ui.label(f"Освободить номер {location['number']:02d}?").classes`, `ui.label(location['label'] + ' · ' + self.location_path(location)).classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `ws.notice`, `ws.pair.unlink`, `ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopyGroupsUI.remove_copy"></a>

## `CopyGroupsUI.remove_copy`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.remove_copy`

Удаляет подтверждённую связь копии из учёта через API. Явно отклоняет недопустимое состояние через ValueError.

```python
async def remove_copy(self, location)
```

Прямые выражения вызова: `ValueError`, `group.get`, `next`, [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), [self.confirm_remove](copy_groups_ui.md#symbol-CopyGroupsUI.confirm_remove), [self.refresh](copy_groups_ui.md#symbol-CopyGroupsUI.refresh), [self.renumber](copy_groups_ui.md#symbol-CopyGroupsUI.renumber), `ws.notice`, `ws.pair.unlink`, `ws.request`.

Явные `raise`:

- `ValueError('Эта связь с копией уже убрана из учёта.')`

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.remove_group"></a>

## `CopyGroupsUI.remove_group`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.remove_group`

Удаляет подтверждённый набор из учёта через API. Обрабатывает ошибки: Exception.

```python
async def remove_group(self, group)
```

Прямые выражения вызова: [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), [self.confirm_remove](copy_groups_ui.md#symbol-CopyGroupsUI.confirm_remove), `ws.notice`, `ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.render_controls"></a>

## `CopyGroupsUI.render_controls`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.render_controls`

Обновляет быстрые команды учёта в правой колонке операций. Действие добавления открывает общий диалог выбора назначения.

```python
def render_controls(self)
```

Присваивания полям `self`: `control_signature`.

Прямые выражения вызова: `(getattr(ws.pair, 'group', None) or {}).get`, `(group or {}).get`, `(member or {}).get`, `(p.volume or {}).get`, `any`, `bool`, `getattr`, `group.get`, `next`, `self.controls.clear`, `self.controls.set_visibility`, [self.location_name](copy_groups_ui.md#symbol-CopyGroupsUI.location_name), [self.main_group](copy_groups_ui.md#symbol-CopyGroupsUI.main_group), [self.membership](copy_groups_ui.md#symbol-CopyGroupsUI.membership), `ui.button`, `ui.button('К основной папке', on_click=lambda: self.open_main(parent)).props`, `ui.button('Подключить набор', on_click=lambda: self.set_connection(group, True)).props`, `ui.button('Упорядочить номера копий', on_click=lambda: self.renumber(group)).props`, `ui.button('Упорядочить номера копий', on_click=lambda: self.renumber(group)).props('outline dense no-caps color=green-9').classes`, `ui.label`, `ui.label('00-main · ' + self.location_name(group['main'])).classes`, `ui.label('Учёт копий').classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopyGroupsUI.render_group"></a>

## `CopyGroupsUI.render_group`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.render_group`

Показывает заголовок основной папки и раскрываемые строки её копий. Ключ архивной строки хранится отдельно от ключа подключённого набора.

```python
def render_group(self, group, copies, *, archive=False)
```

Прямые выражения вызова: `branch_origin`, `branch_summary`, `copy_branches`, `group.get`, `len`, [self.copy_row](copy_groups_ui.md#symbol-CopyGroupsUI.copy_row), `sidebar_branch`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.render_sidebar"></a>

## `CopyGroupsUI.render_sidebar`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.render_sidebar`

Перерисовывает подключённые и архивные наборы папок. Использует self.disconnected.set_visibility, self.disconnected_list.clear, self.list.clear, self.render_group, sidebar_sections.

```python
def render_sidebar(self)
```

Прямые выражения вызова: `bool`, `self.disconnected.set_visibility`, `self.disconnected_list.clear`, `self.list.clear`, [self.render_group](copy_groups_ui.md#symbol-CopyGroupsUI.render_group), [self.update_sidebar_title](copy_groups_ui.md#symbol-CopyGroupsUI.update_sidebar_title), [sidebar_sections](copy_groups_ui.md#symbol-sidebar_sections).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.renumber"></a>

## `CopyGroupsUI.renumber`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.renumber`

Показывает и подтверждает рассчитанные изменения номеров копий. Обрабатывает ошибки: Exception.

```python
async def renumber(self, group)
```

Прямые выражения вызова: `next`, [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), [self.location_name](copy_groups_ui.md#symbol-CopyGroupsUI.location_name), [self.location_path](copy_groups_ui.md#symbol-CopyGroupsUI.location_path), [self.refresh](copy_groups_ui.md#symbol-CopyGroupsUI.refresh), `ui.button`, `ui.button('Переименовать метки', on_click=lambda: dialog.submit(True)).props`, `ui.button('Позже', on_click=lambda: dialog.submit(False)).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Изменятся только метки связей. Имена папок на дисках сохранятся.').classes`, `ui.label('Упорядочить номера копий?').classes`, `ui.label(change['from_label'] + ' → ' + change['to_label']).classes`, `ui.label(self.location_name(group['main'])).classes`, `ui.label(self.location_path(by_id[change['id']])).classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `ws.notice`, `ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopyGroupsUI.set_connection"></a>

## `CopyGroupsUI.set_connection`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.set_connection`

Подключает или отключает набор либо отдельную копию через API. Явно отклоняет недопустимое состояние через ValueError.

```python
async def set_connection(self, group, connected, location=None)
```

Прямые выражения вызова: `ValueError`, `getattr`, [self.changed](copy_groups_ui.md#symbol-CopyGroupsUI.changed), `self.disconnected.open`, `ws.notice`, `ws.pair.unlink`, `ws.request`.

Явные `raise`:

- `ValueError('Сначала дождись завершения копирования.')`

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.set_folder_settings"></a>

## `CopyGroupsUI.set_folder_settings`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.set_folder_settings`

Сохраняет настройки набора и обновляет связанные сведения UI. Обрабатывает ошибки: Exception.

```python
async def set_folder_settings(self, group, **settings)
```

Прямые выражения вызова: [self.refresh](copy_groups_ui.md#symbol-CopyGroupsUI.refresh), `ws.notice`, `ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyGroupsUI.update_sidebar_title"></a>

## `CopyGroupsUI.update_sidebar_title`

[copy_groups_ui.py](../../copy_groups_ui.py) · `CopyGroupsUI.update_sidebar_title`

Показывает общий счётчик наборов папок с дисков и iCloud. Пересчитывается при изменении любой из двух частей списка.

```python
def update_sidebar_title(self)
```

Прямые выражения вызова: `len`, `self.workspace.photo_libraries.cloud_groups`, [sidebar_sections](copy_groups_ui.md#symbol-sidebar_sections).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sidebar_sections"></a>

## `sidebar_sections`

[copy_groups_ui.py](../../copy_groups_ui.py) · `sidebar_sections`

Разделяет наборы и копии на подключённые и архивные секции. Использует active.append, disconnected, group.get, offline.append.

```python
def sidebar_sections(groups)
```

Прямые выражения вызова: `active.append`, `disconnected`, `group.get`, `int`, `len`, `offline.append`.

Выражения возврата (ветви, без исполнения):

- `(active, offline, count)`
