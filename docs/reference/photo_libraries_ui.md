# UI медиатек Photos: `photo_libraries_ui.py`

Список медиатек, состояние подключения и превью, привязанные копии, расписание и сохранение оригиналов. Создаёт виртуальные тома для общих панелей.

[Исходный модуль](../../photo_libraries_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_photo_copy_roles.py](../../tests/test_photo_copy_roles.py#L5), [tests/test_photo_libraries.py](../../tests/test_photo_libraries.py#L13), [tests/test_photos_schedule.py](../../tests/test_photos_schedule.py#L11).

## Оглавление определений

- [progress_text](#symbol-progress-text) — Формирует подпись прогресса превью одной медиатеки.
- [originals_text](#symbol-originals-text) — Форматирует прогресс объектов и ресурсов привязанной копии Photos.
- [originals_state](#symbol-originals-state) — Преобразует техническое состояние сохранения оригиналов в подпись UI.
- [schedule_text](#symbol-schedule-text) — Формирует подпись настройки ночного окна медиатеки.
- [library_state](#symbol-library-state) — Определяет пользовательскую подпись доступности и паузы медиатеки.
- [PhotoLibrariesUI](#symbol-photolibrariesui) — Показывает медиатеки, привязанные копии, расписание и команды оригиналов.
- [PhotoLibrariesUI.__init__](#symbol-photolibrariesui---init--) — Инициализирует PhotoLibrariesUI и его рабочее состояние.
- [PhotoLibrariesUI.copy_membership](#symbol-photolibrariesui-copy-membership) — Находит копию медиатеки, содержащую выбранный файловый путь.
- [PhotoLibrariesUI.refresh_copy_roles](#symbol-photolibrariesui-refresh-copy-roles) — Обновляет метки копий Photos в уже загруженных деревьях.
- [PhotoLibrariesUI.volumes](#symbol-photolibrariesui-volumes) — Представляет сохранённые медиатеки как виртуальные тома рабочего пространства.
- [PhotoLibrariesUI.build](#symbol-photolibrariesui-build) — Создаёт сворачиваемую секцию списка медиатек.
- [PhotoLibrariesUI.refresh](#symbol-photolibrariesui-refresh) — Обновляет данные медиатек и перерисовывает изменившиеся состояния.
- [PhotoLibrariesUI.menu](#symbol-photolibrariesui-menu) — Создаёт общие команды доступа, подключения и добавления медиатеки.
- [PhotoLibrariesUI.render](#symbol-photolibrariesui-render) — Перерисовывает записи медиатек, индикаторы и контекстные меню копий.
- [PhotoLibrariesUI.action](#symbol-photolibrariesui-action) — Исполняет запрос Photos с единым обновлением UI и обработкой ошибки.
- [PhotoLibrariesUI.authorize](#symbol-photolibrariesui-authorize) — Запрашивает разрешение на доступ к Photos через Core.
- [PhotoLibrariesUI.connect](#symbol-photolibrariesui-connect) — Повторяет сопоставление текущей системной медиатеки с сохранённым профилем.
- [PhotoLibrariesUI.toggle](#symbol-photolibrariesui-toggle) — Переключает ручную паузу выбранной медиатеки.
- [PhotoLibrariesUI.toggle_schedule](#symbol-photolibrariesui-toggle-schedule) — Включает или выключает ограничение синхронизации ночным окном.
- [PhotoLibrariesUI.schedule_dialog](#symbol-photolibrariesui-schedule-dialog) — Показывает настройку часов разрешённого окна по Москве.
- [PhotoLibrariesUI.scan](#symbol-photolibrariesui-scan) — Запрашивает ручное обновление индекса выбранной медиатеки.
- [PhotoLibrariesUI.name_dialog](#symbol-photolibrariesui-name-dialog) — Показывает ввод названия медиатеки и возвращает подтверждённое значение.
- [PhotoLibrariesUI.add](#symbol-photolibrariesui-add) — Добавляет текущую системную медиатеку под выбранным названием.
- [PhotoLibrariesUI.rename](#symbol-photolibrariesui-rename) — Меняет пользовательское название сохранённой медиатеки.
- [PhotoLibrariesUI.bind](#symbol-photolibrariesui-bind) — Привязывает выбранную файловую папку к медиатеке после проверки выбора.
- [PhotoLibrariesUI.unbind](#symbol-photolibrariesui-unbind) — Отключает выбранную привязку копии медиатеки через Core.
- [PhotoLibrariesUI.originals_action](#symbol-photolibrariesui-originals-action) — Запускает или приостанавливает сохранение оригиналов выбранной копии.
- [PhotoLibrariesUI.copy_source_dialog](#symbol-photolibrariesui-copy-source-dialog) — Показывает выбор Photos или другой копии как источника оригиналов.
- [PhotoLibrariesUI.originals_journal](#symbol-photolibrariesui-originals-journal) — Показывает события сохранения и пути незавершённых оригиналов.

<a id="symbol-progress-text"></a>

## `progress_text`

[photo_libraries_ui.py:23](../../photo_libraries_ui.py#L23)

Формирует подпись прогресса превью одной медиатеки. Использует f'Превью {done:,} / {total:,} · {percent}'.replace, library.get.

```python
def progress_text(library)
```

Прямые выражения вызова: `f'Превью {done:,} / {total:,} · {percent}'.replace`, `int`, `library.get`.

Выражения возврата (ветви, без исполнения):

- `f'Превью {done:,} / {total:,} · {percent}'.replace(',', ' ')`


<a id="symbol-originals-text"></a>

## `originals_text`

[photo_libraries_ui.py:32](../../photo_libraries_ui.py#L32)

Форматирует прогресс объектов и ресурсов привязанной копии Photos. Использует copy.get, f' · {done:,} / {total:,}'.replace, job.get.

```python
def originals_text(copy)
```

Прямые выражения вызова: `copy.get`, `f' · {done:,} / {total:,}'.replace`, `job.get`.

Выражения возврата (ветви, без исполнения):

- `title + ' · не запускалось'`
- `title + f' · {done:,} / {total:,}'.replace(',', ' ')`


<a id="symbol-originals-state"></a>

## `originals_state`

[photo_libraries_ui.py:43](../../photo_libraries_ui.py#L43)

Преобразует техническое состояние сохранения оригиналов в подпись UI. Использует copy.get, f"Проверка файлов: {job.get('checked_files', 0):,}".replace, job.get.

```python
def originals_state(copy)
```

Прямые выражения вызова: `copy.get`, `f"Проверка файлов: {job.get('checked_files', 0):,}".replace`, `job.get`.

Выражения возврата (ветви, без исполнения):

- `f"Проверка файлов: {job.get('checked_files', 0):,}".replace(',', ' ')`
- `origin + f"{job.get('current_path', '')} · {size:.1f} МБ" + (f" · iCloud {job['fraction']:.0%}" if 0 < job.get('fraction', 0) < 1 else '')`
- `job.get('message', 'Сохранение ещё не запускалось')`


<a id="symbol-schedule-text"></a>

## `schedule_text`

[photo_libraries_ui.py:57](../../photo_libraries_ui.py#L57)

Формирует подпись настройки ночного окна медиатеки. Использует library.get, schedule.get.

```python
def schedule_text(library)
```

Прямые выражения вызова: `library.get`, `schedule.get`.

Выражения возврата (ветви, без исполнения):

- `'Только ночью · ' + schedule.get('window', '00:00–07:00 МСК') if schedule.get('night_only') else ''`


<a id="symbol-library-state"></a>

## `library_state`

[photo_libraries_ui.py:64](../../photo_libraries_ui.py#L64)

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


<a id="symbol-photolibrariesui"></a>

## `PhotoLibrariesUI`

[photo_libraries_ui.py:87](../../photo_libraries_ui.py#L87)

Показывает медиатеки, привязанные копии, расписание и команды оригиналов. Зависимости конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `busy`, `copy_roles_signature`, `libraries`, `refreshing`, `rows`, `signature`, `ws`.

Именованные методы: `__init__`, `copy_membership`, `refresh_copy_roles`, `volumes`, `build`, `refresh`, `menu`, `render`, `action`, `authorize`, `connect`, `toggle`, `toggle_schedule`, `schedule_dialog`, `scan`, `name_dialog`, `add`, `rename`, `bind`, `unbind`, `originals_action`, `copy_source_dialog`, `originals_journal`.

<a id="symbol-photolibrariesui---init--"></a>

## `PhotoLibrariesUI.__init__`

[photo_libraries_ui.py:90](../../photo_libraries_ui.py#L90)

Инициализирует PhotoLibrariesUI и его рабочее состояние. Обновляет состояние объекта: busy, copy_roles_signature, libraries, refreshing, rows, signature, ws.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `busy`, `copy_roles_signature`, `libraries`, `refreshing`, `rows`, `signature`, `ws`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-copy-membership"></a>

## `PhotoLibrariesUI.copy_membership`

[photo_libraries_ui.py:100](../../photo_libraries_ui.py#L100)

Находит копию медиатеки, содержащую выбранный файловый путь. Поля результата: label, is_root, inherited_from, media_library.

```python
def copy_membership(self, volume_id, path)
```

Прямые выражения вызова: `copy.get`, `dict`, `library.get`.

Выражения возврата (ветви, без исполнения):

- `dict(copy, label=f"{copy['number']:02d}-copy", is_root=True, inherited_from=None, media_library=library.get('label') or 'Photos')`
- `None`


<a id="symbol-photolibrariesui-refresh-copy-roles"></a>

## `PhotoLibrariesUI.refresh_copy_roles`

[photo_libraries_ui.py:110](../../photo_libraries_ui.py#L110)

Обновляет метки копий Photos в уже загруженных деревьях. Обновляет состояние объекта: copy_roles_signature.

```python
def refresh_copy_roles(self)
```

Присваивания полям `self`: `copy_roles_signature`.

Прямые выражения вызова: `c.get`, `getattr`, `library.get`, `pane.render`, `self.ws.is_photos`, `tuple`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photolibrariesui-volumes"></a>

## `PhotoLibrariesUI.volumes`

[photo_libraries_ui.py:124](../../photo_libraries_ui.py#L124)

Представляет сохранённые медиатеки как виртуальные тома рабочего пространства. Использует s.get.

```python
def volumes(self)
```

Прямые выражения вызова: `dict`, `s.get`.

Выражения возврата (ветви, без исполнения):

- `[dict(id=f"photos-{s['id']}", source_id=s['id'], kind='photos', name=s.get('label') or 'Photos', display_name=s.get('label') or 'Photos', mount_path=None, availability='online' if s['active'] else 'offline', mounted=False, identity_status='virtual', library=s) for s in self.libraries]`


<a id="symbol-photolibrariesui-build"></a>

## `PhotoLibrariesUI.build`

[photo_libraries_ui.py:132](../../photo_libraries_ui.py#L132)

Создаёт сворачиваемую секцию списка медиатек. Обновляет состояние объекта: add_button, cards, connect_button, note, permission_button, section.

```python
def build(self)
```

Присваивания полям `self`: `add_button`, `cards`, `connect_button`, `note`, `permission_button`, `section`.

Прямые выражения вызова: `self.permission_button.set_visibility`, `self.ws.sidebar_expansion`, `self.ws.sidebar_expansion('libraries', 'Медиатеки', icon='photo_library').props`, `self.ws.sidebar_expansion('libraries', 'Медиатеки', icon='photo_library').props('dense').classes`, `ui.add_css`, `ui.button`, `ui.button('Добавить текущую медиатеку', icon='add', on_click=self.add).props`, `ui.button('Подключить текущую', icon='sync', on_click=self.connect).props`, `ui.button('Разрешить доступ Photos', icon='lock_open', on_click=self.authorize).props`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-refresh"></a>

## `PhotoLibrariesUI.refresh`

[photo_libraries_ui.py:145](../../photo_libraries_ui.py#L145)

Обновляет данные медиатек и перерисовывает изменившиеся состояния. Обновляет состояние объекта: libraries, refreshing, signature.

```python
async def refresh(self)
```

Присваивания полям `self`: `libraries`, `refreshing`, `signature`.

Прямые выражения вызова: `(c.get('originals') or {}).get`, `(s.get('sync_schedule') or {}).get`, `bool`, `c.get`, `connection.get`, `copy.get`, `data.get`, `job.get`, `len`, `library.get`, [library_state](../../photo_libraries_ui.py#L64), `min`, [originals_state](../../photo_libraries_ui.py#L43), [originals_text](../../photo_libraries_ui.py#L32), `pane.preview.refresh_pending`, `pane.update_header`, [progress_text](../../photo_libraries_ui.py#L23), `row.get`, `row.get('copies', {}).get`, `row['schedule'].set_visibility`, `s.get`, [schedule_text](../../photo_libraries_ui.py#L57), `self.add_button.set_enabled`, `self.connect_button.set_enabled`, `self.permission_button.set_enabled`, `self.permission_button.set_visibility`, [self.refresh_copy_roles](../../photo_libraries_ui.py#L110), [self.render](../../photo_libraries_ui.py#L209), `self.rows.get`, `self.ws.error_text`, `self.ws.is_photos`, `self.ws.request`, `tuple`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photolibrariesui-menu"></a>

## `PhotoLibrariesUI.menu`

[photo_libraries_ui.py:201](../../photo_libraries_ui.py#L201)

Создаёт общие команды доступа, подключения и добавления медиатеки. Использует menu.on, ui.context_menu.

```python
def menu(self)
```

Прямые выражения вызова: `menu.on`, `ui.context_menu`.

Выражения возврата (ветви, без исполнения):

- `menu`


<a id="symbol-photolibrariesui-render"></a>

## `PhotoLibrariesUI.render`

[photo_libraries_ui.py:209](../../photo_libraries_ui.py#L209)

Перерисовывает записи медиатек, индикаторы и контекстные меню копий. Использует (copy.get('originals') or {}).get, (library.get('sync_schedule') or {}).get, copy.get, job.get, library.get.

```python
def render(self)
```

Прямые выражения вызова: `(copy.get('originals') or {}).get`, `(library.get('sync_schedule') or {}).get`, `bool`, `copy.get`, `dict`, `job.get`, `library.get`, [library_state](../../photo_libraries_ui.py#L64), [originals_state](../../photo_libraries_ui.py#L43), [originals_text](../../photo_libraries_ui.py#L32), [progress_text](../../photo_libraries_ui.py#L23), `scan.set_enabled`, `schedule.set_visibility`, [schedule_text](../../photo_libraries_ui.py#L57), `self.cards.clear`, [self.menu](../../photo_libraries_ui.py#L201), `self.rows.clear`, `str`, `str(night_only).lower`, `ui.button`, `ui.button(on_click=lambda sid=source_id: self.ws.open_library(sid)).props`, `ui.button(on_click=lambda sid=source_id: self.ws.open_library(sid)).props('flat no-caps').classes`, `ui.column`, `ui.column().classes`, `ui.icon`, `ui.item_section`, `ui.item_section().props`, `ui.label`, `ui.label('Управление: правой кнопкой по папке копии').classes`, `ui.label(library.get('label') or 'Photos').classes`, `ui.label(library_state(library)).classes`, `ui.label(originals_state(copy)).classes`, `ui.label(originals_text(copy)).classes`, `ui.label(progress_text(library)).classes`, `ui.label(schedule_text(library)).classes`, `ui.linear_progress`, `ui.linear_progress(value=0, show_value=False).props`, `ui.linear_progress(value=0, show_value=False).props('color=blue-7').classes`, `ui.linear_progress(value=0, show_value=False).props('color=green-7').classes`, `ui.link`, `ui.link(title, '#').classes`, `ui.link(title, '#').classes('library-copy').on`, `ui.menu_item`, `ui.menu_item(on_click=lambda s=library: self.toggle_schedule(s)).props`, `ui.separator`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-action"></a>

## `PhotoLibrariesUI.action`

[photo_libraries_ui.py:271](../../photo_libraries_ui.py#L271)

Исполняет запрос Photos с единым обновлением UI и обработкой ошибки. Обновляет состояние объекта: busy, signature.

```python
async def action(self, method, path, *, timeout=45, **kwargs)
```

Присваивания полям `self`: `busy`, `signature`.

Прямые выражения вызова: [self.refresh](../../photo_libraries_ui.py#L145), `self.ws.notice`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photolibrariesui-authorize"></a>

## `PhotoLibrariesUI.authorize`

[photo_libraries_ui.py:286](../../photo_libraries_ui.py#L286)

Запрашивает разрешение на доступ к Photos через Core. Асинхронно ожидает: self.action.

```python
async def authorize(self)
```

Прямые выражения вызова: [self.action](../../photo_libraries_ui.py#L271).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-connect"></a>

## `PhotoLibrariesUI.connect`

[photo_libraries_ui.py:291](../../photo_libraries_ui.py#L291)

Повторяет сопоставление текущей системной медиатеки с сохранённым профилем. Асинхронно ожидает: self.action.

```python
async def connect(self)
```

Прямые выражения вызова: [self.action](../../photo_libraries_ui.py#L271).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-toggle"></a>

## `PhotoLibrariesUI.toggle`

[photo_libraries_ui.py:296](../../photo_libraries_ui.py#L296)

Переключает ручную паузу выбранной медиатеки. Асинхронно ожидает: self.action.

```python
async def toggle(self, library)
```

Прямые выражения вызова: [self.action](../../photo_libraries_ui.py#L271).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-toggle-schedule"></a>

## `PhotoLibrariesUI.toggle_schedule`

[photo_libraries_ui.py:302](../../photo_libraries_ui.py#L302)

Включает или выключает ограничение синхронизации ночным окном. Асинхронно ожидает: self.action.

```python
async def toggle_schedule(self, library)
```

Прямые выражения вызова: `library.get`, [self.action](../../photo_libraries_ui.py#L271), `settings.get`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-schedule-dialog"></a>

## `PhotoLibrariesUI.schedule_dialog`

[photo_libraries_ui.py:310](../../photo_libraries_ui.py#L310)

Показывает настройку часов разрешённого окна по Москве. Асинхронно ожидает: self.action.

```python
async def schedule_dialog(self, library)
```

Прямые выражения вызова: `bool`, `library.get`, `range`, [self.action](../../photo_libraries_ui.py#L271), `settings.get`, `ui.button`, `ui.button('Отмена', on_click=lambda : dialog.submit(False)).props`, `ui.button('Сохранить', on_click=lambda : dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.checkbox`, `ui.dialog`, `ui.label`, `ui.label('Время московское. Вне окна оригиналы и фоновые превью ждут. Ручная пауза сохраняется. M4 должен работать.').classes`, `ui.label('Ночная синхронизация').classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(hours, value=settings.get('end_hour', 7), label='Окончание').props`, `ui.select(hours, value=settings.get('end_hour', 7), label='Окончание').props('outlined dense').classes`, `ui.select(hours, value=settings.get('start_hour', 0), label='Начало').props`, `ui.select(hours, value=settings.get('start_hour', 0), label='Начало').props('outlined dense').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-scan"></a>

## `PhotoLibrariesUI.scan`

[photo_libraries_ui.py:328](../../photo_libraries_ui.py#L328)

Запрашивает ручное обновление индекса выбранной медиатеки. Асинхронно ожидает: self.action.

```python
async def scan(self, source_id)
```

Прямые выражения вызова: [self.action](../../photo_libraries_ui.py#L271).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-name-dialog"></a>

## `PhotoLibrariesUI.name_dialog`

[photo_libraries_ui.py:333](../../photo_libraries_ui.py#L333)

Показывает ввод названия медиатеки и возвращает подтверждённое значение. Использует title.startswith, ui.button, ui.button('Отмена', on_click=lambda : dialog.submit(None)).props и ещё 2.

```python
async def name_dialog(self, title, value)
```

Прямые выражения вызова: `title.startswith`, `ui.button`, `ui.button('Отмена', on_click=lambda : dialog.submit(None)).props`, `ui.button('Сохранить', on_click=lambda : dialog.submit((name.value or '').strip())).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.input`, `ui.input('Название', value=value).props`, `ui.input('Название', value=value).props('outlined dense maxlength=120 autofocus').classes`, `ui.label`, `ui.label('Сначала открой отдельную системную медиатеку нужного Apple ID в Photos на M4.').classes`, `ui.label(title).classes`, `ui.row`, `ui.row().classes`.

Выражения возврата (ветви, без исполнения):

- `await dialog`


<a id="symbol-photolibrariesui-add"></a>

## `PhotoLibrariesUI.add`

[photo_libraries_ui.py:346](../../photo_libraries_ui.py#L346)

Добавляет текущую системную медиатеку под выбранным названием. Асинхронно ожидает: self.action, self.name_dialog.

```python
async def add(self)
```

Прямые выражения вызова: `len`, [self.action](../../photo_libraries_ui.py#L271), [self.name_dialog](../../photo_libraries_ui.py#L333).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-rename"></a>

## `PhotoLibrariesUI.rename`

[photo_libraries_ui.py:353](../../photo_libraries_ui.py#L353)

Меняет пользовательское название сохранённой медиатеки. Асинхронно ожидает: self.action, self.name_dialog.

```python
async def rename(self, library)
```

Прямые выражения вызова: `library.get`, [self.action](../../photo_libraries_ui.py#L271), [self.name_dialog](../../photo_libraries_ui.py#L333).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-bind"></a>

## `PhotoLibrariesUI.bind`

[photo_libraries_ui.py:360](../../photo_libraries_ui.py#L360)

Привязывает выбранную файловую папку к медиатеке после проверки выбора. Асинхронно ожидает: self.action.

```python
async def bind(self, library)
```

Прямые выражения вызова: `library.get`, `next`, [self.action](../../photo_libraries_ui.py#L271), `self.ws.panes[1].scope`, `ui.button`, `ui.button('Отмена', on_click=lambda : dialog.submit(False)).props`, `ui.button('Привязать', on_click=lambda : dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Оригиналы будут сохраняться сразу в эту папку. Для запуска выбери «Сохранить оригиналы» в меню папки копии. Уже лежащие в ней файлы будут проверены по содержимому.').classes`, `ui.label('Привязать папку для копий оригиналов').classes`, `ui.label((volume.get('display_name') or volume['name']) + ' /' + scope['path']).classes`, `ui.label(library.get('label') or 'Photos').classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photolibrariesui-unbind"></a>

## `PhotoLibrariesUI.unbind`

[photo_libraries_ui.py:379](../../photo_libraries_ui.py#L379)

Отключает выбранную привязку копии медиатеки через Core. Асинхронно ожидает: self.action.

```python
async def unbind(self, source_id, copy)
```

Прямые выражения вызова: [self.action](../../photo_libraries_ui.py#L271).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-originals-action"></a>

## `PhotoLibrariesUI.originals_action`

[photo_libraries_ui.py:385](../../photo_libraries_ui.py#L385)

Запускает или приостанавливает сохранение оригиналов выбранной копии. Асинхронно ожидает: self.action.

```python
async def originals_action(self, source_id, copy, running)
```

Прямые выражения вызова: [self.action](../../photo_libraries_ui.py#L271).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-copy-source-dialog"></a>

## `PhotoLibrariesUI.copy_source_dialog`

[photo_libraries_ui.py:391](../../photo_libraries_ui.py#L391)

Показывает выбор Photos или другой копии как источника оригиналов. Асинхронно ожидает: self.action.

```python
async def copy_source_dialog(self, library, copy)
```

Прямые выражения вызова: `choices.update`, `copy.get`, [self.action](../../photo_libraries_ui.py#L271), `ui.button`, `ui.button('Отмена', on_click=lambda : dialog.submit(None)).props`, `ui.button('Сохранить', on_click=lambda : dialog.submit(selected.value)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Готовые оригиналы передаются из выбранной копии. Пауза и продолжение управляют всей цепочкой.').classes`, `ui.label(f"Источник для {copy['number']:02d}-copy").classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(choices, value=current if current in choices else None, label='Копировать из').classes`, `ui.select(choices, value=current if current in choices else None, label='Копировать из').classes('w-full').props`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibrariesui-originals-journal"></a>

## `PhotoLibrariesUI.originals_journal`

[photo_libraries_ui.py:409](../../photo_libraries_ui.py#L409)

Показывает события сохранения и пути незавершённых оригиналов. Обрабатывает ошибки: Exception.

```python
async def originals_journal(self, source_id, copy)
```

Прямые выражения вызова: `data.get`, `data['job'].get`, `dialog.open`, `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Записей пока нет').classes`, `ui.label('Незавершённый файл оставлен в копии: ' + path).classes`, `ui.label('Сохранение оригиналов · журнал').classes`, `ui.label(data['job'].get('message', '')).classes`, `ui.label(f"{item['created_at'][:19]} · {item['path']} · {item['message']}").classes`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
