# Состояние браузерной вкладки: `workspace_state.py`

Нормализует компактные снимки навигации; не переносит файловые списки и содержимое с Core в хранилище вкладки.

[Исходный модуль](../../workspace_state.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_sidebar_state.py](../../tests/test_sidebar_state.py#L10), [tests/test_storage_previews.py](../../tests/test_storage_previews.py#L18), [tests/test_workspace_state.py](../../tests/test_workspace_state.py#L6).

## Оглавление определений

- [normalize_sidebar](#symbol-normalize-sidebar) — Восстанавливает только известные булевы настройки раскрытия боковых секций.
- [identifier](#symbol-identifier) — Проверяет формат ID из сохранённого состояния или допускает None.
- [path](#symbol-path) — Проверяет длину и нормализует относительный путь снимка вкладки.
- [pane_snapshot](#symbol-pane-snapshot) — Собирает компактный снимок панели и её режима превью.
- [normalize_state](#symbol-normalize-state) — Проверяет версию и структуру снимка двух панелей, пары и отчёта.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [STORAGE_KEY](../../workspace_state.py#L7) | `'media-actu.workspace.v1'` |
| [SIDEBAR_STORAGE_KEY](../../workspace_state.py#L8) | `'media-actu.sidebar.v1'` |
| [SIDEBAR_DEFAULTS](../../workspace_state.py#L9) | `dict(volumes=False, volume_archive=False, libraries=True, copy_groups=True, copy_archive=False)` |

<a id="symbol-normalize-sidebar"></a>

## `normalize_sidebar`

[workspace_state.py:15](../../workspace_state.py#L15)

Восстанавливает только известные булевы настройки раскрытия боковых секций. Использует SIDEBAR_DEFAULTS.items, value.get.

```python
def normalize_sidebar(value)
```

Прямые выражения вызова: `SIDEBAR_DEFAULTS.items`, `isinstance`, `value.get`.

Выражения возврата (ветви, без исполнения):

- `{key: value[key] if isinstance(value.get(key), bool) else default for (key, default) in SIDEBAR_DEFAULTS.items()}`


<a id="symbol-identifier"></a>

## `identifier`

[workspace_state.py:23](../../workspace_state.py#L23)

Проверяет формат ID из сохранённого состояния или допускает None. Явно отклоняет недопустимое состояние через ValueError.

```python
def identifier(value)
```

Прямые выражения вызова: `ValueError`, `isinstance`, `re.fullmatch`.

Явные `raise`:

- `ValueError('Некорректный ID в сохранённом состоянии')`

Выражения возврата (ветви, без исполнения):

- `None`
- `value`


<a id="symbol-path"></a>

## `path`

[workspace_state.py:33](../../workspace_state.py#L33)

Проверяет длину и нормализует относительный путь снимка вкладки. Явно отклоняет недопустимое состояние через ValueError.

```python
def path(value)
```

Прямые выражения вызова: `ValueError`, `isinstance`, `len`, `relative_path`.

Явные `raise`:

- `ValueError('Некорректный путь в сохранённом состоянии')`

Выражения возврата (ветви, без исполнения):

- `relative_path(value)`


<a id="symbol-pane-snapshot"></a>

## `pane_snapshot`

[workspace_state.py:41](../../workspace_state.py#L41)

Собирает компактный снимок панели и её режима превью. Использует data.get, preview.snapshot, vars.

```python
def pane_snapshot(pane)
```

Прямые выражения вызова: `bool`, `data.get`, `dict`, `isinstance`, `preview.snapshot`, `vars`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-normalize-state"></a>

## `normalize_state`

[workspace_state.py:56](../../workspace_state.py#L56)

Проверяет версию и структуру снимка двух панелей, пары и отчёта. Обрабатывает ошибки: (KeyError, TypeError, ValueError, AttributeError).

```python
def normalize_state(value)
```

Прямые выражения вызова: `bool`, `dict`, [identifier](../../workspace_state.py#L23), `isinstance`, `len`, `original.get`, `p.get`, `pair.get`, [path](../../workspace_state.py#L33), `preview.get`, `str`, `value.get`, `zip`.

Перехватываемые типы: `(KeyError, TypeError, ValueError, AttributeError)`.

Выражения возврата (ветви, без исполнения):

- `None`
- `result`
