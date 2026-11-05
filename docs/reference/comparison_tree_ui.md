# UI найденных путей: `comparison_tree_ui.py`

Правое дерево совпадений общей сверки. Использует сохранённые индексы целей, а не живой обход NAS при раскрытии результата.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../comparison_tree_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [storage_ui.py](storage_ui.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_comparison_tree_ui.py](tests.md#module-tests.test_comparison_tree_ui), [tests/test_tree_keyboard.py](tests.md#module-tests.test_tree_keyboard).

## Оглавление определений

- [ComparisonTree](#symbol-ComparisonTree) — Показывает найденные пути общей сверки в правой панели.
- [ComparisonTree.__init__](#symbol-ComparisonTree.__init__) — Инициализирует ComparisonTree и его рабочее состояние.
- [ComparisonTree.load](#symbol-ComparisonTree.load) — Получает страницу дочерних элементов из сохранённого индекса цели.
- [ComparisonTree.more](#symbol-ComparisonTree.more) — Догружает следующую страницу дочерних элементов сохранённого дерева.
- [ComparisonTree.open_folder](#symbol-ComparisonTree.open_folder) — Делает выбранную папку корнем отображаемого дерева совпадений.
- [ComparisonTree.open_path](#symbol-ComparisonTree.open_path) — Открывает найденный путь в контексте соответствующей цели отчёта.
- [ComparisonTree.render](#symbol-ComparisonTree.render) — Перерисовывает раскрытые ветви сохранённого дерева совпадений.
- [ComparisonTree.render.branch](#symbol-ComparisonTree.render.branch) — Рекурсивно рисует загруженные дочерние ветви совпадения.
- [ComparisonTree.render.node](#symbol-ComparisonTree.render.node) — Рисует один узел совпадения с командами выбора, открытия и свойств.
- [ComparisonTree.reset](#symbol-ComparisonTree.reset) — Сбрасывает найденные ветви и контекст выбранного исходного элемента.
- [ComparisonTree.select](#symbol-ComparisonTree.select) — Выбирает найденный элемент и при необходимости загружает или раскрывает ветвь.
- [ComparisonTree.set_matches](#symbol-ComparisonTree.set_matches) — Применяет найденные пути и контекст с ограничением отображаемых корней.
- [ComparisonTree.show_matches](#symbol-ComparisonTree.show_matches) — Переключает правую панель к дереву найденных совпадений.
- [ComparisonTree.update_header](#symbol-ComparisonTree.update_header) — Обновляет заголовок и путь панели найденных совпадений.

<a id="symbol-ComparisonTree"></a>

## `ComparisonTree`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree`

Показывает найденные пути общей сверки в правой панели. Зависимости конструктора: pane.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `context`, `expanded`, `focus`, `folders`, `generation`, `limit`, `pane`, `roots`, `selected`, `workspace`.

Именованные методы: `__init__`, `reset`, `show_matches`, `set_matches`, `update_header`, `render`, `load`, `open_path`, `open_folder`, `select`, `more`.

<a id="symbol-ComparisonTree.__init__"></a>

## `ComparisonTree.__init__`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.__init__`

Инициализирует ComparisonTree и его рабочее состояние. Обновляет состояние объекта: context, expanded, focus, folders, generation, limit, pane, roots, selected, workspace.

```python
def __init__(self, pane)
```

Присваивания полям `self`: `context`, `expanded`, `focus`, `folders`, `generation`, `limit`, `pane`, `roots`, `selected`, `workspace`.

Прямые выражения вызова: `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.load"></a>

## `ComparisonTree.load`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.load`

Получает страницу дочерних элементов из сохранённого индекса цели. Обрабатывает ошибки: Exception.

```python
async def load(self, entry, *, more=False)
```

Прямые выражения вызова: `len`, `self.folders.get`, `self.folders.get(key, {}).get`, `self.workspace.error_text`, `self.workspace.request`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-ComparisonTree.more"></a>

## `ComparisonTree.more`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.more`

Догружает следующую страницу дочерних элементов сохранённого дерева. Асинхронно ожидает: self.load.

```python
async def more(self, entry)
```

Прямые выражения вызова: [self.load](comparison_tree_ui.md#symbol-ComparisonTree.load), `self.pane.render`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.open_folder"></a>

## `ComparisonTree.open_folder`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.open_folder`

Делает выбранную папку корнем отображаемого дерева совпадений. Обновляет состояние объекта: focus.

```python
async def open_folder(self, entry, scope)
```

Присваивания полям `self`: `focus`.

Прямые выражения вызова: `entry['path'].startswith`, `self.pane.render`, [self.select](comparison_tree_ui.md#symbol-ComparisonTree.select).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ComparisonTree.open_path"></a>

## `ComparisonTree.open_path`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.open_path`

Открывает найденный путь в контексте соответствующей цели отчёта. Асинхронно ожидает: self.open_folder, self.workspace.open_volume.

```python
async def open_path(self, path)
```

Прямые выражения вызова: `PurePosixPath`, `path.startswith`, [self.open_folder](comparison_tree_ui.md#symbol-ComparisonTree.open_folder), `self.workspace.open_volume`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ComparisonTree.render"></a>

## `ComparisonTree.render`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.render`

Перерисовывает раскрытые ветви сохранённого дерева совпадений. Использует branch, count, node, ui.label, ui.label(f'Показаны первые {self.limit} найденных путей.').classes.

```python
def render(self)
```

Прямые выражения вызова: `branch`, `count`, `len`, `node`, `ui.label`, `ui.label(f'Показаны первые {self.limit} найденных путей.').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.render.branch"></a>

## `ComparisonTree.render.branch`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.render.branch`

Рекурсивно рисует загруженные дочерние ветви совпадения. Использует child['name'].startswith, data.get, node, self.folders.get, ui.button.

```python
def branch(entry, scope, depth=0)
```

Прямые выражения вызова: `child['name'].startswith`, `data.get`, `len`, [node](comparison_tree_ui.md#symbol-ComparisonTree.render.node), `self.folders.get`, `ui.button`, `ui.button('Показать ещё…', on_click=lambda e=entry: self.more(e)).props`, `ui.button('Показать ещё…', on_click=lambda e=entry: self.more(e)).props('flat dense no-caps color=dark').style`, `ui.label`, `ui.label('Папка пуста').classes`, `ui.label('Папка пуста').classes('s-muted text-xs py-1').style`, `ui.label(data['error']).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.render.node"></a>

## `ComparisonTree.render.node`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.render.node`

Рисует один узел совпадения с командами выбора, открытия и свойств. Использует PurePosixPath, branch, entry.get, folder_icon, json.dumps.

```python
def node(entry, scope, depth=0, root=False)
```

Прямые выражения вызова: `PurePosixPath`, `bool`, [branch](comparison_tree_ui.md#symbol-ComparisonTree.render.branch), `entry.get`, `folder_icon`, `json.dumps`, `next`, `self.pane.register_navigation`, `self.workspace.copies.membership`, `self.workspace.directory_size_text`, `self.workspace.format_bytes`, `self.workspace.property_menu`, `str`, `ui.button`, `ui.button(entry['name'], on_click=None if directory else lambda e=entry, s=scope: self.select(e, s)).props`, `ui.button(entry['name'], on_click=None if directory else lambda e=entry, s=scope: self.select(e, s)).props('flat dense no-caps color=dark').classes`, `ui.button(icon='expand_more' if key in self.expanded else 'chevron_right', on_click=lambda e=entry, s=scope: self.select(e, s)).props`, `ui.button(icon='expand_more' if key in self.expanded else 'chevron_right', on_click=lambda e=entry, s=scope: self.select(e, s)).props('flat dense color=grey-7 aria-label="Раскрыть найденную папку"').classes`, `ui.element`, `ui.element('div').classes`, `ui.element('div').classes(classes).style`, `ui.element('span').classes`, `ui.icon`, `ui.icon('error_outline', size='13px').classes`, `ui.icon('insert_drive_file' if entry['kind'] == 'file' else 'link', size='14px').classes`, `ui.label`, `ui.label(membership['label']).classes`, `ui.label(scope['volume_name'] + ' /' + ('' if parent == '.' else parent)).classes`, `ui.label(self.workspace.directory_size_text(scope['volume_id'], entry['path'])).classes`, `ui.label(self.workspace.format_bytes(entry['size'])).classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.reset"></a>

## `ComparisonTree.reset`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.reset`

Сбрасывает найденные ветви и контекст выбранного исходного элемента. Обновляет состояние объекта: context, focus, generation, roots, selected.

```python
def reset(self, context=None)
```

Присваивания полям `self`: `context`, `focus`, `generation`, `roots`, `selected`.

Прямые выражения вызова: `self.expanded.clear`, `self.folders.clear`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.select"></a>

## `ComparisonTree.select`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.select`

Выбирает найденный элемент и при необходимости загружает или раскрывает ветвь. Обновляет состояние объекта: selected.

```python
async def select(self, entry, scope, *, expand=False, toggle=True, render=True)
```

Присваивания полям `self`: `selected`.

Прямые выражения вызова: `next`, `pane.render`, `pane.update_header`, `pane.update_navigation_selection`, `self.expanded.add`, `self.expanded.remove`, [self.load](comparison_tree_ui.md#symbol-ComparisonTree.load), `self.workspace.preview_selection`, `self.workspace.render_volumes`, `self.workspace.set_active`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-ComparisonTree.set_matches"></a>

## `ComparisonTree.set_matches`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.set_matches`

Применяет найденные пути и контекст с ограничением отображаемых корней. Обновляет состояние объекта: limit, roots.

```python
def set_matches(self, matches, context, limit=100)
```

Присваивания полям `self`: `limit`, `roots`.

Прямые выражения вызова: `self.pane.render`, [self.reset](comparison_tree_ui.md#symbol-ComparisonTree.reset).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.show_matches"></a>

## `ComparisonTree.show_matches`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.show_matches`

Переключает правую панель к дереву найденных совпадений. Обновляет состояние объекта: focus, selected.

```python
def show_matches(self)
```

Присваивания полям `self`: `focus`, `selected`.

Прямые выражения вызова: `self.pane.render`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonTree.update_header"></a>

## `ComparisonTree.update_header`

[comparison_tree_ui.py](../../comparison_tree_ui.py) · `ComparisonTree.update_header`

Обновляет заголовок и путь панели найденных совпадений. Использует pane.location.set_visibility, pane.path_bar.clear, pane.render_path, pane.toolbar.set_visibility, self.roots[0].get.

```python
def update_header(self)
```

Прямые выражения вызова: `bool`, `len`, `pane.location.set_visibility`, `pane.path_bar.clear`, `pane.render_path`, `pane.toolbar.set_visibility`, `self.roots[0].get`, `self.workspace.format_date`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
