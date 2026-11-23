# UI источников Photos и iCloud Drive: `photo_libraries_ui.py`

Компактный список источников и раскрываемых копий. Показывает превью, расписание и оригиналы Photos, привязку облачных папок и отложенные повторы. Создаёт виртуальные тома для общих панелей.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../photo_libraries_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/icloud_copies.py](media_manager--icloud_copies.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_photo_copy_roles.py](tests.md#module-tests.test_photo_copy_roles), [tests/test_photo_libraries.py](tests.md#module-tests.test_photo_libraries), [tests/test_photos_schedule.py](tests.md#module-tests.test_photos_schedule).

## Оглавление определений

- [PhotoLibrariesUI](#symbol-PhotoLibrariesUI) — Показывает медиатеки, привязанные копии, расписание и команды оригиналов.
- [PhotoLibrariesUI.__init__](#symbol-PhotoLibrariesUI.__init__) — Инициализирует PhotoLibrariesUI и его рабочее состояние.
- [PhotoLibrariesUI.action](#symbol-PhotoLibrariesUI.action) — Исполняет команду источника с единым обновлением UI и обработкой ошибки.
- [PhotoLibrariesUI.add](#symbol-PhotoLibrariesUI.add) — Добавляет текущую системную медиатеку под выбранным названием.
- [PhotoLibrariesUI.authorize](#symbol-PhotoLibrariesUI.authorize) — Запрашивает разрешение на доступ к Photos через Core.
- [PhotoLibrariesUI.bind](#symbol-PhotoLibrariesUI.bind) — Привязывает выбранную файловую папку к медиатеке после проверки выбора.
- [PhotoLibrariesUI.bind_cloud](#symbol-PhotoLibrariesUI.bind_cloud) — Связывает весь iCloud Drive или выбранную слева папку с назначением справа.
- [PhotoLibrariesUI.build](#symbol-PhotoLibrariesUI.build) — Создаёт сворачиваемый список источников, сохраняя прежнюю настройку раскрытия.
- [PhotoLibrariesUI.cloud_copy_menu](#symbol-PhotoLibrariesUI.cloud_copy_menu) — Показывает команды передачи, журнала и отвязки копии iCloud.
- [PhotoLibrariesUI.cloud_copy_status](#symbol-PhotoLibrariesUI.cloud_copy_status) — Подписывает состояние передачи iCloud Drive для компактной строки.
- [PhotoLibrariesUI.cloud_details](#symbol-PhotoLibrariesUI.cloud_details) — Показывает состояние копии и постраничный журнал iCloud Drive.
- [PhotoLibrariesUI.cloud_details.more](#symbol-PhotoLibrariesUI.cloud_details.more) — Получает и добавляет страницу событий в открытый журнал.
- [PhotoLibrariesUI.cloud_menu](#symbol-PhotoLibrariesUI.cloud_menu) — Показывает команду добавления копии для доступного iCloud Drive.
- [PhotoLibrariesUI.cloud_volume](#symbol-PhotoLibrariesUI.cloud_volume) — Возвращает виртуальный том iCloud Drive после первого успешного опроса.
- [PhotoLibrariesUI.connect](#symbol-PhotoLibrariesUI.connect) — Повторяет сопоставление текущей системной медиатеки с сохранённым профилем.
- [PhotoLibrariesUI.connection_menu](#symbol-PhotoLibrariesUI.connection_menu) — Заполняет меню управления системной медиатекой и разрешением Photos.
- [PhotoLibrariesUI.copy_membership](#symbol-PhotoLibrariesUI.copy_membership) — Находит копию медиатеки, содержащую выбранный файловый путь.
- [PhotoLibrariesUI.copy_source_dialog](#symbol-PhotoLibrariesUI.copy_source_dialog) — Показывает выбор Photos или другой копии как источника оригиналов.
- [PhotoLibrariesUI.library_details](#symbol-PhotoLibrariesUI.library_details) — Показывает прогресс и состояние превью в подробностях медиатеки.
- [PhotoLibrariesUI.library_menu](#symbol-PhotoLibrariesUI.library_menu) — Заполняет меню выбранной медиатеки и её настроек.
- [PhotoLibrariesUI.name_dialog](#symbol-PhotoLibrariesUI.name_dialog) — Показывает ввод названия медиатеки и возвращает подтверждённое значение.
- [PhotoLibrariesUI.open_cloud](#symbol-PhotoLibrariesUI.open_cloud) — Открывает дерево iCloud Drive в активной панели с режимом дерева.
- [PhotoLibrariesUI.originals_action](#symbol-PhotoLibrariesUI.originals_action) — Запускает или приостанавливает сохранение оригиналов выбранной копии.
- [PhotoLibrariesUI.originals_journal](#symbol-PhotoLibrariesUI.originals_journal) — Показывает события сохранения и пути незавершённых оригиналов.
- [PhotoLibrariesUI.originals_running](#symbol-PhotoLibrariesUI.originals_running) — Определяет, запущены ли оригиналы копии Photos либо ожидают расписания.
- [PhotoLibrariesUI.photo_copy_menu](#symbol-PhotoLibrariesUI.photo_copy_menu) — Заполняет меню копии Photos командами передачи и связей.
- [PhotoLibrariesUI.refresh](#symbol-PhotoLibrariesUI.refresh) — Обновляет Photos и iCloud независимо, сохраняя раскрытие копий и открытое меню.
- [PhotoLibrariesUI.refresh_copy_roles](#symbol-PhotoLibrariesUI.refresh_copy_roles) — Обновляет метки копий Photos в уже загруженных деревьях.
- [PhotoLibrariesUI.rename](#symbol-PhotoLibrariesUI.rename) — Меняет пользовательское название сохранённой медиатеки.
- [PhotoLibrariesUI.render](#symbol-PhotoLibrariesUI.render) — Перерисовывает компактные заголовки и строки копий Photos и iCloud Drive.
- [PhotoLibrariesUI.render_copy](#symbol-PhotoLibrariesUI.render_copy) — Рисует строку копии с переходом в её папку и подсказкой полного пути.
- [PhotoLibrariesUI.render_signature](#symbol-PhotoLibrariesUI.render_signature) — Отслеживает только изменения состава строк и доступности команд меню.
- [PhotoLibrariesUI.scan](#symbol-PhotoLibrariesUI.scan) — Запрашивает ручное обновление индекса выбранной медиатеки.
- [PhotoLibrariesUI.schedule_dialog](#symbol-PhotoLibrariesUI.schedule_dialog) — Показывает настройку часов разрешённого окна по Москве.
- [PhotoLibrariesUI.set_readout](#symbol-PhotoLibrariesUI.set_readout) — Применяет краткую подпись и подробную подсказку к существующей строке.
- [PhotoLibrariesUI.source](#symbol-PhotoLibrariesUI.source) — Создаёт заголовок источника и отдельный раскрываемый список его копий.
- [PhotoLibrariesUI.source.toggle](#symbol-PhotoLibrariesUI.source.toggle) — Создаёт кнопку раскрытия копий текущего источника.
- [PhotoLibrariesUI.source_line](#symbol-PhotoLibrariesUI.source_line) — Создаёт строку источника или копии с одним показателем и кнопкой команд.
- [PhotoLibrariesUI.toggle](#symbol-PhotoLibrariesUI.toggle) — Переключает ручную паузу выбранной медиатеки.
- [PhotoLibrariesUI.toggle_copies](#symbol-PhotoLibrariesUI.toggle_copies) — Раскрывает или сворачивает список копий отдельного источника.
- [PhotoLibrariesUI.toggle_schedule](#symbol-PhotoLibrariesUI.toggle_schedule) — Включает или выключает ограничение синхронизации ночным окном.
- [PhotoLibrariesUI.track_menu](#symbol-PhotoLibrariesUI.track_menu) — Сохраняет фокус бокового меню при фоновом обновлении.
- [PhotoLibrariesUI.unbind](#symbol-PhotoLibrariesUI.unbind) — Отключает выбранную привязку копии медиатеки через Core.
- [PhotoLibrariesUI.update_readouts](#symbol-PhotoLibrariesUI.update_readouts) — Обновляет компактный статус источников и копий без перерисовки строк.
- [PhotoLibrariesUI.volumes](#symbol-PhotoLibrariesUI.volumes) — Представляет сохранённые медиатеки как виртуальные тома рабочего пространства.
- [library_state](#symbol-library_state) — Определяет пользовательскую подпись доступности и паузы медиатеки.
- [originals_state](#symbol-originals_state) — Преобразует техническое состояние сохранения оригиналов в подпись UI.
- [originals_text](#symbol-originals_text) — Форматирует прогресс объектов и ресурсов привязанной копии Photos.
- [progress_text](#symbol-progress_text) — Формирует подпись прогресса превью одной медиатеки.
- [retry_time](#symbol-retry_time) — Показывает точное время следующей попытки в московском часовом поясе.
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


Состояние, присваиваемое конструктором: `busy`, `cloud`, `connection`, `copy_roles_signature`, `expanded`, `libraries`, `refreshing`, `rows`, `signature`, `ws`.

Именованные методы: `__init__`, `copy_membership`, `refresh_copy_roles`, `volumes`, `build`, `refresh`, `render_signature`, `cloud_volume`, `toggle_copies`, `track_menu`, `source_line`, `source`, `originals_running`, `connection_menu`, `library_menu`, `photo_copy_menu`, `render`, `render_copy`, `set_readout`, `update_readouts`, `library_details`, `open_cloud`, `cloud_menu`, `cloud_copy_status`, `cloud_copy_menu`, `bind_cloud`, `cloud_details`, `action`, `authorize`, `connect`, `toggle`, `toggle_schedule`, `schedule_dialog`, `scan`, `name_dialog`, `add`, `rename`, `bind`, `unbind`, `originals_action`, `copy_source_dialog`, `originals_journal`.

<a id="symbol-PhotoLibrariesUI.__init__"></a>

## `PhotoLibrariesUI.__init__`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.__init__`

Инициализирует PhotoLibrariesUI и его рабочее состояние. Обновляет состояние объекта: busy, copy_roles_signature, libraries, refreshing, rows, signature, ws.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `busy`, `cloud`, `connection`, `copy_roles_signature`, `expanded`, `libraries`, `refreshing`, `rows`, `signature`, `ws`.

Прямые выражения вызова: `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.action"></a>

## `PhotoLibrariesUI.action`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.action`

Исполняет команду источника с единым обновлением UI и обработкой ошибки. Обновляет состояние объекта: busy, signature.

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

Прямые выражения вызова: `library.get`, `next`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), `self.ws.panes[1].scope`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Привязать', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Оригиналы будут сохраняться сразу в эту папку. Для запуска выбери «Сохранить оригиналы» в меню папки копии. Сохранённые оригиналы определяются по учёту Photos и параметрам файлов.').classes`, `ui.label('Привязать папку для копий оригиналов').classes`, `ui.label((volume.get('display_name') or volume['name']) + ' /' + scope['path']).classes`, `ui.label(library.get('label') or 'Photos').classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.bind_cloud"></a>

## `PhotoLibrariesUI.bind_cloud`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.bind_cloud`

Связывает весь iCloud Drive или выбранную слева папку с назначением справа. Асинхронно ожидает: self.action и подтверждение диалога.

```python
async def bind_cloud(self)
```

Прямые выражения вызова: `dict`, `len`, `next`, `reversed`, [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action), `self.expanded.add`, `self.ws.panes[1].scope`, `self.ws.resolve_volume`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(None)).props`, `ui.button('Привязать', on_click=lambda: dialog.submit(source.value)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Назначение').classes`, `ui.label('Привязать копию iCloud Drive').classes`, `ui.label('Чтобы выбрать отдельную папку, открой её в iCloud Drive слева.').classes`, `ui.label((volume.get('display_name') or volume['name']) + ' /' + scope['path']).classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(paths, value=next(reversed(paths)), label='Скопировать из').props`, `ui.select(paths, value=next(reversed(paths)), label='Скопировать из').props('outlined dense').classes`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.build"></a>

## `PhotoLibrariesUI.build`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.build`

Создаёт сворачиваемый список источников, сохраняя прежнюю настройку раскрытия. Обновляет состояние объекта: cards, note, section.

```python
def build(self)
```

Присваивания полям `self`: `cards`, `note`, `section`.

Прямые выражения вызова: `self.note.set_visibility`, `self.ws.sidebar_expansion`, `self.ws.sidebar_expansion('libraries', 'Источники', icon='folder_open').props`, `self.ws.sidebar_expansion('libraries', 'Источники', icon='folder_open').props('dense').classes`, `ui.add_css`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.cloud_copy_menu"></a>

## `PhotoLibrariesUI.cloud_copy_menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.cloud_copy_menu`

Показывает команды передачи, журнала и отвязки копии iCloud. Использует self.action, self.cloud_details.

```python
def cloud_copy_menu(self, copy)
```

Прямые выражения вызова: `ui.menu_item`, `ui.separator`, `unbind.set_enabled`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.cloud_copy_status"></a>

## `PhotoLibrariesUI.cloud_copy_status`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.cloud_copy_status`

Подписывает состояние передачи iCloud Drive для компактной строки. Использует состояние очереди и количество обработанных файлов.

```python
def cloud_copy_status(copy)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `{'idle': '—', 'paused': 'Пауза', 'waiting': 'Ждёт', 'completed': '✓', 'completed_with_conflicts': '⚠'}.get`.

Выражения возврата (ветви, без исполнения):

- `'Офлайн'`
- `{'idle': '—', 'paused': 'Пауза', 'waiting': 'Ждёт', 'completed': '✓', 'completed_with_conflicts': '⚠'}.get(copy['state'], f"{copy['done']}/{copy['total']}")`


<a id="symbol-PhotoLibrariesUI.cloud_details"></a>

## `PhotoLibrariesUI.cloud_details`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.cloud_details`

Показывает состояние копии и постраничный журнал iCloud Drive. Отображает причину и дату каждой запланированной повторной попытки.

```python
async def cloud_details(self, copy_id)
```

Прямые выражения вызова: `dialog.open`, `more`, `next`, [retry_time](photo_libraries_ui.md#symbol-retry_time), `ui.button`, `ui.button('Ещё записи', on_click=more).props`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Повтор ' + retry_time(copy['retry_at'])).classes`, `ui.label(copy['message']).classes`, `ui.label(f"iCloud Drive /{copy['source_path']} → {copy['volume_name']} /{copy['path']}").classes`, `ui.label(f"iCloud Drive · {copy['number']:02d}-copy").classes`, `ui.label(f"{copy['done']} из {copy['total']} файлов · ждут {copy['waiting']} · расхождений {copy['conflicts']}").classes`, `ui.linear_progress`, `ui.linear_progress(value=copy['done'] / copy['total'] if copy['total'] else 0, show_value=False).props`, `ui.row`, `ui.row().classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.cloud_details.more"></a>

## `PhotoLibrariesUI.cloud_details.more`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.cloud_details.more`

Получает и добавляет страницу событий в открытый журнал. Обновляет смещение и видимость кнопки следующей страницы.

```python
async def more()
```

Прямые выражения вызова: `len`, `more_button.disable`, `more_button.enable`, `more_button.set_visibility`, [retry_time](photo_libraries_ui.md#symbol-retry_time), `self.ws.notice`, `self.ws.request`, `ui.label`, `ui.label('Записей пока нет').classes`, `ui.label(f"{item['path'] or '/'} · {item['message'] or 'Готово'}{retry}").classes`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.cloud_menu"></a>

## `PhotoLibrariesUI.cloud_menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.cloud_menu`

Показывает команду добавления копии для доступного iCloud Drive. Использует self.bind_cloud.

```python
def cloud_menu(self)
```

Прямые выражения вызова: `bind.set_enabled`, [self.cloud_volume](photo_libraries_ui.md#symbol-PhotoLibrariesUI.cloud_volume), `ui.menu_item`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.cloud_volume"></a>

## `PhotoLibrariesUI.cloud_volume`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.cloud_volume`

Возвращает виртуальный том iCloud Drive после первого успешного опроса. Использует self.cloud.get.

```python
def cloud_volume(self)
```

Прямые выражения вызова: `self.cloud.get`.

Выражения возврата (ветви, без исполнения):

- `self.cloud.get('volume')`


<a id="symbol-PhotoLibrariesUI.connect"></a>

## `PhotoLibrariesUI.connect`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.connect`

Повторяет сопоставление текущей системной медиатеки с сохранённым профилем. Асинхронно ожидает: self.action.

```python
async def connect(self)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.connection_menu"></a>

## `PhotoLibrariesUI.connection_menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.connection_menu`

Заполняет меню управления системной медиатекой и разрешением Photos. Использует self.add, self.authorize, self.connect.

```python
def connection_menu(self)
```

Прямые выражения вызова: `self.connection.get`, `ui.menu_item`.

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


<a id="symbol-PhotoLibrariesUI.library_details"></a>

## `PhotoLibrariesUI.library_details`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.library_details`

Показывает прогресс и состояние превью в подробностях медиатеки. Использует progress_text, library_state.

```python
def library_details(self, source_id)
```

Прямые выражения вызова: `dialog.open`, `library.get`, [library_state](photo_libraries_ui.md#symbol-library_state), `min`, `next`, [progress_text](photo_libraries_ui.md#symbol-progress_text), [schedule_text](photo_libraries_ui.md#symbol-schedule_text), `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label(library.get('label') or 'Photos').classes`, `ui.label(library_state(library)).classes`, `ui.label(schedule).classes`, `ui.linear_progress`, `ui.linear_progress(value=min(1, done / total) if total else 0, show_value=False).props`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotoLibrariesUI.library_menu"></a>

## `PhotoLibrariesUI.library_menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.library_menu`

Заполняет меню выбранной медиатеки и её настроек. Использует self.connection_menu и существующие команды Photos.

```python
def library_menu(self, library)
```

Прямые выражения вызова: `(library.get('sync_schedule') or {}).get`, `bool`, `library.get`, `scan.set_enabled`, [self.connection_menu](photo_libraries_ui.md#symbol-PhotoLibrariesUI.connection_menu), `ui.menu_item`, `ui.separator`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


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


<a id="symbol-PhotoLibrariesUI.open_cloud"></a>

## `PhotoLibrariesUI.open_cloud`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.open_cloud`

Открывает дерево iCloud Drive в активной панели с режимом дерева. Асинхронно ожидает: self.ws.open_volume.

```python
async def open_cloud(self)
```

Прямые выражения вызова: [self.cloud_volume](photo_libraries_ui.md#symbol-PhotoLibrariesUI.cloud_volume), `self.ws.open_volume`, `ui.notify`.

Выражения возврата (ветви, без исполнения):

- `None`


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

Прямые выражения вызова: `data.get`, `dialog.open`, `dict`, `job.get`, `min`, [originals_text](photo_libraries_ui.md#symbol-originals_text), `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Записей пока нет').classes`, `ui.label('Незавершённый файл оставлен в копии: ' + path).classes`, `ui.label('Сохранение оригиналов · журнал').classes`, `ui.label(f"{copy['volume_name']} /{copy['path']}").classes`, `ui.label(f"{item['created_at'][:19]} · {item['path']} · {item['message']}").classes`, `ui.label(job.get('message', '')).classes`, `ui.label(originals_text(dict(copy, originals=job))).classes`, `ui.linear_progress`, `ui.linear_progress(value=min(1, (job.get('done_assets') or 0) / total) if total else 0, show_value=False).props`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.originals_running"></a>

## `PhotoLibrariesUI.originals_running`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.originals_running`

Определяет, запущены ли оригиналы копии Photos либо ожидают расписания. Использует copy.get, job.get.

```python
def originals_running(copy)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `copy.get`, `job.get`.

Выражения возврата (ветви, без исполнения):

- `job.get('state') in ('manifest', 'inventory', 'saving', 'pausing') or job.get('scheduled', False)`


<a id="symbol-PhotoLibrariesUI.photo_copy_menu"></a>

## `PhotoLibrariesUI.photo_copy_menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.photo_copy_menu`

Заполняет меню копии Photos командами передачи и связей. Использует originals_running для выбора команды передачи.

```python
def photo_copy_menu(self, library, copy)
```

Прямые выражения вызова: [self.originals_running](photo_libraries_ui.md#symbol-PhotoLibrariesUI.originals_running), `ui.menu_item`, `ui.separator`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.refresh"></a>

## `PhotoLibrariesUI.refresh`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.refresh`

Обновляет Photos и iCloud независимо, сохраняя раскрытие копий и открытое меню. Обновляет состояние объекта: cloud, connection, libraries, refreshing, signature.

```python
async def refresh(self)
```

Присваивания полям `self`: `cloud`, `connection`, `libraries`, `refreshing`, `signature`.

Прямые выражения вызова: `bool`, `gather`, `isinstance`, `len`, `library.get`, `pane.preview.refresh_pending`, `pane.update_header`, `photos.get`, `self.note.set_visibility`, [self.refresh_copy_roles](photo_libraries_ui.md#symbol-PhotoLibrariesUI.refresh_copy_roles), [self.render](photo_libraries_ui.md#symbol-PhotoLibrariesUI.render), [self.render_signature](photo_libraries_ui.md#symbol-PhotoLibrariesUI.render_signature), [self.update_readouts](photo_libraries_ui.md#symbol-PhotoLibrariesUI.update_readouts), `self.ws.error_text`, `self.ws.is_photos`, `self.ws.request`.

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

Перерисовывает компактные заголовки и строки копий Photos и iCloud Drive. Сохраняет команды на кнопках меню и правом клике по строке.

```python
def render(self)
```

Прямые выражения вызова: `dict`, `library.get`, [schedule_text](photo_libraries_ui.md#symbol-schedule_text), `self.cards.clear`, [self.cloud_volume](photo_libraries_ui.md#symbol-PhotoLibrariesUI.cloud_volume), [self.render_copy](photo_libraries_ui.md#symbol-PhotoLibrariesUI.render_copy), `self.rows.clear`, [self.source](photo_libraries_ui.md#symbol-PhotoLibrariesUI.source), [self.source_line](photo_libraries_ui.md#symbol-PhotoLibrariesUI.source_line).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.render_copy"></a>

## `PhotoLibrariesUI.render_copy`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.render_copy`

Рисует строку копии с переходом в её папку и подсказкой полного пути. Возвращает показатель состояния строки.

```python
def render_copy(self, copy, on_menu)
```

Прямые выражения вызова: [self.source_line](photo_libraries_ui.md#symbol-PhotoLibrariesUI.source_line).

Выражения возврата (ветви, без исполнения):

- `self.source_line(f"{copy['number']:02d}-copy · {copy['volume_name']}", lambda: self.ws.open_volume(copy['volume_id'], 1, path=copy['path']), on_menu, path=f"{copy['volume_name']} /{copy['path']}", copy=True)`


<a id="symbol-PhotoLibrariesUI.render_signature"></a>

## `PhotoLibrariesUI.render_signature`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.render_signature`

Отслеживает только изменения состава строк и доступности команд меню. Числовой прогресс и подробности обновляются на существующих элементах UI.

```python
def render_signature(self)
```

Прямые выражения вызова: `(library.get('sync_schedule') or {}).get`, `c.get`, `library.get`, `self.cloud.get`, `self.connection.get`, [self.originals_running](photo_libraries_ui.md#symbol-PhotoLibrariesUI.originals_running), `tuple`.

Выражения возврата (ветви, без исполнения):

- `(photos, cloud, self.cloud.get('volume'), self.connection.get('state'))`


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


<a id="symbol-PhotoLibrariesUI.set_readout"></a>

## `PhotoLibrariesUI.set_readout`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.set_readout`

Применяет краткую подпись и подробную подсказку к существующей строке. Обновляет поля элементов label и tooltip.

```python
def set_readout(elements, text, details)
```

Декораторы: `staticmethod`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.source"></a>

## `PhotoLibrariesUI.source`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.source`

Создаёт заголовок источника и отдельный раскрываемый список его копий. Возвращает показатель заголовка и контейнер строк копий.

```python
def source(self, key, name, on_open, on_menu, *, active, copies, schedule='', title=None)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `children.set_visibility`, [self.source_line](photo_libraries_ui.md#symbol-PhotoLibrariesUI.source_line), `ui.column`, `ui.column().classes`, `ui.label`, `ui.label(schedule).classes`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-PhotoLibrariesUI.source.toggle"></a>

## `PhotoLibrariesUI.source.toggle`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.source.toggle`

Создаёт кнопку раскрытия копий текущего источника. Открытие изменяет видимость строк без повторного запроса Core.

```python
def toggle()
```

Прямые выражения вызова: `str`, `str(opened).lower`, `ui.button`, `ui.button(icon='expand_more' if opened else 'chevron_right', on_click=lambda: self.toggle_copies(key, button, children)).props`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.source_line"></a>

## `PhotoLibrariesUI.source_line`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.source_line`

Создаёт строку источника или копии с одним показателем и кнопкой команд. Возвращает обновляемую подпись показателя и её подсказку.

```python
def source_line(self, name, on_open, on_menu, *, active=False, copy=False, path=None, toggle=None)
```

Прямые выражения вызова: `button.tooltip`, `line.on`, `on_menu`, [self.track_menu](photo_libraries_ui.md#symbol-PhotoLibrariesUI.track_menu), [toggle](photo_libraries_ui.md#symbol-PhotoLibrariesUI.toggle), `ui.button`, `ui.button(icon='more_horiz').props`, `ui.button(name, on_click=on_open).props`, `ui.button(name, on_click=on_open).props('flat dense no-caps color=dark align=left').classes`, `ui.label`, `ui.label().classes`, `ui.menu`, `ui.menu().props`, `ui.row`, `ui.row().classes`, `ui.tooltip`.

Выражения возврата (ветви, без исполнения):

- `(status, detail)`


<a id="symbol-PhotoLibrariesUI.toggle"></a>

## `PhotoLibrariesUI.toggle`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.toggle`

Переключает ручную паузу выбранной медиатеки. Асинхронно ожидает: self.action.

```python
async def toggle(self, library)
```

Прямые выражения вызова: [self.action](photo_libraries_ui.md#symbol-PhotoLibrariesUI.action).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotoLibrariesUI.toggle_copies"></a>

## `PhotoLibrariesUI.toggle_copies`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.toggle_copies`

Раскрывает или сворачивает список копий отдельного источника. Обновляет состояние объекта: expanded и видимость списка.

```python
def toggle_copies(self, key, button, copies)
```

Прямые выражения вызова: `button.props`, `copies.set_visibility`, `self.expanded.add`, `self.expanded.remove`, `str`, `str(opened).lower`.

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


<a id="symbol-PhotoLibrariesUI.track_menu"></a>

## `PhotoLibrariesUI.track_menu`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.track_menu`

Сохраняет фокус бокового меню при фоновом обновлении. Использует menu.on.

```python
def track_menu(self, menu)
```

Прямые выражения вызова: `menu.on`.

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


<a id="symbol-PhotoLibrariesUI.update_readouts"></a>

## `PhotoLibrariesUI.update_readouts`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `PhotoLibrariesUI.update_readouts`

Обновляет компактный статус источников и копий без перерисовки строк. Использует полные подписи прогресса в подсказках.

```python
def update_readouts(self)
```

Прямые выражения вызова: `copy.get`, `int`, `job.get`, `len`, `library.get`, [library_state](photo_libraries_ui.md#symbol-library_state), [originals_state](photo_libraries_ui.md#symbol-originals_state), [originals_text](photo_libraries_ui.md#symbol-originals_text), [progress_text](photo_libraries_ui.md#symbol-progress_text), `row['copies'].get`, [self.cloud_copy_status](photo_libraries_ui.md#symbol-PhotoLibrariesUI.cloud_copy_status), [self.cloud_volume](photo_libraries_ui.md#symbol-PhotoLibrariesUI.cloud_volume), `self.connection.get`, `self.rows.get`, [self.set_readout](photo_libraries_ui.md#symbol-PhotoLibrariesUI.set_readout).

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


<a id="symbol-retry_time"></a>

## `retry_time`

[photo_libraries_ui.py](../../photo_libraries_ui.py) · `retry_time`

Показывает точное время следующей попытки в московском часовом поясе. Принимает Unix-время из журнала iCloud Drive.

```python
def retry_time(timestamp)
```

Прямые выражения вызова: `ZoneInfo`, `datetime.fromtimestamp`, `datetime.fromtimestamp(timestamp, ZoneInfo('Europe/Moscow')).strftime`.

Выражения возврата (ветви, без исполнения):

- `datetime.fromtimestamp(timestamp, ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S МСК')`


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
