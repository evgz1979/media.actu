# Медиаиндекс и очередь превью: `media_manager/catalog.py`

Владелец catalog.sqlite3: источники, медиаобъекты, ревизия и постоянная очередь превью. Photos-таблицы расширяются профильными службами.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/catalog.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/scanner.py](media_manager--scanner.md).
Импортируется модулями: [app.py](app.md), [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md), [media_manager/thumbnails.py](media_manager--thumbnails.md).
Тестовые модули с прямым импортом: [tests/test_catalog.py](tests.md#module-tests.test_catalog), [tests/test_photo_libraries.py](tests.md#module-tests.test_photo_libraries), [tests/test_photos_browser.py](tests.md#module-tests.test_photos_browser), [tests/test_photos_originals.py](tests.md#module-tests.test_photos_originals), [tests/test_thumbnails.py](tests.md#module-tests.test_thumbnails).

## Оглавление определений

- [Catalog](#symbol-Catalog) — Хранит источники, медиаиндекс и задания превью в SQLite.
- [Catalog.__init__](#symbol-Catalog.__init__) — Инициализирует Catalog и его рабочее состояние.
- [Catalog.add_source](#symbol-Catalog.add_source) — Регистрирует доступную папку с ролью, названием и комментарием.
- [Catalog.add_system_photos_source](#symbol-Catalog.add_system_photos_source) — Возвращает прежний источник Photos или создаёт photos://system.
- [Catalog.claim_thumbnail_job](#symbol-Catalog.claim_thumbnail_job) — Атомарно выдаёт следующее допустимое задание выбранному виду воркера.
- [Catalog.connect](#symbol-Catalog.connect) — Открывает соединение медиаиндекса с Row, внешними ключами и WAL.
- [Catalog.defer_thumbnail_job](#symbol-Catalog.defer_thumbnail_job) — Откладывает повторную попытку превью с сохранением причины и срока.
- [Catalog.enqueue_all_thumbnails](#symbol-Catalog.enqueue_all_thumbnails) — Пополняет очередь превью для всех зарегистрированных источников.
- [Catalog.enqueue_media_thumbnail](#symbol-Catalog.enqueue_media_thumbnail) — Ставит отдельный медиаобъект в очередь с повышенным приоритетом.
- [Catalog.enqueue_source_thumbnails](#symbol-Catalog.enqueue_source_thumbnails) — Ставит подходящие объекты источника в версионируемую очередь превью.
- [Catalog.finish_thumbnail_job](#symbol-Catalog.finish_thumbnail_job) — Фиксирует готовность превью либо ошибку обработки задания.
- [Catalog.folder_tree](#symbol-Catalog.folder_tree) — Строит дерево виртуальных папок по сохранённым путям медиаиндекса.
- [Catalog.folder_tree.build](#symbol-Catalog.folder_tree.build) — Рекурсивно собирает дочерние узлы одной ветви индексированного дерева.
- [Catalog.get_media](#symbol-Catalog.get_media) — Возвращает объект вместе с видом и путём его источника.
- [Catalog.get_source](#symbol-Catalog.get_source) — Возвращает запись источника по ID либо None.
- [Catalog.initialize](#symbol-Catalog.initialize) — Создаёт схему медиаиндекса и добавляет недостающие поля старых баз.
- [Catalog.list_files](#symbol-Catalog.list_files) — Выбирает ограниченный список медиаобъектов указанной папки.
- [Catalog.list_sources](#symbol-Catalog.list_sources) — Собирает источники с количеством объектов, объёмом и состоянием превью.
- [Catalog.photos_queue_paused](#symbol-Catalog.photos_queue_paused) — Проверяет, заблокирована ли очередь Photos состоянием медиатек.
- [Catalog.prioritize_folder_thumbnails](#symbol-Catalog.prioritize_folder_thumbnails) — Повышает приоритет превью выбранной виртуальной папки.
- [Catalog.release_thumbnail_job](#symbol-Catalog.release_thumbnail_job) — Возвращает занятое задание в ожидание после временной недоступности.
- [Catalog.remove_source](#symbol-Catalog.remove_source) — Удаляет источник и связанные записи медиаиндекса из каталога.
- [Catalog.replace_photos_scan](#symbol-Catalog.replace_photos_scan) — Обновляет объекты Photos, сохраняя ID уже известных записей.
- [Catalog.replace_source_scan](#symbol-Catalog.replace_source_scan) — Сверяет результат обхода папки с медиаиндексом в одной транзакции.
- [Catalog.reset_running_thumbnail_jobs](#symbol-Catalog.reset_running_thumbnail_jobs) — Возвращает прерванные задания превью в очередь ожидания.
- [Catalog.reset_stale_source_scans](#symbol-Catalog.reset_stale_source_scans) — Снимает оставшиеся после перезапуска состояния сканирования.
- [Catalog.resolve_media_file](#symbol-Catalog.resolve_media_file) — Проверяет и возвращает путь обычного файла внутри источника.
- [Catalog.resolve_source_folder](#symbol-Catalog.resolve_source_folder) — Разрешает относительный путь внутри обычного источника для открытия в Finder.
- [Catalog.revision](#symbol-Catalog.revision) — Возвращает числовую ревизию медиаиндекса для опроса UI.
- [Catalog.set_source_status](#symbol-Catalog.set_source_status) — Сохраняет состояние сканирования источника и сообщение об ошибке.
- [Catalog.set_thumbnail_queue_paused](#symbol-Catalog.set_thumbnail_queue_paused) — Сохраняет общую ручную паузу очереди превью.
- [Catalog.summary](#symbol-Catalog.summary) — Возвращает суммарное количество источников, фото, видео и байтов.
- [Catalog.thumbnail_queue_paused](#symbol-Catalog.thumbnail_queue_paused) — Читает сохранённый флаг общей паузы превью.
- [Catalog.thumbnail_queue_summary](#symbol-Catalog.thumbnail_queue_summary) — Агрегирует состояния заданий и сведения об отложенных превью.
- [Catalog.update_source_metadata](#symbol-Catalog.update_source_metadata) — Обновляет роль, название и комментарий зарегистрированного источника.

## Константы и значения по умолчанию

<a id="constant-SCHEMA"></a>

### `SCHEMA`

`Объёмное значение см. в исходном модуле`


<a id="symbol-Catalog"></a>

## `Catalog`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog`

Хранит источники, медиаиндекс и задания превью в SQLite. Зависимости конструктора: database_path.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_write_lock`, `database_path`.

Именованные методы: `__init__`, `connect`, `initialize`, `add_source`, `add_system_photos_source`, `update_source_metadata`, `remove_source`, `get_source`, `resolve_source_folder`, `list_sources`, `set_source_status`, `replace_source_scan`, `replace_photos_scan`, `enqueue_source_thumbnails`, `enqueue_all_thumbnails`, `prioritize_folder_thumbnails`, `enqueue_media_thumbnail`, `reset_stale_source_scans`, `reset_running_thumbnail_jobs`, `claim_thumbnail_job`, `defer_thumbnail_job`, `photos_queue_paused`, `finish_thumbnail_job`, `release_thumbnail_job`, `thumbnail_queue_summary`, `set_thumbnail_queue_paused`, `thumbnail_queue_paused`, `revision`, `summary`, `folder_tree`, `list_files`, `get_media`, `resolve_media_file`.

<a id="symbol-Catalog.__init__"></a>

## `Catalog.__init__`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.__init__`

Инициализирует Catalog и его рабочее состояние. Обновляет состояние объекта: _write_lock, database_path.

```python
def __init__(self, database_path: str | Path) -> None
```

Присваивания полям `self`: `_write_lock`, `database_path`.

Прямые выражения вызова: `Path`, `self.database_path.parent.mkdir`, [self.initialize](media_manager--catalog.md#symbol-Catalog.initialize), `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.add_source"></a>

## `Catalog.add_source`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.add_source`

Регистрирует доступную папку с ролью, названием и комментарием. Изменяет SQLite-таблицы: sources.

```python
def add_source(self, raw_path: str | Path, *, role: str='source', label: str='', comment: str='') -> dict[str, object]
```

SQLite: чтение `sources`; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `comment.strip`, `connection.execute`, `connection.execute('SELECT * FROM sources WHERE path = ?', (str(source),)).fetchone`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `dict`, `label.strip`, `normalize_source`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), `str`.

Явные `raise`:

- `ValueError(f'Неизвестная роль папки: {role}')`

Выражения возврата (ветви, без исполнения):

- `dict(row)`


<a id="symbol-Catalog.add_system_photos_source"></a>

## `Catalog.add_system_photos_source`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.add_system_photos_source`

Возвращает прежний источник Photos или создаёт photos://system. Изменяет SQLite-таблицы: sources.

```python
def add_system_photos_source(self) -> dict[str, object]
```

SQLite: чтение `sources`; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute("SELECT * FROM sources WHERE kind='photos' ORDER BY id LIMIT 1").fetchone`, `connection.execute("SELECT * FROM sources WHERE path = 'photos://system'").fetchone`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `dict`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `dict(existing)`
- `dict(row)`


<a id="symbol-Catalog.claim_thumbnail_job"></a>

## `Catalog.claim_thumbnail_job`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.claim_thumbnail_job`

Атомарно выдаёт следующее допустимое задание выбранному виду воркера. Изменяет SQLite-таблицы: thumbnail_jobs, thumbnail_waits.

```python
def claim_thumbnail_job(self, source_kind: str) -> int | None
```

SQLite: чтение `media_files`, `photos_libraries`, `sources`, `thumbnail_jobs`, `thumbnail_waits`; запись/DDL `thumbnail_jobs`, `thumbnail_waits`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute("\n                SELECT thumbnail_jobs.media_id,media_files.source_id\n                FROM thumbnail_jobs\n                JOIN media_files ON media_files.id = thumbnail_jobs.media_id\n                JOIN sources ON sources.id = media_files.source_id\n                LEFT JOIN photos_libraries ON photos_libraries.source_id=sources.id\n                LEFT JOIN thumbnail_waits ON thumbnail_waits.media_id=media_files.id\n                WHERE thumbnail_jobs.status = 'pending'\n                  AND sources.kind = ?\n                  AND sources.status != 'scanning'\n                  AND (sources.kind!='photos' OR (photos_libraries.active=1 AND photos_libraries.paused=0 AND photos_libraries.state='ready'))\n                  AND (thumbnail_waits.media_id IS NULL OR thumbnail_waits.retry_at<=unixepoch('now'))\n                ORDER BY thumbnail_jobs.priority DESC,\n                         thumbnail_jobs.queued_at,\n                         thumbnail_jobs.media_id\n                LIMIT 1\n                ", (source_kind,)).fetchone`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `getattr`, `int`, `schedule.blocked`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `None`
- `media_id`


<a id="symbol-Catalog.connect"></a>

## `Catalog.connect`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.connect`

Открывает соединение медиаиндекса с Row, внешними ключами и WAL. Использует connection.execute, sqlite3.connect.

```python
def connect(self) -> sqlite3.Connection
```

Прямые выражения вызова: `connection.execute`, `sqlite3.connect`.

Выражения возврата (ветви, без исполнения):

- `connection`


<a id="symbol-Catalog.defer_thumbnail_job"></a>

## `Catalog.defer_thumbnail_job`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.defer_thumbnail_job`

Откладывает повторную попытку превью с сохранением причины и срока. Изменяет SQLite-таблицы: thumbnail_jobs, thumbnail_waits.

```python
def defer_thumbnail_job(self, media_id: int, reason: str, seconds: int=3600) -> None
```

SQLite: чтение не найдено; запись/DDL `thumbnail_jobs`, `thumbnail_waits`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), `time.time`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.enqueue_all_thumbnails"></a>

## `Catalog.enqueue_all_thumbnails`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.enqueue_all_thumbnails`

Пополняет очередь превью для всех зарегистрированных источников. Использует self.enqueue_source_thumbnails, self.list_sources.

```python
def enqueue_all_thumbnails(self) -> None
```

Прямые выражения вызова: `int`, [self.enqueue_source_thumbnails](media_manager--catalog.md#symbol-Catalog.enqueue_source_thumbnails), [self.list_sources](media_manager--catalog.md#symbol-Catalog.list_sources).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.enqueue_media_thumbnail"></a>

## `Catalog.enqueue_media_thumbnail`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.enqueue_media_thumbnail`

Ставит отдельный медиаобъект в очередь с повышенным приоритетом. Изменяет SQLite-таблицы: thumbnail_jobs.

```python
def enqueue_media_thumbnail(self, media_id: int, priority: int=200) -> None
```

SQLite: чтение не найдено; запись/DDL `thumbnail_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `media.get`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), [self.get_media](media_manager--catalog.md#symbol-Catalog.get_media).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-Catalog.enqueue_source_thumbnails"></a>

## `Catalog.enqueue_source_thumbnails`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.enqueue_source_thumbnails`

Ставит подходящие объекты источника в версионируемую очередь превью. Изменяет SQLite-таблицы: thumbnail_jobs.

```python
def enqueue_source_thumbnails(self, source_id: int, priority: int=0) -> int
```

SQLite: чтение `media_files`, `sources`, `thumbnail_jobs`; запись/DDL `thumbnail_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute("\n                SELECT COUNT(*) AS count\n                FROM thumbnail_jobs\n                JOIN media_files ON media_files.id = thumbnail_jobs.media_id\n                WHERE media_files.source_id = ?\n                  AND thumbnail_jobs.status IN ('pending', 'running')\n                ", (source_id,)).fetchone`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `int`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `int(row['count']) if row else 0`


<a id="symbol-Catalog.finish_thumbnail_job"></a>

## `Catalog.finish_thumbnail_job`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.finish_thumbnail_job`

Фиксирует готовность превью либо ошибку обработки задания. Изменяет SQLite-таблицы: thumbnail_jobs.

```python
def finish_thumbnail_job(self, media_id: int, *, error: str | None=None) -> None
```

SQLite: чтение не найдено; запись/DDL `thumbnail_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.folder_tree"></a>

## `Catalog.folder_tree`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.folder_tree`

Строит дерево виртуальных папок по сохранённым путям медиаиндекса. Читает SQLite-таблицы: media_files.

```python
def folder_tree(self, source_id: int) -> list[dict[str, object]]
```

SQLite: чтение `media_files`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePath`, `build`, `children.setdefault`, `children.setdefault(parent, []).append`, `connection.execute`, `connection.execute('SELECT DISTINCT parent_path FROM media_files WHERE source_id = ?', (source_id,)).fetchall`, `folders.add`, `len`, `range`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), `str`.

Выражения возврата (ветви, без исполнения):

- `[{'id': '__root__', 'label': 'Корень', 'children': build('')}]`


<a id="symbol-Catalog.folder_tree.build"></a>

## `Catalog.folder_tree.build`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.folder_tree.build`

Рекурсивно собирает дочерние узлы одной ветви индексированного дерева. Использует PurePath, build, children.get, result.append.

```python
def build(parent: str) -> list[dict[str, object]]
```

Прямые выражения вызова: `PurePath`, [build](media_manager--catalog.md#symbol-Catalog.folder_tree.build), `children.get`, `result.append`, `sorted`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-Catalog.get_media"></a>

## `Catalog.get_media`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.get_media`

Возвращает объект вместе с видом и путём его источника. Читает SQLite-таблицы: media_files, sources.

```python
def get_media(self, media_id: int) -> dict[str, object] | None
```

SQLite: чтение `media_files`, `sources`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute('\n                SELECT media_files.*, sources.path AS source_path,\n                       sources.kind AS source_kind\n                FROM media_files\n                JOIN sources ON sources.id = media_files.source_id\n                WHERE media_files.id = ?\n                ', (media_id,)).fetchone`, `dict`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `dict(row) if row else None`


<a id="symbol-Catalog.get_source"></a>

## `Catalog.get_source`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.get_source`

Возвращает запись источника по ID либо None. Читает SQLite-таблицы: sources.

```python
def get_source(self, source_id: int) -> dict[str, object] | None
```

SQLite: чтение `sources`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute('SELECT * FROM sources WHERE id = ?', (source_id,)).fetchone`, `dict`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `dict(row) if row else None`


<a id="symbol-Catalog.initialize"></a>

## `Catalog.initialize`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.initialize`

Создаёт схему медиаиндекса и добавляет недостающие поля старых баз. Изменяет SQLite-таблицы: sources.

```python
def initialize(self) -> None
```

SQLite: чтение не найдено; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute('PRAGMA table_info(sources)').fetchall`, `connection.executescript`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.list_files"></a>

## `Catalog.list_files`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.list_files`

Выбирает ограниченный список медиаобъектов указанной папки. Читает SQLite-таблицы: media_files.

```python
def list_files(self, source_id: int, folder: str='', limit: int=300) -> list[dict[str, object]]
```

SQLite: чтение `media_files`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute('\n                SELECT id, relative_path, parent_path, name, kind, size, modified_at\n                FROM media_files\n                WHERE source_id = ? AND parent_path = ?\n                ORDER BY kind, name COLLATE NOCASE\n                LIMIT ?\n                ', (source_id, folder, min(max(limit, 1), 1000))).fetchall`, `dict`, `max`, `min`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `[dict(row) for row in rows]`


<a id="symbol-Catalog.list_sources"></a>

## `Catalog.list_sources`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.list_sources`

Собирает источники с количеством объектов, объёмом и состоянием превью. Читает SQLite-таблицы: media_files, photos_libraries, sources, thumbnail_jobs.

```python
def list_sources(self) -> list[dict[str, object]]
```

SQLite: чтение `media_files`, `photos_libraries`, `sources`, `thumbnail_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute(query).fetchall`, `dict`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `[dict(row) for row in connection.execute(query).fetchall()]`


<a id="symbol-Catalog.photos_queue_paused"></a>

## `Catalog.photos_queue_paused`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.photos_queue_paused`

Проверяет, заблокирована ли очередь Photos состоянием медиатек. Читает SQLite-таблицы: photos_libraries.

```python
def photos_queue_paused(self) -> bool
```

SQLite: чтение `photos_libraries`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `db.execute("SELECT source_id FROM photos_libraries WHERE active=1 AND paused=0 AND state='ready'").fetchone`, `getattr`, `schedule.blocked`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `row is None or bool(schedule and schedule.blocked(row['source_id']))`


<a id="symbol-Catalog.prioritize_folder_thumbnails"></a>

## `Catalog.prioritize_folder_thumbnails`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.prioritize_folder_thumbnails`

Повышает приоритет превью выбранной виртуальной папки. Изменяет SQLite-таблицы: thumbnail_jobs.

```python
def prioritize_folder_thumbnails(self, source_id: int, folder: str, priority: int=100) -> None
```

SQLite: чтение `media_files`, `sources`; запись/DDL `thumbnail_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.release_thumbnail_job"></a>

## `Catalog.release_thumbnail_job`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.release_thumbnail_job`

Возвращает занятое задание в ожидание после временной недоступности. Изменяет SQLite-таблицы: thumbnail_jobs.

```python
def release_thumbnail_job(self, media_id: int) -> None
```

SQLite: чтение не найдено; запись/DDL `thumbnail_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.remove_source"></a>

## `Catalog.remove_source`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.remove_source`

Удаляет источник и связанные записи медиаиндекса из каталога. Файлы источника не удаляются; зависимые записи подчиняются внешним ключам SQLite.

```python
def remove_source(self, source_id: int) -> None
```

SQLite: чтение `sources`; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.replace_photos_scan"></a>

## `Catalog.replace_photos_scan`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.replace_photos_scan`

Обновляет объекты Photos, сохраняя ID уже известных записей. Изменяет SQLite-таблицы: media_files, metadata, sources.

```python
def replace_photos_scan(self, source_id: int, assets: list[dict[str, object]]) -> None
```

SQLite: чтение `media_files`; запись/DDL `media_files`, `metadata`, `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `asset.get`, `connection.execute`, `connection.executemany`, `created.astimezone`, `created.astimezone().isoformat`, `datetime.fromisoformat`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `int`, `rows.append`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), `str`, `uuid.uuid4`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.replace_source_scan"></a>

## `Catalog.replace_source_scan`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.replace_source_scan`

Сверяет результат обхода папки с медиаиндексом в одной транзакции. Изменяет SQLite-таблицы: media_files, metadata, sources.

```python
def replace_source_scan(self, source_id: int, report: ScanReport) -> None
```

SQLite: чтение `media_files`; запись/DDL `media_files`, `metadata`, `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePath`, `connection.execute`, `connection.executemany`, `datetime.now`, `datetime.now().astimezone`, `datetime.now().astimezone().isoformat`, `rows.append`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), `str`, `uuid.uuid4`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.reset_running_thumbnail_jobs"></a>

## `Catalog.reset_running_thumbnail_jobs`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.reset_running_thumbnail_jobs`

Возвращает прерванные задания превью в очередь ожидания. Изменяет SQLite-таблицы: thumbnail_jobs.

```python
def reset_running_thumbnail_jobs(self) -> None
```

SQLite: чтение не найдено; запись/DDL `thumbnail_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.reset_stale_source_scans"></a>

## `Catalog.reset_stale_source_scans`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.reset_stale_source_scans`

Снимает оставшиеся после перезапуска состояния сканирования. Изменяет SQLite-таблицы: sources.

```python
def reset_stale_source_scans(self) -> None
```

SQLite: чтение не найдено; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.resolve_media_file"></a>

## `Catalog.resolve_media_file`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.resolve_media_file`

Проверяет и возвращает путь обычного файла внутри источника. Явно отклоняет недопустимое состояние через FileNotFoundError, KeyError, PermissionError.

```python
def resolve_media_file(self, media_id: int) -> Path
```

Прямые выражения вызова: `FileNotFoundError`, `KeyError`, `Path`, `Path(str(media['source_path'])).resolve`, `PermissionError`, `candidate.is_symlink`, `candidate.resolve`, `media.get`, `original.is_file`, `original.is_relative_to`, [self.get_media](media_manager--catalog.md#symbol-Catalog.get_media), `str`.

Явные `raise`:

- `KeyError(media_id)`
- `PermissionError('У виртуального источника нет прямого пути к оригиналу')`
- `PermissionError('Символические ссылки не открываются')`
- `PermissionError('Файл находится вне выбранного источника')`
- `FileNotFoundError(original)`

Выражения возврата (ветви, без исполнения):

- `original`


<a id="symbol-Catalog.resolve_source_folder"></a>

## `Catalog.resolve_source_folder`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.resolve_source_folder`

Разрешает относительный путь внутри обычного источника для открытия в Finder. Явно отклоняет недопустимое состояние через FileNotFoundError, KeyError, PermissionError.

```python
def resolve_source_folder(self, source_id: int, folder: str='') -> Path
```

Прямые выражения вызова: `(source_path / relative).resolve`, `FileNotFoundError`, `KeyError`, `Path`, `Path(str(source['path'])).resolve`, `PermissionError`, `PurePath`, `relative.is_absolute`, [self.get_source](media_manager--catalog.md#symbol-Catalog.get_source), `source.get`, `str`, `target.is_dir`.

Явные `raise`:

- `KeyError(source_id)`
- `PermissionError('Виртуальный источник нельзя открыть в Finder')`
- `PermissionError('Каталог находится вне выбранного источника')`
- `FileNotFoundError(target)`

Выражения возврата (ветви, без исполнения):

- `target`


<a id="symbol-Catalog.revision"></a>

## `Catalog.revision`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.revision`

Возвращает числовую ревизию медиаиндекса для опроса UI. Читает SQLite-таблицы: metadata.

```python
def revision(self) -> int
```

SQLite: чтение `metadata`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute("SELECT value FROM metadata WHERE key = 'catalog_revision'").fetchone`, `int`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `int(row['value']) if row else 0`


<a id="symbol-Catalog.set_source_status"></a>

## `Catalog.set_source_status`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.set_source_status`

Сохраняет состояние сканирования источника и сообщение об ошибке. Изменяет SQLite-таблицы: sources.

```python
def set_source_status(self, source_id: int, status: str, error: str | None=None) -> None
```

SQLite: чтение не найдено; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.set_thumbnail_queue_paused"></a>

## `Catalog.set_thumbnail_queue_paused`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.set_thumbnail_queue_paused`

Сохраняет общую ручную паузу очереди превью. Изменяет SQLite-таблицы: metadata, photos_libraries.

```python
def set_thumbnail_queue_paused(self, paused: bool) -> None
```

SQLite: чтение не найдено; запись/DDL `metadata`, `photos_libraries`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `int`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Catalog.summary"></a>

## `Catalog.summary`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.summary`

Возвращает суммарное количество источников, фото, видео и байтов. Читает SQLite-таблицы: media_files.

```python
def summary(self) -> dict[str, int]
```

SQLite: чтение `media_files`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `connection.execute`, `connection.execute("\n                SELECT COUNT(*) AS total,\n                       COALESCE(SUM(kind = 'photo'), 0) AS photos,\n                       COALESCE(SUM(kind = 'video'), 0) AS videos,\n                       COALESCE(SUM(size), 0) AS bytes\n                FROM media_files\n                ").fetchone`, `int`, `row.keys`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), [self.revision](media_manager--catalog.md#symbol-Catalog.revision).

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-Catalog.thumbnail_queue_paused"></a>

## `Catalog.thumbnail_queue_paused`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.thumbnail_queue_paused`

Читает сохранённый флаг общей паузы превью. Читает SQLite-таблицы: metadata.

```python
def thumbnail_queue_paused(self) -> bool
```

SQLite: чтение `metadata`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `connection.execute`, `connection.execute("SELECT value FROM metadata WHERE key = 'thumbnail_queue_paused'").fetchone`, `int`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect).

Выражения возврата (ветви, без исполнения):

- `bool(int(row['value'])) if row else False`


<a id="symbol-Catalog.thumbnail_queue_summary"></a>

## `Catalog.thumbnail_queue_summary`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.thumbnail_queue_summary`

Агрегирует состояния заданий и сведения об отложенных превью. Поля результата: total, pending, running, done, error, paused.

```python
def thumbnail_queue_summary(self) -> dict[str, int | bool]
```

SQLite: чтение `metadata`, `thumbnail_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `connection.execute`, `connection.execute("SELECT value FROM metadata WHERE key = 'thumbnail_queue_paused'").fetchone`, `connection.execute('SELECT status, COUNT(*) AS count FROM thumbnail_jobs GROUP BY status').fetchall`, `counts.get`, `counts.values`, `int`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), `str`, `sum`.

Выражения возврата (ветви, без исполнения):

- `{'total': sum(counts.values()), 'pending': counts.get('pending', 0), 'running': counts.get('running', 0), 'done': counts.get('done', 0), 'error': counts.get('error', 0), 'paused': bool(int(paused_row['value'])) if paused_row else False}`


<a id="symbol-Catalog.update_source_metadata"></a>

## `Catalog.update_source_metadata`

[media_manager/catalog.py](../../media_manager/catalog.py) · `Catalog.update_source_metadata`

Обновляет роль, название и комментарий зарегистрированного источника. Изменяет SQLite-таблицы: sources.

```python
def update_source_metadata(self, source_id: int, *, role: str, label: str, comment: str) -> dict[str, object]
```

SQLite: чтение не найдено; запись/DDL `sources`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `comment.strip`, `connection.execute`, `label.strip`, [self.connect](media_manager--catalog.md#symbol-Catalog.connect), [self.get_source](media_manager--catalog.md#symbol-Catalog.get_source).

Явные `raise`:

- `ValueError(f'Неизвестная роль папки: {role}')`
- `KeyError(source_id)`

Выражения возврата (ветви, без исполнения):

- `source`
