# UI связанных пар: `paired_workspace_ui.py`

Координирует связанные панели: общий корень, раскрытие и выбор, опрос отчёта, диалоги плана копирования, результаты и история. Отображение больших списков передаёт Vue-компоненту.

[Исходный модуль](../../paired_workspace_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [paired_tree.py](paired_tree.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_number_release.py](../../tests/test_copy_number_release.py#L16), [tests/test_paired_workspace.py](../../tests/test_paired_workspace.py#L8), [tests/test_tree_keyboard.py](../../tests/test_tree_keyboard.py#L11), [tests/test_workspace_state.py](../../tests/test_workspace_state.py#L5).

## Оглавление определений

- [PairedWorkspace](#symbol-pairedworkspace) — Управляет связанными панелями, отчётом пары и подтверждением копирования.
- [PairedWorkspace.__init__](#symbol-pairedworkspace---init--) — Инициализирует PairedWorkspace и его рабочее состояние.
- [PairedWorkspace.copy_running](#symbol-pairedworkspace-copy-running) — Проверяет активность текущей операции копирования по её состоянию.
- [PairedWorkspace.report_title](#symbol-pairedworkspace-report-title) — Формирует название сверки по режиму и методу проверки файлов.
- [PairedWorkspace.build](#symbol-pairedworkspace-build) — Создаёт центральную панель управления связанной парой.
- [PairedWorkspace.render_rail](#symbol-pairedworkspace-render-rail) — Обновляет команды, прогресс и состояние центральной панели пары.
- [PairedWorkspace.link](#symbol-pairedworkspace-link) — Связывает выбранный источник с копией, сохраняя прежнее состояние панелей.
- [PairedWorkspace.unlink](#symbol-pairedworkspace-unlink) — Размыкает панели и восстанавливает независимый просмотр после остановки работы.
- [PairedWorkspace.update_header](#symbol-pairedworkspace-update-header) — Обновляет путь и границы связанной стороны панели.
- [PairedWorkspace.relative](#symbol-pairedworkspace-relative) — Преобразует путь тома в путь относительно выбранной стороны пары.
- [PairedWorkspace.navigate_path](#symbol-pairedworkspace-navigate-path) — Переходит к относительному пути внутри допустимой области пары.
- [PairedWorkspace.visible_rows](#symbol-pairedworkspace-visible-rows) — Отбирает строки с учётом корня, раскрытия, скрытых файлов и различий.
- [PairedWorkspace.configure_view](#symbol-pairedworkspace-configure-view) — Передаёт компоненту строки, выбор и дополнительные свойства связанного дерева.
- [PairedWorkspace.render_tree](#symbol-pairedworkspace-render-tree) — Создаёт или обновляет виртуализированное дерево одной стороны пары.
- [PairedWorkspace.redraw](#symbol-pairedworkspace-redraw) — Обновляет оба связанных дерева и центральное управление.
- [PairedWorkspace.choose](#symbol-pairedworkspace-choose) — Выбирает общий относительный путь в обеих сторонах пары.
- [PairedWorkspace.navigate](#symbol-pairedworkspace-navigate) — Делает относительную папку общим корнем связанных деревьев.
- [PairedWorkspace.on_select](#symbol-pairedworkspace-on-select) — Обрабатывает выбор строки виртуального дерева и обновляет превью.
- [PairedWorkspace.on_open](#symbol-pairedworkspace-on-open) — Обрабатывает открытие папки или файла в связанном дереве.
- [PairedWorkspace.on_toggle](#symbol-pairedworkspace-on-toggle) — Меняет раскрытие папки сразу для двух сторон пары.
- [PairedWorkspace.collapse_all](#symbol-pairedworkspace-collapse-all) — Сворачивает или раскрывает каталоги связанного отчёта.
- [PairedWorkspace.toggle_root_files](#symbol-pairedworkspace-toggle-root-files) — Переключает показ файлов непосредственно в текущем корне пары.
- [PairedWorkspace.toggle_differences](#symbol-pairedworkspace-toggle-differences) — Переключает фильтр различий и обновляет набор загружаемых строк.
- [PairedWorkspace.set_hidden](#symbol-pairedworkspace-set-hidden) — Согласует показ скрытых элементов в двух связанных панелях.
- [PairedWorkspace.start](#symbol-pairedworkspace-start) — Создаёт новую парную сверку заданного режима и метода через Core.
- [PairedWorkspace.apply](#symbol-pairedworkspace-apply) — Применяет отчёт пары, сохраняя подходящее состояние раскрытия и выбора.
- [PairedWorkspace.restore_view](#symbol-pairedworkspace-restore-view) — Восстанавливает корень, раскрытие и фильтры связанного дерева из снимка вкладки.
- [PairedWorkspace.load_rows](#symbol-pairedworkspace-load-rows) — Загружает страницы выровненных строк с проверкой актуальности выбранного задания.
- [PairedWorkspace.poll](#symbol-pairedworkspace-poll) — Обновляет состояние парной сверки и операции копирования через API.
- [PairedWorkspace.apply_copy_operation](#symbol-pairedworkspace-apply-copy-operation) — Применяет прогресс операции и при необходимости открывает итоговую сверку.
- [PairedWorkspace.stop_copy](#symbol-pairedworkspace-stop-copy) — Запрашивает остановку активного копирования отсутствующих элементов.
- [PairedWorkspace.copy_paths](#symbol-pairedworkspace-copy-paths) — Формирует подписи исходной и целевой папок сохранённого плана.
- [PairedWorkspace.copy_item_list](#symbol-pairedworkspace-copy-item-list) — Показывает весь зафиксированный план копирования постранично.
- [PairedWorkspace.copy_item_list.append](#symbol-pairedworkspace-copy-item-list-append) — Добавляет страницу элементов и результатов плана в открытый диалог.
- [PairedWorkspace.copy_item_list.load_more](#symbol-pairedworkspace-copy-item-list-load-more) — Запрашивает следующую страницу элементов плана копирования.
- [PairedWorkspace.prepare_copy](#symbol-pairedworkspace-prepare-copy) — Создаёт план, показывает его пользователю и запускает после подтверждения.
- [PairedWorkspace.copy_details](#symbol-pairedworkspace-copy-details) — Показывает прогресс, состав и результаты операции копирования.
- [PairedWorkspace.stop](#symbol-pairedworkspace-stop) — Запрашивает паузу активной парной сверки.
- [PairedWorkspace.resume](#symbol-pairedworkspace-resume) — Продолжает приостановленную парную сверку через API Core.
- [PairedWorkspace.details](#symbol-pairedworkspace-details) — Показывает итоги парной сверки, счётчики и выбранные области.
- [PairedWorkspace.on_menu_state](#symbol-pairedworkspace-on-menu-state) — Учитывает открытое контекстное меню при периодических обновлениях дерева.
- [PairedWorkspace.on_context](#symbol-pairedworkspace-on-context) — Распределяет команды контекстного меню между свойствами, Finder и решениями.
- [PairedWorkspace.decide](#symbol-pairedworkspace-decide) — Открывает выбор планового решения для элемента только в копии.
- [PairedWorkspace.history](#symbol-pairedworkspace-history) — Показывает историю выбранной связи и открывает сохранённый отчёт пары.
- [PairedWorkspace.history.choose](#symbol-pairedworkspace-history-choose) — Открывает выбранный отчёт истории пары после проверки отсутствия активного копирования.
- [PairedWorkspace.history.legacy](#symbol-pairedworkspace-history-legacy) — Закрывает историю пары и открывает действующий диалог прежних отчётов по именам.

<a id="symbol-pairedworkspace"></a>

## `PairedWorkspace`

[paired_workspace_ui.py:61](../../paired_workspace_ui.py#L61)

Управляет связанными панелями, отчётом пары и подтверждением копирования. Зависимости конструктора: workspace.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `active`, `by_path`, `closed`, `copy_dialog_open`, `copy_id`, `copy_operation`, `differences_only`, `generation`, `history_only`, `loaded_job`, `pending_start`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `saved`, `saved_active`, `scopes`, `selected`, `show_hidden`, `structure_at`, `views`, `ws`.

Именованные методы: `__init__`, `copy_running`, `report_title`, `build`, `render_rail`, `link`, `unlink`, `update_header`, `relative`, `navigate_path`, `visible_rows`, `configure_view`, `render_tree`, `redraw`, `choose`, `navigate`, `on_select`, `on_open`, `on_toggle`, `collapse_all`, `toggle_root_files`, `toggle_differences`, `set_hidden`, `start`, `apply`, `restore_view`, `load_rows`, `poll`, `apply_copy_operation`, `stop_copy`, `copy_paths`, `copy_item_list`, `prepare_copy`, `copy_details`, `stop`, `resume`, `details`, `on_menu_state`, `on_context`, `decide`, `history`.

<a id="symbol-pairedworkspace---init--"></a>

## `PairedWorkspace.__init__`

[paired_workspace_ui.py:64](../../paired_workspace_ui.py#L64)

Инициализирует PairedWorkspace и его рабочее состояние. Обновляет состояние объекта: active, by_path, closed, copy_dialog_open, copy_id, copy_operation, differences_only, generation, history_only, loaded_job и ещё 15.

```python
def __init__(self, workspace)
```

Присваивания полям `self`: `active`, `by_path`, `closed`, `copy_dialog_open`, `copy_id`, `copy_operation`, `differences_only`, `generation`, `history_only`, `loaded_job`, `pending_start`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `saved`, `saved_active`, `scopes`, `selected`, `show_hidden`, `structure_at`, `views`, `ws`.

Прямые выражения вызова: `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-copy-running"></a>

## `PairedWorkspace.copy_running`

[paired_workspace_ui.py:94](../../paired_workspace_ui.py#L94)

Проверяет активность текущей операции копирования по её состоянию. Возвращает локальное значение без обращения к файловой системе.

```python
def copy_running(self)
```

Декораторы: `property`.

Прямые выражения вызова: `bool`.

Выражения возврата (ветви, без исполнения):

- `bool(self.copy_operation and self.copy_operation['state'] in ('running', 'stopping'))`


<a id="symbol-pairedworkspace-report-title"></a>

## `PairedWorkspace.report_title`

[paired_workspace_ui.py:100](../../paired_workspace_ui.py#L100)

Формирует название сверки по режиму и методу проверки файлов. Использует report.get.

```python
def report_title(report)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `report.get`.

Выражения возврата (ветви, без исполнения):

- `'Папки'`
- `'Файлы · ' + ('имя и размер' if report.get('method') == 'size' else 'SHA-256')`


<a id="symbol-pairedworkspace-build"></a>

## `PairedWorkspace.build`

[paired_workspace_ui.py:107](../../paired_workspace_ui.py#L107)

Создаёт центральную панель управления связанной парой. Обновляет состояние объекта: rail.

```python
def build(self)
```

Присваивания полям `self`: `rail`.

Прямые выражения вызова: [self.render_rail](../../paired_workspace_ui.py#L115), `ui.add_css`, `ui.column`, `ui.column().classes`, `ui.timer`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-render-rail"></a>

## `PairedWorkspace.render_rail`

[paired_workspace_ui.py:115](../../paired_workspace_ui.py#L115)

Обновляет команды, прогресс и состояние центральной панели пары. Обновляет состояние объекта: rail_signature.

```python
def render_rail(self)
```

Присваивания полям `self`: `rail_signature`.

Прямые выражения вызова: `(self.copy_operation or {}).get`, `(self.report or {}).get`, `bool`, `button.set_enabled`, `copy.set_enabled`, `files.set_enabled`, `folders.set_enabled`, `hasattr`, `max`, `min`, `next`, `self.rail.clear`, `self.rail.set_visibility`, `self.report.get`, `self.report.get('counts', {}).get`, `self.ws.trees.classes`, `stop.set_enabled`, `str`, `tuple`, `ui.button`, `ui.button('Далее', icon='play_arrow', on_click=self.resume).props`, `ui.button('Два дерева', icon='account_tree', on_click=lambda : preview.set_mode('tree')).props`, `ui.button('Закрыть', icon='link_off', on_click=self.unlink).props`, `ui.button('История', icon='history', on_click=self.history).props`, `ui.button('Итоги', icon='format_list_bulleted', on_click=self.details).props`, `ui.button('Копия', icon='assignment', on_click=self.copy_details).props`, `ui.button('Отчёт', icon='history', on_click=self.ws.legacy_dialog.open).props`, `ui.button('Папки', icon='folder', on_click=lambda : self.start('folders')).props`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.unlink).props`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.unlink).props('flat no-caps color=grey-7 aria-label="Разомкнуть панели"').classes`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.ws.browse).props`, `ui.button('Разомкнуть панели', icon='link_off', on_click=self.ws.browse).props('flat no-caps color=dark aria-label="Разомкнуть панели"').classes`, `ui.button('Скопировать', icon='east', on_click=self.prepare_copy).props`, `ui.button('Сменить стороны', icon='swap_horiz', on_click=lambda : self.ws.panes[1 - preview_index].set_mode('preview')).props`, `ui.button('Стоп', icon='pause', on_click=self.stop).props`, `ui.button('Стоп', icon='pause', on_click=self.stop_copy).props`, `ui.button('Файлы', icon='fact_check', on_click=lambda : self.start('files')).props`, `ui.button(icon='more_horiz').props`, `ui.icon`, `ui.icon('east' if preview_index == 1 else 'west', size='19px').classes`, `ui.icon('east' if preview_index == 1 else 'west', size='19px').classes('pair-connection preview-connection').props`, `ui.icon('link', size='19px').classes`, `ui.icon('link', size='19px').classes('pair-connection').props`, `ui.label`, `ui.label('Копируем →').classes`, `ui.label('Превью\nсправа' if preview_index == 1 else 'Превью\nслева').classes`, `ui.label('Превью\nсправа' if preview_index == 1 else 'Превью\nслева').classes('pair-rail-state').style`, `ui.label('Прежняя\nпривязка').classes`, `ui.label('Прежняя\nпривязка').classes('pair-rail-state').style`, `ui.label(f"{self.report['checked_files']}/{total}").classes`, `ui.label(phase + '\n' + state).classes`, `ui.label(phase + '\n' + state).classes('pair-rail-state').style`, `ui.label(str(operation['copied_files']) + '/' + str(operation['total_files'])).classes`, `ui.label(str(self.report['indexed_directories']) + '\nпапок').classes`, `ui.label(str(self.report['indexed_directories']) + '\nпапок').classes('pair-rail-state').style`, `ui.linear_progress`, `ui.linear_progress(value=min(1, fraction)).props`, `ui.linear_progress(value=min(1, fraction)).props('color=green-8').classes`, `ui.linear_progress(value=progress).props`, `ui.linear_progress(value=progress).props('color=green-8' + ('' if total else ' indeterminate')).classes`, `ui.menu`, `ui.menu_item`, `ui.separator`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-link"></a>

## `PairedWorkspace.link`

[paired_workspace_ui.py:211](../../paired_workspace_ui.py#L211)

Связывает выбранный источник с копией, сохраняя прежнее состояние панелей. Обновляет состояние объекта: active, by_path, copy_id, copy_operation, differences_only, generation, history_only, loaded_job, pending_start, pending_view и ещё 10.

```python
async def link(self, group, location, *, load_folders=True)
```

Присваивания полям `self`: `active`, `by_path`, `copy_id`, `copy_operation`, `differences_only`, `generation`, `history_only`, `loaded_job`, `pending_start`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `saved`, `saved_active`, `scopes`, `selected`, `show_hidden`.

Прямые выражения вызова: `ValueError`, `any`, `asyncio.gather`, `bool`, `location.get`, `next`, `p.save_browse_state`, `p.show_volume`, `self.closed.clear`, [self.render_rail](../../paired_workspace_ui.py#L115), `self.scopes.values`, [self.stop](../../paired_workspace_ui.py#L779), [self.stop_copy](../../paired_workspace_ui.py#L661), `self.views.clear`, `self.ws.browse`, `self.ws.notice`, `self.ws.set_active`, `self.ws.update_scopes`, `source.get`, `zip`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-unlink"></a>

## `PairedWorkspace.unlink`

[paired_workspace_ui.py:252](../../paired_workspace_ui.py#L252)

Размыкает панели и восстанавливает независимый просмотр после остановки работы. Обновляет состояние объекта: active, by_path, copy_operation, generation, history_only, pending_start, pending_view, rail_signature, report, rows, saved.

```python
async def unlink(self)
```

Присваивания полям `self`: `active`, `by_path`, `copy_operation`, `generation`, `history_only`, `pending_start`, `pending_view`, `rail_signature`, `report`, `rows`, `saved`.

Прямые выражения вызова: `pane.restore_browse_state`, `pane.tree.classes`, [self.render_rail](../../paired_workspace_ui.py#L115), [self.stop](../../paired_workspace_ui.py#L779), [self.stop_copy](../../paired_workspace_ui.py#L661), `self.views.clear`, `self.ws.set_active`, `self.ws.update_scopes`, `zip`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-update-header"></a>

## `PairedWorkspace.update_header`

[paired_workspace_ui.py:278](../../paired_workspace_ui.py#L278)

Обновляет путь и границы связанной стороны панели. Использует pane.location.set_visibility, pane.navigation.set_visibility, pane.render_path, pane.result_filter.set_visibility, pane.toolbar.set_visibility.

```python
def update_header(self, pane)
```

Прямые выражения вызова: `bool`, `pane.location.set_visibility`, `pane.navigation.set_visibility`, `pane.render_path`, `pane.result_filter.set_visibility`, `pane.toolbar.set_visibility`, `pane.volume_select.set_enabled`, `pane.volume_select.set_visibility`, `row.get`, `self.by_path.get`, [self.report_title](../../paired_workspace_ui.py#L100), `self.ws.capacity_text`, `self.ws.format_date`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-relative"></a>

## `PairedWorkspace.relative`

[paired_workspace_ui.py:307](../../paired_workspace_ui.py#L307)

Преобразует путь тома в путь относительно выбранной стороны пары. Использует path.startswith.

```python
def relative(self, index, path)
```

Прямые выражения вызова: `len`, `path.startswith`.

Выражения возврата (ветви, без исполнения):

- `''`
- `path[len(prefix):] if path.startswith(prefix) else None`


<a id="symbol-pairedworkspace-navigate-path"></a>

## `PairedWorkspace.navigate_path`

[paired_workspace_ui.py:316](../../paired_workspace_ui.py#L316)

Переходит к относительному пути внутри допустимой области пары. Обновляет состояние объекта: root, selected.

```python
async def navigate_path(self, index, path)
```

Присваивания полям `self`: `root`, `selected`.

Прямые выражения вызова: `absolute_scope_path`, `asyncio.gather`, `p.show_volume`, [self.navigate](../../paired_workspace_ui.py#L421), [self.relative](../../paired_workspace_ui.py#L307), `self.scopes.values`, `self.ws.open_volume`, `zip`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-visible-rows"></a>

## `PairedWorkspace.visible_rows`

[paired_workspace_ui.py:332](../../paired_workspace_ui.py#L332)

Отбирает строки с учётом корня, раскрытия, скрытых файлов и различий. Использует PurePosixPath, any, include.add, part.startswith, path.startswith.

```python
def visible_rows(self)
```

Прямые выражения вызова: `PurePosixPath`, `any`, `dict`, `include.add`, `len`, `part.startswith`, `path.startswith`, `result.append`, `str`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-pairedworkspace-configure-view"></a>

## `PairedWorkspace.configure_view`

[paired_workspace_ui.py:365](../../paired_workspace_ui.py#L365)

Передаёт компоненту строки, выбор и дополнительные свойства связанного дерева. Использует PurePosixPath, any, p.startswith, self.report.get, self.ws.size_texts.

```python
def configure_view(self, view)
```

Прямые выражения вызова: `PurePosixPath`, `any`, `p.startswith`, `self.report.get`, `self.ws.size_texts`, `str`, `sum`, `view.props.update`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-render-tree"></a>

## `PairedWorkspace.render_tree`

[paired_workspace_ui.py:379](../../paired_workspace_ui.py#L379)

Создаёт или обновляет виртуализированное дерево одной стороны пары. Использует PairedTree, existing.set_rows, pane.tree.classes, pane.tree.clear, self.configure_view.

```python
def render_tree(self, pane)
```

Прямые выражения вызова: `PairedTree`, `existing.set_rows`, `pane.tree.classes`, `pane.tree.clear`, [self.configure_view](../../paired_workspace_ui.py#L365), `self.views.get`, [self.visible_rows](../../paired_workspace_ui.py#L332).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-redraw"></a>

## `PairedWorkspace.redraw`

[paired_workspace_ui.py:394](../../paired_workspace_ui.py#L394)

Обновляет оба связанных дерева и центральное управление. Использует pane.update_header, self.configure_view, self.render_tree, self.views[side].run_method, self.views[side].set_rows.

```python
def redraw(self, rows_changed=True)
```

Прямые выражения вызова: `pane.update_header`, [self.configure_view](../../paired_workspace_ui.py#L365), [self.render_tree](../../paired_workspace_ui.py#L379), `self.views[side].run_method`, `self.views[side].set_rows`, [self.visible_rows](../../paired_workspace_ui.py#L332), `self.ws.update_scopes`, `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-choose"></a>

## `PairedWorkspace.choose`

[paired_workspace_ui.py:410](../../paired_workspace_ui.py#L410)

Выбирает общий относительный путь в обеих сторонах пары. Обновляет состояние объекта: selected.

```python
def choose(self, relative)
```

Присваивания полям `self`: `selected`.

Прямые выражения вызова: `(data or row or {}).get`, `absolute_scope_path`, `dict`, `row.get`, `self.by_path.get`, `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-navigate"></a>

## `PairedWorkspace.navigate`

[paired_workspace_ui.py:421](../../paired_workspace_ui.py#L421)

Делает относительную папку общим корнем связанных деревьев. Обновляет состояние объекта: root, root_files_open.

```python
def navigate(self, relative)
```

Присваивания полям `self`: `root`, `root_files_open`.

Прямые выражения вызова: [self.choose](../../paired_workspace_ui.py#L410), `self.closed.discard`, [self.redraw](../../paired_workspace_ui.py#L394), `self.views.values`, `view.run_method`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-on-select"></a>

## `PairedWorkspace.on_select`

[paired_workspace_ui.py:432](../../paired_workspace_ui.py#L432)

Обрабатывает выбор строки виртуального дерева и обновляет превью. Асинхронно ожидает: self.ws.preview_selection.

```python
async def on_select(self, event)
```

Прямые выражения вызова: `event.args.get`, [self.choose](../../paired_workspace_ui.py#L410), `self.closed.discard`, [self.redraw](../../paired_workspace_ui.py#L394), `self.ws.preview_selection`, `self.ws.set_active`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-on-open"></a>

## `PairedWorkspace.on_open`

[paired_workspace_ui.py:446](../../paired_workspace_ui.py#L446)

Обрабатывает открытие папки или файла в связанном дереве. Асинхронно ожидает: self.ws.preview_selection.

```python
async def on_open(self, event)
```

Прямые выражения вызова: `self.by_path.get`, [self.navigate](../../paired_workspace_ui.py#L421), `self.ws.preview_selection`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-on-toggle"></a>

## `PairedWorkspace.on_toggle`

[paired_workspace_ui.py:455](../../paired_workspace_ui.py#L455)

Меняет раскрытие папки сразу для двух сторон пары. Использует self.closed.add, self.closed.remove, self.redraw.

```python
async def on_toggle(self, event)
```

Прямые выражения вызова: `self.closed.add`, `self.closed.remove`, [self.redraw](../../paired_workspace_ui.py#L394).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-collapse-all"></a>

## `PairedWorkspace.collapse_all`

[paired_workspace_ui.py:466](../../paired_workspace_ui.py#L466)

Сворачивает или раскрывает каталоги связанного отчёта. Обновляет состояние объекта: closed, root_files_open.

```python
def collapse_all(self, value)
```

Присваивания полям `self`: `closed`, `root_files_open`.

Прямые выражения вызова: [self.redraw](../../paired_workspace_ui.py#L394), `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-toggle-root-files"></a>

## `PairedWorkspace.toggle_root_files`

[paired_workspace_ui.py:473](../../paired_workspace_ui.py#L473)

Переключает показ файлов непосредственно в текущем корне пары. Обновляет состояние объекта: root_files_open.

```python
def toggle_root_files(self)
```

Присваивания полям `self`: `root_files_open`.

Прямые выражения вызова: [self.redraw](../../paired_workspace_ui.py#L394).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-toggle-differences"></a>

## `PairedWorkspace.toggle_differences`

[paired_workspace_ui.py:479](../../paired_workspace_ui.py#L479)

Переключает фильтр различий и обновляет набор загружаемых строк. Обновляет состояние объекта: differences_only, rail_signature, root.

```python
def toggle_differences(self)
```

Присваивания полям `self`: `differences_only`, `rail_signature`, `root`.

Прямые выражения вызова: [self.choose](../../paired_workspace_ui.py#L410), [self.redraw](../../paired_workspace_ui.py#L394), [self.render_rail](../../paired_workspace_ui.py#L115).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-set-hidden"></a>

## `PairedWorkspace.set_hidden`

[paired_workspace_ui.py:489](../../paired_workspace_ui.py#L489)

Согласует показ скрытых элементов в двух связанных панелях. Обновляет состояние объекта: show_hidden.

```python
def set_hidden(self, value)
```

Присваивания полям `self`: `show_hidden`.

Прямые выражения вызова: `pane.hidden.set_value`, [self.redraw](../../paired_workspace_ui.py#L394).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-start"></a>

## `PairedWorkspace.start`

[paired_workspace_ui.py:500](../../paired_workspace_ui.py#L500)

Создаёт новую парную сверку заданного режима и метода через Core. Обновляет состояние объекта: pending_start.

```python
async def start(self, mode, method='size')
```

Присваивания полям `self`: `pending_start`.

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`, `dict`, [self.apply](../../paired_workspace_ui.py#L524), `self.ws.notice`, `self.ws.persist_workspace`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-apply"></a>

## `PairedWorkspace.apply`

[paired_workspace_ui.py:524](../../paired_workspace_ui.py#L524)

Применяет отчёт пары, сохраняя подходящее состояние раскрытия и выбора. Обновляет состояние объекта: by_path, closed, copy_operation, differences_only, pending_view, rail_signature, report, root, root_files_open, rows, scopes и ещё 2.

```python
async def apply(self, report)
```

Присваивания полям `self`: `by_path`, `closed`, `copy_operation`, `differences_only`, `pending_view`, `rail_signature`, `report`, `root`, `root_files_open`, `rows`, `scopes`, `selected`, `structure_at`.

Прямые выражения вызова: `bool`, `pane.folders.clear`, `pane.render`, `pane.tree.clear`, `pane.volume_select.set_value`, `report.get`, [self.choose](../../paired_workspace_ui.py#L410), [self.load_rows](../../paired_workspace_ui.py#L582), [self.render_rail](../../paired_workspace_ui.py#L115), [self.set_hidden](../../paired_workspace_ui.py#L489), `self.views.clear`, `set`, `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-restore-view"></a>

## `PairedWorkspace.restore_view`

[paired_workspace_ui.py:564](../../paired_workspace_ui.py#L564)

Восстанавливает корень, раскрытие и фильтры связанного дерева из снимка вкладки. Обновляет состояние объекта: closed, differences_only, pending_view, root, root_files_open, selected, show_hidden.

```python
def restore_view(self, state)
```

Присваивания полям `self`: `closed`, `differences_only`, `pending_view`, `root`, `root_files_open`, `selected`, `show_hidden`.

Прямые выражения вызова: `pane.hidden.set_value`, [self.choose](../../paired_workspace_ui.py#L410), [self.redraw](../../paired_workspace_ui.py#L394), `set`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-load-rows"></a>

## `PairedWorkspace.load_rows`

[paired_workspace_ui.py:582](../../paired_workspace_ui.py#L582)

Загружает страницы выровненных строк с проверкой актуальности выбранного задания. Обновляет состояние объекта: by_path, closed, loaded_job, pending_view, rail_signature, root_files_open, rows, structure_at.

```python
async def load_rows(self, job)
```

Присваивания полям `self`: `by_path`, `closed`, `loaded_job`, `pending_view`, `rail_signature`, `root_files_open`, `rows`, `structure_at`.

Прямые выражения вызова: `PurePosixPath`, `r.get`, `range`, `row.get`, `row[side].get`, [self.choose](../../paired_workspace_ui.py#L410), [self.redraw](../../paired_workspace_ui.py#L394), [self.render_rail](../../paired_workspace_ui.py#L115), [self.restore_view](../../paired_workspace_ui.py#L564), `self.ws.format_bytes`, `self.ws.request`, `str`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-poll"></a>

## `PairedWorkspace.poll`

[paired_workspace_ui.py:627](../../paired_workspace_ui.py#L627)

Обновляет состояние парной сверки и операции копирования через API. Обрабатывает ошибки: Exception.

```python
async def poll(self)
```

Прямые выражения вызова: [self.apply](../../paired_workspace_ui.py#L524), [self.apply_copy_operation](../../paired_workspace_ui.py#L650), `self.ws.error_text`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-apply-copy-operation"></a>

## `PairedWorkspace.apply_copy_operation`

[paired_workspace_ui.py:650](../../paired_workspace_ui.py#L650)

Применяет прогресс операции и при необходимости открывает итоговую сверку. Обновляет состояние объекта: copy_operation, rail_signature.

```python
async def apply_copy_operation(self, operation)
```

Присваивания полям `self`: `copy_operation`, `rail_signature`.

Прямые выражения вызова: `operation.get`, [self.apply](../../paired_workspace_ui.py#L524), [self.render_rail](../../paired_workspace_ui.py#L115), `self.ws.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-stop-copy"></a>

## `PairedWorkspace.stop_copy`

[paired_workspace_ui.py:661](../../paired_workspace_ui.py#L661)

Запрашивает остановку активного копирования отсутствующих элементов. Обновляет состояние объекта: copy_operation, rail_signature.

```python
async def stop_copy(self)
```

Присваивания полям `self`: `copy_operation`, `rail_signature`.

Прямые выражения вызова: [self.render_rail](../../paired_workspace_ui.py#L115), `self.ws.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-copy-paths"></a>

## `PairedWorkspace.copy_paths`

[paired_workspace_ui.py:669](../../paired_workspace_ui.py#L669)

Формирует подписи исходной и целевой папок сохранённого плана. Использует ui.label, ui.label(scope['label'] + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes.

```python
def copy_paths(self, operation)
```

Прямые выражения вызова: `ui.label`, `ui.label(scope['label'] + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-copy-item-list"></a>

## `PairedWorkspace.copy_item_list`

[paired_workspace_ui.py:676](../../paired_workspace_ui.py#L676)

Показывает весь зафиксированный план копирования постранично. Асинхронно ожидает: self.ws.request.

```python
async def copy_item_list(self, operation)
```

Прямые выражения вызова: `append`, `more.on_click`, `self.ws.request`, `ui.button`, `ui.button('Показать ещё 200').props`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-copy-item-list-append"></a>

## `PairedWorkspace.copy_item_list.append`

[paired_workspace_ui.py:686](../../paired_workspace_ui.py#L686)

Добавляет страницу элементов и результатов плана в открытый диалог. Использует item.get, more.set_visibility, self.ws.format_bytes, ui.column, ui.column().classes.

```python
def append(data)
```

Прямые выражения вызова: `item.get`, `len`, `more.set_visibility`, `self.ws.format_bytes`, `ui.column`, `ui.column().classes`, `ui.icon`, `ui.icon('folder' if item['kind'] == 'directory' else 'insert_drive_file', size='16px').classes`, `ui.label`, `ui.label('Копия не завершена').classes`, `ui.label(item['message']).classes`, `ui.label(item['path']).classes`, `ui.label(self.ws.format_bytes(item['size'])).classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-copy-item-list-load-more"></a>

## `PairedWorkspace.copy_item_list.load_more`

[paired_workspace_ui.py:706](../../paired_workspace_ui.py#L706)

Запрашивает следующую страницу элементов плана копирования. Обрабатывает ошибки: Exception.

```python
async def load_more()
```

Прямые выражения вызова: [append](../../paired_workspace_ui.py#L686), `more.disable`, `more.enable`, `self.ws.notice`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-prepare-copy"></a>

## `PairedWorkspace.prepare_copy`

[paired_workspace_ui.py:722](../../paired_workspace_ui.py#L722)

Создаёт план, показывает его пользователю и запускает после подтверждения. Обновляет состояние объекта: copy_dialog_open, rail_signature.

```python
async def prepare_copy(self)
```

Присваивания полям `self`: `copy_dialog_open`, `rail_signature`.

Прямые выражения вызова: [self.apply_copy_operation](../../paired_workspace_ui.py#L650), [self.copy_item_list](../../paired_workspace_ui.py#L676), [self.copy_paths](../../paired_workspace_ui.py#L669), [self.render_rail](../../paired_workspace_ui.py#L115), `self.ws.format_bytes`, `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Начать копирование', on_click=lambda : dialog.submit(True)).props`, `ui.button('Отмена', on_click=lambda : dialog.submit(False)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Копируется вся проверенная пара. Существующие файлы и элементы с другим размером останутся на месте.').classes`, `ui.label('Незавершённые копии при прерывании записи будут отмечены для ручного разбора.').classes`, `ui.label('Скопировать отсутствующее →').classes`, `ui.label(f"Файлов: {operation['total_files']} · папок: {operation['total_directories']} · {self.ws.format_bytes(operation['total_bytes'])}").classes`, `ui.row`, `ui.row().classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-copy-details"></a>

## `PairedWorkspace.copy_details`

[paired_workspace_ui.py:756](../../paired_workspace_ui.py#L756)

Показывает прогресс, состав и результаты операции копирования. Обрабатывает ошибки: Exception.

```python
async def copy_details(self)
```

Прямые выражения вызова: `dialog.open`, `operation.get`, [self.copy_item_list](../../paired_workspace_ui.py#L676), [self.copy_paths](../../paired_workspace_ui.py#L669), `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Копирование из ' + self.scopes['left']['label'] + ' →').classes`, `ui.label(f"Готово файлов: {operation['copied_files']} · папок: {operation['copied_directories']} · пропущено: {operation['skipped']} · ошибок: {operation['errors']}").classes`, `ui.label(f"Незавершённых файлов в копии: {operation['incomplete_files']}").classes`, `ui.label(operation['current_path']).classes`, `ui.label(operation['message']).classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-stop"></a>

## `PairedWorkspace.stop`

[paired_workspace_ui.py:779](../../paired_workspace_ui.py#L779)

Запрашивает паузу активной парной сверки. Обновляет состояние объекта: rail_signature, report.

```python
async def stop(self)
```

Присваивания полям `self`: `rail_signature`, `report`.

Прямые выражения вызова: [self.render_rail](../../paired_workspace_ui.py#L115), `self.ws.request`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-resume"></a>

## `PairedWorkspace.resume`

[paired_workspace_ui.py:787](../../paired_workspace_ui.py#L787)

Продолжает приостановленную парную сверку через API Core. Обрабатывает ошибки: Exception.

```python
async def resume(self)
```

Прямые выражения вызова: [self.apply](../../paired_workspace_ui.py#L524), `self.ws.notice`, `self.ws.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-details"></a>

## `PairedWorkspace.details`

[paired_workspace_ui.py:798](../../paired_workspace_ui.py#L798)

Показывает итоги парной сверки, счётчики и выбранные области. Использует dialog.open, report.get, report.get('root_errors', {}).items, report['counts'].items, row.get.

```python
async def details(self)
```

Прямые выражения вызова: `dialog.open`, `report.get`, `report.get('root_errors', {}).items`, `report['counts'].items`, `row.get`, `row[side].get`, [self.report_title](../../paired_workspace_ui.py#L100), `self.ws.format_date`, `str`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.button(row['path'] + (' · ' + DECISIONS[row['decision']] if row['decision'] else ''), on_click=lambda r=row: self.decide(r)).props`, `ui.button(row['path'] + (' · ' + DECISIONS[row['decision']] if row['decision'] else ''), on_click=lambda r=row: self.decide(r)).props('flat dense no-caps color=purple-8').classes`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Итоги · ' + self.report_title(report)).classes`, `ui.label('Только в копии · выбери решение').classes`, `ui.label(explanation).classes`, `ui.label(f"Не удалось прочитать элементов: {report['errors']}").classes`, `ui.label(f"Прочитано каталогов: {report['indexed_directories']}").classes`, `ui.label(report['current_path']).classes`, `ui.label(self.scopes[side]['label'] + ' /' + path + ': ' + error).classes`, `ui.label(self.scopes[side]['label'] + ': ' + error).classes`, `ui.label(self.ws.format_date(report['created_at']) + ' · ' + report['message']).classes`, `ui.label(title + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-on-menu-state"></a>

## `PairedWorkspace.on_menu_state`

[paired_workspace_ui.py:842](../../paired_workspace_ui.py#L842)

Учитывает открытое контекстное меню при периодических обновлениях дерева. Параметры: event.

```python
def on_menu_state(self, event)
```

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-on-context"></a>

## `PairedWorkspace.on_context`

[paired_workspace_ui.py:847](../../paired_workspace_ui.py#L847)

Распределяет команды контекстного меню между свойствами, Finder и решениями. Асинхронно ожидает: self.decide, self.ws.open_in_finder, self.ws.show_properties.

```python
async def on_context(self, event)
```

Прямые выражения вызова: `event.args.get`, `row.get`, `self.by_path.get`, [self.decide](../../paired_workspace_ui.py#L866), `self.ws.open_in_finder`, `self.ws.show_properties`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-pairedworkspace-decide"></a>

## `PairedWorkspace.decide`

[paired_workspace_ui.py:866](../../paired_workspace_ui.py#L866)

Открывает выбор планового решения для элемента только в копии. Обрабатывает ошибки: Exception.

```python
async def decide(self, row)
```

Прямые выражения вызова: `row.get`, [self.load_rows](../../paired_workspace_ui.py#L582), `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Отмена', on_click=lambda : dialog.submit(False)).props`, `ui.button('Сохранить решение', on_click=lambda : dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('От папки ' + row['decision_from'] + ': ' + DECISIONS[row['decision']]).classes`, `ui.label('Сейчас сохраняется решение. Файловые операции будут выполняться отдельно.').classes`, `ui.label('Только в копии').classes`, `ui.label(row['path']).classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select({'': 'Наследовать / снять отдельное решение', **DECISIONS}, value=row.get('own_decision') or '', label='Что сделать').props`, `ui.select({'': 'Наследовать / снять отдельное решение', **DECISIONS}, value=row.get('own_decision') or '', label='Что сделать').props('outlined dense').classes`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-history"></a>

## `PairedWorkspace.history`

[paired_workspace_ui.py:892](../../paired_workspace_ui.py#L892)

Показывает историю выбранной связи и открывает сохранённый отчёт пары. Обрабатывает ошибки: Exception.

```python
async def history(self, *, group=None, location=None)
```

Прямые выражения вызова: `dialog.open`, [self.report_title](../../paired_workspace_ui.py#L100), `self.ws.format_date`, `self.ws.notice`, `self.ws.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.button('Прежние отчёты по именам', on_click=legacy).props`, `ui.button(label, on_click=lambda j=job: choose(j)).props`, `ui.button(label, on_click=lambda j=job: choose(j)).props('flat no-caps color=green-9').classes`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('История сверок пары').classes`, `ui.label('Эта пара ещё не проверялась.').classes`, `ui.label(location['label'] + ' · ' + location['volume_name'] + ' /' + location['path']).classes`, `ui.separator`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-history-choose"></a>

## `PairedWorkspace.history.choose`

[paired_workspace_ui.py:905](../../paired_workspace_ui.py#L905)

Открывает выбранный отчёт истории пары после проверки отсутствия активного копирования. Явно отклоняет недопустимое состояние через ValueError.

```python
async def choose(job)
```

Присваивания полям `self`: `generation`.

Прямые выражения вызова: `ValueError`, `dialog.close`, [self.apply](../../paired_workspace_ui.py#L524), [self.link](../../paired_workspace_ui.py#L211), `self.ws.notice`, `self.ws.persist_workspace`.

Явные `raise`:

- `ValueError('Сначала дождись завершения копирования.')`

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedworkspace-history-legacy"></a>

## `PairedWorkspace.history.legacy`

[paired_workspace_ui.py:924](../../paired_workspace_ui.py#L924)

Закрывает историю пары и открывает действующий диалог прежних отчётов по именам. Использует dialog.close, self.ws.legacy_dialog.open.

```python
def legacy()
```

Прямые выражения вызова: `dialog.close`, `self.ws.legacy_dialog.open`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
