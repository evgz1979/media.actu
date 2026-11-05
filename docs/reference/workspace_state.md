# Состояние браузерной вкладки: `workspace_state.py`

Нормализует компактные снимки навигации; не переносит файловые списки и содержимое с Core в хранилище вкладки.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../workspace_state.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_sidebar_state.py](tests.md#module-tests.test_sidebar_state), [tests/test_storage_previews.py](tests.md#module-tests.test_storage_previews), [tests/test_workspace_state.py](tests.md#module-tests.test_workspace_state).

## Оглавление определений

- [identifier](#symbol-identifier) — Проверяет формат ID из сохранённого состояния или допускает None.
- [normalize_sidebar](#symbol-normalize_sidebar) — Восстанавливает только известные булевы настройки раскрытия боковых секций.
- [normalize_state](#symbol-normalize_state) — Проверяет версию и структуру снимка двух панелей, пары и отчёта.
- [pane_snapshot](#symbol-pane_snapshot) — Собирает компактный снимок панели и её режима превью.
- [path](#symbol-path) — Проверяет длину и нормализует относительный путь снимка вкладки.

## Константы и значения по умолчанию

<a id="constant-SIDEBAR_DEFAULTS"></a>

### `SIDEBAR_DEFAULTS`

`dict(volumes=False, volume_archive=False, libraries=True, copy_groups=True, copy_archive=False)`

<a id="constant-SIDEBAR_STORAGE_KEY"></a>

### `SIDEBAR_STORAGE_KEY`

`'media-actu.sidebar.v1'`

<a id="constant-STORAGE_KEY"></a>

### `STORAGE_KEY`

`'media-actu.workspace.v1'`


<a id="symbol-identifier"></a>

## `identifier`

[workspace_state.py](../../workspace_state.py) · `identifier`

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


<a id="symbol-normalize_sidebar"></a>

## `normalize_sidebar`

[workspace_state.py](../../workspace_state.py) · `normalize_sidebar`

Восстанавливает только известные булевы настройки раскрытия боковых секций. Использует SIDEBAR_DEFAULTS.items, value.get.

```python
def normalize_sidebar(value)
```

Прямые выражения вызова: `SIDEBAR_DEFAULTS.items`, `isinstance`, `value.get`.

Выражения возврата (ветви, без исполнения):

- `{key: value[key] if isinstance(value.get(key), bool) else default for key, default in SIDEBAR_DEFAULTS.items()}`


<a id="symbol-normalize_state"></a>

## `normalize_state`

[workspace_state.py](../../workspace_state.py) · `normalize_state`

Проверяет версию и структуру снимка двух панелей, пары и отчёта. Обрабатывает ошибки: (KeyError, TypeError, ValueError, AttributeError).

```python
def normalize_state(value)
```

Прямые выражения вызова: `bool`, `dict`, [identifier](workspace_state.md#symbol-identifier), `isinstance`, `len`, `original.get`, `p.get`, `pair.get`, [path](workspace_state.md#symbol-path), `preview.get`, `str`, `value.get`, `zip`.

Перехватываемые типы: `(KeyError, TypeError, ValueError, AttributeError)`.

Выражения возврата (ветви, без исполнения):

- `None`
- `result`


<a id="symbol-pane_snapshot"></a>

## `pane_snapshot`

[workspace_state.py](../../workspace_state.py) · `pane_snapshot`

Собирает компактный снимок панели и её режима превью. Использует data.get, preview.snapshot, vars.

```python
def pane_snapshot(pane)
```

Прямые выражения вызова: `bool`, `data.get`, `dict`, `isinstance`, `preview.snapshot`, `vars`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-path"></a>

## `path`

[workspace_state.py](../../workspace_state.py) · `path`

Проверяет длину и нормализует относительный путь снимка вкладки. Явно отклоняет недопустимое состояние через ValueError.

```python
def path(value)
```

Прямые выражения вызова: `ValueError`, `isinstance`, `len`, `relative_path`.

Явные `raise`:

- `ValueError('Некорректный путь в сохранённом состоянии')`

Выражения возврата (ветви, без исполнения):

- `relative_path(value)`
