# Общие роли панелей копирования: `copy_panels.py`

Выбирает первую доступную копию, сопоставляет пути с привязанными областями и форматирует подписи источника и назначения.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../copy_panels.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [copy_groups_ui.py](copy_groups_ui.md), [paired_workspace_ui.py](paired_workspace_ui.md), [photo_libraries_ui.py](photo_libraries_ui.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_workspace_photos.py](tests.md#module-tests.test_workspace_photos).

## Оглавление определений

- [contains_path](#symbol-contains_path) — Проверяет принадлежность выбранного пути области на томе.
- [copy_heading](#symbol-copy_heading) — Формирует подпись источника, действующей копии или архивного назначения.
- [disconnected](#symbol-disconnected) — Проверяет доступность привязанной папки по состоянию связи и тома.
- [first_copy](#symbol-first_copy) — Выбирает копию с наименьшим номером среди доступных.

<a id="symbol-contains_path"></a>

## `contains_path`

[copy_panels.py](../../copy_panels.py) · `contains_path`

Проверяет принадлежность выбранного пути области на томе. Сравнивает компоненты пути, включая пустой корень.

```python
def contains_path(scope, volume_id, path)
```

Прямые выражения вызова: `PurePosixPath`, `PurePosixPath(path).is_relative_to`.

Выражения возврата (ветви, без исполнения):

- `scope['volume_id'] == volume_id and PurePosixPath(path).is_relative_to(scope['path'])`


<a id="symbol-copy_heading"></a>

## `copy_heading`

[copy_panels.py](../../copy_panels.py) · `copy_heading`

Формирует подпись источника, действующей копии или архивного назначения. Для копии может дописать сохранённое предыдущее звено маршрута.

```python
def copy_heading(scope, *, target=False, historical=False)
```

Прямые выражения вызова: `scope.get`.

Выражения возврата (ветви, без исполнения):

- `f'{label} (источник копирования)'`
- `f'Прежняя {label}'`
- `f"{label} (копия №{scope['number']}){suffix}"`


<a id="symbol-disconnected"></a>

## `disconnected`

[copy_panels.py](../../copy_panels.py) · `disconnected`

Проверяет доступность привязанной папки по состоянию связи и тома. Используется для выбора пары и отображения отключённых записей.

```python
def disconnected(location)
```

Прямые выражения вызова: `location.get`.

Выражения возврата (ветви, без исполнения):

- `not location.get('connected', True) or location.get('availability') == 'offline'`


<a id="symbol-first_copy"></a>

## `first_copy`

[copy_panels.py](../../copy_panels.py) · `first_copy`

Выбирает копию с наименьшим номером среди доступных. При недоступности всех назначений возвращает первую сохранённую связь.

```python
def first_copy(copies)
```

Прямые выражения вызова: `min`.

Выражения возврата (ветви, без исполнения):

- `min(copies, key=lambda copy: (disconnected(copy), copy['number']), default=None)`
