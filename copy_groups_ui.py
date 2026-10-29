"""Folder bookmarks and copy relationship controls for the main workspace."""
from pathlib import PurePosixPath

from nicegui import ui

from media_manager.copies import COPY_KINDS, copy_label, inherited_location


class CopyGroupsUI:
    def __init__(self, workspace):
        self.workspace = workspace
        self.groups = []
        self.loaded = False
        self.controls = None
        self.control_signature = None
        self.kind_context = None
        self.kind = 'copy'

    def build_sidebar(self):
        with ui.expansion('Основные папки · 0', icon='folder_copy', value=True).props('dense').classes('copy-section w-full') as self.section:
            self.list = ui.column().classes('copy-group-list w-full gap-0')

    def build_controls(self):
        self.controls = ui.column().classes('w-full gap-2')

    @staticmethod
    def location_name(location):
        return PurePosixPath(location['path']).name if location['path'] else location['volume_name']

    @staticmethod
    def location_path(location):
        return location['volume_name'] + ' /' + location['path']

    def membership(self, volume_id, path):
        locations = [location for group in self.groups for location in [group['main'], *group['copies']]
                     if location['volume_id'] == volume_id]
        return inherited_location(path, locations)

    def main_group(self):
        left = self.workspace.panes[0]
        if left.kind != 'directory':
            return None
        return next((g for g in self.groups if g['main']['volume_id'] == left.volume_id and g['main']['path'] == left.path), None)

    async def refresh(self):
        self.groups = (await self.workspace.request('GET', '/api/storage/copy-groups', timeout=30))['groups']
        if not self.loaded and self.groups:
            self.workspace.volumes_section.close()
        self.loaded = True
        self.render_sidebar()
        self.render_controls()

    def render_sidebar(self):
        self.section.text = f'Основные папки · {len(self.groups)}'
        self.list.clear()
        ws = self.workspace
        panes = getattr(ws, 'panes', [])
        left_member = self.membership(panes[0].volume_id, panes[0].path) if panes else None
        with self.list:
            if not self.groups:
                ui.label('Назначь папке 00-main, чтобы учитывать её копии.').classes('s-muted text-xs p-3')
            for group in self.groups:
                main = group['main']
                chosen = left_member and left_member['group_id'] == group['id']
                with ui.column().classes('copy-bookmark-group w-full gap-0'):
                    with ui.button(on_click=lambda g=group: self.open_main(g)).props('flat no-caps color=dark').classes('copy-bookmark w-full' + (' chosen' if chosen else '')):
                        actions = [('Убрать учёт этой папки', lambda g=group: self.remove_group(g))]
                        if group['numbering_changes']:
                            actions.insert(0, ('Упорядочить номера копий', lambda g=group: self.renumber(g)))
                        ws.property_menu('Свойства папки', lambda m=main: ws.show_properties(m['volume_id'], dict(m, kind='directory')),
                                         extra=actions)
                        with ui.row().classes('w-full items-center no-wrap gap-1'):
                            ui.label('00-main').classes('copy-label main')
                            ui.label(self.location_name(main)).classes('copy-bookmark-name')
                        ui.label(self.location_path(main)).classes('copy-place')
                    for location in group['copies']:
                        selected = panes and panes[1].volume_id == location['volume_id'] and panes[1].path == location['path']
                        with ui.link(target='#').classes('copy-link' + (' chosen' if selected else '')).on(
                            'click', lambda g=group, c=location: self.open_copy(g, c), args=[],
                            js_handler='event => { event.preventDefault(); emit(); }',
                        ):
                            ws.property_menu('Свойства папки', lambda c=location: ws.show_properties(c['volume_id'], dict(c, kind='directory')),
                                             extra=[('Изменить тип копии', lambda c=location: self.edit_kind(c)),
                                                    ('Убрать ссылку на копию', lambda c=location: self.remove_copy(c))])
                            ui.label(location['label']).classes('copy-label')
                            ui.label(self.location_path(location)).classes('copy-link-name')
                            if location['availability'] != 'online':
                                ui.icon('link_off', size='13px').classes('shrink-0 s-muted').props('aria-label="Том недоступен"')

    def render_controls(self):
        if self.controls is None:
            return
        ws = self.workspace
        self.controls.set_visibility(not bool(ws.report))
        if ws.report:
            return
        left, right = ws.panes
        policy = tuple((g['id'], g['next_number'], tuple((c['id'], c['kind'], c['number']) for c in g['copies'])) for g in self.groups)
        signature = (left.volume_id, left.path, left.kind, right.volume_id, right.path, right.kind, policy,
                     (left.volume or {}).get('identity_status'), (right.volume or {}).get('identity_status'))
        if signature == self.control_signature:
            return
        self.control_signature = signature
        self.controls.clear()
        with self.controls:
            ui.label('Учёт копий').classes('workspace-operation-title')
            group = self.main_group()
            member = self.membership(left.volume_id, left.path)
            if not group:
                if member:
                    ui.label(member['label'] + ' · метка папки и её вложенных папок').classes('text-xs s-muted')
                    parent = next(g for g in self.groups if g['id'] == member['group_id'])
                    ui.button('К основной папке', on_click=lambda g=parent: self.open_main(g)).props('flat dense no-caps color=green-9')
                elif left.kind == 'directory' and left.path and left.volume and left.volume.get('identity_status') not in ('unverified', 'legacy'):
                    ui.label(PurePosixPath(left.path).name if left.path else left.volume['name']).classes('text-xs s-muted break-words')
                    ui.button('Назначить 00-main', on_click=lambda v=left.volume_id, p=left.path: self.register_main(v, p)).props('outline dense no-caps color=green-9').classes('w-full')
                else:
                    ui.label('Выбери основную папку слева.').classes('text-xs s-muted')
                ui.separator()
                return
            ui.label('00-main · ' + self.location_name(group['main'])).classes('text-xs s-muted break-words')
            if group['numbering_changes']:
                ui.label('В нумерации копий есть пропуски. Согласуй новые метки перед добавлением копии.').classes('text-xs s-muted')
                ui.button('Упорядочить номера копий', on_click=lambda g=group: self.renumber(g)).props('outline dense no-caps color=green-9').classes('w-full')
                ui.separator()
                return
            destination = {'volume_id': right.volume_id, 'path': right.path}
            valid = right.kind == 'directory' and right.path and right.volume and right.volume.get('identity_status') not in ('unverified', 'legacy')
            if not valid:
                ui.label('Выбери папку назначения справа.').classes('text-xs s-muted')
                ui.separator()
                return
            ui.label('Назначение: ' + right.volume['name'] + ' /' + right.path).classes('workspace-scopes w-full')
            existing = self.membership(right.volume_id, right.path)
            if existing:
                ui.label('Папка уже входит в ' + existing['label'] + '.').classes('text-xs s-muted')
                ui.separator()
                return
            context = group['id'], right.volume_id
            if context != self.kind_context:
                self.kind_context = context
                self.kind = 'cold' if right.volume.get('removable') else 'copy'
            holder = {}

            def changed(event):
                if self.kind_context == context:
                    self.kind = event.value
                    if holder.get('button'):
                        holder['button'].text = 'Связать как ' + copy_label(self.kind, group['next_number'])

            ui.select(COPY_KINDS, value=self.kind, label='Тип копии', on_change=changed).props('outlined dense').classes('w-full')
            holder['button'] = ui.button('Связать как ' + copy_label(self.kind, group['next_number']),
                                        on_click=lambda g=group, d=destination: self.add_copy(g, d, self.kind)).props('unelevated dense no-caps color=green-9').classes('w-full text-xs')
            ui.separator()

    def context_actions(self, volume_id, entry):
        if self.workspace.report or entry['kind'] != 'directory' or self.membership(volume_id, entry['path']):
            return []
        return [('Назначить 00-main', lambda: self.register_main(volume_id, entry['path']))]

    async def changed(self):
        await self.refresh()
        for pane in self.workspace.panes:
            pane.render()
        self.workspace.update_scopes()

    async def register_main(self, volume_id, path):
        ws = self.workspace
        with ws.client:
            try:
                group = await ws.request('POST', '/api/storage/copy-groups', json={'volume_id': volume_id, 'path': path})
                await self.changed()
                ws.volumes_section.close()
                self.section.open()
                await self.open_main(group)
                ui.notify('Основная папка 00-main добавлена', type='positive')
            except Exception as error:
                ws.notice(error)

    async def add_copy(self, group, destination, kind):
        ws = self.workspace
        with ws.client:
            try:
                result = await ws.request('POST', f"/api/storage/copy-groups/{group['id']}/copies", json={**destination, 'kind': kind})
                await self.changed()
                location = next(c for c in result['copies'] if c['volume_id'] == destination['volume_id'] and c['path'] == destination['path'])
                ui.notify('Ссылка ' + location['label'] + ' сохранена', type='positive')
            except Exception as error:
                ws.notice(error)

    async def open_main(self, group):
        ws = self.workspace
        with ws.client:
            if ws.pair.active:
                await ws.pair.unlink()
            if ws.report:
                await ws.browse()
            await ws.panes[0].show_volume(group['main']['volume_id'], group['main']['path'])

    async def open_copy(self, group, location):
        ws = self.workspace
        with ws.client:
            await ws.pair.link(group, location)

    async def edit_kind(self, location):
        ws = self.workspace
        with ws.client:
            ws.editing = True
            try:
                with ui.dialog() as dialog, ui.card().classes('w-[400px] max-w-full p-5 gap-3'):
                    ui.label('Тип копии · ' + location['label']).classes('text-lg font-semibold')
                    kind = ui.select(COPY_KINDS, value=location['kind'], label='Тип копии').props('outlined dense').classes('w-full')
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                        ui.button('Сохранить', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
                if await dialog:
                    await ws.request('PATCH', f"/api/storage/copy-locations/{location['id']}", json={'kind': kind.value})
                    await self.changed()
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = False

    async def confirm_remove(self, title):
        with ui.dialog() as dialog, ui.card().classes('w-[420px] max-w-full p-5 gap-3'):
            ui.label(title).classes('text-lg font-semibold')
            ui.label('Убирается только запись из учёта копий.').classes('text-sm s-muted')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button('Убрать из учёта', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
        return await dialog

    async def renumber(self, group):
        ws = self.workspace
        with ws.client:
            was_editing = ws.editing
            ws.editing = True
            try:
                # Refresh the proposal before asking; the API checks this snapshot again on save.
                await self.refresh()
                group = next((g for g in self.groups if g['id'] == group['id']), None)
                if not group or not group['numbering_changes']:
                    return
                by_id = {copy['id']: copy for copy in group['copies']}
                with ui.dialog() as dialog, ui.card().classes('w-[520px] max-w-full p-5 gap-3'):
                    ui.label('Упорядочить номера копий?').classes('text-lg font-semibold')
                    ui.label(self.location_name(group['main'])).classes('text-sm font-semibold')
                    for change in group['numbering_changes']:
                        with ui.column().classes('w-full gap-0'):
                            ui.label(change['from_label'] + ' → ' + change['to_label']).classes('text-sm font-mono')
                            ui.label(self.location_path(by_id[change['id']])).classes('text-xs s-muted break-words')
                    ui.label('Изменятся только метки связей. Имена папок на дисках сохранятся.').classes('text-sm s-muted')
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Позже', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                        ui.button('Переименовать метки', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
                if await dialog:
                    snapshot = [{key: copy[key] for key in ('id', 'kind', 'number')} for copy in group['copies']]
                    await ws.request('POST', f"/api/storage/copy-groups/{group['id']}/renumber", json={'copies': snapshot})
                    await self.changed()
                    ui.notify('Номера копий упорядочены', type='positive')
            except Exception as error:
                await self.changed()
                ws.notice(error)
            finally:
                ws.editing = was_editing

    async def remove_group(self, group):
        ws = self.workspace
        with ws.client:
            if await self.confirm_remove('Убрать основную папку и ссылки на её копии?'):
                try:
                    await ws.request('DELETE', f"/api/storage/copy-groups/{group['id']}")
                    await self.changed()
                except Exception as error:
                    ws.notice(error)

    async def remove_copy(self, location):
        ws = self.workspace
        with ws.client:
            ws.editing = True
            try:
                if await self.confirm_remove('Убрать ссылку ' + location['label'] + '?'):
                    await ws.request('DELETE', f"/api/storage/copy-locations/{location['id']}")
                    await self.changed()
                    group = next((g for g in self.groups if g['id'] == location['group_id']), None)
                    if group and group['numbering_changes']:
                        await self.renumber(group)
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = False
