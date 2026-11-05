# Рабочее пространство и панели: `workspace_ui.py`

Главная страница NiceGUI. BrowserPane отвечает за одно дерево, StorageWorkspace — за две панели, состояние вкладки, тома, историю, размеры и координацию остальных компонентов UI.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../workspace_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [comparison_tree_ui.py](comparison_tree_ui.md), [copy_groups_ui.py](copy_groups_ui.md), [media_manager/comparison.py](media_manager--comparison.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md), [network_ui.py](network_ui.md), [paired_workspace_ui.py](paired_workspace_ui.md), [photo_libraries_ui.py](photo_libraries_ui.md), [storage_preview_ui.py](storage_preview_ui.md), [storage_ui.py](storage_ui.md), [workspace_state.py](workspace_state.md).
Импортируется модулями: [storage_ui.py](storage_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_directory_sizes.py](tests.md#module-tests.test_directory_sizes), [tests/test_folder_tags.py](tests.md#module-tests.test_folder_tags), [tests/test_paired_workspace.py](tests.md#module-tests.test_paired_workspace), [tests/test_photo_copy_roles.py](tests.md#module-tests.test_photo_copy_roles), [tests/test_refresh_renamed_folder.py](tests.md#module-tests.test_refresh_renamed_folder), [tests/test_sidebar_state.py](tests.md#module-tests.test_sidebar_state), [tests/test_storage_previews.py](tests.md#module-tests.test_storage_previews), [tests/test_tree_keyboard.py](tests.md#module-tests.test_tree_keyboard), [tests/test_workspace_photos.py](tests.md#module-tests.test_workspace_photos), [tests/test_workspace_refresh.py](tests.md#module-tests.test_workspace_refresh), [tests/test_workspace_state.py](tests.md#module-tests.test_workspace_state).

## Оглавление определений

- [BrowserPane](#symbol-BrowserPane) — Управляет деревом, выбором, навигацией и режимом превью одной панели.
- [BrowserPane.__init__](#symbol-BrowserPane.__init__) — Инициализирует BrowserPane и его рабочее состояние.
- [BrowserPane.activate_heading](#symbol-BrowserPane.activate_heading) — Делает панель активной и возвращает клавиатурный фокус дереву.
- [BrowserPane.change_filter](#symbol-BrowserPane.change_filter) — Меняет фильтр статусов сохранённого дерева и перезагружает результат.
- [BrowserPane.comparison_open](#symbol-BrowserPane.comparison_open) — Проверяет наличие открытого результата общей или парной сверки.
- [BrowserPane.display_volume_id](#symbol-BrowserPane.display_volume_id) — Возвращает ID тома, фактически показанного деревом или превью.
- [BrowserPane.focus_tree](#symbol-BrowserPane.focus_tree) — Назначает DOM-фокус дереву без нежелательной прокрутки страницы.
- [BrowserPane.folder_clicked](#symbol-BrowserPane.folder_clicked) — Различает одиночный и двойной щелчок по папке дерева.
- [BrowserPane.go_parent](#symbol-BrowserPane.go_parent) — Переходит к родительской папке с соблюдением границ сверки и превью.
- [BrowserPane.go_root](#symbol-BrowserPane.go_root) — Переходит к допустимому корню текущего режима панели.
- [BrowserPane.hidden_changed](#symbol-BrowserPane.hidden_changed) — Обновляет отображение скрытых элементов и сохраняет состояние вкладки.
- [BrowserPane.keyboard_selected](#symbol-BrowserPane.keyboard_selected) — Принимает клавиатурный выбор строки и открывает связанное превью.
- [BrowserPane.load_folder](#symbol-BrowserPane.load_folder) — Загружает страницу живого, виртуального или сохранённого дерева через API.
- [BrowserPane.mode_changed](#symbol-BrowserPane.mode_changed) — Передаёт действительное переключение режима панели в set_mode.
- [BrowserPane.more](#symbol-BrowserPane.more) — Загружает следующую страницу дочерних элементов папки.
- [BrowserPane.open_path](#symbol-BrowserPane.open_path) — Открывает путь в обычном, парном или сохранённом дереве панели.
- [BrowserPane.refresh](#symbol-BrowserPane.refresh) — Обновляет открытую область и состояние её списков без потери выбранного режима.
- [BrowserPane.refresh_busy](#symbol-BrowserPane.refresh_busy) — Обновляет индикатор фонового чтения открытой папки.
- [BrowserPane.refresh_open_folder](#symbol-BrowserPane.refresh_open_folder) — Фоново обновляет открытую папку, отбрасывая ответы прежнего поколения панели.
- [BrowserPane.register_navigation](#symbol-BrowserPane.register_navigation) — Регистрирует строку для клавиатурной навигации и выбора элемента.
- [BrowserPane.render](#symbol-BrowserPane.render) — Перестраивает видимые строки независимого дерева и регистрирует навигацию.
- [BrowserPane.render.branch](#symbol-BrowserPane.render.branch) — Рекурсивно рисует раскрытые узлы обычного дерева и регистрирует навигацию строк.
- [BrowserPane.render_path](#symbol-BrowserPane.render_path) — Строит кликабельный путь с учётом границы выбранной области.
- [BrowserPane.restore_browse_state](#symbol-BrowserPane.restore_browse_state) — Восстанавливает дерево после выхода из связанного режима.
- [BrowserPane.save_browse_state](#symbol-BrowserPane.save_browse_state) — Сохраняет локальное состояние независимого дерева перед переходом в связанную пару.
- [BrowserPane.scope](#symbol-BrowserPane.scope) — Возвращает допустимую файловую область панели для операций с папками.
- [BrowserPane.select](#symbol-BrowserPane.select) — Выбирает строку дерева, синхронизирует превью и при необходимости раскрывает папку.
- [BrowserPane.set_mode](#symbol-BrowserPane.set_mode) — Переключает дерево и превью с сохранением положения и согласованием второй панели.
- [BrowserPane.show_volume](#symbol-BrowserPane.show_volume) — Показывает том и сначала загружает снимок, затем обновляет доступную папку.
- [BrowserPane.size_scope](#symbol-BrowserPane.size_scope) — Определяет область для отображаемого логического размера папки.
- [BrowserPane.update_header](#symbol-BrowserPane.update_header) — Обновляет путь, подписи и доступность элементов управления панели.
- [BrowserPane.update_navigation_selection](#symbol-BrowserPane.update_navigation_selection) — Обновляет признак выбранной строки среди зарегистрированных DOM-элементов.
- [BrowserPane.update_size_header](#symbol-BrowserPane.update_size_header) — Обновляет размер текущей области в заголовке панели.
- [BrowserPane.update_volume_select](#symbol-BrowserPane.update_volume_select) — Обновляет варианты выбора тома и текущее значение селектора панели.
- [BrowserPane.volume](#symbol-BrowserPane.volume) — Возвращает сведения о выбранном томе или виртуальной медиатеке.
- [BrowserPane.volume_changed](#symbol-BrowserPane.volume_changed) — Обрабатывает актуальное изменение выбранного тома, отбрасывая устаревшие события.
- [StorageWorkspace](#symbol-StorageWorkspace) — Координирует две панели, тома, медиатеки, сверки и сохранённое состояние вкладки.
- [StorageWorkspace.__init__](#symbol-StorageWorkspace.__init__) — Инициализирует StorageWorkspace и его рабочее состояние.
- [StorageWorkspace.apply_folder_tags](#symbol-StorageWorkspace.apply_folder_tags) — Применяет полученные метки к локальным снимкам и строкам UI.
- [StorageWorkspace.apply_report](#symbol-StorageWorkspace.apply_report) — Показывает общую сверку в панелях и обновляет связанные элементы управления.
- [StorageWorkspace.browse](#symbol-StorageWorkspace.browse) — Закрывает отчёт общей сверки и возвращает независимый просмотр папок.
- [StorageWorkspace.browse_volumes](#symbol-StorageWorkspace.browse_volumes) — Объединяет обычные тома и виртуальные медиатеки для выбора в панелях.
- [StorageWorkspace.build_operations](#symbol-StorageWorkspace.build_operations) — Создаёт управление общей сверкой и диалог её прежнего интерфейса.
- [StorageWorkspace.capacity_text](#symbol-StorageWorkspace.capacity_text) — Форматирует сохранённые сведения о заполнении тома.
- [StorageWorkspace.choose_job](#symbol-StorageWorkspace.choose_job) — Получает сохранённый отчёт по ID и применяет его к рабочему пространству.
- [StorageWorkspace.connect](#symbol-StorageWorkspace.connect) — Открывает подключение сохранённого сетевого тома в Finder на машине Core.
- [StorageWorkspace.control](#symbol-StorageWorkspace.control) — Передаёт команду паузы или продолжения общей сверки в Core.
- [StorageWorkspace.directory_size_text](#symbol-StorageWorkspace.directory_size_text) — Форматирует размер папки с учётом актуальности, ошибки и состояния подсчёта.
- [StorageWorkspace.edit_folder_tags](#symbol-StorageWorkspace.edit_folder_tags) — Открывает редактирование пользовательских меток выбранной папки.
- [StorageWorkspace.edit_metadata](#symbol-StorageWorkspace.edit_metadata) — Редактирует сохранённые назначение, флаги и комментарий расположения.
- [StorageWorkspace.error_text](#symbol-StorageWorkspace.error_text) — Извлекает понятное сообщение из HTTP-ошибки или обычного исключения.
- [StorageWorkspace.history_changed](#symbol-StorageWorkspace.history_changed) — Открывает выбранный пользователем отчёт общей сверки.
- [StorageWorkspace.is_photos](#symbol-StorageWorkspace.is_photos) — Распознаёт ID виртуального тома медиатеки photos-<source_id>.
- [StorageWorkspace.load](#symbol-StorageWorkspace.load) — Инициализирует рабочее пространство и применяет параметры старой ссылки либо снимок вкладки.
- [StorageWorkspace.load_directory_sizes](#symbol-StorageWorkspace.load_directory_sizes) — Получает или ставит в очередь размеры выбранных папок через Core.
- [StorageWorkspace.notice](#symbol-StorageWorkspace.notice) — Показывает пользователю сообщение об ошибке операции UI.
- [StorageWorkspace.open_in_finder](#symbol-StorageWorkspace.open_in_finder) — Отправляет Core проверенную команду открытия файлового пути в Finder.
- [StorageWorkspace.open_library](#symbol-StorageWorkspace.open_library) — Открывает выбранную медиатеку в активной панели.
- [StorageWorkspace.open_photo](#symbol-StorageWorkspace.open_photo) — Передаёт Core команду выделения объекта в системном Photos.
- [StorageWorkspace.open_volume](#symbol-StorageWorkspace.open_volume) — Открывает файловый том в выбранной панели с выходом из конфликтующего режима.
- [StorageWorkspace.persist_workspace](#symbol-StorageWorkspace.persist_workspace) — Сохраняет нормализованное состояние рабочего пространства в хранилище вкладки.
- [StorageWorkspace.poll](#symbol-StorageWorkspace.poll) — Опросом обновляет общую и парную сверки, копии, медиатеки и превью.
- [StorageWorkspace.poll_connected](#symbol-StorageWorkspace.poll_connected) — Вызывает периодический обработчик только для ещё существующего клиента NiceGUI.
- [StorageWorkspace.poll_directory_sizes](#symbol-StorageWorkspace.poll_directory_sizes) — Периодически обновляет видимые размеры и ограничивает повторные запросы.
- [StorageWorkspace.preview_selection](#symbol-StorageWorkspace.preview_selection) — Передаёт выбранный элемент в соседнюю панель с включённым превью.
- [StorageWorkspace.property_menu](#symbol-StorageWorkspace.property_menu) — Создаёт контекстное меню свойств с восстановлением фокуса и состоянием редактирования.
- [StorageWorkspace.property_menu.action](#symbol-StorageWorkspace.property_menu.action) — Оборачивает команду контекстного меню в обработчик закрытия и восстановления фокуса.
- [StorageWorkspace.property_menu.action.invoke](#symbol-StorageWorkspace.property_menu.action.invoke) — Асинхронно вызывает команду меню в сохранённом контексте клиента NiceGUI.
- [StorageWorkspace.property_menu.before_show](#symbol-StorageWorkspace.property_menu.before_show) — Перед открытием меню отмечает его активность и скрывает файловые команды для Photos.
- [StorageWorkspace.read_directory](#symbol-StorageWorkspace.read_directory) — Выбирает API обычного тома или виртуальной медиатеки и получает страницу.
- [StorageWorkspace.refresh_history](#symbol-StorageWorkspace.refresh_history) — Обновляет список последних заданий общей сверки.
- [StorageWorkspace.refresh_matches](#symbol-StorageWorkspace.refresh_matches) — Загружает совпадения выбранного элемента и показывает найденные пути справа.
- [StorageWorkspace.refresh_volumes](#symbol-StorageWorkspace.refresh_volumes) — Обновляет тома и связанные сведения, сохраняя отображение при ошибках API.
- [StorageWorkspace.refresh_volumes.access_state](#symbol-StorageWorkspace.refresh_volumes.access_state) — Выделяет признаки доступности тома для обнаружения изменений без полной перерисовки.
- [StorageWorkspace.register_disk](#symbol-StorageWorkspace.register_disk) — Регистрирует выбранный сменный носитель через подтверждённое действие Core.
- [StorageWorkspace.rename_disk](#symbol-StorageWorkspace.rename_disk) — Открывает переименование зарегистрированного сменного носителя.
- [StorageWorkspace.rename_disk.save](#symbol-StorageWorkspace.rename_disk.save) — Сохраняет новое название носителя и обновляет связанные данные UI.
- [StorageWorkspace.render_progress](#symbol-StorageWorkspace.render_progress) — Обновляет прогресс и доступные команды общей сверки, включая старые отчёты.
- [StorageWorkspace.render_volumes](#symbol-StorageWorkspace.render_volumes) — Перерисовывает активные и архивные тома с группировкой и индикаторами.
- [StorageWorkspace.render_volumes.groups](#symbol-StorageWorkspace.render_volumes.groups) — Распределяет переданные тома по отображаемым группам NAS и локальных носителей.
- [StorageWorkspace.render_volumes.groups.volume_actions](#symbol-StorageWorkspace.render_volumes.groups.volume_actions) — Добавляет доступное переименование подтверждённого сменного носителя в меню тома.
- [StorageWorkspace.report_marker](#symbol-StorageWorkspace.report_marker) — Получает признаки изменения отчёта для подавления лишних перерисовок.
- [StorageWorkspace.resolve_volume](#symbol-StorageWorkspace.resolve_volume) — Находит файловый или виртуальный том по ID рабочего пространства.
- [StorageWorkspace.restore_panes](#symbol-StorageWorkspace.restore_panes) — Восстанавливает выбранные области и режимы двух независимых панелей.
- [StorageWorkspace.restore_workspace](#symbol-StorageWorkspace.restore_workspace) — Восстанавливает вкладку, историю и связанную пару из проверенного снимка состояния.
- [StorageWorkspace.selectable_volumes](#symbol-StorageWorkspace.selectable_volumes) — Формирует варианты селектора томов с отображаемыми названиями.
- [StorageWorkspace.set_active](#symbol-StorageWorkspace.set_active) — Выбирает активную панель и обновляет связанное управление.
- [StorageWorkspace.show_journal](#symbol-StorageWorkspace.show_journal) — Показывает события общей сверки с загрузкой предыдущих записей.
- [StorageWorkspace.show_journal.append](#symbol-StorageWorkspace.show_journal.append) — Добавляет события очередной страницы в диалог журнала общей сверки.
- [StorageWorkspace.show_journal.older](#symbol-StorageWorkspace.show_journal.older) — Загружает более ранние события общей сверки по сохранённому курсору.
- [StorageWorkspace.show_properties](#symbol-StorageWorkspace.show_properties) — Показывает свойства тома, папки или файла и доступные команды.
- [StorageWorkspace.sidebar_expansion](#symbol-StorageWorkspace.sidebar_expansion) — Создаёт секцию боковой панели с восстановлением её раскрытия.
- [StorageWorkspace.sidebar_expansion.changed](#symbol-StorageWorkspace.sidebar_expansion.changed) — Сохраняет актуальное раскрытие секции боковой панели в браузерном хранилище.
- [StorageWorkspace.size_texts](#symbol-StorageWorkspace.size_texts) — Собирает форматированные размеры всех известных папок выбранного тома.
- [StorageWorkspace.start_comparison](#symbol-StorageWorkspace.start_comparison) — Создаёт поиск имён по выбранным областям через API Core.
- [StorageWorkspace.update_scopes](#symbol-StorageWorkspace.update_scopes) — Пересчитывает выбранные области и доступность действий сверки и копирования.
- [StorageWorkspace.update_scopes.scope_label](#symbol-StorageWorkspace.update_scopes.scope_label) — Формирует подпись выбранной области из названия тома и относительного пути.
- [StorageWorkspace.update_size_labels](#symbol-StorageWorkspace.update_size_labels) — Обновляет уже созданные подписи размеров без перестроения деревьев.
- [StorageWorkspace.workspace_snapshot](#symbol-StorageWorkspace.workspace_snapshot) — Собирает компактное состояние навигации двух панелей и открытой сверки.
- [archived](#symbol-archived) — Определяет, должен ли недоступный том отображаться в архиве.
- [folder_membership](#symbol-folder_membership) — Определяет принадлежность пути обычной копии или копии медиатеки.
- [register_workspace_page](#symbol-register_workspace_page) — Регистрирует главную страницу с параметрами совместимости старых ссылок.
- [register_workspace_page.workspace_page](#symbol-register_workspace_page.workspace_page) — Создаёт рабочее пространство для клиента и загружает его начальное состояние.
- [volume_label](#symbol-volume_label) — Формирует подпись тома с необязательным именем сетевого ресурса.

## Константы и значения по умолчанию

<a id="constant-JOB_STATES"></a>

### `JOB_STATES`

`{'running': 'Выполняется', 'pausing': 'Останавливается', 'paused': 'Остановлено', 'completed': 'Завершено', 'failed': 'Ошибка'}`

<a id="constant-STATUS_COLORS"></a>

### `STATUS_COLORS`

`{'names_found': '#39754d', 'other_folder': '#8b743e', 'names_missing': '#b87626', 'unverified': '#ab5751', 'skipped': '#8b8f92', 'found': '#39754d', 'cached': '#657891', 'missing': '#b87626', 'candidate': '#77736c'}`

<a id="constant-STATUS_ICONS"></a>

### `STATUS_ICONS`

`{'names_found': 'check', 'names_missing': 'remove', 'other_folder': 'alt_route', 'unverified': 'help_outline', 'skipped': 'block', 'found': 'check', 'cached': 'history', 'missing': 'remove', 'candidate': 'search'}`

<a id="constant-TREE_FOCUS_JS"></a>

### `TREE_FOCUS_JS`

`'event => {\n    if (event.target.closest(\'.pair-virtual, input, textarea, select, [contenteditable="true"], [role="combobox"], [role="menu"]\')) return;\n    const tree = event.currentTarget;\n    const row = event.target.closest(\'[data-tree-key]\');\n    if (row) tree.dataset.keyboardKey = row.dataset.treeKey;\n    tree.dataset.keyboardRevision = tree.dataset.navigationRevision;\n    tree.focus({preventScroll:true});\n}'`

<a id="constant-TREE_KEY_JS"></a>

### `TREE_KEY_JS`

`Объёмное значение см. в исходном модуле`

<a id="constant-WORKSPACE_CSS"></a>

### `WORKSPACE_CSS`

`Объёмное значение см. в исходном модуле`


<a id="symbol-BrowserPane"></a>

## `BrowserPane`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane`

Управляет деревом, выбором, навигацией и режимом превью одной панели. Зависимости конструктора: workspace, index.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `comparison`, `container`, `entry`, `expanded`, `filter_value`, `folder_entries`, `folder_size`, `folders`, `footer`, `generation`, `heading`, `hidden`, `index`, `job_id`, `kind`, `limits`, `loading_folders`, `location`, `matches`, `mode_switch`, `navigation`, `navigation_entries`, `navigation_revision`, `parent_button`, `path`, `path_bar`, `path_signature`, `preview`, `refresh_button`, `refreshing`, `result_filter`, `root_button`, `root_path`, `rows`, `scan`, `size_cells`, `snapshot_label`, `title`, `toolbar`, `tree`, `tree_scroll`, `view_mode`, `volume_id`, `volume_select`, `workspace`.

Именованные методы: `__init__`, `volume`, `display_volume_id`, `scope`, `volume_changed`, `mode_changed`, `set_mode`, `activate_heading`, `focus_tree`, `register_navigation`, `update_navigation_selection`, `keyboard_selected`, `hidden_changed`, `folder_clicked`, `save_browse_state`, `restore_browse_state`, `update_volume_select`, `update_header`, `size_scope`, `comparison_open`, `update_size_header`, `refresh_busy`, `render_path`, `open_path`, `show_volume`, `refresh_open_folder`, `load_folder`, `select`, `go_root`, `go_parent`, `refresh`, `change_filter`, `more`, `render`.

<a id="symbol-BrowserPane.__init__"></a>

## `BrowserPane.__init__`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.__init__`

Инициализирует BrowserPane и его рабочее состояние. Обновляет состояние объекта: comparison, container, entry, expanded, filter_value, folder_entries, folder_size, folders, footer, generation, heading, hidden и ещё 33.

```python
def __init__(self, workspace, index)
```

Присваивания полям `self`: `comparison`, `container`, `entry`, `expanded`, `filter_value`, `folder_entries`, `folder_size`, `folders`, `footer`, `generation`, `heading`, `hidden`, `index`, `job_id`, `kind`, `limits`, `loading_folders`, `location`, `matches`, `mode_switch`, `navigation`, `navigation_entries`, `navigation_revision`, `parent_button`, `path`, `path_bar`, `path_signature`, `preview`, `refresh_button`, `refreshing`, `result_filter`, `root_button`, `root_path`, `rows`, `scan`, `size_cells`, `snapshot_label`, `title`, `toolbar`, `tree`, `tree_scroll`, `view_mode`, `volume_id`, `volume_select`, `workspace`.

Прямые выражения вызова: `ComparisonTree`, `StoragePreview`, `self.container.on`, `self.result_filter.set_visibility`, `self.title.lower`, `self.tree.on`, `set`, `ui.button`, `ui.button(icon='arrow_upward', on_click=self.go_parent).props`, `ui.button(icon='arrow_upward', on_click=self.go_parent).props('flat dense round color=dark').props`, `ui.button(icon='refresh', on_click=self.refresh).props`, `ui.button(icon='refresh', on_click=self.refresh).props('flat dense round color=dark').props`, `ui.button(icon='vertical_align_top', on_click=self.go_root).props`, `ui.button(icon='vertical_align_top', on_click=self.go_root).props('flat dense round color=dark').props`, `ui.button(self.title + ' панель', on_click=self.activate_heading).props`, `ui.button(self.title + ' панель', on_click=self.activate_heading).props('flat dense no-caps color=green-9').classes`, `ui.checkbox`, `ui.checkbox('Скрытые', value=False, on_change=self.hidden_changed).props`, `ui.checkbox('Скрытые', value=False, on_change=self.hidden_changed).props('dense size=xs').classes`, `ui.column`, `ui.column().classes`, `ui.column().classes('s-tree gap-0').props`, `ui.element`, `ui.element('div').classes`, `ui.element('nav').classes`, `ui.element('nav').classes('pane-path').props`, `ui.label`, `ui.label('Просмотр папок').classes`, `ui.label('Том не выбран').classes`, `ui.label().classes`, `ui.label().classes('pane-folder-size').props`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select(options, value='', label='Результаты' if index == 0 else 'Список справа', on_change=self.change_filter).props`, `ui.select(options, value='', label='Результаты' if index == 0 else 'Список справа', on_change=self.change_filter).props('outlined dense').classes`, `ui.select({}, on_change=self.volume_changed).props`, `ui.select({}, on_change=self.volume_changed).props('outlined dense options-dense').props`, `ui.select({}, on_change=self.volume_changed).props('outlined dense options-dense').props('aria-label="Том слева"' if index == 0 else 'aria-label="Том справа"').classes`, `ui.toggle`, `ui.toggle({'tree': 'Дерево', 'preview': 'Превью'}, value='tree', on_change=self.mode_changed).props`, `ui.toggle({'tree': 'Дерево', 'preview': 'Превью'}, value='tree', on_change=self.mode_changed).props('dense no-caps unelevated toggle-color=blue-8').props`, `ui.toggle({'tree': 'Дерево', 'preview': 'Превью'}, value='tree', on_change=self.mode_changed).props('dense no-caps unelevated toggle-color=blue-8').props(f'aria-label="Режим {self.title.lower()} панели"').classes`, `workspace.property_menu`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.activate_heading"></a>

## `BrowserPane.activate_heading`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.activate_heading`

Делает панель активной и возвращает клавиатурный фокус дереву. Использует self.comparison.show_matches, self.focus_tree, self.workspace.set_active.

```python
def activate_heading(self)
```

Прямые выражения вызова: `self.comparison.show_matches`, [self.focus_tree](workspace_ui.md#symbol-BrowserPane.focus_tree), `self.workspace.set_active`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.change_filter"></a>

## `BrowserPane.change_filter`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.change_filter`

Меняет фильтр статусов сохранённого дерева и перезагружает результат. Обновляет состояние объекта: expanded, filter_value.

```python
async def change_filter(self, event)
```

Присваивания полям `self`: `expanded`, `filter_value`.

Прямые выражения вызова: `self.folders.clear`, [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), [self.render](workspace_ui.md#symbol-BrowserPane.render).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.comparison_open"></a>

## `BrowserPane.comparison_open`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.comparison_open`

Проверяет наличие открытого результата общей или парной сверки. Возвращает локальное значение без обращения к файловой системе.

```python
def comparison_open(self)
```

Прямые выражения вызова: `bool`.

Выражения возврата (ветви, без исполнения):

- `bool(self.workspace.report or (self.workspace.pair.active and self.workspace.pair.report))`


<a id="symbol-BrowserPane.display_volume_id"></a>

## `BrowserPane.display_volume_id`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.display_volume_id`

Возвращает ID тома, фактически показанного деревом или превью. Возвращает локальное значение без обращения к файловой системе.

```python
def display_volume_id(self)
```

Декораторы: `property`.

Выражения возврата (ветви, без исполнения):

- `self.preview.volume_id if self.view_mode == 'preview' else self.volume_id`


<a id="symbol-BrowserPane.focus_tree"></a>

## `BrowserPane.focus_tree`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.focus_tree`

Назначает DOM-фокус дереву без нежелательной прокрутки страницы. Использует ws.client.run_javascript.

```python
def focus_tree(self)
```

Прямые выражения вызова: `ws.client.run_javascript`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.folder_clicked"></a>

## `BrowserPane.folder_clicked`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.folder_clicked`

Различает одиночный и двойной щелчок по папке дерева. Асинхронно ожидает: self.comparison.open_folder, self.comparison.select, self.open_path, self.select.

```python
async def folder_clicked(self, event)
```

Прямые выражения вызова: `self.comparison.open_folder`, `self.comparison.select`, `self.folder_entries.get`, [self.open_path](workspace_ui.md#symbol-BrowserPane.open_path), [self.select](workspace_ui.md#symbol-BrowserPane.select).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.go_parent"></a>

## `BrowserPane.go_parent`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.go_parent`

Переходит к родительской папке с соблюдением границ сверки и превью. Обновляет состояние объекта: entry, kind, path.

```python
async def go_parent(self)
```

Присваивания полям `self`: `entry`, `kind`, `path`.

Прямые выражения вызова: `PurePosixPath`, `parent.startswith`, `relative_path`, [self.comparison_open](workspace_ui.md#symbol-BrowserPane.comparison_open), `self.expanded.add`, [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), `self.preview.parent`, [self.render](workspace_ui.md#symbol-BrowserPane.render), [self.show_volume](workspace_ui.md#symbol-BrowserPane.show_volume), `self.workspace.pair.navigate_path`, `self.workspace.pair.relative`, `self.workspace.preview_selection`, `self.workspace.refresh_matches`, `self.workspace.set_active`, `self.workspace.update_scopes`, `str`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.go_root"></a>

## `BrowserPane.go_root`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.go_root`

Переходит к допустимому корню текущего режима панели. Обновляет состояние объекта: entry, kind, path.

```python
async def go_root(self)
```

Присваивания полям `self`: `entry`, `kind`, `path`.

Прямые выражения вызова: [self.comparison_open](workspace_ui.md#symbol-BrowserPane.comparison_open), `self.expanded.add`, `self.preview.open_folder`, [self.render](workspace_ui.md#symbol-BrowserPane.render), [self.show_volume](workspace_ui.md#symbol-BrowserPane.show_volume), `self.workspace.pair.navigate_path`, `self.workspace.preview_selection`, `self.workspace.refresh_matches`, `self.workspace.set_active`, `self.workspace.update_scopes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.hidden_changed"></a>

## `BrowserPane.hidden_changed`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.hidden_changed`

Обновляет отображение скрытых элементов и сохраняет состояние вкладки. Использует self.preview.render, self.render, self.workspace.pair.set_hidden.

```python
def hidden_changed(self, event)
```

Прямые выражения вызова: `self.preview.render`, [self.render](workspace_ui.md#symbol-BrowserPane.render), `self.workspace.pair.set_hidden`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.keyboard_selected"></a>

## `BrowserPane.keyboard_selected`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.keyboard_selected`

Принимает клавиатурный выбор строки и открывает связанное превью. Асинхронно ожидает: self.comparison.select, self.select.

```python
async def keyboard_selected(self, event)
```

Прямые выражения вызова: `event.args.get`, `self.comparison.select`, `self.navigation_entries.get`, [self.select](workspace_ui.md#symbol-BrowserPane.select).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.load_folder"></a>

## `BrowserPane.load_folder`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.load_folder`

Загружает страницу живого, виртуального или сохранённого дерева через API. Обрабатывает ошибки: Exception.

```python
async def load_folder(self, path, *, more=False, refresh=True, discover=True)
```

Прямые выражения вызова: `dict`, `len`, `previous.get`, `self.folders.get`, `self.folders.get(path, {}).get`, `self.scan.get`, `self.workspace.error_text`, `self.workspace.read_directory`, `self.workspace.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `data`
- `self.folders[path]`


<a id="symbol-BrowserPane.mode_changed"></a>

## `BrowserPane.mode_changed`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.mode_changed`

Передаёт действительное переключение режима панели в set_mode. Асинхронно ожидает: self.set_mode.

```python
async def mode_changed(self, event)
```

Прямые выражения вызова: [self.set_mode](workspace_ui.md#symbol-BrowserPane.set_mode).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.more"></a>

## `BrowserPane.more`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.more`

Загружает следующую страницу дочерних элементов папки. Асинхронно ожидает: self.load_folder.

```python
async def more(self, path)
```

Прямые выражения вызова: `self.limits.get`, [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), [self.render](workspace_ui.md#symbol-BrowserPane.render), `self.workspace.is_photos`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.open_path"></a>

## `BrowserPane.open_path`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.open_path`

Открывает путь в обычном, парном или сохранённом дереве панели. Асинхронно ожидает: self.show_volume, self.workspace.open_volume, self.workspace.pair.navigate_path, self.workspace.refresh_matches.

```python
async def open_path(self, path)
```

Прямые выражения вызова: `path.startswith`, `relative_path`, [self.show_volume](workspace_ui.md#symbol-BrowserPane.show_volume), `self.workspace.open_volume`, `self.workspace.pair.navigate_path`, `self.workspace.refresh_matches`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.refresh"></a>

## `BrowserPane.refresh`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.refresh`

Обновляет открытую область и состояние её списков без потери выбранного режима. Обновляет состояние объекта: entry, kind, path, refreshing, root_path.

```python
async def refresh(self)
```

Присваивания полям `self`: `entry`, `kind`, `path`, `refreshing`, `root_path`.

Прямые выражения вызова: `'/'.join`, `(data or {}).get`, `PurePosixPath`, `any`, `child.startswith`, `data.get`, `enumerate`, `filter`, `len`, `list`, `path.startswith`, `path[len(base):].strip`, `range`, `relative_path`, [self.comparison_open](workspace_ui.md#symbol-BrowserPane.comparison_open), `self.expanded.add`, `self.expanded.discard`, `self.folders.pop`, [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), `self.preview.refresh`, [self.refresh_busy](workspace_ui.md#symbol-BrowserPane.refresh_busy), [self.render](workspace_ui.md#symbol-BrowserPane.render), `self.workspace.is_photos`, `self.workspace.open_volume`, `self.workspace.preview_selection`, `self.workspace.set_active`, `self.workspace.size_force.add`, `self.workspace.update_scopes`, `self.workspace.update_size_labels`, `str`, `ui.notify`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.refresh_busy"></a>

## `BrowserPane.refresh_busy`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.refresh_busy`

Обновляет индикатор фонового чтения открытой папки. Использует any, pane.size_scope, self.size_scope, self.workspace.directory_sizes.get, self.workspace.directory_sizes.get(volume_id, {}).get.

```python
def refresh_busy(self)
```

Прямые выражения вызова: `any`, `getattr`, `pane.size_scope`, [self.size_scope](workspace_ui.md#symbol-BrowserPane.size_scope), `self.workspace.directory_sizes.get`, `self.workspace.directory_sizes.get(volume_id, {}).get`, `self.workspace.directory_sizes.get(volume_id, {}).get(path, {}).get`.

Выражения возврата (ветви, без исполнения):

- `True`
- `False`
- `any((pane.refreshing and pane.size_scope() == scope for pane in getattr(self.workspace, 'panes', ()))) or scope in self.workspace.size_force or self.workspace.directory_sizes.get(volume_id, {}).get(path, {}).get('state') in ('queued', 'running')`


<a id="symbol-BrowserPane.refresh_open_folder"></a>

## `BrowserPane.refresh_open_folder`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.refresh_open_folder`

Фоново обновляет открытую папку, отбрасывая ответы прежнего поколения панели. Асинхронно ожидает: self.load_folder.

```python
async def refresh_open_folder(self, generation, volume_id, path)
```

Прямые выражения вызова: [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), `self.loading_folders.discard`, [self.render](workspace_ui.md#symbol-BrowserPane.render).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.register_navigation"></a>

## `BrowserPane.register_navigation`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.register_navigation`

Регистрирует строку для клавиатурной навигации и выбора элемента. Использует (scope or {}).get, entry.get, json.dumps.

```python
def register_navigation(self, row, entry, scope=None, *, selected=False)
```

Прямые выражения вызова: `(scope or {}).get`, `entry.get`, `json.dumps`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.render"></a>

## `BrowserPane.render`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.render`

Перестраивает видимые строки независимого дерева и регистрирует навигацию. Обновляет состояние объекта: navigation_revision.

```python
def render(self)
```

Присваивания полям `self`: `navigation_revision`.

Прямые выражения вызова: `(membership or {}).get`, `bool`, `branch`, `count`, `data.get`, `entry.get`, `entry.get('metadata', {}).get`, [folder_membership](workspace_ui.md#symbol-folder_membership), `len`, `max`, `self.comparison.render`, `self.container.classes`, `self.container.style`, `self.folder_entries.clear`, `self.folders.values`, `self.navigation_entries.clear`, `self.rows.clear`, `self.size_cells.clear`, `self.tree.clear`, [self.update_header](workspace_ui.md#symbol-BrowserPane.update_header), `self.workspace.pair.render_tree`, `ui.button`, `ui.button('Зарегистрировать диск', icon='usb', on_click=lambda: self.workspace.register_disk(self)).props`, `ui.button('Зарегистрировать диск', icon='usb', on_click=lambda: self.workspace.register_disk(self)).props('unelevated no-caps color=green-9').classes`, `ui.element`, `ui.element('div').classes`, `ui.label`, `ui.label('Выбери том для этой панели.').classes`, `ui.label(volume.get('identity_error') or 'Носитель не подтверждён').classes`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.render.branch"></a>

## `BrowserPane.render.branch`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.render.branch`

Рекурсивно рисует раскрытые узлы обычного дерева и регистрирует навигацию строк. Использует PurePosixPath, PurePosixPath(entry['name']).suffix[1:].upper, STATUS_COLORS.get, STATUS_ICONS.get, branch.

```python
def branch(path, depth)
```

Прямые выражения вызова: `PurePosixPath`, `PurePosixPath(entry['name']).suffix[1:].upper`, `STATUS_COLORS.get`, `STATUS_ICONS.get`, [branch](workspace_ui.md#symbol-BrowserPane.render.branch), `data.get`, `datetime.fromtimestamp`, `datetime.fromtimestamp(entry['mtime_ns'] / 1000000000.0, timezone.utc).isoformat`, `e['name'].startswith`, `entry.get`, `entry.get('counts', {}).items`, `entry.get('metadata', {}).get`, `folder_icon`, [folder_membership](workspace_ui.md#symbol-folder_membership), `json.dumps`, `len`, `membership.get`, `next`, `row.on`, `self.folders.get`, `self.limits.get`, [self.register_navigation](workspace_ui.md#symbol-BrowserPane.register_navigation), `self.workspace.copies.context_actions`, `self.workspace.directory_size_text`, `self.workspace.format_bytes`, `self.workspace.format_date`, `self.workspace.is_photos`, `self.workspace.property_menu`, `str`, `ui.button`, `ui.button(entry['name'], on_click=None if directory else lambda e=entry: self.select(e)).props`, `ui.button(entry['name'], on_click=None if directory else lambda e=entry: self.select(e)).props('flat dense no-caps color=dark').classes`, `ui.button(f'Показать ещё… ({remaining})', on_click=lambda p=path: self.more(p)).props`, `ui.button(f'Показать ещё… ({remaining})', on_click=lambda p=path: self.more(p)).props('flat dense no-caps color=dark').classes`, `ui.button(icon='expand_more' if entry['path'] in self.expanded else 'chevron_right', on_click=lambda e=entry: self.select(e, True)).props`, `ui.button(icon='expand_more' if entry['path'] in self.expanded else 'chevron_right', on_click=lambda e=entry: self.select(e, True)).props('flat dense color=grey-7 aria-label="Раскрыть папку"').classes`, `ui.context_menu`, `ui.element`, `ui.element('div').classes`, `ui.element('span').classes`, `ui.icon`, `ui.icon(STATUS_ICONS.get(status, 'help_outline'), size='13px').classes`, `ui.icon(STATUS_ICONS.get(status, 'help_outline'), size='13px').classes('shrink-0').style`, `ui.icon(STATUS_ICONS.get(status, 'help_outline'), size='13px').classes('shrink-0').style('color:' + STATUS_COLORS.get(status, '#747b72')).props`, `ui.icon({'symlink': 'link', 'mount': 'storage'}.get(entry['kind'], 'insert_drive_file'), size='14px').classes`, `ui.label`, `ui.label('Нет видимых элементов' if data.get('entries') else 'Папка пуста').classes`, `ui.label('Читаю папку…' if path in self.loading_folders else 'Список готовится.' if self.scan and self.scan['state'] in ('pending', 'running') else 'Снимок папки не сохранён.').classes`, `ui.label('медиатека').classes`, `ui.label('медиатека').classes('s-tree-role library-role').tooltip`, `ui.label('← ' + membership.get('source_label', 'копия')).classes`, `ui.label(FOLDER_TAGS[tag]).classes`, `ui.label(data['error']).classes`, `ui.label(f"{entry['count']} объектов" if directory and 'count' in entry else self.workspace.format_bytes(size) if size is not None and entry['kind'] == 'file' else '—').classes`, `ui.label(kind or PurePosixPath(entry['name']).suffix[1:].upper() or 'Файл').classes`, `ui.label(membership['label']).classes`, `ui.label(self.workspace.directory_size_text(self.volume_id, entry['path'])).classes`, `ui.label(self.workspace.format_date(modified)).classes`, `ui.label(str(number)).classes`, `ui.label(str(number)).classes('pane-count').style`, `ui.menu_item`, `ui.row`, `ui.row().classes`, `ui.row().classes('s-name-cell').style`, `{'directory': 'Папка', 'symlink': 'Ссылка', 'mount': 'Том', 'special': 'Особый'}.get`, `{'symlink': 'link', 'mount': 'storage'}.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.render_path"></a>

## `BrowserPane.render_path`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.render_path`

Строит кликабельный путь с учётом границы выбранной области. Обновляет состояние объекта: path_signature.

```python
def render_path(self, volume_id, path, kind, *, boundary='', navigate=None, entry_name=None)
```

Присваивания полям `self`: `path_signature`.

Прямые выражения вызова: `'/'.join`, `(volume['mount_path'] or volume.get('network_url') or volume_label(volume)).rstrip`, `PurePosixPath`, `base.rpartition`, `bool`, `crumb.props`, `crumbs.extend`, `enumerate`, `len`, `self.path_bar.clear`, `self.workspace.client.run_javascript`, `self.workspace.resolve_volume`, `ui.button`, `ui.button(name, icon='folder_open' if current else 'folder', on_click=lambda p=relative: navigate(p)).props`, `ui.button(name, icon='folder_open' if current else 'folder', on_click=lambda p=relative: navigate(p)).props('flat dense no-caps').classes`, `ui.element`, `ui.element('span').classes`, `ui.icon`, `ui.label`, `ui.label('/').classes`, `ui.label('/').classes('pane-path-slash').props`, `ui.label(prefix + '/').classes`, `volume.get`, [volume_label](workspace_ui.md#symbol-volume_label).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.restore_browse_state"></a>

## `BrowserPane.restore_browse_state`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.restore_browse_state`

Восстанавливает дерево после выхода из связанного режима. Обновляет состояние объекта: filter_value, generation, job_id, scan.

```python
def restore_browse_state(self, state)
```

Присваивания полям `self`: `filter_value`, `generation`, `job_id`, `scan`.

Прямые выражения вызова: `self.comparison.reset`, `self.hidden.set_value`, `self.matches.clear`, [self.render](workspace_ui.md#symbol-BrowserPane.render), `self.result_filter.set_value`, `self.volume_select.set_value`, `setattr`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.save_browse_state"></a>

## `BrowserPane.save_browse_state`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.save_browse_state`

Сохраняет локальное состояние независимого дерева перед переходом в связанную пару. Поля результата: volume_id, root_path, path, kind, entry, folders, expanded, limits, hidden.

```python
def save_browse_state(self)
```

Прямые выражения вызова: `self.expanded.copy`, `self.folders.copy`, `self.limits.copy`.

Выражения возврата (ветви, без исполнения):

- `{'volume_id': self.volume_id, 'root_path': self.root_path, 'path': self.path, 'kind': self.kind, 'entry': self.entry, 'folders': self.folders.copy(), 'expanded': self.expanded.copy(), 'limits': self.limits.copy(), 'hidden': self.hidden.value}`


<a id="symbol-BrowserPane.scope"></a>

## `BrowserPane.scope`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.scope`

Возвращает допустимую файловую область панели для операций с папками. Поля результата: volume_id, path.

```python
def scope(self)
```

Прямые выражения вызова: `PurePosixPath`, `dict`, `next`, `relative_path`, `self.volume.get`, `self.workspace.is_photos`, `str`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `None`
- `dict(volume_id=self.preview.volume_id, path=path)`
- `{'volume_id': self.volume_id, 'path': path}`


<a id="symbol-BrowserPane.select"></a>

## `BrowserPane.select`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.select`

Выбирает строку дерева, синхронизирует превью и при необходимости раскрывает папку. Обновляет состояние объекта: entry, kind, path.

```python
async def select(self, entry, toggle=False, *, render=True)
```

Присваивания полям `self`: `entry`, `kind`, `path`.

Прямые выражения вызова: `self.expanded.add`, `self.expanded.remove`, [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), [self.render](workspace_ui.md#symbol-BrowserPane.render), [self.update_header](workspace_ui.md#symbol-BrowserPane.update_header), [self.update_navigation_selection](workspace_ui.md#symbol-BrowserPane.update_navigation_selection), `self.workspace.preview_selection`, `self.workspace.refresh_matches`, `self.workspace.set_active`, `self.workspace.update_scopes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.set_mode"></a>

## `BrowserPane.set_mode`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.set_mode`

Переключает дерево и превью с сохранением положения и согласованием второй панели. Обновляет состояние объекта: path_signature, tree_scroll, view_mode.

```python
async def set_mode(self, mode, *, target=None)
```

Присваивания полям `self`: `path_signature`, `tree_scroll`, `view_mode`.

Прямые выражения вызова: `PurePosixPath`, `dict`, `float`, `other.set_mode`, [self.focus_tree](workspace_ui.md#symbol-BrowserPane.focus_tree), `self.mode_switch.set_value`, `self.preview.content.set_visibility`, `self.preview.show`, [self.render](workspace_ui.md#symbol-BrowserPane.render), `self.tree.set_visibility`, `self.volume_select.set_value`, `self.workspace.client.run_javascript`, `self.workspace.pair.render_rail`, `self.workspace.persist_workspace`, `self.workspace.update_scopes`.

Перехватываемые типы: `TimeoutError`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.show_volume"></a>

## `BrowserPane.show_volume`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.show_volume`

Показывает том и сначала загружает снимок, затем обновляет доступную папку. Обновляет состояние объекта: entry, expanded, filter_value, generation, job_id, kind, path, root_path, scan, volume_id.

```python
async def show_volume(self, volume_id, path='', *, scan=None, job_id=None, activate=True)
```

Присваивания полям `self`: `entry`, `expanded`, `filter_value`, `generation`, `job_id`, `kind`, `path`, `root_path`, `scan`, `volume_id`.

Прямые выражения вызова: [archived](workspace_ui.md#symbol-archived), `background_tasks.create`, `relative_path`, [self.focus_tree](workspace_ui.md#symbol-BrowserPane.focus_tree), `self.folders.clear`, `self.limits.clear`, [self.load_folder](workspace_ui.md#symbol-BrowserPane.load_folder), `self.loading_folders.add`, `self.loading_folders.clear`, `self.matches.clear`, [self.refresh_open_folder](workspace_ui.md#symbol-BrowserPane.refresh_open_folder), [self.render](workspace_ui.md#symbol-BrowserPane.render), `self.result_filter.set_value`, `self.size_cells.clear`, `self.tree.clear`, [self.update_header](workspace_ui.md#symbol-BrowserPane.update_header), `self.volume_select.set_value`, `self.workspace.archive.open`, `self.workspace.preview_selection`, `self.workspace.render_volumes`, `self.workspace.set_active`, `self.workspace.update_scopes`, `ui.spinner`, `ui.spinner(size='22px').classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.size_scope"></a>

## `BrowserPane.size_scope`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.size_scope`

Определяет область для отображаемого логического размера папки. Использует PurePosixPath, relative_path, row.get, self.workspace.is_photos, self.workspace.pair.by_path.get.

```python
def size_scope(self)
```

Прямые выражения вызова: `PurePosixPath`, `getattr`, `relative_path`, `row.get`, `self.workspace.is_photos`, `self.workspace.pair.by_path.get`, `str`.

Выражения возврата (ветви, без исполнения):

- `None`
- `(self.volume_id, path)`


<a id="symbol-BrowserPane.update_header"></a>

## `BrowserPane.update_header`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.update_header`

Обновляет путь, подписи и доступность элементов управления панели. Обновляет состояние объекта: path_signature.

```python
def update_header(self)
```

Присваивания полям `self`: `path_signature`.

Прямые выражения вызова: `(self.entry or {}).get`, [archived](workspace_ui.md#symbol-archived), `bool`, `button.set_enabled`, `f" · {library['media_count']:,} объектов".replace`, `library.get`, `selected.get`, `self.comparison.update_header`, [self.comparison_open](workspace_ui.md#symbol-BrowserPane.comparison_open), `self.folders.get`, `self.hidden.set_visibility`, `self.location.set_visibility`, `self.navigation.set_visibility`, `self.path_bar.clear`, `self.path_bar.set_visibility`, `self.preview.update_header`, `self.refresh_button.set_enabled`, [self.render_path](workspace_ui.md#symbol-BrowserPane.render_path), `self.result_filter.set_enabled`, `self.result_filter.set_visibility`, `self.scan.get`, `self.toolbar.set_visibility`, [self.update_size_header](workspace_ui.md#symbol-BrowserPane.update_size_header), [self.update_volume_select](workspace_ui.md#symbol-BrowserPane.update_volume_select), `self.volume_select.set_enabled`, `self.volume_select.set_visibility`, `self.workspace.capacity_text`, `self.workspace.format_date`, `self.workspace.pair.update_header`, `ui.label`, `ui.label('Выбери том').classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.update_navigation_selection"></a>

## `BrowserPane.update_navigation_selection`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.update_navigation_selection`

Обновляет признак выбранной строки среди зарегистрированных DOM-элементов. Использует (scope or {}).get, entry.get, json.dumps, row.classes, self.navigation_entries.items.

```python
def update_navigation_selection(self, entry, scope=None)
```

Прямые выражения вызова: `(scope or {}).get`, `entry.get`, `json.dumps`, `row.classes`, `self.navigation_entries.items`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.update_size_header"></a>

## `BrowserPane.update_size_header`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.update_size_header`

Обновляет размер текущей области в заголовке панели. Использует self.comparison_open, self.folder_size.set_visibility, self.refresh_busy, self.refresh_button.set_enabled, self.size_scope.

```python
def update_size_header(self)
```

Прямые выражения вызова: `bool`, [self.comparison_open](workspace_ui.md#symbol-BrowserPane.comparison_open), `self.folder_size.set_visibility`, [self.refresh_busy](workspace_ui.md#symbol-BrowserPane.refresh_busy), `self.refresh_button.set_enabled`, [self.size_scope](workspace_ui.md#symbol-BrowserPane.size_scope), `self.workspace.directory_size_text`, `self.workspace.is_photos`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-BrowserPane.update_volume_select"></a>

## `BrowserPane.update_volume_select`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.update_volume_select`

Обновляет варианты выбора тома и текущее значение селектора панели. Использует archived, self.volume_select.props.pop, self.volume_select.set_options, self.workspace.resolve_volume, self.workspace.selectable_volumes.

```python
def update_volume_select(self, volume_id)
```

Прямые выражения вызова: [archived](workspace_ui.md#symbol-archived), `self.volume_select.props.pop`, `self.volume_select.set_options`, `self.workspace.resolve_volume`, `self.workspace.selectable_volumes`, `v.get`, [volume_label](workspace_ui.md#symbol-volume_label).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-BrowserPane.volume"></a>

## `BrowserPane.volume`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.volume`

Возвращает сведения о выбранном томе или виртуальной медиатеке. Использует self.workspace.resolve_volume.

```python
def volume(self)
```

Декораторы: `property`.

Прямые выражения вызова: `self.workspace.resolve_volume`.

Выражения возврата (ветви, без исполнения):

- `self.workspace.resolve_volume(self.volume_id)`


<a id="symbol-BrowserPane.volume_changed"></a>

## `BrowserPane.volume_changed`

[workspace_ui.py](../../workspace_ui.py) · `BrowserPane.volume_changed`

Обрабатывает актуальное изменение выбранного тома, отбрасывая устаревшие события. Асинхронно ожидает: self.preview.show, self.workspace.open_volume.

```python
async def volume_changed(self, event)
```

Прямые выражения вызова: `dict`, `self.preview.show`, `self.workspace.open_volume`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace"></a>

## `StorageWorkspace`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace`

Координирует две панели, тома, медиатеки, сверки и сохранённое состояние вкладки. Зависимости конструктора: request, format_bytes, format_date, core_url.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `active_index`, `archive`, `archive_list`, `browse_active`, `browse_state`, `client`, `context_menu_open`, `copies`, `core_url`, `current_matches`, `directory_sizes`, `editing`, `format_bytes`, `format_date`, `job_id`, `last_marker`, `layout`, `link_badge`, `match_generation`, `overview`, `pair`, `panes`, `photo_libraries`, `refresh_button`, `report`, `request`, `sidebar_state`, `sidebar_storage`, `size_force`, `size_open_scopes`, `size_requested`, `sizes_polling`, `state_payload`, `state_ready`, `trees`, `volume_list`, `volumes`, `volumes_section`.

Именованные методы: `__init__`, `sidebar_expansion`, `build_operations`, `error_text`, `notice`, `is_photos`, `browse_volumes`, `selectable_volumes`, `resolve_volume`, `read_directory`, `open_library`, `open_photo`, `capacity_text`, `set_active`, `workspace_snapshot`, `preview_selection`, `persist_workspace`, `restore_panes`, `restore_workspace`, `open_in_finder`, `directory_size_text`, `size_texts`, `update_size_labels`, `load_directory_sizes`, `poll_directory_sizes`, `property_menu`, `open_volume`, `render_volumes`, `refresh_volumes`, `update_scopes`, `load`, `poll_connected`, `refresh_history`, `history_changed`, `choose_job`, `apply_report`, `start_comparison`, `browse`, `report_marker`, `poll`, `render_progress`, `control`, `refresh_matches`, `show_journal`, `show_properties`, `edit_folder_tags`, `apply_folder_tags`, `edit_metadata`, `rename_disk`, `register_disk`, `connect`.

<a id="symbol-StorageWorkspace.__init__"></a>

## `StorageWorkspace.__init__`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.__init__`

Инициализирует StorageWorkspace и его рабочее состояние. Обновляет состояние объекта: active_index, archive, archive_list, browse_active, browse_state, client, context_menu_open, copies, core_url, current_matches и ещё 28.

```python
def __init__(self, request, format_bytes, format_date, core_url='http://127.0.0.1:18765')
```

Присваивания полям `self`: `active_index`, `archive`, `archive_list`, `browse_active`, `browse_state`, `client`, `context_menu_open`, `copies`, `core_url`, `current_matches`, `directory_sizes`, `editing`, `format_bytes`, `format_date`, `job_id`, `last_marker`, `layout`, `link_badge`, `match_generation`, `overview`, `pair`, `panes`, `photo_libraries`, `refresh_button`, `report`, `request`, `sidebar_state`, `sidebar_storage`, `size_force`, `size_open_scopes`, `size_requested`, `sizes_polling`, `state_payload`, `state_ready`, `trees`, `volume_list`, `volumes`, `volumes_section`.

Прямые выражения вызова: [BrowserPane](workspace_ui.md#symbol-BrowserPane), `CopyGroupsUI`, `PairedWorkspace`, `PhotoLibrariesUI`, `normalize_sidebar`, `range`, [self.build_operations](workspace_ui.md#symbol-StorageWorkspace.build_operations), `self.copies.build_sidebar`, `self.pair.build`, `self.photo_libraries.build`, [self.render_progress](workspace_ui.md#symbol-StorageWorkspace.render_progress), [self.set_active](workspace_ui.md#symbol-StorageWorkspace.set_active), [self.sidebar_expansion](workspace_ui.md#symbol-StorageWorkspace.sidebar_expansion), `self.sidebar_expansion('volume_archive', 'Отключённые', icon='link_off').props`, `self.sidebar_expansion('volume_archive', 'Отключённые', icon='link_off').props('dense').classes`, `self.sidebar_expansion('volumes', 'Тома', icon='storage').props`, `self.sidebar_expansion('volumes', 'Тома', icon='storage').props('dense').classes`, `self.sidebar_storage.get`, `set`, `ui.add_css`, `ui.add_head_html`, `ui.button`, `ui.button('Найти NAS', icon='lan', on_click=lambda: show_network_dialog(request, format_date, self.refresh_volumes)).props`, `ui.button('Обновить тома', icon='refresh', on_click=lambda: self.refresh_volumes(True)).props`, `ui.column`, `ui.column().classes`, `ui.element`, `ui.element('div').classes`, `ui.element('div').classes('pane-link').props`, `ui.icon`, `ui.label`, `ui.label('media.actu').classes`, `ui.label('Загрузка томов M4…').classes`, `ui.label('Том откроется в выделенном дереве.').classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.apply_folder_tags"></a>

## `StorageWorkspace.apply_folder_tags`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.apply_folder_tags`

Применяет полученные метки к локальным снимкам и строкам UI. Использует folder.get, pane.folders.values, pane.render.

```python
def apply_folder_tags(self, volume_id, path, metadata)
```

Прямые выражения вызова: `folder.get`, `pane.folders.values`, `pane.render`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.apply_report"></a>

## `StorageWorkspace.apply_report`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.apply_report`

Показывает общую сверку в панелях и обновляет связанные элементы управления. Обновляет состояние объекта: browse_active, browse_state, job_id, last_marker, match_generation, report.

```python
async def apply_report(self, report)
```

Присваивания полям `self`: `browse_active`, `browse_state`, `job_id`, `last_marker`, `match_generation`, `report`.

Прямые выражения вызова: `next`, `pane.save_browse_state`, `right.comparison.reset`, `right.folders.clear`, `right.render`, `self.history.set_value`, `self.legacy_dialog.close`, `self.pair.unlink`, `self.panes[0].show_volume`, [self.refresh_matches](workspace_ui.md#symbol-StorageWorkspace.refresh_matches), [self.render_progress](workspace_ui.md#symbol-StorageWorkspace.render_progress), [self.report_marker](workspace_ui.md#symbol-StorageWorkspace.report_marker), [self.set_active](workspace_ui.md#symbol-StorageWorkspace.set_active).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.browse"></a>

## `StorageWorkspace.browse`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.browse`

Закрывает отчёт общей сверки и возвращает независимый просмотр папок. Обновляет состояние объекта: browse_state, job_id, last_marker, match_generation, report.

```python
async def browse(self)
```

Присваивания полям `self`: `browse_state`, `job_id`, `last_marker`, `match_generation`, `report`.

Прямые выражения вызова: `pane.restore_browse_state`, `self.current_matches.clear`, `self.history.set_value`, `self.panes[1].comparison.reset`, [self.render_progress](workspace_ui.md#symbol-StorageWorkspace.render_progress), `self.results.clear`, [self.set_active](workspace_ui.md#symbol-StorageWorkspace.set_active), `zip`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.browse_volumes"></a>

## `StorageWorkspace.browse_volumes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.browse_volumes`

Объединяет обычные тома и виртуальные медиатеки для выбора в панелях. Использует libraries.volumes.

```python
def browse_volumes(self)
```

Прямые выражения вызова: `getattr`, `libraries.volumes`.

Выражения возврата (ветви, без исполнения):

- `self.volumes + (libraries.volumes() if libraries else [])`


<a id="symbol-StorageWorkspace.build_operations"></a>

## `StorageWorkspace.build_operations`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.build_operations`

Создаёт управление общей сверкой и диалог её прежнего интерфейса. Обновляет состояние объекта: browse_button, counts, history, journal_button, legacy_dialog, pause_button, phase_label, progress, progress_row, refresh_lists и ещё 5.

```python
def build_operations(self)
```

Присваивания полям `self`: `browse_button`, `counts`, `history`, `journal_button`, `legacy_dialog`, `pause_button`, `phase_label`, `progress`, `progress_row`, `refresh_lists`, `results`, `resume_button`, `scopes_label`, `start_button`, `summary`.

Прямые выражения вызова: `self.copies.build_controls`, `ui.button`, `ui.button('Журнал', icon='receipt_long', on_click=self.show_journal).props`, `ui.button('Закрыть результат сверки', icon='close', on_click=self.browse).props`, `ui.button('Закрыть результат сверки', icon='close', on_click=self.browse).props('flat dense no-caps color=dark').classes`, `ui.button('Закрыть', on_click=self.legacy_dialog.close).props`, `ui.button('Остановить', icon='pause', on_click=lambda: self.control('pause')).props`, `ui.button('Продолжить', icon='play_arrow', on_click=lambda: self.control('resume')).props`, `ui.button('Сверить левую → правую', icon='compare_arrows', on_click=self.start_comparison).props`, `ui.button('Сверить левую → правую', icon='compare_arrows', on_click=self.start_comparison).props('unelevated no-caps color=green-9').classes`, `ui.card`, `ui.card().classes`, `ui.checkbox`, `ui.checkbox('Заново собрать списки с дисков', value=False).props`, `ui.checkbox('Заново собрать списки с дисков', value=False).props('dense size=xs').classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.element`, `ui.element('div').classes`, `ui.label`, `ui.label('').classes`, `ui.label('Выбери том и папку в каждой панели.').classes`, `ui.label('Выбери том и папку в каждой панели.').classes('workspace-scopes w-full').style`, `ui.label('Готово к сверке имён').classes`, `ui.label('ОПЕРАЦИИ').classes`, `ui.label('Прежние отчёты по именам').classes`, `ui.label('Сверка').classes`, `ui.linear_progress`, `ui.linear_progress(value=0, show_value=False).props`, `ui.linear_progress(value=0, show_value=False).props('color=green-8').classes`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select({}, label='История сверок', on_change=self.history_changed).props`, `ui.select({}, label='История сверок', on_change=self.history_changed).props('outlined dense clearable').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.capacity_text"></a>

## `StorageWorkspace.capacity_text`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.capacity_text`

Форматирует сохранённые сведения о заполнении тома. Использует self.format_bytes, volume.get.

```python
def capacity_text(self, volume)
```

Прямые выражения вызова: `self.format_bytes`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `'Объём и занятое место пока неизвестны'`
- `text + (' · ранее' if volume.get('capacity_cached') else '')`


<a id="symbol-StorageWorkspace.choose_job"></a>

## `StorageWorkspace.choose_job`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.choose_job`

Получает сохранённый отчёт по ID и применяет его к рабочему пространству. Обрабатывает ошибки: Exception.

```python
async def choose_job(self, job_id)
```

Прямые выражения вызова: [self.apply_report](workspace_ui.md#symbol-StorageWorkspace.apply_report), [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.connect"></a>

## `StorageWorkspace.connect`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.connect`

Открывает подключение сохранённого сетевого тома в Finder на машине Core. Обрабатывает ошибки: Exception.

```python
async def connect(self, volume_id)
```

Прямые выражения вызова: [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`, `ui.notify`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.control"></a>

## `StorageWorkspace.control`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.control`

Передаёт команду паузы или продолжения общей сверки в Core. Обновляет состояние объекта: report.

```python
async def control(self, action)
```

Присваивания полям `self`: `report`.

Прямые выражения вызова: [self.apply_report](workspace_ui.md#symbol-StorageWorkspace.apply_report), [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), [self.refresh_history](workspace_ui.md#symbol-StorageWorkspace.refresh_history), [self.render_progress](workspace_ui.md#symbol-StorageWorkspace.render_progress), `self.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.directory_size_text"></a>

## `StorageWorkspace.directory_size_text`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.directory_size_text`

Форматирует размер папки с учётом актуальности, ошибки и состояния подсчёта. Использует record.get, self.directory_sizes.get, self.directory_sizes.get(volume_id, {}).get, self.format_bytes, self.format_date.

```python
def directory_size_text(self, volume_id, path, *, detail=False)
```

Прямые выражения вызова: `record.get`, `self.directory_sizes.get`, `self.directory_sizes.get(volume_id, {}).get`, `self.format_bytes`, `self.format_date`, `{'offline': 'Неизвестно', 'error': 'Ошибка', 'unknown': '…'}.get`, `{'offline': 'нет сохранённого размера', 'error': 'не удалось подсчитать', 'unknown': 'ожидает подсчёта'}.get`.

Выражения возврата (ветви, без исполнения):

- `{'offline': 'нет сохранённого размера', 'error': 'не удалось подсчитать', 'unknown': 'ожидает подсчёта'}.get(state, 'Считаю…') if detail else {'offline': 'Неизвестно', 'error': 'Ошибка', 'unknown': '…'}.get(state, 'Считаю…')`
- `text`


<a id="symbol-StorageWorkspace.edit_folder_tags"></a>

## `StorageWorkspace.edit_folder_tags`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.edit_folder_tags`

Открывает редактирование пользовательских меток выбранной папки. Обновляет состояние объекта: editing.

```python
async def edit_folder_tags(self, volume_id, path)
```

Присваивания полям `self`: `editing`.

Прямые выражения вызова: `FOLDER_TAGS.items`, `PurePosixPath`, `controls.items`, `data['metadata'].get`, [folder_membership](workspace_ui.md#symbol-folder_membership), `membership.get`, [self.apply_folder_tags](workspace_ui.md#symbol-StorageWorkspace.apply_folder_tags), [self.is_photos](workspace_ui.md#symbol-StorageWorkspace.is_photos), [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Сохранить', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.checkbox`, `ui.dialog`, `ui.label`, `ui.label('Метка «медиатека» задаётся привязкой к Photos.').classes`, `ui.label('Метки папки').classes`, `ui.label('Можно выбрать несколько. Метки относятся только к этой папке.').classes`, `ui.label('медиатека · ' + membership['media_library']).classes`, `ui.label(PurePosixPath(path).name if path else data['volume']['name']).classes`, `ui.row`, `ui.row().classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.edit_metadata"></a>

## `StorageWorkspace.edit_metadata`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.edit_metadata`

Редактирует сохранённые назначение, флаги и комментарий расположения. Обновляет состояние объекта: editing.

```python
async def edit_metadata(self, volume, path, metadata)
```

Присваивания полям `self`: `editing`.

Прямые выражения вызова: `FLAGS.items`, `PurePosixPath`, `flags.items`, `list`, `own.get`, `pane.load_folder`, `pane.render`, `payload.update`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), [self.refresh_volumes](workspace_ui.md#symbol-StorageWorkspace.refresh_volumes), `self.request`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Сохранить отметки', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.label`, `ui.label('Назначение и отметки').classes`, `ui.label('Сохраняются только отметки в базе приложения.').classes`, `ui.label(PurePosixPath(path).name if path else volume_label(volume)).classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `ui.select`, `ui.select({inherit: default if path else 'Не задано', 'yes': 'Да', 'no': 'Нет'}, value=value, label=label).props`, `ui.select({inherit: default if path else 'Не задано', 'yes': 'Да', 'no': 'Нет'}, value=value, label=label).props('outlined dense').classes`, `ui.select({inherit: default, **PURPOSES}, value=own['purpose'] if own['purpose'] is not None else inherit, label='Что здесь хранится').props`, `ui.select({inherit: default, **PURPOSES}, value=own['purpose'] if own['purpose'] is not None else inherit, label='Что здесь хранится').props('outlined dense').classes`, `ui.textarea`, `ui.textarea('Комментарий', value=own.get('comment') or '').props`, `ui.textarea('Комментарий', value=own.get('comment') or '').props('outlined autogrow maxlength=4000').classes`, [volume_label](workspace_ui.md#symbol-volume_label).

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.error_text"></a>

## `StorageWorkspace.error_text`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.error_text`

Извлекает понятное сообщение из HTTP-ошибки или обычного исключения. Обрабатывает ошибки: ValueError.

```python
def error_text(error)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `error.response.json`, `error.response.json().get`, `hasattr`, `str`.

Перехватываемые типы: `ValueError`.

Выражения возврата (ветви, без исполнения):

- `str(error.response.json().get('detail') or error)`
- `str(error)`


<a id="symbol-StorageWorkspace.history_changed"></a>

## `StorageWorkspace.history_changed`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.history_changed`

Открывает выбранный пользователем отчёт общей сверки. Асинхронно ожидает: self.browse, self.choose_job.

```python
async def history_changed(self, event)
```

Прямые выражения вызова: [self.browse](workspace_ui.md#symbol-StorageWorkspace.browse), [self.choose_job](workspace_ui.md#symbol-StorageWorkspace.choose_job).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.is_photos"></a>

## `StorageWorkspace.is_photos`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.is_photos`

Распознаёт ID виртуального тома медиатеки photos-<source_id>. Использует volume_id.startswith, volume_id[7:].isdigit.

```python
def is_photos(volume_id)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `bool`, `isinstance`, `volume_id.startswith`, `volume_id[7:].isdigit`.

Выражения возврата (ветви, без исполнения):

- `bool(isinstance(volume_id, str) and volume_id.startswith('photos-') and volume_id[7:].isdigit())`


<a id="symbol-StorageWorkspace.load"></a>

## `StorageWorkspace.load`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.load`

Инициализирует рабочее пространство и применяет параметры старой ссылки либо снимок вкладки. Обновляет состояние объекта: job_id, report, state_ready.

```python
async def load(self, source='', path='', job='')
```

Присваивания полям `self`: `job_id`, `report`, `state_ready`.

Прямые выражения вызова: [archived](workspace_ui.md#symbol-archived), `json.dumps`, `next`, `normalize_state`, `pane.render`, `relative_path`, [self.choose_job](workspace_ui.md#symbol-StorageWorkspace.choose_job), `self.client.connected`, `self.client.run_javascript`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.pair.views.clear`, `self.panes[0].show_volume`, `self.panes[1].show_volume`, `self.panes[self.active_index].focus_tree`, [self.persist_workspace](workspace_ui.md#symbol-StorageWorkspace.persist_workspace), `self.photo_libraries.refresh`, [self.refresh_history](workspace_ui.md#symbol-StorageWorkspace.refresh_history), [self.refresh_volumes](workspace_ui.md#symbol-StorageWorkspace.refresh_volumes), [self.resolve_volume](workspace_ui.md#symbol-StorageWorkspace.resolve_volume), [self.restore_workspace](workspace_ui.md#symbol-StorageWorkspace.restore_workspace), [self.set_active](workspace_ui.md#symbol-StorageWorkspace.set_active), `ui.timer`, `v.get`.

Перехватываемые типы: `TimeoutError`, `Exception`, `ValueError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.load_directory_sizes"></a>

## `StorageWorkspace.load_directory_sizes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.load_directory_sizes`

Получает или ставит в очередь размеры выбранных папок через Core. Обрабатывает ошибки: Exception.

```python
async def load_directory_sizes(self, volume_id, paths, *, start=False, refresh=False)
```

Прямые выражения вызова: `dict`, `records.get`, `self.directory_sizes.setdefault`, `self.directory_sizes.setdefault(volume_id, {}).update`, [self.error_text](workspace_ui.md#symbol-StorageWorkspace.error_text), `self.request`, `self.size_requested.update`, [self.update_size_labels](workspace_ui.md#symbol-StorageWorkspace.update_size_labels).

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.notice"></a>

## `StorageWorkspace.notice`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.notice`

Показывает пользователю сообщение об ошибке операции UI. Использует self.error_text, ui.notify.

```python
def notice(self, error)
```

Прямые выражения вызова: [self.error_text](workspace_ui.md#symbol-StorageWorkspace.error_text), `ui.notify`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.open_in_finder"></a>

## `StorageWorkspace.open_in_finder`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.open_in_finder`

Отправляет Core проверенную команду открытия файлового пути в Finder. Обрабатывает ошибки: Exception.

```python
async def open_in_finder(self, volume_id, path='')
```

Прямые выражения вызова: [self.is_photos](workspace_ui.md#symbol-StorageWorkspace.is_photos), [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.open_library"></a>

## `StorageWorkspace.open_library`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.open_library`

Открывает выбранную медиатеку в активной панели. Асинхронно ожидает: self.open_volume.

```python
async def open_library(self, source_id)
```

Прямые выражения вызова: [self.open_volume](workspace_ui.md#symbol-StorageWorkspace.open_volume).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.open_photo"></a>

## `StorageWorkspace.open_photo`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.open_photo`

Передаёт Core команду выделения объекта в системном Photos. Обрабатывает ошибки: Exception.

```python
async def open_photo(self, media_id)
```

Прямые выражения вызова: [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.open_volume"></a>

## `StorageWorkspace.open_volume`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.open_volume`

Открывает файловый том в выбранной панели с выходом из конфликтующего режима. Асинхронно ожидает: self.browse, self.pair.unlink, self.panes[index].preview.show, self.panes[index].show_volume.

```python
async def open_volume(self, volume_id, index=None, *, path='')
```

Прямые выражения вызова: `PurePosixPath`, `dict`, [self.browse](workspace_ui.md#symbol-StorageWorkspace.browse), `self.pair.unlink`, `self.panes[index].preview.show`, `self.panes[index].show_volume`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.persist_workspace"></a>

## `StorageWorkspace.persist_workspace`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.persist_workspace`

Сохраняет нормализованное состояние рабочего пространства в хранилище вкладки. Обновляет состояние объекта: state_payload.

```python
def persist_workspace(self)
```

Присваивания полям `self`: `state_payload`.

Прямые выражения вызова: `json.dumps`, `self.client.run_javascript`, [self.workspace_snapshot](workspace_ui.md#symbol-StorageWorkspace.workspace_snapshot).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.poll"></a>

## `StorageWorkspace.poll`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.poll`

Опросом обновляет общую и парную сверки, копии, медиатеки и превью. Обновляет состояние объекта: last_marker, report.

```python
async def poll(self)
```

Присваивания полям `self`: `last_marker`, `report`.

Прямые выражения вызова: `list`, `pane.load_folder`, `pane.render`, [self.error_text](workspace_ui.md#symbol-StorageWorkspace.error_text), `self.panes[1].comparison.reset`, [self.refresh_matches](workspace_ui.md#symbol-StorageWorkspace.refresh_matches), [self.render_progress](workspace_ui.md#symbol-StorageWorkspace.render_progress), [self.report_marker](workspace_ui.md#symbol-StorageWorkspace.report_marker), `self.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.poll_connected"></a>

## `StorageWorkspace.poll_connected`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.poll_connected`

Вызывает периодический обработчик только для ещё существующего клиента NiceGUI. Асинхронно ожидает: callback.

```python
async def poll_connected(self, callback)
```

Прямые выражения вызова: `callback`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.poll_directory_sizes"></a>

## `StorageWorkspace.poll_directory_sizes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.poll_directory_sizes`

Периодически обновляет видимые размеры и ограничивает повторные запросы. Обновляет состояние объекта: size_open_scopes, sizes_polling.

```python
async def poll_directory_sizes(self)
```

Присваивания полям `self`: `size_open_scopes`, `sizes_polling`.

Прямые выражения вызова: `any`, `grouped.items`, `grouped.setdefault`, `grouped.setdefault(volume_id, []).append`, `len`, `open_scopes.add`, `pane.size_scope`, `paths.sort`, `range`, `record.get`, `records.items`, `row.get`, `self.directory_sizes.get`, `self.directory_sizes.get(volume_id, {}).get`, `self.directory_sizes.get(volume_id, {}).get(path, {}).get`, `self.directory_sizes.items`, [self.load_directory_sizes](workspace_ui.md#symbol-StorageWorkspace.load_directory_sizes), `self.pair.visible_rows`, `self.size_force.difference_update`, `self.size_force.intersection`, [self.update_size_labels](workspace_ui.md#symbol-StorageWorkspace.update_size_labels), `set`, `wanted.add`, `wanted.update`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.preview_selection"></a>

## `StorageWorkspace.preview_selection`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.preview_selection`

Передаёт выбранный элемент в соседнюю панель с включённым превью. Асинхронно ожидает: target.preview.show.

```python
async def preview_selection(self, source)
```

Прямые выражения вызова: `PurePosixPath`, `dict`, `target.preview.show`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.property_menu"></a>

## `StorageWorkspace.property_menu`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.property_menu`

Создаёт контекстное меню свойств с восстановлением фокуса и состоянием редактирования. Использует action, extra_content, menu.classes, menu.on, ui.context_menu.

```python
def property_menu(self, label, callback, *, volume_id, path='', extra=(), extra_content=None, folder=False)
```

Прямые выражения вызова: `action`, `extra_content`, `menu.classes`, `menu.on`, `ui.context_menu`, `ui.menu_item`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.property_menu.action"></a>

## `StorageWorkspace.property_menu.action`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.property_menu.action`

Оборачивает команду контекстного меню в обработчик закрытия и восстановления фокуса. Параметры: callback.

```python
def action(callback)
```

Выражения возврата (ветви, без исполнения):

- `invoke`


<a id="symbol-StorageWorkspace.property_menu.action.invoke"></a>

## `StorageWorkspace.property_menu.action.invoke`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.property_menu.action.invoke`

Асинхронно вызывает команду меню в сохранённом контексте клиента NiceGUI. Асинхронно ожидает: callback.

```python
async def invoke()
```

Прямые выражения вызова: `callback`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.property_menu.before_show"></a>

## `StorageWorkspace.property_menu.before_show`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.property_menu.before_show`

Перед открытием меню отмечает его активность и скрывает файловые команды для Photos. Обновляет состояние объекта: context_menu_open.

```python
def before_show()
```

Присваивания полям `self`: `context_menu_open`.

Прямые выражения вызова: `callable`, `finder.set_visibility`, `properties.set_visibility`, [self.is_photos](workspace_ui.md#symbol-StorageWorkspace.is_photos), `tags.set_visibility`, `volume_id`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.read_directory"></a>

## `StorageWorkspace.read_directory`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.read_directory`

Выбирает API обычного тома или виртуальной медиатеки и получает страницу. Асинхронно ожидает: self.request.

```python
async def read_directory(self, volume_id, path, *, refresh=False, discover=False, offset=0, limit=150)
```

Прямые выражения вызова: `dict`, [self.is_photos](workspace_ui.md#symbol-StorageWorkspace.is_photos), `self.request`.

Выражения возврата (ветви, без исполнения):

- `await self.request('GET', f'/api/photos/libraries/{volume_id[7:]}/browse', params=dict(path=path, offset=offset, limit=limit), timeout=45)`
- `await self.request('GET', f'/api/storage/volumes/{volume_id}/directory', params=dict(path=path, refresh=refresh, discover=discover), timeout=45)`


<a id="symbol-StorageWorkspace.refresh_history"></a>

## `StorageWorkspace.refresh_history`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.refresh_history`

Обновляет список последних заданий общей сверки. Обрабатывает ошибки: Exception.

```python
async def refresh_history(self)
```

Прямые выражения вызова: `JOB_STATES.get`, `self.format_date`, `self.history.update`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.refresh_matches"></a>

## `StorageWorkspace.refresh_matches`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.refresh_matches`

Загружает совпадения выбранного элемента и показывает найденные пути справа. Обновляет состояние объекта: current_matches, match_generation.

```python
async def refresh_matches(self)
```

Присваивания полям `self`: `current_matches`, `match_generation`.

Прямые выражения вызова: `PurePosixPath`, `STATUS_COLORS.get`, `data.get`, `dict`, `entry.get`, `len`, `match.get`, `match['path'].startswith`, `max`, `right.comparison.reset`, `right.comparison.set_matches`, `right.render`, `self.current_matches.append`, [self.error_text](workspace_ui.md#symbol-StorageWorkspace.error_text), `self.request`, `self.results.clear`, `ui.label`, `ui.label('Совпадений в выбранной области нет' if self.report['state'] == 'completed' else 'Сверка ещё выполняется').classes`, `ui.label(('Папка: ' if entry['kind'] == 'directory' else 'Файл: ') + entry['name']).classes`, `ui.label(LABELS[status]).classes`, `ui.label(LABELS[status]).classes('text-xs').style`, `ui.label(f'Найдено путей: {len(self.current_matches)}').classes`, `ui.label(self.error_text(error)).classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.refresh_volumes"></a>

## `StorageWorkspace.refresh_volumes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.refresh_volumes`

Обновляет тома и связанные сведения, сохраняя отображение при ошибках API. Обновляет состояние объекта: volumes.

```python
async def refresh_volumes(self, force=False)
```

Присваивания полям `self`: `volumes`.

Прямые выражения вызова: `access_state`, `data.get`, `pane.render`, `pane.update_header`, `previous.get`, `self.copies.refresh`, [self.is_photos](workspace_ui.md#symbol-StorageWorkspace.is_photos), [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.refresh_button.disable`, `self.refresh_button.enable`, [self.render_volumes](workspace_ui.md#symbol-StorageWorkspace.render_volumes), `self.request`, [self.update_scopes](workspace_ui.md#symbol-StorageWorkspace.update_scopes), `ui.notify`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.refresh_volumes.access_state"></a>

## `StorageWorkspace.refresh_volumes.access_state`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.refresh_volumes.access_state`

Выделяет признаки доступности тома для обнаружения изменений без полной перерисовки. Использует volume.get.

```python
def access_state(volume)
```

Прямые выражения вызова: `tuple`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `tuple((volume.get(key) for key in ('id', 'identity_status', 'identity_error', 'availability', 'mounted'))) if volume else None`


<a id="symbol-StorageWorkspace.register_disk"></a>

## `StorageWorkspace.register_disk`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.register_disk`

Регистрирует выбранный сменный носитель через подтверждённое действие Core. Обрабатывает ошибки: Exception.

```python
async def register_disk(self, pane)
```

Прямые выражения вызова: `(name.value or '').strip`, `pane.show_volume`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), [self.refresh_volumes](workspace_ui.md#symbol-StorageWorkspace.refresh_volumes), `self.request`, `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Создать ID на диске', on_click=lambda: dialog.submit(True)).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.input`, `ui.input('Имя диска', placeholder='Например, Архив фото 2 ТБ').props`, `ui.input('Имя диска', placeholder='Например, Архив фото 2 ТБ').props('outlined dense maxlength=120').classes`, `ui.label`, `ui.label('На диск будет один раз записан файл .media-actu-volume.json с постоянным ID и именем. По нему приложение узнает диск при следующем подключении.').classes`, `ui.label('Прежняя история usbshare останется отдельной записью в разделе «Отключённые».').classes`, `ui.label('Регистрация сменного диска').classes`, `ui.label(volume.get('network_url') or volume['mount_path']).classes`, `ui.notify`, `ui.row`, `ui.row().classes`, `volume.get`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.rename_disk"></a>

## `StorageWorkspace.rename_disk`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.rename_disk`

Открывает переименование зарегистрированного сменного носителя. Обновляет состояние объекта: editing.

```python
async def rename_disk(self, volume_id)
```

Присваивания полям `self`: `editing`.

Прямые выражения вызова: `name.on`, `next`, [self.refresh_volumes](workspace_ui.md#symbol-StorageWorkspace.refresh_volumes), `ui.button`, `ui.button('Отмена', on_click=lambda: dialog.submit(False)).props`, `ui.button('Сохранить', on_click=save).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.dialog().props`, `ui.input`, `ui.input('Имя диска', value=volume['name']).props`, `ui.input('Имя диска', value=volume['name']).props('outlined dense maxlength=120 autofocus').classes`, `ui.label`, `ui.label('Имя диска в media.actu').classes`, `ui.label('Имя сохранится на диске и будет использоваться при следующих подключениях.').classes`, `ui.notify`, `ui.row`, `ui.row().classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.rename_disk.save"></a>

## `StorageWorkspace.rename_disk.save`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.rename_disk.save`

Сохраняет новое название носителя и обновляет связанные данные UI. Обрабатывает ошибки: Exception, ValueError.

```python
async def save()
```

Прямые выражения вызова: `(name.value or '').strip`, `cancel_button.disable`, `cancel_button.enable`, `dialog.submit`, `save_button.disable`, `save_button.enable`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`, `str`, `ui.notify`, `validate_name`.

Перехватываемые типы: `ValueError`, `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.render_progress"></a>

## `StorageWorkspace.render_progress`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.render_progress`

Обновляет прогресс и доступные команды общей сверки, включая старые отчёты. Использует JOB_STATES.get, LABELS.get, STATUS_COLORS.get, report.get, report.get('counts', {}).items.

```python
def render_progress(self)
```

Прямые выражения вызова: `JOB_STATES.get`, `LABELS.get`, `STATUS_COLORS.get`, `bool`, `report.get`, `report.get('counts', {}).items`, `self.browse_button.set_visibility`, `self.counts.clear`, `self.counts.set_visibility`, `self.format_date`, `self.history.update`, `self.journal_button.set_visibility`, `self.link_badge.set_visibility`, `self.pair.render_rail`, `self.pause_button.set_enabled`, `self.pause_button.set_visibility`, `self.progress.props`, `self.progress.set_visibility`, `self.progress_row.set_visibility`, `self.refresh_lists.set_visibility`, `self.resume_button.set_visibility`, `self.scopes_label.set_visibility`, `self.start_button.set_visibility`, `self.trees.classes`, [self.update_scopes](workspace_ui.md#symbol-StorageWorkspace.update_scopes), `str`, `ui.label`, `ui.label(LABELS.get(status, status)).style`, `ui.label(str(number)).classes`, `{'index': 'Подготовка списков', 'names': 'Сопоставление имён', 'hash': 'Прежний отчёт по содержимому', 'done': 'Сверка завершена'}.get`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.render_volumes"></a>

## `StorageWorkspace.render_volumes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.render_volumes`

Перерисовывает активные и архивные тома с группировкой и индикаторами. Использует archived, groups, self.archive.set_visibility, self.archive_list.clear, self.volume_list.clear.

```python
def render_volumes(self)
```

Прямые выражения вызова: [archived](workspace_ui.md#symbol-archived), `bool`, `getattr`, `groups`, `len`, `self.archive.set_visibility`, `self.archive_list.clear`, `self.volume_list.clear`, `sum`, `ui.label`, `ui.label('Нет активных томов.' if self.volumes else 'Пока нет сохранённых томов.').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.render_volumes.groups"></a>

## `StorageWorkspace.render_volumes.groups`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.render_volumes.groups`

Распределяет переданные тома по отображаемым группам NAS и локальных носителей. Использует grouped.setdefault, grouped.setdefault(group['id'], {'details': group, 'volumes': []})['volumes'].append, grouped.values и ещё 2.

```python
def groups(items)
```

Прямые выражения вызова: `bool`, `grouped.setdefault`, `grouped.setdefault(group['id'], {'details': group, 'volumes': []})['volumes'].append`, `grouped.values`, `len`, [self.capacity_text](workspace_ui.md#symbol-StorageWorkspace.capacity_text), [self.property_menu](workspace_ui.md#symbol-StorageWorkspace.property_menu), `sorted`, `str`, `ui.button`, `ui.button(on_click=lambda v=volume: self.open_volume(v['id'])).props`, `ui.button(on_click=lambda v=volume: self.open_volume(v['id'])).props('flat no-caps color=dark').classes`, `ui.column`, `ui.column().classes`, `ui.icon`, `ui.icon('circle', size='7px').classes`, `ui.label`, `ui.label('Сменный').classes`, `ui.label(group['details']['name']).classes`, `ui.label(self.capacity_text(volume)).classes`, `ui.label(str(len(group['volumes']))).classes`, `ui.label(volume['share_name']).classes`, `ui.label(volume_label(volume, False)).classes`, `ui.row`, `ui.row().classes`, `volume.get`, [volume_label](workspace_ui.md#symbol-volume_label).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.render_volumes.groups.volume_actions"></a>

## `StorageWorkspace.render_volumes.groups.volume_actions`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.render_volumes.groups.volume_actions`

Добавляет доступное переименование подтверждённого сменного носителя в меню тома. Использует action, rename.set_enabled, ui.menu_item, v.get.

```python
def volume_actions(action, v=volume)
```

Прямые выражения вызова: `action`, `rename.set_enabled`, `ui.menu_item`, `v.get`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.report_marker"></a>

## `StorageWorkspace.report_marker`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.report_marker`

Получает признаки изменения отчёта для подавления лишних перерисовок. Параметры: report.

```python
def report_marker(report)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `tuple`.

Выражения возврата (ветви, без исполнения):

- `(report['state'], report['phase'], tuple(((s['id'], s['state']) for s in report['scans'])))`


<a id="symbol-StorageWorkspace.resolve_volume"></a>

## `StorageWorkspace.resolve_volume`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.resolve_volume`

Находит файловый или виртуальный том по ID рабочего пространства. Использует next, self.browse_volumes.

```python
def resolve_volume(self, volume_id)
```

Прямые выражения вызова: `next`, [self.browse_volumes](workspace_ui.md#symbol-StorageWorkspace.browse_volumes).

Выражения возврата (ветви, без исполнения):

- `next((v for v in self.browse_volumes() if v['id'] == volume_id), None)`


<a id="symbol-StorageWorkspace.restore_panes"></a>

## `StorageWorkspace.restore_panes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.restore_panes`

Восстанавливает выбранные области и режимы двух независимых панелей. Асинхронно ожидает: pane.load_folder, pane.show_volume, self.read_directory.

```python
async def restore_panes(self, states)
```

Прямые выражения вызова: `PurePosixPath`, `dict`, `folder.startswith`, `pane.expanded.add`, `pane.hidden.set_value`, `pane.load_folder`, `pane.render`, `pane.show_volume`, `relative_path`, `reversed`, [self.is_photos](workspace_ui.md#symbol-StorageWorkspace.is_photos), [self.read_directory](workspace_ui.md#symbol-StorageWorkspace.read_directory), [self.resolve_volume](workspace_ui.md#symbol-StorageWorkspace.resolve_volume), `str`, `zip`.

Выражения возврата (ветви, без исполнения):

- `restored`


<a id="symbol-StorageWorkspace.restore_workspace"></a>

## `StorageWorkspace.restore_workspace`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.restore_workspace`

Восстанавливает вкладку, историю и связанную пару из проверенного снимка состояния. Явно отклоняет недопустимое состояние через ValueError.

```python
async def restore_workspace(self, state)
```

Прямые выражения вызова: `PurePosixPath`, `ValueError`, `dict`, `enumerate`, `group.get`, `job.get`, `match[1].get`, `next`, `pair_state.get`, `saved.get`, `saved_right['path'].startswith`, [self.choose_job](workspace_ui.md#symbol-StorageWorkspace.choose_job), `self.pair.apply`, `self.pair.history`, `self.pair.link`, `self.pair.navigate_path`, `self.pair.restore_view`, `self.panes[0].select`, `self.panes[0].show_volume`, `self.panes[1].comparison.open_folder`, `self.panes[1].comparison.select`, `self.panes[index].set_mode`, `self.request`, [self.restore_panes](workspace_ui.md#symbol-StorageWorkspace.restore_panes), [self.set_active](workspace_ui.md#symbol-StorageWorkspace.set_active), [self.update_scopes](workspace_ui.md#symbol-StorageWorkspace.update_scopes), `state.get`.

Явные `raise`:

- `ValueError('Сохранённая сверка относится к другой паре')`

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-StorageWorkspace.selectable_volumes"></a>

## `StorageWorkspace.selectable_volumes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.selectable_volumes`

Формирует варианты селектора томов с отображаемыми названиями. Использует archived, self.browse_volumes, v.get.

```python
def selectable_volumes(self)
```

Прямые выражения вызова: [archived](workspace_ui.md#symbol-archived), [self.browse_volumes](workspace_ui.md#symbol-StorageWorkspace.browse_volumes), `v.get`.

Выражения возврата (ветви, без исполнения):

- `[v for v in self.browse_volumes() if v.get('availability') != 'offline' and (not archived(v))]`


<a id="symbol-StorageWorkspace.set_active"></a>

## `StorageWorkspace.set_active`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.set_active`

Выбирает активную панель и обновляет связанное управление. Обновляет состояние объекта: active_index.

```python
def set_active(self, index)
```

Присваивания полям `self`: `active_index`.

Прямые выражения вызова: `getattr`, `pane.container.classes`, [self.persist_workspace](workspace_ui.md#symbol-StorageWorkspace.persist_workspace), [self.render_volumes](workspace_ui.md#symbol-StorageWorkspace.render_volumes).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.show_journal"></a>

## `StorageWorkspace.show_journal`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.show_journal`

Показывает события общей сверки с загрузкой предыдущих записей. Обрабатывает ошибки: Exception.

```python
async def show_journal(self)
```

Прямые выражения вызова: `append`, `dialog.open`, `len`, `more.set_visibility`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`, `ui.button`, `ui.button('Закрыть', on_click=dialog.close).props`, `ui.button('Показать более ранние записи', on_click=older).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.label`, `ui.label('Журнал сверки').classes`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.show_journal.append"></a>

## `StorageWorkspace.show_journal.append`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.show_journal.append`

Добавляет события очередной страницы в диалог журнала общей сверки. Использует event.get, self.format_date, ui.label, ui.label(event['path']).classes и ещё 1.

```python
def append(items)
```

Прямые выражения вызова: `event.get`, `self.format_date`, `ui.label`, `ui.label(event['path']).classes`, `ui.label(self.format_date(event['at']) + ' · ' + event['message']).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.show_journal.older"></a>

## `StorageWorkspace.show_journal.older`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.show_journal.older`

Загружает более ранние события общей сверки по сохранённому курсору. Обрабатывает ошибки: Exception.

```python
async def older()
```

Прямые выражения вызова: [append](workspace_ui.md#symbol-StorageWorkspace.show_journal.append), `len`, `more.disable`, `more.enable`, `more.set_visibility`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.show_properties"></a>

## `StorageWorkspace.show_properties`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.show_properties`

Показывает свойства тома, папки или файла и доступные команды. Обрабатывает ошибки: Exception.

```python
async def show_properties(self, volume_id, entry=None)
```

Прямые выражения вызова: `(entry or {}).get`, `FLAGS.items`, `PurePosixPath`, `base.rstrip`, [folder_membership](workspace_ui.md#symbol-folder_membership), `membership.get`, `metadata.get`, `metadata['own'].get`, `next`, [self.edit_folder_tags](workspace_ui.md#symbol-StorageWorkspace.edit_folder_tags), [self.edit_metadata](workspace_ui.md#symbol-StorageWorkspace.edit_metadata), `self.format_bytes`, `self.format_date`, [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), `self.request`, `ui.button`, `ui.button('Закрыть', on_click=lambda: dialog.submit(None)).props`, `ui.button('Изменить отметки', on_click=lambda: dialog.submit('edit')).props`, `ui.button('Метки папки…', on_click=lambda: dialog.submit('tags')).props`, `ui.button('Подключить на M4', icon='lan', on_click=lambda: self.connect(volume['id'])).props`, `ui.card`, `ui.card().classes`, `ui.dialog`, `ui.element`, `ui.element('div').classes`, `ui.label`, `ui.label('ID: ' + volume['marker_id']).classes`, `ui.label('Источник: ' + membership.get('source_label', 'копия')).classes`, `ui.label('Место на томе').classes`, `ui.label('Назначение').classes`, `ui.label('Ресурс NAS: ' + volume['share_name']).classes`, `ui.label('Свойства диска' if not path else 'Свойства папки' if kind == 'directory' else 'Свойства файла').classes`, `ui.label('Служебный файл папки: ' + marker_state).classes`, `ui.label('Сменный носитель').classes`, `ui.label('Унаследовано от /' + membership['path']).classes`, `ui.label('медиатека').classes`, `ui.label('медиатека').classes('s-tag').tooltip`, `ui.label(FOLDER_TAGS[tag]).classes`, `ui.label(PurePosixPath(path).name if path else volume_label(volume)).classes`, `ui.label(base.rstrip('/') + ('/' + path if path else '')).classes`, `ui.label(label).classes`, `ui.label(membership['label']).classes`, `ui.label(membership['marker_error']).classes`, `ui.label(metadata['own']['comment']).classes`, `ui.label(prefix + ': ' + self.format_date(capacity['checked_at'])).classes`, `ui.label(title).classes`, `ui.label(volume['identity_error']).classes`, `ui.row`, `ui.row().classes`, `values.get`, `volume.get`, [volume_label](workspace_ui.md#symbol-volume_label).

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.sidebar_expansion"></a>

## `StorageWorkspace.sidebar_expansion`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.sidebar_expansion`

Создаёт секцию боковой панели с восстановлением её раскрытия. Использует ui.expansion.

```python
def sidebar_expansion(self, key, text, *, icon)
```

Прямые выражения вызова: `ui.expansion`.

Выражения возврата (ветви, без исполнения):

- `ui.expansion(text, icon=icon, value=self.sidebar_state[key], on_value_change=changed)`


<a id="symbol-StorageWorkspace.sidebar_expansion.changed"></a>

## `StorageWorkspace.sidebar_expansion.changed`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.sidebar_expansion.changed`

Сохраняет актуальное раскрытие секции боковой панели в браузерном хранилище. Использует normalize_sidebar, self.sidebar_storage.get.

```python
def changed(event)
```

Прямые выражения вызова: `normalize_sidebar`, `self.sidebar_storage.get`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-StorageWorkspace.size_texts"></a>

## `StorageWorkspace.size_texts`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.size_texts`

Собирает форматированные размеры всех известных папок выбранного тома. Использует self.directory_size_text, self.directory_sizes.get.

```python
def size_texts(self, volume_id)
```

Прямые выражения вызова: [self.directory_size_text](workspace_ui.md#symbol-StorageWorkspace.directory_size_text), `self.directory_sizes.get`.

Выражения возврата (ветви, без исполнения):

- `{path: self.directory_size_text(volume_id, path) for path in self.directory_sizes.get(volume_id, {})}`


<a id="symbol-StorageWorkspace.start_comparison"></a>

## `StorageWorkspace.start_comparison`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.start_comparison`

Создаёт поиск имён по выбранным областям через API Core. Обрабатывает ошибки: Exception.

```python
async def start_comparison(self)
```

Прямые выражения вызова: `bool`, `p.scope`, [self.apply_report](workspace_ui.md#symbol-StorageWorkspace.apply_report), [self.notice](workspace_ui.md#symbol-StorageWorkspace.notice), [self.refresh_history](workspace_ui.md#symbol-StorageWorkspace.refresh_history), `self.request`, `self.start_button.disable`, [self.update_scopes](workspace_ui.md#symbol-StorageWorkspace.update_scopes), `ui.notify`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.update_scopes"></a>

## `StorageWorkspace.update_scopes`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.update_scopes`

Пересчитывает выбранные области и доступность действий сверки и копирования. Использует ', '.join, labels.append, next, pane.scope, scope_label.

```python
def update_scopes(self)
```

Прямые выражения вызова: `', '.join`, `bool`, `labels.append`, `next`, `pane.scope`, `scope_label`, `self.copies.render_controls`, `self.copies.render_sidebar`, [self.persist_workspace](workspace_ui.md#symbol-StorageWorkspace.persist_workspace), `self.start_button.disable`, `self.start_button.set_enabled`, [volume_label](workspace_ui.md#symbol-volume_label).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.update_scopes.scope_label"></a>

## `StorageWorkspace.update_scopes.scope_label`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.update_scopes.scope_label`

Формирует подпись выбранной области из названия тома и относительного пути. Использует next, volume_label.

```python
def scope_label(scan)
```

Прямые выражения вызова: `next`, [volume_label](workspace_ui.md#symbol-volume_label).

Выражения возврата (ветви, без исполнения):

- `name + ' /' + scan['root_path']`


<a id="symbol-StorageWorkspace.update_size_labels"></a>

## `StorageWorkspace.update_size_labels`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.update_size_labels`

Обновляет уже созданные подписи размеров без перестроения деревьев. Использует pane.size_cells.items, pane.size_cells.pop, pane.update_size_header, self.directory_size_text, self.pair.views.items.

```python
def update_size_labels(self)
```

Прямые выражения вызова: `list`, `pane.size_cells.items`, `pane.size_cells.pop`, `pane.update_size_header`, [self.directory_size_text](workspace_ui.md#symbol-StorageWorkspace.directory_size_text), `self.pair.views.items`, [self.size_texts](workspace_ui.md#symbol-StorageWorkspace.size_texts), `view.update`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-StorageWorkspace.workspace_snapshot"></a>

## `StorageWorkspace.workspace_snapshot`

[workspace_ui.py](../../workspace_ui.py) · `StorageWorkspace.workspace_snapshot`

Собирает компактное состояние навигации двух панелей и открытой сверки. Использует pair.relative, pane_snapshot.

```python
def workspace_snapshot(self)
```

Прямые выражения вызова: `bool`, `dict`, `pair.relative`, `pane_snapshot`.

Выражения возврата (ветви, без исполнения):

- `state`


<a id="symbol-archived"></a>

## `archived`

[workspace_ui.py](../../workspace_ui.py) · `archived`

Определяет, должен ли недоступный том отображаться в архиве. Использует volume.get.

```python
def archived(volume)
```

Прямые выражения вызова: `volume.get`.

Выражения возврата (ветви, без исполнения):

- `not volume.get('mounted') and (volume['availability'] == 'offline' or volume.get('identity_status') == 'legacy')`


<a id="symbol-folder_membership"></a>

## `folder_membership`

[workspace_ui.py](../../workspace_ui.py) · `folder_membership`

Определяет принадлежность пути обычной копии или копии медиатеки. Использует libraries.copy_membership, workspace.copies.membership.

```python
def folder_membership(workspace, volume_id, path)
```

Прямые выражения вызова: `getattr`, `libraries.copy_membership`, `workspace.copies.membership`.

Выражения возврата (ветви, без исполнения):

- `photo_copy or workspace.copies.membership(volume_id, path)`


<a id="symbol-register_workspace_page"></a>

## `register_workspace_page`

[workspace_ui.py](../../workspace_ui.py) · `register_workspace_page`

Регистрирует главную страницу с параметрами совместимости старых ссылок. Параметры: request, format_bytes, format_date, core_url.

```python
def register_workspace_page(request, format_bytes, format_date, core_url='http://127.0.0.1:18765')
```

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-register_workspace_page.workspace_page"></a>

## `register_workspace_page.workspace_page`

[workspace_ui.py](../../workspace_ui.py) · `register_workspace_page.workspace_page`

Создаёт рабочее пространство для клиента и загружает его начальное состояние. Асинхронно ожидает: workspace.load.

```python
async def workspace_page(source: str='', path: str='', job: str='')
```

Декораторы: `ui.page('/', reconnect_timeout=120)`.

Прямые выражения вызова: [StorageWorkspace](workspace_ui.md#symbol-StorageWorkspace), `callable`, `core_url`, `workspace.load`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-volume_label"></a>

## `volume_label`

[workspace_ui.py](../../workspace_ui.py) · `volume_label`

Формирует подпись тома с необязательным именем сетевого ресурса. Использует name.casefold, share.casefold, volume.get.

```python
def volume_label(volume, with_share=True)
```

Прямые выражения вызова: `name.casefold`, `share.casefold`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `f'{name} · {share}'`
- `name`
