# Повторное сканирование источников: `media_manager/watcher.py`

Watchdog-наблюдатели старой модели обычных источников. Объединяет частые события таймером и вызывает полный перескан источника.

[Исходный модуль](../../media_manager/watcher.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [app.py](app.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md).
Тестовые модули с прямым импортом: нет; возможна косвенная проверка через вызывающие компоненты.

## Оглавление определений

- [DebouncedHandler](#symbol-debouncedhandler) — Объединяет события файловой системы перед повторной сверкой источника.
- [DebouncedHandler.__init__](#symbol-debouncedhandler---init--) — Инициализирует DebouncedHandler и его рабочее состояние.
- [DebouncedHandler.on_any_event](#symbol-debouncedhandler-on-any-event) — Перезапускает таймер после значимого изменения файла или папки.
- [DebouncedHandler.cancel](#symbol-debouncedhandler-cancel) — Отменяет ожидающий вызов обработчика изменений.
- [SourceWatcher](#symbol-sourcewatcher) — Управляет Watchdog-наблюдателями обычных зарегистрированных источников.
- [SourceWatcher.__init__](#symbol-sourcewatcher---init--) — Инициализирует SourceWatcher и его рабочее состояние.
- [SourceWatcher.start](#symbol-sourcewatcher-start) — Запускает общий наблюдатель файловой системы.
- [SourceWatcher.watch](#symbol-sourcewatcher-watch) — Устанавливает рекурсивное наблюдение источника с отложенным пересканированием.
- [SourceWatcher.unwatch](#symbol-sourcewatcher-unwatch) — Отменяет наблюдение и ожидающий таймер выбранного источника.
- [SourceWatcher.stop](#symbol-sourcewatcher-stop) — Снимает наблюдение всех источников и завершает поток Watchdog.

<a id="symbol-debouncedhandler"></a>

## `DebouncedHandler`

[media_manager/watcher.py:13](../../media_manager/watcher.py#L13)

Объединяет события файловой системы перед повторной сверкой источника. Зависимости конструктора: callback, delay.

Базовые классы: `FileSystemEventHandler`.


Состояние, присваиваемое конструктором: `_lock`, `_timer`, `callback`, `delay`.

Именованные методы: `__init__`, `on_any_event`, `cancel`.

<a id="symbol-debouncedhandler---init--"></a>

## `DebouncedHandler.__init__`

[media_manager/watcher.py:16](../../media_manager/watcher.py#L16)

Инициализирует DebouncedHandler и его рабочее состояние. Обновляет состояние объекта: _lock, _timer, callback, delay.

```python
def __init__(self, callback: Callable[[], None], delay: float=1.5) -> None
```

Присваивания полям `self`: `_lock`, `_timer`, `callback`, `delay`.

Прямые выражения вызова: `threading.Lock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-debouncedhandler-on-any-event"></a>

## `DebouncedHandler.on_any_event`

[media_manager/watcher.py:24](../../media_manager/watcher.py#L24)

Перезапускает таймер после значимого изменения файла или папки. Обновляет состояние объекта: _timer.

```python
def on_any_event(self, event: FileSystemEvent) -> None
```

Присваивания полям `self`: `_timer`.

Прямые выражения вызова: `self._timer.cancel`, `self._timer.start`, `threading.Timer`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-debouncedhandler-cancel"></a>

## `DebouncedHandler.cancel`

[media_manager/watcher.py:36](../../media_manager/watcher.py#L36)

Отменяет ожидающий вызов обработчика изменений. Обновляет состояние объекта: _timer.

```python
def cancel(self) -> None
```

Присваивания полям `self`: `_timer`.

Прямые выражения вызова: `self._timer.cancel`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sourcewatcher"></a>

## `SourceWatcher`

[media_manager/watcher.py:45](../../media_manager/watcher.py#L45)

Управляет Watchdog-наблюдателями обычных зарегистрированных источников. Зависимости конструктора: on_change.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_started`, `handlers`, `observer`, `on_change`, `watches`.

Именованные методы: `__init__`, `start`, `watch`, `unwatch`, `stop`.

<a id="symbol-sourcewatcher---init--"></a>

## `SourceWatcher.__init__`

[media_manager/watcher.py:48](../../media_manager/watcher.py#L48)

Инициализирует SourceWatcher и его рабочее состояние. Обновляет состояние объекта: _started, handlers, observer, on_change, watches.

```python
def __init__(self, on_change: Callable[[int], None]) -> None
```

Присваивания полям `self`: `_started`, `handlers`, `observer`, `on_change`, `watches`.

Прямые выражения вызова: `Observer`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sourcewatcher-start"></a>

## `SourceWatcher.start`

[media_manager/watcher.py:57](../../media_manager/watcher.py#L57)

Запускает общий наблюдатель файловой системы. Обновляет состояние объекта: _started.

```python
def start(self) -> None
```

Присваивания полям `self`: `_started`.

Прямые выражения вызова: `self.observer.start`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sourcewatcher-watch"></a>

## `SourceWatcher.watch`

[media_manager/watcher.py:64](../../media_manager/watcher.py#L64)

Устанавливает рекурсивное наблюдение источника с отложенным пересканированием. Использует DebouncedHandler, self.observer.schedule.

```python
def watch(self, source_id: int, path: str | Path) -> None
```

Прямые выражения вызова: [DebouncedHandler](../../media_manager/watcher.py#L13), `self.observer.schedule`, `str`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-sourcewatcher-unwatch"></a>

## `SourceWatcher.unwatch`

[media_manager/watcher.py:74](../../media_manager/watcher.py#L74)

Отменяет наблюдение и ожидающий таймер выбранного источника. Использует handler.cancel, self.handlers.pop, self.observer.unschedule, self.watches.pop.

```python
def unwatch(self, source_id: int) -> None
```

Прямые выражения вызова: `handler.cancel`, `self.handlers.pop`, `self.observer.unschedule`, `self.watches.pop`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-sourcewatcher-stop"></a>

## `SourceWatcher.stop`

[media_manager/watcher.py:84](../../media_manager/watcher.py#L84)

Снимает наблюдение всех источников и завершает поток Watchdog. Обновляет состояние объекта: _started.

```python
def stop(self) -> None
```

Присваивания полям `self`: `_started`.

Прямые выражения вызова: `handler.cancel`, `self.handlers.clear`, `self.handlers.values`, `self.observer.join`, `self.observer.stop`, `self.watches.clear`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
