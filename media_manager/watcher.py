from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


#: Объединяет события файловой системы перед повторной сверкой источника.
#: Зависимости конструктора: callback, delay.
class DebouncedHandler(FileSystemEventHandler):
    #: Инициализирует DebouncedHandler и его рабочее состояние.
    #: Обновляет состояние объекта: _lock, _timer, callback, delay.
    def __init__(self, callback: Callable[[], None], delay: float = 1.5) -> None:
        self.callback = callback
        self.delay = delay
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    #: Перезапускает таймер после значимого изменения файла или папки.
    #: Обновляет состояние объекта: _timer.
    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory and event.event_type == "opened":
            return
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.delay, self.callback)
            self._timer.daemon = True
            self._timer.start()

    #: Отменяет ожидающий вызов обработчика изменений.
    #: Обновляет состояние объекта: _timer.
    def cancel(self) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None


#: Управляет Watchdog-наблюдателями обычных зарегистрированных источников.
#: Зависимости конструктора: on_change.
class SourceWatcher:
    #: Инициализирует SourceWatcher и его рабочее состояние.
    #: Обновляет состояние объекта: _started, handlers, observer, on_change, watches.
    def __init__(self, on_change: Callable[[int], None]) -> None:
        self.on_change = on_change
        self.observer = Observer()
        self.handlers: dict[int, DebouncedHandler] = {}
        self.watches: dict[int, object] = {}
        self._started = False

    #: Запускает общий наблюдатель файловой системы.
    #: Обновляет состояние объекта: _started.
    def start(self) -> None:
        if not self._started:
            self.observer.start()
            self._started = True

    #: Устанавливает рекурсивное наблюдение источника с отложенным пересканированием.
    #: Использует DebouncedHandler, self.observer.schedule.
    def watch(self, source_id: int, path: str | Path) -> None:
        if source_id in self.handlers:
            return
        handler = DebouncedHandler(lambda: self.on_change(source_id))
        watch = self.observer.schedule(handler, str(path), recursive=True)
        self.handlers[source_id] = handler
        self.watches[source_id] = watch

    #: Отменяет наблюдение и ожидающий таймер выбранного источника.
    #: Использует handler.cancel, self.handlers.pop, self.observer.unschedule, self.watches.pop.
    def unwatch(self, source_id: int) -> None:
        handler = self.handlers.pop(source_id, None)
        watch = self.watches.pop(source_id, None)
        if handler:
            handler.cancel()
        if watch and self._started:
            self.observer.unschedule(watch)

    #: Снимает наблюдение всех источников и завершает поток Watchdog.
    #: Обновляет состояние объекта: _started.
    def stop(self) -> None:
        for handler in self.handlers.values():
            handler.cancel()
        self.handlers.clear()
        self.watches.clear()
        if self._started:
            self.observer.stop()
            self.observer.join(timeout=5)
            self._started = False
