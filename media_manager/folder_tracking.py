"""Observe opted-in main folders while Core runs; never copy or open file contents."""
from __future__ import annotations

import logging
import os
from pathlib import Path
import threading

from watchdog.observers import Observer

from .comparison import open_readonly
from .volume_identity import service_file
from .watcher import DebouncedHandler


#: Фильтрует события Watchdog для зарегистрированной основной папки.
#: Базовые типы: DebouncedHandler.
class FolderChangeHandler(DebouncedHandler):
    #: Отмечает значимое изменение, исключая служебные файлы и события чтения.
    #: Использует Path, all, service_file, super, super().on_any_event.
    def on_any_event(self, event):
        if event.event_type not in {'created', 'deleted', 'modified', 'moved'}:
            return
        paths = [event.src_path, getattr(event, 'dest_path', '')]
        if all(not path or service_file(Path(path).name) for path in paths):
            return
        super().on_any_event(event)


#: Поддерживает наблюдатели подключённых основных папок с включённым отслеживанием.
#: Зависимости конструктора: copies.
class FolderTrackingService:
    #: Инициализирует FolderTrackingService и его рабочее состояние.
    #: Обновляет состояние объекта: _lock, _states, _stop, _thread, _wake, _watches, copies, observer.
    def __init__(self, copies):
        self.copies = copies
        self.observer = Observer()
        self._lock = threading.RLock()
        self._watches = {}
        self._states = {}
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._thread = None

    #: Запускает фоновое согласование наблюдателей папок.
    #: Обновляет состояние объекта: _thread.
    def start(self):
        self.observer.start()
        self._thread = threading.Thread(target=self._run, daemon=True, name='folder-tracking')
        self._thread.start()

    #: Пробуждает согласование после изменения настроек или подключения.
    #: Использует self._wake.set.
    def wake(self):
        self._wake.set()

    #: Возвращает состояние наблюдателя выбранной основной папки.
    #: Поля результата: tracking_state, tracking_error.
    def status(self, group_id):
        with self._lock:
            current = self._watches.get(group_id)
            if current and not self._alive(current['watch']):
                return dict(tracking_state='error', tracking_error='Наблюдатель файловой системы остановлен')
            return dict(self._states.get(group_id, dict(tracking_state='starting', tracking_error=None)))

    #: Проверяет работоспособность потока установленного наблюдателя.
    #: Использует any, emitter.is_alive.
    def _alive(self, watch):
        return any(emitter.watch == watch and emitter.is_alive() for emitter in self.observer.emitters)

    #: Периодически обновляет наблюдатели и обрабатывает накопленные события.
    #: Обрабатывает ошибки: Exception.
    def _run(self):
        while not self._stop.is_set():
            self._wake.clear()
            try:
                self.reconcile()
            except Exception:
                logging.exception('Unable to refresh main-folder observers')
            self._wake.wait(30)

    #: Останавливает и удаляет наблюдатель одного набора папок.
    #: Использует current['handler'].cancel, self._watches.pop, self.observer.unschedule.
    def _remove(self, group_id):
        current = self._watches.pop(group_id, None)
        if current:
            current['handler'].cancel()
            self.observer.unschedule(current['watch'])

    #: Записывает изменение основной папки и сбрасывает локальный сигнал обработчика.
    #: Обрабатывает ошибки: Exception.
    def _changed(self, group_id, handler):
        with self._lock:
            current = self._watches.get(group_id)
            if not self._stop.is_set() and current and current['handler'] is handler:
                try:
                    self.copies.mark_changed(group_id)
                except Exception:
                    logging.exception('Unable to record a main-folder change')

    #: Сопоставляет настройки наборов с доступностью томов и существующими наблюдателями.
    #: Обрабатывает ошибки: (OSError, ValueError), OSError.
    def reconcile(self):
        groups = self.copies.groups()
        volumes = self.copies.storage._mounted.copy()
        wanted = {g['id'] for g in groups if g['tracking'] and g.get('connected', True)}
        with self._lock:
            for group_id in set(self._watches) - wanted:
                self._remove(group_id)
            for group_id in set(self._states) - wanted:
                self._states.pop(group_id)
        for group in groups:
            if self._stop.is_set() or group['id'] not in wanted:
                continue
            group_id, main = group['id'], group['main']
            volume = volumes.get(main['volume_id'])
            state, error, identity, path = 'offline', None, None, None
            if volume and main['availability'] == 'online':
                try:
                    with open_readonly(volume, main['path'], directory=True) as descriptor:
                        info = os.fstat(descriptor)
                        path = str(Path(volume['mount_path']) / main['path'])
                        identity = (path, info.st_dev, info.st_ino)
                    state = 'watching'
                except (OSError, ValueError) as problem:
                    state, error = 'error', str(problem)
            with self._lock:
                current = self._watches.get(group_id)
                if current and (current['identity'] != identity or not self._alive(current['watch'])):
                    self._remove(group_id)
                    current = None
                if identity and not current:
                    handler = FolderChangeHandler(lambda: None)
                    handler.callback = lambda g=group_id, h=handler: self._changed(g, h)
                    try:
                        watch = self.observer.schedule(handler, path, recursive=True)
                        self._watches[group_id] = dict(identity=identity, handler=handler, watch=watch)
                    except OSError as problem:
                        state, error = 'error', str(problem)
                self._states[group_id] = dict(tracking_state=state, tracking_error=error)

    #: Останавливает фоновое согласование и все наблюдатели папок.
    #: Использует current['handler'].cancel, self._stop.set, self._thread.join, self._wake.set, self._watches.values.
    def close(self):
        self._stop.set()
        self._wake.set()
        with self._lock:
            for current in self._watches.values():
                current['handler'].cancel()
        if self._thread:
            self._thread.join(timeout=1)
            self.observer.stop()
            self.observer.join(timeout=5)
