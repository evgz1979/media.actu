# Размеры папок: `media_manager/directory_sizes.py`

Вычисляет логические размеры и количество файлов одним обходом с сохранением промежуточных итогов. Два потока создаются по первому запросу; очередь живёт в памяти, результаты — в SQLite.

[Исходный модуль](../../media_manager/directory_sizes.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_directory_sizes.py](../../tests/test_directory_sizes.py#L12), [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L13).

## Оглавление определений

- [within](#symbol-within) — Проверяет, лежит ли путь внутри выбранного относительного корня.
- [DirectorySizeService](#symbol-directorysizeservice) — Считает логические размеры папок в фоне и сохраняет результаты для отключённых томов.
- [DirectorySizeService.__init__](#symbol-directorysizeservice---init--) — Инициализирует DirectorySizeService и его рабочее состояние.
- [DirectorySizeService.close](#symbol-directorysizeservice-close) — Останавливает очередь размеров и пробуждает ожидающие потоки.
- [DirectorySizeService.request](#symbol-directorysizeservice-request) — Возвращает сохранённые размеры и при разрешении ставит непокрытые области в очередь.
- [DirectorySizeService._worker](#symbol-directorysizeservice--worker) — Извлекает области из очереди и записывает результаты либо ошибки подсчёта.
- [DirectorySizeService.calculate](#symbol-directorysizeservice-calculate) — Обходит дерево снизу вверх и сохраняет размеры каждой доступной папки.

<a id="symbol-within"></a>

## `within`

[media_manager/directory_sizes.py:17](../../media_manager/directory_sizes.py#L17)

Проверяет, лежит ли путь внутри выбранного относительного корня. Использует path.startswith.

```python
def within(path, root)
```

Прямые выражения вызова: `path.startswith`.

Выражения возврата (ветви, без исполнения):

- `not root or path == root or path.startswith(root + '/')`


<a id="symbol-directorysizeservice"></a>

## `DirectorySizeService`

[media_manager/directory_sizes.py:23](../../media_manager/directory_sizes.py#L23)

Считает логические размеры папок в фоне и сохраняет результаты для отключённых томов. Зависимости конструктора: storage.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_condition`, `_failures`, `_jobs`, `_queue`, `_stop`, `_workers`, `storage`.

Именованные методы: `__init__`, `close`, `request`, `_worker`, `calculate`.

<a id="symbol-directorysizeservice---init--"></a>

## `DirectorySizeService.__init__`

[media_manager/directory_sizes.py:26](../../media_manager/directory_sizes.py#L26)

Инициализирует DirectorySizeService и его рабочее состояние. Изменяет SQLite-таблицы: directory_sizes.

```python
def __init__(self, storage)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `directory_sizes`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_condition`, `_failures`, `_jobs`, `_queue`, `_stop`, `_workers`, `storage`.

Прямые выражения вызова: `db.execute`, `deque`, `storage.connect`, `threading.Condition`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-directorysizeservice-close"></a>

## `DirectorySizeService.close`

[media_manager/directory_sizes.py:45](../../media_manager/directory_sizes.py#L45)

Останавливает очередь размеров и пробуждает ожидающие потоки. Использует self._condition.notify_all, self._stop.set, worker.join.

```python
def close(self)
```

Прямые выражения вызова: `self._condition.notify_all`, `self._stop.set`, `worker.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-directorysizeservice-request"></a>

## `DirectorySizeService.request`

[media_manager/directory_sizes.py:54](../../media_manager/directory_sizes.py#L54)

Возвращает сохранённые размеры и при разрешении ставит непокрытые области в очередь. Поля результата: sizes.

```python
def request(self, volume_id, paths, *, start=True, refresh=False)
```

SQLite: чтение `directory_sizes`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_workers`.

Прямые выражения вызова: `','.join`, `any`, `bool`, `db.execute`, `dict`, `next`, `now`, `range`, `records.get`, `relative_path`, `self._condition.notify_all`, `self._failures.get`, `self._failures.pop`, `self._jobs.items`, `self._queue.append`, `self.storage._mounted.get`, `self.storage.connect`, `self.storage.get_volume`, `self.storage.refresh`, `sorted`, `threading.Thread`, `value.update`, `volume.get`, [within](../../media_manager/directory_sizes.py#L17), `worker.start`.

Выражения возврата (ветви, без исполнения):

- `{'sizes': sizes}`


<a id="symbol-directorysizeservice--worker"></a>

## `DirectorySizeService._worker`

[media_manager/directory_sizes.py:103](../../media_manager/directory_sizes.py#L103)

Извлекает области из очереди и записывает результаты либо ошибки подсчёта. Обрабатывает ошибки: Exception.

```python
def _worker(self)
```

Прямые выражения вызова: `self._condition.wait_for`, `self._jobs.pop`, `self._queue.popleft`, `self._stop.is_set`, [self.calculate](../../media_manager/directory_sizes.py#L122), `str`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-directorysizeservice-calculate"></a>

## `DirectorySizeService.calculate`

[media_manager/directory_sizes.py:122](../../media_manager/directory_sizes.py#L122)

Обходит дерево снизу вверх и сохраняет размеры каждой доступной папки. Изменяет SQLite-таблицы: directory_sizes.

```python
def calculate(self, volume_id, path)
```

SQLite: чтение `directory_sizes`; запись/DDL `directory_sizes`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `'/'.join`, `OSError`, `PurePosixPath`, `db.execute`, `db.execute('SELECT bytes,files,complete FROM directory_sizes WHERE volume_id=? AND path=?', (volume_id, current)).fetchone`, `dict`, `entry.stat`, `filter`, `next`, `now`, `open_readonly`, `os.fstat`, `os.scandir`, `pending.append`, `pending.extend`, `pending.pop`, `relative_path`, `reversed`, `self._failures.pop`, `self._stop.is_set`, `self.storage.connect`, `self.storage.refresh`, `service_file`, `stat.S_ISDIR`, `stat.S_ISREG`, `str`, `total.pop`, `total.update`, `total['children'].append`, `totals.pop`, `tuple`.

Явные `raise`:

- `OSError('Том отключён или недоступен')`
- `OSError('Папка была заменена во время подсчёта')`
- `OSError('Том был отключён или заменён во время подсчёта')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `None`
