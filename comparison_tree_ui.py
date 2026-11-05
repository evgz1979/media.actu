"""The linked right tree of a comparison, read only from saved target lists."""
from __future__ import annotations

from itertools import count
import json
from pathlib import PurePosixPath

from nicegui import ui

from storage_ui import folder_icon


#: Показывает найденные пути общей сверки в правой панели.
#: Зависимости конструктора: pane.
class ComparisonTree:
    #: Инициализирует ComparisonTree и его рабочее состояние.
    #: Обновляет состояние объекта: context, expanded, focus, folders, generation, limit, pane, roots, selected, workspace.
    def __init__(self, pane):
        self.pane = pane
        self.workspace = pane.workspace
        self.context = None
        self.generation = 0
        self.roots = []
        self.expanded = set()
        self.folders = {}
        self.selected = None
        self.focus = None
        self.limit = 100

    #: Сбрасывает найденные ветви и контекст выбранного исходного элемента.
    #: Обновляет состояние объекта: context, focus, generation, roots, selected.
    def reset(self, context=None):
        self.generation += 1
        self.context = context
        self.roots = []
        self.expanded.clear()
        self.folders.clear()
        self.selected = None
        self.focus = None

    #: Переключает правую панель к дереву найденных совпадений.
    #: Обновляет состояние объекта: focus, selected.
    def show_matches(self):
        self.focus = self.selected = None
        self.pane.render()

    #: Применяет найденные пути и контекст с ограничением отображаемых корней.
    #: Обновляет состояние объекта: limit, roots.
    def set_matches(self, matches, context, limit=100):
        if context != self.context:
            self.reset(context)
        self.roots = matches
        self.limit = limit
        self.pane.render()

    #: Обновляет заголовок и путь панели найденных совпадений.
    #: Использует pane.location.set_visibility, pane.path_bar.clear, pane.render_path, pane.toolbar.set_visibility, self.roots[0].get.
    def update_header(self):
        pane = self.pane
        pane.location.set_visibility(bool(self.selected))
        if self.selected:
            scope, entry = self.selected
            pane.render_path(scope['volume_id'], entry['path'], entry['kind'],
                             boundary=scope['path'], navigate=self.open_path)
        else:
            pane.path_bar.clear()
            pane.path_signature = None
        pane.toolbar.set_visibility(bool(self.roots))
        timestamp = self.roots[0].get('indexed_at') if self.roots else None
        pane.snapshot_label.text = 'Список сверки: ' + self.workspace.format_date(timestamp) if self.roots else ''
        pane.footer.text = f'Найдено путей: {len(self.roots)}' if self.roots else ''

    #: Перерисовывает раскрытые ветви сохранённого дерева совпадений.
    #: Использует branch, count, node, ui.label, ui.label(f'Показаны первые {self.limit} найденных путей.').classes.
    def render(self):
        rows = count()

        #: Рисует один узел совпадения с командами выбора, открытия и свойств.
        #: Использует PurePosixPath, branch, entry.get, folder_icon, json.dumps.
        def node(entry, scope, depth=0, root=False):
            key = entry['scan_id'], entry['path']
            directory = entry['kind'] == 'directory'
            if directory:
                folder_key = json.dumps([scope['volume_id'], entry['scan_id'], entry['path']], ensure_ascii=False)
                self.pane.folder_entries[folder_key] = entry, scope
            selected = self.selected and key == (self.selected[1]['scan_id'], self.selected[1]['path'])
            classes = 's-entry match-entry' + (' alt' if next(rows) % 2 else '') + (' selected' if selected else '')
            with ui.element('div').classes(classes).style(f'padding-left:{4 + depth * 14}px') as row:
                self.pane.register_navigation(row, entry, scope, selected=bool(selected))
                self.workspace.property_menu('Свойства', lambda e=entry, s=scope: self.workspace.show_properties(s['volume_id'], e),
                                             volume_id=scope['volume_id'], path=entry['path'])
                if directory:
                    ui.button(icon='expand_more' if key in self.expanded else 'chevron_right',
                              on_click=lambda e=entry, s=scope: self.select(e, s)).props('flat dense color=grey-7 aria-label="Раскрыть найденную папку"').classes('s-tree-toggle')
                    folder_icon().props['data-folder-key'] = folder_key
                else:
                    ui.element('span').classes('s-tree-spacer')
                    ui.icon('insert_drive_file' if entry['kind'] == 'file' else 'link', size='14px').classes('s-muted shrink-0')
                name_button = ui.button(entry['name'], on_click=None if directory else lambda e=entry, s=scope: self.select(e, s)).props('flat dense no-caps color=dark').classes('s-entry-name')
                if directory:
                    name_button.props['data-folder-key'] = folder_key
                membership = self.workspace.copies.membership(scope['volume_id'], entry['path']) if directory else None
                if membership:
                    ui.label(membership['label']).classes('copy-label' + (' main' if membership['number'] == 0 else ''))
                if directory:
                    self.pane.size_cells[scope['volume_id'], entry['path']] = ui.label(
                        self.workspace.directory_size_text(scope['volume_id'], entry['path'])).classes('text-xs s-muted shrink-0')
                elif entry.get('size') is not None:
                    ui.label(self.workspace.format_bytes(entry['size'])).classes('text-xs s-muted shrink-0')
                if entry.get('error'):
                    ui.icon('error_outline', size='13px').classes('text-orange-800')
                if root:
                    parent = str(PurePosixPath(entry['path']).parent)
                    ui.label(scope['volume_name'] + ' /' + ('' if parent == '.' else parent)).classes('match-location')
            if directory and key in self.expanded:
                branch(entry, scope, depth + 1)

        #: Рекурсивно рисует загруженные дочерние ветви совпадения.
        #: Использует child['name'].startswith, data.get, node, self.folders.get, ui.button.
        def branch(entry, scope, depth=0):
            data = self.folders.get((entry['scan_id'], entry['path']), {})
            for child in data.get('entries', []):
                if self.pane.hidden.value or not child['name'].startswith('.'):
                    node(child, scope, depth)
            if data.get('error'):
                ui.label(data['error']).classes('s-error m-2')
            elif not data.get('entries'):
                ui.label('Папка пуста').classes('s-muted text-xs py-1').style(f'padding-left:{20 + depth * 14}px')
            if len(data.get('entries', [])) < data.get('total', 0):
                ui.button('Показать ещё…', on_click=lambda e=entry: self.more(e)).props('flat dense no-caps color=dark').style(f'margin-left:{14 + depth * 14}px')

        if self.focus:
            scope, entry = self.focus
            branch(entry, scope)
        else:
            for entry in self.roots:
                node(entry, entry, root=True)
        if not self.focus and self.roots and len(self.roots) == self.limit:
            ui.label(f'Показаны первые {self.limit} найденных путей.').classes('s-muted text-xs p-3')

    #: Получает страницу дочерних элементов из сохранённого индекса цели.
    #: Обрабатывает ошибки: Exception.
    async def load(self, entry, *, more=False):
        key = entry['scan_id'], entry['path']
        generation, job_id = self.generation, self.workspace.job_id
        previous = self.folders.get(key, {}).get('entries', []) if more else []
        try:
            data = await self.workspace.request('GET', f'/api/storage/comparisons/{job_id}/target-tree',
                                                params={'scan_id': key[0], 'path': key[1], 'offset': len(previous), 'limit': 150}, timeout=45)
        except Exception as error:
            if generation != self.generation or job_id != self.workspace.job_id:
                return False
            self.folders[key] = {'entries': previous, 'error': self.workspace.error_text(error)}
        else:
            if generation != self.generation or job_id != self.workspace.job_id:
                return False
            self.folders[key] = {**data, 'entries': previous + data['entries']}
        return True

    #: Открывает найденный путь в контексте соответствующей цели отчёта.
    #: Асинхронно ожидает: self.open_folder, self.workspace.open_volume.
    async def open_path(self, path):
        if not self.selected:
            return
        scope, _ = self.selected
        boundary = scope['path']
        if boundary and path != boundary and not path.startswith(boundary + '/'):
            await self.workspace.open_volume(scope['volume_id'], 1, path=path)
            return
        entry = {'scan_id': scope['scan_id'], 'path': path, 'kind': 'directory',
                 'name': PurePosixPath(path).name or scope['volume_name']}
        await self.open_folder(entry, scope)

    #: Делает выбранную папку корнем отображаемого дерева совпадений.
    #: Обновляет состояние объекта: focus.
    async def open_folder(self, entry, scope):
        if entry['kind'] != 'directory':
            return
        boundary = scope['path']
        if boundary and entry['path'] != boundary and not entry['path'].startswith(boundary + '/'):
            return
        generation, job_id = self.generation, self.workspace.job_id
        await self.select(entry, scope, expand=True)
        if generation == self.generation and job_id == self.workspace.job_id:
            self.focus = scope, entry
            self.pane.render()

    #: Выбирает найденный элемент и при необходимости загружает или раскрывает ветвь.
    #: Обновляет состояние объекта: selected.
    async def select(self, entry, scope, *, expand=False, toggle=True, render=True):
        previous_volume = self.pane.volume_id
        already_active = self.workspace.active_index == 1
        key = entry['scan_id'], entry['path']
        self.selected = scope, entry
        pane = self.pane
        pane.volume_id, pane.path, pane.kind, pane.entry = scope['volume_id'], entry['path'], entry['kind'], entry
        pane.scan = next(s for s in self.workspace.report['scans'] if s['id'] == entry['scan_id'])
        self.workspace.set_active(1)
        if already_active and previous_volume != pane.volume_id:
            self.workspace.render_volumes()
        if entry['kind'] == 'directory' and (toggle or expand):
            if key in self.expanded and not expand:
                self.expanded.remove(key)
            else:
                if key not in self.folders and not await self.load(entry):
                    return
                self.expanded.add(key)
        if render:
            pane.render()
        else:
            pane.update_navigation_selection(entry, scope)
            pane.update_header()

        await self.workspace.preview_selection(pane)

    #: Догружает следующую страницу дочерних элементов сохранённого дерева.
    #: Асинхронно ожидает: self.load.
    async def more(self, entry):
        if await self.load(entry, more=True):
            self.pane.render()
