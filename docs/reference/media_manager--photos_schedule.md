# Окна синхронизации Photos: `media_manager/photos_schedule.py`

Хранит часы работы и постоянные запросы оригиналов. Фоновый таймер выдаёт работу только в допустимом окне; ручная пауза и временная блокировка различаются.

[Исходный модуль](../../media_manager/photos_schedule.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_photos_schedule.py](../../tests/test_photos_schedule.py#L10).

## Оглавление определений

- [in_window](#symbol-in-window) — Определяет, попадает ли момент в разрешённые часы выбранной временной зоны.
- [window_key](#symbol-window-key) — Возвращает дату начала текущего окна, включая переход через полночь.
- [PhotosSyncSchedule](#symbol-photossyncschedule) — Координирует сохранённые запросы Photos и разрешённые временные окна.
- [PhotosSyncSchedule.__init__](#symbol-photossyncschedule---init--) — Инициализирует PhotosSyncSchedule и его рабочее состояние.
- [PhotosSyncSchedule._db](#symbol-photossyncschedule--db) — Предоставляет транзакционное соединение каталога с гарантированным закрытием.
- [PhotosSyncSchedule.settings](#symbol-photossyncschedule-settings) — Возвращает настройки окна медиатеки либо безопасные значения по умолчанию.
- [PhotosSyncSchedule.blocked](#symbol-photossyncschedule-blocked) — Проверяет, запрещает ли текущее время работу выбранной медиатеки.
- [PhotosSyncSchedule.describe](#symbol-photossyncschedule-describe) — Дополняет настройки окна текущей блокировкой и подписью времени МСК.
- [PhotosSyncSchedule.configure](#symbol-photossyncschedule-configure) — Сохраняет проверенные часы работы и согласует уже запущенные задания.
- [PhotosSyncSchedule._request](#symbol-photossyncschedule--request) — Читает постоянный запрос автоматического сохранения одной копии.
- [PhotosSyncSchedule.manages](#symbol-photossyncschedule-manages) — Проверяет наличие включённого запроса расписания для копии.
- [PhotosSyncSchedule._arm](#symbol-photossyncschedule--arm) — Включает запрос корневой копии и сбрасывает ожидание повторного запуска.
- [PhotosSyncSchedule.request](#symbol-photossyncschedule-request) — Регистрирует ручной запрос работы через расписание и проверяет немедленный запуск.
- [PhotosSyncSchedule.cancel](#symbol-photossyncschedule-cancel) — Отключает сохранённый запрос автоматической работы корневой копии.
- [PhotosSyncSchedule.decorate](#symbol-photossyncschedule-decorate) — Добавляет к состоянию задания ожидание окна и ошибку расписания.
- [PhotosSyncSchedule._pause_outside_window](#symbol-photossyncschedule--pause-outside-window) — Запрашивает паузу активных оригиналов вне разрешённых часов.
- [PhotosSyncSchedule._arm_if_missing](#symbol-photossyncschedule--arm-if-missing) — Сохраняет отсутствующий запрос для продолжения в следующем окне.
- [PhotosSyncSchedule.tick](#symbol-photossyncschedule-tick) — Выбирает один допустимый корневой запрос и запускает сохранение оригиналов.
- [PhotosSyncSchedule.start](#symbol-photossyncschedule-start) — Запускает фоновый таймер проверки расписания.
- [PhotosSyncSchedule.start.run](#symbol-photossyncschedule-start-run) — Проверяет расписание каждые 15 секунд и сохраняет работоспособность при ошибках.
- [PhotosSyncSchedule.close](#symbol-photossyncschedule-close) — Останавливает таймер расписания и пробуждает ожидающий поток.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [RUNNING](../../media_manager/photos_schedule.py#L8) | `{'manifest', 'inventory', 'saving', 'pausing'}` |
| [DEFAULT](../../media_manager/photos_schedule.py#L9) | `dict(night_only=False, start_hour=0, end_hour=7, timezone='Europe/Moscow')` |

<a id="symbol-in-window"></a>

## `in_window`

[media_manager/photos_schedule.py:14](../../media_manager/photos_schedule.py#L14)

Определяет, попадает ли момент в разрешённые часы выбранной временной зоны. Использует ZoneInfo, instant.astimezone.

```python
def in_window(settings, instant)
```

Прямые выражения вызова: `ZoneInfo`, `instant.astimezone`.

Выражения возврата (ветви, без исполнения):

- `True`
- `start <= hour < end if start < end else hour >= start or hour < end`


<a id="symbol-window-key"></a>

## `window_key`

[media_manager/photos_schedule.py:24](../../media_manager/photos_schedule.py#L24)

Возвращает дату начала текущего окна, включая переход через полночь. Использует ZoneInfo, instant.astimezone, local.date, local.date().isoformat, timedelta.

```python
def window_key(settings, instant)
```

Прямые выражения вызова: `ZoneInfo`, `instant.astimezone`, `local.date`, `local.date().isoformat`, `timedelta`.

Выражения возврата (ветви, без исполнения):

- `local.date().isoformat()`


<a id="symbol-photossyncschedule"></a>

## `PhotosSyncSchedule`

[media_manager/photos_schedule.py:33](../../media_manager/photos_schedule.py#L33)

Координирует сохранённые запросы Photos и разрешённые временные окна. Зависимости конструктора: libraries, originals.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `_settings`, `_stop`, `_thread`, `_tick_lock`, `_wake`, `catalog`, `clock`, `libraries`, `originals`.

Именованные методы: `__init__`, `_db`, `settings`, `blocked`, `describe`, `configure`, `_request`, `manages`, `_arm`, `request`, `cancel`, `decorate`, `_pause_outside_window`, `_arm_if_missing`, `tick`, `start`, `close`.

<a id="symbol-photossyncschedule---init--"></a>

## `PhotosSyncSchedule.__init__`

[media_manager/photos_schedule.py:36](../../media_manager/photos_schedule.py#L36)

Инициализирует PhotosSyncSchedule и его рабочее состояние. Изменяет SQLite-таблицы: photos_sync_requests, photos_sync_settings.

```python
def __init__(self, libraries, originals, *, clock=None)
```

SQLite: чтение `photos_sync_settings`; запись/DDL `photos_sync_requests`, `photos_sync_settings`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_lock`, `_settings`, `_stop`, `_thread`, `_tick_lock`, `_wake`, `catalog`, `clock`, `libraries`, `originals`.

Прямые выражения вызова: `bool`, `db.execute`, `db.executescript`, `dict`, [self._db](../../media_manager/photos_schedule.py#L63), `threading.Event`, `threading.Lock`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photossyncschedule--db"></a>

## `PhotosSyncSchedule._db`

[media_manager/photos_schedule.py:63](../../media_manager/photos_schedule.py#L63)

Предоставляет транзакционное соединение каталога с гарантированным закрытием. Использует db.close, self.catalog.connect.

```python
def _db(self)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `db.close`, `self.catalog.connect`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-photossyncschedule-settings"></a>

## `PhotosSyncSchedule.settings`

[media_manager/photos_schedule.py:73](../../media_manager/photos_schedule.py#L73)

Возвращает настройки окна медиатеки либо безопасные значения по умолчанию. Использует self._settings.get.

```python
def settings(self, source_id)
```

Прямые выражения вызова: `dict`, `self._settings.get`.

Выражения возврата (ветви, без исполнения):

- `dict(self._settings.get(source_id, dict(DEFAULT, source_id=source_id)))`


<a id="symbol-photossyncschedule-blocked"></a>

## `PhotosSyncSchedule.blocked`

[media_manager/photos_schedule.py:79](../../media_manager/photos_schedule.py#L79)

Проверяет, запрещает ли текущее время работу выбранной медиатеки. Использует in_window, self.clock, self.settings.

```python
def blocked(self, source_id)
```

Прямые выражения вызова: [in_window](../../media_manager/photos_schedule.py#L14), `self.clock`, [self.settings](../../media_manager/photos_schedule.py#L73).

Выражения возврата (ветви, без исполнения):

- `not in_window(self.settings(source_id), self.clock())`


<a id="symbol-photossyncschedule-describe"></a>

## `PhotosSyncSchedule.describe`

[media_manager/photos_schedule.py:84](../../media_manager/photos_schedule.py#L84)

Дополняет настройки окна текущей блокировкой и подписью времени МСК. Поля результата: blocked, window.

```python
def describe(self, source_id)
```

Прямые выражения вызова: `dict`, [self.blocked](../../media_manager/photos_schedule.py#L79), [self.settings](../../media_manager/photos_schedule.py#L73).

Выражения возврата (ветви, без исполнения):

- `dict(settings, blocked=self.blocked(source_id), window=f"{settings['start_hour']:02d}:00–{settings['end_hour']:02d}:00 МСК")`


<a id="symbol-photossyncschedule-configure"></a>

## `PhotosSyncSchedule.configure`

[media_manager/photos_schedule.py:91](../../media_manager/photos_schedule.py#L91)

Сохраняет проверенные часы работы и согласует уже запущенные задания. Изменяет SQLite-таблицы: photos_sync_settings.

```python
def configure(self, source_id, night_only, start_hour=0, end_hour=7, timezone='Europe/Moscow')
```

SQLite: чтение `photos_copy_links`; запись/DDL `photos_sync_settings`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `dict`, `int`, `job.get`, [self._arm](../../media_manager/photos_schedule.py#L133), [self._db](../../media_manager/photos_schedule.py#L63), [self._pause_outside_window](../../media_manager/photos_schedule.py#L183), [self._request](../../media_manager/photos_schedule.py#L120), `self._wake.set`, [self.blocked](../../media_manager/photos_schedule.py#L79), [self.describe](../../media_manager/photos_schedule.py#L84), `self.libraries.profile`, `self.originals.summary`, [self.settings](../../media_manager/photos_schedule.py#L73), `type`.

Явные `raise`:

- `ValueError('Задай разные часы начала и окончания от 00 до 23 по Москве')`

Выражения возврата (ветви, без исполнения):

- `self.describe(source_id)`


<a id="symbol-photossyncschedule--request"></a>

## `PhotosSyncSchedule._request`

[media_manager/photos_schedule.py:120](../../media_manager/photos_schedule.py#L120)

Читает постоянный запрос автоматического сохранения одной копии. Читает SQLite-таблицы: photos_sync_requests.

```python
def _request(self, link_id)
```

SQLite: чтение `photos_sync_requests`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT * FROM photos_sync_requests WHERE link_id=?', (link_id,)).fetchone`, `dict`, [self._db](../../media_manager/photos_schedule.py#L63).

Выражения возврата (ветви, без исполнения):

- `dict(row) if row else None`


<a id="symbol-photossyncschedule-manages"></a>

## `PhotosSyncSchedule.manages`

[media_manager/photos_schedule.py:127](../../media_manager/photos_schedule.py#L127)

Проверяет наличие включённого запроса расписания для копии. Использует self._request.

```python
def manages(self, link_id)
```

Прямые выражения вызова: `bool`, [self._request](../../media_manager/photos_schedule.py#L120).

Выражения возврата (ветви, без исполнения):

- `bool(row and row['enabled'])`


<a id="symbol-photossyncschedule--arm"></a>

## `PhotosSyncSchedule._arm`

[media_manager/photos_schedule.py:133](../../media_manager/photos_schedule.py#L133)

Включает запрос корневой копии и сбрасывает ожидание повторного запуска. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def _arm(self, link_id)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._db](../../media_manager/photos_schedule.py#L63), `self.libraries.root_copy`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photossyncschedule-request"></a>

## `PhotosSyncSchedule.request`

[media_manager/photos_schedule.py:141](../../media_manager/photos_schedule.py#L141)

Регистрирует ручной запрос работы через расписание и проверяет немедленный запуск. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def request(self, link_id, source_id=None)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `job.get`, [self._arm](../../media_manager/photos_schedule.py#L133), [self._db](../../media_manager/photos_schedule.py#L63), `self._wake.set`, `self.libraries.root_copy`, `self.originals._link`, `self.originals.summary`, [self.tick](../../media_manager/photos_schedule.py#L202).

Выражения возврата (ветви, без исполнения):

- `self.originals.summary(link_id)`


<a id="symbol-photossyncschedule-cancel"></a>

## `PhotosSyncSchedule.cancel`

[media_manager/photos_schedule.py:154](../../media_manager/photos_schedule.py#L154)

Отключает сохранённый запрос автоматической работы корневой копии. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def cancel(self, link_id)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._db](../../media_manager/photos_schedule.py#L63), `self.libraries.root_copy`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photossyncschedule-decorate"></a>

## `PhotosSyncSchedule.decorate`

[media_manager/photos_schedule.py:161](../../media_manager/photos_schedule.py#L161)

Добавляет к состоянию задания ожидание окна и ошибку расписания. Поля результата: scheduled.

```python
def decorate(self, link_id, job)
```

SQLite: чтение `photos_copy_links`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT source_id FROM photos_copy_links WHERE id=?', (link_id,)).fetchone`, `dict`, `result.update`, [self._db](../../media_manager/photos_schedule.py#L63), [self._request](../../media_manager/photos_schedule.py#L120), [self.blocked](../../media_manager/photos_schedule.py#L79), [self.describe](../../media_manager/photos_schedule.py#L84).

Выражения возврата (ветви, без исполнения):

- `dict(job, scheduled=False)`
- `job`
- `result`


<a id="symbol-photossyncschedule--pause-outside-window"></a>

## `PhotosSyncSchedule._pause_outside_window`

[media_manager/photos_schedule.py:183](../../media_manager/photos_schedule.py#L183)

Запрашивает паузу активных оригиналов вне разрешённых часов. Читает SQLite-таблицы: photos_copy_links, photos_original_jobs.

```python
def _pause_outside_window(self)
```

SQLite: чтение `photos_copy_links`, `photos_original_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `list`, [self._arm_if_missing](../../media_manager/photos_schedule.py#L195), [self._db](../../media_manager/photos_schedule.py#L63), [self.blocked](../../media_manager/photos_schedule.py#L79), `self.originals.pause`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photossyncschedule--arm-if-missing"></a>

## `PhotosSyncSchedule._arm_if_missing`

[media_manager/photos_schedule.py:195](../../media_manager/photos_schedule.py#L195)

Сохраняет отсутствующий запрос для продолжения в следующем окне. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def _arm_if_missing(self, link_id)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self._db](../../media_manager/photos_schedule.py#L63), `self.libraries.root_copy`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photossyncschedule-tick"></a>

## `PhotosSyncSchedule.tick`

[media_manager/photos_schedule.py:202](../../media_manager/photos_schedule.py#L202)

Выбирает один допустимый корневой запрос и запускает сохранение оригиналов. Изменяет SQLite-таблицы: photos_sync_requests.

```python
def tick(self)
```

SQLite: чтение `photos_copy_links`, `photos_original_jobs`, `photos_sync_requests`; запись/DDL `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone`, `dict`, `instant.timestamp`, `job.get`, [self._db](../../media_manager/photos_schedule.py#L63), [self._pause_outside_window](../../media_manager/photos_schedule.py#L183), `self._tick_lock.acquire`, `self._tick_lock.release`, [self.blocked](../../media_manager/photos_schedule.py#L79), [self.cancel](../../media_manager/photos_schedule.py#L154), `self.clock`, `self.libraries.copy_source`, `self.libraries.profile`, `self.originals.start`, `self.originals.summary`, [self.settings](../../media_manager/photos_schedule.py#L73), `str`, [window_key](../../media_manager/photos_schedule.py#L24).

Перехватываемые типы: `(ValueError, OSError, RuntimeError, KeyError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photossyncschedule-start"></a>

## `PhotosSyncSchedule.start`

[media_manager/photos_schedule.py:252](../../media_manager/photos_schedule.py#L252)

Запускает фоновый таймер проверки расписания. Обновляет состояние объекта: _thread.

```python
def start(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._stop.clear`, `self._thread.start`, `threading.Thread`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-photossyncschedule-start-run"></a>

## `PhotosSyncSchedule.start.run`

[media_manager/photos_schedule.py:258](../../media_manager/photos_schedule.py#L258)

Проверяет расписание каждые 15 секунд и сохраняет работоспособность при ошибках. Обрабатывает ошибки: Exception.

```python
def run()
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._wake.clear`, `self._wake.wait`, [self.tick](../../media_manager/photos_schedule.py#L202).

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photossyncschedule-close"></a>

## `PhotosSyncSchedule.close`

[media_manager/photos_schedule.py:273](../../media_manager/photos_schedule.py#L273)

Останавливает таймер расписания и пробуждает ожидающий поток. Обновляет состояние объекта: _thread.

```python
def close(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._stop.set`, `self._thread.join`, `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
