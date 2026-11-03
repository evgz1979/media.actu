# Отслеживание основных папок: `media_manager/folder_tracking.py`

Наблюдатели Watchdog для подключённых основных папок. Сохраняет сигнал изменения, а не актуальный индекс или доказательство расхождения копий.

[Исходный модуль](../../media_manager/folder_tracking.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/volume_identity.py](media_manager--volume_identity.md), [media_manager/watcher.py](media_manager--watcher.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_folder_tracking.py](../../tests/test_folder_tracking.py#L13).

## Оглавление определений

- [FolderChangeHandler](#symbol-folderchangehandler) — Фильтрует события Watchdog для зарегистрированной основной папки.
- [FolderChangeHandler.on_any_event](#symbol-folderchangehandler-on-any-event) — Отмечает значимое изменение, исключая служебные файлы и события чтения.
- [FolderTrackingService](#symbol-foldertrackingservice) — Поддерживает наблюдатели подключённых основных папок с включённым отслеживанием.
- [FolderTrackingService.__init__](#symbol-foldertrackingservice---init--) — Инициализирует FolderTrackingService и его рабочее состояние.
- [FolderTrackingService.start](#symbol-foldertrackingservice-start) — Запускает фоновое согласование наблюдателей папок.
- [FolderTrackingService.wake](#symbol-foldertrackingservice-wake) — Пробуждает согласование после изменения настроек или подключения.
- [FolderTrackingService.status](#symbol-foldertrackingservice-status) — Возвращает состояние наблюдателя выбранной основной папки.
- [FolderTrackingService._alive](#symbol-foldertrackingservice--alive) — Проверяет работоспособность потока установленного наблюдателя.
- [FolderTrackingService._run](#symbol-foldertrackingservice--run) — Периодически обновляет наблюдатели и обрабатывает накопленные события.
- [FolderTrackingService._remove](#symbol-foldertrackingservice--remove) — Останавливает и удаляет наблюдатель одного набора папок.
- [FolderTrackingService._changed](#symbol-foldertrackingservice--changed) — Записывает изменение основной папки и сбрасывает локальный сигнал обработчика.
- [FolderTrackingService.reconcile](#symbol-foldertrackingservice-reconcile) — Сопоставляет настройки наборов с доступностью томов и существующими наблюдателями.
- [FolderTrackingService.close](#symbol-foldertrackingservice-close) — Останавливает фоновое согласование и все наблюдатели папок.

<a id="symbol-folderchangehandler"></a>

## `FolderChangeHandler`

[media_manager/folder_tracking.py:18](../../media_manager/folder_tracking.py#L18)

Фильтрует события Watchdog для зарегистрированной основной папки. Базовые типы: DebouncedHandler.

Базовые классы: `DebouncedHandler`.


Именованные методы: `on_any_event`.

<a id="symbol-folderchangehandler-on-any-event"></a>

## `FolderChangeHandler.on_any_event`

[media_manager/folder_tracking.py:21](../../media_manager/folder_tracking.py#L21)

Отмечает значимое изменение, исключая служебные файлы и события чтения. Использует Path, all, service_file, super, super().on_any_event.

```python
def on_any_event(self, event)
```

Прямые выражения вызова: `Path`, `all`, `getattr`, `service_file`, `super`, `super().on_any_event`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-foldertrackingservice"></a>

## `FolderTrackingService`

[media_manager/folder_tracking.py:32](../../media_manager/folder_tracking.py#L32)

Поддерживает наблюдатели подключённых основных папок с включённым отслеживанием. Зависимости конструктора: copies.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `_states`, `_stop`, `_thread`, `_wake`, `_watches`, `copies`, `observer`.

Именованные методы: `__init__`, `start`, `wake`, `status`, `_alive`, `_run`, `_remove`, `_changed`, `reconcile`, `close`.

<a id="symbol-foldertrackingservice---init--"></a>

## `FolderTrackingService.__init__`

[media_manager/folder_tracking.py:35](../../media_manager/folder_tracking.py#L35)

Инициализирует FolderTrackingService и его рабочее состояние. Обновляет состояние объекта: _lock, _states, _stop, _thread, _wake, _watches, copies, observer.

```python
def __init__(self, copies)
```

Присваивания полям `self`: `_lock`, `_states`, `_stop`, `_thread`, `_wake`, `_watches`, `copies`, `observer`.

Прямые выражения вызова: `Observer`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice-start"></a>

## `FolderTrackingService.start`

[media_manager/folder_tracking.py:47](../../media_manager/folder_tracking.py#L47)

Запускает фоновое согласование наблюдателей папок. Обновляет состояние объекта: _thread.

```python
def start(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._thread.start`, `self.observer.start`, `threading.Thread`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice-wake"></a>

## `FolderTrackingService.wake`

[media_manager/folder_tracking.py:54](../../media_manager/folder_tracking.py#L54)

Пробуждает согласование после изменения настроек или подключения. Использует self._wake.set.

```python
def wake(self)
```

Прямые выражения вызова: `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice-status"></a>

## `FolderTrackingService.status`

[media_manager/folder_tracking.py:59](../../media_manager/folder_tracking.py#L59)

Возвращает состояние наблюдателя выбранной основной папки. Поля результата: tracking_state, tracking_error.

```python
def status(self, group_id)
```

Прямые выражения вызова: `dict`, [self._alive](../../media_manager/folder_tracking.py#L68), `self._states.get`, `self._watches.get`.

Выражения возврата (ветви, без исполнения):

- `dict(tracking_state='error', tracking_error='Наблюдатель файловой системы остановлен')`
- `dict(self._states.get(group_id, dict(tracking_state='starting', tracking_error=None)))`


<a id="symbol-foldertrackingservice--alive"></a>

## `FolderTrackingService._alive`

[media_manager/folder_tracking.py:68](../../media_manager/folder_tracking.py#L68)

Проверяет работоспособность потока установленного наблюдателя. Использует any, emitter.is_alive.

```python
def _alive(self, watch)
```

Прямые выражения вызова: `any`, `emitter.is_alive`.

Выражения возврата (ветви, без исполнения):

- `any((emitter.watch == watch and emitter.is_alive() for emitter in self.observer.emitters))`


<a id="symbol-foldertrackingservice--run"></a>

## `FolderTrackingService._run`

[media_manager/folder_tracking.py:73](../../media_manager/folder_tracking.py#L73)

Периодически обновляет наблюдатели и обрабатывает накопленные события. Обрабатывает ошибки: Exception.

```python
def _run(self)
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._wake.clear`, `self._wake.wait`, [self.reconcile](../../media_manager/folder_tracking.py#L103).

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice--remove"></a>

## `FolderTrackingService._remove`

[media_manager/folder_tracking.py:84](../../media_manager/folder_tracking.py#L84)

Останавливает и удаляет наблюдатель одного набора папок. Использует current['handler'].cancel, self._watches.pop, self.observer.unschedule.

```python
def _remove(self, group_id)
```

Прямые выражения вызова: `current['handler'].cancel`, `self._watches.pop`, `self.observer.unschedule`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice--changed"></a>

## `FolderTrackingService._changed`

[media_manager/folder_tracking.py:92](../../media_manager/folder_tracking.py#L92)

Записывает изменение основной папки и сбрасывает локальный сигнал обработчика. Обрабатывает ошибки: Exception.

```python
def _changed(self, group_id, handler)
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._watches.get`, `self.copies.mark_changed`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice-reconcile"></a>

## `FolderTrackingService.reconcile`

[media_manager/folder_tracking.py:103](../../media_manager/folder_tracking.py#L103)

Сопоставляет настройки наборов с доступностью томов и существующими наблюдателями. Обрабатывает ошибки: (OSError, ValueError), OSError.

```python
def reconcile(self)
```

Прямые выражения вызова: [FolderChangeHandler](../../media_manager/folder_tracking.py#L18), `Path`, `dict`, `g.get`, `open_readonly`, `os.fstat`, [self._alive](../../media_manager/folder_tracking.py#L68), [self._remove](../../media_manager/folder_tracking.py#L84), `self._states.pop`, `self._stop.is_set`, `self._watches.get`, `self.copies.groups`, `self.copies.storage._mounted.copy`, `self.observer.schedule`, `set`, `str`, `volumes.get`.

Перехватываемые типы: `(OSError, ValueError)`, `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-foldertrackingservice-close"></a>

## `FolderTrackingService.close`

[media_manager/folder_tracking.py:144](../../media_manager/folder_tracking.py#L144)

Останавливает фоновое согласование и все наблюдатели папок. Использует current['handler'].cancel, self._stop.set, self._thread.join, self._wake.set, self._watches.values.

```python
def close(self)
```

Прямые выражения вызова: `current['handler'].cancel`, `self._stop.set`, `self._thread.join`, `self._wake.set`, `self._watches.values`, `self.observer.join`, `self.observer.stop`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
