# Выбор источника и назначения копии: `copy_setup_ui.py`

Общий диалог выбирает папку, медиатеку или область iCloud Drive и связывает её с папкой на диске. Один навигатор используется для обоих путей.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../copy_setup_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [copy_panels.py](copy_panels.md), [media_manager/copies.py](media_manager--copies.md), [media_manager/icloud_copies.py](media_manager--icloud_copies.md), [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [CopyFolderPicker](#symbol-CopyFolderPicker) — Показывает текущий путь и дочерние папки для выбора источника или назначения.
- [CopyFolderPicker.__init__](#symbol-CopyFolderPicker.__init__) — Создаёт общие элементы навигации, списка папок и сообщения об ошибке.
- [CopyFolderPicker.navigate](#symbol-CopyFolderPicker.navigate) — Загружает список вложенных папок без чтения файлов и отмечает проверенный адрес.
- [CopyFolderPicker.parent](#symbol-CopyFolderPicker.parent) — Открывает родительскую папку на текущем томе.
- [CopyFolderPicker.set_locked](#symbol-CopyFolderPicker.set_locked) — Блокирует навигацию и отменяет применение запоздалого ответа при закрытии.
- [CopySetupUI](#symbol-CopySetupUI) — Управляет общим диалогом «Из → Куда» и обновляет созданные связи.
- [CopySetupUI.__init__](#symbol-CopySetupUI.__init__) — Сохраняет рабочее пространство и состояние диалога.
- [CopySetupUI.choose_cloud_folder](#symbol-CopySetupUI.choose_cloud_folder) — Позволяет выбрать вложенную папку iCloud Drive по её точному адресу.
- [CopySetupUI.choose_cloud_folder.changed](#symbol-CopySetupUI.choose_cloud_folder.changed) — Разрешает выбор после подтверждённого чтения конкретной вложенной папки.
- [CopySetupUI.destination](#symbol-CopySetupUI.destination) — Показывает источник, маршрут и выбор папки назначения в одном диалоге.
- [CopySetupUI.destination.browse_source](#symbol-CopySetupUI.destination.browse_source) — Открывает выбор папки и применяет только подтверждённый адрес.
- [CopySetupUI.destination.can_save](#symbol-CopySetupUI.destination.can_save) — Проверяет оба адреса и состояние диалога перед сохранением связи.
- [CopySetupUI.destination.change_source](#symbol-CopySetupUI.destination.change_source) — Подписывает выбранную область и обновляет доступность сохранения.
- [CopySetupUI.destination.change_volume](#symbol-CopySetupUI.destination.change_volume) — Обрабатывает выбор тома только для актуального значения поля.
- [CopySetupUI.destination.submit](#symbol-CopySetupUI.destination.submit) — Отправляет подтверждённую связь и оставляет поля доступными для исправления ошибки.
- [CopySetupUI.destination.update_destination](#symbol-CopySetupUI.destination.update_destination) — Согласует выбранный том, предложенный тип копии и доступность сохранения.
- [CopySetupUI.destination.update_origin](#symbol-CopySetupUI.destination.update_origin) — Показывает фактический путь передачи и выбранную область iCloud.
- [CopySetupUI.open](#symbol-CopySetupUI.open) — Открывает диалог, обновляет боковой список и показывает созданную пару.
- [CopySetupUI.save](#symbol-CopySetupUI.save) — Сохраняет настроенную связь через API соответствующего источника.
- [CopySetupUI.source](#symbol-CopySetupUI.source) — Определяет допустимый источник из дерева, бокового списка или панели операций.
- [CopySetupUI.suggested](#symbol-CopySetupUI.suggested) — Выбирает доступную папку из панели напротив источника как быстрый вариант назначения.
- [copy_volume](#symbol-copy_volume) — Определяет подключённый том, пригодный для выбора папки копии.
- [photo_route](#symbol-photo_route) — Показывает адрес и предыдущие звенья выбранной копии Photos.
- [scope_title](#symbol-scope_title) — Формирует читаемый путь по короткому имени тома и пути внутри него.

## Константы и значения по умолчанию

<a id="constant-COPY_SETUP_CSS"></a>

### `COPY_SETUP_CSS`

`Объёмное значение см. в исходном модуле`


<a id="symbol-CopyFolderPicker"></a>

## `CopyFolderPicker`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopyFolderPicker`

Показывает текущий путь и дочерние папки для выбора источника или назначения. Передаёт изменения адреса и доступности диалогу, который принимает выбор.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `address`, `back`, `changed`, `folders`, `generation`, `locked`, `path`, `problem`, `ready`, `volume_id`, `volumes`, `ws`.

Именованные методы: `__init__`, `set_locked`, `parent`, `navigate`.

<a id="symbol-CopyFolderPicker.__init__"></a>

## `CopyFolderPicker.__init__`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopyFolderPicker.__init__`

Создаёт общие элементы навигации, списка папок и сообщения об ошибке. Принимает разрешённые тома и обработчик изменения выбора.

```python
def __init__(self, workspace, volumes, changed, *, up_label)
```

Присваивания полям `self`: `address`, `back`, `changed`, `folders`, `generation`, `locked`, `path`, `problem`, `ready`, `volume_id`, `volumes`, `ws`.

Прямые выражения вызова: `self.back.disable`, `self.problem.set_visibility`, `ui.button`, `ui.button(icon='arrow_upward', on_click=self.parent).props`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label().classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyFolderPicker.navigate"></a>

## `CopyFolderPicker.navigate`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopyFolderPicker.navigate`

Загружает список вложенных папок без чтения файлов и отмечает проверенный адрес. Игнорирует ответ, если пользователь перешёл дальше или закрыл диалог.

```python
async def navigate(self, volume_id, path='')
```

Присваивания полям `self`: `generation`, `path`, `ready`, `volume_id`.

Прямые выражения вызова: `ValueError`, `bool`, `data.get`, [scope_title](copy_setup_ui.md#symbol-scope_title), `self.back.set_enabled`, `self.changed`, `self.folders.clear`, `self.problem.set_visibility`, `self.ws.error_text`, `self.ws.read_directory`, `ui.button`, `ui.button('Повторить', icon='refresh', on_click=lambda: self.navigate(volume_id, path)).props`, `ui.button('Повторить', icon='refresh', on_click=lambda: self.navigate(volume_id, path)).props('flat dense no-caps color=dark').classes`, `ui.button(item['name'], icon='folder', on_click=lambda p=item['path']: self.navigate(volume_id, p)).props`, `ui.button(item['name'], icon='folder', on_click=lambda p=item['path']: self.navigate(volume_id, p)).props('flat dense no-caps color=dark').classes`, `ui.label`, `ui.label('Вложенных папок нет').classes`, `ui.spinner`, `ui.spinner(size='18px').classes`.

Явные `raise`:

- `ValueError(data.get('error') or 'Папка сейчас недоступна.')`

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopyFolderPicker.parent"></a>

## `CopyFolderPicker.parent`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopyFolderPicker.parent`

Открывает родительскую папку на текущем томе. Оставляет корень верхней границей выбора.

```python
async def parent(self)
```

Прямые выражения вызова: `PurePosixPath`, `relative_path`, [self.navigate](copy_setup_ui.md#symbol-CopyFolderPicker.navigate), `str`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopyFolderPicker.set_locked"></a>

## `CopyFolderPicker.set_locked`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopyFolderPicker.set_locked`

Блокирует навигацию и отменяет применение запоздалого ответа при закрытии. Обновляет доступность перехода в родительскую папку.

```python
def set_locked(self, locked)
```

Присваивания полям `self`: `generation`, `locked`.

Прямые выражения вызова: `bool`, `self.back.set_enabled`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI"></a>

## `CopySetupUI`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI`

Управляет общим диалогом «Из → Куда» и обновляет созданные связи. Зависимость конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `opened`, `ws`.

Именованные методы: `__init__`, `source`, `suggested`, `open`, `save`, `choose_cloud_folder`, `destination`.

<a id="symbol-CopySetupUI.__init__"></a>

## `CopySetupUI.__init__`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.__init__`

Сохраняет рабочее пространство и состояние диалога. Обновляет состояние объекта: ws, opened.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `opened`, `ws`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.choose_cloud_folder"></a>

## `CopySetupUI.choose_cloud_folder`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.choose_cloud_folder`

Позволяет выбрать вложенную папку iCloud Drive по её точному адресу. Возвращает подтверждённый путь или None после отмены.

```python
async def choose_cloud_folder(self, volume, path)
```

Прямые выражения вызова: [CopyFolderPicker](copy_setup_ui.md#symbol-CopyFolderPicker), `choose.disable`, `dialog.delete`, `picker.set_locked`, `ui.button`, `ui.button('Выбрать эту папку', on_click=lambda: dialog.submit(picker.path) if picker.ready and picker.path else None).props`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.dialog().props`, `ui.label`, `ui.label('Выбрать папку iCloud Drive').classes`, `ui.row`, `ui.row().classes`, `ui.timer`.

Выражения возврата (ветви, без исполнения):

- `await dialog`


<a id="symbol-CopySetupUI.choose_cloud_folder.changed"></a>

## `CopySetupUI.choose_cloud_folder.changed`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.choose_cloud_folder.changed`

Разрешает выбор после подтверждённого чтения конкретной вложенной папки. Корень выбирается отдельной командой в основном диалоге.

```python
def changed()
```

Прямые выражения вызова: `bool`, `choose.set_enabled`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.destination"></a>

## `CopySetupUI.destination`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination`

Показывает источник, маршрут и выбор папки назначения в одном диалоге. Сохраняет окно открытым при ошибке чтения или отказе Core.

```python
async def destination(self, source, volumes, suggestion, preferred_kind)
```

Прямые выражения вызова: [CopyFolderPicker](copy_setup_ui.md#symbol-CopyFolderPicker), `confirm.disable`, `copy.get`, `dialog.delete`, `dict`, `iter`, `next`, `picker.set_locked`, `problem.set_visibility`, [scope_title](copy_setup_ui.md#symbol-scope_title), `selector.on_value_change`, `self.ws.resolve_volume`, `shortcut.tooltip`, `sorted`, `source.get`, `ui.button`, `ui.button('Весь iCloud Drive', on_click=lambda: change_source('')).props`, `ui.button('Выбрать папку…', icon='folder_open', on_click=browse_source).props`, `ui.button('Из соседней панели', on_click=lambda: picker.navigate(**suggestion)).props`, `ui.button('Из соседней панели', on_click=lambda: picker.navigate(**suggestion)).props('flat dense no-caps color=green-9').classes`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.button('Сохранить связь', on_click=submit).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.dialog().props`, `ui.label`, `ui.label('Добавить копию').classes`, `ui.label('Из').classes`, `ui.label('Куда').classes`, `ui.label().classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(COPY_KINDS, value=preferred_kind or 'copy', label='Тип копии').props`, `ui.select(COPY_KINDS, value=preferred_kind or 'copy', label='Тип копии').props('dense outlined options-dense').classes`, `ui.select(upstream_choices, value=(direct or all_copies[0])['id'], label='Копировать из').props`, `ui.select(upstream_choices, value=(direct or all_copies[0])['id'], label='Копировать из').props('dense outlined options-dense').classes`, `ui.select({i: scope_title(v, '') for i, v in volumes.items()}, label='Том назначения').props`, `ui.select({i: scope_title(v, '') for i, v in volumes.items()}, label='Том назначения').props('dense outlined options-dense').classes`, `ui.timer`, `update_origin`, `upstream.on_value_change`, `volumes.items`.

Выражения возврата (ветви, без исполнения):

- `await dialog`


<a id="symbol-CopySetupUI.destination.browse_source"></a>

## `CopySetupUI.destination.browse_source`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.browse_source`

Открывает выбор папки и применяет только подтверждённый адрес. После отмены сохраняет прежнюю область.

```python
async def browse_source()
```

Прямые выражения вызова: [can_save](copy_setup_ui.md#symbol-CopySetupUI.destination.can_save), [change_source](copy_setup_ui.md#symbol-CopySetupUI.destination.change_source), `confirm.disable`, `confirm.set_enabled`, [self.choose_cloud_folder](copy_setup_ui.md#symbol-CopySetupUI.choose_cloud_folder).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.destination.can_save"></a>

## `CopySetupUI.destination.can_save`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.can_save`

Проверяет оба адреса и состояние диалога перед сохранением связи. Для iCloud отличает отсутствие выбора от явно выбранного корня.

```python
def can_save()
```

Прямые выражения вызова: `bool`.

Выражения возврата (ветви, без исполнения):

- `source_path is not None and picker.ready and bool(picker.path) and ((picker.volume_id, picker.path) != (source['volume_id'], source_path)) and (not (state['saving'] or state['selecting_source']))`


<a id="symbol-CopySetupUI.destination.change_source"></a>

## `CopySetupUI.destination.change_source`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.change_source`

Подписывает выбранную область и обновляет доступность сохранения. Пустой путь iCloud показывает как весь облачный диск.

```python
def change_source(path)
```

Прямые выражения вызова: [can_save](copy_setup_ui.md#symbol-CopySetupUI.destination.can_save), `confirm.set_enabled`, `problem.set_visibility`, [update_origin](copy_setup_ui.md#symbol-CopySetupUI.destination.update_origin).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.destination.change_volume"></a>

## `CopySetupUI.destination.change_volume`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.change_volume`

Обрабатывает выбор тома только для актуального значения поля. Асинхронно ожидает: picker.navigate.

```python
async def change_volume(event)
```

Прямые выражения вызова: `picker.navigate`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.destination.submit"></a>

## `CopySetupUI.destination.submit`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.submit`

Отправляет подтверждённую связь и оставляет поля доступными для исправления ошибки. Асинхронно ожидает: self.save.

```python
async def submit()
```

Прямые выражения вызова: [can_save](copy_setup_ui.md#symbol-CopySetupUI.destination.can_save), `confirm.set_enabled`, `control.disable`, `control.enable`, `dialog.submit`, `dict`, `picker.set_locked`, `problem.set_visibility`, [self.save](copy_setup_ui.md#symbol-CopySetupUI.save), `self.ws.error_text`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.destination.update_destination"></a>

## `CopySetupUI.destination.update_destination`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.update_destination`

Согласует выбранный том, предложенный тип копии и доступность сохранения. Сбрасывает ошибку сохранения, когда меняется назначение.

```python
def update_destination()
```

Прямые выражения вызова: [can_save](copy_setup_ui.md#symbol-CopySetupUI.destination.can_save), `confirm.set_enabled`, `kind.set_value`, `problem.set_visibility`, `selector.set_value`, `volumes[volume_id].get`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.destination.update_origin"></a>

## `CopySetupUI.destination.update_origin`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.update_origin`

Показывает фактический путь передачи и выбранную область iCloud. Использует photo_route для отображения промежуточных звеньев.

```python
def update_origin()
```

Прямые выражения вызова: [photo_route](copy_setup_ui.md#symbol-photo_route), [scope_title](copy_setup_ui.md#symbol-scope_title).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.open"></a>

## `CopySetupUI.open`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.open`

Открывает диалог, обновляет боковой список и показывает созданную пару. Выбирает именно сохранённое назначение, даже если у источника уже есть копии.

```python
async def open(self, volume_id, path='', *, index=None, preferred_kind=None)
```

Присваивания полям `self`: `opened`.

Прямые выражения вызова: `all`, [copy_volume](copy_setup_ui.md#symbol-copy_volume), `libraries.expanded.add`, `libraries.open_copy`, `libraries.refresh`, `libraries.section.open`, `next`, [self.destination](copy_setup_ui.md#symbol-CopySetupUI.destination), [self.source](copy_setup_ui.md#symbol-CopySetupUI.source), [self.suggested](copy_setup_ui.md#symbol-CopySetupUI.suggested), `self.ws.copies.changed`, `self.ws.copies.expanded.add`, `self.ws.copies.open_copy`, `self.ws.copies.section.open`, `self.ws.notice`, `target.items`, `ui.notify`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.save"></a>

## `CopySetupUI.save`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.save`

Сохраняет настроенную связь через API соответствующего источника. Для iCloud сохраняет выбранный путь, включая явно выбранный корень.

```python
async def save(self, source, target, kind, upstream)
```

Прямые выражения вызова: `dict`, `self.ws.request`.

Выражения возврата (ветви, без исполнения):

- `await self.ws.request('POST', '/api/storage/folder-copy-bindings', json=dict(source=origin, destination=dict(target, kind=kind)))`
- `await self.ws.request('POST', f"/api/photos/libraries/{source['library']['id']}/copies", json=dict(target, source_link_id=upstream or None))`
- `await self.ws.request('POST', '/api/icloud/copies', json=dict(target, source_path=source['path']))`


<a id="symbol-CopySetupUI.source"></a>

## `CopySetupUI.source`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.source`

Определяет допустимый источник из дерева, бокового списка или панели операций. Для Photos выбирает всю медиатеку, для iCloud Drive сохраняет выбранную папку.

```python
def source(self, volume_id, path, entry_kind='directory')
```

Прямые выражения вызова: [copy_volume](copy_setup_ui.md#symbol-copy_volume), `dict`, `self.ws.copies.membership`, `self.ws.resolve_volume`.

Выражения возврата (ветви, без исполнения):

- `None`
- `dict(kind='photos', volume_id=volume_id, path='', library=volume['library'])`
- `dict(kind='icloud', volume_id=volume_id, path=path)`
- `dict(kind='folder', volume_id=volume_id, path=path)`


<a id="symbol-CopySetupUI.suggested"></a>

## `CopySetupUI.suggested`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.suggested`

Выбирает доступную папку из панели напротив источника как быстрый вариант назначения. Поддерживает вызов из любого дерева и из боковой колонки.

```python
def suggested(self, source, index)
```

Прямые выражения вызова: [copy_volume](copy_setup_ui.md#symbol-copy_volume), `next`, `self.ws.panes[1 - index].scope`, `self.ws.resolve_volume`.

Выражения возврата (ветви, без исполнения):

- `scope`
- `None`


<a id="symbol-copy_volume"></a>

## `copy_volume`

[copy_setup_ui.py](../../copy_setup_ui.py) · `copy_volume`

Определяет подключённый том, пригодный для выбора папки копии. Проверяет сохранённую идентичность и доступность.

```python
def copy_volume(volume)
```

Прямые выражения вызова: `bool`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `bool(volume and volume['kind'] not in ('photos', 'icloud') and (volume['availability'] == 'online') and (volume.get('identity_status') not in ('unverified', 'legacy')))`


<a id="symbol-photo_route"></a>

## `photo_route`

[copy_setup_ui.py](../../copy_setup_ui.py) · `photo_route`

Показывает адрес и предыдущие звенья выбранной копии Photos. Недоступное звено отображается отдельно от прямого маршрута Photos.

```python
def photo_route(library, link_id)
```

Прямые выражения вызова: `' → '.join`, `copy_route`, `dict`, `library.get`, `next`.

Выражения возврата (ветви, без исполнения):

- `label`
- `'Недоступный источник'`
- `' → '.join((node['label'] for node in route))`


<a id="symbol-scope_title"></a>

## `scope_title`

[copy_setup_ui.py](../../copy_setup_ui.py) · `scope_title`

Формирует читаемый путь по короткому имени тома и пути внутри него. Возвращает имя тома для корня.

```python
def scope_title(volume, path)
```

Прямые выражения вызова: `volume.get`.

Выражения возврата (ветви, без исполнения):

- `f'{name} /{path}' if path else name`
