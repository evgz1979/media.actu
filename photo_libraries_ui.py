"""Library bookmarks, per-library thumbnail progress, and copy associations."""
from pathlib import PurePosixPath

from nicegui import ui


LIBRARY_CSS = '''
.library-list { width:100%; padding:4px; gap:5px; }
.library-button.q-btn { width:100%; padding:8px; text-align:left; border:1px solid transparent; }
.library-button .q-btn__content { width:100%; display:flex; flex-direction:column; align-items:stretch; gap:4px; }
.library-button.connected { background:#edf4e9; border-color:#c5d3bd; }
.library-name { font-size:12px; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.library-progress { font-size:10px; color:#6c7865; text-transform:none; overflow-wrap:anywhere; line-height:14px; }
.library-progress-bar { height:3px; }
.library-copy { display:block; padding:3px 8px 3px 18px; font-size:10px; color:#637b91; text-decoration:none; overflow-wrap:anywhere; }
.library-note { font-size:10px; line-height:15px; color:#7b8475; padding:5px 10px; }
.library-actions .q-btn { font-size:10px; padding:2px 7px; min-height:26px; }
'''


def progress_text(library):
    done = int(library.get('thumbnail_done') or 0)
    total = int(library.get('thumbnail_total') or 0)
    percent = f'{done / total * 100:.1f}%' if total else '0%'
    return f'Превью {done:,} / {total:,} · {percent}'.replace(',', ' ')


def originals_text(copy):
    job = copy.get('originals') or {}
    title = f"Сохранение оригиналов · {copy['number']:02d}-copy"
    if job.get('state', 'idle') == 'idle':
        return title + ' · не запускалось'
    total, done = job.get('total_assets', 0), job.get('done_assets', 0)
    return title + f' · {done:,} / {total:,}'.replace(',', ' ')


def originals_state(copy):
    job = copy.get('originals') or {}
    state = job.get('state', 'idle')
    if state == 'inventory':
        return f"Проверка файлов: {job.get('checked_files', 0):,}".replace(',', ' ')
    if state == 'saving':
        size = job.get('current_bytes', 0) / (1024 * 1024)
        return f"{job.get('current_path', '')} · {size:.1f} МБ" + (f" · iCloud {job['fraction']:.0%}" if 0 < job.get('fraction', 0) < 1 else '')
    return job.get('message', 'Сохранение ещё не запускалось')


def schedule_text(library):
    schedule = library.get('sync_schedule') or {}
    return 'Только ночью · ' + schedule.get('window', '00:00–07:00 МСК') if schedule.get('night_only') else ''


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


class PhotoLibrariesUI:
    def __init__(self, workspace):
        self.ws = workspace
        self.libraries = []
        self.rows = {}
        self.signature = None
        self.copy_roles_signature = None
        self.busy = self.refreshing = False

    def copy_membership(self, volume_id, path):
        for library in self.libraries:
            for copy in library.get('copies', []):
                if copy.get('connected', True) and copy['volume_id'] == volume_id and copy['path'] == path:
                    return dict(copy, label=f"{copy['number']:02d}-copy", is_root=True,
                                inherited_from=None, media_library=library.get('label') or 'Photos')
        return None

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

    def volumes(self):
        return [dict(id=f"photos-{s['id']}", source_id=s['id'], kind='photos',
                     name=s.get('label') or 'Photos', display_name=s.get('label') or 'Photos',
                     mount_path=None, availability='online' if s['active'] else 'offline',
                     mounted=False, identity_status='virtual', library=s) for s in self.libraries]

    def build(self):
        ui.add_css(LIBRARY_CSS)
        with ui.expansion('Медиатеки', icon='photo_library', value=True).props('dense').classes('copy-section w-full') as self.section:
            self.cards = ui.column().classes('library-list')
            self.note = ui.label().classes('library-note w-full')
            with ui.column().classes('library-actions w-full px-2 pb-2 gap-1'):
                self.permission_button = ui.button('Разрешить доступ Photos', icon='lock_open', on_click=self.authorize).props('flat no-caps color=green-9')
                self.connect_button = ui.button('Подключить текущую', icon='sync', on_click=self.connect).props('flat no-caps color=dark')
                self.add_button = ui.button('Добавить текущую медиатеку', icon='add', on_click=self.add).props('flat no-caps color=dark')
        self.permission_button.set_visibility(False)

    async def refresh(self):
        if self.refreshing or self.ws.client.is_deleted:
            return
        self.refreshing = True
        try:
            data = await self.ws.request('GET', '/api/photos/libraries', timeout=20)
            with self.ws.client:
                if self.ws.client.is_deleted:
                    return
                self.libraries = data['libraries']
                connection = data.get('connection', {})
                self.permission_button.set_visibility(connection.get('state') == 'no_access')
                self.add_button.set_enabled(not self.busy and connection.get('state') != 'no_access')
                self.connect_button.set_enabled(not self.busy)
                self.permission_button.set_enabled(not self.busy)
                self.note.text = connection.get('error') or 'Оригиналы → привязанные копии'
                self.section.text = f'Медиатеки · {len(self.libraries)}'
                signature = tuple((s['id'], s.get('label'), s['active'], s['paused'], s['connection_state'],
                                   tuple((s.get('sync_schedule') or {}).get(key) for key in ('night_only', 'start_hour', 'end_hour')),
                                   tuple((c['id'], c['volume_name'], c['path'], c['availability'], (c.get('originals') or {}).get('state'), (c.get('originals') or {}).get('scheduled')) for c in s.get('copies', [])))
                                  for s in self.libraries)
                if signature != self.signature and not self.ws.context_menu_open:
                    self.signature = signature
                    self.render()
                    for pane in self.ws.panes:
                        if self.ws.is_photos(pane.display_volume_id):
                            pane.path_signature = None
                            pane.update_header()
                self.refresh_copy_roles()
                for library in self.libraries:
                    row = self.rows.get(library['id'])
                    if row:
                        row['progress'].text = progress_text(library)
                        total = library.get('thumbnail_total') or 0
                        row['bar'].value = min(1, library.get('thumbnail_done', 0) / total) if total else 0
                        row['state'].text = library_state(library)
                        row['schedule'].text = schedule_text(library)
                        row['schedule'].set_visibility(bool(schedule_text(library)))
                        for copy in library.get('copies', []):
                            refs = row.get('copies', {}).get(copy['id'])
                            if refs:
                                job = copy.get('originals') or {}
                                refs['progress'].text = originals_text(copy)
                                refs['state'].text = originals_state(copy)
                                refs['bar'].value = min(1, job.get('done_assets', 0) / job['total_assets']) if job.get('total_assets') else 0
                    for pane in self.ws.panes:
                        if pane.view_mode == 'preview' and pane.preview.volume_id == f"photos-{library['id']}":
                            await pane.preview.refresh_pending(library.get('thumbnail_done', 0))
        except Exception as error:
            if not self.ws.client.is_deleted:
                self.note.text = self.ws.error_text(error)
        finally:
            self.refreshing = False

    def menu(self):
        menu = ui.context_menu()
        menu.on('show', lambda: setattr(self.ws, 'context_menu_open', True))
        menu.on('hide', lambda: setattr(self.ws, 'context_menu_open', False))
        return menu

    def render(self):
        self.cards.clear()
        self.rows.clear()
        with self.cards:
            for library in self.libraries:
                source_id = library['id']
                with ui.column().classes('w-full gap-0'):
                    with ui.button(on_click=lambda sid=source_id: self.ws.open_library(sid)).props('flat no-caps').classes(
                        'library-button' + (' connected' if library['active'] else '')):
                        with self.menu():
                            ui.menu_item('Открыть медиатеку', on_click=lambda sid=source_id: self.ws.open_library(sid))
                            ui.menu_item('Переименовать', on_click=lambda s=library: self.rename(s))
                            ui.menu_item('Продолжить превью' if library['paused'] or not library['active'] else 'Пауза превью',
                                         on_click=lambda s=library: self.toggle(s))
                            for copy in library.get('copies', []):
                                job = copy.get('originals') or {}
                                running = job.get('state') in ('manifest', 'inventory', 'saving', 'pausing') or job.get('scheduled', False)
                                ui.menu_item(('Пауза оригиналов' if running else 'Продолжить оригиналы') + f" · {copy['number']:02d}-copy",
                                    on_click=lambda sid=source_id, c=copy, active=running: self.originals_action(sid, c, active))
                            night_only = bool((library.get('sync_schedule') or {}).get('night_only'))
                            with ui.menu_item(on_click=lambda s=library: self.toggle_schedule(s)).props(
                                'role=menuitemcheckbox aria-checked=' + str(night_only).lower()):
                                with ui.item_section().props('side'):
                                    ui.icon('check_box' if night_only else 'check_box_outline_blank', size='18px')
                                ui.item_section('Синхронизация только ночью')
                            ui.menu_item('Часы ночной синхронизации…', on_click=lambda s=library: self.schedule_dialog(s))
                            scan = ui.menu_item('Обновить каталог', on_click=lambda sid=source_id: self.scan(sid))
                            scan.set_enabled(bool(library['active']))
                            ui.separator()
                            ui.menu_item('Привязать папку для копий оригиналов', on_click=lambda s=library: self.bind(s))
                        ui.label(library.get('label') or 'Photos').classes('library-name')
                        progress = ui.label(progress_text(library)).classes('library-progress')
                        bar = ui.linear_progress(value=0, show_value=False).props('color=green-7').classes('library-progress-bar')
                        state = ui.label(library_state(library)).classes('library-progress')
                        schedule = ui.label(schedule_text(library)).classes('library-progress')
                        schedule.set_visibility(bool(schedule_text(library)))
                        self.rows[source_id] = dict(progress=progress, bar=bar, state=state, schedule=schedule, copies={})
                        for copy in library.get('copies', []):
                            refs = dict(progress=ui.label(originals_text(copy)).classes('library-progress'))
                            refs['bar'] = ui.linear_progress(value=0, show_value=False).props('color=blue-7').classes('library-progress-bar')
                            refs['state'] = ui.label(originals_state(copy)).classes('library-progress')
                            self.rows[source_id]['copies'][copy['id']] = refs
                        if library.get('copies'):
                            ui.label('Управление: правой кнопкой по папке копии').classes('library-progress')
                    for copy in library.get('copies', []):
                        title = f"{copy['number']:02d}-copy · {copy['volume_name']} /{copy['path']}"
                        with ui.link(title, '#').classes('library-copy').on('click',
                            lambda c=copy: self.ws.open_volume(c['volume_id'], 1, path=c['path']), js_handler='(event) => { event.preventDefault(); emit(); }'):
                            with self.menu():
                                job_state = (copy.get('originals') or {}).get('state', 'idle')
                                running = job_state in ('manifest', 'inventory', 'saving', 'pausing') or (copy.get('originals') or {}).get('scheduled', False)
                                ui.menu_item('Пауза сохранения' if running else ('Сохранить оригиналы' if job_state == 'idle' else 'Продолжить / проверить оригиналы'),
                                             on_click=lambda sid=source_id, c=copy, active=running: self.originals_action(sid, c, active))
                                ui.menu_item('Журнал сохранения', on_click=lambda sid=source_id, c=copy: self.originals_journal(sid, c))
                                ui.separator()
                                ui.menu_item('Отвязать копию', on_click=lambda sid=source_id, c=copy: self.unbind(sid, c))

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

    async def authorize(self):
        await self.action('POST', '/api/photos/authorize', timeout=700)

    async def connect(self):
        await self.action('POST', '/api/photos/libraries/connect')

    async def toggle(self, library):
        action = 'resume' if library['paused'] or not library['active'] else 'pause'
        await self.action('POST', f"/api/photos/libraries/{library['id']}/{action}")

    async def toggle_schedule(self, library):
        settings = library.get('sync_schedule') or {}
        await self.action('PATCH', f"/api/photos/libraries/{library['id']}/sync-schedule", json={
            'night_only': not settings.get('night_only', False),
            'start_hour': settings.get('start_hour', 0), 'end_hour': settings.get('end_hour', 7)})

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

    async def scan(self, source_id):
        await self.action('POST', f'/api/sources/{source_id}/scan', timeout=650)

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

    async def add(self):
        name = await self.name_dialog('Сохранить текущую медиатеку Photos', f'Photos {len(self.libraries) + 1}')
        if name:
            await self.action('POST', '/api/photos/libraries', json={'label': name})

    async def rename(self, library):
        name = await self.name_dialog('Название медиатеки', library.get('label') or 'Photos')
        if name:
            await self.action('PATCH', f"/api/photos/libraries/{library['id']}", json={'label': name})

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
            ui.label('Оригиналы будут сохраняться сразу в эту папку. Для запуска выбери «Сохранить оригиналы» в меню папки копии. Уже лежащие в ней файлы будут проверены по содержимому.').classes('s-note')
            with ui.row().classes('w-full justify-end'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button('Привязать', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
        if await dialog:
            await self.action('POST', f"/api/photos/libraries/{library['id']}/copies", json=scope)

    async def unbind(self, source_id, copy):
        await self.action('DELETE', f"/api/photos/libraries/{source_id}/copies/{copy['id']}")


    async def originals_action(self, source_id, copy, running):
        action = 'pause' if running else 'start'
        await self.action('POST', f"/api/photos/libraries/{source_id}/copies/{copy['id']}/originals/{action}")

    async def originals_journal(self, source_id, copy):
        try:
            data = await self.ws.request('GET', f"/api/photos/libraries/{source_id}/copies/{copy['id']}/originals/journal")
            with ui.dialog() as dialog, ui.card().classes('w-[720px] max-w-full p-5 gap-3'):
                ui.label('Сохранение оригиналов · журнал').classes('text-lg font-semibold')
                ui.label(data['job'].get('message', '')).classes('s-note')
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
