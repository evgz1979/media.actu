"""Compact sidebar for Photos and iCloud Drive sources and their copies."""
from asyncio import gather
from contextlib import contextmanager
from datetime import datetime
from pathlib import PurePosixPath
from zoneinfo import ZoneInfo

from nicegui import ui

from media_manager.icloud_copies import ICLOUD_VOLUME_ID


LIBRARY_CSS = """
.library-list { width:100%; padding:3px 5px 5px; gap:3px; }
.source-items { gap:1px; }
.source-row { width:100%; gap:3px; min-width:0; min-height:28px; border-radius:4px; padding:0 2px; }
.source-row.active { background:#eef4eb; }
.source-row.source-copy { padding-left:22px; min-height:24px; }
.source-row .q-btn { min-height:22px; padding:1px 3px; }
.source-row .source-name { flex:1; min-width:0; font-size:11px; }
.source-name .q-btn__content { width:100%; justify-content:flex-start; flex-wrap:nowrap; }
.source-name .block { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.source-readout { flex-shrink:0; max-width:40%; color:#58674f; font-size:10px; white-space:nowrap; }
.source-schedule { padding-left:27px; font-size:10px; color:#64705f; }
.library-note { font-size:10px; color:#835649; padding:2px 9px; }
"""


#: Формирует подпись прогресса превью одной медиатеки.
#: Использует f'Превью {done:,} / {total:,} · {percent}'.replace, library.get.
def progress_text(library):
    done = int(library.get('thumbnail_done') or 0)
    total = int(library.get('thumbnail_total') or 0)
    percent = f'{done / total * 100:.1f}%' if total else '0%'
    return f'Превью {done:,} / {total:,} · {percent}'.replace(',', ' ')


#: Форматирует прогресс объектов и ресурсов привязанной копии Photos.
#: Использует copy.get, f' · {done:,} / {total:,}'.replace, job.get.
def originals_text(copy):
    job = copy.get('originals') or {}
    title = (f"Из {copy.get('source_label','копии')}" if copy.get('source_link_id') else 'Оригиналы из Photos') + f" · {copy['number']:02d}-copy"
    if job.get('state', 'idle') == 'idle':
        return title + ' · не запускалось'
    total, done = job.get('total_assets', 0), job.get('done_assets', 0)
    return title + f' · {done:,} / {total:,}'.replace(',', ' ')


#: Преобразует техническое состояние сохранения оригиналов в подпись UI.
#: Использует copy.get, f"Проверка файлов: {job.get('checked_files', 0):,}".replace, job.get.
def originals_state(copy):
    job = copy.get('originals') or {}
    state = job.get('state', 'idle')
    if state == 'inventory':
        return f"Проверка файлов: {job.get('checked_files', 0):,}".replace(',', ' ')
    if state == 'saving':
        size = job.get('current_bytes', 0) / (1024 * 1024)
        origin = 'Из ' + job['current_source'] + ' · ' if job.get('current_source') and job['current_source']!='Photos' else ''
        return origin + f"{job.get('current_path', '')} · {size:.1f} МБ" + (f" · iCloud {job['fraction']:.0%}" if 0 < job.get('fraction', 0) < 1 else '')
    return job.get('message', 'Сохранение ещё не запускалось')


#: Формирует подпись настройки ночного окна медиатеки.
#: Использует library.get, schedule.get.
def schedule_text(library):
    schedule = library.get('sync_schedule') or {}
    return 'Только ночью · ' + schedule.get('window', '00:00–07:00 МСК') if schedule.get('night_only') else ''


#: Показывает точное время следующей попытки в московском часовом поясе.
#: Принимает Unix-время из журнала iCloud Drive.
def retry_time(timestamp):
    return datetime.fromtimestamp(timestamp, ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S МСК')


#: Определяет пользовательскую подпись доступности и паузы медиатеки.
#: Использует (library.get('sync_schedule') or {}).get, library.get.
def library_state(library):
    state = library.get('connection_state')
    if state == 'no_access':
        return 'Нужно разрешение Фото'
    if not library.get('active'):
        return 'Не подключена · сохранённый каталог'
    if library.get('paused'):
        return 'Пауза'
    if (library.get('sync_schedule') or {}).get('blocked'):
        return 'Синхронизация ожидает ночного окна'
    if library.get('status') == 'scanning':
        return 'Обновляю каталог…'
    waiting = int(library.get('waiting') or 0)
    pending = int(library.get('thumbnail_pending') or 0)
    if waiting and pending <= waiting and not library.get('thumbnail_running'):
        return f'Ожидают миниатюру Photos: {waiting}'
    if pending or library.get('thumbnail_running'):
        return 'Загружаю превью'
    return 'Есть ошибки превью' if library.get('thumbnail_error') else 'Превью готовы'


#: Показывает медиатеки, привязанные копии, расписание и команды оригиналов.
#: Зависимости конструктора: workspace.
class PhotoLibrariesUI:
    #: Инициализирует PhotoLibrariesUI и его рабочее состояние.
    #: Обновляет состояние объекта: busy, copy_roles_signature, libraries, refreshing, rows, signature, ws.
    def __init__(self, workspace):
        self.ws = workspace
        self.libraries = []
        self.connection = {}
        self.cloud = {}
        self.expanded = set()
        self.rows = {}
        self.signature = None
        self.copy_roles_signature = None
        self.busy = self.refreshing = False

    #: Находит копию медиатеки, содержащую выбранный файловый путь.
    #: Поля результата: label, is_root, inherited_from, media_library.
    def copy_membership(self, volume_id, path):
        for library in self.libraries:
            for copy in library.get('copies', []):
                if copy.get('connected', True) and copy['volume_id'] == volume_id and copy['path'] == path:
                    return dict(copy, label=f"{copy['number']:02d}-copy", is_root=True,
                                inherited_from=None, media_library=library.get('label') or 'Photos')
        return None

    #: Обновляет метки копий Photos в уже загруженных деревьях.
    #: Обновляет состояние объекта: copy_roles_signature.
    def refresh_copy_roles(self):
        signature = tuple((library['id'], library.get('label'),
                           tuple((c['id'], c['volume_id'], c['path'], c['number'], c.get('connected', True))
                                 for c in library.get('copies', []))) for library in self.libraries)
        if (signature == self.copy_roles_signature or self.ws.context_menu_open
                or getattr(self.ws, 'editing', False)):
            return
        self.copy_roles_signature = signature
        for pane in self.ws.panes:
            if pane.view_mode == 'tree' and pane.volume_id and not self.ws.is_photos(pane.volume_id):
                pane.render()

    #: Представляет сохранённые медиатеки как виртуальные тома рабочего пространства.
    #: Использует s.get.
    def volumes(self):
        return [dict(id=f"photos-{s['id']}", source_id=s['id'], kind='photos',
                     name=s.get('label') or 'Photos', display_name=s.get('label') or 'Photos',
                     mount_path=None, availability='online' if s['active'] else 'offline',
                     mounted=False, identity_status='virtual', library=s) for s in self.libraries]

    #: Создаёт сворачиваемый список источников, сохраняя прежнюю настройку раскрытия.
    #: Обновляет состояние объекта: cards, note, section.
    def build(self):
        ui.add_css(LIBRARY_CSS)
        with self.ws.sidebar_expansion('libraries', 'Источники', icon='folder_open').props('dense').classes('copy-section w-full') as self.section:
            self.cards = ui.column().classes('library-list')
            self.note = ui.label().classes('library-note w-full truncate')
            self.note.set_visibility(False)

    #: Обновляет Photos и iCloud независимо, сохраняя раскрытие копий и открытое меню.
    #: Обновляет состояние объекта: cloud, connection, libraries, refreshing, signature.
    async def refresh(self):
        if self.refreshing or self.ws.client.is_deleted:
            return
        self.refreshing = True
        try:
            photos, cloud = await gather(
                self.ws.request('GET', '/api/photos/libraries', timeout=20),
                self.ws.request('GET', '/api/icloud/drive', timeout=20),
                return_exceptions=True)
            with self.ws.client:
                if self.ws.client.is_deleted:
                    return
                errors = [self.ws.error_text(result) for result in (photos, cloud) if isinstance(result, Exception)]
                if isinstance(photos, dict):
                    self.libraries, self.connection = photos['libraries'], photos.get('connection', {})
                if isinstance(cloud, dict):
                    self.cloud = cloud
                self.note.text = errors[0] if errors else ''
                self.note.set_visibility(bool(errors))
                self.section.text = f'Источники · {len(self.libraries) + bool(self.cloud)}'
                signature = self.render_signature()
                if signature != self.signature and not self.ws.context_menu_open:
                    self.signature = signature
                    self.render()
                    for pane in self.ws.panes:
                        if self.ws.is_photos(pane.display_volume_id) or pane.display_volume_id == ICLOUD_VOLUME_ID:
                            pane.path_signature = None
                            pane.update_header()
                self.refresh_copy_roles()
                self.update_readouts()
                for library in self.libraries:
                    for pane in self.ws.panes:
                        if pane.view_mode == 'preview' and pane.preview.volume_id == f"photos-{library['id']}":
                            await pane.preview.refresh_pending(library.get('thumbnail_done', 0))
        except Exception as error:
            if not self.ws.client.is_deleted:
                self.note.text = self.ws.error_text(error)
                self.note.set_visibility(True)
        finally:
            self.refreshing = False

    #: Отслеживает только изменения состава строк и доступности команд меню.
    #: Числовой прогресс и подробности обновляются на существующих элементах UI.
    def render_signature(self):
        photos = tuple((library['id'], library.get('label'), library['active'], library['paused'],
                        tuple((library.get('sync_schedule') or {}).get(key) for key in ('night_only', 'start_hour', 'end_hour')),
                        tuple((c['id'], c['volume_name'], c['path'], c['number'], c.get('source_link_id'),
                               c.get('source_label'), c['availability'], self.originals_running(c))
                              for c in library.get('copies', []))) for library in self.libraries)
        cloud = tuple((c['id'], c['number'], c['volume_name'], c['active'], c['availability']) for c in self.cloud.get('copies', []))
        return photos, cloud, self.cloud.get('volume'), self.connection.get('state')

    #: Возвращает виртуальный том iCloud Drive после первого успешного опроса.
    #: Использует self.cloud.get.
    def cloud_volume(self):
        return self.cloud.get('volume')

    #: Раскрывает или сворачивает список копий отдельного источника.
    #: Обновляет состояние объекта: expanded и видимость списка.
    def toggle_copies(self, key, button, copies):
        if key in self.expanded:
            self.expanded.remove(key)
        else:
            self.expanded.add(key)
        opened = key in self.expanded
        button.props('icon=' + ('expand_more' if opened else 'chevron_right'))
        button.props['aria-expanded'] = str(opened).lower()
        button.props['aria-label'] = 'Свернуть копии' if opened else 'Показать копии'
        copies.set_visibility(opened)

    #: Сохраняет фокус бокового меню при фоновом обновлении.
    #: Использует menu.on.
    def track_menu(self, menu):
        menu.on('before-show', lambda: setattr(self.ws, 'context_menu_open', True))
        menu.on('hide', lambda: setattr(self.ws, 'context_menu_open', False))

    #: Создаёт строку источника или копии с одним показателем и кнопкой команд.
    #: Возвращает обновляемую подпись показателя и её подсказку.
    def source_line(self, name, on_open, on_menu, *, active=False, copy=False, path=None, toggle=None):
        classes = 'source-row items-center no-wrap' + (' active' if active else '') + (' source-copy' if copy else '')
        with ui.row().classes(classes) as line:
            if toggle:
                toggle()
            button = ui.button(name, on_click=on_open).props('flat dense no-caps color=dark align=left').classes('source-name')
            if path:
                button.tooltip(path)
            status = ui.label().classes('source-readout truncate')
            with status:
                detail = ui.tooltip()
            with ui.button(icon='more_horiz').props('flat dense size=sm color=grey-7 aria-label="Команды"'):
                with ui.menu().props('anchor="bottom right" self="top right"') as menu:
                    self.track_menu(menu)
                    on_menu()
            line.on('contextmenu', menu.open, js_handler='(event) => { event.preventDefault(); emit(); }')
        return status, detail

    #: Создаёт заголовок источника и отдельный раскрываемый список его копий.
    #: Возвращает показатель заголовка и контейнер строк копий.
    @contextmanager
    def source(self, key, name, on_open, on_menu, *, active, copies, schedule='', title=None):
        with ui.column().classes('w-full source-items'):
            opened = key in self.expanded
            button = None

            #: Создаёт кнопку раскрытия копий текущего источника.
            #: Открытие изменяет видимость строк без повторного запроса Core.
            def toggle():
                nonlocal button
                button = ui.button(icon='expand_more' if opened else 'chevron_right',
                                   on_click=lambda: self.toggle_copies(key, button, children)).props(
                    f'flat dense size=sm color=grey-7 aria-expanded={str(opened).lower()}')
                button.props['aria-label'] = 'Свернуть копии' if opened else 'Показать копии'

            header = self.source_line(name, on_open, on_menu, active=active, path=title, toggle=toggle if copies else None)
            if schedule:
                ui.label(schedule).classes('source-schedule')
            with ui.column().classes('w-full source-items') as children:
                yield header
            children.set_visibility(opened)

    #: Определяет, запущены ли оригиналы копии Photos либо ожидают расписания.
    #: Использует copy.get, job.get.
    @staticmethod
    def originals_running(copy):
        job = copy.get('originals') or {}
        return job.get('state') in ('manifest', 'inventory', 'saving', 'pausing') or job.get('scheduled', False)

    #: Заполняет меню управления системной медиатекой и разрешением Photos.
    #: Использует self.add, self.authorize, self.connect.
    def connection_menu(self):
        if self.connection.get('state') == 'no_access':
            ui.menu_item('Разрешить доступ Photos', on_click=self.authorize)
        ui.menu_item('Подключить текущую медиатеку', on_click=self.connect)
        ui.menu_item('Добавить текущую медиатеку', on_click=self.add)

    #: Заполняет меню выбранной медиатеки и её настроек.
    #: Использует self.connection_menu и существующие команды Photos.
    def library_menu(self, library):
        source_id = library['id']
        ui.menu_item('Подробнее о медиатеке', on_click=lambda: self.library_details(source_id))
        ui.menu_item('Переименовать', on_click=lambda: self.rename(library))
        ui.menu_item('Продолжить превью' if library['paused'] or not library['active'] else 'Пауза превью',
                     on_click=lambda: self.toggle(library))
        night_only = bool((library.get('sync_schedule') or {}).get('night_only'))
        ui.menu_item(('✓ ' if night_only else '') + 'Синхронизация только ночью', on_click=lambda: self.toggle_schedule(library))
        ui.menu_item('Часы ночной синхронизации…', on_click=lambda: self.schedule_dialog(library))
        scan = ui.menu_item('Обновить каталог', on_click=lambda: self.scan(source_id))
        scan.set_enabled(bool(library['active']))
        ui.menu_item('Привязать папку для копий оригиналов', on_click=lambda: self.bind(library))
        ui.separator()
        self.connection_menu()

    #: Заполняет меню копии Photos командами передачи и связей.
    #: Использует originals_running для выбора команды передачи.
    def photo_copy_menu(self, library, copy):
        source_id = library['id']
        running = self.originals_running(copy)
        ui.menu_item('Пауза сохранения' if running else 'Сохранить / проверить оригиналы',
                     on_click=lambda: self.originals_action(source_id, copy, running))
        ui.menu_item('Подробности и журнал', on_click=lambda: self.originals_journal(source_id, copy))
        ui.menu_item('Источник копирования…', on_click=lambda: self.copy_source_dialog(library, copy))
        if copy['number'] != 1:
            ui.menu_item('Сделать 01-copy', on_click=lambda: self.action('POST', f"/api/photos/libraries/{source_id}/copies/{copy['id']}/make-first"))
        ui.separator()
        ui.menu_item('Отвязать копию', on_click=lambda: self.unbind(source_id, copy))

    #: Перерисовывает компактные заголовки и строки копий Photos и iCloud Drive.
    #: Сохраняет команды на кнопках меню и правом клике по строке.
    def render(self):
        self.cards.clear()
        self.rows.clear()
        with self.cards:
            for library in self.libraries:
                source_id = library['id']
                copies = library.get('copies', [])
                title = library.get('label') or 'Photos'
                name = 'Photos' if title == 'Системная медиатека Photos' else title
                with self.source(source_id, name, lambda sid=source_id: self.ws.open_library(sid),
                                 lambda s=library: self.library_menu(s), active=library['active'],
                                 copies=copies, schedule=schedule_text(library), title=title) as status:
                    self.rows[source_id] = dict(status=status, copies={})
                    for copy in copies:
                        self.rows[source_id]['copies'][copy['id']] = self.render_copy(
                            copy, lambda s=library, c=copy: self.photo_copy_menu(s, c))
            if not self.libraries:
                self.rows['photos'] = dict(status=self.source_line('Photos', None, self.connection_menu))
            if self.cloud:
                copies = self.cloud['copies']
                with self.source(ICLOUD_VOLUME_ID, 'iCloud Drive', self.open_cloud, self.cloud_menu,
                                 active=self.cloud_volume()['availability'] == 'online', copies=copies) as status:
                    self.rows[ICLOUD_VOLUME_ID] = dict(status=status, copies={})
                    for copy in copies:
                        self.rows[ICLOUD_VOLUME_ID]['copies'][copy['id']] = self.render_copy(
                            copy, lambda c=copy: self.cloud_copy_menu(c))

    #: Рисует строку копии с переходом в её папку и подсказкой полного пути.
    #: Возвращает показатель состояния строки.
    def render_copy(self, copy, on_menu):
        return self.source_line(f"{copy['number']:02d}-copy · {copy['volume_name']}",
                                lambda: self.ws.open_volume(copy['volume_id'], 1, path=copy['path']), on_menu,
                                path=f"{copy['volume_name']} /{copy['path']}", copy=True)

    #: Применяет краткую подпись и подробную подсказку к существующей строке.
    #: Обновляет поля элементов label и tooltip.
    @staticmethod
    def set_readout(elements, text, details):
        label, tooltip = elements
        label.text = text
        tooltip.text = details

    #: Обновляет компактный статус источников и копий без перерисовки строк.
    #: Использует полные подписи прогресса в подсказках.
    def update_readouts(self):
        if row := self.rows.get('photos'):
            self.set_readout(row['status'], 'Доступ' if self.connection.get('state') == 'no_access' else '',
                             self.connection.get('error') or 'Настройки Photos')
        for library in self.libraries:
            if row := self.rows.get(library['id']):
                done = int(library.get('thumbnail_done') or 0)
                total = int(library.get('thumbnail_total') or 0)
                text = f'{done / total:.1%}' if total else '—'
                if not library['active']:
                    text = 'Офлайн'
                elif library['paused']:
                    text = 'Пауза'
                self.set_readout(row['status'], text, progress_text(library) + ' · ' + library_state(library))
                for copy in library.get('copies', []):
                    if elements := row['copies'].get(copy['id']):
                        job = copy.get('originals') or {}
                        total = job.get('total_assets') or 0
                        done = job.get('done_assets') or 0
                        state = job.get('state', 'idle')
                        text = ('Офлайн' if copy['availability'] != 'online' else '✓' if state == 'completed'
                                else '⚠' if state in ('failed', 'completed_with_errors') else f'{done / total:.0%}' if total else '—')
                        self.set_readout(elements, text, originals_text(copy) + ' · ' + originals_state(copy))
        if row := self.rows.get(ICLOUD_VOLUME_ID):
            copies = self.cloud['copies']
            online = self.cloud_volume()['availability'] == 'online'
            text = f'{len(copies)} коп.' if online else 'Офлайн'
            self.set_readout(row['status'], text, 'iCloud Drive на M4' if online else 'iCloud Drive недоступен на M4')
            for copy in copies:
                if elements := row['copies'].get(copy['id']):
                    text = self.cloud_copy_status(copy)
                    self.set_readout(elements, text, copy['message'] or f"{copy['done']} / {copy['total']} файлов")

    #: Показывает прогресс и состояние превью в подробностях медиатеки.
    #: Использует progress_text, library_state.
    def library_details(self, source_id):
        library = next((s for s in self.libraries if s['id'] == source_id), None)
        if not library:
            return
        with ui.dialog() as dialog, ui.card().classes('w-[420px] max-w-full p-5 gap-2'):
            ui.label(library.get('label') or 'Photos').classes('text-lg font-semibold')
            ui.label(progress_text(library))
            done, total = library.get('thumbnail_done') or 0, library.get('thumbnail_total') or 0
            ui.linear_progress(value=min(1, done / total) if total else 0, show_value=False).props('color=green-7')
            ui.label(library_state(library)).classes('s-note')
            if schedule := schedule_text(library):
                ui.label(schedule).classes('s-note')
            ui.button('Закрыть', on_click=dialog.close).props('flat no-caps')
        dialog.open()

    #: Открывает дерево iCloud Drive в активной панели с режимом дерева.
    #: Асинхронно ожидает: self.ws.open_volume.
    async def open_cloud(self):
        if self.cloud_volume()['availability'] != 'online':
            ui.notify('iCloud Drive недоступен на M4', type='warning')
            return
        index = self.ws.active_index
        if self.ws.panes[index].view_mode == 'preview':
            index = 1 - index
        await self.ws.open_volume(ICLOUD_VOLUME_ID, index)

    #: Показывает команду добавления копии для доступного iCloud Drive.
    #: Использует self.bind_cloud.
    def cloud_menu(self):
        bind = ui.menu_item('Привязать папку для копии…', on_click=self.bind_cloud)
        bind.set_enabled(self.cloud_volume()['availability'] == 'online')

    #: Подписывает состояние передачи iCloud Drive для компактной строки.
    #: Использует состояние очереди и количество обработанных файлов.
    @staticmethod
    def cloud_copy_status(copy):
        if copy['availability'] != 'online':
            return 'Офлайн'
        return {'idle': '—', 'paused': 'Пауза', 'waiting': 'Ждёт', 'completed': '✓',
                'completed_with_conflicts': '⚠'}.get(copy['state'], f"{copy['done']}/{copy['total']}")

    #: Показывает команды передачи, журнала и отвязки копии iCloud.
    #: Использует self.action, self.cloud_details.
    def cloud_copy_menu(self, copy):
        endpoint = f"/api/icloud/copies/{copy['id']}"
        action = 'pause' if copy['active'] else 'start'
        title = 'Пауза' if copy['active'] else 'Скопировать недостающие'
        ui.menu_item(title, on_click=lambda: self.action('POST', f'{endpoint}/{action}'))
        ui.menu_item('Подробности и журнал', on_click=lambda: self.cloud_details(copy['id']))
        ui.separator()
        unbind = ui.menu_item('Отвязать копию', on_click=lambda: self.action('DELETE', endpoint))
        unbind.set_enabled(not copy['active'])

    #: Связывает весь iCloud Drive или выбранную слева папку с назначением справа.
    #: Асинхронно ожидает: self.action и подтверждение диалога.
    async def bind_cloud(self):
        scope = self.ws.panes[1].scope()
        volume = self.ws.resolve_volume(scope['volume_id']) if scope else None
        if not volume or not scope['path'] or volume['availability'] != 'online':
            ui.notify('Открой папку назначения на подключённом томе в правой панели.', type='info')
            return
        left = self.ws.panes[0]
        paths = {'': 'Весь iCloud Drive'}
        if left.volume_id == ICLOUD_VOLUME_ID and left.view_mode == 'tree' and left.kind == 'directory' and left.path:
            paths[left.path] = f'iCloud Drive /{left.path}'
        with ui.dialog() as dialog, ui.card().classes('w-[460px] max-w-full p-5 gap-3'):
            ui.label('Привязать копию iCloud Drive').classes('text-lg font-semibold')
            source = ui.select(paths, value=next(reversed(paths)), label='Скопировать из').props('outlined dense').classes('w-full')
            ui.label('Назначение').classes('s-muted text-xs')
            ui.label((volume.get('display_name') or volume['name']) + ' /' + scope['path']).classes('s-path break-words')
            if len(paths) == 1:
                ui.label('Чтобы выбрать отдельную папку, открой её в iCloud Drive слева.').classes('s-note')
            with ui.row().classes('w-full justify-end'):
                ui.button('Отмена', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
                ui.button('Привязать', on_click=lambda: dialog.submit(source.value)).props('unelevated no-caps color=green-9')
        choice = await dialog
        if choice is not None:
            self.expanded.add(ICLOUD_VOLUME_ID)
            await self.action('POST', '/api/icloud/copies', json=dict(scope, source_path=choice))

    #: Показывает состояние копии и постраничный журнал iCloud Drive.
    #: Отображает причину и дату каждой запланированной повторной попытки.
    async def cloud_details(self, copy_id):
        copy = next((c for c in self.cloud['copies'] if c['id'] == copy_id), None)
        if not copy:
            return
        offset = 0
        with ui.dialog() as dialog, ui.card().classes('w-[660px] max-w-full p-5 gap-2'):
            ui.label(f"iCloud Drive · {copy['number']:02d}-copy").classes('text-lg font-semibold')
            ui.label(f"iCloud Drive /{copy['source_path']} → {copy['volume_name']} /{copy['path']}").classes('s-path break-words')
            ui.label(f"{copy['done']} из {copy['total']} файлов · ждут {copy['waiting']} · расхождений {copy['conflicts']}").classes('s-note')
            ui.linear_progress(value=copy['done'] / copy['total'] if copy['total'] else 0, show_value=False).props('color=green-7')
            if copy['message']:
                ui.label(copy['message']).classes('s-note break-words')
            if copy['retry_at']:
                ui.label('Повтор ' + retry_time(copy['retry_at'])).classes('s-note')
            entries = ui.column().classes('w-full max-h-[55vh] overflow-auto gap-1')

            #: Получает и добавляет страницу событий в открытый журнал.
            #: Обновляет смещение и видимость кнопки следующей страницы.
            async def more():
                nonlocal offset
                more_button.disable()
                try:
                    data = await self.ws.request('GET', f'/api/icloud/copies/{copy_id}/journal', params={'offset': offset})
                    with entries:
                        for item in data['items']:
                            next_at = item['retry_at']
                            retry = ' · повтор ' + retry_time(next_at) if next_at else ''
                            ui.label(f"{item['path'] or '/'} · {item['message'] or 'Готово'}{retry}").classes('text-xs break-all')
                        if not offset and not data['items']:
                            ui.label('Записей пока нет').classes('s-note')
                    offset += len(data['items'])
                    more_button.set_visibility(data['more'])
                except Exception as error:
                    self.ws.notice(error)
                finally:
                    more_button.enable()

            with ui.row().classes('w-full justify-end'):
                more_button = ui.button('Ещё записи', on_click=more).props('flat no-caps')
                ui.button('Закрыть', on_click=dialog.close).props('flat no-caps')
        dialog.open()
        await more()

    #: Исполняет команду источника с единым обновлением UI и обработкой ошибки.
    #: Обновляет состояние объекта: busy, signature.
    async def action(self, method, path, *, timeout=45, **kwargs):
        if self.busy:
            return
        self.busy = True
        try:
            await self.ws.request(method, path, timeout=timeout, **kwargs)
        except Exception as error:
            self.ws.notice(error)
        finally:
            self.busy = False
            self.signature = None
            await self.refresh()

    #: Запрашивает разрешение на доступ к Photos через Core.
    #: Асинхронно ожидает: self.action.
    async def authorize(self):
        await self.action('POST', '/api/photos/authorize', timeout=700)

    #: Повторяет сопоставление текущей системной медиатеки с сохранённым профилем.
    #: Асинхронно ожидает: self.action.
    async def connect(self):
        await self.action('POST', '/api/photos/libraries/connect')

    #: Переключает ручную паузу выбранной медиатеки.
    #: Асинхронно ожидает: self.action.
    async def toggle(self, library):
        action = 'resume' if library['paused'] or not library['active'] else 'pause'
        await self.action('POST', f"/api/photos/libraries/{library['id']}/{action}")

    #: Включает или выключает ограничение синхронизации ночным окном.
    #: Асинхронно ожидает: self.action.
    async def toggle_schedule(self, library):
        settings = library.get('sync_schedule') or {}
        await self.action('PATCH', f"/api/photos/libraries/{library['id']}/sync-schedule", json={
            'night_only': not settings.get('night_only', False),
            'start_hour': settings.get('start_hour', 0), 'end_hour': settings.get('end_hour', 7)})

    #: Показывает настройку часов разрешённого окна по Москве.
    #: Асинхронно ожидает: self.action.
    async def schedule_dialog(self, library):
        settings = library.get('sync_schedule') or {}
        with ui.dialog() as dialog, ui.card().classes('w-[420px] max-w-full p-5 gap-3'):
            ui.label('Ночная синхронизация').classes('text-lg font-semibold')
            enabled = ui.checkbox('Синхронизировать только ночью', value=bool(settings.get('night_only')))
            hours = {hour: f'{hour:02d}:00' for hour in range(24)}
            start = ui.select(hours, value=settings.get('start_hour', 0), label='Начало').props('outlined dense').classes('w-full')
            end = ui.select(hours, value=settings.get('end_hour', 7), label='Окончание').props('outlined dense').classes('w-full')
            ui.label('Время московское. Вне окна оригиналы и фоновые превью ждут. Ручная пауза сохраняется. M4 должен работать.').classes('s-note')
            with ui.row().classes('w-full justify-end'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button('Сохранить', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
        if await dialog:
            await self.action('PATCH', f"/api/photos/libraries/{library['id']}/sync-schedule", json={
                'night_only': enabled.value, 'start_hour': start.value, 'end_hour': end.value})

    #: Запрашивает ручное обновление индекса выбранной медиатеки.
    #: Асинхронно ожидает: self.action.
    async def scan(self, source_id):
        await self.action('POST', f'/api/sources/{source_id}/scan', timeout=650)

    #: Показывает ввод названия медиатеки и возвращает подтверждённое значение.
    #: Использует title.startswith, ui.button, ui.button('Отмена', on_click=lambda : dialog.submit(None)).props и ещё 2.
    async def name_dialog(self, title, value):
        with ui.dialog() as dialog, ui.card().classes('w-[420px] max-w-full p-5 gap-3'):
            ui.label(title).classes('text-lg font-semibold')
            name = ui.input('Название', value=value).props('outlined dense maxlength=120 autofocus').classes('w-full')
            if title.startswith('Сохранить'):
                ui.label('Сначала открой отдельную системную медиатеку нужного Apple ID в Photos на M4.').classes('s-note')
            with ui.row().classes('w-full justify-end'):
                ui.button('Отмена', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
                ui.button('Сохранить', on_click=lambda: dialog.submit((name.value or '').strip())).props('unelevated no-caps color=green-9')
        return await dialog

    #: Добавляет текущую системную медиатеку под выбранным названием.
    #: Асинхронно ожидает: self.action, self.name_dialog.
    async def add(self):
        name = await self.name_dialog('Сохранить текущую медиатеку Photos', f'Photos {len(self.libraries) + 1}')
        if name:
            await self.action('POST', '/api/photos/libraries', json={'label': name})

    #: Меняет пользовательское название сохранённой медиатеки.
    #: Асинхронно ожидает: self.action, self.name_dialog.
    async def rename(self, library):
        name = await self.name_dialog('Название медиатеки', library.get('label') or 'Photos')
        if name:
            await self.action('PATCH', f"/api/photos/libraries/{library['id']}", json={'label': name})

    #: Привязывает выбранную файловую папку к медиатеке после проверки выбора.
    #: Асинхронно ожидает: self.action.
    async def bind(self, library):
        scope = self.ws.panes[1].scope()
        if not scope or not scope['path']:
            ui.notify('Сначала открой папку для копии в правой панели.', type='info')
            return
        volume = next(v for v in self.ws.volumes if v['id'] == scope['volume_id'])
        with ui.dialog() as dialog, ui.card().classes('w-[470px] max-w-full p-5 gap-3'):
            ui.label('Привязать папку для копий оригиналов').classes('text-lg font-semibold')
            ui.label(library.get('label') or 'Photos').classes('font-semibold')
            ui.label((volume.get('display_name') or volume['name']) + ' /' + scope['path']).classes('s-path break-words')
            ui.label('Оригиналы будут сохраняться сразу в эту папку. Для запуска выбери «Сохранить оригиналы» в меню папки копии. Сохранённые оригиналы определяются по учёту Photos и параметрам файлов.').classes('s-note')
            with ui.row().classes('w-full justify-end'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button('Привязать', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
        if await dialog:
            await self.action('POST', f"/api/photos/libraries/{library['id']}/copies", json=scope)

    #: Отключает выбранную привязку копии медиатеки через Core.
    #: Асинхронно ожидает: self.action.
    async def unbind(self, source_id, copy):
        await self.action('DELETE', f"/api/photos/libraries/{source_id}/copies/{copy['id']}")


    #: Запускает или приостанавливает сохранение оригиналов выбранной копии.
    #: Асинхронно ожидает: self.action.
    async def originals_action(self, source_id, copy, running):
        action = 'pause' if running else 'start'
        await self.action('POST', f"/api/photos/libraries/{source_id}/copies/{copy['id']}/originals/{action}")

    #: Показывает выбор Photos или другой копии как источника оригиналов.
    #: Асинхронно ожидает: self.action.
    async def copy_source_dialog(self, library, copy):
        choices = {'photos':'Photos · системная медиатека'}
        choices.update({c['id']:f"{c['number']:02d}-copy · {c['volume_name']} /{c['path']}"
                        for c in library['copies'] if c['id']!=copy['id']})
        with ui.dialog() as dialog,ui.card().classes('w-[560px] max-w-full p-5 gap-3'):
            ui.label(f"Источник для {copy['number']:02d}-copy").classes('text-lg font-semibold')
            current = copy.get('source_link_id') or 'photos'
            selected = ui.select(choices,value=current if current in choices else None,label='Копировать из').classes('w-full').props('outlined')
            ui.label('Готовые оригиналы передаются из выбранной копии. Пауза и продолжение управляют всей цепочкой.').classes('s-note')
            with ui.row().classes('w-full justify-end'):
                ui.button('Отмена',on_click=lambda:dialog.submit(None)).props('flat no-caps')
                ui.button('Сохранить',on_click=lambda:dialog.submit(selected.value)).props('no-caps')
        value = await dialog
        if value:
            await self.action('PATCH',f"/api/photos/libraries/{library['id']}/copies/{copy['id']}/source",json={'source_id':None if value=='photos' else value})

    #: Показывает события сохранения и пути незавершённых оригиналов.
    #: Обрабатывает ошибки: Exception.
    async def originals_journal(self, source_id, copy):
        try:
            data = await self.ws.request('GET', f"/api/photos/libraries/{source_id}/copies/{copy['id']}/originals/journal")
            job = data['job']
            total = job.get('total_assets') or 0
            with ui.dialog() as dialog, ui.card().classes('w-[720px] max-w-full p-5 gap-3'):
                ui.label('Сохранение оригиналов · журнал').classes('text-lg font-semibold')
                ui.label(f"{copy['volume_name']} /{copy['path']}").classes('s-path break-words')
                ui.label(originals_text(dict(copy, originals=job))).classes('s-note')
                ui.linear_progress(value=min(1, (job.get('done_assets') or 0) / total) if total else 0,
                                   show_value=False).props('color=blue-7')
                ui.label(job.get('message', '')).classes('s-note')
                with ui.column().classes('w-full max-h-[60vh] overflow-auto gap-2'):
                    for path in data.get('incomplete_paths', []):
                        ui.label('Незавершённый файл оставлен в копии: ' + path).classes('text-xs text-red-8 break-all')
                    for item in data['items']:
                        ui.label(f"{item['created_at'][:19]} · {item['path']} · {item['message']}").classes('text-xs break-all')
                    if not data['items']:
                        ui.label('Записей пока нет').classes('s-note')
                ui.button('Закрыть', on_click=dialog.close).props('flat no-caps')
            dialog.open()
        except Exception as error:
            self.ws.notice(error)
