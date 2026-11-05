# Окна синхронизации Photos: `media_manager/photos_schedule.py`

Хранит часы работы и постоянные запросы оригиналов. Фоновый таймер выдаёт работу только в допустимом окне; ручная пауза и временная блокировка различаются.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/photos_schedule.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_photos_schedule.py](tests.md#module-tests.test_photos_schedule).

## Оглавление определений

- [PhotosSyncSchedule](#symbol-PhotosSyncSchedule) — Координирует сохранённые запросы Photos и разрешённые временные окна.
- [PhotosSyncSchedule.__init__](#symbol-PhotosSyncSchedule.__init__) — Инициализирует PhotosSyncSchedule и его рабочее состояние.
- [PhotosSyncSchedule._arm](#symbol-PhotosSyncSchedule._arm) — Включает запрос корневой копии и сбрасывает ожидание повторного запуска.
- [PhotosSyncSchedule._arm_if_missing](#symbol-PhotosSyncSchedule._arm_if_missing) — Сохраняет отсутствующий запрос для продолжения в следующем окне.
- [PhotosSyncSchedule._db](#symbol-PhotosSyncSchedule._db) — Предоставляет транзакционное соединение каталога с гарантированным закрытием.
- [PhotosSyncSchedule._pause_outside_window](#symbol-PhotosSyncSchedule._pause_outside_window) — Запрашивает паузу активных оригиналов вне разрешённых часов.
- [PhotosSyncSchedule._request](#symbol-PhotosSyncSchedule._request) — Читает постоянный запрос автоматического сохранения одной копии.
- [PhotosSyncSchedule.blocked](#symbol-PhotosSyncSchedule.blocked) — Проверяет, запрещает ли текущее время работу выбранной медиатеки.
- [PhotosSyncSchedule.cancel](#symbol-PhotosSyncSchedule.cancel) — Отключает сохранённый запрос автоматической работы корневой копии.
- [PhotosSyncSchedule.close](#symbol-PhotosSyncSchedule.close) — Останавливает таймер расписания и пробуждает ожидающий поток.
- [PhotosSyncSchedule.configure](#symbol-PhotosSyncSchedule.configure) — Сохраняет проверенные часы работы и согласует уже запущенные задания.
- [PhotosSyncSchedule.decorate](#symbol-PhotosSyncSchedule.decorate) — Добавляет к состоянию задания ожидание окна и ошибку расписания.
- [PhotosSyncSchedule.describe](#symbol-PhotosSyncSchedule.describe) — Дополняет настройки окна текущей блокировкой и подписью времени МСК.
- [PhotosSyncSchedule.manages](#symbol-PhotosSyncSchedule.manages) — Проверяет наличие включённого запроса расписания для копии.
- [PhotosSyncSchedule.request](#symbol-PhotosSyncSchedule.request) — Регистрирует ручной запрос работы через расписание и проверяет немедленный запуск.
- [PhotosSyncSchedule.settings](#symbol-PhotosSyncSchedule.settings) — Возвращает настройки окна медиатеки либо безопасные значения по умолчанию.
- [PhotosSyncSchedule.start](#symbol-PhotosSyncSchedule.start) — Запускает фоновый таймер проверки расписания.
- [PhotosSyncSchedule.start.run](#symbol-PhotosSyncSchedule.start.run) — Проверяет расписание каждые 15 секунд и сохраняет работоспособность при ошибках.
- [PhotosSyncSchedule.tick](#symbol-PhotosSyncSchedule.tick) — Выбирает один допустимый корневой запрос и запускает сохранение оригиналов.
- [in_window](#symbol-in_window) — Определяет, попадает ли момент в разрешённые часы выбранной временной зоны.
- [window_key](#symbol-window_key) — Возвращает дату начала текущего окна, включая переход через полночь.

## Константы и значения по умолчанию

<a id="constant-DEFAULT"></a>

### `DEFAULT`

`dict(night_only=False, start_hour=0, end_hour=7, timezone='Europe/Moscow')`

<a id="constant-RUNNING"></a>

### `RUNNING`

`{'manifest', 'inventory', 'saving', 'pausing'}`


<a id="symbol-PhotosSyncSchedule"></a>

## `PhotosSyncSchedule`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule`

Координирует сохранённые запросы Photos и разрешённые временные окна. Зависимости конструктора: libraries, originals.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `_settings`, `_stop`, `_thread`, `_tick_lock`, `_wake`, `catalog`, `clock`, `libraries`, `originals`.

Именованные методы: `__init__`, `_db`, `settings`, `blocked`, `describe`, `configure`, `_request`, `manages`, `_arm`, `request`, `cancel`, `decorate`, `_pause_outside_window`, `_arm_if_missing`, `tick`, `start`, `close`.

<a id="symbol-PhotosSyncSchedule.__init__"></a>

## `PhotosSyncSchedule.__init__`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.__init__`

Инициализирует PhotosSyncSchedule и его рабочее состояние. Изменяет SQLite-таблицы: photos_sync_requests, photos_sync_settings.

```python
def __init__(self, libraries, originals, *, clock=None)
```

SQLite: чтение `photos_sync_settings`; запись/DDL `photos_sync_requests`, `photos_sync_settings`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_lock`, `_settings`, `_stop`, `_thread`, `_tick_lock`, `_wake`, `catalog`, `clock`, `libraries`, `originals`.

Прямые выражения вызова: `bool`, `db.execute`, `db.executescript`, `dict`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), `threading.Event`, `threading.Lock`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule._arm"></a>

## `PhotosSyncSchedule._arm`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule._arm`

Включает запрос корневой копии и сбрасывает ожидание повторного запуска. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def _arm(self, link_id)
```

SQLite: чтение не найдено; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), `self.libraries.root_copy`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule._arm_if_missing"></a>

## `PhotosSyncSchedule._arm_if_missing`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule._arm_if_missing`

Сохраняет отсутствующий запрос для продолжения в следующем окне. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def _arm_if_missing(self, link_id)
```

SQLite: чтение не найдено; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), `self.libraries.root_copy`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule._db"></a>

## `PhotosSyncSchedule._db`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule._db`

Предоставляет транзакционное соединение каталога с гарантированным закрытием. Использует db.close, self.catalog.connect.

```python
def _db(self)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `db.close`, `self.catalog.connect`.

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-PhotosSyncSchedule._pause_outside_window"></a>

## `PhotosSyncSchedule._pause_outside_window`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule._pause_outside_window`

Запрашивает паузу активных оригиналов вне разрешённых часов. Читает SQLite-таблицы: photos_copy_links, photos_original_jobs.

```python
def _pause_outside_window(self)
```

SQLite: чтение `photos_copy_links`, `photos_original_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `list`, [self._arm_if_missing](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._arm_if_missing), [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), [self.blocked](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.blocked), `self.originals.pause`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule._request"></a>

## `PhotosSyncSchedule._request`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule._request`

Читает постоянный запрос автоматического сохранения одной копии. Читает SQLite-таблицы: photos_sync_requests.

```python
def _request(self, link_id)
```

SQLite: чтение `photos_sync_requests`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT * FROM photos_sync_requests WHERE link_id=?', (link_id,)).fetchone`, `dict`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db).

Выражения возврата (ветви, без исполнения):

- `dict(row) if row else None`


<a id="symbol-PhotosSyncSchedule.blocked"></a>

## `PhotosSyncSchedule.blocked`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.blocked`

Проверяет, запрещает ли текущее время работу выбранной медиатеки. Использует in_window, self.clock, self.settings.

```python
def blocked(self, source_id)
```

Прямые выражения вызова: [in_window](media_manager--photos_schedule.md#symbol-in_window), `self.clock`, [self.settings](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.settings).

Выражения возврата (ветви, без исполнения):

- `not in_window(self.settings(source_id), self.clock())`


<a id="symbol-PhotosSyncSchedule.cancel"></a>

## `PhotosSyncSchedule.cancel`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.cancel`

Отключает сохранённый запрос автоматической работы корневой копии. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def cancel(self, link_id)
```

SQLite: чтение не найдено; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), `self.libraries.root_copy`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule.close"></a>

## `PhotosSyncSchedule.close`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.close`

Останавливает таймер расписания и пробуждает ожидающий поток. Обновляет состояние объекта: _thread.

```python
def close(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._stop.set`, `self._thread.join`, `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule.configure"></a>

## `PhotosSyncSchedule.configure`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.configure`

Сохраняет проверенные часы работы и согласует уже запущенные задания. Изменяет SQLite-таблицы: photos_sync_settings.

```python
def configure(self, source_id, night_only, start_hour=0, end_hour=7, timezone='Europe/Moscow')
```

SQLite: чтение `photos_copy_links`; запись/DDL `photos_sync_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `dict`, `int`, `job.get`, [self._arm](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._arm), [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), [self._pause_outside_window](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._pause_outside_window), [self._request](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._request), `self._wake.set`, [self.blocked](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.blocked), [self.describe](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.describe), `self.libraries.profile`, `self.originals.summary`, [self.settings](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.settings), `type`.

Явные `raise`:

- `ValueError('Задай разные часы начала и окончания от 00 до 23 по Москве')`

Выражения возврата (ветви, без исполнения):

- `self.describe(source_id)`


<a id="symbol-PhotosSyncSchedule.decorate"></a>

## `PhotosSyncSchedule.decorate`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.decorate`

Добавляет к состоянию задания ожидание окна и ошибку расписания. Поля результата: scheduled.

```python
def decorate(self, link_id, job)
```

SQLite: чтение `photos_copy_links`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT source_id FROM photos_copy_links WHERE id=?', (link_id,)).fetchone`, `dict`, `result.update`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), [self._request](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._request), [self.blocked](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.blocked), [self.describe](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.describe).

Выражения возврата (ветви, без исполнения):

- `dict(job, scheduled=False)`
- `job`
- `result`


<a id="symbol-PhotosSyncSchedule.describe"></a>

## `PhotosSyncSchedule.describe`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.describe`

Дополняет настройки окна текущей блокировкой и подписью времени МСК. Поля результата: blocked, window.

```python
def describe(self, source_id)
```

Прямые выражения вызова: `dict`, [self.blocked](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.blocked), [self.settings](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.settings).

Выражения возврата (ветви, без исполнения):

- `dict(settings, blocked=self.blocked(source_id), window=f"{settings['start_hour']:02d}:00–{settings['end_hour']:02d}:00 МСК")`


<a id="symbol-PhotosSyncSchedule.manages"></a>

## `PhotosSyncSchedule.manages`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.manages`

Проверяет наличие включённого запроса расписания для копии. Использует self._request.

```python
def manages(self, link_id)
```

Прямые выражения вызова: `bool`, [self._request](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._request).

Выражения возврата (ветви, без исполнения):

- `bool(row and row['enabled'])`


<a id="symbol-PhotosSyncSchedule.request"></a>

## `PhotosSyncSchedule.request`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.request`

Регистрирует ручной запрос работы через расписание и проверяет немедленный запуск. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def request(self, link_id, source_id=None)
```

SQLite: чтение не найдено; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `job.get`, [self._arm](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._arm), [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), `self._wake.set`, `self.libraries.root_copy`, `self.originals._link`, `self.originals.summary`, [self.tick](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.tick).

Выражения возврата (ветви, без исполнения):

- `self.originals.summary(link_id)`


<a id="symbol-PhotosSyncSchedule.settings"></a>

## `PhotosSyncSchedule.settings`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.settings`

Возвращает настройки окна медиатеки либо безопасные значения по умолчанию. Использует self._settings.get.

```python
def settings(self, source_id)
```

Прямые выражения вызова: `dict`, `self._settings.get`.

Выражения возврата (ветви, без исполнения):

- `dict(self._settings.get(source_id, dict(DEFAULT, source_id=source_id)))`


<a id="symbol-PhotosSyncSchedule.start"></a>

## `PhotosSyncSchedule.start`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.start`

Запускает фоновый таймер проверки расписания. Обновляет состояние объекта: _thread.

```python
def start(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._stop.clear`, `self._thread.start`, `threading.Thread`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-PhotosSyncSchedule.start.run"></a>

## `PhotosSyncSchedule.start.run`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.start.run`

Проверяет расписание каждые 15 секунд и сохраняет работоспособность при ошибках. Обрабатывает ошибки: Exception.

```python
def run()
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._wake.clear`, `self._wake.wait`, [self.tick](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.tick).

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PhotosSyncSchedule.tick"></a>

## `PhotosSyncSchedule.tick`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `PhotosSyncSchedule.tick`

Выбирает один допустимый корневой запрос и запускает сохранение оригиналов. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def tick(self)
```

SQLite: чтение `photos_copy_links`, `photos_original_jobs`, `photos_sync_requests`; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone`, `dict`, `instant.timestamp`, `job.get`, [self._db](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._db), [self._pause_outside_window](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule._pause_outside_window), `self._tick_lock.acquire`, `self._tick_lock.release`, [self.blocked](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.blocked), [self.cancel](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.cancel), `self.clock`, `self.libraries.copy_source`, `self.libraries.profile`, `self.originals.start`, `self.originals.summary`, [self.settings](media_manager--photos_schedule.md#symbol-PhotosSyncSchedule.settings), `str`, [window_key](media_manager--photos_schedule.md#symbol-window_key).

Перехватываемые типы: `(ValueError, OSError, RuntimeError, KeyError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-in_window"></a>

## `in_window`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `in_window`

Определяет, попадает ли момент в разрешённые часы выбранной временной зоны. Использует ZoneInfo, instant.astimezone.

```python
def in_window(settings, instant)
```

Прямые выражения вызова: `ZoneInfo`, `instant.astimezone`.

Выражения возврата (ветви, без исполнения):

- `True`
- `start <= hour < end if start < end else hour >= start or hour < end`


<a id="symbol-window_key"></a>

## `window_key`

[media_manager/photos_schedule.py](../../media_manager/photos_schedule.py) · `window_key`

Возвращает дату начала текущего окна, включая переход через полночь. Использует ZoneInfo, instant.astimezone, local.date, local.date().isoformat, timedelta.

```python
def window_key(settings, instant)
```

Прямые выражения вызова: `ZoneInfo`, `instant.astimezone`, `local.date`, `local.date().isoformat`, `timedelta`.

Выражения возврата (ветви, без исполнения):

- `local.date().isoformat()`
