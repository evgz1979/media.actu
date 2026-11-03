# Служебные описания папок: `media_manager/folder_markers.py`

Транзакционная очередь и фоновая запись .media-actu-folder.json. Проверяет принадлежность папки и маркера, повторяет запись после временных ошибок.

[Исходный модуль](../../media_manager/folder_markers.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [media_manager/copies.py](media_manager--copies.md).
Тестовые модули с прямым импортом: [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L14).

## Оглавление определений

- [timestamp](#symbol-timestamp) — Возвращает время UTC для версии служебного описания папки.
- [queue_marker](#symbol-queue-marker) — Ставит изменённое описание папки в очередь в транзакции вызывающего каталога.
- [read_folder_marker](#symbol-read-folder-marker) — Читает ограниченный JSON-маркер и проверяет схему и идентификаторы.
- [write_folder_marker](#symbol-write-folder-marker) — Публикует служебное описание после проверки владения прежним маркером.
- [FolderMarkerService](#symbol-foldermarkerservice) — Согласует постоянную очередь маркеров с доступными зарегистрированными папками.
- [FolderMarkerService.__init__](#symbol-foldermarkerservice---init--) — Инициализирует FolderMarkerService и его рабочее состояние.
- [FolderMarkerService.start](#symbol-foldermarkerservice-start) — Запускает фоновый поток синхронизации описаний папок.
- [FolderMarkerService.wake](#symbol-foldermarkerservice-wake) — Пробуждает поток после изменения связей или описания папки.
- [FolderMarkerService.close](#symbol-foldermarkerservice-close) — Запрашивает остановку и ожидает завершения потока маркеров.
- [FolderMarkerService._run](#symbol-foldermarkerservice--run) — Периодически согласует очередь маркеров, переживая временные ошибки.
- [FolderMarkerService._current](#symbol-foldermarkerservice--current) — Проверяет, что ревизия задания маркера ещё актуальна.
- [FolderMarkerService._may_replace](#symbol-foldermarkerservice--may-replace) — Проверяет допустимость замены маркера прежней освобождённой привязки.
- [FolderMarkerService._owns_path](#symbol-foldermarkerservice--owns-path) — Подтверждает принадлежность текущего пути действующей или архивной привязке.
- [FolderMarkerService.reconcile](#symbol-foldermarkerservice-reconcile) — Проверяет тома и записывает актуальные маркеры с повторными попытками.
- [FolderMarkerService.reconcile.before_publish](#symbol-foldermarkerservice-reconcile-before-publish) — Повторно проверяет ревизию задания, принадлежность пути и ID папки перед публикацией маркера.
- [FolderMarkerService.status](#symbol-foldermarkerservice-status) — Возвращает сводку состояний и ошибок постоянной очереди маркеров.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [FOLDER_MARKER_LIMIT](../../media_manager/folder_markers.py#L17) | `16384` |
| [FOLDER_MARKER_SCHEMA](../../media_manager/folder_markers.py#L18) | `"\nCREATE TABLE IF NOT EXISTS folder_marker_jobs (\n    location_id TEXT PRIMARY KEY, group_id TEXT NOT NULL, volume_id TEXT NOT NULL,\n    path TEXT NOT NULL, payload TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,\n    state TEXT NOT NULL DEFAULT 'pending', error TEXT, synced_at TEXT,\n    next_check REAL NOT NULL DEFAULT 0\n);\n"` |

<a id="symbol-timestamp"></a>

## `timestamp`

[media_manager/folder_markers.py:30](../../media_manager/folder_markers.py#L30)

Возвращает время UTC для версии служебного описания папки. Использует datetime.now, datetime.now(timezone.utc).isoformat.

```python
def timestamp()
```

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`.

Выражения возврата (ветви, без исполнения):

- `datetime.now(timezone.utc).isoformat()`


<a id="symbol-queue-marker"></a>

## `queue_marker`

[media_manager/folder_markers.py:36](../../media_manager/folder_markers.py#L36)

Ставит изменённое описание папки в очередь в транзакции вызывающего каталога. Изменяет SQLite-таблицы: folder_marker_jobs.

```python
def queue_marker(db, payload)
```

SQLite: чтение `folder_marker_jobs`; запись/DDL `folder_marker_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT payload FROM folder_marker_jobs WHERE location_id=?', (payload['folder_id'],)).fetchone`, `json.dumps`, `json.loads`, `saved.pop`, [timestamp](../../media_manager/folder_markers.py#L30).

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-read-folder-marker"></a>

## `read_folder_marker`

[media_manager/folder_markers.py:54](../../media_manager/folder_markers.py#L54)

Читает ограниченный JSON-маркер и проверяет схему и идентификаторы. Явно отклоняет недопустимое состояние через OSError, ValueError.

```python
def read_folder_marker(root)
```

Прямые выражения вызова: `OSError`, `UUID`, `ValueError`, `any`, `document.get`, `isinstance`, `json.loads`, `len`, `ord`, `os.close`, `os.fdopen`, `os.fstat`, `os.open`, `stat.S_ISREG`, `stream.read`, `type`.

Явные `raise`:

- `OSError('Некорректный служебный файл папки')`
- `OSError('Служебный файл папки слишком большой')`
- `ValueError('version')`
- `ValueError(key)`
- `ValueError('status')`
- `ValueError('number')`
- `ValueError('role')`
- `OSError('Не удалось подтвердить служебный файл папки')`

Перехватываемые типы: `FileNotFoundError`, `(ValueError, TypeError, KeyError, AttributeError)`.

Выражения возврата (ветви, без исполнения):

- `None`
- `document`


<a id="symbol-write-folder-marker"></a>

## `write_folder_marker`

[media_manager/folder_markers.py:95](../../media_manager/folder_markers.py#L95)

Публикует служебное описание после проверки владения прежним маркером. Явно отклоняет недопустимое состояние через OSError, ValueError.

```python
def write_folder_marker(root, payload, *, may_replace=lambda previous: False, before_publish=lambda : None)
```

Прямые выражения вызова: `(json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode`, `OSError`, `ValueError`, `before_publish`, `json.dumps`, `len`, `may_replace`, `os.fdopen`, `os.fstat`, `os.fsync`, `os.open`, `os.replace`, `os.stat`, `os.unlink`, `publish_exclusive`, [read_folder_marker](../../media_manager/folder_markers.py#L54), `stream.fileno`, `stream.flush`, `stream.write`, `uuid4`.

Явные `raise`:

- `OSError('В папке уже есть служебный файл другой привязки. Он сохранён.')`
- `OSError('Служебный файл папки относится к другому набору или тому')`
- `ValueError('Описание папки не помещается в служебный файл')`
- `OSError('Служебный файл папки изменился во время записи')`
- `OSError('Не удалось подтвердить запись служебного файла папки')`

Перехватываемые типы: `OSError`, `BaseException`, `FileNotFoundError`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-foldermarkerservice"></a>

## `FolderMarkerService`

[media_manager/folder_markers.py:158](../../media_manager/folder_markers.py#L158)

Согласует постоянную очередь маркеров с доступными зарегистрированными папками. Зависимости конструктора: copies.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_stop`, `_sync_lock`, `_thread`, `_wake`, `copies`, `storage`.

Именованные методы: `__init__`, `start`, `wake`, `close`, `_run`, `_current`, `_may_replace`, `_owns_path`, `reconcile`, `status`.

<a id="symbol-foldermarkerservice---init--"></a>

## `FolderMarkerService.__init__`

[media_manager/folder_markers.py:161](../../media_manager/folder_markers.py#L161)

Инициализирует FolderMarkerService и его рабочее состояние. Обновляет состояние объекта: _stop, _sync_lock, _thread, _wake, copies, storage.

```python
def __init__(self, copies)
```

Присваивания полям `self`: `_stop`, `_sync_lock`, `_thread`, `_wake`, `copies`, `storage`.

Прямые выражения вызова: `threading.Event`, `threading.Lock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldermarkerservice-start"></a>

## `FolderMarkerService.start`

[media_manager/folder_markers.py:169](../../media_manager/folder_markers.py#L169)

Запускает фоновый поток синхронизации описаний папок. Обновляет состояние объекта: _thread.

```python
def start(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._thread.start`, `self.copies.queue_folder_markers`, `threading.Thread`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldermarkerservice-wake"></a>

## `FolderMarkerService.wake`

[media_manager/folder_markers.py:176](../../media_manager/folder_markers.py#L176)

Пробуждает поток после изменения связей или описания папки. Использует self._wake.set.

```python
def wake(self)
```

Прямые выражения вызова: `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldermarkerservice-close"></a>

## `FolderMarkerService.close`

[media_manager/folder_markers.py:181](../../media_manager/folder_markers.py#L181)

Запрашивает остановку и ожидает завершения потока маркеров. Использует self._stop.set, self._thread.join, self._wake.set.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`, `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldermarkerservice--run"></a>

## `FolderMarkerService._run`

[media_manager/folder_markers.py:189](../../media_manager/folder_markers.py#L189)

Периодически согласует очередь маркеров, переживая временные ошибки. Обрабатывает ошибки: Exception.

```python
def _run(self)
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._wake.clear`, `self._wake.wait`, [self.reconcile](../../media_manager/folder_markers.py#L235).

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldermarkerservice--current"></a>

## `FolderMarkerService._current`

[media_manager/folder_markers.py:200](../../media_manager/folder_markers.py#L200)

Проверяет, что ревизия задания маркера ещё актуальна. Читает SQLite-таблицы: folder_marker_jobs.

```python
def _current(self, job)
```

SQLite: чтение `folder_marker_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `db.execute('SELECT revision FROM folder_marker_jobs WHERE location_id=?', (job['location_id'],)).fetchone`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `bool(row and row['revision'] == job['revision'])`


<a id="symbol-foldermarkerservice--may-replace"></a>

## `FolderMarkerService._may_replace`

[media_manager/folder_markers.py:207](../../media_manager/folder_markers.py#L207)

Проверяет допустимость замены маркера прежней освобождённой привязки. Читает SQLite-таблицы: folder_marker_jobs.

```python
def _may_replace(self, previous, payload)
```

SQLite: чтение `folder_marker_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `db.execute('SELECT payload FROM folder_marker_jobs WHERE location_id=?', (previous['folder_id'],)).fetchone`, `json.loads`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `False`
- `bool(known and known['status'] in {'released', 'removed'} and ((known['group_id'], known['volume_id']) == (previous['group_id'], previous['volume_id'])))`


<a id="symbol-foldermarkerservice--owns-path"></a>

## `FolderMarkerService._owns_path`

[media_manager/folder_markers.py:218](../../media_manager/folder_markers.py#L218)

Подтверждает принадлежность текущего пути действующей или архивной привязке. Читает SQLite-таблицы: copy_locations, folder_marker_jobs, released_copy_locations.

```python
def _owns_path(self, job)
```

SQLite: чтение `copy_locations`, `folder_marker_jobs`, `released_copy_locations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `db.execute("SELECT location_id FROM folder_marker_jobs WHERE volume_id=? AND path=?\n                                  ORDER BY json_extract(payload,'$.created_at') DESC,location_id DESC LIMIT 1", (job['volume_id'], job['path'])).fetchone`, `db.execute('SELECT id FROM copy_locations WHERE volume_id=? AND path=?', (job['volume_id'], job['path'])).fetchone`, `db.execute('SELECT id FROM released_copy_locations WHERE volume_id=? AND path=?\n                                  ORDER BY released_at DESC,id DESC LIMIT 1', (job['volume_id'], job['path'])).fetchone`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `owner['id'] == job['location_id']`
- `bool(owner and owner['location_id'] == job['location_id'])`


<a id="symbol-foldermarkerservice-reconcile"></a>

## `FolderMarkerService.reconcile`

[media_manager/folder_markers.py:235](../../media_manager/folder_markers.py#L235)

Проверяет тома и записывает актуальные маркеры с повторными попытками. Изменяет SQLite-таблицы: folder_marker_jobs.

```python
def reconcile(self)
```

SQLite: чтение `folder_marker_jobs`; запись/DDL `folder_marker_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `isinstance`, `json.loads`, `open_readonly`, `os.fstat`, [self._current](../../media_manager/folder_markers.py#L200), [self._owns_path](../../media_manager/folder_markers.py#L218), `self._stop.is_set`, `self._sync_lock.acquire`, `self._sync_lock.release`, `self.storage.connect`, `self.storage.refresh`, `str`, `time.time`, [timestamp](../../media_manager/folder_markers.py#L30), `volume.get`, `volumes.get`, [write_folder_marker](../../media_manager/folder_markers.py#L95).

Перехватываемые типы: `(OSError, ValueError)`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-foldermarkerservice-reconcile-before-publish"></a>

## `FolderMarkerService.reconcile.before_publish`

[media_manager/folder_markers.py:267](../../media_manager/folder_markers.py#L267)

Повторно проверяет ревизию задания, принадлежность пути и ID папки перед публикацией маркера. Явно отклоняет недопустимое состояние через OSError.

```python
def before_publish()
```

Прямые выражения вызова: `OSError`, `open_readonly`, `os.fstat`, [self._current](../../media_manager/folder_markers.py#L200), [self._owns_path](../../media_manager/folder_markers.py#L218), `self._stop.is_set`.

Явные `raise`:

- `OSError('Описание папки изменилось. Запись будет повторена.')`
- `OSError('Папка заменена во время записи')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldermarkerservice-status"></a>

## `FolderMarkerService.status`

[media_manager/folder_markers.py:291](../../media_manager/folder_markers.py#L291)

Возвращает сводку состояний и ошибок постоянной очереди маркеров. Поля результата: folders, counts.

```python
def status(self)
```

SQLite: чтение `folder_marker_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `self.storage.connect`, `sum`.

Выражения возврата (ветви, без исполнения):

- `{'folders': rows, 'counts': {state: sum((row['state'] == state for row in rows)) for state in ('ready', 'pending', 'error', 'superseded')}}`
