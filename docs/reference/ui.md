# Вход в NiceGUI и HTTP-клиент: `ui.py`

Создаёт общий AsyncClient для обращения к Core, форматирует значения, регистрирует страницы и поддерживает перенаправление /media.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [comparison_ui.py](comparison_ui.md), [storage_ui.py](storage_ui.md).
Импортируется модулями: вход может выполняться через CLI или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_ui_connection.py](tests.md#module-tests.test_ui_connection).

## Оглавление определений

- [close_core_client](#symbol-close_core_client) — Закрывает общий HTTP-пул UI при завершении процесса.
- [core_request](#symbol-core_request) — Выполняет JSON-запрос Core через повторно используемый асинхронный пул соединений.
- [format_bytes](#symbol-format_bytes) — Форматирует размер в двоичных ступенях с русскими единицами.
- [format_date](#symbol-format_date) — Преобразует ISO-время в локальную подпись даты и часов.
- [format_percent](#symbol-format_percent) — Форматирует отношение готового к общему с дополнительной точностью малых значений.
- [old_media_page](#symbol-old_media_page) — Перенаправляет прежний адрес /media к медиатеке на общей главной странице.

## Константы и значения по умолчанию

<a id="constant-CORE_URL"></a>

### `CORE_URL`

`'http://127.0.0.1:18765'`


<a id="symbol-close_core_client"></a>

## `close_core_client`

[ui.py](../../ui.py) · `close_core_client`

Закрывает общий HTTP-пул UI при завершении процесса. Асинхронно ожидает: _core_client.aclose.

```python
async def close_core_client() -> None
```

Прямые выражения вызова: `_core_client.aclose`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-core_request"></a>

## `core_request`

[ui.py](../../ui.py) · `core_request`

Выполняет JSON-запрос Core через повторно используемый асинхронный пул соединений. Асинхронно ожидает: _core_client.request.

```python
async def core_request(method: str, path: str, *, timeout: float=20, **kwargs: Any) -> dict[str, Any]
```

Прямые выражения вызова: `_core_client.request`, `httpx.AsyncClient`, `httpx.Limits`, `response.json`, `response.raise_for_status`.

Выражения возврата (ветви, без исполнения):

- `response.json()`


<a id="symbol-format_bytes"></a>

## `format_bytes`

[ui.py](../../ui.py) · `format_bytes`

Форматирует размер в двоичных ступенях с русскими единицами. Использует float.

```python
def format_bytes(value: int) -> str
```

Прямые выражения вызова: `float`.

Выражения возврата (ветви, без исполнения):

- `'0 Б'`
- `f'{size:.{precision}f} {unit}'`


<a id="symbol-format_date"></a>

## `format_date`

[ui.py](../../ui.py) · `format_date`

Преобразует ISO-время в локальную подпись даты и часов. Использует datetime.fromisoformat, datetime.fromisoformat(value).astimezone, datetime.fromisoformat(value).astimezone().strftime.

```python
def format_date(value: str | None) -> str
```

Прямые выражения вызова: `datetime.fromisoformat`, `datetime.fromisoformat(value).astimezone`, `datetime.fromisoformat(value).astimezone().strftime`.

Выражения возврата (ветви, без исполнения):

- `'—'`
- `datetime.fromisoformat(value).astimezone().strftime('%d.%m.%Y %H:%M')`


<a id="symbol-format_percent"></a>

## `format_percent`

[ui.py](../../ui.py) · `format_percent`

Форматирует отношение готового к общему с дополнительной точностью малых значений. Параметры: done, total.

```python
def format_percent(done: int, total: int) -> str
```

Выражения возврата (ветви, без исполнения):

- `'0.0%'`
- `f'{percent:.{precision}f}%'`


<a id="symbol-old_media_page"></a>

## `old_media_page`

[ui.py](../../ui.py) · `old_media_page`

Перенаправляет прежний адрес /media к медиатеке на общей главной странице. Использует RedirectResponse.

```python
async def old_media_page(source: int | None=None)
```

Декораторы: `nicegui_app.get('/media', include_in_schema=False)`.

Прямые выражения вызова: `RedirectResponse`, `str`.

Выражения возврата (ветви, без исполнения):

- `RedirectResponse('/?source=photos-' + str(source) if source is not None else '/')`
