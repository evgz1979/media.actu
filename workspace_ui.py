"""Two independent storage trees and operations in one workspace."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from pathlib import PurePosixPath

from nicegui import ui

from media_manager.comparison import LABELS, NAME_STATUSES
from media_manager.storage import FLAGS, PURPOSES, ROLES, relative_path
from network_ui import show_network_dialog
from storage_ui import CSS, folder_icon


STATUS_COLORS = {
    'names_found': '#39754d', 'other_folder': '#8b743e', 'names_missing': '#b87626',
    'unverified': '#ab5751', 'skipped': '#8b8f92', 'found': '#39754d',
    'cached': '#657891', 'missing': '#b87626', 'candidate': '#77736c',
}
STATUS_ICONS = {'names_found': 'check', 'names_missing': 'remove', 'other_folder': 'alt_route',
                'unverified': 'help_outline', 'skipped': 'block', 'found': 'check',
                'cached': 'history', 'missing': 'remove', 'candidate': 'search'}
JOB_STATES = {'running': 'Выполняется', 'pausing': 'Останавливается',
              'paused': 'Остановлено', 'completed': 'Завершено', 'failed': 'Ошибка'}
WORKSPACE_CSS = """
.commander-intro { padding:12px 26px 10px; }
.commander-intro .s-title { font-size:24px; }
.commander-layout { display:grid; grid-template-columns:240px minmax(0,1fr) minmax(0,1fr); gap:14px; padding:0 26px 26px; width:100%; align-items:start; }
.commander-pane { border:2px solid var(--s-line); }
.commander-pane.active-pane { border-color:#8ba984; }
.commander-pane .s-panel-head { padding:8px 10px; gap:5px; }
.commander-pane .s-tree { height:calc(100vh - 420px); min-height:220px; max-height:none; width:100%; }
.commander-layout.comparing .s-tree { height:calc(100vh - 550px); min-height:190px; }
.commander-pane .s-list-grid { grid-template-columns:minmax(170px,1fr) 116px 62px 62px; min-width:440px; }
.commander-pane .pane-heading { font-size:11px; font-weight:650; color:#71816b; min-height:24px; padding:0 5px; }
.pane-volume { width:100%; } .pane-volume .q-field__control { min-height:36px; }
.pane-path { min-height:17px; width:100%; overflow-wrap:anywhere; }
.pane-status { padding:7px 11px; border-top:1px solid var(--s-line); font-size:11px; min-height:31px; color:var(--s-muted); }
.pane-result { flex-shrink:0; font-size:10px; max-width:150px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.pane-count { font-size:10px; padding:0 3px; background:#edf1e9; border-radius:3px; }
.pane-match { box-shadow:inset 3px 0 #6e9b64; }
.workspace-operations { margin:0 26px 14px; padding:10px 14px; width:calc(100% - 52px); gap:6px; }
.workspace-history { min-width:230px; max-width:340px; }
.workspace-summary { font-size:11px; color:var(--s-muted); width:100%; }
.workspace-results { gap:6px; flex-wrap:wrap; align-items:center; }
.workspace-results .q-btn { font-size:11px; min-height:24px; padding:2px 7px; }
.workspace-scopes { color:#667363; font-size:12px; overflow-wrap:anywhere; }
.workspace-filter { min-width:170px; font-size:11px; }
.workspace-property-grid { display:grid; grid-template-columns:1fr auto; gap:5px 16px; width:100%; font-size:13px; }
.commander-sidebar .s-volumes { max-height:calc(100vh - 340px); }
.commander-sidebar .s-volume-row { padding-left:6px; padding-right:6px; }
.commander-sidebar .s-volume-capacity { font-size:10px; }
@media(max-width:1100px) {
 .commander-layout { grid-template-columns:200px minmax(0,1fr) minmax(0,1fr); gap:10px; padding:0 16px 20px; }
 .workspace-operations { margin:0 16px 12px; width:calc(100% - 32px); }
 .commander-intro { padding:16px; }
}
@media(max-width:760px) {
 .commander-layout { grid-template-columns:minmax(260px,1fr) minmax(260px,1fr); overflow-x:auto; }
 .commander-sidebar { grid-column:1 / -1; }
 .commander-sidebar .s-volumes { max-height:190px; }
 .commander-pane .s-tree { height:440px; min-height:330px; }
 .workspace-history { min-width:180px; }
}
"""


def volume_label(volume, with_share=True):
    name = volume.get('display_name') or volume['name']
    share = volume.get('share_name')
    if with_share and volume.get('marker_id') and share and share.casefold() != name.casefold():
        return f'{name} · {share}'
    return name


def archived(volume):
    return not volume.get('mounted') and (volume['availability'] == 'offline' or volume.get('identity_status') == 'legacy')


class BrowserPane:
    def __init__(self, workspace, index):
        self.workspace = workspace
        self.index = index
        self.title = 'Левая' if index == 0 else 'Правая'
        self.volume_id = None
        self.root_path = ''
        self.path = ''
        self.kind = 'directory'
        self.entry = None
        self.scan = None
        self.job_id = None
        self.folders = {}
        self.expanded = {''}
        self.limits = {}
        self.matches = set()
        self.generation = 0
        self.filter_value = ''
        with ui.column().classes('s-panel commander-pane w-full gap-0') as self.container:
            self.container.on('click', lambda: workspace.set_active(index))
            with ui.column().classes('s-panel-head w-full gap-2'):
                with ui.row().classes('w-full items-center justify-between gap-1 no-wrap'):
                    self.heading = ui.button(self.title + ' панель', on_click=lambda: workspace.set_active(index)).props('flat dense no-caps color=green-9').classes('pane-heading')
                    with ui.row().classes('gap-0 no-wrap'):
                        ui.button(icon='arrow_upward', on_click=self.go_parent).props('flat dense round color=dark').props(f'aria-label="На уровень выше {self.title.lower()}"')
                        ui.button(icon='vertical_align_top', on_click=self.go_root).props('flat dense round color=dark').props(f'aria-label="Корень {self.title.lower()} панели"')
                        ui.button(icon='refresh', on_click=self.refresh).props('flat dense round color=dark').props(f'aria-label="Обновить {self.title.lower()} панель"')
                        ui.button(icon='info_outline', on_click=lambda: workspace.show_properties(self)).props('flat dense round color=dark').props(f'aria-label="Свойства {self.title.lower()} панели"')
                self.volume_select = ui.select({}, label='Том слева' if index == 0 else 'Том справа', on_change=self.volume_changed).props('outlined dense').classes('pane-volume')
                self.path_label = ui.label('Выбери том').classes('s-path s-muted pane-path')
            with ui.row().classes('s-tree-toolbar w-full items-center justify-between no-wrap'):
                self.snapshot_label = ui.label('Просмотр папок').classes('s-muted text-xs')
                self.hidden = ui.checkbox('Скрытые', value=False, on_change=lambda: self.render()).props('dense size=xs').classes('text-xs s-muted')
            options = {'': 'Все результаты', **{s: LABELS[s] for s in NAME_STATUSES}} if index == 0 else {'': 'Все элементы'}
            self.result_filter = ui.select(options, value='', label='Результаты' if index == 0 else 'Список справа',
                                          on_change=self.change_filter).props('outlined dense').classes('workspace-filter mx-2 my-1')
            self.result_filter.set_visibility(False)
            self.tree = ui.column().classes('s-tree gap-0')
            self.footer = ui.label('Том не выбран').classes('pane-status w-full')

    @property
    def volume(self):
        return next((v for v in self.workspace.volumes if v['id'] == self.volume_id), None)

    def scope(self):
        if not self.volume or self.volume.get('identity_status') == 'unverified':
            return None
        path = self.path if self.kind == 'directory' else relative_path(str(PurePosixPath(self.path).parent))
        return {'volume_id': self.volume_id, 'path': path}

    async def volume_changed(self, event):
        if event.value and event.value != self.volume_id:
            await self.show_volume(event.value)

    def update_header(self):
        self.volume_select.options = {
            v['id']: volume_label(v) + (' · архив' if archived(v) else ' · не подтверждён' if v.get('identity_status') == 'unverified' else '')
            for v in self.workspace.volumes
        }
        self.volume_select.update()
        volume = self.volume
        if not volume:
            self.path_label.text = 'Выбери том'
            return
        base = volume['mount_path'] or volume.get('network_url') or ''
        self.path_label.text = base.rstrip('/') + ('/' + self.path if self.path else '')
        if self.scan:
            timestamp = self.scan.get('finished_at') or self.scan.get('started_at')
            self.snapshot_label.text = 'Список сверки: ' + self.workspace.format_date(timestamp)
        else:
            selected = self.folders.get(self.path, self.folders.get(self.root_path, {}))
            timestamp = selected.get('scanned_at')
            cached = selected.get('cached') or volume['availability'] != 'online'
            self.snapshot_label.text = (('Сохранённый снимок: ' if cached else 'Папка прочитана: ') + self.workspace.format_date(timestamp)) if timestamp else 'Снимок папки не сохранён'
        location = 'Архив' if archived(volume) else {'online': 'Подключён', 'unknown': 'Доступность неизвестна', 'offline': 'Отключён'}[volume['availability']]
        self.footer.text = location + ' · ' + self.workspace.capacity_text(volume)
        self.result_filter.set_visibility(bool(self.scan and self.workspace.report and self.workspace.report['mode'] == 'names'))
        self.result_filter.set_enabled(bool(self.scan and self.scan['side'] == 'source'))

    async def show_volume(self, volume_id, path='', *, scan=None, job_id=None, activate=True):
        self.generation += 1
        generation = self.generation
        self.volume_id = volume_id
        self.root_path = relative_path(path)
        self.path = self.root_path
        self.kind, self.entry = 'directory', None
        self.scan, self.job_id = scan, job_id
        self.folders.clear()
        self.expanded = {self.root_path}
        self.limits.clear()
        self.matches.clear()
        self.filter_value = ''
        self.result_filter.set_value('')
        self.volume_select.set_value(volume_id)
        if self.volume and archived(self.volume):
            self.workspace.archive.open()
        if activate:
            self.workspace.set_active(self.index)
        self.update_header()
        self.tree.clear()
        with self.tree:
            ui.spinner(size='22px').classes('m-4')
        await self.load_folder(self.root_path)
        if generation != self.generation:
            return
        self.render()
        self.workspace.render_volumes()
        self.workspace.update_scopes()

    async def load_folder(self, path, *, more=False, refresh=True):
        generation = self.generation
        volume_id = self.volume_id
        try:
            if self.scan:
                previous = self.folders.get(path, {}).get('entries', []) if more else []
                params = {'path': path, 'offset': len(previous), 'limit': 150}
                if self.scan['side'] == 'source':
                    params['status'] = self.filter_value
                    endpoint = f'/api/storage/comparisons/{self.job_id}/tree'
                else:
                    params['scan_id'] = self.scan['id']
                    endpoint = f'/api/storage/comparisons/{self.job_id}/target-tree'
                data = await self.workspace.request('GET', endpoint, params=params, timeout=45)
                data = {**data, 'entries': previous + data['entries'], 'cached': True,
                        'scanned_at': self.scan.get('finished_at') or self.scan.get('started_at') or True}
            else:
                data = await self.workspace.request('GET', f'/api/storage/volumes/{volume_id}/directory',
                                                    params={'path': path, 'refresh': refresh}, timeout=45)
            if generation == self.generation:
                self.folders[path] = data
        except Exception as error:
            if generation == self.generation:
                previous = self.folders.get(path, {})
                self.folders[path] = {**previous, 'entries': previous.get('entries', []), 'cached': True,
                                      'error': self.workspace.error_text(error)}

    async def select(self, entry, toggle=False):
        self.workspace.set_active(self.index)
        self.path, self.kind, self.entry = entry['path'], entry['kind'], entry
        if toggle and self.kind == 'directory':
            if self.path in self.expanded:
                self.expanded.remove(self.path)
            else:
                self.expanded.add(self.path)
                if self.path not in self.folders:
                    await self.load_folder(self.path)
        self.render()
        self.workspace.update_scopes()
        if self.index == 0:
            await self.workspace.refresh_matches()

    async def go_root(self):
        self.workspace.set_active(self.index)
        boundary = self.scan['root_path'] if self.scan else ''
        if self.root_path != boundary:
            await self.show_volume(self.volume_id, boundary, scan=self.scan, job_id=self.job_id)
            return
        self.path, self.kind, self.entry = self.root_path, 'directory', None
        self.expanded.add(self.root_path)
        self.render()
        self.workspace.update_scopes()
        if self.index == 0:
            await self.workspace.refresh_matches()

    async def go_parent(self):
        if self.path == self.root_path:
            boundary = self.scan['root_path'] if self.scan else ''
            if self.root_path != boundary:
                parent = relative_path(str(PurePosixPath(self.root_path).parent))
                await self.show_volume(self.volume_id, parent, scan=self.scan, job_id=self.job_id)
            return
        parent = relative_path(str(PurePosixPath(self.path).parent))
        if self.root_path and parent != self.root_path and not parent.startswith(self.root_path + '/'):
            parent = self.root_path
        self.path, self.kind, self.entry = parent, 'directory', None
        self.expanded.add(parent)
        if parent not in self.folders:
            await self.load_folder(parent)
        self.workspace.set_active(self.index)
        self.render()
        self.workspace.update_scopes()
        if self.index == 0:
            await self.workspace.refresh_matches()

    async def refresh(self):
        if not self.volume_id:
            return
        self.workspace.set_active(self.index)
        path = self.path if self.kind == 'directory' else relative_path(str(PurePosixPath(self.path).parent))
        await self.load_folder(path)
        for child in list(self.folders):
            if child != path and (not path or child.startswith(path + '/')):
                self.folders.pop(child)
                self.expanded.discard(child)
        self.render()

    async def change_filter(self, event):
        if event.value == self.filter_value:
            return
        self.filter_value = event.value
        self.folders.clear()
        self.expanded = {self.root_path}
        await self.load_folder(self.root_path)
        self.render()

    async def more(self, path):
        if self.scan:
            await self.load_folder(path, more=True)
        else:
            self.limits[path] = self.limits.get(path, 150) + 150
        self.render()

    def render(self):
        self.update_header()
        self.tree.clear()
        volume = self.volume
        with self.tree:
            if not volume:
                ui.label('Выбери том для этой панели.').classes('s-muted text-sm p-4')
                return
            if volume.get('identity_status') == 'unverified':
                ui.label(volume.get('identity_error') or 'Носитель не подтверждён').classes('s-error m-3')
                if volume.get('mounted') and volume.get('removable'):
                    ui.button('Зарегистрировать диск', icon='usb', on_click=lambda: self.workspace.register_disk(self)).props('unelevated no-caps color=green-9').classes('m-3')
                return
            with ui.element('div').classes('s-tree-heading s-list-grid'):
                for title in ['Имя', 'Дата изменения', 'Размер', 'Тип']:
                    with ui.element('div'):
                        ui.label(title)
            row_numbers = count()

            def branch(path, depth):
                data = self.folders.get(path)
                if not data:
                    return
                if data.get('error'):
                    ui.label(data['error']).classes('s-error m-2')
                if not data.get('scanned_at') and not data.get('entries'):
                    ui.label('Список готовится.' if self.scan and self.scan['state'] in ('pending', 'running') else 'Снимок папки не сохранён.').classes('s-muted text-xs p-3')
                    return
                entries = [e for e in data.get('entries', []) if self.hidden.value or not e['name'].startswith('.')]
                limit = len(entries) if self.scan else self.limits.get(path, 150)
                if not entries and not data.get('error'):
                    ui.label('Нет видимых элементов' if data.get('entries') else 'Папка пуста').classes('s-muted text-xs p-3')
                for entry in entries[:limit]:
                    directory = entry['kind'] == 'directory'
                    classes = 's-entry s-list-grid' + (' alt' if next(row_numbers) % 2 else '')
                    classes += ' selected' if entry['path'] == self.path else ''
                    classes += ' pane-match' if entry['path'] in self.matches else ''
                    with ui.element('div').classes(classes):
                        with ui.row().classes('s-name-cell').style(f'padding-left:{4 + depth * 14}px'):
                            if directory:
                                ui.button(icon='expand_more' if entry['path'] in self.expanded else 'chevron_right',
                                          on_click=lambda e=entry: self.select(e, True)).props('flat dense color=grey-7 aria-label="Раскрыть папку"').classes('s-tree-toggle')
                                folder_icon()
                            else:
                                ui.element('span').classes('s-tree-spacer')
                                ui.icon({'symlink': 'link', 'mount': 'storage'}.get(entry['kind'], 'insert_drive_file'), size='14px').classes('s-muted shrink-0')
                            ui.button(entry['name'], on_click=lambda e=entry: self.select(e, e['kind'] == 'directory')).props('flat dense no-caps color=dark').classes('s-entry-name')
                            role = entry.get('metadata', {}).get('effective', {}).get('role')
                            if role:
                                ui.label({'primary': 'Осн.', 'copy': 'Копия', 'archive': 'Архив', 'temporary': 'Врем.'}[role]).classes('s-tree-role')
                            status = entry.get('status')
                            if status:
                                ui.icon(STATUS_ICONS.get(status, 'help_outline'), size='13px').classes('shrink-0').style('color:' + STATUS_COLORS.get(status, '#747b72')).props(f'aria-label="{LABELS[status]}"')
                            if directory:
                                for status, number in entry.get('counts', {}).items():
                                    if number:
                                        ui.label(str(number)).classes('pane-count').style('color:' + STATUS_COLORS.get(status, '#747b72'))
                        modified = entry.get('modified_at')
                        if not modified and entry.get('mtime_ns'):
                            modified = datetime.fromtimestamp(entry['mtime_ns'] / 1e9, timezone.utc).isoformat()
                        ui.label(self.workspace.format_date(modified)).classes('s-entry-cell')
                        size = entry.get('size')
                        ui.label(self.workspace.format_bytes(size) if size is not None and entry['kind'] == 'file' else '—').classes('s-entry-cell s-entry-size')
                        kind = {'directory': 'Папка', 'symlink': 'Ссылка', 'mount': 'Том', 'special': 'Особый'}.get(entry['kind'])
                        ui.label(kind or PurePosixPath(entry['name']).suffix[1:].upper() or 'Файл').classes('s-entry-cell')
                    if directory and entry['path'] in self.expanded:
                        branch(entry['path'], depth + 1)
                remaining = data.get('total', len(entries)) - len(data.get('entries', [])) if self.scan else len(entries) - limit
                if remaining > 0:
                    ui.button(f'Показать ещё… ({remaining})', on_click=lambda p=path: self.more(p)).props('flat dense no-caps color=dark').classes('ml-5')

            branch(self.root_path, 0)


class StorageWorkspace:
    def __init__(self, request, format_bytes, format_date):
        self.request, self.format_bytes, self.format_date = request, format_bytes, format_date
        self.volumes = []
        self.active_index = 0
        self.report = None
        self.job_id = None
        self.last_marker = None
        self.editing = False
        self.match_generation = 0
        self.current_matches = []
        ui.add_head_html('<meta name="color-scheme" content="light">')
        ui.add_css(CSS + WORKSPACE_CSS)
        with ui.row().classes('s-header w-full items-center justify-between no-wrap'):
            with ui.row().classes('items-center gap-7'):
                ui.label('media.actu').classes('s-brand')
                with ui.row().classes('items-center gap-1'):
                    ui.link('Хранилища', '/').classes('s-nav active')
                    ui.link('Медиа', '/media').classes('s-nav')
            with ui.row().classes('items-center gap-2 s-readonly'):
                ui.icon('lock_outline', size='15px').classes('s-muted')
                ui.label('Данные только для чтения').classes('s-muted text-xs')
        with ui.row().classes('commander-intro w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label('Хранилища').classes('s-title')
                self.overview = ui.label('Загрузка томов M4…').classes('s-muted text-sm')
            with ui.row().classes('items-center gap-2'):
                ui.button('Найти NAS', icon='lan', on_click=lambda: show_network_dialog(request, format_date, self.refresh_volumes)).props('outline no-caps color=green-9')
                self.refresh_button = ui.button('Обновить тома', icon='refresh', on_click=lambda: self.refresh_volumes(True)).props('outline no-caps color=dark')
        with ui.column().classes('s-panel workspace-operations'):
            with ui.row().classes('w-full items-center justify-between gap-2'):
                with ui.row().classes('items-center gap-2'):
                    self.start_button = ui.button('Сверить левую → правую', icon='compare_arrows', on_click=self.start_comparison).props('unelevated no-caps color=green-9')
                    self.refresh_lists = ui.checkbox('Обновить списки с дисков', value=False).props('dense size=xs').classes('text-xs')
                    ui.button('Свойства', icon='info_outline', on_click=lambda: self.show_properties(self.panes[self.active_index])).props('flat dense no-caps color=dark')
                self.history = ui.select({}, label='История сверок', on_change=self.history_changed).props('outlined dense clearable').classes('workspace-history')
            self.scopes_label = ui.label('Выбери том и папку в каждой панели.').classes('workspace-scopes w-full')
            with ui.row().classes('w-full items-center justify-between gap-2') as self.progress_row:
                self.phase_label = ui.label('Готово к сверке имён').classes('text-xs s-muted')
                with ui.row().classes('gap-1 items-center'):
                    self.pause_button = ui.button('Остановить', icon='pause', on_click=lambda: self.control('pause')).props('flat dense no-caps color=dark')
                    self.resume_button = ui.button('Продолжить', icon='play_arrow', on_click=lambda: self.control('resume')).props('flat dense no-caps color=green-9')
                    self.browse_button = ui.button('К просмотру дисков', icon='folder_open', on_click=self.browse).props('flat dense no-caps color=dark')
                    self.journal_button = ui.button('Журнал', icon='receipt_long', on_click=self.show_journal).props('flat dense no-caps color=dark')
            self.progress = ui.linear_progress(value=0, show_value=False).props('color=green-8').classes('w-full')
            self.summary = ui.label('Сверка использует сохранённые списки; отсутствующие списки будут собраны. Содержимое файлов не читается.').classes('workspace-summary')
            self.results = ui.row().classes('workspace-results w-full')
        with ui.element('div').classes('commander-layout') as self.layout:
            with ui.column().classes('s-panel commander-sidebar w-full gap-0'):
                with ui.column().classes('s-panel-head w-full gap-2'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label('ТОМА').classes('s-caption')
                        self.volume_count = ui.label('—').classes('s-muted text-xs')
                    self.active_select = ui.toggle({0: 'Слева', 1: 'Справа'}, value=0, on_change=lambda e: self.set_active(e.value)).props('no-caps dense color=grey-3 text-color=dark toggle-color=green-8').classes('w-full')
                    self.active_hint = ui.label('Открыть в левой панели').classes('s-muted text-xs')
                self.volume_list = ui.column().classes('s-volumes w-full p-2 gap-0')
                with ui.expansion('Архив', icon='archive', value=False).props('dense').classes('s-volume-archive w-full') as self.archive:
                    self.archive_list = ui.column().classes('s-archive-volumes w-full p-2 gap-0')
                with ui.column().classes('px-3 py-3 gap-1'):
                    ui.label('Нажми на панель, затем выбери том.').classes('s-muted text-xs')
                    ui.link('Системная медиатека Photos →', '/media').classes('text-xs text-green-900 no-underline')
            self.panes = [BrowserPane(self, index) for index in range(2)]
        self.set_active(0)
        self.render_progress()

    @staticmethod
    def error_text(error):
        if hasattr(error, 'response'):
            try:
                return str(error.response.json().get('detail') or error)
            except ValueError:
                pass
        return str(error)

    def notice(self, error):
        ui.notify(self.error_text(error), type='negative')

    def capacity_text(self, volume):
        capacity = volume.get('capacity')
        if not capacity:
            return 'Объём и занятое место пока неизвестны'
        text = f"Занято {self.format_bytes(capacity['used_bytes'])} из {self.format_bytes(capacity['total_bytes'])}"
        text += f" · {capacity['used_bytes'] / capacity['total_bytes'] * 100:.0f}%"
        return text + (' · ранее' if volume.get('capacity_cached') else '')

    def set_active(self, index):
        if index not in (0, 1):
            return
        self.active_index = index
        if self.active_select.value != index:
            self.active_select.set_value(index)
        self.active_hint.text = 'Открыть в левой панели' if index == 0 else 'Открыть в правой панели'
        for pane in getattr(self, 'panes', []):
            pane.container.classes(add='active-pane' if pane.index == index else '', remove='' if pane.index == index else 'active-pane')
        self.render_volumes()

    def render_volumes(self):
        self.volume_list.clear()
        self.archive_list.clear()
        active = [v for v in self.volumes if not archived(v)]
        offline = [v for v in self.volumes if archived(v)]
        online = sum(v['availability'] == 'online' for v in self.volumes)
        self.overview.text = f'Томов: {len(self.volumes)} · подключено: {online} · в архиве: {len(offline)}'
        self.volume_count.text = str(len(active))
        self.archive.text = f'Архив · {len(offline)}'
        self.archive.set_visibility(bool(offline))
        selected = self.panes[self.active_index].volume_id if getattr(self, 'panes', []) else None

        def groups(items):
            grouped = {}
            for volume in items:
                group = volume.get('group') or {'id': volume['kind'], 'name': 'Сетевые тома' if volume['kind'] == 'network' else 'M4', 'kind': 'network' if volume['kind'] == 'network' else 'local'}
                grouped.setdefault(group['id'], {'details': group, 'volumes': []})['volumes'].append(volume)
            for group in sorted(grouped.values(), key=lambda g: (g['details']['kind'] == 'local', g['details']['name'].casefold())):
                with ui.row().classes('s-volume-group w-full items-center no-wrap'):
                    ui.icon('dns' if group['details']['kind'] == 'network' else 'computer', size='15px')
                    ui.label(group['details']['name']).classes('grow truncate')
                    ui.label(str(len(group['volumes']))).classes('s-muted font-normal')
                for volume in group['volumes']:
                    role = volume['metadata']['effective'].get('role')
                    channel = bool(volume.get('marker_id') and volume.get('share_name'))
                    classes = 's-volume-row' + (' with-channel' if channel else '') + (' chosen' if volume['id'] == selected else '')
                    with ui.button(on_click=lambda v=volume: self.panes[self.active_index].show_volume(v['id'])).props('flat no-caps color=dark').classes(classes).tooltip(volume_label(volume) + ' · ' + self.capacity_text(volume)):
                        ui.icon('circle', size='7px').classes('shrink-0 ' + {'online': 'text-green-700', 'offline': 'text-grey-5', 'unknown': 'text-amber-700'}[volume['availability']])
                        with ui.column().classes('gap-0 flex-1 min-w-0'):
                            with ui.row().classes('w-full items-center no-wrap gap-1'):
                                ui.label(volume_label(volume, False)).classes('s-volume-name')
                                if volume.get('removable'):
                                    ui.label('Сменный').classes('s-volume-role s-volume-removable')
                                if role:
                                    ui.label({'primary': 'Осн.', 'copy': 'Копия', 'archive': 'Архив', 'temporary': 'Врем.'}[role]).classes('s-volume-role')
                            if channel:
                                ui.label(volume['share_name']).classes('s-volume-channel')
                            ui.label(self.capacity_text(volume)).classes('s-volume-capacity')
        with self.volume_list:
            if not active:
                ui.label('Нет активных томов.' if self.volumes else 'Пока нет сохранённых томов.').classes('s-muted text-sm p-3')
            groups(active)
        with self.archive_list:
            groups(offline)

    async def refresh_volumes(self, force=False):
        self.refresh_button.disable()
        try:
            data = await self.request('GET', '/api/storage/volumes', params={'refresh': force}, timeout=45)
            self.volumes = data['volumes']
            self.render_volumes()
            for pane in self.panes:
                pane.update_header()
                if pane.volume_id:
                    pane.render()
            self.update_scopes()
            if data.get('error'):
                ui.notify('Подключение томов не удалось обновить. Показаны сохранённые сведения.', type='warning')
        except Exception as error:
            self.overview.text = 'Нет соединения с Core M4'
            self.notice(error)
        finally:
            self.refresh_button.enable()

    def update_scopes(self):
        labels = []
        valid = True
        for pane in self.panes:
            scope = pane.scope()
            valid = valid and bool(scope)
            if scope:
                labels.append(volume_label(pane.volume) + (' /' + scope['path'] if scope['path'] else ' /'))
            else:
                labels.append('Выбери том и папку')
        self.scopes_label.text = 'Слева: ' + labels[0] + '  →  Справа: ' + labels[1]
        running = self.report and self.report['state'] in ('running', 'pausing')
        self.start_button.set_enabled(bool(valid and not running))

    async def load(self, source='', path='', job=''):
        await self.refresh_volumes()
        active = [v for v in self.volumes if not archived(v) and v.get('identity_status') != 'unverified']
        candidates = active or self.volumes
        if candidates:
            requested = next((v for v in self.volumes if v['id'] == source), None)
            left = requested or next((v for v in candidates if v.get('marker_id') and v.get('mounted')), candidates[0])
            right = next((v for v in candidates if v['name'] == 'Media-copy01' and v['id'] != left['id']),
                         next((v for v in candidates if v['id'] != left['id']), left))
            try:
                initial_path = relative_path(path) if requested else ''
            except ValueError as error:
                self.notice(error)
                initial_path = ''
            await self.panes[0].show_volume(left['id'], initial_path, activate=False)
            await self.panes[1].show_volume(right['id'], activate=False)
        else:
            for pane in self.panes:
                pane.render()
        await self.refresh_history()
        if job:
            await self.choose_job(job)
        self.set_active(0)
        ui.timer(30, self.refresh_volumes)
        ui.timer(3, self.poll)

    async def refresh_history(self):
        try:
            jobs = (await self.request('GET', '/api/storage/comparisons', timeout=45))['jobs']
            self.history.options = {j['id']: self.format_date(j['created_at']) + ' · ' + JOB_STATES.get(j['state'], j['state']) for j in jobs}
            self.history.update()
        except Exception as error:
            self.notice(error)

    async def history_changed(self, event):
        if event.value and event.value != self.job_id:
            await self.choose_job(event.value)
        elif not event.value and self.job_id:
            await self.browse()

    async def choose_job(self, job_id):
        try:
            report = await self.request('GET', f'/api/storage/comparisons/{job_id}', timeout=45)
            await self.apply_report(report)
        except Exception as error:
            self.notice(error)

    async def apply_report(self, report):
        self.report, self.job_id = report, report['id']
        self.history.set_value(self.job_id)
        source = next(s for s in report['scans'] if s['side'] == 'source')
        targets = [s for s in report['scans'] if s['side'] == 'target']
        target = next((s for s in targets if s['volume_id'] == self.panes[1].volume_id), targets[0])
        for pane, scan in zip(self.panes, [source, target]):
            await pane.show_volume(scan['volume_id'], scan['root_path'], scan=scan, job_id=self.job_id, activate=False)
        self.last_marker = self.report_marker(report)
        self.render_progress()
        await self.refresh_matches()

    async def start_comparison(self):
        left, right = [p.scope() for p in self.panes]
        if not left or not right:
            ui.notify('Выбери подтверждённый том и папку в каждой панели.', type='warning')
            return
        self.start_button.disable()
        try:
            created = await self.request('POST', '/api/storage/comparisons',
                                         json={'source': left, 'targets': [right], 'reuse_index': not bool(self.refresh_lists.value)}, timeout=45)
            await self.refresh_history()
            await self.apply_report(created)
        except Exception as error:
            self.notice(error)
        finally:
            self.update_scopes()

    async def browse(self):
        self.job_id, self.report, self.last_marker = None, None, None
        self.history.set_value(None)
        self.current_matches.clear()
        self.results.clear()
        for pane in self.panes:
            if pane.scan:
                await pane.show_volume(pane.volume_id, pane.root_path, activate=False)
        self.render_progress()

    @staticmethod
    def report_marker(report):
        return report['state'], report['phase'], tuple((s['id'], s['state']) for s in report['scans'])

    async def poll(self):
        if not self.job_id or (self.report and self.report['state'] == 'completed'):
            return
        job_id = self.job_id
        try:
            report = await self.request('GET', f'/api/storage/comparisons/{job_id}', timeout=45)
            if self.job_id != job_id:
                return
            marker = self.report_marker(report)
            self.report = report
            self.render_progress()
            if marker != self.last_marker:
                self.last_marker = marker
                scans = {s['id']: s for s in report['scans']}
                for pane in self.panes:
                    if pane.job_id == job_id and pane.scan:
                        pane.scan = scans[pane.scan['id']]
                        for path in list(pane.folders) or [pane.root_path]:
                            await pane.load_folder(path)
                        pane.render()
                await self.refresh_matches()
        except Exception as error:
            self.phase_label.text = 'Нет связи с Core: ' + self.error_text(error)

    def render_progress(self):
        report = self.report
        running = bool(report and report['state'] in ('running', 'pausing'))
        self.pause_button.set_visibility(running)
        self.pause_button.set_enabled(bool(report and report['state'] == 'running'))
        legacy = bool(report and report['mode'] != 'names')
        self.resume_button.set_visibility(bool(report and (report['state'] in ('paused', 'failed') or (legacy and not running))))
        self.resume_button.text = 'Сверить по именам' if legacy else 'Продолжить'
        self.browse_button.set_visibility(bool(report))
        self.journal_button.set_visibility(bool(report))
        self.progress.set_visibility(bool(report))
        self.progress_row.set_visibility(bool(report))
        self.layout.classes(add='comparing' if report else '', remove='' if report else 'comparing')
        if not report:
            self.phase_label.text = 'Готово к сверке имён'
            self.summary.text = 'Сверка использует сохранённые списки; отсутствующие списки будут собраны. Содержимое файлов не читается.'
            self.update_scopes()
            return
        phase = {'index': 'Подготовка списков', 'names': 'Сопоставление имён', 'hash': 'Прежний отчёт по содержимому', 'done': 'Сверка завершена'}.get(report['phase'], report['phase'])
        if legacy:
            phase = 'Прежний отчёт по содержимому'
        self.phase_label.text = phase + ' · ' + JOB_STATES.get(report['state'], report['state'])
        history_label = self.format_date(report['created_at']) + ' · ' + JOB_STATES.get(report['state'], report['state'])
        if self.job_id in self.history.options and self.history.options[self.job_id] != history_label:
            self.history.options[self.job_id] = history_label
            self.history.update()
        self.progress.value = 1 if report['state'] == 'completed' else 0
        if running:
            self.progress.props('indeterminate')
        else:
            self.progress.props(remove='indeterminate')
        if running:
            self.summary.text = report.get('current_path') or report.get('message') or phase
        else:
            counts = ' · '.join(f'{LABELS.get(status, status)}: {number}' for status, number in report.get('counts', {}).items())
            self.summary.text = (counts + ' · ' if counts else '') + 'Результат относится к сохранённым спискам от ' + self.format_date(report['created_at'])
        self.update_scopes()

    async def control(self, action):
        if not self.job_id:
            return
        try:
            updated = await self.request('POST', f'/api/storage/comparisons/{self.job_id}/{action}', timeout=45)
            if updated['id'] != self.job_id:
                await self.refresh_history()
                await self.apply_report(updated)
            else:
                self.report = updated
                self.render_progress()
        except Exception as error:
            self.notice(error)

    async def refresh_matches(self):
        self.match_generation += 1
        generation = self.match_generation
        self.current_matches = []
        self.results.clear()
        left, right = self.panes
        right.matches.clear()
        if not self.job_id or not left.scan or left.scan['side'] != 'source' or left.job_id != self.job_id:
            right.render()
            return
        try:
            data = await self.request('GET', f'/api/storage/comparisons/{self.job_id}/detail',
                                      params={'path': left.path}, timeout=45)
        except Exception:
            right.render()
            return
        if generation != self.match_generation:
            return
        for match in data.get('matches', []):
            if 'scan_id' not in match:
                scans = [s for s in self.report['scans'] if s['side'] == 'target' and s['volume_id'] == match['volume_id']
                         and (not s['root_path'] or match['path'] == s['root_path'] or match['path'].startswith(s['root_path'] + '/'))]
                if not scans:
                    continue
                match = dict(match, scan_id=max(scans, key=lambda s: len(s['root_path']))['id'], kind='file')
            self.current_matches.append(match)
        right.matches = {m['path'] for m in self.current_matches if right.scan and m.get('scan_id') == right.scan['id']}
        right.render()
        with self.results:
            entry = data['entry']
            status = entry.get('status')
            if status:
                ui.label(LABELS[status]).classes('text-xs').style('color:' + STATUS_COLORS.get(status, '#747b72'))
            ui.label(('Папка: ' if entry['kind'] == 'directory' else 'Файл: ') + entry['name']).classes('text-xs s-muted')
            if self.current_matches:
                ui.button(f"Совпадения: {len(self.current_matches)}", icon='find_in_page', on_click=self.show_matches).props('outline dense no-caps color=green-9')
            else:
                ui.label('Совпадений в выбранной области нет' if self.report['state'] == 'completed' else 'Сверка ещё выполняется').classes('text-xs s-muted')

    async def show_matches(self):
        matches = list(self.current_matches)
        with ui.dialog() as dialog, ui.card().classes('w-[700px] max-w-full p-5 gap-3'):
            ui.label('Совпадения имён').classes('text-lg font-semibold')
            ui.label('Выбери путь, чтобы открыть его в правой панели.').classes('text-xs s-muted')
            with ui.column().classes('w-full gap-1 max-h-[60vh] overflow-auto'):
                for match in matches:
                    ui.button(match['volume_name'] + ' /' + match['path'], on_click=lambda m=match: dialog.submit(m)).props('flat dense no-caps color=dark').classes('w-full text-left justify-start')
            ui.button('Закрыть', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
        match = await dialog
        if not match:
            return
        scan = next(s for s in self.report['scans'] if s['id'] == match['scan_id'])
        root = match['path'] if match['kind'] == 'directory' else relative_path(str(PurePosixPath(match['path']).parent))
        await self.panes[1].show_volume(scan['volume_id'], root, scan=scan, job_id=self.job_id)
        if match['kind'] != 'directory':
            await self.panes[1].select(match)

    async def show_journal(self):
        if not self.job_id:
            return
        job_id = self.job_id
        try:
            events = (await self.request('GET', f'/api/storage/comparisons/{job_id}/events', timeout=45))['events']
            with ui.dialog() as dialog, ui.card().classes('w-[850px] max-w-full p-5 gap-3'):
                ui.label('Журнал сверки').classes('text-lg font-semibold')
                container = ui.column().classes('w-full max-h-[65vh] overflow-auto gap-2')
                cursor = events[-1]['id'] if events else None

                def append(items):
                    with container:
                        for event in items:
                            ui.label(self.format_date(event['at']) + ' · ' + event['message']).classes('text-sm')
                            if event.get('path'):
                                ui.label(event['path']).classes('s-path s-muted')

                async def older():
                    nonlocal cursor
                    more.disable()
                    try:
                        items = (await self.request('GET', f'/api/storage/comparisons/{job_id}/events',
                                                    params={'before': cursor}, timeout=45))['events']
                        append(items)
                        cursor = items[-1]['id'] if items else cursor
                        more.set_visibility(len(items) == 100)
                    except Exception as error:
                        self.notice(error)
                    finally:
                        more.enable()

                append(events)
                more = ui.button('Показать более ранние записи', on_click=older).props('outline no-caps color=dark')
                more.set_visibility(len(events) == 100)
                ui.button('Закрыть', on_click=dialog.close).props('flat no-caps color=dark')
            dialog.open()
        except Exception as error:
            self.notice(error)

    async def show_properties(self, pane):
        volume = pane.volume
        if not volume:
            return
        self.set_active(pane.index)
        try:
            data = await self.request('GET', f'/api/storage/volumes/{volume["id"]}/directory',
                                      params={'path': pane.path if pane.kind == 'directory' else '', 'refresh': False}, timeout=45)
            metadata = data['metadata'] if pane.kind == 'directory' else (pane.entry or {}).get('metadata', volume['metadata'])
        except Exception as error:
            self.notice(error)
            return
        with ui.dialog() as dialog, ui.card().classes('w-[450px] max-w-full p-5 gap-4'):
            ui.label('Свойства · ' + pane.title.lower() + ' панель').classes('s-caption')
            ui.label(PurePosixPath(pane.path).name if pane.path else volume_label(volume)).classes('text-lg font-semibold break-words')
            ui.label(pane.path or volume.get('network_url') or volume['mount_path']).classes('s-path s-muted')
            if volume.get('removable'):
                ui.label('Сменный носитель').classes('s-tag purpose')
            capacity = volume.get('capacity')
            if capacity:
                ui.label('Место на томе').classes('s-caption')
                with ui.element('div').classes('workspace-property-grid'):
                    for title, key in [('Объём', 'total_bytes'), ('Занято', 'used_bytes'), ('Свободно', 'free_bytes')]:
                        ui.label(title).classes('s-muted')
                        ui.label(self.format_bytes(capacity[key]))
                prefix = 'Последние сведения' if volume.get('capacity_cached') else 'Обновлено'
                ui.label(prefix + ': ' + self.format_date(capacity['checked_at'])).classes('text-xs s-muted')
            if volume.get('identity_error'):
                ui.label(volume['identity_error']).classes('s-error w-full')
            if volume.get('marker_id'):
                ui.label('ID: ' + volume['marker_id']).classes('s-path s-muted')
            if volume.get('share_name'):
                ui.label('Ресурс NAS: ' + volume['share_name']).classes('text-xs s-muted')
            values = metadata['effective']
            with ui.element('div').classes('workspace-property-grid'):
                for title, field, labels in [('Назначение', 'purpose', PURPOSES), ('Хранение', 'role', ROLES)]:
                    ui.label(title).classes('s-muted')
                    ui.label(labels[values[field]])
            for key, label in FLAGS.items():
                if values.get(key):
                    ui.label(label).classes('s-tag flag')
            if metadata['own'].get('comment'):
                ui.label(metadata['own']['comment']).classes('text-sm break-words')
            if not volume.get('mounted') and volume.get('network_url'):
                ui.button('Подключить на M4', icon='lan', on_click=lambda: self.connect(volume['id'])).props('outline no-caps color=dark')
            with ui.row().classes('w-full justify-end gap-2'):
                if pane.kind == 'directory' and volume.get('identity_status') != 'unverified':
                    ui.button('Изменить роли', on_click=lambda: dialog.submit('edit')).props('outline no-caps color=green-9')
                ui.button('Закрыть', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
        if await dialog == 'edit':
            await self.edit_metadata(pane, metadata)

    async def edit_metadata(self, pane, metadata):
        volume_id, path = pane.volume_id, pane.path
        inherit = '__inherit__'
        own = metadata['own']
        self.editing = True
        with ui.dialog() as dialog, ui.card().classes('w-[460px] max-w-full p-5 gap-4'):
            ui.label('Роли и назначение').classes('text-lg font-semibold')
            ui.label(PurePosixPath(path).name if path else volume_label(pane.volume)).classes('text-sm s-muted break-words')
            default = 'От родительской папки / тома' if path else 'Не назначено'
            purpose = ui.select({inherit: default, **PURPOSES}, value=own['purpose'] if own['purpose'] is not None else inherit, label='Что здесь хранится').props('outlined dense').classes('w-full')
            role = ui.select({inherit: default, **ROLES}, value=own['role'] if own['role'] is not None else inherit, label='Роль хранения').props('outlined dense').classes('w-full')
            flags = {}
            for key, label in FLAGS.items():
                value = inherit if own[key] is None else 'yes' if own[key] else 'no'
                flags[key] = ui.select({inherit: default if path else 'Не задано', 'yes': 'Да', 'no': 'Нет'}, value=value, label=label).props('outlined dense').classes('w-full')
            comment = ui.textarea('Комментарий', value=own.get('comment') or '').props('outlined autogrow maxlength=4000').classes('w-full')
            ui.label('Сохраняются только отметки в базе приложения.').classes('text-xs s-muted')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button('Сохранить отметки', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
        try:
            if not await dialog:
                return
            payload = {'path': path, 'purpose': None if purpose.value == inherit else purpose.value,
                       'role': None if role.value == inherit else role.value, 'comment': comment.value or ''}
            payload.update({key: None if control.value == inherit else control.value == 'yes' for key, control in flags.items()})
            await self.request('PATCH', f'/api/storage/volumes/{volume_id}/metadata', json=payload)
            await self.refresh_volumes()
            if pane.volume_id == volume_id:
                for folder in list(pane.folders):
                    await pane.load_folder(folder, refresh=False)
                pane.render()
            ui.notify('Отметки сохранены', type='positive')
        except Exception as error:
            self.notice(error)
        finally:
            self.editing = False

    async def register_disk(self, pane):
        volume = pane.volume
        if not volume:
            return
        with ui.dialog() as dialog, ui.card().classes('w-[460px] max-w-full p-5 gap-4'):
            ui.label('Регистрация сменного диска').classes('text-lg font-semibold')
            ui.label(volume.get('network_url') or volume['mount_path']).classes('s-path s-muted')
            name = ui.input('Имя диска', placeholder='Например, Архив фото 2 ТБ').props('outlined dense maxlength=120').classes('w-full')
            ui.label('На диск будет один раз записан файл .media-actu-volume.json с постоянным ID и именем. По нему приложение узнает диск при следующем подключении.').classes('s-note')
            ui.label('Прежняя история usbshare останется отдельной записью в архиве.').classes('text-xs s-muted')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button('Создать ID на диске', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
        if not await dialog:
            return
        try:
            registered = await self.request('POST', f'/api/storage/volumes/{volume["id"]}/register-removable',
                                             json={'name': (name.value or '').strip()}, timeout=45)
            await self.refresh_volumes(True)
            await pane.show_volume(registered['id'])
            ui.notify('Диск зарегистрирован', type='positive')
        except Exception as error:
            self.notice(error)

    async def connect(self, volume_id):
        try:
            await self.request('POST', f'/api/storage/volumes/{volume_id}/connect')
            ui.notify('Заверши подключение в Finder на M4', type='info')
        except Exception as error:
            self.notice(error)


def register_workspace_page(request, format_bytes, format_date):
    @ui.page('/')
    async def workspace_page(source: str = '', path: str = '', job: str = ''):
        workspace = StorageWorkspace(request, format_bytes, format_date)
        await workspace.load(source, path, job)
