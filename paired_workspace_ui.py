"""Linked main/copy pairs, compact central controls, aligned virtual trees."""
import asyncio
from pathlib import PurePosixPath

from nicegui import ui

from media_manager.paired_comparison import DECISIONS, STATUS_LABELS, absolute_scope_path
from paired_tree import PairedTree


PAIR_CSS = '''
.commander-trees.pair-linked { grid-template-columns:minmax(0,1fr) 56px minmax(0,1fr); gap:4px; }
.commander-trees > .commander-pane:first-child { grid-column:1; grid-row:1; }
.commander-trees.pair-linked > .commander-pane:nth-child(2) { grid-column:3; }
.commander-trees.pair-linked .commander-pane { border-color:#b0c4a7; }
.commander-trees.pair-linked .commander-pane.active-pane { border-color:#75986c; }
.commander-trees.pair-linked .pane-status { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.pair-rail { grid-column:2; grid-row:1; width:56px; display:flex; align-items:center; gap:7px; padding-top:10px; }
.pair-rail .q-btn { min-width:0; width:54px; padding:3px 1px; min-height:40px; font-size:10px; line-height:13px; }
.pair-rail .q-btn__content { display:flex; flex-direction:column; gap:2px; flex-wrap:nowrap; }
.pair-rail .q-icon { font-size:17px; margin:0; }
.pair-disconnect .block { white-space:normal; }
.pair-connection { border:1px solid #b1c7ad; border-radius:50%; padding:4px; color:#397645; background:#edf5e9; }
.pair-rail-state { font-size:9px; text-align:center; line-height:13px; color:#64725f; overflow-wrap:anywhere; }
.pair-running-path { max-width:100%; }
.s-tree.pair-host { overflow:hidden; }
.pair-tree { display:flex; flex-direction:column; width:100%; height:100%; min-height:0; }
.pair-root-files { display:flex; align-items:center; gap:4px; width:100%; min-height:28px; border:0; border-bottom:1px solid #dfe7db; background:#f3f6ef; color:#626f59; font-size:11px; text-align:left; cursor:pointer; }
.pair-root-files .material-icons { font-size:17px; }
.pair-virtual { position:relative; flex:1; min-height:0; width:100%; overflow:auto; scrollbar-gutter:stable; }
.pair-row { position:absolute; left:0; width:100%; height:28px; display:flex; align-items:center; gap:4px; padding-right:7px; font-size:12px; cursor:default; border-bottom:1px solid #f0f2ef; }
.pair-row.alt { background:#f6f8f5; }
.pair-row.selected { background:#e9f1e4; box-shadow:inset 2px 0 #638c58; }
.pair-row.ghost { color:#c5cbd0; background:repeating-linear-gradient(135deg,#fafbfd,#fafbfd 5px,#f3f5f8 5px,#f3f5f8 6px); }
.pair-row.ghost .pair-file-icon { color:#d0d9df; }
.pair-row.ghost .pair-toggle { color:inherit; }
.pair-row-name { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pair-toggle { border:0; padding:0; width:17px; height:22px; background:none; color:#758172; flex-shrink:0; cursor:pointer; }
.pair-toggle .material-icons { font-size:17px; }
.pair-toggle-spacer { width:17px; flex-shrink:0; }
.pair-file-icon { color:#5a9ed1; font-size:16px; flex-shrink:0; }
.pair-row-state { font-size:10px; color:#71816d; max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex-shrink:0; }
.pair-missing_copy .pair-row-state { color:#a96717; }
.pair-extra_copy .pair-row-state { color:#85518e; }
.pair-different .pair-row-state, .pair-size_different .pair-row-state, .pair-conflict .pair-row-state { color:#b1443f; }
.pair-unverified .pair-row-state, .pair-copy_incomplete .pair-row-state { color:#a27130; }
.pair-same .pair-row-state, .pair-same_size .pair-row-state { color:#35804b; }
.pair-decide { border:0; background:none; padding:0; cursor:pointer; text-decoration:underline; }
.pair-size { color:#7a8477; font-size:10px; flex-shrink:0; }
.pair-decision { color:#795688; font-size:9px; max-width:70px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pair-attention { font-size:9px; border:1px solid #d5bd91; color:#9b6f22; padding:0 3px; border-radius:3px; }
.pair-empty { padding:18px 12px; font-size:12px; color:#78816f; }
.pair-scopes { font-size:12px; color:#5e7155; overflow-wrap:anywhere; }
.pair-history-row { width:100%; text-align:left; }
'''


class PairedWorkspace:
    def __init__(self, workspace):
        self.ws = workspace
        self.active = False
        self.scopes = None
        self.copy_id = None
        self.report = None
        self.rows = []
        self.by_path = {}
        self.closed = set()
        self.root = ''
        self.selected = ''
        self.differences_only = False
        self.show_hidden = False
        self.structure_at = None
        self.views = {}
        self.generation = 0
        self.saved = None
        self.saved_active = 0
        self.rail_signature = None
        self.loaded_job = None
        self.root_files_open = False
        self.copy_operation = None
        self.copy_dialog_open = False

    @property
    def copy_running(self):
        return bool(self.copy_operation and self.copy_operation['state'] in ('running', 'stopping'))

    @staticmethod
    def report_title(report):
        if report['mode'] == 'folders':
            return 'Папки'
        return 'Файлы · ' + ('имя и размер' if report.get('method') == 'size' else 'SHA-256')

    def build(self):
        ui.add_css(PAIR_CSS)
        self.rail = ui.column().classes('pair-rail')
        self.render_rail()
        ui.timer(1.5, self.poll)

    def render_rail(self):
        if not hasattr(self, 'rail') or self.ws.client.is_deleted:
            return
        linked = self.active or bool(self.ws.report)
        self.ws.trees.classes(add='pair-linked' if linked else '', remove='' if linked else 'pair-linked')
        self.rail.set_visibility(linked)
        if not linked:
            return
        signature = (self.active, (self.report or {}).get('state'), (self.report or {}).get('mode'),
                     (self.report or {}).get('phase'), bool(self.ws.report), (self.report or {}).get('checked_files'),
                     (self.report or {}).get('total_files'), (self.report or {}).get('indexed_directories'),
                     (self.report or {}).get('method'), bool(self.rows), self.differences_only,
                     tuple((self.copy_operation or {}).get(k) for k in ('id', 'state', 'copied_bytes', 'checked_items', 'message')),
                     self.copy_dialog_open)
        if signature == self.rail_signature:
            return
        self.rail_signature = signature
        self.rail.clear()
        with self.rail:
            ui.icon('link', size='19px').classes('pair-connection').props('role=img aria-hidden=false aria-label="Панели связаны"')
            if not self.active:
                ui.button('Отчёт', icon='history', on_click=self.ws.legacy_dialog.open).props('flat no-caps color=green-9')
                ui.button('Разомкнуть панели', icon='link_off', on_click=self.ws.browse).props('flat no-caps color=dark aria-label="Разомкнуть панели"').classes('pair-disconnect')
                return
            running = self.copy_running or (self.report and self.report['state'] in ('running', 'pausing'))
            folders = ui.button('Папки', icon='folder', on_click=lambda: self.start('folders')).props('outline no-caps color=green-9 aria-label="Сверить папки"')
            folders.set_enabled(not running)
            if self.report and self.report['state'] == 'completed':
                files = ui.button('Файлы', icon='fact_check', on_click=lambda: self.start('files')).props('outline no-caps color=blue-8 aria-label="Сверить имена и размеры файлов"')
                files.set_enabled(not self.copy_running)
                if self.report['mode'] == 'files' and self.report.get('copyable_count', self.report.get('counts', {}).get('missing_copy')):
                    copy = ui.button('Скопировать', icon='east', on_click=self.prepare_copy).props('outline no-caps color=green-9 aria-label="Скопировать отсутствующее из основной в копию"')
                    copy.set_enabled(not self.copy_running and not self.copy_dialog_open)
            if self.copy_running:
                operation = self.copy_operation
                ui.label('Копируем →').classes('pair-rail-state')
                total = operation['total_bytes']
                fraction = operation['copied_bytes'] / total if total else operation['checked_items'] / max(1, operation['total_directories'])
                ui.linear_progress(value=min(1, fraction)).props('color=green-8').classes('w-full')
                ui.label(str(operation['copied_files']) + '/' + str(operation['total_files'])).classes('pair-rail-state')
                stop = ui.button('Стоп', icon='pause', on_click=self.stop_copy).props('flat no-caps color=dark aria-label="Остановить копирование"')
                stop.set_enabled(operation['state'] == 'running')
            if self.report and not self.copy_running:
                state = {'running': 'Проверяем', 'pausing': 'Остановка', 'paused': 'Пауза', 'failed': 'Ошибка', 'completed': 'Готово'}[self.report['state']]
                phase = {'index': 'Список', 'hash': 'SHA-256', 'align': 'Сравнение', 'done': ('Имя, размер' if self.report.get('method') == 'size' else 'SHA-256') if self.report['mode'] == 'files' else 'Папки'}[self.report['phase']]
                ui.label(phase + '\n' + state).classes('pair-rail-state').style('white-space:pre-line')
                if running:
                    total = self.report['total_files']
                    progress = self.report['checked_files'] / total if total else 0
                    ui.linear_progress(value=progress).props('color=green-8' + ('' if total else ' indeterminate')).classes('w-full')
                    if total:
                        ui.label(f"{self.report['checked_files']}/{total}").classes('pair-rail-state')
                    elif self.report.get('indexed_directories'):
                        ui.label(str(self.report['indexed_directories']) + '\nпапок').classes('pair-rail-state').style('white-space:pre-line')
                    button = ui.button('Стоп', icon='pause', on_click=self.stop).props('flat no-caps color=dark')
                    button.set_enabled(self.report['state'] == 'running')
                elif self.report['state'] in ('paused', 'failed'):
                    ui.button('Далее', icon='play_arrow', on_click=self.resume).props('flat no-caps color=green-9 aria-label="Продолжить сверку"')
                ui.button('Итоги', icon='format_list_bulleted', on_click=self.details).props('flat no-caps color=green-9')
            if self.copy_operation and self.copy_operation['state'] != 'planned':
                ui.button('Копия', icon='assignment', on_click=self.copy_details).props('flat no-caps color=green-9 aria-label="Результат копирования"')
            ui.button('История', icon='history', on_click=self.history).props('flat no-caps color=dark')
            if self.rows or (self.report and self.report['state'] == 'completed'):
                with ui.button(icon='more_horiz').props('flat aria-label="Дополнительные команды"'):
                    with ui.menu():
                        if self.rows:
                            if self.report['mode'] == 'folders':
                                ui.menu_item('Раскрыть всё', on_click=lambda: self.collapse_all(False))
                                ui.menu_item('Показать все строки' if self.differences_only else 'Только различия', on_click=self.toggle_differences)
                            ui.menu_item('Свернуть всё', on_click=lambda: self.collapse_all(True))
                        if self.report['state'] == 'completed' and not self.copy_running:
                            ui.menu_item('Сверить содержимое · SHA-256', on_click=lambda: self.start('files', 'sha256'))
            ui.button('Разомкнуть панели', icon='link_off', on_click=self.unlink).props('flat no-caps color=grey-7 aria-label="Разомкнуть панели"').classes('pair-disconnect')

    async def link(self, group, location):
        with self.ws.client:
            if self.copy_running:
                await self.stop_copy()
            if self.active and self.report and self.report['state'] in ('running', 'pausing'):
                await self.stop()
            if self.ws.report:
                await self.ws.browse()
            if self.saved is None:
                self.saved = [p.save_browse_state() for p in self.ws.panes]
                self.saved_active = self.ws.active_index
            self.generation += 1
            self.active = True
            self.scopes = {'left': group['main'], 'right': location}
            self.copy_id = location['id']
            self.report, self.rows, self.by_path = None, [], {}
            self.copy_operation = None
            self.root = self.selected = ''
            self.closed.clear()
            self.differences_only = False
            self.loaded_job = None
            self.root_files_open = False
            self.show_hidden = any(p.hidden.value for p in self.ws.panes)
            self.views.clear()
            self.rail_signature = None
            self.render_rail()
            await asyncio.gather(*(p.show_volume(s['volume_id'], s['path'], activate=False)
                                   for p, s in zip(self.ws.panes, self.scopes.values())))
            self.ws.set_active(0)
            self.ws.update_scopes()

    async def unlink(self):
        if not self.active:
            return
        with self.ws.client:
            if self.copy_running:
                await self.stop_copy()
            if self.report and self.report['state'] in ('running', 'pausing'):
                await self.stop()
            self.generation += 1
            self.active, self.report = False, None
            self.copy_operation = None
            self.rows, self.by_path = [], {}
            self.views.clear()
            states, self.saved = self.saved, None
            for pane, state in zip(self.ws.panes, states or []):
                pane.tree.classes(remove='pair-host')
                pane.restore_browse_state(state)
            self.rail_signature = None
            self.render_rail()
            self.ws.set_active(self.saved_active)
            self.ws.update_scopes()

    def update_header(self, pane):
        side = 'left' if pane.index == 0 else 'right'
        scope = self.scopes[side]
        pane.location.set_visibility(True)
        pane.volume_select.set_visibility(True)
        pane.volume_select.set_enabled(not bool(self.report))
        pane.navigation.set_visibility(True)
        pane.toolbar.set_visibility(True)
        pane.result_filter.set_visibility(False)
        pane.heading.text = scope['label']
        boundary = scope['path']
        pane.render_path(scope['volume_id'], pane.path, pane.kind, boundary=boundary)
        if self.report:
            pane.snapshot_label.text = ('Проверяем файлы · папки: ' + self.ws.format_date(self.structure_at)
                                        if self.structure_at else self.report_title(self.report) + ' · ' + self.ws.format_date(self.report['created_at']))
            row = self.by_path.get(self.selected)
            if row and not row.get(side):
                pane.footer.text = 'Не проверено' if row['status'] == 'unverified' else 'Отсутствует · ' + scope['label']
            else:
                pane.footer.text = self.report['message'] + ' · ' + scope['label']
        else:
            pane.snapshot_label.text = 'Связь с ' + self.scopes['right' if side == 'left' else 'left']['label']
            if pane.volume:
                pane.footer.text = self.ws.capacity_text(pane.volume)

    def relative(self, index, path):
        scope = self.scopes['left' if index == 0 else 'right']
        if path == scope['path']:
            return ''
        prefix = scope['path'] + '/'
        return path[len(prefix):] if path.startswith(prefix) else None

    async def navigate_path(self, index, path):
        relative = self.relative(index, path)
        if relative is None:
            return
        if self.report:
            self.navigate(relative)
        else:
            with self.ws.client:
                await asyncio.gather(*(p.show_volume(s['volume_id'], absolute_scope_path(s, relative), activate=False)
                                       for p, s in zip(self.ws.panes, self.scopes.values())))

    def visible_rows(self):
        include = None
        if self.differences_only:
            include = set()
            for row in self.rows:
                if row['status'] not in ('both', 'same', 'same_size', 'skipped'):
                    path = row['path']
                    while path:
                        include.add(path)
                        parent = str(PurePosixPath(path).parent)
                        path = '' if parent == '.' else parent
        result, hidden_under = [], None
        base_depth = len(PurePosixPath(self.root).parts) if self.root else 0
        for row in self.rows:
            path = row['path']
            if not self.show_hidden and any(part.startswith('.') for part in PurePosixPath(path).parts):
                continue
            if self.root and not path.startswith(self.root + '/'):
                continue
            if include is not None and path not in include:
                continue
            parent = str(PurePosixPath(path).parent)
            if (self.report and self.report['mode'] == 'files' and row['kind'] != 'directory'
                    and ('' if parent == '.' else parent) == self.root and not self.root_files_open):
                continue
            if hidden_under and path.startswith(hidden_under + '/'):
                continue
            hidden_under = path if path in self.closed else None
            result.append(dict(row, level=row['depth'] - base_depth, collapsed=path in self.closed))
        return result

    def configure_view(self, view):
        root_files = sum(r['kind'] != 'directory' and str(PurePosixPath(r['path']).parent) == (self.root or '.')
                         and (self.show_hidden or not any(p.startswith('.') for p in PurePosixPath(r['path']).parts))
                         for r in self.rows) if self.report['mode'] == 'files' else 0
        view.props.update(root_file_count=root_files, root_files_open=self.root_files_open)
        view.props['empty_text'] = ('Идёт сверка…' if self.report['state'] in ('running', 'pausing') else
                                   self.report['message'] if self.report['state'] == 'failed' else
                                   'Часть данных не проверена. Подробности — в итогах.' if self.report.get('root_errors') else
                                   'Различий нет' if self.differences_only else 'Папок нет')

    def render_tree(self, pane):
        side = 'left' if pane.index == 0 else 'right'
        pane.tree.classes(add='pair-host')
        existing = self.views.get(side)
        if existing is None:
            pane.tree.clear()
            with pane.tree:
                existing = PairedTree(side, self.on_select, self.on_open, self.on_toggle, self.on_context, self.toggle_root_files)
            self.views[side] = existing
        self.configure_view(existing)
        existing.set_rows(self.visible_rows(), self.selected)

    def redraw(self, rows_changed=True):
        visible = self.visible_rows() if rows_changed else None
        for side, pane in zip(('left', 'right'), self.ws.panes):
            if side in self.views:
                if rows_changed:
                    self.configure_view(self.views[side])
                    self.views[side].set_rows(visible, self.selected)
                else:
                    self.views[side].run_method('setSelection', self.selected)
            else:
                self.render_tree(pane)
            pane.update_header()
        self.ws.update_scopes()

    def choose(self, relative):
        self.selected = relative
        row = self.by_path.get(relative)
        for side, pane in zip(('left', 'right'), self.ws.panes):
            data = row.get(side) if row else None
            pane.path = data['path'] if data else absolute_scope_path(self.scopes[side], relative)
            pane.kind = (data or row or {}).get('kind', 'directory')
            pane.entry = dict(data or {}, path=pane.path, kind=pane.kind)

    def navigate(self, relative):
        self.root = relative
        self.root_files_open = False
        self.closed.discard(relative)
        self.choose(relative)
        self.redraw()
        for view in self.views.values():
            view.run_method('resetScroll')

    async def on_select(self, event):
        with self.ws.client:
            if event.args['path'] not in self.by_path:
                return
            self.ws.set_active(0 if event.args['side'] == 'left' else 1)
            self.choose(event.args['path'])
            expanded = event.args['path'] in self.closed
            self.closed.discard(event.args['path'])
            self.redraw(rows_changed=expanded)

    async def on_open(self, event):
        with self.ws.client:
            row = self.by_path.get(event.args['path'])
            if row and row['kind'] == 'directory':
                self.navigate(row['path'])

    async def on_toggle(self, event):
        with self.ws.client:
            path = event.args['path']
            if path in self.closed:
                self.closed.remove(path)
            else:
                self.closed.add(path)
            self.redraw()

    def collapse_all(self, value):
        self.closed = {r['path'] for r in self.rows if r['kind'] == 'directory'} if value else set()
        self.root_files_open = not value
        self.redraw()

    def toggle_root_files(self):
        self.root_files_open = not self.root_files_open
        self.redraw()

    def toggle_differences(self):
        self.differences_only = not self.differences_only
        self.root = ''
        self.choose('')
        self.rail_signature = None
        self.render_rail()
        self.redraw()

    def set_hidden(self, value):
        changed = self.show_hidden != value
        self.show_hidden = value
        for pane in self.ws.panes:
            if pane.hidden.value != value:
                pane.hidden.set_value(value)
        if changed:
            self.redraw()

    async def start(self, mode, method='size'):
        with self.ws.client:
            generation = self.generation
            try:
                data = await self.ws.request('POST', '/api/storage/paired-comparisons',
                                             json={'copy_id': self.copy_id, 'mode': mode, 'method': method,
                                                   'base_job_id': self.report['id'] if mode == 'files' and self.report else None}, timeout=45)
                if generation != self.generation:
                    return
                await self.apply(data)
            except Exception as error:
                self.ws.notice(error)

    async def apply(self, report):
        previous = self.report
        self.report = report
        self.copy_operation = report.get('copy_operation')
        self.scopes = report['scopes']
        for side, pane in zip(('left', 'right'), self.ws.panes):
            pane.volume_id = self.scopes[side]['volume_id']
            pane.volume_select.set_value(pane.volume_id)
        if not previous or report['id'] != previous['id']:
            self.root = self.selected = ''
            self.differences_only = report['mode'] == 'files'
            self.root_files_open = False
            self.closed = {r['path'] for r in self.rows if r['kind'] == 'directory'} if report['mode'] == 'files' else set()
            carry = previous and report['mode'] == 'files' and previous['copy_id'] == report['copy_id'] and bool(self.rows)
            if carry:
                self.structure_at = self.structure_at or previous['created_at']
                self.choose('')
            else:
                self.structure_at = None
                self.rows, self.by_path = [], {}
                self.views.clear()
                for pane in self.ws.panes:
                    pane.tree.clear()
                    pane.folders.clear()
        self.rail_signature = None
        self.render_rail()
        self.set_hidden(self.show_hidden)
        if report['state'] == 'completed':
            await self.load_rows(report['id'])
        else:
            for side, pane in zip(('left', 'right'), self.ws.panes):
                pane.path = self.scopes[side]['path']
                pane.kind = 'directory'
                pane.render()

    async def load_rows(self, job):
        generation = self.generation
        params = {'limit': 5000, 'differences_only': self.report['mode'] == 'files'}
        first = await self.ws.request('GET', f'/api/storage/paired-comparisons/{job}/rows', params=params, timeout=45)
        rows = first['rows']
        for offset in range(5000, first['total'], 5000):
            if generation != self.generation:
                return
            rows += (await self.ws.request('GET', f'/api/storage/paired-comparisons/{job}/rows',
                                           params={**params, 'offset': offset}, timeout=45))['rows']
        if generation != self.generation or not self.report or self.report['id'] != job:
            return
        for row in rows:
            for side in ('left', 'right'):
                if row.get(side) and row[side].get('size') is not None:
                    row[side]['size_text'] = self.ws.format_bytes(row[side]['size'])
        self.rows = rows
        self.structure_at = None
        self.by_path = {row['path']: row for row in rows}
        # Older SHA reports predate the separate file counter.
        old_directories = {r['path'] for r in rows if r['kind'] == 'directory' and 'file_attention_count' not in r}
        for path in old_directories:
            self.by_path[path]['file_attention_count'] = 0
        if old_directories:
            for row in rows:
                if row['kind'] == 'directory' or row['status'] in ('same', 'same_size', 'skipped'):
                    continue
                for parent in PurePosixPath(row['path']).parents:
                    if str(parent) in old_directories:
                        self.by_path[str(parent)]['file_attention_count'] += 1
        if self.loaded_job != job:
            self.closed = {r['path'] for r in rows if r['kind'] == 'directory'
                           and (self.report['mode'] == 'files' or not r.get('attention_count'))}
            self.root_files_open = False
            self.loaded_job = job
        self.choose(self.selected)
        self.rail_signature = None
        self.render_rail()
        self.redraw()

    async def poll(self):
        if not self.active or not self.report:
            return
        generation, job = self.generation, self.report['id']
        try:
            if self.copy_running:
                operation = await self.ws.request('GET', f"/api/storage/copy-operations/{self.copy_operation['id']}", timeout=30)
                if generation == self.generation and self.active and self.report and self.report['id'] == job:
                    with self.ws.client:
                        await self.apply_copy_operation(operation)
                return
            if self.report['state'] not in ('running', 'pausing'):
                return
            report = await self.ws.request('GET', f'/api/storage/paired-comparisons/{job}', timeout=30)
            if generation != self.generation or not self.report or self.report['id'] != job:
                return
            with self.ws.client:
                await self.apply(report)
        except Exception as error:
            self.ws.overview.text = 'Нет связи с Core: ' + self.ws.error_text(error)

    async def apply_copy_operation(self, operation):
        self.copy_operation = operation
        verification = operation.get('verification_id')
        if verification and self.report and self.report['id'] != verification:
            report = await self.ws.request('GET', f'/api/storage/paired-comparisons/{verification}', timeout=30)
            await self.apply(report)
        self.rail_signature = None
        self.render_rail()

    async def stop_copy(self):
        if self.copy_running:
            self.copy_operation = await self.ws.request('POST', f"/api/storage/copy-operations/{self.copy_operation['id']}/stop", timeout=30)
            self.rail_signature = None
            self.render_rail()

    def copy_paths(self, operation):
        for side in ('left', 'right'):
            scope = operation['scopes'][side]
            ui.label(scope['label'] + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes('text-sm break-all')

    async def copy_item_list(self, operation):
        """The entire frozen plan can be reviewed in manageable pages."""
        page = await self.ws.request('GET', f"/api/storage/copy-operations/{operation['id']}/items", params={'limit': 200}, timeout=30)
        position = 0
        container = ui.column().classes('w-full max-h-[45vh] overflow-auto gap-1')
        shown = ui.label().classes('text-xs s-muted')
        more = ui.button('Показать ещё 200').props('flat dense no-caps color=green-9')

        def append(data):
            nonlocal position
            with container:
                for item in data['items']:
                    with ui.row().classes('w-full items-start no-wrap gap-2'):
                        ui.icon('folder' if item['kind'] == 'directory' else 'insert_drive_file', size='16px').classes('text-blue-5')
                        with ui.column().classes('min-w-0 flex-1 gap-0'):
                            ui.label(item['path']).classes('text-xs break-all')
                            if item.get('incomplete'):
                                ui.label('Копия не завершена').classes('text-xs text-amber-9')
                            if item['message']:
                                ui.label(item['message']).classes('text-xs text-amber-9 break-all')
                        if item['kind'] == 'file':
                            ui.label(self.ws.format_bytes(item['size'])).classes('text-xs s-muted shrink-0')
            position += len(data['items'])
            shown.text = f"Показано: {position} из {data['total']}"
            more.set_visibility(position < data['total'])

        async def load_more():
            with self.ws.client:
                more.disable()
                try:
                    append(await self.ws.request('GET', f"/api/storage/copy-operations/{operation['id']}/items",
                                                 params={'offset': position, 'limit': 200}, timeout=30))
                except Exception as error:
                    self.ws.notice(error)
                finally:
                    more.enable()

        more.on_click(load_more)
        append(page)

    async def prepare_copy(self):
        if self.copy_dialog_open or self.copy_running or not self.report:
            return
        with self.ws.client:
            generation, report_id = self.generation, self.report['id']
            was_editing = self.ws.editing
            self.copy_dialog_open, self.ws.editing = True, True
            self.rail_signature = None
            self.render_rail()
            try:
                operation = await self.ws.request('POST', f'/api/storage/paired-comparisons/{report_id}/copy-plan', timeout=60)
                if self.ws.client.is_deleted or generation != self.generation or not self.report or self.report['id'] != report_id:
                    return
                with ui.dialog() as dialog, ui.card().classes('w-[660px] max-w-full p-5 gap-3'):
                    ui.label('Скопировать отсутствующее →').classes('text-lg font-semibold')
                    self.copy_paths(operation)
                    ui.label(f"Файлов: {operation['total_files']} · папок: {operation['total_directories']} · {self.ws.format_bytes(operation['total_bytes'])}").classes('text-sm font-semibold')
                    ui.label('Копируется вся проверенная пара. Существующие файлы и элементы с другим размером останутся на месте.').classes('text-sm s-muted')
                    ui.label('Незавершённые копии при прерывании записи будут отмечены для ручного разбора.').classes('text-xs s-muted')
                    await self.copy_item_list(operation)
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                        ui.button('Начать копирование', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
                if await dialog and not self.ws.client.is_deleted and generation == self.generation and self.report and self.report['id'] == report_id:
                    await self.apply_copy_operation(await self.ws.request('POST', f"/api/storage/copy-operations/{operation['id']}/start", timeout=45))
            except Exception as error:
                self.ws.notice(error)
            finally:
                self.copy_dialog_open, self.ws.editing = False, was_editing
                self.rail_signature = None
                self.render_rail()

    async def copy_details(self):
        if not self.copy_operation:
            return
        with self.ws.client:
            try:
                operation = await self.ws.request('GET', f"/api/storage/copy-operations/{self.copy_operation['id']}", timeout=30)
                with ui.dialog() as dialog, ui.card().classes('w-[660px] max-w-full p-5 gap-3'):
                    ui.label('Копирование из 00-main →').classes('text-lg font-semibold')
                    self.copy_paths(operation)
                    ui.label(operation['message']).classes('text-sm font-semibold')
                    ui.label(f"Готово файлов: {operation['copied_files']} · папок: {operation['copied_directories']} · пропущено: {operation['skipped']} · ошибок: {operation['errors']}").classes('text-sm s-muted')
                    if operation.get('incomplete_files'):
                        ui.label(f"Незавершённых файлов в копии: {operation['incomplete_files']}").classes('text-sm text-amber-9')
                    if operation['current_path']:
                        ui.label(operation['current_path']).classes('text-xs break-all')
                    await self.copy_item_list(operation)
                    ui.button('Закрыть', on_click=dialog.close).props('flat no-caps color=dark')
                dialog.open()
            except Exception as error:
                self.ws.notice(error)

    async def stop(self):
        if self.report:
            self.report = await self.ws.request('POST', f"/api/storage/paired-comparisons/{self.report['id']}/pause", timeout=30)
            self.rail_signature = None
            self.render_rail()

    async def resume(self):
        with self.ws.client:
            try:
                await self.apply(await self.ws.request('POST', f"/api/storage/paired-comparisons/{self.report['id']}/resume", timeout=30))
            except Exception as error:
                self.ws.notice(error)

    async def details(self):
        with self.ws.client:
            report = self.report
            with ui.dialog() as dialog, ui.card().classes('w-[580px] max-w-full p-5 gap-3'):
                ui.label('Итоги · ' + self.report_title(report)).classes('text-lg font-semibold')
                for side, title in (('left', '00-main'), ('right', self.scopes['right']['label'])):
                    scope = self.scopes[side]
                    ui.label(title + ' · ' + scope['volume_name'] + ' /' + scope['path']).classes('pair-scopes')
                ui.label(self.ws.format_date(report['created_at']) + ' · ' + report['message']).classes('text-sm s-muted')
                if report.get('indexed_directories'):
                    ui.label(f"Прочитано каталогов: {report['indexed_directories']}").classes('text-xs s-muted')
                if report['current_path']:
                    ui.label(report['current_path']).classes('text-xs break-words')
                for status, count in report['counts'].items():
                    with ui.row().classes('w-full justify-between'):
                        ui.label(STATUS_LABELS[status])
                        ui.label(str(count))
                explanation = ('Сравниваются имена, относительные пути и размеры. Содержимое файлов не читается.'
                               if report['mode'] == 'files' and report.get('method') == 'size' else
                               'Совпадает — содержимое файлов проверено по SHA-256.' if report['mode'] == 'files' else
                               'Есть в обоих — наличие папок. Файлы пока не сравнивались.')
                ui.label(explanation).classes('text-xs s-muted')
                if report['errors']:
                    ui.label(f"Не удалось прочитать элементов: {report['errors']}").classes('text-sm text-amber-9')
                    for side, error in report.get('root_errors', {}).items():
                        ui.label(self.scopes[side]['label'] + ': ' + error).classes('text-xs text-amber-9 break-words')
                    errors = [(row['path'], side, row[side]['error']) for row in self.rows
                              for side in ('left', 'right') if row.get(side) and row[side].get('error')]
                    if errors:
                        with ui.column().classes('w-full max-h-48 overflow-auto gap-1'):
                            for path, side, error in errors[:100]:
                                ui.label(self.scopes[side]['label'] + ' /' + path + ': ' + error).classes('text-xs break-words')
                extras = [r for r in self.rows if r['status'] == 'extra_copy']
                if extras:
                    ui.label('Только в копии · выбери решение').classes('font-semibold')
                    with ui.column().classes('w-full max-h-64 overflow-auto gap-1'):
                        for row in extras:
                            ui.button(row['path'] + (' · ' + DECISIONS[row['decision']] if row['decision'] else ''),
                                      on_click=lambda r=row: self.decide(r)).props('flat dense no-caps color=purple-8').classes('text-xs break-all')
                ui.button('Закрыть', on_click=dialog.close).props('flat no-caps color=dark')
            dialog.open()

    async def on_context(self, event):
        row = self.by_path.get(event.args['path'])
        if not row:
            return
        with self.ws.client:
            if event.args['side'] == 'right' and row['status'] == 'extra_copy':
                await self.decide(row)
            else:
                side = event.args['side']
                data = row.get(side)
                if data:
                    await self.ws.show_properties(self.scopes[side]['volume_id'], data)

    async def decide(self, row):
        with self.ws.client:
            job, generation = self.report['id'], self.generation
            self.ws.editing = True
            try:
                with ui.dialog() as dialog, ui.card().classes('w-[460px] max-w-full p-5 gap-3'):
                    ui.label('Только в копии').classes('text-lg font-semibold')
                    ui.label(row['path']).classes('text-sm break-all')
                    action = ui.select({'': 'Наследовать / снять отдельное решение', **DECISIONS}, value=row.get('own_decision') or '', label='Что сделать').props('outlined dense').classes('w-full')
                    if row.get('decision_from'):
                        ui.label('От папки ' + row['decision_from'] + ': ' + DECISIONS[row['decision']]).classes('text-xs s-muted break-all')
                    ui.label('Сейчас сохраняется решение. Файловые операции будут выполняться отдельно.').classes('text-xs s-muted')
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                        ui.button('Сохранить решение', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
                if await dialog:
                    await self.ws.request('PATCH', f'/api/storage/paired-comparisons/{job}/decision', json={'path': row['path'], 'action': action.value or None})
                    if generation == self.generation:
                        await self.load_rows(job)
            except Exception as error:
                self.ws.notice(error)
            finally:
                self.ws.editing = False

    async def history(self):
        with self.ws.client:
            try:
                jobs = (await self.ws.request('GET', '/api/storage/paired-comparisons', params={'copy_id': self.copy_id}, timeout=30))['jobs']
                with ui.dialog() as dialog, ui.card().classes('w-[600px] max-w-full p-5 gap-3'):
                    ui.label('История сверок пары').classes('text-lg font-semibold')
                    if not jobs:
                        ui.label('Эта пара ещё не проверялась.').classes('s-muted text-sm')
                    async def choose(job):
                        dialog.close()
                        self.generation += 1
                        await self.apply(job)
                    for job in jobs:
                        label = self.ws.format_date(job['created_at']) + ' · ' + self.report_title(job)
                        label += ' · ' + {'completed': 'Готово', 'paused': 'Пауза', 'running': 'Выполняется', 'pausing': 'Остановка', 'failed': 'Ошибка'}[job['state']]
                        ui.button(label, on_click=lambda j=job: choose(j)).props('flat no-caps color=green-9').classes('pair-history-row')
                    ui.separator()
                    def legacy():
                        dialog.close()
                        self.ws.legacy_dialog.open()
                    ui.button('Прежние отчёты по именам', on_click=legacy).props('flat no-caps color=dark')
                    ui.button('Закрыть', on_click=dialog.close).props('flat no-caps color=dark')
                dialog.open()
            except Exception as error:
                self.ws.notice(error)
