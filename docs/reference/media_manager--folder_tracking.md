# Отслеживание основных папок: `media_manager/folder_tracking.py`

Наблюдатели Watchdog для подключённых основных папок. Сохраняет сигнал изменения, а не актуальный индекс или доказательство расхождения копий.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/folder_tracking.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/volume_identity.py](media_manager--volume_identity.md), [media_manager/watcher.py](media_manager--watcher.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_folder_tracking.py](tests.md#module-tests.test_folder_tracking).

## Оглавление определений

- [FolderChangeHandler](#symbol-FolderChangeHandler) — Фильтрует события Watchdog для зарегистрированной основной папки.
- [FolderChangeHandler.on_any_event](#symbol-FolderChangeHandler.on_any_event) — Отмечает значимое изменение, исключая служебные файлы и события чтения.
- [FolderTrackingService](#symbol-FolderTrackingService) — Поддерживает наблюдатели подключённых основных папок с включённым отслеживанием.
- [FolderTrackingService.__init__](#symbol-FolderTrackingService.__init__) — Инициализирует FolderTrackingService и его рабочее состояние.
- [FolderTrackingService._alive](#symbol-FolderTrackingService._alive) — Проверяет работоспособность потока установленного наблюдателя.
- [FolderTrackingService._changed](#symbol-FolderTrackingService._changed) — Записывает изменение основной папки и сбрасывает локальный сигнал обработчика.
- [FolderTrackingService._remove](#symbol-FolderTrackingService._remove) — Останавливает и удаляет наблюдатель одного набора папок.
- [FolderTrackingService._run](#symbol-FolderTrackingService._run) — Периодически обновляет наблюдатели и обрабатывает накопленные события.
- [FolderTrackingService.close](#symbol-FolderTrackingService.close) — Останавливает фоновое согласование и все наблюдатели папок.
- [FolderTrackingService.reconcile](#symbol-FolderTrackingService.reconcile) — Сопоставляет настройки наборов с доступностью томов и существующими наблюдателями.
- [FolderTrackingService.start](#symbol-FolderTrackingService.start) — Запускает фоновое согласование наблюдателей папок.
- [FolderTrackingService.status](#symbol-FolderTrackingService.status) — Возвращает состояние наблюдателя выбранной основной папки.
- [FolderTrackingService.wake](#symbol-FolderTrackingService.wake) — Пробуждает согласование после изменения настроек или подключения.

<a id="symbol-FolderChangeHandler"></a>

## `FolderChangeHandler`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderChangeHandler`

Фильтрует события Watchdog для зарегистрированной основной папки. Базовые типы: DebouncedHandler.

Базовые классы: `DebouncedHandler`.


Именованные методы: `on_any_event`.

<a id="symbol-FolderChangeHandler.on_any_event"></a>

## `FolderChangeHandler.on_any_event`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderChangeHandler.on_any_event`

Отмечает значимое изменение, исключая служебные файлы и события чтения. Использует Path, all, service_file, super, super().on_any_event.

```python
def on_any_event(self, event)
```

Прямые выражения вызова: `Path`, `all`, `getattr`, `service_file`, `super`, `super().on_any_event`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-FolderTrackingService"></a>

## `FolderTrackingService`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService`

Поддерживает наблюдатели подключённых основных папок с включённым отслеживанием. Зависимости конструктора: copies.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_lock`, `_states`, `_stop`, `_thread`, `_wake`, `_watches`, `copies`, `observer`.

Именованные методы: `__init__`, `start`, `wake`, `status`, `_alive`, `_run`, `_remove`, `_changed`, `reconcile`, `close`.

<a id="symbol-FolderTrackingService.__init__"></a>

## `FolderTrackingService.__init__`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService.__init__`

Инициализирует FolderTrackingService и его рабочее состояние. Обновляет состояние объекта: _lock, _states, _stop, _thread, _wake, _watches, copies, observer.

```python
def __init__(self, copies)
```

Присваивания полям `self`: `_lock`, `_states`, `_stop`, `_thread`, `_wake`, `_watches`, `copies`, `observer`.

Прямые выражения вызова: `Observer`, `threading.Event`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService._alive"></a>

## `FolderTrackingService._alive`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService._alive`

Проверяет работоспособность потока установленного наблюдателя. Использует any, emitter.is_alive.

```python
def _alive(self, watch)
```

Прямые выражения вызова: `any`, `emitter.is_alive`.

Выражения возврата (ветви, без исполнения):

- `any((emitter.watch == watch and emitter.is_alive() for emitter in self.observer.emitters))`


<a id="symbol-FolderTrackingService._changed"></a>

## `FolderTrackingService._changed`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService._changed`

Записывает изменение основной папки и сбрасывает локальный сигнал обработчика. Обрабатывает ошибки: Exception.

```python
def _changed(self, group_id, handler)
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._watches.get`, `self.copies.mark_changed`.

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService._remove"></a>

## `FolderTrackingService._remove`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService._remove`

Останавливает и удаляет наблюдатель одного набора папок. Использует current['handler'].cancel, self._watches.pop, self.observer.unschedule.

```python
def _remove(self, group_id)
```

Прямые выражения вызова: `current['handler'].cancel`, `self._watches.pop`, `self.observer.unschedule`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService._run"></a>

## `FolderTrackingService._run`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService._run`

Периодически обновляет наблюдатели и обрабатывает накопленные события. Обрабатывает ошибки: Exception.

```python
def _run(self)
```

Прямые выражения вызова: `logging.exception`, `self._stop.is_set`, `self._wake.clear`, `self._wake.wait`, [self.reconcile](media_manager--folder_tracking.md#symbol-FolderTrackingService.reconcile).

Перехватываемые типы: `Exception`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService.close"></a>

## `FolderTrackingService.close`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService.close`

Останавливает фоновое согласование и все наблюдатели папок. Использует current['handler'].cancel, self._stop.set, self._thread.join, self._wake.set, self._watches.values.

```python
def close(self)
```

Прямые выражения вызова: `current['handler'].cancel`, `self._stop.set`, `self._thread.join`, `self._wake.set`, `self._watches.values`, `self.observer.join`, `self.observer.stop`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService.reconcile"></a>

## `FolderTrackingService.reconcile`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService.reconcile`

Сопоставляет настройки наборов с доступностью томов и существующими наблюдателями. Обрабатывает ошибки: (OSError, ValueError), OSError.

```python
def reconcile(self)
```

Прямые выражения вызова: [FolderChangeHandler](media_manager--folder_tracking.md#symbol-FolderChangeHandler), `Path`, `dict`, `g.get`, `open_readonly`, `os.fstat`, [self._alive](media_manager--folder_tracking.md#symbol-FolderTrackingService._alive), [self._remove](media_manager--folder_tracking.md#symbol-FolderTrackingService._remove), `self._states.pop`, `self._stop.is_set`, `self._watches.get`, `self.copies.groups`, `self.copies.storage._mounted.copy`, `self.observer.schedule`, `set`, `str`, `volumes.get`.

Перехватываемые типы: `(OSError, ValueError)`, `OSError`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService.start"></a>

## `FolderTrackingService.start`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService.start`

Запускает фоновое согласование наблюдателей папок. Обновляет состояние объекта: _thread.

```python
def start(self)
```

Присваивания полям `self`: `_thread`.

Прямые выражения вызова: `self._thread.start`, `self.observer.start`, `threading.Thread`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-FolderTrackingService.status"></a>

## `FolderTrackingService.status`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService.status`

Возвращает состояние наблюдателя выбранной основной папки. Поля результата: tracking_state, tracking_error.

```python
def status(self, group_id)
```

Прямые выражения вызова: `dict`, [self._alive](media_manager--folder_tracking.md#symbol-FolderTrackingService._alive), `self._states.get`, `self._watches.get`.

Выражения возврата (ветви, без исполнения):

- `dict(tracking_state='error', tracking_error='Наблюдатель файловой системы остановлен')`
- `dict(self._states.get(group_id, dict(tracking_state='starting', tracking_error=None)))`


<a id="symbol-FolderTrackingService.wake"></a>

## `FolderTrackingService.wake`

[media_manager/folder_tracking.py](../../media_manager/folder_tracking.py) · `FolderTrackingService.wake`

Пробуждает согласование после изменения настроек или подключения. Использует self._wake.set.

```python
def wake(self)
```

Прямые выражения вызова: `self._wake.set`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
