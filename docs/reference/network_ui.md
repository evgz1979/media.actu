# Диалог NAS: `network_ui.py`

Диалог серверов и ресурсов NAS: обнаружение, выбор, обновление ресурсов и запоминание. Все действия с системой выполняет Core.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../network_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [show_network_dialog](#symbol-show_network_dialog) — Открывает диалог обнаружения серверов и выбора SMB-ресурсов.
- [show_network_dialog.choose_server](#symbol-show_network_dialog.choose_server) — Выбирает сервер и загружает его сохранённый список ресурсов.
- [show_network_dialog.load_shares](#symbol-show_network_dialog.load_shares) — Получает ресурсы выбранного сервера с необязательным обновлением.
- [show_network_dialog.remember_share](#symbol-show_network_dialog.remember_share) — Запоминает ресурс и при запросе открывает подключение в Finder на Core.
- [show_network_dialog.render_servers](#symbol-show_network_dialog.render_servers) — Перерисовывает сохранённые и обнаруженные серверы NAS.
- [show_network_dialog.render_shares](#symbol-show_network_dialog.render_shares) — Перерисовывает ресурсы выбранного сервера и доступные команды.
- [show_network_dialog.scan](#symbol-show_network_dialog.scan) — Запускает поиск NAS и обновляет список серверов диалога.
- [show_network_dialog.show_warning](#symbol-show_network_dialog.show_warning) — Показывает предупреждение сетевой операции внутри диалога.

<a id="symbol-show_network_dialog"></a>

## `show_network_dialog`

[network_ui.py](../../network_ui.py) · `show_network_dialog`

Открывает диалог обнаружения серверов и выбора SMB-ресурсов. Обрабатывает ошибки: Exception.

```python
async def show_network_dialog(request, format_date, on_changed)
```

Прямые выражения вызова: `dialog.open`, `reload_button.disable`, `render_servers`, `request`, `scan`, `ui.add_css`, `ui.button`, `ui.button('Повторить поиск', icon='search', on_click=lambda: scan()).props`, `ui.button(icon='close', on_click=dialog.close).props`, `ui.button(icon='refresh', on_click=lambda: load_shares(True)).props`, `ui.card`, `ui.card().classes`, `ui.column`, `ui.column().classes`, `ui.dialog`, `ui.element`, `ui.element('div').classes`, `ui.label`, `ui.label('').classes`, `ui.label('NAS в локальной сети').classes`, `ui.label('«Добавить» сохраняет ресурс в списке томов. «Подключить на M4» открывает Finder на M4; пароль приложение не запрашивает.').classes`, `ui.label('Выбери NAS').classes`, `ui.label('Здесь появятся его сетевые ресурсы.').classes`, `ui.label('Поиск NAS…').classes`, `ui.label('Поиск выполняется на M4. Ресурсы можно запомнить без подключения.').classes`, `ui.row`, `ui.row().classes`, `warning.set_visibility`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-show_network_dialog.choose_server"></a>

## `show_network_dialog.choose_server`

[network_ui.py](../../network_ui.py) · `show_network_dialog.choose_server`

Выбирает сервер и загружает его сохранённый список ресурсов. Асинхронно ожидает: load_shares.

```python
async def choose_server(server_id)
```

Прямые выражения вызова: [load_shares](network_ui.md#symbol-show_network_dialog.load_shares), [render_servers](network_ui.md#symbol-show_network_dialog.render_servers), `share_list.clear`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-show_network_dialog.load_shares"></a>

## `show_network_dialog.load_shares`

[network_ui.py](../../network_ui.py) · `show_network_dialog.load_shares`

Получает ресурсы выбранного сервера с необязательным обновлением. Обрабатывает ошибки: Exception.

```python
async def load_shares(refresh)
```

Прямые выражения вызова: `bool`, `reload_button.disable`, `reload_button.set_enabled`, [render_shares](network_ui.md#symbol-show_network_dialog.render_shares), `request`, [show_warning](network_ui.md#symbol-show_network_dialog.show_warning).

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-show_network_dialog.remember_share"></a>

## `show_network_dialog.remember_share`

[network_ui.py](../../network_ui.py) · `show_network_dialog.remember_share`

Запоминает ресурс и при запросе открывает подключение в Finder на Core. Обрабатывает ошибки: Exception.

```python
async def remember_share(share, connect=False)
```

Прямые выражения вызова: [load_shares](network_ui.md#symbol-show_network_dialog.load_shares), `on_changed`, `request`, [show_warning](network_ui.md#symbol-show_network_dialog.show_warning), `ui.notify`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-show_network_dialog.render_servers"></a>

## `show_network_dialog.render_servers`

[network_ui.py](../../network_ui.py) · `show_network_dialog.render_servers`

Перерисовывает сохранённые и обнаруженные серверы NAS. Использует server_list.clear, ui.column, ui.column().classes и ещё 2.

```python
def render_servers()
```

Прямые выражения вызова: `server_list.clear`, `ui.column`, `ui.column().classes`, `ui.column().classes('nas-choice gap-1' + (' selected' if server['id'] == selected else '')).on`, `ui.icon`, `ui.icon('dns', size='20px').classes`, `ui.label`, `ui.label('NAS пока не найдены. Устройство должно быть включено и находиться в доступной M4 сети.').classes`, `ui.label('Найден в последнем поиске' if server['discovered'] else 'Сохранён ранее').classes`, `ui.label(server['host']).classes`, `ui.label(server['name']).classes`, `ui.row`, `ui.row().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-show_network_dialog.render_shares"></a>

## `show_network_dialog.render_shares`

[network_ui.py](../../network_ui.py) · `show_network_dialog.render_shares`

Перерисовывает ресурсы выбранного сервера и доступные команды. Использует format_date, server.get, share_list.clear, shares_data.get, show_warning.

```python
def render_shares()
```

Прямые выражения вызова: `format_date`, `len`, `server.get`, `share_list.clear`, `shares_data.get`, [show_warning](network_ui.md#symbol-show_network_dialog.show_warning), `ui.button`, `ui.button('Добавить', on_click=lambda s=share: remember_share(s)).props`, `ui.button('Подключить на M4', on_click=lambda s=share: remember_share(s, True)).props`, `ui.column`, `ui.column().classes`, `ui.label`, `ui.label('В списке томов').classes`, `ui.label('Не найден в последнем списке').classes`, `ui.label('Список ресурсов ещё не получен.' if not server.get('shares_at') else 'Файловые ресурсы не найдены.').classes`, `ui.label(share['comment']).classes`, `ui.label(share['name']).classes`, `ui.row`, `ui.row().classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-show_network_dialog.scan"></a>

## `show_network_dialog.scan`

[network_ui.py](../../network_ui.py) · `show_network_dialog.scan`

Запускает поиск NAS и обновляет список серверов диалога. Обрабатывает ошибки: Exception.

```python
async def scan()
```

Прямые выражения вызова: `bool`, `data.get`, `len`, [render_servers](network_ui.md#symbol-show_network_dialog.render_servers), `request`, `scan_button.disable`, `scan_button.enable`, [show_warning](network_ui.md#symbol-show_network_dialog.show_warning), `sum`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-show_network_dialog.show_warning"></a>

## `show_network_dialog.show_warning`

[network_ui.py](../../network_ui.py) · `show_network_dialog.show_warning`

Показывает предупреждение сетевой операции внутри диалога. Использует warning.set_visibility.

```python
def show_warning(message)
```

Прямые выражения вызова: `bool`, `warning.set_visibility`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
