"""Folder bookmarks and copy relationship controls for the main workspace."""
from pathlib import PurePosixPath

from nicegui import ui

from copy_panels import disconnected, first_copy
from media_manager.copies import COPY_KINDS, FOLDER_LABELS, copy_label, inherited_location
from sidebar_ui import sidebar_branch, sidebar_line


#: Разделяет наборы и копии на подключённые и архивные секции.
#: Использует active.append, disconnected, group.get, offline.append.
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


#: Показывает наборы папок и выполняет команды учёта через Core API.
#: Зависимости конструктора: workspace.
class CopyGroupsUI:
    #: Инициализирует CopyGroupsUI и его рабочее состояние.
    #: Обновляет состояние объекта: control_signature, controls, expanded, groups, workspace.
    def __init__(self, workspace):
        self.workspace = workspace
        self.groups = []
        self.controls = None
        self.control_signature = None
        self.expanded = set()

    #: Создаёт боковые секции основных папок и отключённых связей.
    #: Обновляет состояние объекта: disconnected, disconnected_list, list, section.
    def build_sidebar(self):
        with self.workspace.sidebar_expansion('copy_groups', 'Основные папки · 0', icon='folder_copy') as self.section:
            self.list = ui.column().classes('sidebar-list w-full')
            with self.workspace.sidebar_expansion('copy_archive', 'Отключённые · 0', icon='link_off') as self.disconnected:
                self.disconnected_list = ui.column().classes('sidebar-list w-full')

    #: Создаёт контейнер команд назначения основной папки и копии.
    #: Обновляет состояние объекта: controls.
    def build_controls(self):
        self.controls = ui.column().classes('w-full gap-2')

    #: Возвращает короткое название зарегистрированной папки.
    #: Использует PurePosixPath.
    @staticmethod
    def location_name(location):
        return PurePosixPath(location['path']).name if location['path'] else location['volume_name']

    #: Формирует подпись расположения с томом и относительным путём.
    #: Параметры: location.
    @staticmethod
    def location_path(location):
        return location['volume_name'] + ' /' + location['path']

    #: Находит наследуемую принадлежность пути зарегистрированной области.
    #: Использует group.get, inherited_location, location.get.
    def membership(self, volume_id, path):
        locations = [location for group in self.groups if group.get('connected', True)
                     for location in [group['main'], *group['copies']]
                     if location.get('connected', True) and location['volume_id'] == volume_id]
        return inherited_location(path, locations)

    #: Определяет набор основной папки в текущей выбранной области.
    #: Использует next.
    def main_group(self):
        left = self.workspace.panes[0]
        if left.kind != 'directory':
            return None
        return next((g for g in self.groups if g['main']['volume_id'] == left.volume_id and g['main']['path'] == left.path), None)

    #: Загружает актуальные наборы, типы копий и смысловые метки через API.
    #: Обновляет состояние объекта: groups.
    async def refresh(self):
        self.groups = (await self.workspace.request('GET', '/api/storage/copy-groups', timeout=30))['groups']
        self.render_sidebar()
        self.render_controls()

    #: Перерисовывает подключённые и архивные наборы папок.
    #: Использует self.disconnected.set_visibility, self.disconnected_list.clear, self.list.clear, self.render_group, sidebar_sections.
    def render_sidebar(self):
        active, offline, count = sidebar_sections(self.groups)
        self.section.text = f'Основные папки · {len(active)}'
        self.list.clear()
        self.disconnected_list.clear()
        self.disconnected.text = f'Отключённые · {count}'
        self.disconnected.set_visibility(bool(count))
        with self.list:
            if not self.groups:
                ui.label('Основных папок пока нет').classes('sidebar-empty')
            elif not active:
                ui.label('Все папки отключены').classes('sidebar-empty')
            for group, copies in active:
                self.render_group(group, copies)
        with self.disconnected_list:
            for group, copies in offline:
                self.render_group(group, copies, archive=True)

    #: Показывает заголовок основной папки и раскрываемые строки её копий.
    #: Ключ архивной строки хранится отдельно от ключа подключённого набора.
    def render_group(self, group, copies, *, archive=False):
        key = ('archive', group['id']) if archive else group['id']
        with sidebar_branch(self.expanded, key, copies, lambda toggle: self.main_row(group, copies, toggle)):
            for location in copies:
                self.copy_row(group, location)

    #: Формирует компактную строку основной папки и её контекстные действия.
    #: Подробности отслеживания и полный путь доступны в подсказке.
    def main_row(self, group, copies, toggle):
        ws = self.workspace
        main = group['main']
        panes = getattr(ws, 'panes', [])
        member = self.membership(panes[0].volume_id, panes[0].path) if panes else None
        offline = not group.get('connected', True) or disconnected(main)
        if group.get('connected', True):
            actions = [('Отключить набор', lambda: self.set_connection(group, False))]
            if not offline and not group['numbering_changes']:
                actions.insert(0, ('Добавить копию…', lambda: ws.copy_setup.open(main['volume_id'], main['path'])))
        else:
            actions = [('Подключить набор', lambda: self.set_connection(group, True)),
                       ('Удалить набор из учёта…', lambda: self.remove_group(group))]
        if group['numbering_changes']:
            actions.insert(0, ('Упорядочить номера копий', lambda: self.renumber(group)))
        detail = ['00-main', self.location_path(main)]
        if group.get('label'):
            detail.append(FOLDER_LABELS[group['label']])
        if group.get('tracking'):
            detail.append(group.get('tracking_error') or {
                'watching': 'Отслеживается', 'offline': 'Ожидает подключения', 'error': 'Отслеживание недоступно'
            }.get(group.get('tracking_state'), 'Включение отслеживания…'))
        if group.get('changed_at'):
            detail.append('Последнее изменение · ' + ws.format_date(group['changed_at']))
        tooltip = ' · '.join(detail)
        chosen = bool(member and member['group_id'] == group['id'])
        with sidebar_line(self.location_name(main), lambda: self.open_main(group), tooltip=tooltip, toggle=toggle,
                          icon='link_off' if offline else 'folder', offline=offline, chosen=chosen) as row:
            status = 'Офлайн' if offline else 'Изменено' if group.get('changed_at') else f'{len(copies)} коп.' if copies else ''
            if status:
                ui.label(status).classes('sidebar-readout truncate').tooltip(tooltip)
            ws.property_menu('Свойства папки', lambda: ws.show_properties(main['volume_id'], dict(main, kind='directory')),
                             volume_id=main['volume_id'], path=main['path'], extra=actions,
                             extra_content=lambda action: self.folder_menu(group, action), row=row)

    #: Показывает короткий адрес, метку и действия отдельной обычной копии.
    #: Сохраняет историю и управление архивными привязками.
    def copy_row(self, group, location):
        ws = self.workspace
        panes = getattr(ws, 'panes', [])
        selected = bool(panes and panes[1].volume_id == location['volume_id'] and panes[1].path == location['path'])
        released = location.get('number_released', False)
        offline = disconnected(location) or not group.get('connected', True)
        actions = [('История копии', lambda: ws.pair.history(group=group, location=location))]
        if released:
            actions.append(('Вернуть прежнюю привязку', lambda: self.set_connection(group, True, location)))
        else:
            if not offline:
                actions.insert(0, ('Открыть для сверки', lambda: self.open_copy(group, location)))
                actions.insert(1, ('Добавить следующую копию…',
                                   lambda: ws.copy_setup.open(location['volume_id'], location['path'])))
            actions.extend((('Изменить тип копии', lambda: self.edit_kind(location)),
                            ('Источник копирования…', lambda: self.choose_source(group, location))))
        if not released and not group.get('connected', True):
            actions.append(('Подключить набор', lambda: self.set_connection(group, True)))
        elif not released:
            connected = not location.get('connected', True)
            actions.append(('Подключить копию' if connected else 'Отключить копию',
                            lambda: self.set_connection(group, connected, location)))
        if not location.get('connected', True):
            if not released:
                actions.append((f"Освободить номер {location['number']:02d}…", lambda: self.release_number(location)))
            actions.append(('Удалить связь из учёта…', lambda: self.remove_copy(location)))
        detail = self.location_path(location)
        if location.get('source_location_id'):
            detail = location['source_label'] + ' → ' + detail
        with sidebar_line(f"{location['label']} · {location['volume_name']}", lambda: self.open_copy(group, location),
                          tooltip=detail, chosen=selected, offline=offline, indented=True) as row:
            if offline:
                ui.label('Офлайн').classes('sidebar-readout truncate')
            ws.property_menu('Свойства папки', lambda: ws.show_properties(location['volume_id'], dict(location, kind='directory')),
                             volume_id=location['volume_id'], path=location['path'], extra=actions, row=row)

    #: Создаёт команды настройки основной папки и отслеживания изменений.
    #: Использует FOLDER_LABELS.items, action, group.get, str(bool(group.get('tracking'))).lower, str(group.get('label', '') == value).lower.
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

    #: Сохраняет настройки набора и обновляет связанные сведения UI.
    #: Обрабатывает ошибки: Exception.
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

    #: Подтверждает просмотр конкретной отметки изменения основной папки.
    #: Обрабатывает ошибки: Exception.
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

    #: Подключает или отключает набор либо отдельную копию через API.
    #: Явно отклоняет недопустимое состояние через ValueError.
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

    #: Обновляет быстрые команды учёта в правой колонке операций.
    #: Действие добавления открывает общий диалог выбора назначения.
    def render_controls(self):
        if self.controls is None:
            return
        ws = self.workspace
        history_only = getattr(ws.pair, 'history_only', False)
        virtual_pair = bool((getattr(ws.pair, 'group', None) or {}).get('virtual_id'))
        browse_only = virtual_pair or any(getattr(p, 'view_mode', 'tree') == 'preview' or (p.volume or {}).get('kind') in ('photos', 'icloud')
                                          for p in getattr(ws, 'panes', ()))
        choosing_copy = bool(getattr(getattr(ws, 'copy_setup', None), 'draft', None))
        if ws.report or history_only or browse_only or choosing_copy:
            self.controls.set_visibility(False)
            return
        left = ws.panes[0]
        group = self.main_group()
        member = self.membership(left.volume_id, left.path)
        self.controls.set_visibility(bool(group or member))
        if not group and not member:
            return
        signature = (left.volume_id, left.path, (member or {}).get('id'),
                     (group or {}).get('id'), (group or {}).get('connected'), (group or {}).get('numbering_changes'))
        if signature == self.control_signature:
            return
        self.control_signature = signature
        self.controls.clear()
        with self.controls:
            ui.label('Учёт копий').classes('workspace-operation-title')
            if group:
                ui.label('00-main · ' + self.location_name(group['main'])).classes('text-xs s-muted break-words')
                if not group.get('connected', True):
                    ui.button('Подключить набор', on_click=lambda: self.set_connection(group, True)).props('outline dense no-caps color=green-9')
                    return
                if group['numbering_changes']:
                    ui.button('Упорядочить номера копий', on_click=lambda: self.renumber(group)).props(
                        'outline dense no-caps color=green-9').classes('w-full')
                    return
            if member and not group:
                parent = next(g for g in self.groups if g['id'] == member['group_id'])
                ui.button('К основной папке', on_click=lambda: self.open_main(parent)).props('flat dense no-caps color=green-9')

    #: Предоставляет команды учёта для контекстного меню выбранной папки.
    #: Использует self.membership.
    def context_actions(self, volume_id, entry, *, index=None):
        ws = self.workspace
        if ws.report or entry['kind'] != 'directory':
            return []
        path = entry['path']
        actions = []
        source = ws.copy_setup.source(volume_id, path)
        if source:
            actions.append(('Добавить копию…', lambda: ws.copy_setup.open(volume_id, path, index=index)))
        if not self.membership(volume_id, path) and path and (not source or source['kind'] == 'folder'):
            actions.append(('Назначить основной папкой', lambda: self.register_main(volume_id, path)))
        return actions

    #: Обновляет наборы, тома, медиатеки и видимые метки после изменения связей.
    #: Асинхронно ожидает: self.refresh.
    async def changed(self):
        await self.refresh()
        for pane in self.workspace.panes:
            pane.render()
        self.workspace.update_scopes()

    #: Регистрирует выбранную папку как новую основную область 00-main.
    #: Обрабатывает ошибки: Exception.
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

    #: Открывает основную папку в рабочем пространстве.
    #: Асинхронно ожидает: ws.browse, ws.pair.link, ws.pair.unlink, ws.panes[0].show_volume.
    async def open_main(self, group):
        ws = self.workspace
        with ws.client:
            if copy := first_copy(group['copies']):
                await ws.pair.link(group, copy)
                return
            if ws.pair.active:
                await ws.pair.unlink()
            if ws.report:
                await ws.browse()
            await ws.panes[0].show_volume(group['main']['volume_id'], group['main']['path'])

    #: Открывает зарегистрированную пару источника и копии.
    #: Асинхронно ожидает: ws.pair.history, ws.pair.link.
    async def open_copy(self, group, location):
        ws = self.workspace
        with ws.client:
            if location.get('number_released'):
                await ws.pair.history(group=group, location=location)
            else:
                await ws.pair.link(group, location)

    #: Показывает выбор основной или другой копии как источника назначения.
    #: Обрабатывает ошибки: Exception.
    async def choose_source(self, group, location):
        ws = self.workspace
        with ws.client:
            ws.editing = True
            try:
                choices = {c['id']: c['label'] + ' · ' + self.location_path(c)
                           for c in [group['main'], *group['copies']]
                           if c['id'] != location['id'] and c.get('connected', True)}
                with ui.dialog() as dialog, ui.card().classes('w-[600px] max-w-full p-5 gap-3'):
                    ui.label('Источник для ' + location['label']).classes('text-lg font-semibold')
                    current = location.get('source_location_id') or group['main']['id']
                    selected = ui.select(choices, value=current if current in choices else None, label='Копировать из').classes('w-full').props('outlined')
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Отмена', on_click=lambda:dialog.submit(None)).props('flat no-caps')
                        ui.button('Сохранить', on_click=lambda:dialog.submit(selected.value)).props('no-caps')
                source = await dialog
                if source:
                    await ws.request('PATCH', f"/api/storage/copy-locations/{location['id']}/source", json={'source_id':source})
                    if ws.pair.active and ws.pair.copy_id == location['id']:
                        await ws.pair.unlink()
                    await self.changed()
            except Exception as error:
                ws.notice(error)
            finally:
                ws.editing = False

    #: Запрашивает подтверждение освобождения номера отключённой копии.
    #: Обрабатывает ошибки: Exception.
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

    #: Показывает смену типа обычной, сменной или облачной копии.
    #: Обрабатывает ошибки: Exception.
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

    #: Показывает подтверждение удаления связей с явными путями папок.
    #: Использует self.location_path, ui.button, ui.button('Отмена', on_click=lambda : dialog.submit(False)).props и ещё 2.
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

    #: Показывает и подтверждает рассчитанные изменения номеров копий.
    #: Обрабатывает ошибки: Exception.
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

    #: Удаляет подтверждённый набор из учёта через API.
    #: Обрабатывает ошибки: Exception.
    async def remove_group(self, group):
        ws = self.workspace
        with ws.client:
            if await self.confirm_remove('Удалить набор и его связи из учёта?'):
                try:
                    await ws.request('DELETE', f"/api/storage/copy-groups/{group['id']}")
                    await self.changed()
                except Exception as error:
                    ws.notice(error)

    #: Удаляет подтверждённую связь копии из учёта через API.
    #: Явно отклоняет недопустимое состояние через ValueError.
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
