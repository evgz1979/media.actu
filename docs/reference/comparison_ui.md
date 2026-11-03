# Совместимость адреса /compare: `comparison_ui.py`

Действующий переход со старой страницы сравнения на главную; параметры source, path и job сохраняются в query string.

[Исходный модуль](../../comparison_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [ui.py](ui.md).
Тестовые модули с прямым импортом: нет; возможна косвенная проверка через вызывающие компоненты.

## Оглавление определений

- [register_comparison_page](#symbol-register-comparison-page) — Регистрирует перенаправление прежнего адреса общей сверки.
- [register_comparison_page.comparison_redirect](#symbol-register-comparison-page-comparison-redirect) — Перенаправляет /compare на главную с сохранением непустых параметров ссылки.

<a id="symbol-register-comparison-page"></a>

## `register_comparison_page`

[comparison_ui.py:10](../../comparison_ui.py#L10)

Регистрирует перенаправление прежнего адреса общей сверки. Параметры: request, format_bytes, format_date.

```python
def register_comparison_page(request, format_bytes, format_date)
```

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-register-comparison-page-comparison-redirect"></a>

## `register_comparison_page.comparison_redirect`

[comparison_ui.py:14](../../comparison_ui.py#L14)

Перенаправляет /compare на главную с сохранением непустых параметров ссылки. Использует RedirectResponse, urlencode, {'source': source, 'path': path, 'job': job}.items.

```python
async def comparison_redirect(source: str='', path: str='', job: str='')
```

Декораторы: `app.get('/compare', include_in_schema=False)`.

Прямые выражения вызова: `RedirectResponse`, `urlencode`, `{'source': source, 'path': path, 'job': job}.items`.

Выражения возврата (ветви, без исполнения):

- `RedirectResponse('/' + ('?' + urlencode(params) if params else ''), status_code=307)`
