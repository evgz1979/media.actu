"""One destination picker for folder, Photos and iCloud Drive copy bindings."""
from pathlib import PurePosixPath

from nicegui import ui

from media_manager.copies import COPY_KINDS
from media_manager.icloud_copies import ICLOUD_VOLUME_ID
from media_manager.storage import relative_path


COPY_SETUP_CSS = """
.pane-add-copy.q-btn { flex-shrink:0; padding:1px 6px; font-size:11px; min-height:27px; }
.pane-add-copy .q-btn__content { flex-wrap:nowrap; }
.pane-add-copy .q-icon { font-size:15px; margin-right:3px; }
.copy-setup.q-card { width:min(550px,calc(100vw - 28px)); padding:18px; gap:10px; }
.copy-setup-path { padding:6px 8px; background:#edf4eb; border-radius:4px; color:#36563e; }
.copy-setup-folders { max-height:min(34vh,255px); min-height:50px; overflow-y:auto; border:1px solid #dfe6dc; border-radius:4px; }
.copy-setup-folders .q-btn { justify-content:flex-start; min-height:27px; padding:2px 7px; font-size:12px; }
.copy-setup-folders .q-btn__content { flex-wrap:nowrap; justify-content:flex-start; text-align:left; }
.copy-setup-folders .q-icon { font-size:15px; margin-right:5px; }
"""


#: Формирует читаемый путь по короткому имени тома и пути внутри него.
#: Возвращает имя тома для корня.
def scope_title(volume, path):
    name = volume.get('display_name') or volume['name']
    return f'{name} /{path}' if path else name


#: Определяет подключённый том, пригодный для выбора папки копии.
#: Проверяет сохранённую идентичность и доступность.
def copy_volume(volume):
    return bool(volume and volume['kind'] not in ('photos', 'icloud') and volume['availability'] == 'online'
                and volume.get('identity_status') not in ('unverified', 'legacy'))


#: Показывает адрес и предыдущие звенья выбранной копии Photos.
#: Недоступное звено отображается отдельно от прямого маршрута Photos.
def photo_route(library, link_id):
    copies = {copy['id']: copy for copy in library['copies']}
    nodes, seen = [], set()
    while link_id and link_id in copies and link_id not in seen:
        seen.add(link_id)
        copy = copies[link_id]
        nodes.append(f"{copy['number']:02d}-copy · {copy['volume_name']}")
        link_id = copy.get('source_link_id')
    nodes.append('Недоступная копия' if link_id else library.get('label') or 'Photos')
    return ' → '.join(reversed(nodes))


#: Управляет общим диалогом «Из → Куда» и обновляет созданные связи.
#: Зависимость конструктора: workspace.
class CopySetupUI:
    #: Сохраняет рабочее пространство и состояние диалога.
    #: Обновляет состояние объекта: ws, opened.
    def __init__(self, workspace):
        self.ws = workspace
        self.opened = False

    #: Определяет допустимый источник из дерева, бокового списка или панели операций.
    #: Для Photos выбирает всю медиатеку, для iCloud Drive сохраняет выбранную папку.
    def source(self, volume_id, path, entry_kind='directory'):
        volume = self.ws.resolve_volume(volume_id)
        if not volume:
            return None
        if volume['kind'] == 'photos':
            return dict(kind='photos', volume_id=volume_id, path='', library=volume['library'])
        if entry_kind != 'directory':
            return None
        if volume_id == ICLOUD_VOLUME_ID and volume['availability'] == 'online':
            return dict(kind='icloud', volume_id=volume_id, path=path)
        if not path or not copy_volume(volume):
            return None
        member = self.ws.copies.membership(volume_id, path)
        if member and (member['number'] != 0 or not member['is_root']):
            return None
        return dict(kind='folder', volume_id=volume_id, path=path)

    #: Выбирает доступную папку из панели напротив источника как быстрый вариант назначения.
    #: Поддерживает вызов из любого дерева и из боковой колонки.
    def suggested(self, source, index):
        if index is None:
            active = self.ws.active_index
            index = next((i for i in (active, 1 - active)
                          if self.ws.panes[i].display_volume_id == source['volume_id']), 0)
        scope = self.ws.panes[1 - index].scope()
        if (scope and scope['path'] and copy_volume(self.ws.resolve_volume(scope['volume_id']))
                and (scope['volume_id'], scope['path']) != (source['volume_id'], source['path'])):
            return scope
        return None

    #: Открывает диалог и показывает созданную строку копии после принятой связи.
    #: Асинхронно ожидает: self.destination, self.ws.copies.changed, self.ws.photo_libraries.refresh.
    async def open(self, volume_id, path='', *, index=None, preferred_kind=None):
        if self.opened:
            return
        source = self.source(volume_id, path)
        if not source:
            ui.notify('Выбери медиатеку, папку iCloud Drive или основную папку набора.', type='info')
            return
        volumes = {volume['id']: volume for volume in self.ws.volumes if copy_volume(volume)}
        if not volumes:
            ui.notify('Подключи подтверждённый том для копии.', type='warning')
            return
        self.opened = True
        was_editing = self.ws.editing
        self.ws.editing = True
        try:
            result = await self.destination(source, volumes, self.suggested(source, index), preferred_kind)
            if result is None:
                return
            ui.notify('Связь копии сохранена', type='positive')
            if source['kind'] == 'folder':
                self.ws.copies.expanded.add(result['id'])
                await self.ws.copies.changed()
                self.ws.copies.section.open()
            else:
                libraries = self.ws.photo_libraries
                libraries.expanded.add(source['library']['id'] if source['kind'] == 'photos' else ICLOUD_VOLUME_ID)
                libraries.signature = None
                await libraries.refresh()
                libraries.section.open()
        except Exception as error:
            self.ws.notice(error)
        finally:
            self.opened = False
            self.ws.editing = was_editing

    #: Сохраняет настроенную связь через API соответствующего источника.
    #: Асинхронно ожидает: self.ws.request.
    async def save(self, source, target, kind, upstream, cloud_root):
        if source['kind'] == 'folder':
            origin = {key: source[key] for key in ('volume_id', 'path')}
            return await self.ws.request('POST', '/api/storage/folder-copy-bindings',
                                         json=dict(source=origin, destination=dict(target, kind=kind)))
        if source['kind'] == 'photos':
            return await self.ws.request('POST', f"/api/photos/libraries/{source['library']['id']}/copies",
                                         json=dict(target, source_link_id=upstream or None))
        return await self.ws.request('POST', '/api/icloud/copies',
                                     json=dict(target, source_path='' if cloud_root else source['path']))

    #: Показывает источник, маршрут и выбор папки назначения в одном диалоге.
    #: Сохраняет окно открытым при ошибке чтения или отказе Core.
    async def destination(self, source, volumes, suggestion, preferred_kind):
        source_volume = self.ws.resolve_volume(source['volume_id'])
        library = source.get('library')
        all_copies = sorted(library['copies'], key=lambda c: c['number']) if library else []
        direct = next((copy for copy in all_copies if not copy.get('source_link_id')), None)
        upstream_choices = {}
        for copy in all_copies:
            title = f"{copy['number']:02d}-copy · {copy['volume_name']}"
            upstream_choices[copy['id']] = title + (' · офлайн' if copy['availability'] != 'online' else '')

        state = dict(volume_id=None, path='', generation=0, ready=False, saving=False)
        folder_kind = source['kind'] == 'folder'
        with ui.dialog().props('persistent') as dialog, ui.card().classes('copy-setup'):
            ui.label('Добавить копию').classes('text-lg font-semibold')
            ui.label('Из').classes('text-xs font-semibold s-muted')
            origin = ui.label().classes('copy-setup-path w-full break-all')
            upstream = None
            if all_copies:
                upstream = ui.select(upstream_choices, value=(direct or all_copies[0])['id'],
                                     label='Копировать из').props('dense outlined options-dense').classes('w-full')
            all_cloud = ui.checkbox('Весь iCloud Drive', value=False).props('dense size=sm') if source['kind'] == 'icloud' and source['path'] else None

            #: Показывает фактический путь передачи и выбранную область iCloud.
            #: Использует photo_route для отображения промежуточных звеньев.
            def update_origin():
                if library:
                    origin.text = photo_route(library, upstream.value if upstream else '')
                else:
                    path = '' if all_cloud and all_cloud.value else source['path']
                    origin.text = scope_title(source_volume, path)

            if upstream:
                upstream.on_value_change(update_origin)
            if all_cloud:
                all_cloud.on_value_change(update_origin)
            update_origin()
            ui.label('Куда').classes('text-xs font-semibold s-muted')
            with ui.row().classes('w-full gap-2 items-center no-wrap'):
                selector = ui.select({i: scope_title(v, '') for i, v in volumes.items()},
                                     label='Том назначения').props('dense outlined options-dense').classes('grow min-w-0')
                shortcut = None
                if suggestion:
                    shortcut = ui.button('Из соседней панели', on_click=lambda: navigate(**suggestion)).props(
                        'flat dense no-caps color=green-9').classes('text-xs shrink-0')
                    shortcut.tooltip(scope_title(volumes[suggestion['volume_id']], suggestion['path']))
            with ui.row().classes('w-full gap-2 items-center no-wrap'):
                back = ui.button(icon='arrow_upward', on_click=lambda: navigate(
                    state['volume_id'], relative_path(str(PurePosixPath(state['path']).parent)))).props(
                    'flat dense size=sm aria-label="На уровень выше"')
                destination_path = ui.label().classes('text-xs break-all')
            folders = ui.column().classes('copy-setup-folders w-full gap-0')
            kind = ui.select(COPY_KINDS, value=preferred_kind or 'copy', label='Тип копии').props(
                'dense outlined options-dense').classes('w-full') if folder_kind else None
            problem = ui.label().classes('s-error text-xs break-words')
            problem.set_visibility(False)

            #: Загружает дочерние папки по выбранному адресу и игнорирует запоздалый ответ.
            #: Обновляет текущий путь, возможность сохранения и предложенный тип копии.
            async def navigate(volume_id, path=''):
                if state['saving'] or volume_id not in volumes:
                    return
                if kind and preferred_kind is None and state['volume_id'] != volume_id:
                    kind.set_value('cold' if volumes[volume_id].get('removable') else 'copy')
                revision = state['generation'] + 1
                state.update(volume_id=volume_id, path=path, generation=revision, ready=False)
                selector.set_value(volume_id)
                destination_path.text = scope_title(volumes[volume_id], path)
                back.set_enabled(bool(path))
                confirm.disable()
                problem.set_visibility(False)
                folders.clear()
                with folders:
                    ui.spinner(size='18px').classes('m-2')
                try:
                    data = await self.ws.read_directory(volume_id, path, refresh=True)
                    if revision != state['generation']:
                        return
                    if data.get('cached') or data.get('error'):
                        raise ValueError(data.get('error') or 'Папка назначения сейчас недоступна.')
                except Exception as error:
                    if revision == state['generation']:
                        folders.clear()
                        problem.text = self.ws.error_text(error)
                        problem.set_visibility(True)
                    return
                folders.clear()
                entries = [item for item in data['entries'] if item['kind'] == 'directory']
                with folders:
                    for item in entries:
                        ui.button(item['name'], icon='folder', on_click=lambda p=item['path']: navigate(volume_id, p)).props(
                            'flat dense no-caps color=dark').classes('w-full')
                    if not entries:
                        ui.label('Вложенных папок нет').classes('sidebar-empty')
                state['ready'] = bool(path) and (volume_id, path) != (source['volume_id'], source['path'])
                confirm.set_enabled(state['ready'])

            #: Обрабатывает выбор тома только для актуального значения поля.
            #: Асинхронно ожидает: navigate.
            async def change_volume(event):
                if event.value == selector.value and event.value != state['volume_id']:
                    await navigate(event.value)

            #: Отправляет подтверждённую связь и оставляет поля доступными для исправления ошибки.
            #: Асинхронно ожидает: self.save.
            async def submit():
                if not state['ready'] or state['saving']:
                    return
                state['saving'] = True
                problem.set_visibility(False)
                controls = [control for control in (selector, shortcut, back, kind, upstream, all_cloud, cancel, confirm) if control]
                for control in controls:
                    control.disable()
                try:
                    result = await self.save(source, {key: state[key] for key in ('volume_id', 'path')},
                                             kind.value if kind else None, upstream.value if upstream else None,
                                             bool(all_cloud and all_cloud.value))
                except Exception as error:
                    problem.text = self.ws.error_text(error)
                    problem.set_visibility(True)
                else:
                    dialog.submit(result)
                finally:
                    state['saving'] = False
                    for control in controls:
                        control.enable()
                    back.set_enabled(bool(state['path']))

            selector.on_value_change(change_volume)
            with ui.row().classes('w-full justify-end gap-2'):
                cancel = ui.button('Отмена', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
                confirm = ui.button('Сохранить связь', on_click=submit).props('unelevated no-caps color=green-9')
            confirm.disable()
            back.disable()
            first = suggestion['volume_id'] if suggestion else next(iter(volumes))
            ui.timer(.01, lambda: navigate(first), once=True)
        return await dialog
