# UI связанных пар: `paired_workspace_ui.py`

Координирует связанные панели: общий корень, раскрытие и выбор, опрос отчёта, диалоги плана копирования, результаты и история. Отображение больших списков передаёт Vue-компоненту.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../paired_workspace_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [paired_tree.py](paired_tree.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_paired_workspace.py](tests.md#module-tests.test_paired_workspace), [tests/test_tree_keyboard.py](tests.md#module-tests.test_tree_keyboard), [tests/test_workspace_state.py](tests.md#module-tests.test_workspace_state).

## Оглавление определений

- [PairedWorkspace](#symbol-PairedWorkspace) — Управляет связанными панелями, отчётом пары и подтверждением копирования.
- [PairedWorkspace.__init__](#symbol-PairedWorkspace.__init__) — Инициализирует PairedWorkspace и его рабочее состояние.
- [PairedWorkspace.apply](#symbol-PairedWorkspace.apply) — Применяет отчёт пары, сохраняя подходящее состояние раскрытия и выбора.
- [PairedWorkspace.apply_copy_operation](#symbol-PairedWorkspace.apply_copy_operation) — Применяет прогресс операции и при необходимости открывает итоговую сверку.
- [PairedWorkspace.build](#symbol-PairedWorkspace.build) — Создаёт центральную панель управления связанной парой.
- [PairedWorkspace.choose](#symbol-PairedWorkspace.choose) — Выбирает общий относительный путь в обеих сторонах пары.
- [PairedWorkspace.collapse_all](#symbol-PairedWorkspace.collapse_all) — Сворачивает или раскрывает каталоги связанного отчёта.
- [PairedWorkspace.configure_view](#symbol-PairedWorkspace.configure_view) — Передаёт компоненту строки, выбор и дополнительные свойства связанного дерева.
- [PairedWorkspace.copy_details](#symbol-PairedWorkspace.copy_details) — Показывает прогресс, состав и результаты операции копирования.
- [PairedWorkspace.copy_item_list](#symbol-PairedWorkspace.copy_item_list) — Показывает весь зафиксированный план копирования постранично.
- [PairedWorkspace.copy_item_list.append](#symbol-PairedWorkspace.copy_item_list.append) — Добавляет страницу элементов и результатов плана в открытый диалог.
- [PairedWorkspace.copy_item_list.load_more](#symbol-PairedWorkspace.copy_item_list.load_more) — Запрашивает следующую страницу элементов плана копирования.
- [PairedWorkspace.copy_paths](#symbol-PairedWorkspace.copy_paths) — Формирует подписи исходной и целевой папок сохранённого плана.
- [PairedWorkspace.copy_running](#symbol-PairedWorkspace.copy_running) — Проверяет активность текущей операции копирования по её состоянию.
- [PairedWorkspace.decide](#symbol-PairedWorkspace.decide) — Открывает выбор планового решения для элемента только в копии.
- [PairedWorkspace.details](#symbol-PairedWorkspace.details) — Показывает итоги парной сверки, счётчики и выбранные области.
- [PairedWorkspace.history](#symbol-PairedWorkspace.history) — Показывает историю выбранной связи и открывает сохранённый отчёт пары.
- [PairedWorkspace.history.choose](#symbol-PairedWorkspace.history.choose) — Открывает выбранный отчёт истории пары после проверки отсутствия активного копирования.
- [PairedWorkspace.history.legacy](#symbol-PairedWorkspace.history.legacy) — Закрывает историю пары и открывает действующий диалог прежних отчётов по именам.
- [PairedWorkspace.link](#symbol-PairedWorkspace.link) — Связывает выбранный источник с копией, сохраняя прежнее состояние панелей.
- [PairedWorkspace.load_rows](#symbol-PairedWorkspace.load_rows) — Загружает страницы выровненных строк с проверкой актуальности выбранного задания.
- [PairedWorkspace.navigate](#symbol-PairedWorkspace.navigate) — Делает относительную папку общим корнем связанных деревьев.
- [PairedWorkspace.navigate_path](#symbol-PairedWorkspace.navigate_path) — Переходит к относительному пути внутри допустимой области пары.
- [PairedWorkspace.on_context](#symbol-PairedWorkspace.on_context) — Распределяет команды контекстного меню между свойствами, Finder и решениями.
- [PairedWorkspace.on_menu_state](#symbol-PairedWorkspace.on_menu_state) — Учитывает открытое контекстное меню при периодических обновлениях дерева.
- [PairedWorkspace.on_open](#symbol-PairedWorkspace.on_open) — Обрабатывает открытие папки или файла в связанном дереве.
- [PairedWorkspace.on_select](#symbol-PairedWorkspace.on_select) — Обрабатывает выбор строки виртуального дерева и обновляет превью.
- [PairedWorkspace.on_toggle](#symbol-PairedWorkspace.on_toggle) — Меняет раскрытие папки сразу для двух сторон пары.
- [PairedWorkspace.poll](#symbol-PairedWorkspace.poll) — Обновляет состояние парной сверки и операции копирования через API.
- [PairedWorkspace.prepare_copy](#symbol-PairedWorkspace.prepare_copy) — Создаёт план, показывает его пользователю и запускает после подтверждения.
- [PairedWorkspace.redraw](#symbol-PairedWorkspace.redraw) — Обновляет оба связанных дерева и центральное управление.
- [PairedWorkspace.relative](#symbol-PairedWorkspace.relative) — Преобразует путь тома в путь относительно выбранной стороны пары.
- [PairedWorkspace.render_rail](#symbol-PairedWorkspace.render_rail) — Обновляет команды, прогресс и состояние центральной панели пары.
- [PairedWorkspace.render_tree](#symbol-PairedWorkspace.render_tree) — Создаёт или обновляет виртуализированное дерево одной стороны пары.
- [PairedWorkspace.report_title](#symbol-PairedWorkspace.report_title) — Формирует название сверки по режиму и методу проверки файлов.
- [PairedWorkspace.restore_view](#symbol-PairedWorkspace.restore_view) — Восстанавливает корень, раскрытие и фильтры связанного дерева из снимка вкладки.
- [PairedWorkspace.resume](#symbol-PairedWorkspace.resume) — Продолжает приостановленную парную сверку через API Core.
- [PairedWorkspace.set_hidden](#symbol-PairedWorkspace.set_hidden) — Согласует показ скрытых элементов в двух связанных панелях.
- [PairedWorkspace.start](#symbol-PairedWorkspace.start) — Создаёт новую парную сверку заданного режима и метода через Core.
- [PairedWorkspace.stop](#symbol-PairedWorkspace.stop) — Запрашивает паузу активной парной сверки.
- [PairedWorkspace.stop_copy](#symbol-PairedWorkspace.stop_copy) — Запрашивает остановку активного копирования отсутствующих элементов.
- [PairedWorkspace.toggle_differences](#symbol-PairedWorkspace.toggle_differences) — Переключает фильтр различий и обновляет набор загружаемых строк.
- [PairedWorkspace.toggle_root_files](#symbol-PairedWorkspace.toggle_root_files) — Переключает показ файлов непосредственно в текущем корне пары.
- [PairedWorkspace.unlink](#symbol-PairedWorkspace.unlink) — Размыкает панели и восстанавливает независимый просмотр после остановки работы.
- [PairedWorkspace.update_header](#symbol-PairedWorkspace.update_header) — Обновляет путь и границы связанной стороны панели.
- [PairedWorkspace.visible_rows](#symbol-PairedWorkspace.visible_rows) — Отбирает строки с учётом корня, раскрытия, скрытых файлов и различий.

## Константы и значения по умолчанию

<a id="constant-PAIR_CSS"></a>

### `PAIR_CSS`

`Объёмное значение см. в исходном модуле`


<a id="symbol-PairedWorkspace"></a>

## `PairedWorkspace`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace`

Управляет связанными панелями, отчётом пары и подтверждением копирования. Зависимости конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `active`, `by_path`, `closed`, `copy_dialog_open`, `copy_id`, `copy_operation`, `differences_only`, `generation`, `history_only`, `loaded_job`, `pending_start`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `saved`, `saved_active`, `scopes`, `selected`, `show_hidden`, `structure_at`, `views`, `ws`.

Именованные методы: `__init__`, `copy_running`, `report_title`, `build`, `render_rail`, `link`, `unlink`, `update_header`, `relative`, `navigate_path`, `visible_rows`, `configure_view`, `render_tree`, `redraw`, `choose`, `navigate`, `on_select`, `on_open`, `on_toggle`, `collapse_all`, `toggle_root_files`, `toggle_differences`, `set_hidden`, `start`, `apply`, `restore_view`, `load_rows`, `poll`, `apply_copy_operation`, `stop_copy`, `copy_paths`, `copy_item_list`, `prepare_copy`, `copy_details`, `stop`, `resume`, `details`, `on_menu_state`, `on_context`, `decide`, `history`.

<a id="symbol-PairedWorkspace.__init__"></a>

## `PairedWorkspace.__init__`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.__init__`

Инициализирует PairedWorkspace и его рабочее состояние. Обновляет состояние объекта: active, by_path, closed, copy_dialog_open, copy_id, copy_operation, differences_only, generation, history_only, loaded_job и ещё 15.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `active`, `by_path`, `closed`, `copy_dialog_open`, `copy_id`, `copy_operation`, `differences_only`, `generation`, `history_only`, `loaded_job`, `pending_start`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `saved`, `saved_active`, `scopes`, `selected`, `show_hidden`, `structure_at`, `views`, `ws`.

Прямые выражения вызова: `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.apply"></a>

## `PairedWorkspace.apply`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.apply`

Применяет отчёт пары, сохраняя подходящее состояние раскрытия и выбора. Обновляет состояние объекта: by_path, closed, copy_operation, differences_only, pending_view, rail_signature, report, root, root_files_open, rows, scopes и ещё 2.

```python
async def apply(self, report)
```

Присваивания полям `self`: `by_path`, `closed`, `copy_operation`, `differences_only`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `scopes`, `selected`, `structure_at`.

Прямые выражения вызова: `bool`, `pane.folders.clear`, `pane.render`, `pane.tree.clear`, `pane.volume_select.set_value`, `report.get`, [self.choose](paired_workspace_ui.md#symbol-PairedWorkspace.choose), [self.load_rows](paired_workspace_ui.md#symbol-PairedWorkspace.load_rows), [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), [self.set_hidden](paired_workspace_ui.md#symbol-PairedWorkspace.set_hidden), `self.views.clear`, `set`, `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.apply_copy_operation"></a>

## `PairedWorkspace.apply_copy_operation`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.apply_copy_operation`

Применяет прогресс операции и при необходимости открывает итоговую сверку. Обновляет состояние объекта: copy_operation, rail_signature.

```python
async def apply_copy_operation(self, operation)
```

Присваивания полям `self`: `copy_operation`, `rail_signature`.

Прямые выражения вызова: `operation.get`, [self.apply](paired_workspace_ui.md#symbol-PairedWorkspace.apply), [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), `self.ws.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.build"></a>

## `PairedWorkspace.build`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.build`

Создаёт центральную панель управления связанной парой. Обновляет состояние объекта: rail.

```python
def build(self)
```

Присваивания полям `self`: `rail`.

Прямые выражения вызова: [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), `ui.add_css`, `ui.column`, `ui.column().classes`, `ui.timer`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.choose"></a>

## `PairedWorkspace.choose`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.choose`

Выбирает общий относительный путь в обеих сторонах пары. Обновляет состояние объекта: selected.

```python
def choose(self, relative)
```

Присваивания полям `self`: `selected`.

Прямые выражения вызова: `(data or row or {}).get`, `absolute_scope_path`, `dict`, `row.get`, `self.by_path.get`, `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.collapse_all"></a>

## `PairedWorkspace.collapse_all`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.collapse_all`

Сворачивает или раскрывает каталоги связанного отчёта. Обновляет состояние объекта: closed, root_files_open.

```python
def collapse_all(self, value)
```

Присваивания полям `self`: `closed`, `root_files_open`.

Прямые выражения вызова: [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw), `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.configure_view"></a>

## `PairedWorkspace.configure_view`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.configure_view`

Передаёт компоненту строки, выбор и дополнительные свойства связанного дерева. Использует PurePosixPath, any, p.startswith, self.report.get, self.ws.size_texts.

```python
def configure_view(self, view)
```

Прямые выражения вызова: `PurePosixPath`, `any`, `p.startswith`, `self.report.get`, `self.ws.size_texts`, `str`, `sum`, `view.props.update`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.copy_details"></a>

## `PairedWorkspace.copy_details`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.copy_details`

Показывает прогресс, состав и результаты операции копирования. Обрабатывает ошибки: Exception.

```python
async def copy_details(self)
```

Прямые выражения вызова: `dialog.open`, `operation.get`, [self.copy_item_list](paired_workspace_ui.md#symbol-PairedWorkspace.copy_item_list), [self.copy_paths](paired_workspace_ui.md#symbol-PairedWorkspace.copy_paths), `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Копирование из ' + self.scopes['left']['label'] + ' →').classes`, `ui.label(f"Готово файлов: {operation['copied_files']} · папок: {operation['copied_directories']} · пропущено: {operation['skipped']} · ошибок: {operation['errors']}").classes`, `ui.label(f"Незавершённых файлов в копии: {operation['incomplete_files']}").classes`, `ui.label(operation['current_path']).classes`, `ui.label(operation['message']).classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.copy_item_list"></a>

## `PairedWorkspace.copy_item_list`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.copy_item_list`

Показывает весь зафиксированный план копирования постранично. Асинхронно ожидает: self.ws.request.

```python
async def copy_item_list(self, operation)
```

Прямые выражения вызова: `append`, `more.on_click`, `self.ws.request`, `ui.button`, `ui.button('Показать ещё 200').props`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.copy_item_list.append"></a>

## `PairedWorkspace.copy_item_list.append`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.copy_item_list.append`

Добавляет страницу элементов и результатов плана в открытый диалог. Использует item.get, more.set_visibility, self.ws.format_bytes, ui.column, ui.column().classes.

```python
def append(data)
```

Прямые выражения вызова: `item.get`, `len`, `more.set_visibility`, `self.ws.format_bytes`, `ui.column`, `ui.column().classes`, `ui.icon`, `ui.icon('folder' if item['kind'] == 'directory' else 'insert_drive_file', size='16px').classes`, `ui.label`, `ui.label('Копия не завершена').classes`, `ui.label(item['message']).classes`, `ui.label(item['path']).classes`, `ui.label(self.ws.format_bytes(item['size'])).classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.copy_item_list.load_more"></a>

## `PairedWorkspace.copy_item_list.load_more`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.copy_item_list.load_more`

Запрашивает следующую страницу элементов плана копирования. Обрабатывает ошибки: Exception.

```python
async def load_more()
```

Прямые выражения вызова: [append](paired_workspace_ui.md#symbol-PairedWorkspace.copy_item_list.append), `more.disable`, `more.enable`, `self.ws.notice`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.copy_paths"></a>

## `PairedWorkspace.copy_paths`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.copy_paths`

Формирует подписи исходной и целевой папок сохранённого плана. Использует ui.label, ui.label(scope['label'] + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes.

```python
def copy_paths(self, operation)
```

Прямые выражения вызова: `ui.label`, `ui.label(scope['label'] + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.copy_running"></a>

## `PairedWorkspace.copy_running`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.copy_running`

Проверяет активность текущей операции копирования по её состоянию. Возвращает локальное значение без обращения к файловой системе.

```python
def copy_running(self)
```

Декораторы: `property`.

Прямые выражения вызова: `bool`.

Выражения возврата (ветви, без исполнения):

- `bool(self.copy_operation and self.copy_operation['state'] in ('running', 'stopping'))`


<a id="symbol-PairedWorkspace.decide"></a>

## `PairedWorkspace.decide`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.decide`

Открывает выбор планового решения для элемента только в копии. Обрабатывает ошибки: Exception.

```python
async def decide(self, row)
```

Прямые выражения вызова: `row.get`, [self.load_rows](paired_workspace_ui.md#symbol-PairedWorkspace.load_rows), `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Сохранить решение', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('От папки ' + row['decision_from'] + ': ' + DECISIONS[row['decision']]).classes`, `ui.label('Сейчас сохраняется решение. Файловые операции будут выполняться отдельно.').classes`, `ui.label('Только в копии').classes`, `ui.label(row['path']).classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select({'': 'Наследовать / снять отдельное решение', **DECISIONS}, value=row.get('own_decision') or '', label='Что сделать').props`, `ui.select({'': 'Наследовать / снять отдельное решение', **DECISIONS}, value=row.get('own_decision') or '', label='Что сделать').props('outlined dense').classes`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.details"></a>

## `PairedWorkspace.details`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.details`

Показывает итоги парной сверки, счётчики и выбранные области. Использует dialog.open, report.get, report.get('root_errors', {}).items, report['counts'].items, row.get.

```python
async def details(self)
```

Прямые выражения вызова: `dialog.open`, `report.get`, `report.get('root_errors', {}).items`, `report['counts'].items`, `row.get`, `row[side].get`, [self.report_title](paired_workspace_ui.md#symbol-PairedWorkspace.report_title), `self.ws.format_date`, `str`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.button(row['path'] + (' · ' + DECISIONS[row['decision']] if row['decision'] else ''), on_click=lambda r=row: self.decide(r)).props`, `ui.button(row['path'] + (' · ' + DECISIONS[row['decision']] if row['decision'] else ''), on_click=lambda r=row: self.decide(r)).props('flat dense no-caps color=purple-8').classes`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Итоги · ' + self.report_title(report)).classes`, `ui.label('Только в копии · выбери решение').classes`, `ui.label(explanation).classes`, `ui.label(f"Не удалось прочитать элементов: {report['errors']}").classes`, `ui.label(f"Прочитано каталогов: {report['indexed_directories']}").classes`, `ui.label(report['current_path']).classes`, `ui.label(self.scopes[side]['label'] + ' /' + path + ': ' + error).classes`, `ui.label(self.scopes[side]['label'] + ': ' + error).classes`, `ui.label(self.ws.format_date(report['created_at']) + ' · ' + report['message']).classes`, `ui.label(title + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.history"></a>

## `PairedWorkspace.history`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.history`

Показывает историю выбранной связи и открывает сохранённый отчёт пары. Обрабатывает ошибки: Exception.

```python
async def history(self, *, group=None, location=None)
```

Прямые выражения вызова: `dialog.open`, [self.report_title](paired_workspace_ui.md#symbol-PairedWorkspace.report_title), `self.ws.format_date`, `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.button('Прежние отчёты по именам', on_click=legacy).props`, `ui.button(label, on_click=lambda j=job: choose(j)).props`, `ui.button(label, on_click=lambda j=job: choose(j)).props('flat no-caps color=green-9').classes`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('История сверок пары').classes`, `ui.label('Эта пара ещё не проверялась.').classes`, `ui.label(location['label'] + ' · ' + location['volume_name'] + ' /' + location['path']).classes`, `ui.separator`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.history.choose"></a>

## `PairedWorkspace.history.choose`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.history.choose`

Открывает выбранный отчёт истории пары после проверки отсутствия активного копирования. Явно отклоняет недопустимое состояние через ValueError.

```python
async def choose(job)
```

Присваивания полям `self`: `generation`.

Прямые выражения вызова: `ValueError`, `dialog.close`, [self.apply](paired_workspace_ui.md#symbol-PairedWorkspace.apply), [self.link](paired_workspace_ui.md#symbol-PairedWorkspace.link), `self.ws.notice`, `self.ws.persist_workspace`.

Явные `raise`:

- `ValueError('Сначала дождись завершения копирования.')`

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.history.legacy"></a>

## `PairedWorkspace.history.legacy`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.history.legacy`

Закрывает историю пары и открывает действующий диалог прежних отчётов по именам. Использует dialog.close, self.ws.legacy_dialog.open.

```python
def legacy()
```

Прямые выражения вызова: `dialog.close`, `self.ws.legacy_dialog.open`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.link"></a>

## `PairedWorkspace.link`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.link`

Связывает выбранный источник с копией, сохраняя прежнее состояние панелей. Обновляет состояние объекта: active, by_path, copy_id, copy_operation, differences_only, generation, history_only, loaded_job, pending_start, pending_view и ещё 10.

```python
async def link(self, group, location, *, load_folders=True)
```

Присваивания полям `self`: `active`, `by_path`, `copy_id`, `copy_operation`, `differences_only`, `generation`, `history_only`, `loaded_job`, `pending_start`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `saved`, `saved_active`, `scopes`, `selected`, `show_hidden`.

Прямые выражения вызова: `ValueError`, `any`, `asyncio.gather`, `bool`, `location.get`, `next`, `p.save_browse_state`, `p.show_volume`, `self.closed.clear`, [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), `self.scopes.values`, [self.stop](paired_workspace_ui.md#symbol-PairedWorkspace.stop), [self.stop_copy](paired_workspace_ui.md#symbol-PairedWorkspace.stop_copy), `self.views.clear`, `self.ws.browse`, `self.ws.notice`, `self.ws.set_active`, `self.ws.update_scopes`, `source.get`, `zip`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.load_rows"></a>

## `PairedWorkspace.load_rows`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.load_rows`

Загружает страницы выровненных строк с проверкой актуальности выбранного задания. Обновляет состояние объекта: by_path, closed, loaded_job, pending_view, rail_signature, root_files_open, rows, structure_at.

```python
async def load_rows(self, job)
```

Присваивания полям `self`: `by_path`, `closed`, `loaded_job`, `pending_view`, `rail_signature`, `root_files_open`, `rows`, `structure_at`.

Прямые выражения вызова: `PurePosixPath`, `r.get`, `range`, `row.get`, `row[side].get`, [self.choose](paired_workspace_ui.md#symbol-PairedWorkspace.choose), [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw), [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), [self.restore_view](paired_workspace_ui.md#symbol-PairedWorkspace.restore_view), `self.ws.format_bytes`, `self.ws.request`, `str`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.navigate"></a>

## `PairedWorkspace.navigate`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.navigate`

Делает относительную папку общим корнем связанных деревьев. Обновляет состояние объекта: root, root_files_open.

```python
def navigate(self, relative)
```

Присваивания полям `self`: `root`, `root_files_open`.

Прямые выражения вызова: [self.choose](paired_workspace_ui.md#symbol-PairedWorkspace.choose), `self.closed.discard`, [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw), `self.views.values`, `view.run_method`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.navigate_path"></a>

## `PairedWorkspace.navigate_path`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.navigate_path`

Переходит к относительному пути внутри допустимой области пары. Обновляет состояние объекта: root, selected.

```python
async def navigate_path(self, index, path)
```

Присваивания полям `self`: `root`, `selected`.

Прямые выражения вызова: `absolute_scope_path`, `asyncio.gather`, `p.show_volume`, [self.navigate](paired_workspace_ui.md#symbol-PairedWorkspace.navigate), [self.relative](paired_workspace_ui.md#symbol-PairedWorkspace.relative), `self.scopes.values`, `self.ws.open_volume`, `zip`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.on_context"></a>

## `PairedWorkspace.on_context`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.on_context`

Распределяет команды контекстного меню между свойствами, Finder и решениями. Асинхронно ожидает: self.decide, self.ws.open_in_finder, self.ws.show_properties.

```python
async def on_context(self, event)
```

Прямые выражения вызова: `event.args.get`, `row.get`, `self.by_path.get`, [self.decide](paired_workspace_ui.md#symbol-PairedWorkspace.decide), `self.ws.open_in_finder`, `self.ws.show_properties`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.on_menu_state"></a>

## `PairedWorkspace.on_menu_state`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.on_menu_state`

Учитывает открытое контекстное меню при периодических обновлениях дерева. Параметры: event.

```python
def on_menu_state(self, event)
```

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.on_open"></a>

## `PairedWorkspace.on_open`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.on_open`

Обрабатывает открытие папки или файла в связанном дереве. Асинхронно ожидает: self.ws.preview_selection.

```python
async def on_open(self, event)
```

Прямые выражения вызова: `self.by_path.get`, [self.navigate](paired_workspace_ui.md#symbol-PairedWorkspace.navigate), `self.ws.preview_selection`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.on_select"></a>

## `PairedWorkspace.on_select`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.on_select`

Обрабатывает выбор строки виртуального дерева и обновляет превью. Асинхронно ожидает: self.ws.preview_selection.

```python
async def on_select(self, event)
```

Прямые выражения вызова: `event.args.get`, [self.choose](paired_workspace_ui.md#symbol-PairedWorkspace.choose), `self.closed.discard`, [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw), `self.ws.preview_selection`, `self.ws.set_active`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.on_toggle"></a>

## `PairedWorkspace.on_toggle`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.on_toggle`

Меняет раскрытие папки сразу для двух сторон пары. Использует self.closed.add, self.closed.remove, self.redraw.

```python
async def on_toggle(self, event)
```

Прямые выражения вызова: `self.closed.add`, `self.closed.remove`, [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.poll"></a>

## `PairedWorkspace.poll`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.poll`

Обновляет состояние парной сверки и операции копирования через API. Обрабатывает ошибки: Exception.

```python
async def poll(self)
```

Прямые выражения вызова: [self.apply](paired_workspace_ui.md#symbol-PairedWorkspace.apply), [self.apply_copy_operation](paired_workspace_ui.md#symbol-PairedWorkspace.apply_copy_operation), `self.ws.error_text`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.prepare_copy"></a>

## `PairedWorkspace.prepare_copy`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.prepare_copy`

Создаёт план, показывает его пользователю и запускает после подтверждения. Обновляет состояние объекта: copy_dialog_open, rail_signature.

```python
async def prepare_copy(self)
```

Присваивания полям `self`: `copy_dialog_open`, `rail_signature`.

Прямые выражения вызова: [self.apply_copy_operation](paired_workspace_ui.md#symbol-PairedWorkspace.apply_copy_operation), [self.copy_item_list](paired_workspace_ui.md#symbol-PairedWorkspace.copy_item_list), [self.copy_paths](paired_workspace_ui.md#symbol-PairedWorkspace.copy_paths), [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), `self.ws.format_bytes`, `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Начать копирование', on_click=lambda: dialog.submit(True)).props`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Копируется вся проверенная пара. Существующие файлы и элементы с другим размером останутся на месте.').classes`, `ui.label('Незавершённые копии при прерывании записи будут отмечены для ручного разбора.').classes`, `ui.label('Скопировать отсутствующее →').classes`, `ui.label(f"Файлов: {operation['total_files']} · папок: {operation['total_directories']} · {self.ws.format_bytes(operation['total_bytes'])}").classes`, `ui.row`, `ui.row().classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.redraw"></a>

## `PairedWorkspace.redraw`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.redraw`

Обновляет оба связанных дерева и центральное управление. Использует pane.update_header, self.configure_view, self.render_tree, self.views[side].run_method, self.views[side].set_rows.

```python
def redraw(self, rows_changed=True)
```

Прямые выражения вызова: `pane.update_header`, [self.configure_view](paired_workspace_ui.md#symbol-PairedWorkspace.configure_view), [self.render_tree](paired_workspace_ui.md#symbol-PairedWorkspace.render_tree), `self.views[side].run_method`, `self.views[side].set_rows`, [self.visible_rows](paired_workspace_ui.md#symbol-PairedWorkspace.visible_rows), `self.ws.update_scopes`, `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.relative"></a>

## `PairedWorkspace.relative`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.relative`

Преобразует путь тома в путь относительно выбранной стороны пары. Использует path.startswith.

```python
def relative(self, index, path)
```

Прямые выражения вызова: `len`, `path.startswith`.

Выражения возврата (ветви, без исполнения):

- `''`
- `path[len(prefix):] if path.startswith(prefix) else None`


<a id="symbol-PairedWorkspace.render_rail"></a>

## `PairedWorkspace.render_rail`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.render_rail`

Обновляет команды, прогресс и состояние центральной панели пары. Обновляет состояние объекта: rail_signature.

```python
def render_rail(self)
```

Присваивания полям `self`: `rail_signature`.

Прямые выражения вызова: `(self.copy_operation or {}).get`, `(self.report or {}).get`, `bool`, `button.set_enabled`, `copy.set_enabled`, `files.set_enabled`, `folders.set_enabled`, `hasattr`, `max`, `min`, `next`, `self.rail.clear`, `self.rail.set_visibility`, `self.report.get`, `self.report.get('counts', {}).get`, `self.ws.trees.classes`, `stop.set_enabled`, `str`, `tuple`, `ui.button`, `ui.button('Далее', icon='play_arrow', on_click=self.resume).props`, `ui.button('Два дерева', icon='account_tree', on_click=lambda: preview.set_mode('tree')).props`, `ui.button('Закрыть', icon='link_off', on_click=self.unlink).props`, `ui.button('История', icon='history', on_click=self.history).props`, `ui.button('Итоги', icon='format_list_bulleted', on_click=self.details).props`, `ui.button('Копия', icon='assignment', on_click=self.copy_details).props`, `ui.button('Отчёт', icon='history', on_click=self.ws.legacy_dialog.open).props`, `ui.button('Папки', icon='folder', on_click=lambda: self.start('folders')).props`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.unlink).props`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.unlink).props('flat no-caps color=grey-7 aria-label="Разомкнуть панели"').classes`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.ws.browse).props`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.ws.browse).props('flat no-caps color=dark aria-label="Разомкнуть панели"').classes`, `ui.button('Скопировать', icon='east', on_click=self.prepare_copy).props`, `ui.button('Сменить стороны', icon='swap_horiz', on_click=lambda: self.ws.panes[1 - preview_index].set_mode('preview')).props`, `ui.button('Стоп', icon='pause', on_click=self.stop).props`, `ui.button('Стоп', icon='pause', on_click=self.stop_copy).props`, `ui.button('Файлы', icon='fact_check', on_click=lambda: self.start('files')).props`, `ui.button(icon='more_horiz').props`, `ui.icon`, `ui.icon('east' if preview_index == 1 else 'west', size='19px').classes`, `ui.icon('east' if preview_index == 1 else 'west', size='19px').classes('pair-connection preview-connection').props`, `ui.icon('link', size='19px').classes`, `ui.icon('link', size='19px').classes('pair-connection').props`, `ui.label`, `ui.label('Копируем →').classes`, `ui.label('Превью\nсправа' if preview_index == 1 else 'Превью\nслева').classes`, `ui.label('Превью\nсправа' if preview_index == 1 else 'Превью\nслева').classes('pair-rail-state').style`, `ui.label('Прежняя\nпривязка').classes`, `ui.label('Прежняя\nпривязка').classes('pair-rail-state').style`, `ui.label(f"{self.report['checked_files']}/{total}").classes`, `ui.label(phase + '\n' + state).classes`, `ui.label(phase + '\n' + state).classes('pair-rail-state').style`, `ui.label(str(operation['copied_files']) + '/' + str(operation['total_files'])).classes`, `ui.label(str(self.report['indexed_directories']) + '\nпапок').classes`, `ui.label(str(self.report['indexed_directories']) + '\nпапок').classes('pair-rail-state').style`, `ui.linear_progress`, `ui.linear_progress(value=min(1, fraction)).props`, `ui.linear_progress(value=min(1, fraction)).props('color=green-8').classes`, `ui.linear_progress(value=progress).props`, `ui.linear_progress(value=progress).props('color=green-8' + ('' if total else ' indeterminate')).classes`, `ui.menu`, `ui.menu_item`, `ui.separator`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.render_tree"></a>

## `PairedWorkspace.render_tree`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.render_tree`

Создаёт или обновляет виртуализированное дерево одной стороны пары. Использует PairedTree, existing.set_rows, pane.tree.classes, pane.tree.clear, self.configure_view.

```python
def render_tree(self, pane)
```

Прямые выражения вызова: `PairedTree`, `existing.set_rows`, `pane.tree.classes`, `pane.tree.clear`, [self.configure_view](paired_workspace_ui.md#symbol-PairedWorkspace.configure_view), `self.views.get`, [self.visible_rows](paired_workspace_ui.md#symbol-PairedWorkspace.visible_rows).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.report_title"></a>

## `PairedWorkspace.report_title`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.report_title`

Формирует название сверки по режиму и методу проверки файлов. Использует report.get.

```python
def report_title(report)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `report.get`.

Выражения возврата (ветви, без исполнения):

- `'Папки'`
- `'Файлы · ' + ('имя и размер' if report.get('method') == 'size' else 'SHA-256')`


<a id="symbol-PairedWorkspace.restore_view"></a>

## `PairedWorkspace.restore_view`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.restore_view`

Восстанавливает корень, раскрытие и фильтры связанного дерева из снимка вкладки. Обновляет состояние объекта: closed, differences_only, pending_view, root, root_files_open, selected, show_hidden.

```python
def restore_view(self, state)
```

Присваивания полям `self`: `closed`, `differences_only`, `pending_view`, `root`, `root_files_open`, `selected`, `show_hidden`.

Прямые выражения вызова: `pane.hidden.set_value`, [self.choose](paired_workspace_ui.md#symbol-PairedWorkspace.choose), [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw), `set`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.resume"></a>

## `PairedWorkspace.resume`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.resume`

Продолжает приостановленную парную сверку через API Core. Обрабатывает ошибки: Exception.

```python
async def resume(self)
```

Прямые выражения вызова: [self.apply](paired_workspace_ui.md#symbol-PairedWorkspace.apply), `self.ws.notice`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.set_hidden"></a>

## `PairedWorkspace.set_hidden`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.set_hidden`

Согласует показ скрытых элементов в двух связанных панелях. Обновляет состояние объекта: show_hidden.

```python
def set_hidden(self, value)
```

Присваивания полям `self`: `show_hidden`.

Прямые выражения вызова: `pane.hidden.set_value`, [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.start"></a>

## `PairedWorkspace.start`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.start`

Создаёт новую парную сверку заданного режима и метода через Core. Обновляет состояние объекта: pending_start.

```python
async def start(self, mode, method='size')
```

Присваивания полям `self`: `pending_start`.

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`, `dict`, [self.apply](paired_workspace_ui.md#symbol-PairedWorkspace.apply), `self.ws.notice`, `self.ws.persist_workspace`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.stop"></a>

## `PairedWorkspace.stop`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.stop`

Запрашивает паузу активной парной сверки. Обновляет состояние объекта: rail_signature, report.

```python
async def stop(self)
```

Присваивания полям `self`: `rail_signature`, `report`.

Прямые выражения вызова: [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), `self.ws.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.stop_copy"></a>

## `PairedWorkspace.stop_copy`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.stop_copy`

Запрашивает остановку активного копирования отсутствующих элементов. Обновляет состояние объекта: copy_operation, rail_signature.

```python
async def stop_copy(self)
```

Присваивания полям `self`: `copy_operation`, `rail_signature`.

Прямые выражения вызова: [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), `self.ws.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.toggle_differences"></a>

## `PairedWorkspace.toggle_differences`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.toggle_differences`

Переключает фильтр различий и обновляет набор загружаемых строк. Обновляет состояние объекта: differences_only, rail_signature, root.

```python
def toggle_differences(self)
```

Присваивания полям `self`: `differences_only`, `rail_signature`, `root`.

Прямые выражения вызова: [self.choose](paired_workspace_ui.md#symbol-PairedWorkspace.choose), [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw), [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.toggle_root_files"></a>

## `PairedWorkspace.toggle_root_files`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.toggle_root_files`

Переключает показ файлов непосредственно в текущем корне пары. Обновляет состояние объекта: root_files_open.

```python
def toggle_root_files(self)
```

Присваивания полям `self`: `root_files_open`.

Прямые выражения вызова: [self.redraw](paired_workspace_ui.md#symbol-PairedWorkspace.redraw).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.unlink"></a>

## `PairedWorkspace.unlink`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.unlink`

Размыкает панели и восстанавливает независимый просмотр после остановки работы. Обновляет состояние объекта: active, by_path, copy_operation, generation, history_only, pending_start, pending_view, rail_signature, report, rows, saved.

```python
async def unlink(self)
```

Присваивания полям `self`: `active`, `by_path`, `copy_operation`, `generation`, `history_only`, `pending_start`, `pending_view`, `rail_signature`, `report`, `rows`, `saved`.

Прямые выражения вызова: `pane.restore_browse_state`, `pane.tree.classes`, [self.render_rail](paired_workspace_ui.md#symbol-PairedWorkspace.render_rail), [self.stop](paired_workspace_ui.md#symbol-PairedWorkspace.stop), [self.stop_copy](paired_workspace_ui.md#symbol-PairedWorkspace.stop_copy), `self.views.clear`, `self.ws.set_active`, `self.ws.update_scopes`, `zip`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PairedWorkspace.update_header"></a>

## `PairedWorkspace.update_header`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.update_header`

Обновляет путь и границы связанной стороны панели. Использует pane.location.set_visibility, pane.navigation.set_visibility, pane.render_path, pane.result_filter.set_visibility, pane.toolbar.set_visibility.

```python
def update_header(self, pane)
```

Прямые выражения вызова: `bool`, `pane.location.set_visibility`, `pane.navigation.set_visibility`, `pane.render_path`, `pane.result_filter.set_visibility`, `pane.toolbar.set_visibility`, `pane.volume_select.set_enabled`, `pane.volume_select.set_visibility`, `row.get`, `self.by_path.get`, [self.report_title](paired_workspace_ui.md#symbol-PairedWorkspace.report_title), `self.ws.capacity_text`, `self.ws.format_date`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedWorkspace.visible_rows"></a>

## `PairedWorkspace.visible_rows`

[paired_workspace_ui.py](../../paired_workspace_ui.py) · `PairedWorkspace.visible_rows`

Отбирает строки с учётом корня, раскрытия, скрытых файлов и различий. Использует PurePosixPath, any, include.add, part.startswith, path.startswith.

```python
def visible_rows(self)
```

Прямые выражения вызова: `PurePosixPath`, `any`, `dict`, `include.add`, `len`, `part.startswith`, `path.startswith`, `result.append`, `str`.

Выражения возврата (ветви, без исполнения):

- `result`
