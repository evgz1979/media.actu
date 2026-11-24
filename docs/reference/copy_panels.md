# Маршруты и роли панелей копирования: `copy_panels.py`

Выбирает первую доступную копию, строит маршрут по сохранённым связям и форматирует подписи источника и назначения.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../copy_panels.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [copy_groups_ui.py](copy_groups_ui.md), [copy_setup_ui.py](copy_setup_ui.md), [paired_workspace_ui.py](paired_workspace_ui.md), [photo_libraries_ui.py](photo_libraries_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_panels.py](tests.md#module-tests.test_copy_panels), [tests/test_workspace_photos.py](tests.md#module-tests.test_workspace_photos).

## Оглавление определений

- [_copy_ancestry](#symbol-_copy_ancestry) — Поднимается от выбранной копии к корню по сохранённым ссылкам.
- [branch_origin](#symbol-branch_origin) — Подписывает непосредственный источник строки общего дерева копий.
- [branch_summary](#symbol-branch_summary) — Подписывает самый длинный маршрут для свёрнутой строки источника.
- [copy_branches](#symbol-copy_branches) — Возвращает путь до каждой копии в порядке дерева, начиная с первого назначения.
- [copy_heading](#symbol-copy_heading) — Формирует подпись источника, действующей копии или архивного назначения.
- [copy_route](#symbol-copy_route) — Строит маршрут через выбранную копию по фактическим связям источников.
- [copy_upstream](#symbol-copy_upstream) — Возвращает фактический источник выбранной копии, учитывая тип хранимой ссылки.
- [disconnected](#symbol-disconnected) — Проверяет доступность привязанной папки по состоянию связи и тома.
- [first_copy](#symbol-first_copy) — Выбирает копию с наименьшим номером среди доступных.

<a id="symbol-_copy_ancestry"></a>

## `_copy_ancestry`

[copy_panels.py](../../copy_panels.py) · `_copy_ancestry`

Поднимается от выбранной копии к корню по сохранённым ссылкам. Возвращает путь и признак цикла, отмечает отсутствующий источник без подстановки корня.

```python
def _copy_ancestry(root, by_id, target, parent_key)
```

Прямые выражения вызова: `by_id.get`, `dict`, `list`, `nodes.append`, `nodes[-1].get`, `reversed`, `seen.add`.

Выражения возврата (ветви, без исполнения):

- `(list(reversed(nodes)), cycle)`


<a id="symbol-branch_origin"></a>

## `branch_origin`

[copy_panels.py](../../copy_panels.py) · `branch_origin`

Подписывает непосредственный источник строки общего дерева копий. Для прямой копии подпись не нужна.

```python
def branch_origin(branch)
```

Прямые выражения вызова: `len`, `parent.get`.

Выражения возврата (ветви, без исполнения):

- `''`
- `parent['label']`
- `f'из {label}'`


<a id="symbol-branch_summary"></a>

## `branch_summary`

[copy_panels.py](../../copy_panels.py) · `branch_summary`

Подписывает самый длинный маршрут для свёрнутой строки источника. Многоточие указывает на недоступное звено или другие зависимые ветки.

```python
def branch_summary(branches)
```

Прямые выражения вызова: `' → '.join`, `any`, `len`, `max`, `node.get`.

Выражения возврата (ветви, без исполнения):

- `summary + (' · …' if any((branch[-1]['id'] not in shown for branch in chains)) else '')`


<a id="symbol-copy_branches"></a>

## `copy_branches`

[copy_panels.py](../../copy_panels.py) · `copy_branches`

Возвращает путь до каждой копии в порядке дерева, начиная с первого назначения. Сохраняет недоступный источник и оставляет повреждённую связь видимой.

```python
def copy_branches(copies, *, parent_key)
```

Прямые выражения вызова: [_copy_ancestry](copy_panels.md#symbol-_copy_ancestry), `branches.append`, `by_id.values`, `dict`, `sorted`, `tuple`.

Выражения возврата (ветви, без исполнения):

- `sorted(branches, key=lambda branch: tuple((node['number'] for node in branch if 'number' in node)))`


<a id="symbol-copy_heading"></a>

## `copy_heading`

[copy_panels.py](../../copy_panels.py) · `copy_heading`

Формирует подпись источника, действующей копии или архивного назначения. Заголовок показывает роль относительно выбранного перехода.

```python
def copy_heading(scope, *, target=False, historical=False)
```

Выражения возврата (ветви, без исполнения):

- `f'{label} (источник копирования)'`
- `f'Прежняя {label}'`
- `f"{label} (копия №{scope['number']})"`


<a id="symbol-copy_route"></a>

## `copy_route`

[copy_panels.py](../../copy_panels.py) · `copy_route`

Строит маршрут через выбранную копию по фактическим связям источников. По умолчанию продолжает маршрут первой доступной копией каждого следующего звена.

```python
def copy_route(root, copies, target, *, parent_key, downstream=True)
```

Прямые выражения вызова: [_copy_ancestry](copy_panels.md#symbol-_copy_ancestry), `copy.get`, [first_copy](copy_panels.md#symbol-first_copy), `nodes.append`, `seen.add`, `tuple`.

Выражения возврата (ветви, без исполнения):

- `(root, target)`
- `tuple(nodes)`


<a id="symbol-copy_upstream"></a>

## `copy_upstream`

[copy_panels.py](../../copy_panels.py) · `copy_upstream`

Возвращает фактический источник выбранной копии, учитывая тип хранимой ссылки. При отсутствующем непосредственном источнике или цикле возвращает None.

```python
def copy_upstream(root, copies, target, *, parent_key)
```

Прямые выражения вызова: [_copy_ancestry](copy_panels.md#symbol-_copy_ancestry), `len`.

Выражения возврата (ветви, без исполнения):

- `root`
- `nodes[-2]`
- `None`


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
