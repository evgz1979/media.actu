# Выбор источника и назначения копии: `copy_setup_ui.py`

Закрепляет папку, медиатеку или область iCloud Drive слева, принимает назначение из правого дерева и сохраняет маршрут копии.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../copy_setup_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [copy_panels.py](copy_panels.md), [media_manager/copies.py](media_manager--copies.md), [media_manager/icloud_copies.py](media_manager--icloud_copies.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [CopySetupUI](#symbol-CopySetupUI) — Управляет выбором готовой папки назначения в правом дереве.
- [CopySetupUI.__init__](#symbol-CopySetupUI.__init__) — Инициализирует состояние выбора и защищает создание от двойного нажатия.
- [CopySetupUI.build](#symbol-CopySetupUI.build) — Размещает путь, тип и подтверждение в отдельной центральной колонке.
- [CopySetupUI.cancel](#symbol-CopySetupUI.cancel) — Отменяет выбор и возвращает прежний отчёт или связанную пару, если они были открыты.
- [CopySetupUI.clear](#symbol-CopySetupUI.clear) — Убирает редактор и возвращает обычные команды панелей.
- [CopySetupUI.describe](#symbol-CopySetupUI.describe) — Подписывает полный маршрут от корня до выбранного источника.
- [CopySetupUI.open](#symbol-CopySetupUI.open) — Переводит рабочее пространство в выбор назначения между двумя деревьями.
- [CopySetupUI.refresh](#symbol-CopySetupUI.refresh) — Отображает выбранное назначение и доступность подтверждения без пересборки деревьев.
- [CopySetupUI.save](#symbol-CopySetupUI.save) — Сохраняет связь через API выбранного источника.
- [CopySetupUI.show_saved](#symbol-CopySetupUI.show_saved) — Обновляет боковую колонку и открывает именно сохранённое назначение.
- [CopySetupUI.source](#symbol-CopySetupUI.source) — Определяет выбранный источник и его роль в цепочке.
- [CopySetupUI.submit](#symbol-CopySetupUI.submit) — Проверяет выбранную папку и сохраняет связь, затем показывает созданную пару.
- [CopySetupUI.target](#symbol-CopySetupUI.target) — Выбирает правую папку, если том доступен и пути не пересекаются.
- [copy_origin_route](#symbol-copy_origin_route) — Показывает адрес и предыдущие звенья выбранной копии.
- [copy_volume](#symbol-copy_volume) — Определяет подключённый том, пригодный для назначения копии.
- [scope_title](#symbol-scope_title) — Формирует читаемый путь по короткому имени тома и пути внутри него.

## Константы и значения по умолчанию

<a id="constant-COPY_SETUP_CSS"></a>

### `COPY_SETUP_CSS`

`Объёмное значение см. в исходном модуле`


<a id="symbol-CopySetupUI"></a>

## `CopySetupUI`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI`

Управляет выбором готовой папки назначения в правом дереве. Держит источник и тип копии до явного сохранения или отмены.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `destination_key`, `draft`, `opening`, `previous`, `saving`, `ws`.

Именованные методы: `__init__`, `build`, `source`, `describe`, `target`, `refresh`, `open`, `clear`, `cancel`, `submit`, `save`, `show_saved`.

<a id="symbol-CopySetupUI.__init__"></a>

## `CopySetupUI.__init__`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.__init__`

Инициализирует состояние выбора и защищает создание от двойного нажатия. Состояние черновика хранится только на открытой странице.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `destination_key`, `draft`, `opening`, `previous`, `saving`, `ws`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.build"></a>

## `CopySetupUI.build`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.build`

Размещает путь, тип и подтверждение в отдельной центральной колонке. Обе панели остаются обычными деревьями во время выбора.

```python
def build(self)
```

Присваивания полям `self`: `cancel_button`, `confirm`, `destination`, `kind`, `origin`, `panel`, `problem`.

Прямые выражения вызова: `self.panel.set_visibility`, `self.problem.set_visibility`, `ui.button`, `ui.button('Отмена', on_click=self.cancel).props`, `ui.button('Связать как копию', on_click=self.submit).props`, `ui.column`, `ui.column().classes`, `ui.column().classes('copy-setup-panel').props`, `ui.icon`, `ui.icon('south', size='16px').classes`, `ui.label`, `ui.label('Из').classes`, `ui.label('Куда').classes`, `ui.label().classes`, `ui.select`, `ui.select(COPY_KINDS, value='copy', label='Тип копии').props`, `ui.select(COPY_KINDS, value='copy', label='Тип копии').props('dense outlined options-dense').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.cancel"></a>

## `CopySetupUI.cancel`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.cancel`

Отменяет выбор и возвращает прежний отчёт или связанную пару, если они были открыты. Независимая навигация по двум деревьям сохраняется.

```python
async def cancel(self)
```

Присваивания полям `self`: `opening`.

Прямые выражения вызова: [self.clear](copy_setup_ui.md#symbol-CopySetupUI.clear), `self.ws.notice`, `self.ws.restore_workspace`, `self.ws.update_scopes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.clear"></a>

## `CopySetupUI.clear`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.clear`

Убирает редактор и возвращает обычные команды панелей. Используется также при переходе к другой паре.

```python
def clear(self)
```

Присваивания полям `self`: `destination_key`, `draft`, `previous`.

Прямые выражения вызова: `pane.mode_switch.enable`, `self.panel.set_visibility`, `self.problem.set_visibility`, `self.ws.trees.classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.describe"></a>

## `CopySetupUI.describe`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.describe`

Подписывает полный маршрут от корня до выбранного источника. Для прямого источника показывает полный путь выбранной папки.

```python
def describe(self, source)
```

Прямые выражения вызова: [copy_origin_route](copy_setup_ui.md#symbol-copy_origin_route), `dict`, `library.get`, `next`, [scope_title](copy_setup_ui.md#symbol-scope_title), `self.ws.photo_libraries.cloud.get`, `self.ws.resolve_volume`, `source.get`.

Выражения возврата (ветви, без исполнения):

- `copy_origin_route(label, library.get('copies', []), link_id)`
- `copy_origin_route(label, self.ws.photo_libraries.cloud.get('copies', []), link_id)`
- `copy_origin_route(root, group['copies'], location, parent_key='source_location_id', root_id=main['id'])`
- `label`


<a id="symbol-CopySetupUI.open"></a>

## `CopySetupUI.open`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.open`

Переводит рабочее пространство в выбор назначения между двумя деревьями. Открытая правая папка подставляется сразу, а предыдущая связанная пара доступна после отмены.

```python
async def open(self, volume_id, path='', *, index=None, preferred_kind=None)
```

Присваивания полям `self`: `draft`, `opening`, `previous`.

Прямые выражения вызова: `any`, `bool`, `dict`, `next`, `pane.mode_switch.disable`, `pane.set_mode`, `panes[0].show_volume`, `panes[1 - index].save_browse_state`, `panes[1].focus_tree`, `panes[1].restore_browse_state`, `panes[1].show_volume`, [self.clear](copy_setup_ui.md#symbol-CopySetupUI.clear), [self.describe](copy_setup_ui.md#symbol-CopySetupUI.describe), `self.kind.set_value`, `self.kind.set_visibility`, `self.panel.set_visibility`, [self.source](copy_setup_ui.md#symbol-CopySetupUI.source), `source.get`, `ui.notify`, `ws.browse`, `ws.is_photos`, `ws.notice`, `ws.pair.unlink`, `ws.set_active`, `ws.trees.classes`, `ws.update_scopes`, `ws.workspace_snapshot`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.refresh"></a>

## `CopySetupUI.refresh`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.refresh`

Отображает выбранное назначение и доступность подтверждения без пересборки деревьев. Закрывает устаревший черновик при выборе другой области слева.

```python
def refresh(self)
```

Присваивания полям `self`: `destination_key`.

Прямые выражения вызова: [scope_title](copy_setup_ui.md#symbol-scope_title), [self.clear](copy_setup_ui.md#symbol-CopySetupUI.clear), `self.confirm.set_enabled`, `self.kind.set_value`, `self.problem.set_visibility`, [self.target](copy_setup_ui.md#symbol-CopySetupUI.target), `self.ws.panes[1].volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.save"></a>

## `CopySetupUI.save`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.save`

Сохраняет связь через API выбранного источника. Для цепочки передаёт постоянный ID предыдущего звена.

```python
async def save(self, source, target, kind)
```

Прямые выражения вызова: `dict`, `self.ws.request`, `source.get`.

Выражения возврата (ветви, без исполнения):

- `await self.ws.request('POST', '/api/storage/folder-copy-bindings', json=dict(source=origin, destination=dict(target, kind=kind), source_location_id=source.get('source_location_id')))`
- `await self.ws.request('POST', f"/api/photos/libraries/{source['library']['id']}/copies", json=dict(target, source_link_id=source.get('source_link_id')))`
- `await self.ws.request('POST', '/api/icloud/copies', json=dict(target, source_path=source['path'], source_link_id=source.get('source_link_id')))`


<a id="symbol-CopySetupUI.show_saved"></a>

## `CopySetupUI.show_saved`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.show_saved`

Обновляет боковую колонку и открывает именно сохранённое назначение. Нужная копия выбирается по адресу или ID из результата Core.

```python
async def show_saved(self, source, target, result)
```

Прямые выражения вызова: `all`, `copies.changed`, `copies.expanded.add`, `copies.open_copy`, `copies.section.open`, `libraries.expanded.add`, `libraries.open_copy`, `libraries.refresh`, `next`, `section.open`, `target.items`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-CopySetupUI.source"></a>

## `CopySetupUI.source`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.source`

Определяет выбранный источник и его роль в цепочке. Для физических копий проверяет точный корень привязки.

```python
def source(self, volume_id, path, entry_kind='directory')
```

Прямые выражения вызова: `copy.get`, [copy_volume](copy_setup_ui.md#symbol-copy_volume), `dict`, `getattr`, `libraries.cloud.get`, `library.get`, `self.ws.copies.membership`, `self.ws.resolve_volume`, `source.update`.

Выражения возврата (ветви, без исполнения):

- `None`
- `dict(kind='photos', volume_id=volume_id, path='', library=volume['library'])`
- `dict(kind='icloud', volume_id=volume_id, path=path)`
- `dict(kind='icloud', volume_id=ICLOUD_VOLUME_ID, path=copy['source_path'], source_link_id=copy['id'])`
- `dict(kind='photos', volume_id=f"photos-{library['id']}", path='', library=library, source_link_id=copy['id'])`
- `source`


<a id="symbol-CopySetupUI.submit"></a>

## `CopySetupUI.submit`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.submit`

Проверяет выбранную папку и сохраняет связь, затем показывает созданную пару. Файловая операция может быть запущена отдельно из открытой пары.

```python
async def submit(self)
```

Присваивания полям `self`: `saving`.

Прямые выражения вызова: `ValueError`, `listing.get`, `self.cancel_button.disable`, `self.cancel_button.enable`, [self.clear](copy_setup_ui.md#symbol-CopySetupUI.clear), `self.confirm.disable`, `self.kind.disable`, `self.kind.enable`, `self.problem.set_visibility`, [self.save](copy_setup_ui.md#symbol-CopySetupUI.save), [self.show_saved](copy_setup_ui.md#symbol-CopySetupUI.show_saved), [self.target](copy_setup_ui.md#symbol-CopySetupUI.target), `self.ws.error_text`, `self.ws.notice`, `self.ws.read_directory`, `self.ws.update_scopes`, `ui.notify`.

Явные `raise`:

- `ValueError(listing.get('error') or 'Папка назначения сейчас недоступна.')`

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-CopySetupUI.target"></a>

## `CopySetupUI.target`

[copy_setup_ui.py](../../copy_setup_ui.py) · `CopySetupUI.target`

Выбирает правую папку, если том доступен и пути не пересекаются. Путь хранится вместе с ID тома, а файл и корень тома непригодны как назначение.

```python
def target(self)
```

Прямые выражения вызова: `PurePosixPath`, [copy_volume](copy_setup_ui.md#symbol-copy_volume), `dict`, `left.is_relative_to`, `right.is_relative_to`.

Выражения возврата (ветви, без исполнения):

- `None`
- `dict(volume_id=pane.volume_id, path=pane.path)`


<a id="symbol-copy_origin_route"></a>

## `copy_origin_route`

[copy_setup_ui.py](../../copy_setup_ui.py) · `copy_origin_route`

Показывает адрес и предыдущие звенья выбранной копии. Использует фактические связи, включая отсутствующий источник.

```python
def copy_origin_route(label, copies, link_id, *, parent_key='source_link_id', root_id=None)
```

Прямые выражения вызова: `' → '.join`, `copy.get`, `copy_route`, `dict`, `next`.

Выражения возврата (ветви, без исполнения):

- `label`
- `'Недоступный источник'`
- `' → '.join((node['label'] for node in route))`


<a id="symbol-copy_volume"></a>

## `copy_volume`

[copy_setup_ui.py](../../copy_setup_ui.py) · `copy_volume`

Определяет подключённый том, пригодный для назначения копии. Проверяет доступность и сохранённую идентичность тома.

```python
def copy_volume(volume)
```

Прямые выражения вызова: `bool`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `bool(volume and volume['kind'] not in ('photos', 'icloud') and (volume['availability'] == 'online') and (volume.get('identity_status') not in ('unverified', 'legacy')))`


<a id="symbol-scope_title"></a>

## `scope_title`

[copy_setup_ui.py](../../copy_setup_ui.py) · `scope_title`

Формирует читаемый путь по короткому имени тома и пути внутри него. Для корневой папки возвращает имя тома.

```python
def scope_title(volume, path)
```

Прямые выражения вызова: `volume.get`.

Выражения возврата (ветви, без исполнения):

- `f'{name} /{path}' if path else name`
