# UI медиатек Photos: `photo_libraries_ui.py`

Список медиатек, состояние подключения и превью, привязанные копии, расписание и сохранение оригиналов. Создаёт виртуальные тома для общих панелей.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../photo_libraries_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_photo_copy_roles.py](tests.md#module-tests.test_photo_copy_roles), [tests/test_photo_libraries.py](tests.md#module-tests.test_photo_libraries), [tests/test_photos_schedule.py](tests.md#module-tests.test_photos_schedule).

## Оглавление определений

- [PhotoLibrariesUI](#symbol-PhotoLibrariesUI) — Показывает медиатеки, привязанные копии, расписание и команды оригиналов.
- [PhotoLibrariesUI.__init__](#symbol-PhotoLibrariesUI.__init__) — Инициализирует PhotoLibrariesUI и его рабочее состояние.
- [PhotoLibrariesUI.action](#symbol-PhotoLibrariesUI.action) — Исполняет запрос Photos с единым обновлением UI и обработкой ошибки.
- [PhotoLibrariesUI.add](#symbol-PhotoLibrariesUI.add) — Добавляет текущую системную медиатеку под выбранным названием.
- [PhotoLibrariesUI.authorize](#symbol-PhotoLibrariesUI.authorize) — Запрашивает разрешение на доступ к Photos через Core.
- [PhotoLibrariesUI.bind](#symbol-PhotoLibrariesUI.bind) — Привязывает выбранную файловую папку к медиатеке после проверки выбора.
- [PhotoLibrariesUI.build](#symbol-PhotoLibrariesUI.build) — Создаёт сворачиваемую секцию списка медиатек.
- [PhotoLibrariesUI.connect](#symbol-PhotoLibrariesUI.connect) — Повторяет сопоставление текущей системной медиатеки с сохранённым профилем.
- [PhotoLibrariesUI.copy_membership](#symbol-PhotoLibrariesUI.copy_membership) — Находит копию медиатеки, содержащую выбранный файловый путь.
- [PhotoLibrariesUI.copy_source_dialog](#symbol-PhotoLibrariesUI.copy_source_dialog) — Показывает выбор Photos или другой копии как источника оригиналов.
- [PhotoLibrariesUI.menu](#symbol-PhotoLibrariesUI.menu) — Создаёт общие команды доступа, подключения и добавления медиатеки.
- [PhotoLibrariesUI.name_dialog](#symbol-PhotoLibrariesUI.name_dialog) — Показывает ввод названия медиатеки и возвращает подтверждённое значение.
- [PhotoLibrariesUI.originals_action](#symbol-PhotoLibrariesUI.originals_action) — Запускает или приостанавливает сохранение оригиналов выбранной копии.
- [PhotoLibrariesUI.originals_journal](#symbol-PhotoLibrariesUI.originals_journal) — Показывает события сохранения и пути незавершённых оригиналов.
- [PhotoLibrariesUI.refresh](#symbol-PhotoLibrariesUI.refresh) — Обновляет данные медиатек и перерисовывает изменившиеся состояния.
- [PhotoLibrariesUI.refresh_copy_roles](#symbol-PhotoLibrariesUI.refresh_copy_roles) — Обновляет метки копий Photos в уже загруженных деревьях.
- [PhotoLibrariesUI.rename](#symbol-PhotoLibrariesUI.rename) — Меняет пользовательское название сохранённой медиатеки.
- [PhotoLibrariesUI.render](#symbol-PhotoLibrariesUI.render) — Перерисовывает записи медиатек, индикаторы и контекстные меню копий.
- [PhotoLibrariesUI.scan](#symbol-PhotoLibrariesUI.scan) — Запрашивает ручное обновление индекса выбранной медиатеки.
- [PhotoLibrariesUI.schedule_dialog](#symbol-PhotoLibrariesUI.schedule_dialog) — Показывает настройку часов разрешённого окна по Москве.
- [PhotoLibrariesUI.toggle](#symbol-PhotoLibrariesUI.toggle) — Переключает ручную паузу выбранной медиатеки.
- [PhotoLibrariesUI.toggle_schedule](#symbol-PhotoLibrariesUI.toggle_schedule) — Включает или выключает ограничение синхронизации ночным окном.
- [PhotoLibrariesUI.unbind](#symbol-PhotoLibrariesUI.unbind) — Отключает выбранную привязку копии медиатеки через Core.
- [PhotoLibrariesUI.volumes](#symbol-PhotoLibrariesUI.volumes) — Представляет сохранённые медиатеки как виртуальные тома рабочего пространства.
- [library_state](#symbol-library_state) — Определяет пользовательскую подпись доступности и паузы медиатеки.
- [originals_state](#symbol-originals_state) — Преобразует техническое состояние сохранения оригиналов в подпись UI.
- [originals_text](#symbol-originals_text) — Форматирует прогресс объектов и ресурсов привязанной копии Photos.
- [progress_text](#symbol-progress_text) — Формирует подпись прогресса превью одной медиатеки.
- [schedule_text](#symbol-schedule_text) — Формирует подпись настройки ночного окна медиатеки.

## Константы и значения по умолчанию

<a id="constant-LIBRARY_CSS"></a>

### `LIBRARY_CSS`

`Объёмное значение см. в исходном модуле`


<a id="symbol-PhotoLibrariesUI"></a>

## `PhotoLibrariesUI`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI`

Показывает медиатеки, привязанные копии, расписание и команды оригиналов. Зависимости конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `busy`, `copy_roles_signature`, `libraries`, `refreshing`, `rows`, `signature`, `ws`.

Именованные методы: `__init__`, `copy_membership`, `refresh_copy_roles`, `volumes`, `build`, `refresh`, `menu`, `render`, `action`, `authorize`, `connect`, `toggle`, `toggle_schedule`, `schedule_dialog`, `scan`, `name_dialog`, `add`, `rename`, `bind`, `unbind`, `originals_action`, `copy_source_dialog`, `originals_journal`.

<a id="symbol-PhotoLibrariesUI.__init__"></a>

## `PhotoLibrariesUI.__init__`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.__init__`

Инициализирует PhotoLibrariesUI и его рабочее состояние. Обновляет состояние объекта: busy, copy_roles_signature, libraries, refreshing, rows, signature, ws.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `busy`, `copy_roles_signature`, `libraries`, `refreshing`, `rows`, `signature`, `ws`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.action"></a>

## `PhotoLibrariesUI.action`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.action`

Исполняет запрос Photos с единым обновлением UI и обработкой ошибки. Обновляет состояние объекта: busy, signature.

```python
async def action(self, method, path, *, timeout=45, **kwargs)
```

Присваивания полям `self`: `busy`, `signature`.

Прямые выражения вызова: [self.refresh](photo_libraries_ui.md#symbol-PhotoLibrariesUI.refresh), `self.ws.notice`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.add"></a>

## `PhotoLibrariesUI.add`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.add`

Добавляет текущую системную медиатеку под выбранным названием. Асинхронно ожидает: self.action, self.name_dialog.

```python
async def add(self)
```

Прямые выражения вызова: `len`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), [self.name_dialog](photo_libraries_ui.md#symbol-PhotoLibrariesUI.name_dialog).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.authorize"></a>

## `PhotoLibrariesUI.authorize`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.authorize`

Запрашивает разрешение на доступ к Photos через Core. Асинхронно ожидает: self.action.

```python
async def authorize(self)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.bind"></a>

## `PhotoLibrariesUI.bind`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.bind`

Привязывает выбранную файловую папку к медиатеке после проверки выбора. Асинхронно ожидает: self.action.

```python
async def bind(self, library)
```

Прямые выражения вызова: `library.get`, `next`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), `self.ws.panes[1].scope`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Привязать', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Оригиналы будут сохраняться сразу в эту папку. Для запуска выбери «Сохранить оригиналы» в меню папки копии. Уже лежащие в ней файлы будут проверены по содержимому.').classes`, `ui.label('Привязать папку для копий оригиналов').classes`, `ui.label((volume.get('display_name') or volume['name']) + ' /' + scope['path']).classes`, `ui.label(library.get('label') or 'Photos').classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.build"></a>

## `PhotoLibrariesUI.build`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.build`

Создаёт сворачиваемую секцию списка медиатек. Обновляет состояние объекта: add_button, cards, connect_button, note, permission_button, section.

```python
def build(self)
```

Присваивания полям `self`: `add_button`, `cards`, `connect_button`, `note`, `permission_button`, `section`.

Прямые выражения вызова: `self.permission_button.set_visibility`, `self.ws.sidebar_expansion`, `self.ws.sidebar_expansion('libraries', 'Медиатеки', icon='photo_library').props`, `self.ws.sidebar_expansion('libraries', 'Медиатеки', icon='photo_library').props('dense').classes`, `ui.add_css`, `ui.button`, `ui.button('Добавить текущую медиатеку', icon='add', on_click=self.add).props`, `ui.button('Подключить текущую', icon='sync', on_click=self.connect).props`, `ui.button('Разрешить доступ Photos', icon='lock_open', on_click=self.authorize).props`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.connect"></a>

## `PhotoLibrariesUI.connect`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.connect`

Повторяет сопоставление текущей системной медиатеки с сохранённым профилем. Асинхронно ожидает: self.action.

```python
async def connect(self)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.copy_membership"></a>

## `PhotoLibrariesUI.copy_membership`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.copy_membership`

Находит копию медиатеки, содержащую выбранный файловый путь. Поля результата: label, is_root, inherited_from, media_library.

```python
def copy_membership(self, volume_id, path)
```

Прямые выражения вызова: `copy.get`, `dict`, `library.get`.

Выражения возврата (ветви, без исполнения):

- `dict(copy, label=f"{copy['number']:02d}-copy", is_root=True, inherited_from=None, media_library=library.get('label') or 'Photos')`
- `None`


<a id="symbol-PhotoLibrariesUI.copy_source_dialog"></a>

## `PhotoLibrariesUI.copy_source_dialog`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.copy_source_dialog`

Показывает выбор Photos или другой копии как источника оригиналов. Асинхронно ожидает: self.action.

```python
async def copy_source_dialog(self, library, copy)
```

Прямые выражения вызова: `choices.update`, `copy.get`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.button('Сохранить', on_click=lambda: dialog.submit(selected.value)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Готовые оригиналы передаются из выбранной копии. Пауза и продолжение управляют всей цепочкой.').classes`, `ui.label(f"Источник для {copy['number']:02d}-copy").classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(choices, value=current if current in choices else None, label='Копировать из').classes`, `ui.select(choices, value=current if current in choices else None, label='Копировать из').classes('w-full').props`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.menu"></a>

## `PhotoLibrariesUI.menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.menu`

Создаёт общие команды доступа, подключения и добавления медиатеки. Использует menu.on, ui.context_menu.

```python
def menu(self)
```

Прямые выражения вызова: `menu.on`, `ui.context_menu`.

Выражения возврата (ветви, без исполнения):

- `menu`


<a id="symbol-PhotoLibrariesUI.name_dialog"></a>

## `PhotoLibrariesUI.name_dialog`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.name_dialog`

Показывает ввод названия медиатеки и возвращает подтверждённое значение. Использует title.startswith, ui.button, ui.button('Отмена', on_click=lambda : dialog.submit(None)).props и ещё 2.

```python
async def name_dialog(self, title, value)
```

Прямые выражения вызова: `title.startswith`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.button('Сохранить', on_click=lambda: dialog.submit((name.value or '').strip())).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.input`, `ui.input('Название', value=value).props`, `ui.input('Название', value=value).props('outlined dense maxlength=120 autofocus').classes`, `ui.label`, `ui.label('Сначала открой отдельную системную медиатеку нужного Apple ID в Photos на M4.').classes`, `ui.label(title).classes`, `ui.row`, `ui.row().classes`.

Выражения возврата (ветви, без исполнения):

- `await dialog`


<a id="symbol-PhotoLibrariesUI.originals_action"></a>

## `PhotoLibrariesUI.originals_action`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.originals_action`

Запускает или приостанавливает сохранение оригиналов выбранной копии. Асинхронно ожидает: self.action.

```python
async def originals_action(self, source_id, copy, running)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.originals_journal"></a>

## `PhotoLibrariesUI.originals_journal`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.originals_journal`

Показывает события сохранения и пути незавершённых оригиналов. Обрабатывает ошибки: Exception.

```python
async def originals_journal(self, source_id, copy)
```

Прямые выражения вызова: `data.get`, `data['job'].get`, `dialog.open`, `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Записей пока нет').classes`, `ui.label('Незавершённый файл оставлен в копии: ' + path).classes`, `ui.label('Сохранение оригиналов · журнал').classes`, `ui.label(data['job'].get('message', '')).classes`, `ui.label(f"{item['created_at'][:19]} · {item['path']} · {item['message']}").classes`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.refresh"></a>

## `PhotoLibrariesUI.refresh`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.refresh`

Обновляет данные медиатек и перерисовывает изменившиеся состояния. Обновляет состояние объекта: libraries, refreshing, signature.

```python
async def refresh(self)
```

Присваивания полям `self`: `libraries`, `refreshing`, `signature`.

Прямые выражения вызова: `(c.get('originals') or {}).get`, `(s.get('sync_schedule') or {}).get`, `bool`, `c.get`, `connection.get`, `copy.get`, `data.get`, `job.get`, `len`, `library.get`, [library_state](photo_libraries_ui.md#symbol-library_state), `min`, [originals_state](photo_libraries_ui.md#symbol-originals_state), [originals_text](photo_libraries_ui.md#symbol-originals_text), `pane.preview.refresh_pending`, `pane.update_header`, [progress_text](photo_libraries_ui.md#symbol-progress_text), `row.get`, `row.get('copies', {}).get`, `row['schedule'].set_visibility`, `s.get`, [schedule_text](photo_libraries_ui.md#symbol-schedule_text), `self.add_button.set_enabled`, `self.connect_button.set_enabled`, `self.permission_button.set_enabled`, `self.permission_button.set_visibility`, [self.refresh_copy_roles](photo_libraries_ui.md#symbol-PhotoLibrariesUI.refresh_copy_roles), [self.render](photo_libraries_ui.md#symbol-PhotoLibrariesUI.render), `self.rows.get`, `self.ws.error_text`, `self.ws.is_photos`, `self.ws.request`, `tuple`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.refresh_copy_roles"></a>

## `PhotoLibrariesUI.refresh_copy_roles`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.refresh_copy_roles`

Обновляет метки копий Photos в уже загруженных деревьях. Обновляет состояние объекта: copy_roles_signature.

```python
def refresh_copy_roles(self)
```

Присваивания полям `self`: `copy_roles_signature`.

Прямые выражения вызова: `c.get`, `getattr`, `library.get`, `pane.render`, `self.ws.is_photos`, `tuple`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.rename"></a>

## `PhotoLibrariesUI.rename`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.rename`

Меняет пользовательское название сохранённой медиатеки. Асинхронно ожидает: self.action, self.name_dialog.

```python
async def rename(self, library)
```

Прямые выражения вызова: `library.get`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), [self.name_dialog](photo_libraries_ui.md#symbol-PhotoLibrariesUI.name_dialog).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.render"></a>

## `PhotoLibrariesUI.render`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.render`

Перерисовывает записи медиатек, индикаторы и контекстные меню копий. Использует (copy.get('originals') or {}).get, (library.get('sync_schedule') or {}).get, copy.get, job.get, library.get.

```python
def render(self)
```

Прямые выражения вызова: `(copy.get('originals') or {}).get`, `(library.get('sync_schedule') or {}).get`, `bool`, `copy.get`, `dict`, `job.get`, `library.get`, [library_state](photo_libraries_ui.md#symbol-library_state), [originals_state](photo_libraries_ui.md#symbol-originals_state), [originals_text](photo_libraries_ui.md#symbol-originals_text), [progress_text](photo_libraries_ui.md#symbol-progress_text), `scan.set_enabled`, `schedule.set_visibility`, [schedule_text](photo_libraries_ui.md#symbol-schedule_text), `self.cards.clear`, [self.menu](photo_libraries_ui.md#symbol-PhotoLibrariesUI.menu), `self.rows.clear`, `str`, `str(night_only).lower`, `ui.button`, `ui.button(on_click=lambda sid=source_id: self.ws.open_library(sid)).props`, `ui.button(on_click=lambda sid=source_id: self.ws.open_library(sid)).props('flat no-caps').classes`, `ui.column`, `ui.column().classes`, `ui.icon`, `ui.item_section`, `ui.item_section().props`, `ui.label`, `ui.label('Управление: правой кнопкой по папке копии').classes`, `ui.label(library.get('label') or 'Photos').classes`, `ui.label(library_state(library)).classes`, `ui.label(originals_state(copy)).classes`, `ui.label(originals_text(copy)).classes`, `ui.label(progress_text(library)).classes`, `ui.label(schedule_text(library)).classes`, `ui.linear_progress`, `ui.linear_progress(value=0, show_value=False).props`, `ui.linear_progress(value=0, show_value=False).props('color=blue-7').classes`, `ui.linear_progress(value=0, show_value=False).props('color=green-7').classes`, `ui.link`, `ui.link(title, '#').classes`, `ui.link(title, '#').classes('library-copy').on`, `ui.menu_item`, `ui.menu_item(on_click=lambda s=library: self.toggle_schedule(s)).props`, `ui.separator`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.scan"></a>

## `PhotoLibrariesUI.scan`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.scan`

Запрашивает ручное обновление индекса выбранной медиатеки. Асинхронно ожидает: self.action.

```python
async def scan(self, source_id)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.schedule_dialog"></a>

## `PhotoLibrariesUI.schedule_dialog`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.schedule_dialog`

Показывает настройку часов разрешённого окна по Москве. Асинхронно ожидает: self.action.

```python
async def schedule_dialog(self, library)
```

Прямые выражения вызова: `bool`, `library.get`, `range`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), `settings.get`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Сохранить', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.checkbox`, `ui.dialog`, `ui.label`, `ui.label('Время московское. Вне окна оригиналы и фоновые превью ждут. Ручная пауза сохраняется. M4 должен работать.').classes`, `ui.label('Ночная синхронизация').classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(hours, value=settings.get('end_hour', 7), label='Окончание').props`, `ui.select(hours, value=settings.get('end_hour', 7), label='Окончание').props('outlined dense').classes`, `ui.select(hours, value=settings.get('start_hour', 0), label='Начало').props`, `ui.select(hours, value=settings.get('start_hour', 0), label='Начало').props('outlined dense').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.toggle"></a>

## `PhotoLibrariesUI.toggle`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.toggle`

Переключает ручную паузу выбранной медиатеки. Асинхронно ожидает: self.action.

```python
async def toggle(self, library)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.toggle_schedule"></a>

## `PhotoLibrariesUI.toggle_schedule`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.toggle_schedule`

Включает или выключает ограничение синхронизации ночным окном. Асинхронно ожидает: self.action.

```python
async def toggle_schedule(self, library)
```

Прямые выражения вызова: `library.get`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), `settings.get`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.unbind"></a>

## `PhotoLibrariesUI.unbind`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.unbind`

Отключает выбранную привязку копии медиатеки через Core. Асинхронно ожидает: self.action.

```python
async def unbind(self, source_id, copy)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.volumes"></a>

## `PhotoLibrariesUI.volumes`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.volumes`

Представляет сохранённые медиатеки как виртуальные тома рабочего пространства. Использует s.get.

```python
def volumes(self)
```

Прямые выражения вызова: `dict`, `s.get`.

Выражения возврата (ветви, без исполнения):

- `[dict(id=f"photos-{s['id']}", source_id=s['id'], kind='photos', name=s.get('label') or 'Photos', display_name=s.get('label') or 'Photos', mount_path=None, availability='online' if s['active'] else 'offline', mounted=False, identity_status='virtual', library=s) for s in self.libraries]`


<a id="symbol-library_state"></a>

## `library_state`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `library_state`

Определяет пользовательскую подпись доступности и паузы медиатеки. Использует (library.get('sync_schedule') or {}).get, library.get.

```python
def library_state(library)
```

Прямые выражения вызова: `(library.get('sync_schedule') or {}).get`, `int`, `library.get`.

Выражения возврата (ветви, без исполнения):

- `'Нужно разрешение Фото'`
- `'Не подключена · сохранённый каталог'`
- `'Пауза'`
- `'Синхронизация ожидает ночного окна'`
- `'Обновляю каталог…'`
- `f'Ожидают миниатюру Photos: {waiting}'`
- `'Загружаю превью'`
- `'Есть ошибки превью' if library.get('thumbnail_error') else 'Превью готовы'`


<a id="symbol-originals_state"></a>

## `originals_state`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `originals_state`

Преобразует техническое состояние сохранения оригиналов в подпись UI. Использует copy.get, f"Проверка файлов: {job.get('checked_files', 0):,}".replace, job.get.

```python
def originals_state(copy)
```

Прямые выражения вызова: `copy.get`, `f"Проверка файлов: {job.get('checked_files', 0):,}".replace`, `job.get`.

Выражения возврата (ветви, без исполнения):

- `f"Проверка файлов: {job.get('checked_files', 0):,}".replace(',', ' ')`
- `origin + f"{job.get('current_path', '')} · {size:.1f} МБ" + (f" · iCloud {job['fraction']:.0%}" if 0 < job.get('fraction', 0) < 1 else '')`
- `job.get('message', 'Сохранение ещё не запускалось')`


<a id="symbol-originals_text"></a>

## `originals_text`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `originals_text`

Форматирует прогресс объектов и ресурсов привязанной копии Photos. Использует copy.get, f' · {done:,} / {total:,}'.replace, job.get.

```python
def originals_text(copy)
```

Прямые выражения вызова: `copy.get`, `f' · {done:,} / {total:,}'.replace`, `job.get`.

Выражения возврата (ветви, без исполнения):

- `title + ' · не запускалось'`
- `title + f' · {done:,} / {total:,}'.replace(',', ' ')`


<a id="symbol-progress_text"></a>

## `progress_text`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `progress_text`

Формирует подпись прогресса превью одной медиатеки. Использует f'Превью {done:,} / {total:,} · {percent}'.replace, library.get.

```python
def progress_text(library)
```

Прямые выражения вызова: `f'Превью {done:,} / {total:,} · {percent}'.replace`, `int`, `library.get`.

Выражения возврата (ветви, без исполнения):

- `f'Превью {done:,} / {total:,} · {percent}'.replace(',', ' ')`


<a id="symbol-schedule_text"></a>

## `schedule_text`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `schedule_text`

Формирует подпись настройки ночного окна медиатеки. Использует library.get, schedule.get.

```python
def schedule_text(library)
```

Прямые выражения вызова: `library.get`, `schedule.get`.

Выражения возврата (ветви, без исполнения):

- `'Только ночью · ' + schedule.get('window', '00:00–07:00 МСК') if schedule.get('night_only') else ''`
