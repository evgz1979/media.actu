# Профили медиатек Photos: `media_manager/photo_libraries.py`

Сопоставляет текущую системную медиатеку с сохранёнными профилями по якорным ID. Управляет отдельными копиями и направленным графом источников Photos.

[Исходный модуль](../../media_manager/photo_libraries.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md), [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [app.py](app.md), [media_manager/photos_originals.py](media_manager--photos_originals.md).
Тестовые модули с прямым импортом: [tests/test_photo_libraries.py](../../tests/test_photo_libraries.py#L9), [tests/test_photos_browser.py](../../tests/test_photos_browser.py#L7), [tests/test_photos_originals.py](../../tests/test_photos_originals.py#L10).

## Оглавление определений

- [now](#symbol-now) — Возвращает текущее время UTC для записей профиля и журнала.
- [matches](#symbol-matches) — Проверяет совпадение найденных ID с якорями сохранённой медиатеки.
- [PhotoLibraries](#symbol-photolibraries) — Управляет идентичностью, доступностью и привязанными копиями медиатек Photos.
- [PhotoLibraries.__init__](#symbol-photolibraries---init--) — Инициализирует PhotoLibraries и его рабочее состояние.
- [PhotoLibraries._db](#symbol-photolibraries--db) — Предоставляет транзакционное соединение медиаиндекса с гарантированным закрытием.
- [PhotoLibraries._migrate](#symbol-photolibraries--migrate) — Создаёт профили для прежних Photos-источников и сбрасывает активность до проверки.
- [PhotoLibraries._profiles](#symbol-photolibraries--profiles) — Читает все профили и декодирует сохранённые якорные идентификаторы.
- [PhotoLibraries.profile](#symbol-photolibraries-profile) — Возвращает профиль медиатеки по ID источника либо поднимает KeyError.
- [PhotoLibraries._unavailable](#symbol-photolibraries--unavailable) — Помечает медиатеки неактивными и сохраняет причину недоступности.
- [PhotoLibraries.refresh_connection](#symbol-photolibraries-refresh-connection) — Сопоставляет системную медиатеку с одним профилем через PhotoKit probe.
- [PhotoLibraries.authorize](#symbol-photolibraries-authorize) — Запрашивает системное разрешение Photos и повторяет сопоставление профиля.
- [PhotoLibraries.register](#symbol-photolibraries-register) — Регистрирует текущую непустую медиатеку отдельным виртуальным источником.
- [PhotoLibraries.rename](#symbol-photolibraries-rename) — Меняет пользовательское название сохранённой медиатеки.
- [PhotoLibraries.set_paused](#symbol-photolibraries-set-paused) — Сохраняет ручную паузу превью медиатеки и обновляет очередь при продолжении.
- [PhotoLibraries._require_active](#symbol-photolibraries--require-active) — Требует активную медиатеку в состоянии ready для обращения к PhotoKit.
- [PhotoLibraries.scan](#symbol-photolibraries-scan) — Получает каталог активной медиатеки и обновляет индекс и якоря.
- [PhotoLibraries.create_thumbnail](#symbol-photolibraries-create-thumbnail) — Создаёт превью объекта только из подтверждённой активной медиатеки.
- [PhotoLibraries.open_asset](#symbol-photolibraries-open-asset) — Выделяет объект активной медиатеки в системном приложении Photos.
- [PhotoLibraries.list](#symbol-photolibraries-list) — Собирает профили, виртуальные тома, прогресс превью, копии и расписание.
- [PhotoLibraries.copy_source](#symbol-photolibraries-copy-source) — Возвращает ID копии-источника либо None для прямого источника Photos.
- [PhotoLibraries.root_copy](#symbol-photolibraries-root-copy) — Поднимается по цепочке источников к первой копии и проверяет циклы.
- [PhotoLibraries.set_copy_source](#symbol-photolibraries-set-copy-source) — Меняет источник копии медиатеки с проверкой связей и отсутствия циклов.
- [PhotoLibraries.make_first_copy](#symbol-photolibraries-make-first-copy) — Перенумеровывает копии медиатеки, ставя выбранную первой без изменения маршрутов.
- [PhotoLibraries.bind_copy](#symbol-photolibraries-bind-copy) — Привязывает доступную проверенную папку к медиатеке с отдельным номером.
- [PhotoLibraries.unbind_copy](#symbol-photolibraries-unbind-copy) — Отключает привязку копии медиатеки, сохраняя запись и квитанции ресурсов.

<a id="symbol-now"></a>

## `now`

[media_manager/photo_libraries.py:18](../../media_manager/photo_libraries.py#L18)

Возвращает текущее время UTC для записей профиля и журнала. Использует datetime.now, datetime.now(timezone.utc).isoformat.

```python
def now()
```

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`.

Выражения возврата (ветви, без исполнения):

- `datetime.now(timezone.utc).isoformat()`


<a id="symbol-matches"></a>

## `matches`

[media_manager/photo_libraries.py:24](../../media_manager/photo_libraries.py#L24)

Проверяет совпадение найденных ID с якорями сохранённой медиатеки. Использует set(anchors).intersection.

```python
def matches(anchors, found)
```

Прямые выражения вызова: `bool`, `len`, `min`, `set`, `set(anchors).intersection`.

Выражения возврата (ветви, без исполнения):

- `bool(anchors) and len(set(anchors).intersection(found)) >= min(3, len(anchors))`


<a id="symbol-photolibraries"></a>

## `PhotoLibraries`

[media_manager/photo_libraries.py:30](../../media_manager/photo_libraries.py#L30)

Управляет идентичностью, доступностью и привязанными копиями медиатек Photos. Зависимости конструктора: catalog, storage, adapter.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `adapter`, `catalog`, `connection`, `originals`, `polling`, `schedule`, `storage`.

Именованные методы: `__init__`, `_db`, `_migrate`, `_profiles`, `profile`, `_unavailable`, `refresh_connection`, `authorize`, `register`, `rename`, `set_paused`, `_require_active`, `scan`, `create_thumbnail`, `open_asset`, `list`, `copy_source`, `root_copy`, `set_copy_source`, `make_first_copy`, `bind_copy`, `unbind_copy`.

<a id="symbol-photolibraries---init--"></a>

## `PhotoLibraries.__init__`

[media_manager/photo_libraries.py:33](../../media_manager/photo_libraries.py#L33)

Инициализирует PhotoLibraries и его рабочее состояние. Обновляет состояние объекта: _lock, adapter, catalog, connection, originals, polling, schedule, storage.

```python
def __init__(self, catalog, storage, adapter)
```

Присваивания полям `self`: `_lock`, `adapter`, `catalog`, `connection`, `originals`, `polling`, `schedule`, `storage`.

Прямые выражения вызова: `dict`, [self._migrate](../../media_manager/photo_libraries.py#L55), `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries--db"></a>

## `PhotoLibraries._db`

[media_manager/photo_libraries.py:45](../../media_manager/photo_libraries.py#L45)

Предоставляет транзакционное соединение медиаиндекса с гарантированным закрытием. Использует db.close, self.catalog.connect.

```python
def _db(self)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `db.close`, `self.catalog.connect`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-photolibraries--migrate"></a>

## `PhotoLibraries._migrate`

[media_manager/photo_libraries.py:55](../../media_manager/photo_libraries.py#L55)

Создаёт профили для прежних Photos-источников и сбрасывает активность до проверки. Изменяет SQLite-таблицы: photos_copy_sources, photos_libraries.

```python
def _migrate(self)
```

SQLite: чтение `media_files`, `sources`; запись/DDL `photos_copy_sources`, `photos_libraries`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `any`, `db.execute`, `db.execute("SELECT id FROM sources WHERE kind='photos'").fetchall`, `getattr`, `json.dumps`, [self._db](../../media_manager/photo_libraries.py#L45), `self.catalog.add_system_photos_source`, `self.catalog.list_sources`, `uuid.uuid4`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries--profiles"></a>

## `PhotoLibraries._profiles`

[media_manager/photo_libraries.py:71](../../media_manager/photo_libraries.py#L71)

Читает все профили и декодирует сохранённые якорные идентификаторы. Читает SQLite-таблицы: photos_libraries.

```python
def _profiles(self)
```

SQLite: чтение `photos_libraries`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `json.loads`, [self._db](../../media_manager/photo_libraries.py#L45).

Выражения возврата (ветви, без исполнения):

- `rows`


<a id="symbol-photolibraries-profile"></a>

## `PhotoLibraries.profile`

[media_manager/photo_libraries.py:80](../../media_manager/photo_libraries.py#L80)

Возвращает профиль медиатеки по ID источника либо поднимает KeyError. Явно отклоняет недопустимое состояние через KeyError.

```python
def profile(self, source_id)
```

Прямые выражения вызова: `KeyError`, `next`, [self._profiles](../../media_manager/photo_libraries.py#L71).

Явные `raise`:

- `KeyError('Медиатека не найдена')`

Выражения возврата (ветви, без исполнения):

- `profile`


<a id="symbol-photolibraries--unavailable"></a>

## `PhotoLibraries._unavailable`

[media_manager/photo_libraries.py:88](../../media_manager/photo_libraries.py#L88)

Помечает медиатеки неактивными и сохраняет причину недоступности. Изменяет SQLite-таблицы: photos_libraries, sources.

```python
def _unavailable(self, state, error)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_libraries`, `sources`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `connection`.

Прямые выражения вызова: `db.execute`, `dict`, [now](../../media_manager/photo_libraries.py#L18), [self._db](../../media_manager/photo_libraries.py#L45), `str`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries-refresh-connection"></a>

## `PhotoLibraries.refresh_connection`

[media_manager/photo_libraries.py:96](../../media_manager/photo_libraries.py#L96)

Сопоставляет системную медиатеку с одним профилем через PhotoKit probe. Изменяет SQLite-таблицы: photos_libraries, sources.

```python
def refresh_connection(self, *, restart=True)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_libraries`, `sources`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `connection`.

Прямые выражения вызова: `db.execute`, `dict`, `json.dumps`, `len`, [matches](../../media_manager/photo_libraries.py#L24), `next`, [now](../../media_manager/photo_libraries.py#L18), `probe.get`, [self._db](../../media_manager/photo_libraries.py#L45), [self._profiles](../../media_manager/photo_libraries.py#L71), [self._unavailable](../../media_manager/photo_libraries.py#L88), `self.adapter.probe`, `self.catalog.list_sources`, `self.connection.update`, `set`.

Перехватываемые типы: `PhotosAccessDenied`, `PhotosAdapterError`.

Выражения возврата (ветви, без исполнения):

- `self.connection`


<a id="symbol-photolibraries-authorize"></a>

## `PhotoLibraries.authorize`

[media_manager/photo_libraries.py:132](../../media_manager/photo_libraries.py#L132)

Запрашивает системное разрешение Photos и повторяет сопоставление профиля. Использует self.adapter.status, self.refresh_connection.

```python
def authorize(self)
```

Прямые выражения вызова: `self.adapter.status`, [self.refresh_connection](../../media_manager/photo_libraries.py#L96).

Выражения возврата (ветви, без исполнения):

- `self.refresh_connection()`


<a id="symbol-photolibraries-register"></a>

## `PhotoLibraries.register`

[media_manager/photo_libraries.py:138](../../media_manager/photo_libraries.py#L138)

Регистрирует текущую непустую медиатеку отдельным виртуальным источником. Изменяет SQLite-таблицы: photos_libraries, sources.

```python
def register(self, label)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_libraries`, `sources`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `connection`.

Прямые выражения вызова: `ValueError`, `any`, `db.execute`, `dict`, `json.dumps`, `label.strip`, `len`, [matches](../../media_manager/photo_libraries.py#L24), [now](../../media_manager/photo_libraries.py#L18), `probe.get`, [self._db](../../media_manager/photo_libraries.py#L45), [self._profiles](../../media_manager/photo_libraries.py#L71), `self.adapter.probe`, [self.profile](../../media_manager/photo_libraries.py#L80), `uuid.uuid4`.

Явные `raise`:

- `ValueError('Задай название медиатеки до 120 символов')`
- `ValueError('Эта медиатека уже сохранена. Для другого Apple ID открой отдельную системную медиатеку в Photos.')`
- `ValueError('В текущей медиатеке пока нет объектов. Дождись её загрузки в Photos.')`

Выражения возврата (ветви, без исполнения):

- `self.profile(source_id)`


<a id="symbol-photolibraries-rename"></a>

## `PhotoLibraries.rename`

[media_manager/photo_libraries.py:162](../../media_manager/photo_libraries.py#L162)

Меняет пользовательское название сохранённой медиатеки. Изменяет SQLite-таблицы: sources.

```python
def rename(self, source_id, label)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `label.strip`, `len`, [self._db](../../media_manager/photo_libraries.py#L45), [self.profile](../../media_manager/photo_libraries.py#L80).

Явные `raise`:

- `ValueError('Задай название медиатеки до 120 символов')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries-set-paused"></a>

## `PhotoLibraries.set_paused`

[media_manager/photo_libraries.py:171](../../media_manager/photo_libraries.py#L171)

Сохраняет ручную паузу превью медиатеки и обновляет очередь при продолжении. Изменяет SQLite-таблицы: photos_libraries, thumbnail_waits.

```python
def set_paused(self, source_id, paused)
```

SQLite: чтение `media_files`, `thumbnail_waits`; запись/DDL `photos_libraries`, `thumbnail_waits`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PhotosLibraryUnavailable`, `connection.get`, `db.execute`, `int`, [self._db](../../media_manager/photo_libraries.py#L45), `self.catalog.enqueue_source_thumbnails`, [self.profile](../../media_manager/photo_libraries.py#L80), [self.refresh_connection](../../media_manager/photo_libraries.py#L96).

Явные `raise`:

- `PhotosLibraryUnavailable(connection.get('error') or 'Открой эту системную медиатеку на M4 и повтори подключение.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries--require-active"></a>

## `PhotoLibraries._require_active`

[media_manager/photo_libraries.py:186](../../media_manager/photo_libraries.py#L186)

Требует активную медиатеку в состоянии ready для обращения к PhotoKit. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def _require_active(self, source_id)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, [self.profile](../../media_manager/photo_libraries.py#L80).

Явные `raise`:

- `PhotosLibraryUnavailable('Эта медиатека сейчас не подключена. Сохранённые превью доступны.')`

Выражения возврата (ветви, без исполнения):

- `profile`


<a id="symbol-photolibraries-scan"></a>

## `PhotoLibraries.scan`

[media_manager/photo_libraries.py:194](../../media_manager/photo_libraries.py#L194)

Получает каталог активной медиатеки и обновляет индекс и якоря. Изменяет SQLite-таблицы: photos_libraries.

```python
def scan(self, source_id)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_libraries`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PhotosLibraryUnavailable`, `db.execute`, `json.dumps`, [self._db](../../media_manager/photo_libraries.py#L45), [self._require_active](../../media_manager/photo_libraries.py#L186), `self.adapter.scan`, `self.catalog.enqueue_source_thumbnails`, `self.catalog.replace_photos_scan`, `self.catalog.set_source_status`, `self.schedule.blocked`, `self.schedule.describe`.

Явные `raise`:

- `PhotosLibraryUnavailable('Синхронизация разрешена только ночью: ' + self.schedule.describe(source_id)['window'])`

Выражения возврата (ветви, без исполнения):

- `assets`


<a id="symbol-photolibraries-create-thumbnail"></a>

## `PhotoLibraries.create_thumbnail`

[media_manager/photo_libraries.py:211](../../media_manager/photo_libraries.py#L211)

Создаёт превью объекта только из подтверждённой активной медиатеки. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def create_thumbnail(self, source_id, asset_identifier, target)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, `isinstance`, [self._require_active](../../media_manager/photo_libraries.py#L186), [self._unavailable](../../media_manager/photo_libraries.py#L88), `self.adapter.create_thumbnail`, `self.schedule.blocked`.

Явные `raise`:

- `PhotosLibraryUnavailable('Превью ожидают ночного окна')`

Перехватываемые типы: `(PhotosAccessDenied, PhotosLibraryUnavailable)`.

Выражения возврата (ветви, без исполнения):

- `self.adapter.create_thumbnail(asset_identifier, target, anchors=profile['anchors'])`


<a id="symbol-photolibraries-open-asset"></a>

## `PhotoLibraries.open_asset`

[media_manager/photo_libraries.py:224](../../media_manager/photo_libraries.py#L224)

Выделяет объект активной медиатеки в системном приложении Photos. Явно отклоняет недопустимое состояние через PhotosLibraryUnavailable.

```python
def open_asset(self, source_id, identifier)
```

Прямые выражения вызова: `PhotosLibraryUnavailable`, [matches](../../media_manager/photo_libraries.py#L24), `probe.get`, [self._require_active](../../media_manager/photo_libraries.py#L186), [self._unavailable](../../media_manager/photo_libraries.py#L88), `self.adapter.open_asset`, `self.adapter.probe`.

Явные `raise`:

- `PhotosLibraryUnavailable('Открыта другая медиатека Photos')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries-list"></a>

## `PhotoLibraries.list`

[media_manager/photo_libraries.py:235](../../media_manager/photo_libraries.py#L235)

Собирает профили, виртуальные тома, прогресс превью, копии и расписание. Поля результата: libraries, connection.

```python
def list(self)
```

SQLite: чтение `media_files`, `photos_copy_links`, `photos_copy_sources`, `thumbnail_waits`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `copies.append`, `db.execute`, `dict`, `next`, `result.append`, [self._db](../../media_manager/photo_libraries.py#L45), [self._profiles](../../media_manager/photo_libraries.py#L71), `self.catalog.list_sources`, `self.originals.summary`, `self.schedule.describe`, `self.storage.refresh`, `sources.get`, `volume.get`, `volumes.get`, `waits.get`.

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `dict(libraries=result, connection=self.connection)`


<a id="symbol-photolibraries-copy-source"></a>

## `PhotoLibraries.copy_source`

[media_manager/photo_libraries.py:270](../../media_manager/photo_libraries.py#L270)

Возвращает ID копии-источника либо None для прямого источника Photos. Читает SQLite-таблицы: photos_copy_sources.

```python
def copy_source(self, link_id)
```

SQLite: чтение `photos_copy_sources`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT source_link_id FROM photos_copy_sources WHERE link_id=?', (link_id,)).fetchone`, [self._db](../../media_manager/photo_libraries.py#L45).

Выражения возврата (ветви, без исполнения):

- `row[0] if row else None`


<a id="symbol-photolibraries-root-copy"></a>

## `PhotoLibraries.root_copy`

[media_manager/photo_libraries.py:277](../../media_manager/photo_libraries.py#L277)

Поднимается по цепочке источников к первой копии и проверяет циклы. Явно отклоняет недопустимое состояние через ValueError.

```python
def root_copy(self, link_id)
```

Прямые выражения вызова: `ValueError`, [self.copy_source](../../media_manager/photo_libraries.py#L270), `set`, `visited.add`.

Явные `raise`:

- `ValueError('Циклическая связь копий медиатеки')`

Выражения возврата (ветви, без исполнения):

- `link_id`


<a id="symbol-photolibraries-set-copy-source"></a>

## `PhotoLibraries.set_copy_source`

[media_manager/photo_libraries.py:290](../../media_manager/photo_libraries.py#L290)

Меняет источник копии медиатеки с проверкой связей и отсутствия циклов. Изменяет SQLite-таблицы: photos_copy_sources, photos_sync_requests.

```python
def set_copy_source(self, source_id, link_id, source_link_id)
```

SQLite: чтение `photos_copy_links`, `photos_copy_sources`, `photos_original_jobs`; запись/DDL `photos_copy_sources`, `photos_sync_requests`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone`, `db.execute("SELECT 1 FROM sqlite_master WHERE name='photos_sync_requests'").fetchone`, `dict`, `edges.pop`, [self._db](../../media_manager/photo_libraries.py#L45), [self.profile](../../media_manager/photo_libraries.py#L80), `set`, `visited.add`.

Явные `raise`:

- `ValueError('Сначала приостанови сохранение оригиналов')`
- `ValueError('Источник должен быть копией этой медиатеки')`
- `ValueError('Циклические связи копирования запрещены')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries-make-first-copy"></a>

## `PhotoLibraries.make_first_copy`

[media_manager/photo_libraries.py:319](../../media_manager/photo_libraries.py#L319)

Перенумеровывает копии медиатеки, ставя выбранную первой без изменения маршрутов. Изменяет SQLite-таблицы: photos_copy_links.

```python
def make_first_copy(self, source_id, link_id)
```

SQLite: чтение `photos_copy_links`, `photos_original_jobs`; запись/DDL `photos_copy_links`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone`, `enumerate`, `links.insert`, `links.remove`, [self._db](../../media_manager/photo_libraries.py#L45), [self.profile](../../media_manager/photo_libraries.py#L80).

Явные `raise`:

- `ValueError('Сначала приостанови сохранение оригиналов')`
- `KeyError('Копия медиатеки не найдена')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-photolibraries-bind-copy"></a>

## `PhotoLibraries.bind_copy`

[media_manager/photo_libraries.py:336](../../media_manager/photo_libraries.py#L336)

Привязывает доступную проверенную папку к медиатеке с отдельным номером. Изменяет SQLite-таблицы: photos_copy_links.

```python
def bind_copy(self, source_id, volume_id, path)
```

SQLite: чтение `photos_copy_links`; запись/DDL `photos_copy_links`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute('SELECT * FROM photos_copy_links WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, `db.execute('SELECT COALESCE(MAX(number),0)+1 FROM photos_copy_links WHERE source_id=?', (source_id,)).fetchone`, `dict`, `item['path'].startswith`, `next`, [now](../../media_manager/photo_libraries.py#L18), `open_readonly`, `path.startswith`, `relative_path`, [self._db](../../media_manager/photo_libraries.py#L45), [self.profile](../../media_manager/photo_libraries.py#L80), `self.storage.refresh`, `uuid.uuid4`.

Явные `raise`:

- `ValueError('Выбери отдельную папку копии, не корень диска')`
- `ValueError('Том копии должен быть подключён')`
- `ValueError('Эта папка пересекается с другой копией медиатеки. Выбери отдельную папку.')`

Выражения возврата (ветви, без исполнения):

- `dict(existing, connected=1)`
- `link`


<a id="symbol-photolibraries-unbind-copy"></a>

## `PhotoLibraries.unbind_copy`

[media_manager/photo_libraries.py:362](../../media_manager/photo_libraries.py#L362)

Отключает привязку копии медиатеки, сохраняя запись и квитанции ресурсов. Изменяет SQLite-таблицы: photos_copy_links.

```python
def unbind_copy(self, source_id, link_id)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `photos_copy_links`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, [self._db](../../media_manager/photo_libraries.py#L45), [self.profile](../../media_manager/photo_libraries.py#L80).

Явные `raise`:

- `KeyError('Копия медиатеки не найдена')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
