"""Persistent per-library sync windows; no disk scans are run by this timer."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import threading
from zoneinfo import ZoneInfo


RUNNING = {'manifest', 'inventory', 'saving', 'pausing'}
DEFAULT = dict(night_only=False, start_hour=0, end_hour=7, timezone='Europe/Moscow')


#: Определяет, попадает ли момент в разрешённые часы выбранной временной зоны.
#: Использует ZoneInfo, instant.astimezone.
def in_window(settings, instant):
    if not settings['night_only']:
        return True
    hour = instant.astimezone(ZoneInfo(settings['timezone'])).hour
    start, end = settings['start_hour'], settings['end_hour']
    return start <= hour < end if start < end else hour >= start or hour < end


#: Возвращает дату начала текущего окна, включая переход через полночь.
#: Использует ZoneInfo, instant.astimezone, local.date, local.date().isoformat, timedelta.
def window_key(settings, instant):
    local = instant.astimezone(ZoneInfo(settings['timezone']))
    if settings['start_hour'] > settings['end_hour'] and local.hour < settings['end_hour']:
        local -= timedelta(days=1)
    return local.date().isoformat()


#: Координирует сохранённые запросы Photos и разрешённые временные окна.
#: Зависимости конструктора: libraries, originals.
class PhotosSyncSchedule:
    #: Инициализирует PhotosSyncSchedule и его рабочее состояние.
    #: Изменяет SQLite-таблицы: photos_sync_requests, photos_sync_settings.
    def __init__(self, libraries, originals, *, clock=None):
        self.libraries, self.originals, self.catalog = libraries, originals, libraries.catalog
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self._lock, self._tick_lock = threading.RLock(), threading.Lock()
        self._stop, self._wake = threading.Event(), threading.Event()
        self._thread = None
        with self.catalog._write_lock, self._db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS photos_sync_settings (
                    source_id INTEGER PRIMARY KEY REFERENCES photos_libraries(source_id) ON DELETE CASCADE,
                    night_only INTEGER NOT NULL, start_hour INTEGER NOT NULL,
                    end_hour INTEGER NOT NULL, timezone TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS photos_sync_requests (
                    link_id TEXT PRIMARY KEY REFERENCES photos_copy_links(id) ON DELETE CASCADE,
                    enabled INTEGER NOT NULL DEFAULT 1, last_window TEXT,
                    seen_result TEXT, retry_after REAL NOT NULL DEFAULT 0,
                    error TEXT NOT NULL DEFAULT '');
            ''')
            self._settings = {r['source_id']: dict(r, night_only=bool(r['night_only']))
                              for r in db.execute('SELECT * FROM photos_sync_settings')}
        libraries.schedule = self
        originals.schedule = self
        self.catalog.photos_schedule = self

    #: Предоставляет транзакционное соединение каталога с гарантированным закрытием.
    #: Использует db.close, self.catalog.connect.
    @contextmanager
    def _db(self):
        db = self.catalog.connect()
        try:
            with db:
                yield db
        finally:
            db.close()

    #: Возвращает настройки окна медиатеки либо безопасные значения по умолчанию.
    #: Использует self._settings.get.
    def settings(self, source_id):
        with self._lock:
            return dict(self._settings.get(source_id, dict(DEFAULT, source_id=source_id)))

    #: Проверяет, запрещает ли текущее время работу выбранной медиатеки.
    #: Использует in_window, self.clock, self.settings.
    def blocked(self, source_id):
        return not in_window(self.settings(source_id), self.clock())

    #: Дополняет настройки окна текущей блокировкой и подписью времени МСК.
    #: Поля результата: blocked, window.
    def describe(self, source_id):
        settings = self.settings(source_id)
        return dict(settings, blocked=self.blocked(source_id),
                    window=f"{settings['start_hour']:02d}:00–{settings['end_hour']:02d}:00 МСК")

    #: Сохраняет проверенные часы работы и согласует уже запущенные задания.
    #: Изменяет SQLite-таблицы: photos_sync_settings.
    def configure(self, source_id, night_only, start_hour=0, end_hour=7, timezone='Europe/Moscow'):
        self.libraries.profile(source_id)
        if (type(night_only) is not bool or type(start_hour) is not int or type(end_hour) is not int
                or not 0 <= start_hour <= 23 or not 0 <= end_hour <= 23 or start_hour == end_hour
                or timezone != 'Europe/Moscow'):
            raise ValueError('Задай разные часы начала и окончания от 00 до 23 по Москве')
        previous = self.settings(source_id)
        settings = dict(source_id=source_id, night_only=night_only, start_hour=start_hour,
                        end_hour=end_hour, timezone=timezone)
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR REPLACE INTO photos_sync_settings VALUES (?,?,?,?,?)',
                       (source_id, int(night_only), start_hour, end_hour, timezone))
            links = [r[0] for r in db.execute('SELECT id FROM photos_copy_links WHERE source_id=? AND connected=1', (source_id,))]
        with self._lock:
            self._settings[source_id] = settings
        if night_only and not previous['night_only']:
            # A configured night window continues work that the user had already
            # started. Merely binding a new destination still starts no download.
            for link_id in links:
                job = self.originals.summary(link_id, raw=True)
                if job.get('id') and (self._request(link_id) is None or job['state'] in RUNNING):
                    self._arm(link_id)
        if self.blocked(source_id):
            self._pause_outside_window()
        self._wake.set()
        return self.describe(source_id)

    #: Читает постоянный запрос автоматического сохранения одной копии.
    #: Читает SQLite-таблицы: photos_sync_requests.
    def _request(self, link_id):
        with self._db() as db:
            row = db.execute('SELECT * FROM photos_sync_requests WHERE link_id=?', (link_id,)).fetchone()
        return dict(row) if row else None

    #: Проверяет наличие включённого запроса расписания для копии.
    #: Использует self._request.
    def manages(self, link_id):
        row = self._request(link_id)
        return bool(row and row['enabled'])

    #: Включает запрос корневой копии и сбрасывает ожидание повторного запуска.
    #: Изменяет SQLite-таблицы: photos_sync_requests.
    def _arm(self, link_id):
        link_id = self.libraries.root_copy(link_id)
        with self.catalog._write_lock, self._db() as db:
            db.execute('''INSERT INTO photos_sync_requests(link_id) VALUES (?)
                ON CONFLICT(link_id) DO UPDATE SET enabled=1,last_window=NULL,seen_result=NULL,retry_after=0,error='' ''', (link_id,))

    #: Регистрирует ручной запрос работы через расписание и проверяет немедленный запуск.
    #: Изменяет SQLite-таблицы: photos_sync_requests.
    def request(self, link_id, source_id=None):
        self.originals._link(link_id, source_id)
        link_id = self.libraries.root_copy(link_id)
        self._arm(link_id)
        job = self.originals.summary(link_id, raw=True)
        with self.catalog._write_lock, self._db() as db:
            db.execute('UPDATE photos_sync_requests SET seen_result=? WHERE link_id=?', (job.get('updated_at'), link_id))
        self.tick()
        self._wake.set()
        return self.originals.summary(link_id)

    #: Отключает сохранённый запрос автоматической работы корневой копии.
    #: Изменяет SQLite-таблицы: photos_sync_requests.
    def cancel(self, link_id):
        link_id = self.libraries.root_copy(link_id)
        with self.catalog._write_lock, self._db() as db:
            db.execute('UPDATE photos_sync_requests SET enabled=0 WHERE link_id=?', (link_id,))

    #: Добавляет к состоянию задания ожидание окна и ошибку расписания.
    #: Поля результата: scheduled.
    def decorate(self, link_id, job):
        request = self._request(link_id)
        if not request or not request['enabled']:
            return dict(job, scheduled=False)
        with self._db() as db:
            row = db.execute('SELECT source_id FROM photos_copy_links WHERE id=?', (link_id,)).fetchone()
        if not row:
            return job
        blocked = self.blocked(row['source_id'])
        result = dict(job, scheduled=True, schedule_error=request['error'])
        if job['state'] not in RUNNING:
            if blocked:
                result.update(state='scheduled', original_state=job['state'],
                              message='Ожидает ночного окна · ' + self.describe(row['source_id'])['window'])
            elif job['state'] in ('idle', 'paused'):
                result.update(state='scheduled', original_state=job['state'], message='В очереди на сохранение оригиналов')
            if request['error'] and not blocked:
                result['message'] = request['error']
        return result

    #: Запрашивает паузу активных оригиналов вне разрешённых часов.
    #: Читает SQLite-таблицы: photos_copy_links, photos_original_jobs.
    def _pause_outside_window(self):
        with self._db() as db:
            rows = list(db.execute('''SELECT j.link_id,l.source_id FROM photos_original_jobs j
                JOIN photos_copy_links l ON l.id=j.link_id
                WHERE j.state IN ('manifest','inventory','saving')'''))
        for row in rows:
            if self.blocked(row['source_id']):
                self._arm_if_missing(row['link_id'])
                self.originals.pause(row['link_id'], _scheduled=True)

    #: Сохраняет отсутствующий запрос для продолжения в следующем окне.
    #: Изменяет SQLite-таблицы: photos_sync_requests.
    def _arm_if_missing(self, link_id):
        link_id = self.libraries.root_copy(link_id)
        with self.catalog._write_lock, self._db() as db:
            db.execute('INSERT OR IGNORE INTO photos_sync_requests(link_id) VALUES (?)', (link_id,))

    #: Выбирает один допустимый корневой запрос и запускает сохранение оригиналов.
    #: Изменяет SQLite-таблицы: photos_sync_requests.
    def tick(self):
        if not self._tick_lock.acquire(blocking=False):
            return
        try:
            self._pause_outside_window()
            with self._db() as db:
                if db.execute("SELECT 1 FROM photos_original_jobs WHERE state IN ('manifest','inventory','saving','pausing')").fetchone():
                    return
                requests = [dict(r) for r in db.execute('''SELECT r.*,l.source_id,l.connected
                    FROM photos_sync_requests r JOIN photos_copy_links l ON l.id=r.link_id
                    WHERE r.enabled=1 ORDER BY r.link_id''')]
            instant = self.clock()
            for request in requests:
                source_id, link_id = request['source_id'], request['link_id']
                if self.libraries.copy_source(link_id):
                    continue  # Descendants are copied by their root's worker.
                profile = self.libraries.profile(source_id)
                if not request['connected'] or not profile['active'] or profile['state'] != 'ready' or self.blocked(source_id):
                    continue
                if request['retry_after'] > instant.timestamp():
                    continue
                job = self.originals.summary(link_id, raw=True)
                settings = self.settings(source_id)
                current_window = window_key(settings, instant)
                if job['state'] in ('completed', 'completed_with_errors'):
                    if not settings['night_only']:
                        self.cancel(link_id)
                        continue
                    if request['last_window'] == current_window:
                        continue
                if job['state'] in ('waiting', 'failed') and job.get('updated_at') != request['seen_result']:
                    with self.catalog._write_lock, self._db() as db:
                        db.execute('UPDATE photos_sync_requests SET retry_after=?,seen_result=?,error=? WHERE link_id=?',
                                   (instant.timestamp() + 300, job.get('updated_at'), job.get('message', ''), link_id))
                    continue
                try:
                    self.originals.start(link_id, source_id, _scheduled=True)
                except (ValueError, OSError, RuntimeError, KeyError) as error:
                    with self.catalog._write_lock, self._db() as db:
                        db.execute('UPDATE photos_sync_requests SET retry_after=?,error=? WHERE link_id=?',
                                   (instant.timestamp() + 300, str(error), link_id))
                    continue
                with self.catalog._write_lock, self._db() as db:
                    db.execute("UPDATE photos_sync_requests SET last_window=?,retry_after=0,error='' WHERE link_id=?", (current_window, link_id))
                break
        finally:
            self._tick_lock.release()

    #: Запускает фоновый таймер проверки расписания.
    #: Обновляет состояние объекта: _thread.
    def start(self):
        if self._thread:
            return
        self._stop.clear()
        #: Проверяет расписание каждые 15 секунд и сохраняет работоспособность при ошибках.
        #: Обрабатывает ошибки: Exception.
        def run():
            while not self._stop.is_set():
                try:
                    self.tick()
                except Exception:
                    # Keep the timer alive across unavailable volumes/accounts.
                    import logging
                    logging.exception('Photos night schedule failed')
                self._wake.wait(15)
                self._wake.clear()
        self._thread = threading.Thread(target=run, name='photos-sync-schedule', daemon=True)
        self._thread.start()

    #: Останавливает таймер расписания и пробуждает ожидающий поток.
    #: Обновляет состояние объекта: _thread.
    def close(self):
        self._stop.set()
        self._wake.set()
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None
