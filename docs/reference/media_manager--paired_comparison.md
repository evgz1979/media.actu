# Сверка связанных папок: `media_manager/paired_comparison.py`

Симметричная сверка выбранного источника и копии: структура, имя и размер, дополнительный SHA-256; хранит выровненные строки и решения пользователя.

[Исходный модуль](../../media_manager/paired_comparison.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [media_manager/copy_files.py](media_manager--copy_files.md), [paired_workspace_ui.py](paired_workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_connections.py](../../tests/test_copy_connections.py#L12), [tests/test_copy_files.py](../../tests/test_copy_files.py#L13), [tests/test_copy_number_release.py](../../tests/test_copy_number_release.py#L14), [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L15), [tests/test_paired_comparison.py](../../tests/test_paired_comparison.py#L10), [tests/test_paired_comparison.py](../../tests/test_paired_comparison.py#L171).

## Оглавление определений

- [absolute_scope_path](#symbol-absolute-scope-path) — Объединяет корень зарегистрированной области и относительный путь строки.
- [PairedComparisonCatalog](#symbol-pairedcomparisoncatalog) — Ведёт двухсторонние сверки, выровненные строки и решения по лишним элементам.
- [PairedComparisonCatalog.__init__](#symbol-pairedcomparisoncatalog---init--) — Инициализирует PairedComparisonCatalog и его рабочее состояние.
- [PairedComparisonCatalog.busy](#symbol-pairedcomparisoncatalog-busy) — Проверяет работу парной сверки или связанной операции копирования.
- [PairedComparisonCatalog._idle](#symbol-pairedcomparisoncatalog--idle) — Проверяет отсутствие конфликтующей парной или общей сверки.
- [PairedComparisonCatalog._update](#symbol-pairedcomparisoncatalog--update) — Сохраняет поля парной сверки и время последнего изменения.
- [PairedComparisonCatalog._check](#symbol-pairedcomparisoncatalog--check) — Прерывает обход, если пользователь запросил паузу сверки.
- [PairedComparisonCatalog._pair](#symbol-pairedcomparisoncatalog--pair) — Разрешает актуальный источник и назначение действующей связи копии.
- [PairedComparisonCatalog.create](#symbol-pairedcomparisoncatalog-create) — Создаёт сверку структуры или файлов для зарегистрированной пары.
- [PairedComparisonCatalog.resume](#symbol-pairedcomparisoncatalog-resume) — Продолжает приостановленную сверку после проверки неизменности связи.
- [PairedComparisonCatalog.pause](#symbol-pairedcomparisoncatalog-pause) — Запрашивает кооперативную остановку выбранной парной сверки.
- [PairedComparisonCatalog.close](#symbol-pairedcomparisoncatalog-close) — Останавливает поток парной сверки при завершении Core.
- [PairedComparisonCatalog.job](#symbol-pairedcomparisoncatalog-job) — Собирает отчёт, счётчики, ошибки корней и сведения о копировании.
- [PairedComparisonCatalog.jobs](#symbol-pairedcomparisoncatalog-jobs) — Возвращает последние отчёты всех пар или выбранной копии.
- [PairedComparisonCatalog._save_entry](#symbol-pairedcomparisoncatalog--save-entry) — Сохраняет метаданные одного элемента стороны сверки в JSON.
- [PairedComparisonCatalog._entries](#symbol-pairedcomparisoncatalog--entries) — Восстанавливает индекс элементов выбранной стороны из SQLite.
- [PairedComparisonCatalog._inventory](#symbol-pairedcomparisoncatalog--inventory) — Обходит одну сторону пары и сохраняет перечень элементов и ошибки.
- [PairedComparisonCatalog._hash](#symbol-pairedcomparisoncatalog--hash) — Читает SHA-256 одного файла с проверкой его параметров до и после чтения.
- [PairedComparisonCatalog._hash_pairs](#symbol-pairedcomparisoncatalog--hash-pairs) — Проверяет содержимое пар файлов одинакового размера и повторно проверяет версии.
- [PairedComparisonCatalog._status](#symbol-pairedcomparisoncatalog--status) — Классифицирует строку по наличию сторон, типу, ошибкам и выбранному методу.
- [PairedComparisonCatalog._classify](#symbol-pairedcomparisoncatalog--classify) — Выравнивает стороны по пути и сохраняет статусы и счётчики различий.
- [PairedComparisonCatalog.run](#symbol-pairedcomparisoncatalog-run) — Выполняет индексацию, дополнительное хеширование и сборку результата пары.
- [PairedComparisonCatalog.rows](#symbol-pairedcomparisoncatalog-rows) — Возвращает страницу строк отчёта с фильтрацией и наследуемыми решениями.
- [PairedComparisonCatalog.decide](#symbol-pairedcomparisoncatalog-decide) — Сохраняет или снимает решение для элемента только в копии.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [STATUS_LABELS](../../media_manager/paired_comparison.py#L17) | `{'both': 'Есть в обеих', 'missing_copy': 'Нет в копии', 'extra_copy': 'Только в копии', 'same': 'Совпадает', 'different': 'Отличается', 'conflict': 'Разный тип', 'same_size': 'Имя и размер совпали', 'size_different': 'Размер отличается', 'copy_incomplete': 'Копия не завершена', 'unverified': 'Не проверено', 'skipped': 'Не сравнивается'}` |
| [DECISIONS](../../media_manager/paired_comparison.py#L24) | `{'keep': 'Оставить в копии', 'add_main': 'Добавить в 00-main', 'move': 'Подготовить перенос', 'remove': 'Подготовить удаление'}` |

<a id="symbol-absolute-scope-path"></a>

## `absolute_scope_path`

[media_manager/paired_comparison.py:30](../../media_manager/paired_comparison.py#L30)

Объединяет корень зарегистрированной области и относительный путь строки. Использует '/'.join, relative_path.

```python
def absolute_scope_path(scope, path)
```

Прямые выражения вызова: `'/'.join`, `relative_path`.

Выражения возврата (ветви, без исполнения):

- `'/'.join((part for part in (scope['path'], relative_path(path)) if part))`


<a id="symbol-pairedcomparisoncatalog"></a>

## `PairedComparisonCatalog`

[media_manager/paired_comparison.py:36](../../media_manager/paired_comparison.py#L36)

Ведёт двухсторонние сверки, выровненные строки и решения по лишним элементам. Зависимости конструктора: storage, copies, legacy.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_flush_at`, `_lock`, `_stop`, `_thread`, `copies`, `legacy`, `storage`, `transfers`.

Именованные методы: `__init__`, `busy`, `_idle`, `_update`, `_check`, `_pair`, `create`, `resume`, `pause`, `close`, `job`, `jobs`, `_save_entry`, `_entries`, `_inventory`, `_hash`, `_hash_pairs`, `_status`, `_classify`, `run`, `rows`, `decide`.

<a id="symbol-pairedcomparisoncatalog---init--"></a>

## `PairedComparisonCatalog.__init__`

[media_manager/paired_comparison.py:39](../../media_manager/paired_comparison.py#L39)

Инициализирует PairedComparisonCatalog и его рабочее состояние. Изменяет SQLite-таблицы: paired_decisions, paired_entries, paired_jobs, paired_rows.

```python
def __init__(self, storage, copies, legacy=None)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `paired_decisions`, `paired_entries`, `paired_jobs`, `paired_rows`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_flush_at`, `_lock`, `_stop`, `_thread`, `copies`, `legacy`, `storage`, `transfers`.

Прямые выражения вызова: `db.execute`, `db.executescript`, `now`, `storage.connect`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog-busy"></a>

## `PairedComparisonCatalog.busy`

[media_manager/paired_comparison.py:84](../../media_manager/paired_comparison.py#L84)

Проверяет работу парной сверки или связанной операции копирования. Использует self._thread.is_alive, self.transfers.busy.

```python
def busy(self)
```

Прямые выражения вызова: `bool`, `self._thread.is_alive`, `self.transfers.busy`.

Выражения возврата (ветви, без исполнения):

- `self._thread is not None and self._thread.is_alive() or bool(self.transfers and self.transfers.busy())`


<a id="symbol-pairedcomparisoncatalog--idle"></a>

## `PairedComparisonCatalog._idle`

[media_manager/paired_comparison.py:89](../../media_manager/paired_comparison.py#L89)

Проверяет отсутствие конфликтующей парной или общей сверки. Явно отклоняет недопустимое состояние через ValueError.

```python
def _idle(self)
```

Прямые выражения вызова: `ValueError`, [self.busy](../../media_manager/paired_comparison.py#L84), `self.legacy._assert_idle`.

Явные `raise`:

- `ValueError('Другая сверка ещё выполняется. Сначала останови её.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--update"></a>

## `PairedComparisonCatalog._update`

[media_manager/paired_comparison.py:97](../../media_manager/paired_comparison.py#L97)

Сохраняет поля парной сверки и время последнего изменения. Изменяет SQLite-таблицы: paired_jobs.

```python
def _update(self, job, **values)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `paired_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--check"></a>

## `PairedComparisonCatalog._check`

[media_manager/paired_comparison.py:105](../../media_manager/paired_comparison.py#L105)

Прерывает обход, если пользователь запросил паузу сверки. Явно отклоняет недопустимое состояние через Paused.

```python
def _check(self)
```

Прямые выражения вызова: `Paused`, `self._stop.is_set`.

Явные `raise`:

- `Paused()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--pair"></a>

## `PairedComparisonCatalog._pair`

[media_manager/paired_comparison.py:111](../../media_manager/paired_comparison.py#L111)

Разрешает актуальный источник и назначение действующей связи копии. Явно отклоняет недопустимое состояние через KeyError, ValueError.

```python
def _pair(self, copy_id)
```

Прямые выражения вызова: `KeyError`, `ValueError`, `any`, `copy.get`, `group.get`, `next`, `self.copies.groups`, `source.get`.

Явные `raise`:

- `ValueError('Номер прежней привязки освобождён. Для неё доступна только история.')`
- `ValueError('Связь отключена. Сначала подключи её в разделе «Отключённые».')`
- `ValueError('Источник копирования недоступен или отключён. Проверь связь.')`
- `KeyError('Связь с копией не найдена')`

Выражения возврата (ветви, без исполнения):

- `{'left': source, 'right': copy}`


<a id="symbol-pairedcomparisoncatalog-create"></a>

## `PairedComparisonCatalog.create`

[media_manager/paired_comparison.py:128](../../media_manager/paired_comparison.py#L128)

Создаёт сверку структуры или файлов для зарегистрированной пары. Изменяет SQLite-таблицы: paired_jobs.

```python
def create(self, copy_id, mode='folders', base_job_id=None, *, method='size', background=True)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `paired_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `any`, `db.execute`, `json.dumps`, `now`, `scopes.values`, [self._idle](../../media_manager/paired_comparison.py#L89), [self._pair](../../media_manager/paired_comparison.py#L111), [self.job](../../media_manager/paired_comparison.py#L193), [self.resume](../../media_manager/paired_comparison.py#L159), `self.storage.connect`, `self.storage.get_volume`, `uuid4`.

Явные `raise`:

- `ValueError('Неизвестный вид сверки')`
- `ValueError('Неизвестный метод сверки файлов')`
- `ValueError('Сначала заверши сверку папок этой пары.')`
- `ValueError('Связь изменилась. Сначала заново сверь папки.')`
- `ValueError('Сначала подтверди подключённый диск.')`

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-pairedcomparisoncatalog-resume"></a>

## `PairedComparisonCatalog.resume`

[media_manager/paired_comparison.py:159](../../media_manager/paired_comparison.py#L159)

Продолжает приостановленную сверку после проверки неизменности связи. Явно отклоняет недопустимое состояние через ValueError.

```python
def resume(self, job)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `ValueError`, `any`, [self._idle](../../media_manager/paired_comparison.py#L89), [self._pair](../../media_manager/paired_comparison.py#L111), `self._stop.clear`, `self._thread.start`, [self._update](../../media_manager/paired_comparison.py#L97), [self.job](../../media_manager/paired_comparison.py#L193), `threading.Thread`.

Явные `raise`:

- `ValueError('Эту сверку нельзя продолжить.')`
- `ValueError('Источник или связь изменились. Начни новую сверку.')`

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-pairedcomparisoncatalog-pause"></a>

## `PairedComparisonCatalog.pause`

[media_manager/paired_comparison.py:177](../../media_manager/paired_comparison.py#L177)

Запрашивает кооперативную остановку выбранной парной сверки. Использует self._stop.set, self._update, self.job.

```python
def pause(self, job)
```

Прямые выражения вызова: `self._stop.set`, [self._update](../../media_manager/paired_comparison.py#L97), [self.job](../../media_manager/paired_comparison.py#L193).

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-pairedcomparisoncatalog-close"></a>

## `PairedComparisonCatalog.close`

[media_manager/paired_comparison.py:186](../../media_manager/paired_comparison.py#L186)

Останавливает поток парной сверки при завершении Core. Использует self._stop.set, self._thread.join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog-job"></a>

## `PairedComparisonCatalog.job`

[media_manager/paired_comparison.py:193](../../media_manager/paired_comparison.py#L193)

Собирает отчёт, счётчики, ошибки корней и сведения о копировании. Явно отклоняет недопустимое состояние через KeyError.

```python
def job(self, job)
```

SQLite: чтение `paired_entries`, `paired_jobs`, `paired_rows`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT * FROM paired_jobs WHERE id=?', (job,)).fetchone`, `db.execute('SELECT COUNT(*) FROM paired_rows WHERE job_id=?', (job,)).fetchone`, `dict`, `json.loads`, `json.loads(r['data']).get`, `len`, `self.storage.connect`, `self.transfers.candidates`, `self.transfers.latest`.

Явные `raise`:

- `KeyError('Сверка пары не найдена')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-pairedcomparisoncatalog-jobs"></a>

## `PairedComparisonCatalog.jobs`

[media_manager/paired_comparison.py:211](../../media_manager/paired_comparison.py#L211)

Возвращает последние отчёты всех пар или выбранной копии. Читает SQLite-таблицы: paired_jobs.

```python
def jobs(self, copy_id=None)
```

SQLite: чтение `paired_jobs`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self.job](../../media_manager/paired_comparison.py#L193), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `[self.job(job) for job in ids]`


<a id="symbol-pairedcomparisoncatalog--save-entry"></a>

## `PairedComparisonCatalog._save_entry`

[media_manager/paired_comparison.py:219](../../media_manager/paired_comparison.py#L219)

Сохраняет метаданные одного элемента стороны сверки в JSON. Изменяет SQLite-таблицы: paired_entries.

```python
def _save_entry(self, db, job, side, path, data)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `paired_entries`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `json.dumps`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--entries"></a>

## `PairedComparisonCatalog._entries`

[media_manager/paired_comparison.py:225](../../media_manager/paired_comparison.py#L225)

Восстанавливает индекс элементов выбранной стороны из SQLite. Читает SQLite-таблицы: paired_entries.

```python
def _entries(self, job, side)
```

SQLite: чтение `paired_entries`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `json.loads`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `{r['path']: json.loads(r['data']) for r in db.execute('SELECT path,data FROM paired_entries WHERE job_id=? AND side=?', (job, side))}`


<a id="symbol-pairedcomparisoncatalog--inventory"></a>

## `PairedComparisonCatalog._inventory`

[media_manager/paired_comparison.py:232](../../media_manager/paired_comparison.py#L232)

Обходит одну сторону пары и сохраняет перечень элементов и ошибки. Изменяет SQLite-таблицы: directories, paired_entries, paired_jobs.

```python
def _inventory(self, job, side, scope, volume, files)
```

SQLite: чтение `paired_entries`; запись/DDL `directories`, `paired_entries`, `paired_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `'/'.join`, `OSError`, [absolute_scope_path](../../media_manager/paired_comparison.py#L30), `children.append`, `db.execute`, `db.execute('SELECT data FROM paired_entries WHERE job_id=? AND side=? AND path=?', (job, side, path)).fetchone`, `e.get`, `entries.append`, `entry.get`, `entry.update`, `fingerprint`, `item.is_dir`, `item.is_file`, `item.is_symlink`, `item.name.startswith`, `item.stat`, `json.dumps`, `json.loads`, `now`, `open_readonly`, `os.fstat`, `os.scandir`, `pending.extend`, `pending.pop`, `reversed`, [self._check](../../media_manager/paired_comparison.py#L105), [self._save_entry](../../media_manager/paired_comparison.py#L219), [self._update](../../media_manager/paired_comparison.py#L97), `self.storage.connect`, `service_file`, `str`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--hash"></a>

## `PairedComparisonCatalog._hash`

[media_manager/paired_comparison.py:289](../../media_manager/paired_comparison.py#L289)

Читает SHA-256 одного файла с проверкой его параметров до и после чтения. Явно отклоняет недопустимое состояние через OSError.

```python
def _hash(self, job, side, entry, volume, counters)
```

Присваивания полям `self`: `_flush_at`.

Прямые выражения вызова: `OSError`, `any`, `before.items`, `digest.hexdigest`, `digest.update`, `entry.get`, `entry.update`, `fingerprint`, `hashlib.sha256`, `len`, `now`, `open_readonly`, `os.fstat`, `os.read`, [self._check](../../media_manager/paired_comparison.py#L105), [self._save_entry](../../media_manager/paired_comparison.py#L219), [self._update](../../media_manager/paired_comparison.py#L97), `self.storage.connect`, `str`, `time.monotonic`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`
- `OSError('Файл изменился после сбора списка. Запусти новую сверку.')`
- `OSError('Файл вырос во время чтения')`
- `OSError('Файл изменился во время чтения')`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--hash-pairs"></a>

## `PairedComparisonCatalog._hash_pairs`

[media_manager/paired_comparison.py:330](../../media_manager/paired_comparison.py#L330)

Проверяет содержимое пар файлов одинакового размера и повторно проверяет версии. Явно отклоняет недопустимое состояние через OSError.

```python
def _hash_pairs(self, job, inventories, volumes)
```

Прямые выражения вызова: `OSError`, `any`, `candidates.append`, `dict`, `entry.get`, `entry.update`, `fingerprint`, `fingerprint(os.fstat(descriptor)).items`, `inventories['left'].items`, `inventories['right'].get`, `left.get`, `len`, `open_readonly`, `os.fstat`, `right.get`, [self._check](../../media_manager/paired_comparison.py#L105), [self._hash](../../media_manager/paired_comparison.py#L289), [self._save_entry](../../media_manager/paired_comparison.py#L219), [self._update](../../media_manager/paired_comparison.py#L97), `self.storage.connect`, `str`, `sum`, `volumes.get`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`
- `OSError('Файл изменился до завершения сверки')`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog--status"></a>

## `PairedComparisonCatalog._status`

[media_manager/paired_comparison.py:363](../../media_manager/paired_comparison.py#L363)

Классифицирует строку по наличию сторон, типу, ошибкам и выбранному методу. Использует any, e.get, left.get, path.startswith, right.get.

```python
def _status(path, left, right, failures, files, method)
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `any`, `e.get`, `left.get`, `path.startswith`, `right.get`.

Выражения возврата (ветви, без исполнения):

- `'unverified'`
- `'skipped'`
- `'missing_copy'`
- `'extra_copy'`
- `'conflict'`
- `'both'`
- `'size_different' if method == 'size' else 'different'`
- `'same_size'`
- `'same' if left['digest'] == right['digest'] else 'different'`


<a id="symbol-pairedcomparisoncatalog--classify"></a>

## `PairedComparisonCatalog._classify`

[media_manager/paired_comparison.py:393](../../media_manager/paired_comparison.py#L393)

Выравнивает стороны по пути и сохраняет статусы и счётчики различий. Изменяет SQLite-таблицы: paired_decisions, paired_rows.

```python
def _classify(self, job, inventories, files, method)
```

SQLite: чтение `paired_decisions`, `paired_jobs`, `paired_rows`; запись/DDL `paired_decisions`, `paired_rows`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `any`, `bool`, `children.get`, `children.setdefault`, `children.setdefault('' if parent == '.' else parent, []).append`, `db.execute`, `db.execute('SELECT base_job_id FROM paired_jobs WHERE id=?', (job,)).fetchone`, `db.execute('SELECT copy_id FROM paired_jobs WHERE id=?', (job,)).fetchone`, `db.executemany`, `e.get`, `entries.items`, `entries.values`, `enumerate`, `inventories.items`, `inventories.values`, `inventories['left'].get`, `inventories['left'].keys`, `inventories['right'].get`, `inventories['right'].keys`, `json.dumps`, `len`, `list`, `ordered.append`, `pending.extend`, `pending.pop`, `reversed`, `right.get`, `rows.values`, [self._check](../../media_manager/paired_comparison.py#L105), [self._status](../../media_manager/paired_comparison.py#L363), `self.storage.connect`, `self.transfers.incomplete`, `sorted`, `str`, `sum`.

Выражения возврата (ветви, без исполнения):

- `errors`


<a id="symbol-pairedcomparisoncatalog-run"></a>

## `PairedComparisonCatalog.run`

[media_manager/paired_comparison.py:444](../../media_manager/paired_comparison.py#L444)

Выполняет индексацию, дополнительное хеширование и сборку результата пары. Обрабатывает ошибки: Exception, Paused.

```python
def run(self, job)
```

Прямые выражения вызова: `current.get`, `report['scopes'].items`, [self._classify](../../media_manager/paired_comparison.py#L393), [self._entries](../../media_manager/paired_comparison.py#L225), [self._hash_pairs](../../media_manager/paired_comparison.py#L330), [self._inventory](../../media_manager/paired_comparison.py#L232), [self._update](../../media_manager/paired_comparison.py#L97), [self.job](../../media_manager/paired_comparison.py#L193), `self.storage.refresh`, `str`.

Перехватываемые типы: `Paused`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedcomparisoncatalog-rows"></a>

## `PairedComparisonCatalog.rows`

[media_manager/paired_comparison.py:467](../../media_manager/paired_comparison.py#L467)

Возвращает страницу строк отчёта с фильтрацией и наследуемыми решениями. Поля результата: rows, total, offset.

```python
def rows(self, job, offset=0, limit=1000, differences_only=False)
```

SQLite: чтение `paired_decisions`, `paired_rows`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `db.execute`, `db.execute('SELECT COUNT(*) FROM paired_rows r WHERE r.job_id=?' + predicate, (job,)).fetchone`, `dict`, `json.loads`, `rows.append`, [self.job](../../media_manager/paired_comparison.py#L193), `self.storage.connect`, `str`.

Выражения возврата (ветви, без исполнения):

- `{'rows': rows, 'total': total, 'offset': offset}`


<a id="symbol-pairedcomparisoncatalog-decide"></a>

## `PairedComparisonCatalog.decide`

[media_manager/paired_comparison.py:491](../../media_manager/paired_comparison.py#L491)

Сохраняет или снимает решение для элемента только в копии. Решения keep/add_main/move/remove являются планом и не изменяют пользовательские файлы.

```python
def decide(self, job, path, action)
```

SQLite: чтение `paired_decisions`, `paired_rows`; запись/DDL `paired_decisions`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `db.execute`, `db.execute('SELECT status FROM paired_rows WHERE job_id=? AND path=?', (job, path)).fetchone`, `now`, `relative_path`, `self.storage.connect`.

Явные `raise`:

- `ValueError('Неизвестное решение')`
- `ValueError('Решение можно назначить элементу «Только в копии».')`

Выражения возврата (ветви, без исполнения):

- `{'path': path, 'action': action}`
