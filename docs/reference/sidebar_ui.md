# Строки и меню боковой колонки: `sidebar_ui.py`

Общие компактные заголовки, строки, контекстные меню и переключатели раскрытия для томов, источников, основных папок и архивных записей.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../sidebar_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [copy_groups_ui.py](copy_groups_ui.md), [photo_libraries_ui.py](photo_libraries_ui.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [sidebar_branch](#symbol-sidebar_branch) — Рисует заголовок и раскрываемые под ним копии в общей боковой колонке.
- [sidebar_branch.change](#symbol-sidebar_branch.change) — Переключает видимость копий без пересборки строк источника.
- [sidebar_branch.control](#symbol-sidebar_branch.control) — Создаёт кнопку раскрытия в общей позиции значка строки.
- [sidebar_branch.update](#symbol-sidebar_branch.update) — Отображает актуальный значок и доступное имя переключателя копий.
- [sidebar_line](#symbol-sidebar_line) — Создаёт компактную строку с общими отступами и подсказкой полного названия.
- [sidebar_menu](#symbol-sidebar_menu) — Показывает одно и то же меню по кнопке команд и по правому клику на строке.

## Константы и значения по умолчанию

<a id="constant-SIDEBAR_CSS"></a>

### `SIDEBAR_CSS`

`Объёмное значение см. в исходном модуле`


<a id="symbol-sidebar_branch"></a>

## `sidebar_branch`

[sidebar_ui.py](../../sidebar_ui.py) · `sidebar_branch`

Рисует заголовок и раскрываемые под ним копии в общей боковой колонке. Сохраняет раскрытие и показывает короткий маршрут в свёрнутом виде.

```python
def sidebar_branch(expanded, key, copies, header, *, summary='')
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `children.set_visibility`, `header`, `route.set_visibility`, `route.tooltip`, `ui.button`, `ui.button(summary, icon='account_tree', on_click=change).props`, `ui.button(summary, icon='account_tree', on_click=change).props('flat dense no-caps').classes`, `ui.column`, `ui.column().classes`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-sidebar_branch.change"></a>

## `sidebar_branch.change`

[sidebar_ui.py](../../sidebar_ui.py) · `sidebar_branch.change`

Переключает видимость копий без пересборки строк источника. Меняет набор раскрытых ключей.

```python
def change()
```

Прямые выражения вызова: `children.set_visibility`, `expanded.add`, `expanded.remove`, `route.set_visibility`, [update](sidebar_ui.md#symbol-sidebar_branch.update).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sidebar_branch.control"></a>

## `sidebar_branch.control`

[sidebar_ui.py](../../sidebar_ui.py) · `sidebar_branch.control`

Создаёт кнопку раскрытия в общей позиции значка строки. Использует update для начальной подписи SVG и доступного имени.

```python
def control()
```

Прямые выражения вызова: `ui.button`, `ui.button(color=None, on_click=change).props`, `ui.button(color=None, on_click=change).props('flat dense size=sm').classes`, [update](sidebar_ui.md#symbol-sidebar_branch.update).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sidebar_branch.update"></a>

## `sidebar_branch.update`

[sidebar_ui.py](../../sidebar_ui.py) · `sidebar_branch.update`

Отображает актуальный значок и доступное имя переключателя копий. Использует состояние раскрытия по ключу.

```python
def update()
```

Прямые выражения вызова: `str`, `str(opened).lower`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sidebar_line"></a>

## `sidebar_line`

[sidebar_ui.py](../../sidebar_ui.py) · `sidebar_line`

Создаёт компактную строку с общими отступами и подсказкой полного названия. В контексте строки размещаются статус и необязательное меню действий.

```python
def sidebar_line(name, on_open, *, tooltip=None, icon=None, icon_color='', toggle=None, chosen=False, offline=False, indented=False, depth=0, origin='')
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `' '.join`, `button.tooltip`, `line.classes`, `line.classes('copy-dependent').style`, `min`, `toggle`, `ui.button`, `ui.button(name, color=None, on_click=on_open).props`, `ui.button(name, color=None, on_click=on_open).props('flat dense no-caps align=left').classes`, `ui.column`, `ui.column().classes`, `ui.element`, `ui.element('span').classes`, `ui.icon`, `ui.icon('subdirectory_arrow_right', size='11px').classes`, `ui.icon(icon, size='13px').classes`, `ui.label`, `ui.label(origin).classes`, `ui.row`, `ui.row().classes`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-sidebar_menu"></a>

## `sidebar_menu`

[sidebar_ui.py](../../sidebar_ui.py) · `sidebar_menu`

Показывает одно и то же меню по кнопке команд и по правому клику на строке. Возвращает контейнер для пунктов меню.

```python
def sidebar_menu(row)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `row.on`, `ui.button`, `ui.button(icon='more_horiz', color=None).props`, `ui.menu`, `ui.menu().props`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.
