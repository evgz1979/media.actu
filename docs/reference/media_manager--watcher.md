# Повторное сканирование источников: `media_manager/watcher.py`

Watchdog-наблюдатели старой модели обычных источников. Объединяет частые события таймером и вызывает полный перескан источника.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/watcher.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [app.py](app.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [DebouncedHandler](#symbol-DebouncedHandler) — Объединяет события файловой системы перед повторной сверкой источника.
- [DebouncedHandler.__init__](#symbol-DebouncedHandler.__init__) — Инициализирует DebouncedHandler и его рабочее состояние.
- [DebouncedHandler.cancel](#symbol-DebouncedHandler.cancel) — Отменяет ожидающий вызов обработчика изменений.
- [DebouncedHandler.on_any_event](#symbol-DebouncedHandler.on_any_event) — Перезапускает таймер после значимого изменения файла или папки.
- [SourceWatcher](#symbol-SourceWatcher) — Управляет Watchdog-наблюдателями обычных зарегистрированных источников.
- [SourceWatcher.__init__](#symbol-SourceWatcher.__init__) — Инициализирует SourceWatcher и его рабочее состояние.
- [SourceWatcher.start](#symbol-SourceWatcher.start) — Запускает общий наблюдатель файловой системы.
- [SourceWatcher.stop](#symbol-SourceWatcher.stop) — Снимает наблюдение всех источников и завершает поток Watchdog.
- [SourceWatcher.unwatch](#symbol-SourceWatcher.unwatch) — Отменяет наблюдение и ожидающий таймер выбранного источника.
- [SourceWatcher.watch](#symbol-SourceWatcher.watch) — Устанавливает рекурсивное наблюдение источника с отложенным пересканированием.

<a id="symbol-DebouncedHandler"></a>

## `DebouncedHandler`

[media_manager/watcher.py](../../media_manager/watcher.py) · `DebouncedHandler`

Объединяет события файловой системы перед повторной сверкой источника. Зависимости конструктора: callback, delay.

Базовые классы: `FileSystemEventHandler`.


Состояние, присваиваемое конструктором: `_lock`, `_timer`, `callback`, `delay`.

Именованные методы: `__init__`, `on_any_event`, `cancel`.

<a id="symbol-DebouncedHandler.__init__"></a>

## `DebouncedHandler.__init__`

[media_manager/watcher.py](../../media_manager/watcher.py) · `DebouncedHandler.__init__`

Инициализирует DebouncedHandler и его рабочее состояние. Обновляет состояние объекта: _lock, _timer, callback, delay.

```python
def __init__(self, callback: Callable[[], None], delay: float=1.5) -> None
```

Присваивания полям `self`: `_lock`, `_timer`, `callback`, `delay`.

Прямые выражения вызова: `threading.Lock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-DebouncedHandler.cancel"></a>

## `DebouncedHandler.cancel`

[media_manager/watcher.py](../../media_manager/watcher.py) · `DebouncedHandler.cancel`

Отменяет ожидающий вызов обработчика изменений. Обновляет состояние объекта: _timer.

```python
def cancel(self) -> None
```

Присваивания полям `self`: `_timer`.

Прямые выражения вызова: `self._timer.cancel`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-DebouncedHandler.on_any_event"></a>

## `DebouncedHandler.on_any_event`

[media_manager/watcher.py](../../media_manager/watcher.py) · `DebouncedHandler.on_any_event`

Перезапускает таймер после значимого изменения файла или папки. Обновляет состояние объекта: _timer.

```python
def on_any_event(self, event: FileSystemEvent) -> None
```

Присваивания полям `self`: `_timer`.

Прямые выражения вызова: `self._timer.cancel`, `self._timer.start`, `threading.Timer`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-SourceWatcher"></a>

## `SourceWatcher`

[media_manager/watcher.py](../../media_manager/watcher.py) · `SourceWatcher`

Управляет Watchdog-наблюдателями обычных зарегистрированных источников. Зависимости конструктора: on_change.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_started`, `handlers`, `observer`, `on_change`, `watches`.

Именованные методы: `__init__`, `start`, `watch`, `unwatch`, `stop`.

<a id="symbol-SourceWatcher.__init__"></a>

## `SourceWatcher.__init__`

[media_manager/watcher.py](../../media_manager/watcher.py) · `SourceWatcher.__init__`

Инициализирует SourceWatcher и его рабочее состояние. Обновляет состояние объекта: _started, handlers, observer, on_change, watches.

```python
def __init__(self, on_change: Callable[[int], None]) -> None
```

Присваивания полям `self`: `_started`, `handlers`, `observer`, `on_change`, `watches`.

Прямые выражения вызова: `Observer`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SourceWatcher.start"></a>

## `SourceWatcher.start`

[media_manager/watcher.py](../../media_manager/watcher.py) · `SourceWatcher.start`

Запускает общий наблюдатель файловой системы. Обновляет состояние объекта: _started.

```python
def start(self) -> None
```

Присваивания полям `self`: `_started`.

Прямые выражения вызова: `self.observer.start`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SourceWatcher.stop"></a>

## `SourceWatcher.stop`

[media_manager/watcher.py](../../media_manager/watcher.py) · `SourceWatcher.stop`

Снимает наблюдение всех источников и завершает поток Watchdog. Обновляет состояние объекта: _started.

```python
def stop(self) -> None
```

Присваивания полям `self`: `_started`.

Прямые выражения вызова: `handler.cancel`, `self.handlers.clear`, `self.handlers.values`, `self.observer.join`, `self.observer.stop`, `self.watches.clear`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SourceWatcher.unwatch"></a>

## `SourceWatcher.unwatch`

[media_manager/watcher.py](../../media_manager/watcher.py) · `SourceWatcher.unwatch`

Отменяет наблюдение и ожидающий таймер выбранного источника. Использует handler.cancel, self.handlers.pop, self.observer.unschedule, self.watches.pop.

```python
def unwatch(self, source_id: int) -> None
```

Прямые выражения вызова: `handler.cancel`, `self.handlers.pop`, `self.observer.unschedule`, `self.watches.pop`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-SourceWatcher.watch"></a>

## `SourceWatcher.watch`

[media_manager/watcher.py](../../media_manager/watcher.py) · `SourceWatcher.watch`

Устанавливает рекурсивное наблюдение источника с отложенным пересканированием. Использует DebouncedHandler, self.observer.schedule.

```python
def watch(self, source_id: int, path: str | Path) -> None
```

Прямые выражения вызова: [DebouncedHandler](media_manager--watcher.md#symbol-DebouncedHandler), `self.observer.schedule`, `str`.

Выражения возврата (ветви, без исполнения):

- `None`
