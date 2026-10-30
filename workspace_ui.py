"""Two independent storage trees and operations in one workspace."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
import json
from pathlib import PurePosixPath

from nicegui import ui

from comparison_tree_ui import ComparisonTree
from copy_groups_ui import CopyGroupsUI
from media_manager.comparison import LABELS, NAME_STATUSES
from media_manager.storage import FLAGS, PURPOSES, relative_path
from network_ui import show_network_dialog
from paired_workspace_ui import PairedWorkspace
from storage_ui import CSS, FOLDER_CLICK_JS, folder_icon


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
.commander-layout { display:grid; grid-template-columns:220px minmax(0,1fr) minmax(0,1fr) 260px; gap:12px; padding:0 26px 26px; width:100%; align-items:start; }
.commander-trees { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); grid-column:2 / span 2; gap:12px; position:relative; min-width:0; }
.pane-link { position:absolute; z-index:3; top:14px; left:50%; transform:translateX(-50%); width:28px; height:28px; display:flex; align-items:center; justify-content:center; border:1px solid #9bb491; border-radius:50%; background:#edf3e7; color:#427644; }
.commander-trees.linked .commander-pane { border-color:#b0c4a7; }
.commander-trees.linked .commander-pane.active-pane { border-color:#75986c; }
.commander-pane { border:2px solid var(--s-line); height:calc(100vh - 180px); min-height:440px; }
.commander-pane.active-pane { border-color:#8ba984; }
.commander-pane .s-panel-head { padding:8px 10px; gap:5px; }
.commander-pane .s-panel-head, .commander-pane .s-tree-toolbar, .commander-pane .pane-status, .commander-pane .workspace-filter { flex-shrink:0; }
.commander-pane .s-tree { flex:1; min-height:180px; max-height:none; width:100%; }
.commander-pane .s-list-grid { grid-template-columns:minmax(150px,1fr) 112px 56px 56px; min-width:374px; }
.commander-trees.names-comparison .commander-pane:first-child .s-list-grid { grid-template-columns:minmax(0,1fr); min-width:0; }
.commander-trees.names-comparison .commander-pane:first-child .s-entry-cell,
.commander-trees.names-comparison .commander-pane:first-child .s-tree-heading > div:not(:first-child) { display:none; }
.commander-pane .pane-heading { font-size:13px; font-weight:650; color:#71816b; min-height:24px; padding:0 5px; }
.pane-location { display:flex; align-items:center; gap:10px; width:100%; min-width:0; }
.pane-volume { flex:0 0 clamp(148px,28%,180px); width:clamp(148px,28%,180px); min-width:0; font-size:12px; }
.pane-volume .q-field__control, .pane-volume .q-field__marginal { height:34px; min-height:34px; }
.pane-volume .q-field__native { padding:0; min-height:34px; }
.pane-volume .q-field__native > span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pane-volume .q-field__append { padding-left:4px; }
.pane-path { display:flex; flex:1; align-items:center; gap:5px; min-width:0; flex-wrap:nowrap; overflow-x:auto; overflow-y:hidden; padding:3px 0 5px; scrollbar-width:thin; }
.pane-path-prefix, .pane-path-slash { flex-shrink:0; white-space:nowrap; color:#526b83; font-size:13px; }
.pane-crumb { flex-shrink:0; min-height:28px; padding:2px 7px; border:1px solid #c7dced; border-radius:5px; background:#eaf4fc; color:#285b80; font-size:13px; line-height:22px; white-space:nowrap; }
.pane-crumb .q-btn__content { flex-wrap:nowrap; gap:4px; }
.pane-crumb .q-icon { font-size:15px; margin:0; }
.pane-crumb.current { background:#d8eafa; border-color:#a8c8e2; color:#164b74; font-weight:650; }
.pane-crumb.context { display:flex; align-items:center; gap:4px; }
.pane-crumb.q-btn:hover { background:#d7eafb; }
.pane-crumb:focus-visible { outline:2px solid #6ca4d0; outline-offset:1px; }
.pane-status { padding:7px 11px; border-top:1px solid var(--s-line); font-size:11px; min-height:31px; color:var(--s-muted); }
.pane-result { flex-shrink:0; font-size:10px; max-width:150px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.pane-count { font-size:10px; padding:0 3px; background:#edf1e9; border-radius:3px; }
.pane-match { box-shadow:inset 3px 0 #6e9b64; }
.match-entry { display:flex; align-items:center; gap:3px; padding-right:6px; width:100%; }
.match-entry .s-entry-name { flex:1; min-width:0; }
.match-location { flex:0 1 48%; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; text-align:right; font-size:10px; color:var(--s-muted); }
.workspace-operation-body { padding:12px; gap:12px; }
.workspace-operation-body .q-btn { max-width:100%; }
.workspace-start .q-btn__content { flex-wrap:nowrap; }
.workspace-start .q-icon { font-size:18px; }
.workspace-history { width:100%; font-size:11px; }
.workspace-history .q-field__native > span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.workspace-operation-title { font-size:13px; font-weight:650; }
.workspace-summary { font-size:11px; color:var(--s-muted); width:100%; }
.workspace-counts { width:100%; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:5px 8px; font-size:11px; }
.workspace-results { gap:6px; flex-wrap:wrap; align-items:center; }
.workspace-results .q-btn { font-size:11px; min-height:24px; padding:2px 7px; }
.workspace-scopes { color:#667363; font-size:12px; overflow-wrap:anywhere; }
.workspace-filter { min-width:170px; font-size:11px; }
.workspace-property-grid { display:grid; grid-template-columns:1fr auto; gap:5px 16px; width:100%; font-size:13px; }
.commander-sidebar .s-volumes { max-height:calc(100vh - 310px); }
.commander-sidebar .s-volume-row { padding-left:6px; padding-right:6px; }
.commander-sidebar .s-volume-capacity { font-size:10px; }
.workspace-operations { max-height:calc(100vh - 180px); overflow-y:auto; }
.copy-section { border-bottom:1px solid var(--s-line); }
.copy-section > .q-expansion-item__container > .q-item { min-height:48px; padding:10px 14px; font-size:11px; color:#687466; font-weight:650; }
.copy-section .q-item__section--avatar { min-width:24px; padding-right:7px; }
.copy-section .q-item__section--avatar .q-icon { font-size:17px; }
.copy-group-list { max-height:calc(100vh - 300px); overflow:auto; padding:4px; }
.copy-bookmark-group { padding:3px 0 7px; border-bottom:1px solid var(--s-line); }
.copy-bookmark { padding:6px; border:1px solid transparent; border-radius:6px; }
.copy-bookmark .q-btn__content { width:100%; align-items:flex-start; flex-direction:column; gap:2px; }
.copy-bookmark.chosen { background:#edf3e7; border-color:#b7c8b0; }
.copy-bookmark-name { flex:1; min-width:0; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; text-align:left; font-size:12px; }
.copy-place { width:100%; text-align:left; font-size:10px; color:var(--s-muted); overflow-wrap:anywhere; line-height:1.4; font-weight:400; }
.copy-link { display:flex; flex-wrap:nowrap; align-items:center; gap:6px; margin-left:12px; padding:2px 4px; width:calc(100% - 12px); min-height:24px; color:#637b91; text-decoration:none; }
.copy-link.chosen { color:#365f43; font-weight:600; }
.copy-link .copy-label { padding:0; background:transparent; color:inherit; }
.copy-link-name { flex:1; min-width:0; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; font-size:11px; line-height:20px; }
.copy-link:hover .copy-link-name { text-decoration:underline; }
.copy-link:focus-visible { outline:1px solid #9cb8d5; outline-offset:-1px; }
.copy-label { flex-shrink:0; font-size:10px; line-height:16px; padding:0 4px; border-radius:3px; background:#edf1f7; color:#536a89; font-family:ui-monospace,Menlo,monospace; white-space:nowrap; }
.copy-label.main { color:#3f6744; background:#eaf2e6; }
.s-tree-role.copy-label { max-width:none; }
.commander-pane.folder-labels .s-list-grid { grid-template-columns:minmax(220px,1fr) 112px 56px 56px; min-width:444px; }
@media(max-width:1450px) {
 .commander-layout { grid-template-columns:220px minmax(0,1fr) minmax(0,1fr) 240px; gap:10px; padding:0 16px 20px; }
 .commander-trees { gap:10px; }
 .commander-intro { padding:12px 16px 10px; }
}
@media(max-width:1100px) {
 .commander-layout { grid-template-columns:180px minmax(300px,1fr) minmax(300px,1fr) 240px; overflow-x:auto; }
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
        self.rows = {}
        self.folder_entries = {}
        self.generation = 0
        self.filter_value = ''
        self.path_signature = None
        with ui.column().classes('s-panel commander-pane w-full gap-0') as self.container:
            self.container.on('click', lambda: workspace.set_active(index))
            self.container.on('focusin', lambda: workspace.set_active(index))
            with ui.column().classes('s-panel-head w-full gap-2'):
                workspace.property_menu('Свойства диска', lambda: workspace.show_properties(self.volume_id))
                with ui.row().classes('w-full items-center justify-between gap-1 no-wrap'):
                    self.heading = ui.button(self.title + ' панель', on_click=self.activate_heading).props('flat dense no-caps color=green-9').classes('pane-heading')
                    with ui.row().classes('gap-0 no-wrap') as self.navigation:
                        ui.button(icon='arrow_upward', on_click=self.go_parent).props('flat dense round color=dark').props(f'aria-label="На уровень выше {self.title.lower()}"')
                        ui.button(icon='vertical_align_top', on_click=self.go_root).props('flat dense round color=dark').props(f'aria-label="Корень {self.title.lower()} панели"')
                        ui.button(icon='refresh', on_click=self.refresh).props('flat dense round color=dark').props(f'aria-label="Обновить {self.title.lower()} панель"')
                with ui.element('div').classes('pane-location') as self.location:
                    self.volume_select = ui.select({}, on_change=self.volume_changed).props('outlined dense options-dense').props(
                        'aria-label="Том слева"' if index == 0 else 'aria-label="Том справа"').classes('pane-volume')
                    self.path_bar = ui.element('nav').classes('pane-path').props(
                        'aria-label="Путь левой панели"' if index == 0 else 'aria-label="Путь правой панели"')
            with ui.row().classes('s-tree-toolbar w-full items-center justify-between no-wrap') as self.toolbar:
                self.snapshot_label = ui.label('Просмотр папок').classes('s-muted text-xs')
                self.hidden = ui.checkbox('Скрытые', value=False, on_change=self.hidden_changed).props('dense size=xs').classes('text-xs s-muted')
            options = {'': 'Все результаты', **{s: LABELS[s] for s in NAME_STATUSES}} if index == 0 else {'': 'Все элементы'}
            self.result_filter = ui.select(options, value='', label='Результаты' if index == 0 else 'Список справа',
                                          on_change=self.change_filter).props('outlined dense').classes('workspace-filter mx-2 my-1')
            self.result_filter.set_visibility(False)
            self.tree = ui.column().classes('s-tree gap-0')
            self.tree.on('click', self.folder_clicked, js_handler=FOLDER_CLICK_JS)
            self.footer = ui.label('Том не выбран').classes('pane-status w-full')
        self.comparison = ComparisonTree(self) if index == 1 else None

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
            await self.workspace.open_volume(event.value, self.index)

    def activate_heading(self):
        self.workspace.set_active(self.index)
        if self.index == 1 and self.workspace.report and self.comparison.focus:
            self.comparison.show_matches()

    def hidden_changed(self, event):
        if self.workspace.pair.active and self.workspace.pair.report:
            self.workspace.pair.set_hidden(event.value)
        else:
            self.render()

    async def folder_clicked(self, event):
        entry = self.folder_entries.get(event.args['key'])
        if entry is None:
            return
        with self.workspace.client:
            if self.index == 1 and self.workspace.report:
                entry, scope = entry
                if event.args['double']:
                    await self.comparison.open_folder(entry, scope)
                else:
                    await self.comparison.select(entry, scope)
            elif event.args['double']:
                await self.open_path(entry['path'])
            else:
                await self.select(entry, True)

    def save_browse_state(self):
        return {'volume_id': self.volume_id, 'root_path': self.root_path, 'path': self.path,
                'kind': self.kind, 'entry': self.entry, 'folders': self.folders.copy(),
                'expanded': self.expanded.copy(), 'limits': self.limits.copy(), 'hidden': self.hidden.value}

    def restore_browse_state(self, state):
        self.generation += 1
        self.scan, self.job_id = None, None
        for name in ('volume_id', 'root_path', 'path', 'kind', 'entry', 'folders', 'expanded', 'limits'):
            setattr(self, name, state[name])
        self.filter_value = ''
        self.result_filter.set_value('')
        self.hidden.set_value(state['hidden'])
        self.volume_select.set_value(self.volume_id)
        self.matches.clear()
        if self.comparison:
            self.comparison.reset()
        self.render()

    def update_header(self):
        self.volume_select.options = {
            v['id']: volume_label(v) + (' · архив' if archived(v) else ' · не подтверждён' if v.get('identity_status') == 'unverified' else '')
            for v in self.workspace.volumes
        }
        self.volume_select.update()
        if self.workspace.pair.active:
            self.workspace.pair.update_header(self)
            return
        report = self.workspace.report
        self.heading.text = ('Источник' if self.index == 0 else 'Совпадения') if report else self.title + ' панель'
        self.volume_select.set_enabled(not bool(report))
        self.volume_select.set_visibility(not (report and self.index == 1))
        self.navigation.set_visibility(not (report and self.index == 1))
        if report and self.index == 1:
            self.result_filter.set_visibility(False)
            self.comparison.update_header()
            return
        self.location.set_visibility(True)
        self.path_bar.set_visibility(True)
        self.toolbar.set_visibility(True)
        volume = self.volume
        if not volume:
            self.path_bar.clear()
            self.path_signature = None
            with self.path_bar:
                ui.label('Выбери том').classes('pane-path-prefix')
            return
        self.render_path(self.volume_id, self.path, self.kind,
                         boundary=self.scan['root_path'] if self.scan else '')
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

    def render_path(self, volume_id, path, kind, *, boundary='', navigate=None):
        volume = next((v for v in self.workspace.volumes if v['id'] == volume_id), None)
        if not volume:
            return
        base = (volume['mount_path'] or volume.get('network_url') or volume_label(volume)).rstrip('/') or '/'
        signature = volume_id, base, path, kind, boundary, bool(self.workspace.report)
        if signature == self.path_signature:
            return
        self.path_signature = signature
        self.path_bar.clear()
        navigate = navigate or self.open_path
        prefix, _, root_name = base.rpartition('/')
        crumbs = [(root_name or '/', '', 'directory')]
        parts = PurePosixPath(path).parts if path else ()
        crumbs.extend((name, '/'.join(parts[:i + 1]), kind if i == len(parts) - 1 else 'directory')
                      for i, name in enumerate(parts))
        with self.path_bar:
            if prefix:
                ui.label(prefix + '/').classes('pane-path-prefix')
            for i, (name, relative, entry_kind) in enumerate(crumbs):
                if i:
                    ui.label('/').classes('pane-path-slash').props('aria-hidden=true')
                permitted = not boundary or relative == boundary or relative.startswith(boundary + '/')
                current = relative == path
                classes = 'pane-crumb' + (' current' if current else '')
                if permitted and entry_kind == 'directory':
                    crumb = ui.button(name, icon='folder_open' if current else 'folder',
                                      on_click=lambda p=relative: navigate(p)).props('flat dense no-caps').classes(classes)
                else:
                    with ui.element('span').classes(classes + ' context') as crumb:
                        ui.icon('folder' if entry_kind == 'directory' else 'insert_drive_file', size='15px')
                        ui.label(name)
                if current:
                    crumb.props('aria-current=location')
        # Keep the selected folder visible without scrolling the tree or the page.
        self.workspace.client.run_javascript(f'requestAnimationFrame(() => {{ const bar = getHtmlElement({self.path_bar.id}); if (bar) bar.scrollLeft = bar.scrollWidth; }});')

    async def open_path(self, path):
        path = relative_path(path)
        if self.workspace.pair.active:
            await self.workspace.pair.navigate_path(self.index, path)
            return
        boundary = self.scan['root_path'] if self.scan else ''
        if boundary and path != boundary and not path.startswith(boundary + '/'):
            return
        with self.workspace.client:
            await self.show_volume(self.volume_id, path, scan=self.scan, job_id=self.job_id)
            if self.index == 0:
                await self.workspace.refresh_matches()

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

    async def select(self, entry, toggle=False, *, render=True):
        self.workspace.set_active(self.index)
        self.path, self.kind, self.entry = entry['path'], entry['kind'], entry
        if toggle and self.kind == 'directory':
            if self.path in self.expanded:
                self.expanded.remove(self.path)
            else:
                self.expanded.add(self.path)
                if self.path not in self.folders:
                    await self.load_folder(self.path)
        if render:
            self.render()
        else:
            for path, row in self.rows.items():
                row.classes(add='selected' if path == self.path else '', remove='' if path == self.path else 'selected')
            self.update_header()
        self.workspace.update_scopes()
        if self.index == 0:
            await self.workspace.refresh_matches()

    async def go_root(self):
        if self.workspace.pair.active:
            await self.workspace.pair.navigate_path(self.index, self.workspace.pair.scopes['left' if self.index == 0 else 'right']['path'])
            return
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
        if self.workspace.pair.active:
            relative = self.workspace.pair.relative(self.index, self.path)
            if relative:
                parent = str(PurePosixPath(relative).parent)
                scope = self.workspace.pair.scopes['left' if self.index == 0 else 'right']
                path = scope['path'] + ('/' + parent if parent != '.' else '')
                await self.workspace.pair.navigate_path(self.index, path)
            return
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
        if self.workspace.pair.active and self.workspace.pair.report:
            if self.workspace.pair.report['state'] == 'completed':
                await self.workspace.pair.load_rows(self.workspace.pair.report['id'])
            return
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
        if self.workspace.pair.active and self.workspace.pair.report:
            self.update_header()
            self.folder_entries.clear()
            self.rows.clear()
            self.workspace.pair.render_tree(self)
            return
        labels = any(entry['kind'] == 'directory' and self.workspace.copies.membership(self.volume_id, entry['path'])
                     for data in self.folders.values() for entry in data.get('entries', []))
        self.container.classes(add='folder-labels' if labels else '', remove='' if labels else 'folder-labels')
        self.update_header()
        self.tree.clear()
        self.rows.clear()
        self.folder_entries.clear()
        if self.index == 1 and self.workspace.report:
            with self.tree:
                self.comparison.render()
            return
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
                    if directory:
                        folder_key = json.dumps([self.volume_id, self.job_id, entry['path']], ensure_ascii=False)
                        self.folder_entries[folder_key] = entry
                    classes = 's-entry s-list-grid' + (' alt' if next(row_numbers) % 2 else '')
                    classes += ' selected' if entry['path'] == self.path else ''
                    classes += ' pane-match' if entry['path'] in self.matches else ''
                    with ui.element('div').classes(classes) as row:
                        self.rows[entry['path']] = row
                        row.on('contextmenu', lambda e=entry: self.select(e, render=False))
                        self.workspace.property_menu('Свойства', lambda e=entry: self.workspace.show_properties(self.volume_id, e),
                                                     extra=self.workspace.copies.context_actions(self.volume_id, entry))
                        with ui.row().classes('s-name-cell').style(f'padding-left:{4 + depth * 14}px'):
                            if directory:
                                ui.button(icon='expand_more' if entry['path'] in self.expanded else 'chevron_right',
                                          on_click=lambda e=entry: self.select(e, True)).props('flat dense color=grey-7 aria-label="Раскрыть папку"').classes('s-tree-toggle')
                                folder_icon().props['data-folder-key'] = folder_key
                            else:
                                ui.element('span').classes('s-tree-spacer')
                                ui.icon({'symlink': 'link', 'mount': 'storage'}.get(entry['kind'], 'insert_drive_file'), size='14px').classes('s-muted shrink-0')
                            name_button = ui.button(entry['name'], on_click=None if directory else lambda e=entry: self.select(e)).props('flat dense no-caps color=dark').classes('s-entry-name')
                            if directory:
                                name_button.props['data-folder-key'] = folder_key
                            membership = self.workspace.copies.membership(self.volume_id, entry['path']) if directory else None
                            if membership:
                                ui.label(membership['label']).classes('s-tree-role copy-label' + (' main' if membership['number'] == 0 else ''))
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
        self.client = ui.context.client
        self.volumes = []
        self.active_index = 0
        self.report = None
        self.job_id = None
        self.last_marker = None
        self.editing = False
        self.context_menu_open = False
        self.match_generation = 0
        self.current_matches = []
        self.browse_state = None
        self.browse_active = 0
        self.pair = PairedWorkspace(self)
        self.copies = CopyGroupsUI(self)
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
                ui.label('Оригиналы — только чтение').classes('s-muted text-xs')
        with ui.row().classes('commander-intro w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label('Хранилища').classes('s-title')
                self.overview = ui.label('Загрузка томов M4…').classes('s-muted text-sm')
            with ui.row().classes('items-center gap-2'):
                ui.button('Найти NAS', icon='lan', on_click=lambda: show_network_dialog(request, format_date, self.refresh_volumes)).props('outline no-caps color=green-9')
                self.refresh_button = ui.button('Обновить тома', icon='refresh', on_click=lambda: self.refresh_volumes(True)).props('outline no-caps color=dark')
        with ui.element('div').classes('commander-layout') as self.layout:
            with ui.column().classes('s-panel commander-sidebar w-full gap-0'):
                with ui.expansion('Тома', icon='storage', value=True).props('dense').classes('copy-section w-full') as self.volumes_section:
                    self.volume_list = ui.column().classes('s-volumes w-full p-2 gap-0')
                    with ui.expansion('Архив', icon='archive', value=False).props('dense').classes('s-volume-archive w-full') as self.archive:
                        self.archive_list = ui.column().classes('s-archive-volumes w-full p-2 gap-0')
                    ui.label('Том откроется в выделенном дереве.').classes('s-muted text-xs px-3 py-2')
                self.copies.build_sidebar()
                with ui.column().classes('px-3 py-3 gap-1'):
                    ui.link('Системная медиатека Photos →', '/media').classes('text-xs text-green-900 no-underline')
            with ui.element('div').classes('commander-trees') as self.trees:
                self.panes = [BrowserPane(self, index) for index in range(2)]
                self.link_badge = ui.element('div').classes('pane-link').props('role="img" aria-label="Панели связаны в режиме сверки"')
                with self.link_badge:
                    ui.icon('link', size='19px')
                self.pair.build()
            self.build_operations()
        self.set_active(0)
        self.render_progress()

    def build_operations(self):
        with ui.column().classes('s-panel workspace-operations w-full gap-0'):
            with ui.column().classes('s-panel-head w-full'):
                ui.label('ОПЕРАЦИИ').classes('s-caption')
            with ui.column().classes('workspace-operation-body w-full'):
                self.copies.build_controls()
        with ui.dialog() as self.legacy_dialog, ui.card().classes('w-[650px] max-w-full p-5 gap-3'):
            ui.label('Прежние отчёты по именам').classes('text-lg font-semibold')
            ui.label('Сверка').classes('workspace-operation-title')
            self.scopes_label = ui.label('Выбери том и папку в каждой панели.').classes('workspace-scopes w-full').style('white-space:pre-line')
            self.start_button = ui.button('Сверить левую → правую', icon='compare_arrows', on_click=self.start_comparison).props('unelevated no-caps color=green-9').classes('workspace-start w-full text-xs')
            self.refresh_lists = ui.checkbox('Заново собрать списки с дисков', value=False).props('dense size=xs').classes('text-xs')
            self.history = ui.select({}, label='История сверок', on_change=self.history_changed).props('outlined dense clearable').classes('workspace-history')
            with ui.column().classes('w-full gap-2') as self.progress_row:
                self.phase_label = ui.label('Готово к сверке имён').classes('text-xs s-muted')
                with ui.row().classes('gap-1 items-center'):
                    self.pause_button = ui.button('Остановить', icon='pause', on_click=lambda: self.control('pause')).props('flat dense no-caps color=dark')
                    self.resume_button = ui.button('Продолжить', icon='play_arrow', on_click=lambda: self.control('resume')).props('flat dense no-caps color=green-9')
            self.progress = ui.linear_progress(value=0, show_value=False).props('color=green-8').classes('w-full')
            self.counts = ui.element('div').classes('workspace-counts')
            self.summary = ui.label('').classes('workspace-summary')
            self.results = ui.row().classes('workspace-results w-full')
            self.journal_button = ui.button('Журнал', icon='receipt_long', on_click=self.show_journal).props('flat dense no-caps color=dark')
            self.browse_button = ui.button('Закрыть результат сверки', icon='close', on_click=self.browse).props('flat dense no-caps color=dark').classes('text-xs')
            ui.button('Закрыть', on_click=self.legacy_dialog.close).props('flat no-caps color=dark')

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
        changed = index != self.active_index
        self.active_index = index
        for pane in getattr(self, 'panes', []):
            pane.container.classes(add='active-pane' if pane.index == index else '', remove='' if pane.index == index else 'active-pane')
        if changed:
            self.render_volumes()

    def property_menu(self, label, callback, *, extra=()):
        client = ui.context.client

        def action(callback):
            async def invoke():
                with client:
                    await callback()
            return invoke

        with ui.context_menu() as menu:
            menu.on('before-show', lambda: setattr(self, 'context_menu_open', True))
            menu.on('hide', lambda: setattr(self, 'context_menu_open', False))
            ui.menu_item(label, on_click=action(callback))
            for text, handler in extra:
                ui.menu_item(text, on_click=action(handler))

    async def open_volume(self, volume_id, index=None):
        with self.client:
            index = self.active_index if index is None else index
            if self.pair.active:
                await self.pair.unlink()
            if self.report:
                await self.browse()
            await self.panes[index].show_volume(volume_id)

    def render_volumes(self):
        self.volume_list.clear()
        self.archive_list.clear()
        active = [v for v in self.volumes if not archived(v)]
        offline = [v for v in self.volumes if archived(v)]
        online = sum(v['availability'] == 'online' for v in self.volumes)
        self.overview.text = f'Томов: {len(self.volumes)} · подключено: {online} · в архиве: {len(offline)}'
        self.volumes_section.text = f'Тома · {len(active)}'
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
                    channel = bool(volume.get('marker_id') and volume.get('share_name'))
                    classes = 's-volume-row' + (' with-channel' if channel else '') + (' chosen' if volume['id'] == selected else '')
                    with ui.button(on_click=lambda v=volume: self.open_volume(v['id'])).props('flat no-caps color=dark').classes(classes):
                        self.property_menu('Свойства диска', lambda v=volume: self.show_properties(v['id']))
                        ui.icon('circle', size='7px').classes('shrink-0 ' + {'online': 'text-green-700', 'offline': 'text-grey-5', 'unknown': 'text-amber-700'}[volume['availability']])
                        with ui.column().classes('gap-0 flex-1 min-w-0'):
                            with ui.row().classes('w-full items-center no-wrap gap-1'):
                                ui.label(volume_label(volume, False)).classes('s-volume-name')
                                if volume.get('removable'):
                                    ui.label('Сменный').classes('s-volume-role s-volume-removable')
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
        if not force and (self.context_menu_open or self.editing):
            return
        self.refresh_button.disable()
        try:
            data = await self.request('GET', '/api/storage/volumes', params={'refresh': force}, timeout=45)
            self.volumes = data['volumes']
            self.render_volumes()
            await self.copies.refresh()
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
        self.copies.render_sidebar()
        self.copies.render_controls()
        if self.report:
            def scope_label(scan):
                volume = next((v for v in self.volumes if v['id'] == scan['volume_id']), None)
                name = volume_label(volume) if volume else scan['volume_name']
                return name + ' /' + scan['root_path']

            source = next(s for s in self.report['scans'] if s['side'] == 'source')
            targets = [s for s in self.report['scans'] if s['side'] == 'target']
            self.scopes_label.text = 'Слева: ' + scope_label(source) + '\nСправа: ' + ', '.join(scope_label(s) for s in targets)
            self.start_button.disable()
            return
        labels = []
        valid = True
        for pane in self.panes:
            scope = pane.scope()
            valid = valid and bool(scope)
            if scope:
                labels.append(volume_label(pane.volume) + (' /' + scope['path'] if scope['path'] else ' /'))
            else:
                labels.append('Выбери том и папку')
        self.scopes_label.text = 'Слева: ' + labels[0] + '\nСправа: ' + labels[1]
        running = self.report and self.report['state'] in ('running', 'pausing')
        self.start_button.set_enabled(bool(valid and not running))

    async def load(self, source='', path='', job=''):
        await self.refresh_volumes()
        active = [v for v in self.volumes if not archived(v) and v.get('identity_status') != 'unverified']
        candidates = active or self.volumes
        if candidates:
            requested = next((v for v in self.volumes if v['id'] == source), None)
            left = requested or next((v for v in candidates if v.get('marker_id') and v.get('mounted')), candidates[0])
            right = next((v for v in candidates if v['id'] != left['id']), left)
            try:
                initial_path = relative_path(path) if requested else ''
            except ValueError as error:
                self.notice(error)
                initial_path = ''
            await self.panes[0].show_volume(left['id'], initial_path, activate=False)
            if not self.pair.active:
                await self.panes[1].show_volume(right['id'], activate=False)
        else:
            for pane in self.panes:
                pane.render()
        await self.refresh_history()
        if job and not self.pair.active:
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
        if self.pair.active:
            await self.pair.unlink()
        self.legacy_dialog.close()
        if not self.report:
            self.browse_state = [pane.save_browse_state() for pane in self.panes]
            self.browse_active = self.active_index
        self.match_generation += 1
        self.report, self.job_id = report, report['id']
        self.history.set_value(self.job_id)
        source = next(s for s in report['scans'] if s['side'] == 'source')
        targets = [s for s in report['scans'] if s['side'] == 'target']
        target = next((s for s in targets if s['volume_id'] == self.panes[1].volume_id), targets[0])
        right = self.panes[1]
        right.generation += 1
        right.volume_id, right.scan, right.job_id = target['volume_id'], target, self.job_id
        right.path = right.root_path = target['root_path']
        right.kind, right.entry = 'directory', None
        right.folders.clear()
        right.comparison.reset()
        right.render()
        self.render_progress()
        await self.panes[0].show_volume(source['volume_id'], source['root_path'], scan=source, job_id=self.job_id, activate=False)
        self.last_marker = self.report_marker(report)
        self.render_progress()
        self.set_active(0)
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
        self.match_generation += 1
        self.job_id, self.report, self.last_marker = None, None, None
        self.history.set_value(None)
        self.current_matches.clear()
        self.results.clear()
        self.panes[1].comparison.reset()
        if self.browse_state:
            for pane, state in zip(self.panes, self.browse_state):
                pane.restore_browse_state(state)
            self.browse_state = None
        self.render_progress()
        self.set_active(self.browse_active)

    @staticmethod
    def report_marker(report):
        return report['state'], report['phase'], tuple((s['id'], s['state']) for s in report['scans'])

    async def poll(self):
        if self.context_menu_open or self.editing:
            return
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
                self.panes[1].comparison.reset()
                for pane in self.panes[:1]:
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
        self.link_badge.set_visibility(False)
        self.pair.render_rail()
        self.trees.classes(add='linked' if report else '', remove='' if report else 'linked')
        names = bool(report and report.get('mode') == 'names')
        self.trees.classes(add='names-comparison' if names else '', remove='' if names else 'names-comparison')
        self.start_button.set_visibility(False)
        self.refresh_lists.set_visibility(False)
        self.scopes_label.set_visibility(bool(report))
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
        self.counts.clear()
        self.counts.set_visibility(bool(report and report.get('counts')))
        if not report:
            self.phase_label.text = 'Готово к сверке имён'
            self.summary.text = 'Выбери прежний отчёт. Новая сверка пары запускается кнопкой «Папки» между деревьями.'
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
            self.summary.text = 'Сохранённые списки от ' + self.format_date(report['created_at'])
        with self.counts:
            for status, number in report.get('counts', {}).items():
                ui.label(LABELS.get(status, status)).style('color:' + STATUS_COLORS.get(status, '#747b72'))
                ui.label(str(number)).classes('text-right')
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
        if not self.job_id or not left.scan or left.scan['side'] != 'source' or left.job_id != self.job_id:
            return
        job_id, path = self.job_id, left.path
        context = job_id, path
        if right.comparison.context != context:
            right.comparison.reset(context)
            right.render()
        try:
            data = await self.request('GET', f'/api/storage/comparisons/{job_id}/detail',
                                      params={'path': path}, timeout=45)
        except Exception as error:
            if generation == self.match_generation:
                with self.results:
                    ui.label(self.error_text(error)).classes('text-xs s-muted')
            return
        if generation != self.match_generation or job_id != self.job_id or path != left.path:
            return
        for match in data.get('matches', []):
            if 'scan_id' not in match:
                scans = [s for s in self.report['scans'] if s['side'] == 'target' and s['volume_id'] == match['volume_id']
                         and (not s['root_path'] or match['path'] == s['root_path'] or match['path'].startswith(s['root_path'] + '/'))]
                if not scans:
                    continue
                match = dict(match, scan_id=max(scans, key=lambda s: len(s['root_path']))['id'], kind='file')
            match = dict(match, name=match.get('name') or PurePosixPath(match['path']).name)
            self.current_matches.append(match)
        right.comparison.set_matches(self.current_matches, context, data.get('matches_limit', 100))
        with self.results:
            entry = data['entry']
            status = entry.get('status')
            if status:
                ui.label(LABELS[status]).classes('text-xs').style('color:' + STATUS_COLORS.get(status, '#747b72'))
            ui.label(('Папка: ' if entry['kind'] == 'directory' else 'Файл: ') + entry['name']).classes('text-xs s-muted')
            if self.current_matches:
                ui.label(f"Найдено путей: {len(self.current_matches)}").classes('text-xs s-muted')
            else:
                ui.label('Совпадений в выбранной области нет' if self.report['state'] == 'completed' else 'Сверка ещё выполняется').classes('text-xs s-muted')

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

    async def show_properties(self, volume_id, entry=None):
        volume = next((v for v in self.volumes if v['id'] == volume_id), None)
        if not volume:
            return
        path = entry['path'] if entry else ''
        kind = entry['kind'] if entry else 'directory'
        try:
            metadata = (entry or {}).get('metadata', volume['metadata'])
            if path and kind == 'directory':
                data = await self.request('GET', f'/api/storage/volumes/{volume_id}/directory',
                                          params={'path': path, 'refresh': False}, timeout=45)
                metadata = data['metadata']
        except Exception as error:
            self.notice(error)
            return
        with ui.dialog() as dialog, ui.card().classes('w-[450px] max-w-full p-5 gap-4'):
            ui.label('Свойства диска' if not path else 'Свойства папки' if kind == 'directory' else 'Свойства файла').classes('s-caption')
            ui.label(PurePosixPath(path).name if path else volume_label(volume)).classes('text-lg font-semibold break-words')
            base = volume.get('network_url') or volume['mount_path'] or ''
            ui.label(base.rstrip('/') + ('/' + path if path else '')).classes('s-path s-muted')
            if not path and volume.get('removable'):
                ui.label('Сменный носитель').classes('s-tag purpose')
            capacity = volume.get('capacity')
            if not path and capacity:
                ui.label('Место на томе').classes('s-caption')
                with ui.element('div').classes('workspace-property-grid'):
                    for title, key in [('Объём', 'total_bytes'), ('Занято', 'used_bytes'), ('Свободно', 'free_bytes')]:
                        ui.label(title).classes('s-muted')
                        ui.label(self.format_bytes(capacity[key]))
                prefix = 'Последние сведения' if volume.get('capacity_cached') else 'Обновлено'
                ui.label(prefix + ': ' + self.format_date(capacity['checked_at'])).classes('text-xs s-muted')
            if volume.get('identity_error'):
                ui.label(volume['identity_error']).classes('s-error w-full')
            if not path and volume.get('marker_id'):
                ui.label('ID: ' + volume['marker_id']).classes('s-path s-muted')
            if not path and volume.get('share_name'):
                ui.label('Ресурс NAS: ' + volume['share_name']).classes('text-xs s-muted')
            values = metadata['effective']
            with ui.element('div').classes('workspace-property-grid'):
                ui.label('Назначение').classes('s-muted')
                ui.label(PURPOSES[values['purpose']])
            membership = self.copies.membership(volume_id, path)
            if membership:
                ui.label(membership['label']).classes('copy-label' + (' main' if membership['number'] == 0 else ''))
                if not membership['is_root']:
                    ui.label('Унаследовано от /' + membership['path']).classes('s-path s-muted')
            for key, label in FLAGS.items():
                if values.get(key):
                    ui.label(label).classes('s-tag flag')
            if metadata['own'].get('comment'):
                ui.label(metadata['own']['comment']).classes('text-sm break-words')
            if not volume.get('mounted') and volume.get('network_url'):
                ui.button('Подключить на M4', icon='lan', on_click=lambda: self.connect(volume['id'])).props('outline no-caps color=dark')
            with ui.row().classes('w-full justify-end gap-2'):
                if kind == 'directory' and volume.get('identity_status') != 'unverified':
                    ui.button('Изменить отметки', on_click=lambda: dialog.submit('edit')).props('outline no-caps color=green-9')
                ui.button('Закрыть', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
        if await dialog == 'edit':
            await self.edit_metadata(volume, path, metadata)

    async def edit_metadata(self, volume, path, metadata):
        volume_id = volume['id']
        inherit = '__inherit__'
        own = metadata['own']
        self.editing = True
        with ui.dialog() as dialog, ui.card().classes('w-[460px] max-w-full p-5 gap-4'):
            ui.label('Назначение и отметки').classes('text-lg font-semibold')
            ui.label(PurePosixPath(path).name if path else volume_label(volume)).classes('text-sm s-muted break-words')
            default = 'От родительской папки / тома' if path else 'Не назначено'
            purpose = ui.select({inherit: default, **PURPOSES}, value=own['purpose'] if own['purpose'] is not None else inherit, label='Что здесь хранится').props('outlined dense').classes('w-full')
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
                       'role': None, 'comment': comment.value or ''}
            payload.update({key: None if control.value == inherit else control.value == 'yes' for key, control in flags.items()})
            await self.request('PATCH', f'/api/storage/volumes/{volume_id}/metadata', json=payload)
            self.editing = False
            await self.refresh_volumes()
            for pane in self.panes:
                if pane.volume_id == volume_id:
                    if pane.index == 1 and self.report:
                        pane.render()
                        continue
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
