# Сверка связанных папок: `media_manager/paired_comparison.py`

Симметричная сверка выбранного источника и копии: структура, имя и размер, дополнительный SHA-256; хранит выровненные строки и решения пользователя.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/paired_comparison.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [media_manager/copy_files.py](media_manager--copy_files.md), [paired_workspace_ui.py](paired_workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_copy_connections.py](tests.md#module-tests.test_copy_connections), [tests/test_copy_files.py](tests.md#module-tests.test_copy_files), [tests/test_copy_number_release.py](tests.md#module-tests.test_copy_number_release), [tests/test_folder_markers.py](tests.md#module-tests.test_folder_markers), [tests/test_paired_comparison.py](tests.md#module-tests.test_paired_comparison).

## Оглавление определений

- [PairedComparisonCatalog](#symbol-PairedComparisonCatalog) — Ведёт двухсторонние сверки, выровненные строки и решения по лишним элементам.
- [PairedComparisonCatalog.__init__](#symbol-PairedComparisonCatalog.__init__) — Инициализирует PairedComparisonCatalog и его рабочее состояние.
- [PairedComparisonCatalog._check](#symbol-PairedComparisonCatalog._check) — Прерывает обход, если пользователь запросил паузу сверки.
- [PairedComparisonCatalog._classify](#symbol-PairedComparisonCatalog._classify) — Выравнивает стороны по пути и сохраняет статусы и счётчики различий.
- [PairedComparisonCatalog._entries](#symbol-PairedComparisonCatalog._entries) — Восстанавливает индекс элементов выбранной стороны из SQLite.
- [PairedComparisonCatalog._hash](#symbol-PairedComparisonCatalog._hash) — Читает SHA-256 одного файла с проверкой его параметров до и после чтения.
- [PairedComparisonCatalog._hash_pairs](#symbol-PairedComparisonCatalog._hash_pairs) — Проверяет содержимое пар файлов одинакового размера и повторно проверяет версии.
- [PairedComparisonCatalog._idle](#symbol-PairedComparisonCatalog._idle) — Проверяет отсутствие конфликтующей парной или общей сверки.
- [PairedComparisonCatalog._inventory](#symbol-PairedComparisonCatalog._inventory) — Обходит одну сторону пары и сохраняет перечень элементов и ошибки.
- [PairedComparisonCatalog._pair](#symbol-PairedComparisonCatalog._pair) — Разрешает актуальный источник и назначение действующей связи копии.
- [PairedComparisonCatalog._save_entry](#symbol-PairedComparisonCatalog._save_entry) — Сохраняет метаданные одного элемента стороны сверки в JSON.
- [PairedComparisonCatalog._status](#symbol-PairedComparisonCatalog._status) — Классифицирует строку по наличию сторон, типу, ошибкам и выбранному методу.
- [PairedComparisonCatalog._update](#symbol-PairedComparisonCatalog._update) — Сохраняет поля парной сверки и время последнего изменения.
- [PairedComparisonCatalog.busy](#symbol-PairedComparisonCatalog.busy) — Проверяет работу парной сверки или связанной операции копирования.
- [PairedComparisonCatalog.close](#symbol-PairedComparisonCatalog.close) — Останавливает поток парной сверки при завершении Core.
- [PairedComparisonCatalog.create](#symbol-PairedComparisonCatalog.create) — Создаёт сверку структуры или файлов для зарегистрированной пары.
- [PairedComparisonCatalog.decide](#symbol-PairedComparisonCatalog.decide) — Сохраняет или снимает решение для элемента только в копии.
- [PairedComparisonCatalog.job](#symbol-PairedComparisonCatalog.job) — Собирает отчёт, счётчики, ошибки корней и сведения о копировании.
- [PairedComparisonCatalog.jobs](#symbol-PairedComparisonCatalog.jobs) — Возвращает последние отчёты всех пар или выбранной копии.
- [PairedComparisonCatalog.pause](#symbol-PairedComparisonCatalog.pause) — Запрашивает кооперативную остановку выбранной парной сверки.
- [PairedComparisonCatalog.resume](#symbol-PairedComparisonCatalog.resume) — Продолжает приостановленную сверку после проверки неизменности связи.
- [PairedComparisonCatalog.rows](#symbol-PairedComparisonCatalog.rows) — Возвращает страницу строк отчёта с фильтрацией и наследуемыми решениями.
- [PairedComparisonCatalog.run](#symbol-PairedComparisonCatalog.run) — Выполняет индексацию, дополнительное хеширование и сборку результата пары.
- [absolute_scope_path](#symbol-absolute_scope_path) — Объединяет корень зарегистрированной области и относительный путь строки.

## Константы и значения по умолчанию

<a id="constant-DECISIONS"></a>

### `DECISIONS`

`{'keep': 'Оставить в копии', 'add_main': 'Добавить в 00-main', 'move': 'Подготовить перенос', 'remove': 'Подготовить удаление'}`

<a id="constant-STATUS_LABELS"></a>

### `STATUS_LABELS`

`{'both': 'Есть в обеих', 'missing_copy': 'Нет в копии', 'extra_copy': 'Только в копии', 'same': 'Совпадает', 'different': 'Отличается', 'conflict': 'Разный тип', 'same_size': 'Имя и размер совпали', 'size_different': 'Размер отличается', 'copy_incomplete': 'Копия не завершена', 'unverified': 'Не проверено', 'skipped': 'Не сравнивается'}`


<a id="symbol-PairedComparisonCatalog"></a>

## `PairedComparisonCatalog`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog`

Ведёт двухсторонние сверки, выровненные строки и решения по лишним элементам. Зависимости конструктора: storage, copies, legacy.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_flush_at`, `_lock`, `_stop`, `_thread`, `copies`, `legacy`, `storage`, `transfers`.

Именованные методы: `__init__`, `busy`, `_idle`, `_update`, `_check`, `_pair`, `create`, `resume`, `pause`, `close`, `job`, `jobs`, `_save_entry`, `_entries`, `_inventory`, `_hash`, `_hash_pairs`, `_status`, `_classify`, `run`, `rows`, `decide`.

<a id="symbol-PairedComparisonCatalog.__init__"></a>

## `PairedComparisonCatalog.__init__`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.__init__`

Инициализирует PairedComparisonCatalog и его рабочее состояние. Изменяет SQLite-таблицы: paired_decisions, paired_entries, paired_jobs, paired_rows.

```python
def __init__(self, storage, copies, legacy=None)
```

SQLite: чтение не найдено; запись/DDL `paired_decisions`, `paired_entries`, `paired_jobs`, `paired_rows`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_flush_at`, `_lock`, `_stop`, `_thread`, `copies`, `legacy`, `storage`, `transfers`.

Прямые выражения вызова: `db.execute`, `db.executescript`, `now`, `storage.connect`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._check"></a>

## `PairedComparisonCatalog._check`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._check`

Прерывает обход, если пользователь запросил паузу сверки. Явно отклоняет недопустимое состояние через Paused.

```python
def _check(self)
```

Прямые выражения вызова: `Paused`, `self._stop.is_set`.

Явные `raise`:

- `Paused()`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._classify"></a>

## `PairedComparisonCatalog._classify`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._classify`

Выравнивает стороны по пути и сохраняет статусы и счётчики различий. Изменяет SQLite-таблицы: paired_decisions, paired_rows.

```python
def _classify(self, job, inventories, files, method)
```

SQLite: чтение `paired_decisions`, `paired_jobs`, `paired_rows`; запись/DDL `paired_decisions`, `paired_rows`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `any`, `bool`, `children.get`, `children.setdefault`, `children.setdefault('' if parent == '.' else parent, []).append`, `db.execute`, `db.execute('SELECT base_job_id FROM paired_jobs WHERE id=?', (job,)).fetchone`, `db.execute('SELECT copy_id FROM paired_jobs WHERE id=?', (job,)).fetchone`, `db.executemany`, `e.get`, `entries.items`, `entries.values`, `enumerate`, `inventories.items`, `inventories.values`, `inventories['left'].get`, `inventories['left'].keys`, `inventories['right'].get`, `inventories['right'].keys`, `json.dumps`, `len`, `list`, `ordered.append`, `pending.extend`, `pending.pop`, `reversed`, `right.get`, `rows.values`, [self._check](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._check), [self._status](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._status), `self.storage.connect`, `self.transfers.incomplete`, `sorted`, `str`, `sum`.

Выражения возврата (ветви, без исполнения):

- `errors`


<a id="symbol-PairedComparisonCatalog._entries"></a>

## `PairedComparisonCatalog._entries`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._entries`

Восстанавливает индекс элементов выбранной стороны из SQLite. Читает SQLite-таблицы: paired_entries.

```python
def _entries(self, job, side)
```

SQLite: чтение `paired_entries`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `json.loads`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `{r['path']: json.loads(r['data']) for r in db.execute('SELECT path,data FROM paired_entries WHERE job_id=? AND side=?', (job, side))}`


<a id="symbol-PairedComparisonCatalog._hash"></a>

## `PairedComparisonCatalog._hash`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._hash`

Читает SHA-256 одного файла с проверкой его параметров до и после чтения. Явно отклоняет недопустимое состояние через OSError.

```python
def _hash(self, job, side, entry, volume, counters)
```

Присваивания полям `self`: `_flush_at`.

Прямые выражения вызова: `OSError`, `any`, `before.items`, `digest.hexdigest`, `digest.update`, `entry.get`, `entry.update`, `fingerprint`, `hashlib.sha256`, `len`, `now`, `open_readonly`, `os.fstat`, `os.read`, [self._check](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._check), [self._save_entry](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._save_entry), [self._update](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._update), `self.storage.connect`, `str`, `time.monotonic`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`
- `OSError('Файл изменился после сбора списка. Запусти новую сверку.')`
- `OSError('Файл вырос во время чтения')`
- `OSError('Файл изменился во время чтения')`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._hash_pairs"></a>

## `PairedComparisonCatalog._hash_pairs`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._hash_pairs`

Проверяет содержимое пар файлов одинакового размера и повторно проверяет версии. Явно отклоняет недопустимое состояние через OSError.

```python
def _hash_pairs(self, job, inventories, volumes)
```

Прямые выражения вызова: `OSError`, `any`, `candidates.append`, `dict`, `entry.get`, `entry.update`, `fingerprint`, `fingerprint(os.fstat(descriptor)).items`, `inventories['left'].items`, `inventories['right'].get`, `left.get`, `len`, `open_readonly`, `os.fstat`, `right.get`, [self._check](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._check), [self._hash](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._hash), [self._save_entry](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._save_entry), [self._update](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._update), `self.storage.connect`, `str`, `sum`, `volumes.get`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`
- `OSError('Файл изменился до завершения сверки')`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._idle"></a>

## `PairedComparisonCatalog._idle`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._idle`

Проверяет отсутствие конфликтующей парной или общей сверки. Явно отклоняет недопустимое состояние через ValueError.

```python
def _idle(self)
```

Прямые выражения вызова: `ValueError`, [self.busy](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.busy), `self.legacy._assert_idle`.

Явные `raise`:

- `ValueError('Другая сверка ещё выполняется. Сначала останови её.')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._inventory"></a>

## `PairedComparisonCatalog._inventory`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._inventory`

Обходит одну сторону пары и сохраняет перечень элементов и ошибки. Изменяет SQLite-таблицы: directories, paired_entries, paired_jobs.

```python
def _inventory(self, job, side, scope, volume, files)
```

SQLite: чтение `paired_entries`; запись/DDL `directories`, `paired_entries`, `paired_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `'/'.join`, `OSError`, [absolute_scope_path](media_manager--paired_comparison.md#symbol-absolute_scope_path), `children.append`, `db.execute`, `db.execute('SELECT data FROM paired_entries WHERE job_id=? AND side=? AND path=?', (job, side, path)).fetchone`, `e.get`, `entries.append`, `entry.get`, `entry.update`, `fingerprint`, `item.is_dir`, `item.is_file`, `item.is_symlink`, `item.name.startswith`, `item.stat`, `json.dumps`, `json.loads`, `now`, `open_readonly`, `os.fstat`, `os.scandir`, `pending.extend`, `pending.pop`, `reversed`, [self._check](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._check), [self._save_entry](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._save_entry), [self._update](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._update), `self.storage.connect`, `service_file`, `str`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`

Перехватываемые типы: `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._pair"></a>

## `PairedComparisonCatalog._pair`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._pair`

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


<a id="symbol-PairedComparisonCatalog._save_entry"></a>

## `PairedComparisonCatalog._save_entry`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._save_entry`

Сохраняет метаданные одного элемента стороны сверки в JSON. Изменяет SQLite-таблицы: paired_entries.

```python
def _save_entry(self, db, job, side, path, data)
```

SQLite: чтение не найдено; запись/DDL `paired_entries`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `json.dumps`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog._status"></a>

## `PairedComparisonCatalog._status`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._status`

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


<a id="symbol-PairedComparisonCatalog._update"></a>

## `PairedComparisonCatalog._update`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog._update`

Сохраняет поля парной сверки и время последнего изменения. Изменяет SQLite-таблицы: paired_jobs.

```python
def _update(self, job, **values)
```

SQLite: чтение не найдено; запись/DDL `paired_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `','.join`, `db.execute`, `now`, `self.storage.connect`, `values.values`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog.busy"></a>

## `PairedComparisonCatalog.busy`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.busy`

Проверяет работу парной сверки или связанной операции копирования. Использует self._thread.is_alive, self.transfers.busy.

```python
def busy(self)
```

Прямые выражения вызова: `bool`, `self._thread.is_alive`, `self.transfers.busy`.

Выражения возврата (ветви, без исполнения):

- `self._thread is not None and self._thread.is_alive() or bool(self.transfers and self.transfers.busy())`


<a id="symbol-PairedComparisonCatalog.close"></a>

## `PairedComparisonCatalog.close`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.close`

Останавливает поток парной сверки при завершении Core. Использует self._stop.set, self._thread.join.

```python
def close(self)
```

Прямые выражения вызова: `self._stop.set`, `self._thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedComparisonCatalog.create"></a>

## `PairedComparisonCatalog.create`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.create`

Создаёт сверку структуры или файлов для зарегистрированной пары. Изменяет SQLite-таблицы: paired_jobs.

```python
def create(self, copy_id, mode='folders', base_job_id=None, *, method='size', background=True)
```

SQLite: чтение не найдено; запись/DDL `paired_jobs`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `ValueError`, `any`, `db.execute`, `json.dumps`, `now`, `scopes.values`, [self._idle](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._idle), [self._pair](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._pair), [self.job](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.job), [self.resume](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.resume), `self.storage.connect`, `self.storage.get_volume`, `uuid4`.

Явные `raise`:

- `ValueError('Неизвестный вид сверки')`
- `ValueError('Неизвестный метод сверки файлов')`
- `ValueError('Сначала заверши сверку папок этой пары.')`
- `ValueError('Связь изменилась. Сначала заново сверь папки.')`
- `ValueError('Сначала подтверди подключённый диск.')`

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-PairedComparisonCatalog.decide"></a>

## `PairedComparisonCatalog.decide`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.decide`

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


<a id="symbol-PairedComparisonCatalog.job"></a>

## `PairedComparisonCatalog.job`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.job`

Собирает отчёт, счётчики, ошибки корней и сведения о копировании. Явно отклоняет недопустимое состояние через KeyError.

```python
def job(self, job)
```

SQLite: чтение `paired_entries`, `paired_jobs`, `paired_rows`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT * FROM paired_jobs WHERE id=?', (job,)).fetchone`, `db.execute('SELECT COUNT(*) FROM paired_rows WHERE job_id=?', (job,)).fetchone`, `dict`, `json.loads`, `json.loads(r['data']).get`, `len`, `self.storage.connect`, `self.transfers.candidates`, `self.transfers.latest`.

Явные `raise`:

- `KeyError('Сверка пары не найдена')`

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-PairedComparisonCatalog.jobs"></a>

## `PairedComparisonCatalog.jobs`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.jobs`

Возвращает последние отчёты всех пар или выбранной копии. Читает SQLite-таблицы: paired_jobs.

```python
def jobs(self, copy_id=None)
```

SQLite: чтение `paired_jobs`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, [self.job](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.job), `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `[self.job(job) for job in ids]`


<a id="symbol-PairedComparisonCatalog.pause"></a>

## `PairedComparisonCatalog.pause`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.pause`

Запрашивает кооперативную остановку выбранной парной сверки. Использует self._stop.set, self._update, self.job.

```python
def pause(self, job)
```

Прямые выражения вызова: `self._stop.set`, [self._update](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._update), [self.job](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.job).

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-PairedComparisonCatalog.resume"></a>

## `PairedComparisonCatalog.resume`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.resume`

Продолжает приостановленную сверку после проверки неизменности связи. Явно отклоняет недопустимое состояние через ValueError.

```python
def resume(self, job)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `ValueError`, `any`, [self._idle](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._idle), [self._pair](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._pair), `self._stop.clear`, `self._thread.start`, [self._update](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._update), [self.job](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.job), `threading.Thread`.

Явные `raise`:

- `ValueError('Эту сверку нельзя продолжить.')`
- `ValueError('Источник или связь изменились. Начни новую сверку.')`

Выражения возврата (ветви, без исполнения):

- `self.job(job)`


<a id="symbol-PairedComparisonCatalog.rows"></a>

## `PairedComparisonCatalog.rows`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.rows`

Возвращает страницу строк отчёта с фильтрацией и наследуемыми решениями. Поля результата: rows, total, offset.

```python
def rows(self, job, offset=0, limit=1000, differences_only=False)
```

SQLite: чтение `paired_decisions`, `paired_rows`; запись/DDL не найдена. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `db.execute`, `db.execute('SELECT COUNT(*) FROM paired_rows r WHERE r.job_id=?' + predicate, (job,)).fetchone`, `dict`, `json.loads`, `rows.append`, [self.job](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.job), `self.storage.connect`, `str`.

Выражения возврата (ветви, без исполнения):

- `{'rows': rows, 'total': total, 'offset': offset}`


<a id="symbol-PairedComparisonCatalog.run"></a>

## `PairedComparisonCatalog.run`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `PairedComparisonCatalog.run`

Выполняет индексацию, дополнительное хеширование и сборку результата пары. Обрабатывает ошибки: Exception, Paused.

```python
def run(self, job)
```

Прямые выражения вызова: `current.get`, `report['scopes'].items`, [self._classify](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._classify), [self._entries](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._entries), [self._hash_pairs](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._hash_pairs), [self._inventory](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._inventory), [self._update](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog._update), [self.job](media_manager--paired_comparison.md#symbol-PairedComparisonCatalog.job), `self.storage.refresh`, `str`.

Перехватываемые типы: `Paused`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-absolute_scope_path"></a>

## `absolute_scope_path`

[media_manager/paired_comparison.py](../../media_manager/paired_comparison.py) · `absolute_scope_path`

Объединяет корень зарегистрированной области и относительный путь строки. Использует '/'.join, relative_path.

```python
def absolute_scope_path(scope, path)
```

Прямые выражения вызова: `'/'.join`, `relative_path`.

Выражения возврата (ветви, без исполнения):

- `'/'.join((part for part in (scope['path'], relative_path(path)) if part))`
