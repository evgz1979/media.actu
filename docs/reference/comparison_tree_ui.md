# UI найденных путей: `comparison_tree_ui.py`

Правое дерево совпадений общей сверки. Использует сохранённые индексы целей, а не живой обход NAS при раскрытии результата.

[Исходный модуль](../../comparison_tree_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [storage_ui.py](storage_ui.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_comparison_tree_ui.py](../../tests/test_comparison_tree_ui.py#L6), [tests/test_tree_keyboard.py](../../tests/test_tree_keyboard.py#L10).

## Оглавление определений

- [ComparisonTree](#symbol-comparisontree) — Показывает найденные пути общей сверки в правой панели.
- [ComparisonTree.__init__](#symbol-comparisontree---init--) — Инициализирует ComparisonTree и его рабочее состояние.
- [ComparisonTree.reset](#symbol-comparisontree-reset) — Сбрасывает найденные ветви и контекст выбранного исходного элемента.
- [ComparisonTree.show_matches](#symbol-comparisontree-show-matches) — Переключает правую панель к дереву найденных совпадений.
- [ComparisonTree.set_matches](#symbol-comparisontree-set-matches) — Применяет найденные пути и контекст с ограничением отображаемых корней.
- [ComparisonTree.update_header](#symbol-comparisontree-update-header) — Обновляет заголовок и путь панели найденных совпадений.
- [ComparisonTree.render](#symbol-comparisontree-render) — Перерисовывает раскрытые ветви сохранённого дерева совпадений.
- [ComparisonTree.render.node](#symbol-comparisontree-render-node) — Рисует один узел совпадения с командами выбора, открытия и свойств.
- [ComparisonTree.render.branch](#symbol-comparisontree-render-branch) — Рекурсивно рисует загруженные дочерние ветви совпадения.
- [ComparisonTree.load](#symbol-comparisontree-load) — Получает страницу дочерних элементов из сохранённого индекса цели.
- [ComparisonTree.open_path](#symbol-comparisontree-open-path) — Открывает найденный путь в контексте соответствующей цели отчёта.
- [ComparisonTree.open_folder](#symbol-comparisontree-open-folder) — Делает выбранную папку корнем отображаемого дерева совпадений.
- [ComparisonTree.select](#symbol-comparisontree-select) — Выбирает найденный элемент и при необходимости загружает или раскрывает ветвь.
- [ComparisonTree.more](#symbol-comparisontree-more) — Догружает следующую страницу дочерних элементов сохранённого дерева.

<a id="symbol-comparisontree"></a>

## `ComparisonTree`

[comparison_tree_ui.py:15](../../comparison_tree_ui.py#L15)

Показывает найденные пути общей сверки в правой панели. Зависимости конструктора: pane.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `context`, `expanded`, `focus`, `folders`, `generation`, `limit`, `pane`, `roots`, `selected`, `workspace`.

Именованные методы: `__init__`, `reset`, `show_matches`, `set_matches`, `update_header`, `render`, `load`, `open_path`, `open_folder`, `select`, `more`.

<a id="symbol-comparisontree---init--"></a>

## `ComparisonTree.__init__`

[comparison_tree_ui.py:18](../../comparison_tree_ui.py#L18)

Инициализирует ComparisonTree и его рабочее состояние. Обновляет состояние объекта: context, expanded, focus, folders, generation, limit, pane, roots, selected, workspace.

```python
def __init__(self, pane)
```

Присваивания полям `self`: `context`, `expanded`, `focus`, `folders`, `generation`, `limit`, `pane`, `roots`, `selected`, `workspace`.

Прямые выражения вызова: `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-reset"></a>

## `ComparisonTree.reset`

[comparison_tree_ui.py:32](../../comparison_tree_ui.py#L32)

Сбрасывает найденные ветви и контекст выбранного исходного элемента. Обновляет состояние объекта: context, focus, generation, roots, selected.

```python
def reset(self, context=None)
```

Присваивания полям `self`: `context`, `focus`, `generation`, `roots`, `selected`.

Прямые выражения вызова: `self.expanded.clear`, `self.folders.clear`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-show-matches"></a>

## `ComparisonTree.show_matches`

[comparison_tree_ui.py:43](../../comparison_tree_ui.py#L43)

Переключает правую панель к дереву найденных совпадений. Обновляет состояние объекта: focus, selected.

```python
def show_matches(self)
```

Присваивания полям `self`: `focus`, `selected`.

Прямые выражения вызова: `self.pane.render`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-set-matches"></a>

## `ComparisonTree.set_matches`

[comparison_tree_ui.py:49](../../comparison_tree_ui.py#L49)

Применяет найденные пути и контекст с ограничением отображаемых корней. Обновляет состояние объекта: limit, roots.

```python
def set_matches(self, matches, context, limit=100)
```

Присваивания полям `self`: `limit`, `roots`.

Прямые выражения вызова: `self.pane.render`, [self.reset](../../comparison_tree_ui.py#L32).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-update-header"></a>

## `ComparisonTree.update_header`

[comparison_tree_ui.py:58](../../comparison_tree_ui.py#L58)

Обновляет заголовок и путь панели найденных совпадений. Использует pane.location.set_visibility, pane.path_bar.clear, pane.render_path, pane.toolbar.set_visibility, self.roots[0].get.

```python
def update_header(self)
```

Прямые выражения вызова: `bool`, `len`, `pane.location.set_visibility`, `pane.path_bar.clear`, `pane.render_path`, `pane.toolbar.set_visibility`, `self.roots[0].get`, `self.workspace.format_date`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-render"></a>

## `ComparisonTree.render`

[comparison_tree_ui.py:75](../../comparison_tree_ui.py#L75)

Перерисовывает раскрытые ветви сохранённого дерева совпадений. Использует branch, count, node, ui.label, ui.label(f'Показаны первые {self.limit} найденных путей.').classes.

```python
def render(self)
```

Прямые выражения вызова: `branch`, `count`, `len`, `node`, `ui.label`, `ui.label(f'Показаны первые {self.limit} найденных путей.').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-render-node"></a>

## `ComparisonTree.render.node`

[comparison_tree_ui.py:80](../../comparison_tree_ui.py#L80)

Рисует один узел совпадения с командами выбора, открытия и свойств. Использует PurePosixPath, branch, entry.get, folder_icon, json.dumps.

```python
def node(entry, scope, depth=0, root=False)
```

Прямые выражения вызова: `PurePosixPath`, `bool`, [branch](../../comparison_tree_ui.py#L120), `entry.get`, `folder_icon`, `json.dumps`, `next`, `self.pane.register_navigation`, `self.workspace.copies.membership`, `self.workspace.directory_size_text`, `self.workspace.format_bytes`, `self.workspace.property_menu`, `str`, `ui.button`, `ui.button(entry['name'], on_click=None if directory else lambda e=entry, s=scope: self.select(e, s)).props`, `ui.button(entry['name'], on_click=None if directory else lambda e=entry, s=scope: self.select(e, s)).props('flat dense no-caps color=dark').classes`, `ui.button(icon='expand_more' if key in self.expanded else 'chevron_right', on_click=lambda e=entry, s=scope: self.select(e, s)).props`, `ui.button(icon='expand_more' if key in self.expanded else 'chevron_right', on_click=lambda e=entry, s=scope: self.select(e, s)).props('flat dense color=grey-7 aria-label="Раскрыть найденную папку"').classes`, `ui.element`, `ui.element('div').classes`, `ui.element('div').classes(classes).style`, `ui.element('span').classes`, `ui.icon`, `ui.icon('error_outline', size='13px').classes`, `ui.icon('insert_drive_file' if entry['kind'] == 'file' else 'link', size='14px').classes`, `ui.label`, `ui.label(membership['label']).classes`, `ui.label(scope['volume_name'] + ' /' + ('' if parent == '.' else parent)).classes`, `ui.label(self.workspace.directory_size_text(scope['volume_id'], entry['path'])).classes`, `ui.label(self.workspace.format_bytes(entry['size'])).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-render-branch"></a>

## `ComparisonTree.render.branch`

[comparison_tree_ui.py:120](../../comparison_tree_ui.py#L120)

Рекурсивно рисует загруженные дочерние ветви совпадения. Использует child['name'].startswith, data.get, node, self.folders.get, ui.button.

```python
def branch(entry, scope, depth=0)
```

Прямые выражения вызова: `child['name'].startswith`, `data.get`, `len`, [node](../../comparison_tree_ui.py#L80), `self.folders.get`, `ui.button`, `ui.button('Показать ещё…', on_click=lambda e=entry: self.more(e)).props`, `ui.button('Показать ещё…', on_click=lambda e=entry: self.more(e)).props('flat dense no-caps color=dark').style`, `ui.label`, `ui.label('Папка пуста').classes`, `ui.label('Папка пуста').classes('s-muted text-xs py-1').style`, `ui.label(data['error']).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisontree-load"></a>

## `ComparisonTree.load`

[comparison_tree_ui.py:143](../../comparison_tree_ui.py#L143)

Получает страницу дочерних элементов из сохранённого индекса цели. Обрабатывает ошибки: Exception.

```python
async def load(self, entry, *, more=False)
```

Прямые выражения вызова: `len`, `self.folders.get`, `self.folders.get(key, {}).get`, `self.workspace.error_text`, `self.workspace.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-comparisontree-open-path"></a>

## `ComparisonTree.open_path`

[comparison_tree_ui.py:162](../../comparison_tree_ui.py#L162)

Открывает найденный путь в контексте соответствующей цели отчёта. Асинхронно ожидает: self.open_folder, self.workspace.open_volume.

```python
async def open_path(self, path)
```

Прямые выражения вызова: `PurePosixPath`, `path.startswith`, [self.open_folder](../../comparison_tree_ui.py#L176), `self.workspace.open_volume`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-comparisontree-open-folder"></a>

## `ComparisonTree.open_folder`

[comparison_tree_ui.py:176](../../comparison_tree_ui.py#L176)

Делает выбранную папку корнем отображаемого дерева совпадений. Обновляет состояние объекта: focus.

```python
async def open_folder(self, entry, scope)
```

Присваивания полям `self`: `focus`.

Прямые выражения вызова: `entry['path'].startswith`, `self.pane.render`, [self.select](../../comparison_tree_ui.py#L190).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-comparisontree-select"></a>

## `ComparisonTree.select`

[comparison_tree_ui.py:190](../../comparison_tree_ui.py#L190)

Выбирает найденный элемент и при необходимости загружает или раскрывает ветвь. Обновляет состояние объекта: selected.

```python
async def select(self, entry, scope, *, expand=False, toggle=True, render=True)
```

Присваивания полям `self`: `selected`.

Прямые выражения вызова: `next`, `pane.render`, `pane.update_header`, `pane.update_navigation_selection`, `self.expanded.add`, `self.expanded.remove`, [self.load](../../comparison_tree_ui.py#L143), `self.workspace.preview_selection`, `self.workspace.render_volumes`, `self.workspace.set_active`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-comparisontree-more"></a>

## `ComparisonTree.more`

[comparison_tree_ui.py:218](../../comparison_tree_ui.py#L218)

Догружает следующую страницу дочерних элементов сохранённого дерева. Асинхронно ожидает: self.load.

```python
async def more(self, entry)
```

Прямые выражения вызова: [self.load](../../comparison_tree_ui.py#L143), `self.pane.render`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
