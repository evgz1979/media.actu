# Поиск совпадений по именам: `media_manager/comparison.py`

Действующая сверка одной области с несколькими целями по именам; также хранит и показывает старые отчёты сверки содержимого. Здесь находятся общие функции безопасного чтения.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/comparison.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_originals.py](media_manager--photos_originals.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_comparison.py](tests.md#module-tests.test_comparison), [tests/test_folder_markers.py](tests.md#module-tests.test_folder_markers), [tests/test_volume_identity.py](tests.md#module-tests.test_volume_identity).

## Оглавление определений

- [ComparisonCatalog](#symbol-ComparisonCatalog) — Ведёт задания, индексы, результаты и историю поиска по именам.
- [ComparisonCatalog.__init__](#symbol-ComparisonCatalog.__init__) — Инициализирует ComparisonCatalog и его рабочее состояние.
- [ComparisonCatalog._assert_idle](#symbol-ComparisonCatalog._assert_idle) — Запрещает новый запуск, пока предыдущий поток сверки работает.
- [ComparisonCatalog._check](#symbol-ComparisonCatalog._check) — Прерывает текущую обработку, если запрошена остановка сверки.
- [ComparisonCatalog._classify_names](#symbol-ComparisonCatalog._classify_names) — Сопоставляет нормализованные имена, типы и непосредственные родительские папки.
- [ComparisonCatalog._counts](#symbol-ComparisonCatalog._counts) — Считает непосредственные дочерние элементы выбранной области индекса.
- [ComparisonCatalog._event](#symbol-ComparisonCatalog._event) — Добавляет событие в журнал сверки в переданной транзакции.
- [ComparisonCatalog._inventory](#symbol-ComparisonCatalog._inventory) — Обходит выбранную область и сохраняет метаданные и ошибки элементов.
- [ComparisonCatalog._reuse_inventory](#symbol-ComparisonCatalog._reuse_inventory) — Переносит подходящий завершённый индекс из прежнего задания.
- [ComparisonCatalog._update](#symbol-ComparisonCatalog._update) — Обновляет поля задания сверки и время изменения.
- [ComparisonCatalog.close](#symbol-ComparisonCatalog.close) — Останавливает поток сверки при завершении Core.
- [ComparisonCatalog.create](#symbol-ComparisonCatalog.create) — Создаёт сверку имён непересекающихся областей и при необходимости запускает её.
- [ComparisonCatalog.detail](#symbol-ComparisonCatalog.detail) — Возвращает подробности элемента и найденные пути в целях сверки.
- [ComparisonCatalog.events](#symbol-ComparisonCatalog.events) — Возвращает страницу журнала сверки с обратной пагинацией.
- [ComparisonCatalog.job](#symbol-ComparisonCatalog.job) — Собирает состояние задания, области поиска и счётчики результатов.
- [ComparisonCatalog.jobs](#symbol-ComparisonCatalog.jobs) — Возвращает недавние задания общей сверки.
- [ComparisonCatalog.pause](#symbol-ComparisonCatalog.pause) — Запрашивает остановку сверки после текущего шага чтения.
- [ComparisonCatalog.resume](#symbol-ComparisonCatalog.resume) — Продолжает сверку имён или создаёт её вместо старой сверки содержимого.
- [ComparisonCatalog.run](#symbol-ComparisonCatalog.run) — Собирает или повторно использует списки и классифицирует совпадения имён.
- [ComparisonCatalog.target_tree](#symbol-ComparisonCatalog.target_tree) — Читает один уровень сохранённого дерева целевой области.
- [ComparisonCatalog.tree](#symbol-ComparisonCatalog.tree) — Возвращает страницу исходного дерева отчёта с фильтром статуса.
- [Paused](#symbol-Paused) — Сигнализирует кооперативную остановку фоновой сверки.
- [fingerprint](#symbol-fingerprint) — Собирает размер, времена и идентификаторы файлового объекта из stat.
- [name_key](#symbol-name_key) — Нормализует имя в Unicode NFC и приводит регистр для сравнения.
- [open_readonly](#symbol-open_readonly) — Открывает проверенный файл или каталог относительно дескрипторов родителей.
- [parent_key](#symbol-parent_key) — Нормализует имя непосредственного родительского каталога.
- [sqlite_file_identifier](#symbol-sqlite_file_identifier) — Сохраняет большие inode и device без округления SQLite.

## Константы и значения по умолчанию

<a id="constant-LABELS"></a>

### `LABELS`

`{'names_found': 'Совпали имена', 'other_folder': 'Имя в другой папке', 'names_missing': 'Не найдено по именам', 'found': 'Есть на NAS', 'cached': 'Есть по сохранённым хэшам', 'missing': 'Не найдено', 'candidate': 'Кандидат на совпадение', 'unverified': 'Не проверено', 'skipped': 'Не сравнивается'}`

<a id="constant-NAME_STATUSES"></a>

### `NAME_STATUSES`

`('names_found', 'other_folder', 'names_missing', 'unverified', 'skipped')`


<a id="symbol-ComparisonCatalog"></a>

## `ComparisonCatalog`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog`

Ведёт задания, индексы, результаты и историю поиска по именам. Зависимости конструктора: storage.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `_stop`, `_thread`, `storage`.

Именованные методы: `__init__`, `_event`, `_update`, `_check`, `create`, `_assert_idle`, `resume`, `pause`, `close`, `run`, `_reuse_inventory`, `_inventory`, `_classify_names`, `jobs`, `job`, `tree`, `_counts`, `detail`, `target_tree`, `events`.

<a id="symbol-ComparisonCatalog.__init__"></a>

## `ComparisonCatalog.__init__`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.__init__`

Инициализирует ComparisonCatalog и его рабочее состояние. Изменяет SQLite-таблицы: comparison_entries, comparison_events, comparison_hashes, comparison_jobs, comparison_results, comparison_scans.

```python
def __init__(self, storage: StorageCatalog)
```

SQLite: чтение `comparison_jobs`; запись/DDL `comparison_entries`, `comparison_events`, `comparison_hashes`, `comparison_jobs`, `comparison_results`, `comparison_scans`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_lock`, `_stop`, `_thread`, `storage`.

Прямые выражения вызова: `additions.items`, `columns.items`, `db.execute`, `db.execute("SELECT id FROM comparison_jobs WHERE state IN ('running','pausing')").fetchall`, `db.executescript`, `now`, [self._event](media_manager--comparison.md#symbol-ComparisonCatalog._event), `self.storage.connect`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog._assert_idle"></a>

## `ComparisonCatalog._assert_idle`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._assert_idle`

Запрещает новый запуск, пока предыдущий поток сверки работает. Явно отклоняет недопустимое состояние через ValueError.

```python
def _assert_idle(self)
```

Прямые выражения вызова: `ValueError`, `self._thread.is_alive`.

Явные `raise`:

- `ValueError('Уже выполняется сверка. Сначала останови её.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog._check"></a>

## `ComparisonCatalog._check`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._check`

Прерывает текущую обработку, если запрошена остановка сверки. Явно отклоняет недопустимое состояние через Paused.

```python
def _check(self)
```

Прямые выражения вызова: [Paused](media_manager--comparison.md#symbol-Paused), `self._stop.is_set`.

Явные `raise`:

- `Paused()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog._classify_names"></a>

## `ComparisonCatalog._classify_names`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._classify_names`

Сопоставляет нормализованные имена, типы и непосредственные родительские папки. Изменяет SQLite-таблицы: comparison_results.

```python
def _classify_names(self, job)
```

SQLite: чтение `comparison_entries`, `comparison_scans`; запись/DDL `comparison_results`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `all`, `db.execute`, `db.executemany`, `dict`, `len`, `names.add`, `next`, `pairs.add`, `results.append`, `results.clear`, [self._check](media_manager--comparison.md#symbol-ComparisonCatalog._check), `self.storage.connect`, `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog._counts"></a>

## `ComparisonCatalog._counts`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._counts`

Считает непосредственные дочерние элементы выбранной области индекса. Читает SQLite-таблицы: comparison_entries, comparison_results.

```python
def _counts(db, scan, path)
```

Декораторы: `staticmethod`.

SQLite: чтение `comparison_entries`, `comparison_results`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`.

Выражения возврата (ветви, без исполнения):

- `{r['status']: r['n'] for r in db.execute('SELECT r.status,COUNT(*) n FROM comparison_entries e JOIN comparison_results r ON r.entry_id=e.id\n            WHERE e.scan_id=?' + condition + ' GROUP BY r.status', params)}`


<a id="symbol-ComparisonCatalog._event"></a>

## `ComparisonCatalog._event`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._event`

Добавляет событие в журнал сверки в переданной транзакции. Изменяет SQLite-таблицы: comparison_events.

```python
def _event(db, job, level, message, path='')
```

Декораторы: `staticmethod`.

SQLite: чтение не найдено; запись/DDL `comparison_events`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `now`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog._inventory"></a>

## `ComparisonCatalog._inventory`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._inventory`

Обходит выбранную область и сохраняет метаданные и ошибки элементов. Изменяет SQLite-таблицы: comparison_entries, comparison_scans, directories.

```python
def _inventory(self, job, scan, volume)
```

SQLite: чтение не найдено; запись/DDL `comparison_entries`, `comparison_scans`, `directories`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `(path + '/' + item.name).lstrip`, `(volume or {}).get`, `PurePosixPath`, `children.append`, `datetime.fromtimestamp`, `datetime.fromtimestamp(e['mtime_ns'] / 1000000000.0, timezone.utc).isoformat`, `db.execute`, `db.executemany`, `dict`, `entries.append`, `item.is_dir`, `item.is_file`, `item.is_symlink`, `json.dumps`, [name_key](media_manager--comparison.md#symbol-name_key), `now`, [open_readonly](media_manager--comparison.md#symbol-open_readonly), `os.scandir`, [parent_key](media_manager--comparison.md#symbol-parent_key), `pending.clear`, `pending.extend`, `pending.pop`, [self._check](media_manager--comparison.md#symbol-ComparisonCatalog._check), [self._event](media_manager--comparison.md#symbol-ComparisonCatalog._event), [self._update](media_manager--comparison.md#symbol-ComparisonCatalog._update), `self.storage.connect`, `service_file`, `str`.

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog._reuse_inventory"></a>

## `ComparisonCatalog._reuse_inventory`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._reuse_inventory`

Переносит подходящий завершённый индекс из прежнего задания. Изменяет SQLite-таблицы: comparison_entries, comparison_scans.

```python
def _reuse_inventory(self, job, scan)
```

SQLite: чтение `comparison_entries`, `comparison_scans`; запись/DDL `comparison_entries`, `comparison_scans`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.create_function`, `db.execute`, `db.execute("SELECT * FROM comparison_scans WHERE volume_id=? AND root_path=?\n                AND state='complete' AND id!=? ORDER BY finished_at DESC,id DESC LIMIT 1", (scan['volume_id'], scan['root_path'], scan['id'])).fetchone`, [self._event](media_manager--comparison.md#symbol-ComparisonCatalog._event), [self._update](media_manager--comparison.md#symbol-ComparisonCatalog._update), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-ComparisonCatalog._update"></a>

## `ComparisonCatalog._update`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog._update`

Обновляет поля задания сверки и время изменения. Изменяет SQLite-таблицы: comparison_jobs.

```python
def _update(self, job, **values)
```

SQLite: чтение не найдено; запись/DDL `comparison_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog.close"></a>

## `ComparisonCatalog.close`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.close`

Останавливает поток сверки при завершении Core. Использует self._stop.set, self._thread.join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog.create"></a>

## `ComparisonCatalog.create`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.create`

Создаёт сверку имён непересекающихся областей и при необходимости запускает её. Изменяет SQLite-таблицы: comparison_jobs, comparison_scans.

```python
def create(self, source: dict, targets: list[dict], reread=False, *, background=True, reuse_index=True)
```

SQLite: чтение не найдено; запись/DDL `comparison_jobs`, `comparison_scans`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `a.startswith`, `b.startswith`, `db.execute`, `dict`, `int`, `len`, `now`, `relative_path`, `scope.get`, `scopes.append`, [self._assert_idle](media_manager--comparison.md#symbol-ComparisonCatalog._assert_idle), [self._event](media_manager--comparison.md#symbol-ComparisonCatalog._event), [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), [self.resume](media_manager--comparison.md#symbol-ComparisonCatalog.resume), `self.storage.connect`, `self.storage.get_volume`, `uuid.uuid4`.

Явные `raise`:

- `ValueError('Выбери от 1 до 16 областей поиска')`
- `ValueError('Сначала зарегистрируй сменный диск, чтобы не использовать индекс другого носителя')`
- `ValueError('Источник и области поиска не должны пересекаться')`

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-ComparisonCatalog.detail"></a>

## `ComparisonCatalog.detail`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.detail`

Возвращает подробности элемента и найденные пути в целях сверки. Явно отклоняет недопустимое состояние через KeyError.

```python
def detail(self, job, path=None)
```

SQLite: чтение `comparison_entries`, `comparison_results`, `comparison_scans`, `volumes`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT e.*,r.status,r.reason FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE e.scan_id=? AND e.path=?', (scan['id'], path)).fetchone`, `dict`, `next`, `relative_path`, [self._counts](media_manager--comparison.md#symbol-ComparisonCatalog._counts), [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), `self.storage.connect`, `self.storage.metadata`.

Явные `raise`:

- `KeyError('Элемент ещё не проиндексирован')`

Выражения возврата (ветви, без исполнения):

- `dict(entry=entry, matches=matches, matches_limit=100)`


<a id="symbol-ComparisonCatalog.events"></a>

## `ComparisonCatalog.events`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.events`

Возвращает страницу журнала сверки с обратной пагинацией. Читает SQLite-таблицы: comparison_events.

```python
def events(self, job, before=None, limit=100)
```

SQLite: чтение `comparison_events`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT * FROM comparison_events WHERE job_id=?' + (' AND id<?' if before else '') + ' ORDER BY id DESC LIMIT ?', (job, before, limit) if before else (job, limit)).fetchall`, `dict`, [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `[dict(r) for r in rows]`


<a id="symbol-ComparisonCatalog.job"></a>

## `ComparisonCatalog.job`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.job`

Собирает состояние задания, области поиска и счётчики результатов. Явно отклоняет недопустимое состояние через KeyError.

```python
def job(self, job)
```

SQLite: чтение `comparison_entries`, `comparison_events`, `comparison_jobs`, `comparison_results`, `comparison_scans`, `volumes`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute("SELECT COUNT(*) FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND e.kind='directory'", (job,)).fetchone`, `db.execute("SELECT COUNT(*) FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND e.kind='file'", (job,)).fetchone`, `db.execute("SELECT COUNT(*) FROM comparison_events WHERE job_id=? AND level='error'", (job,)).fetchone`, `db.execute('SELECT * FROM comparison_jobs WHERE id=?', (job,)).fetchone`, `dict`, `self.storage.connect`, `self.storage.get_volume`.

Явные `raise`:

- `KeyError('Проверка не найдена')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-ComparisonCatalog.jobs"></a>

## `ComparisonCatalog.jobs`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.jobs`

Возвращает недавние задания общей сверки. Читает SQLite-таблицы: comparison_jobs.

```python
def jobs(self)
```

SQLite: чтение `comparison_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `[self.job(job) for job in ids]`


<a id="symbol-ComparisonCatalog.pause"></a>

## `ComparisonCatalog.pause`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.pause`

Запрашивает остановку сверки после текущего шага чтения. Использует self._stop.set, self._update, self.job.

```python
def pause(self, job)
```

Прямые выражения вызова: `self._stop.set`, [self._update](media_manager--comparison.md#symbol-ComparisonCatalog._update), [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job).

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-ComparisonCatalog.resume"></a>

## `ComparisonCatalog.resume`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.resume`

Продолжает сверку имён или создаёт её вместо старой сверки содержимого. Явно отклоняет недопустимое состояние через ValueError.

```python
def resume(self, job)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `ValueError`, `dict`, `next`, [self._assert_idle](media_manager--comparison.md#symbol-ComparisonCatalog._assert_idle), `self._stop.clear`, `self._thread.start`, [self._update](media_manager--comparison.md#symbol-ComparisonCatalog._update), [self.create](media_manager--comparison.md#symbol-ComparisonCatalog.create), [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), `threading.Thread`.

Явные `raise`:

- `ValueError('Сначала останови старую сверку содержимого')`
- `ValueError('Эту проверку нельзя продолжить')`

Выражения возврата (ветви, без исполнения):

- `self.create(dict(volume_id=source['volume_id'], path=source['root_path']), targets, reuse_index=True)`
- `self.job(job)`


<a id="symbol-ComparisonCatalog.run"></a>

## `ComparisonCatalog.run`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.run`

Собирает или повторно использует списки и классифицирует совпадения имён. Изменяет SQLite-таблицы: comparison_entries, comparison_results, comparison_scans.

```python
def run(self, job)
```

SQLite: чтение `comparison_entries`, `comparison_results`, `comparison_scans`; запись/DDL `comparison_entries`, `comparison_results`, `comparison_scans`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `OSError`, `ValueError`, `db.execute`, `db.execute("SELECT e.error FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND s.side='source' AND e.parent IS NULL", (job,)).fetchone`, `dict`, `now`, [self._check](media_manager--comparison.md#symbol-ComparisonCatalog._check), [self._classify_names](media_manager--comparison.md#symbol-ComparisonCatalog._classify_names), [self._event](media_manager--comparison.md#symbol-ComparisonCatalog._event), [self._inventory](media_manager--comparison.md#symbol-ComparisonCatalog._inventory), [self._reuse_inventory](media_manager--comparison.md#symbol-ComparisonCatalog._reuse_inventory), [self._update](media_manager--comparison.md#symbol-ComparisonCatalog._update), [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), `self.storage.connect`, `self.storage.refresh`, `str`, `volumes.get`.

Явные `raise`:

- `ValueError('Старый отчёт сохранён. Запусти новую сверку по именам.')`
- `OSError('Нет списка источника. Подключи том или используй сохранённый полный индекс.')`

Перехватываемые типы: `Paused`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-ComparisonCatalog.target_tree"></a>

## `ComparisonCatalog.target_tree`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.target_tree`

Читает один уровень сохранённого дерева целевой области. Явно отклоняет недопустимое состояние через KeyError, ValueError.

```python
def target_tree(self, job, scan_id, path=None, offset=0, limit=200)
```

SQLite: чтение `comparison_entries`, `comparison_scans`, `volumes`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute("SELECT s.*,v.name AS volume_name FROM comparison_scans s JOIN volumes v ON v.id=s.volume_id WHERE s.job_id=? AND s.id=? AND s.side='target'", (job, scan_id)).fetchone`, `db.execute('SELECT COUNT(*) FROM comparison_entries WHERE scan_id=? AND parent=?', (scan_id, path)).fetchone`, `db.execute('SELECT kind,error FROM comparison_entries WHERE scan_id=? AND path=?', (scan_id, path)).fetchone`, `dict`, `path.startswith`, `relative_path`, `self.storage.connect`.

Явные `raise`:

- `KeyError('Область NAS не найдена в этой сверке')`
- `ValueError('Папка вне выбранной области NAS')`
- `KeyError('Папка отсутствует в сохранённом списке')`
- `ValueError('Раскрывать можно только папки из сохранённого списка')`

Выражения возврата (ветви, без исполнения):

- `dict(entries=entries, total=total, path=path, scan_id=scan_id, volume_name=scan['volume_name'], error=folder['error'])`


<a id="symbol-ComparisonCatalog.tree"></a>

## `ComparisonCatalog.tree`

[media_manager/comparison.py](../../media_manager/comparison.py) · `ComparisonCatalog.tree`

Возвращает страницу исходного дерева отчёта с фильтром статуса. Явно отклоняет недопустимое состояние через ValueError.

```python
def tree(self, job, path=None, status='', offset=0, limit=200)
```

SQLite: чтение `comparison_entries`, `comparison_results`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute('SELECT COUNT(*) FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE ' + where, params).fetchone`, `db.execute('SELECT e.*,r.status,r.reason FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE ' + where + " ORDER BY e.kind!='directory',e.name COLLATE NOCASE LIMIT ? OFFSET ?", (*params, limit, offset)).fetchall`, `dict`, `entries.append`, `next`, `params.extend`, `path.startswith`, `relative_path`, [self._counts](media_manager--comparison.md#symbol-ComparisonCatalog._counts), [self.job](media_manager--comparison.md#symbol-ComparisonCatalog.job), `self.storage.connect`.

Явные `raise`:

- `ValueError('Неизвестный фильтр')`
- `ValueError('Папка вне источника')`

Выражения возврата (ветви, без исполнения):

- `dict(entries=entries, total=total, path=path, root_path=scan['root_path'])`


<a id="symbol-Paused"></a>

## `Paused`

[media_manager/comparison.py](../../media_manager/comparison.py) · `Paused`

Сигнализирует кооперативную остановку фоновой сверки. Базовые типы: Exception.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет.

<a id="symbol-fingerprint"></a>

## `fingerprint`

[media_manager/comparison.py](../../media_manager/comparison.py) · `fingerprint`

Собирает размер, времена и идентификаторы файлового объекта из stat. Поля результата: size, mtime_ns, ctime_ns, inode, device.

```python
def fingerprint(info)
```

Прямые выражения вызова: `dict`, [sqlite_file_identifier](media_manager--comparison.md#symbol-sqlite_file_identifier).

Выражения возврата (ветви, без исполнения):

- `dict(size=info.st_size, mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns, inode=sqlite_file_identifier(info.st_ino), device=sqlite_file_identifier(info.st_dev))`


<a id="symbol-name_key"></a>

## `name_key`

[media_manager/comparison.py](../../media_manager/comparison.py) · `name_key`

Нормализует имя в Unicode NFC и приводит регистр для сравнения. Использует unicodedata.normalize, unicodedata.normalize('NFC', name).casefold.

```python
def name_key(name)
```

Прямые выражения вызова: `unicodedata.normalize`, `unicodedata.normalize('NFC', name).casefold`.

Выражения возврата (ветви, без исполнения):

- `unicodedata.normalize('NFC', name).casefold()`


<a id="symbol-open_readonly"></a>

## `open_readonly`

[media_manager/comparison.py](../../media_manager/comparison.py) · `open_readonly`

Открывает проверенный файл или каталог относительно дескрипторов родителей. Запрещает symlink, специальные файлы и смену тома; повторно проверяет ID при выходе.

```python
def open_readonly(volume: dict, path: str, *, directory=False)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `OSError`, `PurePosixPath`, `descriptors.append`, `enumerate`, `len`, `os.close`, `os.fstat`, `os.open`, `relative_path`, `reversed`, `stat.S_ISDIR`, `stat.S_ISREG`, `verify_identity`, `volume.get`.

Явные `raise`:

- `OSError('Том был отключён или заменён')`
- `OSError('Переход на другой том запрещён')`
- `OSError('Нужна папка')`
- `OSError('Содержимое этого типа файлов не читается')`

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-parent_key"></a>

## `parent_key`

[media_manager/comparison.py](../../media_manager/comparison.py) · `parent_key`

Нормализует имя непосредственного родительского каталога. Использует PurePosixPath, name_key.

```python
def parent_key(parent)
```

Прямые выражения вызова: `PurePosixPath`, [name_key](media_manager--comparison.md#symbol-name_key).

Выражения возврата (ветви, без исполнения):

- `name_key(PurePosixPath(parent).name) if parent else ''`


<a id="symbol-sqlite_file_identifier"></a>

## `sqlite_file_identifier`

[media_manager/comparison.py](../../media_manager/comparison.py) · `sqlite_file_identifier`

Сохраняет большие inode и device без округления SQLite. Значения вне signed int64 кодируются текстом fsid:, обычные целые сохраняют тип.

```python
def sqlite_file_identifier(value: int) -> int | str
```

Выражения возврата (ветви, без исполнения):

- `value if -(1 << 63) <= value < 1 << 63 else f'fsid:{value}'`
