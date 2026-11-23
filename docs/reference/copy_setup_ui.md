# Выбор назначения копии: `copy_setup_ui.py`

Общий диалог связывает обычную папку, Photos или iCloud Drive с папкой на диске. Показывает цепочку Photos и принимает папку из соседней панели.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../copy_setup_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/copies.py](media_manager--copies.md), [media_manager/icloud_copies.py](media_manager--icloud_copies.md), [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [CopySetupUI](#symbol-CopySetupUI) — Управляет общим диалогом «Из → Куда» и обновляет созданные связи.
- [CopySetupUI.__init__](#symbol-CopySetupUI.__init__) — Сохраняет рабочее пространство и состояние диалога.
- [CopySetupUI.destination](#symbol-CopySetupUI.destination) — Показывает источник, маршрут и выбор папки назначения в одном диалоге.
- [CopySetupUI.destination.change_volume](#symbol-CopySetupUI.destination.change_volume) — Обрабатывает выбор тома только для актуального значения поля.
- [CopySetupUI.destination.navigate](#symbol-CopySetupUI.destination.navigate) — Загружает дочерние папки по выбранному адресу и игнорирует запоздалый ответ.
- [CopySetupUI.destination.submit](#symbol-CopySetupUI.destination.submit) — Отправляет подтверждённую связь и оставляет поля доступными для исправления ошибки.
- [CopySetupUI.destination.update_origin](#symbol-CopySetupUI.destination.update_origin) — Показывает фактический путь передачи и выбранную область iCloud.
- [CopySetupUI.open](#symbol-CopySetupUI.open) — Открывает диалог и показывает созданную строку копии после принятой связи.
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


<a id="symbol-CopySetupUI"></a>

## `CopySetupUI`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI`

Управляет общим диалогом «Из → Куда» и обновляет созданные связи. Зависимость конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `opened`, `ws`.

Именованные методы: `__init__`, `source`, `suggested`, `open`, `save`, `destination`.

<a id="symbol-CopySetupUI.__init__"></a>

## `CopySetupUI.__init__`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.__init__`

Сохраняет рабочее пространство и состояние диалога. Обновляет состояние объекта: ws, opened.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `opened`, `ws`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.destination"></a>

## `CopySetupUI.destination`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination`

Показывает источник, маршрут и выбор папки назначения в одном диалоге. Сохраняет окно открытым при ошибке чтения или отказе Core.

```python
async def destination(self, source, volumes, suggestion, preferred_kind)
```

Прямые выражения вызова: `all_cloud.on_value_change`, `back.disable`, `confirm.disable`, `copy.get`, `dict`, `iter`, `next`, `problem.set_visibility`, [scope_title](copy_setup_ui.md#symbol-scope_title), `selector.on_value_change`, `self.ws.resolve_volume`, `shortcut.tooltip`, `sorted`, `source.get`, `ui.button`, `ui.button('Из соседней панели', on_click=lambda: navigate(**suggestion)).props`, `ui.button('Из соседней панели', on_click=lambda: navigate(**suggestion)).props('flat dense no-caps color=green-9').classes`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.button('Сохранить связь', on_click=submit).props`, `ui.button(icon='arrow_upward', on_click=lambda: navigate(state['volume_id'], relative_path(str(PurePosixPath(state['path']).parent)))).props`, `ui.card`, `ui.card().classes`, `ui.checkbox`, `ui.checkbox('Весь iCloud Drive', value=False).props`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.dialog().props`, `ui.label`, `ui.label('Добавить копию').classes`, `ui.label('Из').classes`, `ui.label('Куда').classes`, `ui.label().classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(COPY_KINDS, value=preferred_kind or 'copy', label='Тип копии').props`, `ui.select(COPY_KINDS, value=preferred_kind or 'copy', label='Тип копии').props('dense outlined options-dense').classes`, `ui.select(upstream_choices, value=(direct or all_copies[0])['id'], label='Копировать из').props`, `ui.select(upstream_choices, value=(direct or all_copies[0])['id'], label='Копировать из').props('dense outlined options-dense').classes`, `ui.select({i: scope_title(v, '') for i, v in volumes.items()}, label='Том назначения').props`, `ui.select({i: scope_title(v, '') for i, v in volumes.items()}, label='Том назначения').props('dense outlined options-dense').classes`, `ui.timer`, `update_origin`, `upstream.on_value_change`, `volumes.items`.

Выражения возврата (ветви, без исполнения):

- `await dialog`


<a id="symbol-CopySetupUI.destination.change_volume"></a>

## `CopySetupUI.destination.change_volume`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.change_volume`

Обрабатывает выбор тома только для актуального значения поля. Асинхронно ожидает: navigate.

```python
async def change_volume(event)
```

Прямые выражения вызова: [navigate](copy_setup_ui.md#symbol-CopySetupUI.destination.navigate).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.destination.navigate"></a>

## `CopySetupUI.destination.navigate`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.navigate`

Загружает дочерние папки по выбранному адресу и игнорирует запоздалый ответ. Обновляет текущий путь, возможность сохранения и предложенный тип копии.

```python
async def navigate(volume_id, path='')
```

Прямые выражения вызова: `ValueError`, `back.set_enabled`, `bool`, `confirm.disable`, `confirm.set_enabled`, `data.get`, `folders.clear`, `kind.set_value`, `problem.set_visibility`, [scope_title](copy_setup_ui.md#symbol-scope_title), `selector.set_value`, `self.ws.error_text`, `self.ws.read_directory`, `state.update`, `ui.button`, `ui.button(item['name'], icon='folder', on_click=lambda p=item['path']: navigate(volume_id, p)).props`, `ui.button(item['name'], icon='folder', on_click=lambda p=item['path']: navigate(volume_id, p)).props('flat dense no-caps color=dark').classes`, `ui.label`, `ui.label('Вложенных папок нет').classes`, `ui.spinner`, `ui.spinner(size='18px').classes`, `volumes[volume_id].get`.

Явные `raise`:

- `ValueError(data.get('error') or 'Папка назначения сейчас недоступна.')`

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.destination.submit"></a>

## `CopySetupUI.destination.submit`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.destination.submit`

Отправляет подтверждённую связь и оставляет поля доступными для исправления ошибки. Асинхронно ожидает: self.save.

```python
async def submit()
```

Прямые выражения вызова: `back.set_enabled`, `bool`, `control.disable`, `control.enable`, `dialog.submit`, `problem.set_visibility`, [self.save](copy_setup_ui.md#symbol-CopySetupUI.save), `self.ws.error_text`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


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

Открывает диалог и показывает созданную строку копии после принятой связи. Асинхронно ожидает: self.destination, self.ws.copies.changed, self.ws.photo_libraries.refresh.

```python
async def open(self, volume_id, path='', *, index=None, preferred_kind=None)
```

Присваивания полям `self`: `opened`.

Прямые выражения вызова: [copy_volume](copy_setup_ui.md#symbol-copy_volume), `libraries.expanded.add`, `libraries.refresh`, `libraries.section.open`, [self.destination](copy_setup_ui.md#symbol-CopySetupUI.destination), [self.source](copy_setup_ui.md#symbol-CopySetupUI.source), [self.suggested](copy_setup_ui.md#symbol-CopySetupUI.suggested), `self.ws.copies.changed`, `self.ws.copies.expanded.add`, `self.ws.copies.section.open`, `self.ws.notice`, `ui.notify`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.save"></a>

## `CopySetupUI.save`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.save`

Сохраняет настроенную связь через API соответствующего источника. Асинхронно ожидает: self.ws.request.

```python
async def save(self, source, target, kind, upstream, cloud_root)
```

Прямые выражения вызова: `dict`, `self.ws.request`.

Выражения возврата (ветви, без исполнения):

- `await self.ws.request('POST', '/api/storage/folder-copy-bindings', json=dict(source=origin, destination=dict(target, kind=kind)))`
- `await self.ws.request('POST', f"/api/photos/libraries/{source['library']['id']}/copies", json=dict(target, source_link_id=upstream or None))`
- `await self.ws.request('POST', '/api/icloud/copies', json=dict(target, source_path='' if cloud_root else source['path']))`


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

Прямые выражения вызова: `' → '.join`, `copy.get`, `library.get`, `nodes.append`, `reversed`, `seen.add`, `set`.

Выражения возврата (ветви, без исполнения):

- `' → '.join(reversed(nodes))`


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
