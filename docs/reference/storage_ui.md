# Общие элементы и регистрация UI: `storage_ui.py`

Сохраняет общие CSS, SVG-иконку папки, обработчик двойного клика и регистрацию главной через workspace_ui. Имя модуля историческое, текущие импорты действуют.

[Исходный модуль](../../storage_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [workspace_ui.py](workspace_ui.md).
Импортируется модулями: [comparison_tree_ui.py](comparison_tree_ui.md), [ui.py](ui.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: нет; возможна косвенная проверка через вызывающие компоненты.

## Оглавление определений

- [folder_icon](#symbol-folder-icon) — Создаёт SVG-иконку папки с уникальным ID градиента.
- [register_storage_page](#symbol-register-storage-page) — Передаёт регистрацию главной страницы действующему рабочему пространству.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [FOLDER_ICON_IDS](../../storage_ui.py#L10) | `count()` |

<a id="symbol-folder-icon"></a>

## `folder_icon`

[storage_ui.py:30](../../storage_ui.py#L30)

Создаёт SVG-иконку папки с уникальным ID градиента. Использует next, ui.html, ui.html(svg, sanitize=False).classes, ui.html(svg, sanitize=False).classes('s-folder-icon').style.

```python
def folder_icon(size=16)
```

Прямые выражения вызова: `next`, `ui.html`, `ui.html(svg, sanitize=False).classes`, `ui.html(svg, sanitize=False).classes('s-folder-icon').style`.

Выражения возврата (ветви, без исполнения):

- `ui.html(svg, sanitize=False).classes('s-folder-icon').style(f'width:{size}px;height:{size}px')`


<a id="symbol-register-storage-page"></a>

## `register_storage_page`

[storage_ui.py:111](../../storage_ui.py#L111)

Передаёт регистрацию главной страницы действующему рабочему пространству. Использует register_workspace_page.

```python
def register_storage_page(request, format_bytes, format_date, core_url='http://127.0.0.1:18765')
```

Прямые выражения вызова: `register_workspace_page`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
