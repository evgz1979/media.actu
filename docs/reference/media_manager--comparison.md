# Поиск совпадений по именам: `media_manager/comparison.py`

Действующая сверка одной области с несколькими целями по именам; также хранит и показывает старые отчёты сверки содержимого. Здесь находятся общие функции безопасного чтения.

[Исходный модуль](../../media_manager/comparison.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_originals.py](media_manager--photos_originals.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_comparison.py](../../tests/test_comparison.py#L12), [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L10), [tests/test_volume_identity.py](../../tests/test_volume_identity.py#L14).

## Оглавление определений

- [name_key](#symbol-name-key) — Нормализует имя в Unicode NFC и приводит регистр для сравнения.
- [parent_key](#symbol-parent-key) — Нормализует имя непосредственного родительского каталога.
- [Paused](#symbol-paused) — Сигнализирует кооперативную остановку фоновой сверки.
- [open_readonly](#symbol-open-readonly) — Открывает проверенный файл или каталог относительно дескрипторов родителей.
- [sqlite_file_identifier](#symbol-sqlite-file-identifier) — Сохраняет большие inode и device без округления SQLite.
- [fingerprint](#symbol-fingerprint) — Собирает размер, времена и идентификаторы файлового объекта из stat.
- [ComparisonCatalog](#symbol-comparisoncatalog) — Ведёт задания, индексы, результаты и историю поиска по именам.
- [ComparisonCatalog.__init__](#symbol-comparisoncatalog---init--) — Инициализирует ComparisonCatalog и его рабочее состояние.
- [ComparisonCatalog._event](#symbol-comparisoncatalog--event) — Добавляет событие в журнал сверки в переданной транзакции.
- [ComparisonCatalog._update](#symbol-comparisoncatalog--update) — Обновляет поля задания сверки и время изменения.
- [ComparisonCatalog._check](#symbol-comparisoncatalog--check) — Прерывает текущую обработку, если запрошена остановка сверки.
- [ComparisonCatalog.create](#symbol-comparisoncatalog-create) — Создаёт сверку имён непересекающихся областей и при необходимости запускает её.
- [ComparisonCatalog._assert_idle](#symbol-comparisoncatalog--assert-idle) — Запрещает новый запуск, пока предыдущий поток сверки работает.
- [ComparisonCatalog.resume](#symbol-comparisoncatalog-resume) — Продолжает сверку имён или создаёт её вместо старой сверки содержимого.
- [ComparisonCatalog.pause](#symbol-comparisoncatalog-pause) — Запрашивает остановку сверки после текущего шага чтения.
- [ComparisonCatalog.close](#symbol-comparisoncatalog-close) — Останавливает поток сверки при завершении Core.
- [ComparisonCatalog.run](#symbol-comparisoncatalog-run) — Собирает или повторно использует списки и классифицирует совпадения имён.
- [ComparisonCatalog._reuse_inventory](#symbol-comparisoncatalog--reuse-inventory) — Переносит подходящий завершённый индекс из прежнего задания.
- [ComparisonCatalog._inventory](#symbol-comparisoncatalog--inventory) — Обходит выбранную область и сохраняет метаданные и ошибки элементов.
- [ComparisonCatalog._classify_names](#symbol-comparisoncatalog--classify-names) — Сопоставляет нормализованные имена, типы и непосредственные родительские папки.
- [ComparisonCatalog.jobs](#symbol-comparisoncatalog-jobs) — Возвращает недавние задания общей сверки.
- [ComparisonCatalog.job](#symbol-comparisoncatalog-job) — Собирает состояние задания, области поиска и счётчики результатов.
- [ComparisonCatalog.tree](#symbol-comparisoncatalog-tree) — Возвращает страницу исходного дерева отчёта с фильтром статуса.
- [ComparisonCatalog._counts](#symbol-comparisoncatalog--counts) — Считает непосредственные дочерние элементы выбранной области индекса.
- [ComparisonCatalog.detail](#symbol-comparisoncatalog-detail) — Возвращает подробности элемента и найденные пути в целях сверки.
- [ComparisonCatalog.target_tree](#symbol-comparisoncatalog-target-tree) — Читает один уровень сохранённого дерева целевой области.
- [ComparisonCatalog.events](#symbol-comparisoncatalog-events) — Возвращает страницу журнала сверки с обратной пагинацией.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [LABELS](../../media_manager/comparison.py#L18) | `{'names_found': 'Совпали имена', 'other_folder': 'Имя в другой папке', 'names_missing': 'Не найдено по именам', 'found': 'Есть на NAS', 'cached': 'Есть по сохранённым хэшам', 'missing': 'Не найдено', 'candidate': 'Кандидат на совпадение', 'unverified': 'Не проверено', 'skipped': 'Не сравнивается'}` |
| [NAME_STATUSES](../../media_manager/comparison.py#L25) | `('names_found', 'other_folder', 'names_missing', 'unverified', 'skipped')` |

<a id="symbol-name-key"></a>

## `name_key`

[media_manager/comparison.py:30](../../media_manager/comparison.py#L30)

Нормализует имя в Unicode NFC и приводит регистр для сравнения. Использует unicodedata.normalize, unicodedata.normalize('NFC', name).casefold.

```python
def name_key(name)
```

Прямые выражения вызова: `unicodedata.normalize`, `unicodedata.normalize('NFC', name).casefold`.

Выражения возврата (ветви, без исполнения):

- `unicodedata.normalize('NFC', name).casefold()`


<a id="symbol-parent-key"></a>

## `parent_key`

[media_manager/comparison.py:36](../../media_manager/comparison.py#L36)

Нормализует имя непосредственного родительского каталога. Использует PurePosixPath, name_key.

```python
def parent_key(parent)
```

Прямые выражения вызова: `PurePosixPath`, [name_key](../../media_manager/comparison.py#L30).

Выражения возврата (ветви, без исполнения):

- `name_key(PurePosixPath(parent).name) if parent else ''`


<a id="symbol-paused"></a>

## `Paused`

[media_manager/comparison.py:42](../../media_manager/comparison.py#L42)

Сигнализирует кооперативную остановку фоновой сверки. Базовые типы: Exception.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-open-readonly"></a>

## `open_readonly`

[media_manager/comparison.py:49](../../media_manager/comparison.py#L49)

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

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-sqlite-file-identifier"></a>

## `sqlite_file_identifier`

[media_manager/comparison.py:85](../../media_manager/comparison.py#L85)

Сохраняет большие inode и device без округления SQLite. Значения вне signed int64 кодируются текстом fsid:, обычные целые сохраняют тип.

```python
def sqlite_file_identifier(value: int) -> int | str
```

Выражения возврата (ветви, без исполнения):

- `value if -(1 << 63) <= value < 1 << 63 else f'fsid:{value}'`


<a id="symbol-fingerprint"></a>

## `fingerprint`

[media_manager/comparison.py:97](../../media_manager/comparison.py#L97)

Собирает размер, времена и идентификаторы файлового объекта из stat. Поля результата: size, mtime_ns, ctime_ns, inode, device.

```python
def fingerprint(info)
```

Прямые выражения вызова: `dict`, [sqlite_file_identifier](../../media_manager/comparison.py#L85).

Выражения возврата (ветви, без исполнения):

- `dict(size=info.st_size, mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns, inode=sqlite_file_identifier(info.st_ino), device=sqlite_file_identifier(info.st_dev))`


<a id="symbol-comparisoncatalog"></a>

## `ComparisonCatalog`

[media_manager/comparison.py:104](../../media_manager/comparison.py#L104)

Ведёт задания, индексы, результаты и историю поиска по именам. Зависимости конструктора: storage.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `_stop`, `_thread`, `storage`.

Именованные методы: `__init__`, `_event`, `_update`, `_check`, `create`, `_assert_idle`, `resume`, `pause`, `close`, `run`, `_reuse_inventory`, `_inventory`, `_classify_names`, `jobs`, `job`, `tree`, `_counts`, `detail`, `target_tree`, `events`.

<a id="symbol-comparisoncatalog---init--"></a>

## `ComparisonCatalog.__init__`

[media_manager/comparison.py:107](../../media_manager/comparison.py#L107)

Инициализирует ComparisonCatalog и его рабочее состояние. Изменяет SQLite-таблицы: comparison_entries, comparison_events, comparison_hashes, comparison_jobs, comparison_results, comparison_scans.

```python
def __init__(self, storage: StorageCatalog)
```

SQLite: чтение `comparison_jobs`; запись/DDL `comparison_entries`, `comparison_events`, `comparison_hashes`, `comparison_jobs`, `comparison_results`, `comparison_scans`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_lock`, `_stop`, `_thread`, `storage`.

Прямые выражения вызова: `additions.items`, `columns.items`, `db.execute`, `db.execute("SELECT id FROM comparison_jobs WHERE state IN ('running','pausing')").fetchall`, `db.executescript`, `now`, [self._event](../../media_manager/comparison.py#L170), `self.storage.connect`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog--event"></a>

## `ComparisonCatalog._event`

[media_manager/comparison.py:170](../../media_manager/comparison.py#L170)

Добавляет событие в журнал сверки в переданной транзакции. Изменяет SQLite-таблицы: comparison_events.

```python
def _event(db, job, level, message, path='')
```

Декораторы: `staticmethod`.

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `comparison_events`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `now`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog--update"></a>

## `ComparisonCatalog._update`

[media_manager/comparison.py:176](../../media_manager/comparison.py#L176)

Обновляет поля задания сверки и время изменения. Изменяет SQLite-таблицы: comparison_jobs.

```python
def _update(self, job, **values)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `comparison_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog--check"></a>

## `ComparisonCatalog._check`

[media_manager/comparison.py:183](../../media_manager/comparison.py#L183)

Прерывает текущую обработку, если запрошена остановка сверки. Явно отклоняет недопустимое состояние через Paused.

```python
def _check(self)
```

Прямые выражения вызова: [Paused](../../media_manager/comparison.py#L42), `self._stop.is_set`.

Явные `raise`:

- `Paused()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog-create"></a>

## `ComparisonCatalog.create`

[media_manager/comparison.py:189](../../media_manager/comparison.py#L189)

Создаёт сверку имён непересекающихся областей и при необходимости запускает её. Изменяет SQLite-таблицы: comparison_jobs, comparison_scans.

```python
def create(self, source: dict, targets: list[dict], reread=False, *, background=True, reuse_index=True)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `comparison_jobs`, `comparison_scans`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `a.startswith`, `b.startswith`, `db.execute`, `dict`, `int`, `len`, `now`, `relative_path`, `scope.get`, `scopes.append`, [self._assert_idle](../../media_manager/comparison.py#L220), [self._event](../../media_manager/comparison.py#L170), [self.job](../../media_manager/comparison.py#L450), [self.resume](../../media_manager/comparison.py#L226), `self.storage.connect`, `self.storage.get_volume`, `uuid.uuid4`.

Явные `raise`:

- `ValueError('Выбери от 1 до 16 областей поиска')`
- `ValueError('Сначала зарегистрируй сменный диск, чтобы не использовать индекс другого носителя')`
- `ValueError('Источник и области поиска не должны пересекаться')`

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-comparisoncatalog--assert-idle"></a>

## `ComparisonCatalog._assert_idle`

[media_manager/comparison.py:220](../../media_manager/comparison.py#L220)

Запрещает новый запуск, пока предыдущий поток сверки работает. Явно отклоняет недопустимое состояние через ValueError.

```python
def _assert_idle(self)
```

Прямые выражения вызова: `ValueError`, `self._thread.is_alive`.

Явные `raise`:

- `ValueError('Уже выполняется сверка. Сначала останови её.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog-resume"></a>

## `ComparisonCatalog.resume`

[media_manager/comparison.py:226](../../media_manager/comparison.py#L226)

Продолжает сверку имён или создаёт её вместо старой сверки содержимого. Явно отклоняет недопустимое состояние через ValueError.

```python
def resume(self, job)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `ValueError`, `dict`, `next`, [self._assert_idle](../../media_manager/comparison.py#L220), `self._stop.clear`, `self._thread.start`, [self._update](../../media_manager/comparison.py#L176), [self.create](../../media_manager/comparison.py#L189), [self.job](../../media_manager/comparison.py#L450), `threading.Thread`.

Явные `raise`:

- `ValueError('Сначала останови старую сверку содержимого')`
- `ValueError('Эту проверку нельзя продолжить')`

Выражения возврата (ветви, без исполнения):

- `self.create(dict(volume_id=source['volume_id'], path=source['root_path']), targets, reuse_index=True)`
- `self.job(job)`


<a id="symbol-comparisoncatalog-pause"></a>

## `ComparisonCatalog.pause`

[media_manager/comparison.py:246](../../media_manager/comparison.py#L246)

Запрашивает остановку сверки после текущего шага чтения. Использует self._stop.set, self._update, self.job.

```python
def pause(self, job)
```

Прямые выражения вызова: `self._stop.set`, [self._update](../../media_manager/comparison.py#L176), [self.job](../../media_manager/comparison.py#L450).

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-comparisoncatalog-close"></a>

## `ComparisonCatalog.close`

[media_manager/comparison.py:256](../../media_manager/comparison.py#L256)

Останавливает поток сверки при завершении Core. Использует self._stop.set, self._thread.join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog-run"></a>

## `ComparisonCatalog.run`

[media_manager/comparison.py:263](../../media_manager/comparison.py#L263)

Собирает или повторно использует списки и классифицирует совпадения имён. Изменяет SQLite-таблицы: comparison_entries, comparison_results, comparison_scans.

```python
def run(self, job)
```

SQLite: чтение `comparison_entries`, `comparison_results`, `comparison_scans`; запись/DDL `comparison_entries`, `comparison_results`, `comparison_scans`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `OSError`, `ValueError`, `db.execute`, `db.execute("SELECT e.error FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND s.side='source' AND e.parent IS NULL", (job,)).fetchone`, `dict`, `now`, [self._check](../../media_manager/comparison.py#L183), [self._classify_names](../../media_manager/comparison.py#L406), [self._event](../../media_manager/comparison.py#L170), [self._inventory](../../media_manager/comparison.py#L337), [self._reuse_inventory](../../media_manager/comparison.py#L313), [self._update](../../media_manager/comparison.py#L176), [self.job](../../media_manager/comparison.py#L450), `self.storage.connect`, `self.storage.refresh`, `str`, `volumes.get`.

Явные `raise`:

- `ValueError('Старый отчёт сохранён. Запусти новую сверку по именам.')`
- `OSError('Нет списка источника. Подключи том или используй сохранённый полный индекс.')`

Перехватываемые типы: `Paused`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog--reuse-inventory"></a>

## `ComparisonCatalog._reuse_inventory`

[media_manager/comparison.py:313](../../media_manager/comparison.py#L313)

Переносит подходящий завершённый индекс из прежнего задания. Изменяет SQLite-таблицы: comparison_entries, comparison_scans.

```python
def _reuse_inventory(self, job, scan)
```

SQLite: чтение `comparison_entries`, `comparison_scans`; запись/DDL `comparison_entries`, `comparison_scans`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.create_function`, `db.execute`, `db.execute("SELECT * FROM comparison_scans WHERE volume_id=? AND root_path=?\n                AND state='complete' AND id!=? ORDER BY finished_at DESC,id DESC LIMIT 1", (scan['volume_id'], scan['root_path'], scan['id'])).fetchone`, [self._event](../../media_manager/comparison.py#L170), [self._update](../../media_manager/comparison.py#L176), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `False`
- `True`


<a id="symbol-comparisoncatalog--inventory"></a>

## `ComparisonCatalog._inventory`

[media_manager/comparison.py:337](../../media_manager/comparison.py#L337)

Обходит выбранную область и сохраняет метаданные и ошибки элементов. Изменяет SQLite-таблицы: comparison_entries, comparison_scans, directories.

```python
def _inventory(self, job, scan, volume)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `comparison_entries`, `comparison_scans`, `directories`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `(path + '/' + item.name).lstrip`, `(volume or {}).get`, `PurePosixPath`, `children.append`, `datetime.fromtimestamp`, `datetime.fromtimestamp(e['mtime_ns'] / 1000000000.0, timezone.utc).isoformat`, `db.execute`, `db.executemany`, `dict`, `entries.append`, `item.is_dir`, `item.is_file`, `item.is_symlink`, `json.dumps`, [name_key](../../media_manager/comparison.py#L30), `now`, [open_readonly](../../media_manager/comparison.py#L49), `os.scandir`, [parent_key](../../media_manager/comparison.py#L36), `pending.clear`, `pending.extend`, `pending.pop`, [self._check](../../media_manager/comparison.py#L183), [self._event](../../media_manager/comparison.py#L170), [self._update](../../media_manager/comparison.py#L176), `self.storage.connect`, `service_file`, `str`.

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog--classify-names"></a>

## `ComparisonCatalog._classify_names`

[media_manager/comparison.py:406](../../media_manager/comparison.py#L406)

Сопоставляет нормализованные имена, типы и непосредственные родительские папки. Изменяет SQLite-таблицы: comparison_results.

```python
def _classify_names(self, job)
```

SQLite: чтение `comparison_entries`, `comparison_scans`; запись/DDL `comparison_results`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `all`, `db.execute`, `db.executemany`, `dict`, `len`, `names.add`, `next`, `pairs.add`, `results.append`, `results.clear`, [self._check](../../media_manager/comparison.py#L183), `self.storage.connect`, `set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-comparisoncatalog-jobs"></a>

## `ComparisonCatalog.jobs`

[media_manager/comparison.py:443](../../media_manager/comparison.py#L443)

Возвращает недавние задания общей сверки. Читает SQLite-таблицы: comparison_jobs.

```python
def jobs(self)
```

SQLite: чтение `comparison_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self.job](../../media_manager/comparison.py#L450), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `[self.job(job) for job in ids]`


<a id="symbol-comparisoncatalog-job"></a>

## `ComparisonCatalog.job`

[media_manager/comparison.py:450](../../media_manager/comparison.py#L450)

Собирает состояние задания, области поиска и счётчики результатов. Явно отклоняет недопустимое состояние через KeyError.

```python
def job(self, job)
```

SQLite: чтение `comparison_entries`, `comparison_events`, `comparison_jobs`, `comparison_results`, `comparison_scans`, `volumes`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute("SELECT COUNT(*) FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND e.kind='directory'", (job,)).fetchone`, `db.execute("SELECT COUNT(*) FROM comparison_entries e JOIN comparison_scans s ON s.id=e.scan_id WHERE s.job_id=? AND e.kind='file'", (job,)).fetchone`, `db.execute("SELECT COUNT(*) FROM comparison_events WHERE job_id=? AND level='error'", (job,)).fetchone`, `db.execute('SELECT * FROM comparison_jobs WHERE id=?', (job,)).fetchone`, `dict`, `self.storage.connect`, `self.storage.get_volume`.

Явные `raise`:

- `KeyError('Проверка не найдена')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-comparisoncatalog-tree"></a>

## `ComparisonCatalog.tree`

[media_manager/comparison.py:469](../../media_manager/comparison.py#L469)

Возвращает страницу исходного дерева отчёта с фильтром статуса. Явно отклоняет недопустимое состояние через ValueError.

```python
def tree(self, job, path=None, status='', offset=0, limit=200)
```

SQLite: чтение `comparison_entries`, `comparison_results`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute('SELECT COUNT(*) FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE ' + where, params).fetchone`, `db.execute('SELECT e.*,r.status,r.reason FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE ' + where + " ORDER BY e.kind!='directory',e.name COLLATE NOCASE LIMIT ? OFFSET ?", (*params, limit, offset)).fetchall`, `dict`, `entries.append`, `next`, `params.extend`, `path.startswith`, `relative_path`, [self._counts](../../media_manager/comparison.py#L498), [self.job](../../media_manager/comparison.py#L450), `self.storage.connect`.

Явные `raise`:

- `ValueError('Неизвестный фильтр')`
- `ValueError('Папка вне источника')`

Выражения возврата (ветви, без исполнения):

- `dict(entries=entries, total=total, path=path, root_path=scan['root_path'])`


<a id="symbol-comparisoncatalog--counts"></a>

## `ComparisonCatalog._counts`

[media_manager/comparison.py:498](../../media_manager/comparison.py#L498)

Считает непосредственные дочерние элементы выбранной области индекса. Читает SQLite-таблицы: comparison_entries, comparison_results.

```python
def _counts(db, scan, path)
```

Декораторы: `staticmethod`.

SQLite: чтение `comparison_entries`, `comparison_results`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`.

Выражения возврата (ветви, без исполнения):

- `{r['status']: r['n'] for r in db.execute('SELECT r.status,COUNT(*) n FROM comparison_entries e JOIN comparison_results r ON r.entry_id=e.id\n            WHERE e.scan_id=?' + condition + ' GROUP BY r.status', params)}`


<a id="symbol-comparisoncatalog-detail"></a>

## `ComparisonCatalog.detail`

[media_manager/comparison.py:506](../../media_manager/comparison.py#L506)

Возвращает подробности элемента и найденные пути в целях сверки. Явно отклоняет недопустимое состояние через KeyError.

```python
def detail(self, job, path=None)
```

SQLite: чтение `comparison_entries`, `comparison_results`, `comparison_scans`, `volumes`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT e.*,r.status,r.reason FROM comparison_entries e LEFT JOIN comparison_results r ON r.entry_id=e.id WHERE e.scan_id=? AND e.path=?', (scan['id'], path)).fetchone`, `dict`, `next`, `relative_path`, [self._counts](../../media_manager/comparison.py#L498), [self.job](../../media_manager/comparison.py#L450), `self.storage.connect`, `self.storage.metadata`.

Явные `raise`:

- `KeyError('Элемент ещё не проиндексирован')`

Выражения возврата (ветви, без исполнения):

- `dict(entry=entry, matches=matches, matches_limit=100)`


<a id="symbol-comparisoncatalog-target-tree"></a>

## `ComparisonCatalog.target_tree`

[media_manager/comparison.py:536](../../media_manager/comparison.py#L536)

Читает один уровень сохранённого дерева целевой области. Явно отклоняет недопустимое состояние через KeyError, ValueError.

```python
def target_tree(self, job, scan_id, path=None, offset=0, limit=200)
```

SQLite: чтение `comparison_entries`, `comparison_scans`, `volumes`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `ValueError`, `db.execute`, `db.execute("SELECT s.*,v.name AS volume_name FROM comparison_scans s JOIN volumes v ON v.id=s.volume_id WHERE s.job_id=? AND s.id=? AND s.side='target'", (job, scan_id)).fetchone`, `db.execute('SELECT COUNT(*) FROM comparison_entries WHERE scan_id=? AND parent=?', (scan_id, path)).fetchone`, `db.execute('SELECT kind,error FROM comparison_entries WHERE scan_id=? AND path=?', (scan_id, path)).fetchone`, `dict`, `path.startswith`, `relative_path`, `self.storage.connect`.

Явные `raise`:

- `KeyError('Область NAS не найдена в этой сверке')`
- `ValueError('Папка вне выбранной области NAS')`
- `KeyError('Папка отсутствует в сохранённом списке')`
- `ValueError('Раскрывать можно только папки из сохранённого списка')`

Выражения возврата (ветви, без исполнения):

- `dict(entries=entries, total=total, path=path, scan_id=scan_id, volume_name=scan['volume_name'], error=folder['error'])`


<a id="symbol-comparisoncatalog-events"></a>

## `ComparisonCatalog.events`

[media_manager/comparison.py:556](../../media_manager/comparison.py#L556)

Возвращает страницу журнала сверки с обратной пагинацией. Читает SQLite-таблицы: comparison_events.

```python
def events(self, job, before=None, limit=100)
```

SQLite: чтение `comparison_events`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT * FROM comparison_events WHERE job_id=?' + (' AND id<?' if before else '') + ' ORDER BY id DESC LIMIT ?', (job, before, limit) if before else (job, limit)).fetchall`, `dict`, [self.job](../../media_manager/comparison.py#L450), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `[dict(r) for r in rows]`
