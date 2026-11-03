# Фоновые воркеры превью: `media_manager/thumbnail_workers.py`

Постоянная очередь заданий находится в Catalog; потоки берут её независимо для folder и photos, сохраняют завершение, временное ожидание и ошибки.

[Исходный модуль](../../media_manager/thumbnail_workers.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/catalog.py](media_manager--catalog.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md), [media_manager/thumbnails.py](media_manager--thumbnails.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: нет; возможна косвенная проверка через вызывающие компоненты.

## Оглавление определений

- [ThumbnailWorkerPool](#symbol-thumbnailworkerpool) — Обрабатывает постоянную очередь обычными и отдельными Photos-воркерами.
- [ThumbnailWorkerPool.__init__](#symbol-thumbnailworkerpool---init--) — Инициализирует ThumbnailWorkerPool и его рабочее состояние.
- [ThumbnailWorkerPool.start](#symbol-thumbnailworkerpool-start) — Восстанавливает очередь после перезапуска и запускает настроенные потоки.
- [ThumbnailWorkerPool.stop](#symbol-thumbnailworkerpool-stop) — Запрашивает остановку воркеров и пробуждает ожидающие потоки.
- [ThumbnailWorkerPool.wake](#symbol-thumbnailworkerpool-wake) — Сигнализирует о новых заданиях или изменении условий обработки.
- [ThumbnailWorkerPool.status](#symbol-thumbnailworkerpool-status) — Собирает постоянные счётчики очереди и текущее состояние потоков.
- [ThumbnailWorkerPool._work](#symbol-thumbnailworkerpool--work) — Выдаёт и обрабатывает задания одного вида с разбором временных ошибок.
- [ThumbnailWorkerPool._wait](#symbol-thumbnailworkerpool--wait) — Ожидает сигнал пробуждения или истечение короткого интервала опроса.
- [ThumbnailWorkerPool._set_state](#symbol-thumbnailworkerpool--set-state) — Потокобезопасно обновляет диагностическое состояние одного воркера.

<a id="symbol-thumbnailworkerpool"></a>

## `ThumbnailWorkerPool`

[media_manager/thumbnail_workers.py:12](../../media_manager/thumbnail_workers.py#L12)

Обрабатывает постоянную очередь обычными и отдельными Photos-воркерами. Зависимости конструктора: catalog, thumbnails.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_state_lock`, `_states`, `_stop`, `_threads`, `_wake`, `catalog`, `folder_workers`, `photos_workers`, `thumbnails`.

Именованные методы: `__init__`, `start`, `stop`, `wake`, `status`, `_work`, `_wait`, `_set_state`.

<a id="symbol-thumbnailworkerpool---init--"></a>

## `ThumbnailWorkerPool.__init__`

[media_manager/thumbnail_workers.py:15](../../media_manager/thumbnail_workers.py#L15)

Инициализирует ThumbnailWorkerPool и его рабочее состояние. Обновляет состояние объекта: _state_lock, _states, _stop, _threads, _wake, catalog, folder_workers, photos_workers, thumbnails.

```python
def __init__(self, catalog: Catalog, thumbnails: ThumbnailService, *, folder_workers: int=2, photos_workers: int=1) -> None
```

Присваивания полям `self`: `_state_lock`, `_states`, `_stop`, `_threads`, `_wake`, `catalog`, `folder_workers`, `photos_workers`, `thumbnails`.

Прямые выражения вызова: `threading.Event`, `threading.Lock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-thumbnailworkerpool-start"></a>

## `ThumbnailWorkerPool.start`

[media_manager/thumbnail_workers.py:35](../../media_manager/thumbnail_workers.py#L35)

Восстанавливает очередь после перезапуска и запускает настроенные потоки. Использует self._stop.clear, self._threads.append, self.catalog.enqueue_all_thumbnails, self.catalog.reset_running_thumbnail_jobs, thread.start.

```python
def start(self) -> None
```

Прямые выражения вызова: `enumerate`, `self._stop.clear`, `self._threads.append`, `self.catalog.enqueue_all_thumbnails`, `self.catalog.reset_running_thumbnail_jobs`, `thread.start`, `threading.Thread`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-thumbnailworkerpool-stop"></a>

## `ThumbnailWorkerPool.stop`

[media_manager/thumbnail_workers.py:56](../../media_manager/thumbnail_workers.py#L56)

Запрашивает остановку воркеров и пробуждает ожидающие потоки. Использует self._states.clear, self._stop.set, self._threads.clear, self._wake.set, thread.join.

```python
def stop(self) -> None
```

Прямые выражения вызова: `self._states.clear`, `self._stop.set`, `self._threads.clear`, `self._wake.set`, `thread.join`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-thumbnailworkerpool-wake"></a>

## `ThumbnailWorkerPool.wake`

[media_manager/thumbnail_workers.py:67](../../media_manager/thumbnail_workers.py#L67)

Сигнализирует о новых заданиях или изменении условий обработки. Использует self._wake.set.

```python
def wake(self) -> None
```

Прямые выражения вызова: `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-thumbnailworkerpool-status"></a>

## `ThumbnailWorkerPool.status`

[media_manager/thumbnail_workers.py:72](../../media_manager/thumbnail_workers.py#L72)

Собирает постоянные счётчики очереди и текущее состояние потоков. Использует result.update, self._states.values, self.catalog.list_sources, self.catalog.photos_queue_paused, self.catalog.thumbnail_queue_summary.

```python
def status(self) -> dict[str, object]
```

Прямые выражения вызова: `bool`, `dict`, `int`, `list`, `result.update`, `self._states.values`, `self.catalog.list_sources`, `self.catalog.photos_queue_paused`, `self.catalog.thumbnail_queue_summary`, `sorted`, `source.get`, `states.count`, `str`, `sum`, `thread.is_alive`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-thumbnailworkerpool--work"></a>

## `ThumbnailWorkerPool._work`

[media_manager/thumbnail_workers.py:114](../../media_manager/thumbnail_workers.py#L114)

Выдаёт и обрабатывает задания одного вида с разбором временных ошибок. Явно отклоняет недопустимое состояние через RuntimeError.

```python
def _work(self, source_kind: str) -> None
```

Прямые выражения вызова: `RuntimeError`, [self._set_state](../../media_manager/thumbnail_workers.py#L155), `self._stop.is_set`, [self._wait](../../media_manager/thumbnail_workers.py#L149), `self._wake.clear`, `self._wake.wait`, `self.catalog.claim_thumbnail_job`, `self.catalog.defer_thumbnail_job`, `self.catalog.finish_thumbnail_job`, `self.catalog.photos_queue_paused`, `self.catalog.release_thumbnail_job`, `self.catalog.thumbnail_queue_paused`, `self.thumbnails.get_or_create`, `str`, `threading.current_thread`.

Явные `raise`:

- `RuntimeError('Превью недоступно')`

Перехватываемые типы: `PhotosThumbnailPending`, `(PhotosAccessDenied, PhotosLibraryUnavailable)`, `ThumbnailCacheUnavailable`, `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-thumbnailworkerpool--wait"></a>

## `ThumbnailWorkerPool._wait`

[media_manager/thumbnail_workers.py:149](../../media_manager/thumbnail_workers.py#L149)

Ожидает сигнал пробуждения или истечение короткого интервала опроса. Использует self._wake.clear, self._wake.wait.

```python
def _wait(self) -> None
```

Прямые выражения вызова: `self._wake.clear`, `self._wake.wait`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-thumbnailworkerpool--set-state"></a>

## `ThumbnailWorkerPool._set_state`

[media_manager/thumbnail_workers.py:155](../../media_manager/thumbnail_workers.py#L155)

Потокобезопасно обновляет диагностическое состояние одного воркера. Параметры: worker_name, state.

```python
def _set_state(self, worker_name: str, state: str) -> None
```

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
