"""Folder bookmarks and copy relationship controls for the main workspace."""
from pathlib import PurePosixPath

from nicegui import ui

from media_manager.copies import COPY_KINDS, FOLDER_LABELS, copy_label, inherited_location


def disconnected(location):
    return not location.get('connected', True) or location.get('availability') == 'offline'


def sidebar_sections(groups):
    active, offline, count = [], [], 0
    for group in groups:
        disabled = not group.get('connected', True)
        main_offline = disabled or disconnected(group['main'])
        available = [c for c in group['copies'] if not disabled and not disconnected(c)]
        unavailable = [c for c in group['copies'] if disabled or disconnected(c)] + group.get('released_copies', [])
        if not main_offline or available:
            active.append((group, available))
        if main_offline or unavailable:
            offline.append((group, unavailable))
            count += int(main_offline) + len(unavailable)
    return active, offline, count


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
            with ui.expansion('Отключённые · 0', icon='link_off', value=False).props('dense').classes('s-volume-archive w-full') as self.disconnected:
                self.disconnected_list = ui.column().classes('copy-group-list w-full gap-0')

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
        active, offline, count = sidebar_sections(self.groups)
        self.section.text = f'Основные папки · {len(active)}'
        self.list.clear()
        self.disconnected_list.clear()
        self.disconnected.text = f'Отключённые · {count}'
        self.disconnected.set_visibility(bool(count))
        with self.list:
            if not self.groups:
                ui.label('Назначь папке 00-main, чтобы учитывать её копии.').classes('s-muted text-xs p-3')
            elif not active:
                ui.label('Все связанные папки отключены.').classes('s-muted text-xs p-3')
            for group, copies in active:
                self.render_group(group, copies)
        with self.disconnected_list:
            for group, copies in offline:
                self.render_group(group, copies)

    def render_group(self, group, copies):
        ws = self.workspace
        panes = getattr(ws, 'panes', [])
        left_member = self.membership(panes[0].volume_id, panes[0].path) if panes else None
        main = group['main']
        chosen = left_member and left_member['group_id'] == group['id']
        with ui.column().classes('copy-bookmark-group w-full gap-0'):
            with ui.button(on_click=lambda: self.open_main(group)).props('flat no-caps color=dark').classes(
                'copy-bookmark w-full' + (' chosen' if chosen else '') + (' disconnected' if disconnected(main) else '')
            ):
                if group.get('connected', True):
                    actions = [('Отключить набор', lambda: self.set_connection(group, False))]
                else:
                    actions = [('Подключить набор', lambda: self.set_connection(group, True)),
                               ('Удалить набор из учёта…', lambda: self.remove_group(group))]
                if group['numbering_changes']:
                    actions.insert(0, ('Упорядочить номера копий', lambda: self.renumber(group)))
                ws.property_menu('Свойства папки', lambda: ws.show_properties(main['volume_id'], dict(main, kind='directory')),
                                 volume_id=main['volume_id'], path=main['path'], extra=actions,
                                 extra_content=lambda action: self.folder_menu(group, action))
                with ui.row().classes('w-full items-center no-wrap gap-1'):
                    ui.label('00-main').classes('copy-label main')
                    ui.label(self.location_name(main)).classes('copy-bookmark-name')
                    if disconnected(main):
                        ui.icon('link_off', size='13px').props('aria-label="Основная папка отключена"')
                ui.label(self.location_path(main)).classes('copy-place')
                self.folder_badges(group)
            for location in copies:
                selected = panes and panes[1].volume_id == location['volume_id'] and panes[1].path == location['path']
                with ui.link(target='#').classes('copy-link' + (' chosen' if selected else '') + (' disconnected' if disconnected(location) else '')).on(
                    'click', lambda g=group, c=location: self.open_copy(g, c), args=[],
                    js_handler='event => { event.preventDefault(); emit(); }',
                ):
                    released = location.get('number_released', False)
                    actions = [('История копии', lambda c=location: ws.pair.history(group=group, location=c))]
                    if released:
                        actions.append(('Вернуть прежнюю привязку', lambda c=location: self.set_connection(group, True, c)))
                    else:
                        actions.append(('Изменить тип копии', lambda c=location: self.edit_kind(c)))
                    if not released and not group.get('connected', True):
                        actions.append(('Подключить набор', lambda: self.set_connection(group, True)))
                    elif not released:
                        connected = not location.get('connected', True)
                        actions.append(('Подключить копию' if connected else 'Отключить копию',
                                        lambda c=location, v=connected: self.set_connection(group, v, c)))
                    if not location.get('connected', True):
                        if not released:
                            actions.append((f"Освободить номер {location['number']:02d}…", lambda c=location: self.release_number(c)))
                        actions.append(('Удалить связь из учёта…', lambda c=location: self.remove_copy(c)))
                    ws.property_menu('Свойства папки', lambda c=location: ws.show_properties(c['volume_id'], dict(c, kind='directory')),
                                     volume_id=location['volume_id'], path=location['path'], extra=actions)
                    ui.label(location['label']).classes('copy-label')
                    ui.label(self.location_path(location)).classes('copy-link-name')
                    if disconnected(location):
                        ui.icon('link_off', size='13px').classes('shrink-0 s-muted').props('aria-label="Копия отключена"')

    def folder_badges(self, group):
        if not (group.get('tracking') or group.get('label') or group.get('changed_at')):
            return
        with ui.row().classes('copy-folder-tags'):
            if group.get('tracking'):
                state = group.get('tracking_state', 'starting')
                text = {'watching': 'Отслеживается', 'offline': 'Ожидает подключения',
                        'error': 'Отслеживание недоступно'}.get(state, 'Включение отслеживания…')
                if not group.get('connected', True):
                    text = 'Отслеживание приостановлено'
                ui.label(text).classes('copy-folder-tag tracking').tooltip(
                    group.get('tracking_error') or 'Изменения в основной папке и вложенных папках при работающем Core')
            if group.get('label'):
                ui.label(FOLDER_LABELS[group['label']]).classes('copy-folder-tag ' + group['label'])
            if group.get('changed_at'):
                ui.label('Есть изменения').classes('copy-folder-tag changed').tooltip(
                    'Последнее изменение: ' + self.workspace.format_date(group['changed_at']))

    def folder_menu(self, group, action):
        ui.separator()
        with ui.menu_item(on_click=action(lambda: self.set_folder_settings(group, tracking=not group.get('tracking', False)))).props(
            'role=menuitemcheckbox aria-checked=' + str(bool(group.get('tracking'))).lower()
        ):
            with ui.item_section().props('side'):
                ui.icon('check_box' if group.get('tracking') else 'check_box_outline_blank', size='18px')
            ui.item_section('Отслеживать изменения')
        if group.get('changed_at'):
            ui.menu_item('Изменения просмотрены', on_click=action(lambda: self.acknowledge_changes(group)))
        ui.separator()
        ui.label('Метка папки').classes('text-xs s-muted px-4 pt-2 pb-1')
        for value, text in FOLDER_LABELS.items():
            with ui.menu_item(on_click=action(lambda v=value: self.set_folder_settings(group, label=v))).props(
                'role=menuitemradio aria-checked=' + str(group.get('label', '') == value).lower()
            ):
                with ui.item_section().props('side'):
                    ui.icon('radio_button_checked' if group.get('label', '') == value else 'radio_button_unchecked', size='18px')
                ui.item_section(text)
        ui.separator()

    async def set_folder_settings(self, group, **settings):
        ws = self.workspace
        with ws.client:
            was_editing = ws.editing
            ws.editing = True
            try:
                await ws.request('PATCH', f"/api/storage/copy-groups/{group['id']}", json=settings)
                await self.refresh()
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = was_editing

    async def acknowledge_changes(self, group):
        ws = self.workspace
        with ws.client:
            was_editing = ws.editing
            ws.editing = True
            try:
                await ws.request('POST', f"/api/storage/copy-groups/{group['id']}/acknowledge",
                                 json={'changed_at': group['changed_at']})
                await self.refresh()
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = was_editing

    async def set_connection(self, group, connected, location=None):
        ws = self.workspace
        with ws.client:
            was_editing = ws.editing
            ws.editing = True
            try:
                affected = ws.pair.active and ws.pair.copy_id in {
                    c['id'] for c in ([location] if location else group['copies'])}
                if not connected and affected and getattr(ws.pair, 'copy_running', False):
                    raise ValueError('Сначала дождись завершения копирования.')
                endpoint = (f"/api/storage/copy-locations/{location['id']}" if location else
                            f"/api/storage/copy-groups/{group['id']}")
                await ws.request('PATCH', endpoint + '/connection', json={'connected': connected})
                if not connected and affected:
                    await ws.pair.unlink()
                await self.changed()
                if not connected:
                    self.disconnected.open()
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = was_editing

    def render_controls(self):
        if self.controls is None:
            return
        ws = self.workspace
        history_only = getattr(ws.pair, 'history_only', False)
        preview = any(getattr(p, 'view_mode', 'tree') == 'preview' for p in getattr(ws, 'panes', ()))
        self.controls.set_visibility(not bool(ws.report) and not history_only and not preview)
        if ws.report or history_only or preview:
            return
        left, right = ws.panes
        policy = tuple((g['id'], g['next_number'], g.get('connected', True),
                        tuple((c['id'], c['kind'], c['number'], c.get('connected', True)) for c in g['copies'])) for g in self.groups)
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
            if not group.get('connected', True):
                ui.label('Набор отключён. Связи и история сохранены.').classes('text-xs s-muted')
                ui.button('Подключить набор', on_click=lambda: self.set_connection(group, True)).props('outline dense no-caps color=green-9')
                ui.separator()
                return
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
            available = [c for c in group['copies'] if not disconnected(c)]
            if group['copies']:
                await ws.pair.link(group, min(available or group['copies'], key=lambda location: location['number']))
                return
            if ws.pair.active:
                await ws.pair.unlink()
            if ws.report:
                await ws.browse()
            await ws.panes[0].show_volume(group['main']['volume_id'], group['main']['path'])

    async def open_copy(self, group, location):
        ws = self.workspace
        with ws.client:
            if location.get('number_released'):
                await ws.pair.history(group=group, location=location)
            else:
                await ws.pair.link(group, location)

    async def release_number(self, location):
        ws = self.workspace
        with ws.client:
            was_editing = ws.editing
            ws.editing = True
            try:
                with ui.dialog() as dialog, ui.card().classes('w-[520px] max-w-full p-5 gap-3'):
                    ui.label(f"Освободить номер {location['number']:02d}?").classes('text-lg font-semibold')
                    ui.label(location['label'] + ' · ' + self.location_path(location)).classes('text-sm break-words')
                    ui.label('Прежняя привязка и её история останутся в «Отключённых». Номер можно будет использовать для новой папки.').classes('text-sm s-muted')
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                        ui.button('Освободить номер', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
                if not await dialog:
                    return
                await ws.request('POST', f"/api/storage/copy-locations/{location['id']}/release-number",
                                 json={'number': location['number'], 'kind': location['kind']})
                if ws.pair.active and ws.pair.copy_id == location['id']:
                    await ws.pair.unlink()
                await self.changed()
                self.disconnected.open()
                ui.notify('Номер освобождён, прежняя история сохранена', type='positive')
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = was_editing

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

    async def confirm_remove(self, title, *, locations=(), button_label='Удалить из учёта'):
        with ui.dialog() as dialog, ui.card().classes('w-[520px] max-w-full p-5 gap-3'):
            ui.label(title).classes('text-lg font-semibold')
            for location in locations:
                with ui.column().classes('w-full gap-0'):
                    ui.label(location['label']).classes('text-sm font-semibold')
                    ui.label(self.location_path(location)).classes('text-sm break-all')
            ui.label('Запись будет удалена из учёта приложения. Папки и файлы на дисках останутся.').classes('text-sm s-muted')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                ui.button(button_label, on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
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
            if await self.confirm_remove('Удалить набор и его связи из учёта?'):
                try:
                    await ws.request('DELETE', f"/api/storage/copy-groups/{group['id']}")
                    await self.changed()
                except Exception as error:
                    ws.notice(error)

    async def remove_copy(self, location):
        ws = self.workspace
        with ws.client:
            was_editing = ws.editing
            ws.editing = True
            try:
                await self.refresh()
                group = next((g for g in self.groups if g['id'] == location['group_id']), None)
                location = next((c for c in [*group['copies'], *group.get('released_copies', [])]
                                 if c['id'] == location['id']), None) if group else None
                if location is None:
                    raise ValueError('Эта связь с копией уже убрана из учёта.')
                if await self.confirm_remove('Убрать связь с копией?', locations=(group['main'], location), button_label='Убрать связь'):
                    await ws.request('DELETE', f"/api/storage/copy-locations/{location['id']}")
                    if ws.pair.active and ws.pair.copy_id == location['id']:
                        await ws.pair.unlink()
                    await self.changed()
                    group = next((g for g in self.groups if g['id'] == location['group_id']), None)
                    if group and group['numbering_changes']:
                        await self.renumber(group)
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = was_editing
