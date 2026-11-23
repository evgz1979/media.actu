"""One destination picker for folder, Photos and iCloud Drive copy bindings."""
from pathlib import PurePosixPath

from nicegui import ui

from copy_panels import copy_route
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
    label = library.get('label') or 'Photos'
    if not link_id:
        return label
    copies = [dict(c, label=f"{c['number']:02d}-copy · {c['volume_name']}") for c in library['copies']]
    target = next((copy for copy in copies if copy['id'] == link_id), None)
    if not target:
        return 'Недоступный источник'
    route = copy_route(dict(id=None, label=label), copies, target, parent_key='source_link_id', downstream=False)
    return ' → '.join(node['label'] for node in route)


#: Показывает текущий путь и дочерние папки для выбора источника или назначения.
#: Передаёт изменения адреса и доступности диалогу, который принимает выбор.
class CopyFolderPicker:
    #: Создаёт общие элементы навигации, списка папок и сообщения об ошибке.
    #: Принимает разрешённые тома и обработчик изменения выбора.
    def __init__(self, workspace, volumes, changed, *, up_label):
        self.ws = workspace
        self.volumes = volumes
        self.changed = changed
        self.volume_id = None
        self.path = ''
        self.ready = self.locked = False
        self.generation = 0
        with ui.row().classes('w-full gap-2 items-center no-wrap'):
            self.back = ui.button(icon='arrow_upward', on_click=self.parent).props(
                f'flat dense size=sm aria-label="{up_label}"')
            self.address = ui.label().classes('text-xs break-all')
        self.folders = ui.column().classes('copy-setup-folders w-full gap-0')
        self.problem = ui.label().classes('s-error text-xs break-words')
        self.problem.set_visibility(False)
        self.back.disable()

    #: Блокирует навигацию и отменяет применение запоздалого ответа при закрытии.
    #: Обновляет доступность перехода в родительскую папку.
    def set_locked(self, locked):
        self.locked = locked
        self.back.set_enabled(bool(self.path) and not locked)
        if locked:
            self.generation += 1

    #: Открывает родительскую папку на текущем томе.
    #: Оставляет корень верхней границей выбора.
    async def parent(self):
        if self.path:
            await self.navigate(self.volume_id, relative_path(str(PurePosixPath(self.path).parent)))

    #: Загружает список вложенных папок без чтения файлов и отмечает проверенный адрес.
    #: Игнорирует ответ, если пользователь перешёл дальше или закрыл диалог.
    async def navigate(self, volume_id, path=''):
        if self.locked or volume_id not in self.volumes:
            return
        self.generation += 1
        revision = self.generation
        self.volume_id, self.path, self.ready = volume_id, path, False
        self.address.text = scope_title(self.volumes[volume_id], path)
        self.back.set_enabled(bool(path))
        self.problem.set_visibility(False)
        self.changed()
        self.folders.clear()
        with self.folders:
            ui.spinner(size='18px').classes('m-2')
        try:
            data = await self.ws.read_directory(volume_id, path, refresh=True)
            if revision != self.generation:
                return
            if data.get('cached') or data.get('error'):
                raise ValueError(data.get('error') or 'Папка сейчас недоступна.')
        except Exception as error:
            if revision == self.generation:
                self.folders.clear()
                self.problem.text = self.ws.error_text(error)
                self.problem.set_visibility(True)
                with self.folders:
                    ui.button('Повторить', icon='refresh', on_click=lambda: self.navigate(volume_id, path)).props(
                        'flat dense no-caps color=dark').classes('w-full')
            return
        self.folders.clear()
        entries = [item for item in data['entries'] if item['kind'] == 'directory']
        with self.folders:
            for item in entries:
                ui.button(item['name'], icon='folder', on_click=lambda p=item['path']: self.navigate(volume_id, p)).props(
                    'flat dense no-caps color=dark').classes('w-full')
            if not entries:
                ui.label('Вложенных папок нет').classes('sidebar-empty')
        self.ready = True
        self.changed()


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

    #: Открывает диалог, обновляет боковой список и показывает созданную пару.
    #: Выбирает именно сохранённое назначение, даже если у источника уже есть копии.
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
            saved = await self.destination(source, volumes, self.suggested(source, index), preferred_kind)
            if saved is None:
                return
            result, target = saved
            ui.notify('Связь копии сохранена', type='positive')
            if source['kind'] == 'folder':
                self.ws.copies.expanded.add(result['id'])
                await self.ws.copies.changed()
                self.ws.copies.section.open()
                copy = next(c for c in result['copies'] if all(c[key] == value for key, value in target.items()))
                await self.ws.copies.open_copy(result, copy)
            else:
                libraries = self.ws.photo_libraries
                libraries.expanded.add(source['library']['id'] if source['kind'] == 'photos' else ICLOUD_VOLUME_ID)
                libraries.signature = None
                await libraries.refresh(wait=True)
                libraries.section.open()
                await libraries.open_copy(source['volume_id'], result['id'])
        except Exception as error:
            self.ws.notice(error)
        finally:
            self.opened = False
            self.ws.editing = was_editing

    #: Сохраняет настроенную связь через API соответствующего источника.
    #: Для iCloud сохраняет выбранный путь, включая явно выбранный корень.
    async def save(self, source, target, kind, upstream):
        if source['kind'] == 'folder':
            origin = {key: source[key] for key in ('volume_id', 'path')}
            return await self.ws.request('POST', '/api/storage/folder-copy-bindings',
                                         json=dict(source=origin, destination=dict(target, kind=kind)))
        if source['kind'] == 'photos':
            return await self.ws.request('POST', f"/api/photos/libraries/{source['library']['id']}/copies",
                                         json=dict(target, source_link_id=upstream or None))
        return await self.ws.request('POST', '/api/icloud/copies',
                                     json=dict(target, source_path=source['path']))

    #: Позволяет выбрать вложенную папку iCloud Drive по её точному адресу.
    #: Возвращает подтверждённый путь или None после отмены.
    async def choose_cloud_folder(self, volume, path):
        #: Разрешает выбор после подтверждённого чтения конкретной вложенной папки.
        #: Корень выбирается отдельной командой в основном диалоге.
        def changed():
            choose.set_enabled(picker.ready and bool(picker.path))

        with ui.dialog().props('persistent') as dialog, ui.card().classes('copy-setup'):
            ui.label('Выбрать папку iCloud Drive').classes('text-lg font-semibold')
            picker = CopyFolderPicker(self.ws, {ICLOUD_VOLUME_ID: volume}, changed, up_label='На уровень выше в iCloud Drive')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Отмена', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
                choose = ui.button('Выбрать эту папку', on_click=lambda: dialog.submit(picker.path)
                                   if picker.ready and picker.path else None).props('unelevated no-caps color=green-9')
            choose.disable()
            ui.timer(.01, lambda: picker.navigate(ICLOUD_VOLUME_ID, path), once=True)
        try:
            return await dialog
        finally:
            picker.set_locked(True)
            dialog.delete()

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

        state = dict(kind_volume=None, saving=False, selecting_source=False)
        cloud_kind = source['kind'] == 'icloud'
        source_path = (source['path'] or None) if cloud_kind else source['path']
        folder_kind = source['kind'] == 'folder'

        #: Проверяет оба адреса и состояние диалога перед сохранением связи.
        #: Для iCloud отличает отсутствие выбора от явно выбранного корня.
        def can_save():
            return (source_path is not None and picker.ready and bool(picker.path)
                    and (picker.volume_id, picker.path) != (source['volume_id'], source_path)
                    and not (state['saving'] or state['selecting_source']))

        #: Подписывает выбранную область и обновляет доступность сохранения.
        #: Пустой путь iCloud показывает как весь облачный диск.
        def change_source(path):
            nonlocal source_path
            if state['saving'] or state['selecting_source']:
                return
            source_path = path
            update_origin()
            problem.set_visibility(False)
            confirm.set_enabled(can_save())

        #: Открывает выбор папки и применяет только подтверждённый адрес.
        #: После отмены сохраняет прежнюю область.
        async def browse_source():
            if state['saving'] or state['selecting_source']:
                return
            state['selecting_source'] = True
            confirm.disable()
            try:
                selected = await self.choose_cloud_folder(source_volume, source_path or '')
            finally:
                state['selecting_source'] = False
                confirm.set_enabled(can_save())
            if selected is not None:
                change_source(selected)

        with ui.dialog().props('persistent') as dialog, ui.card().classes('copy-setup'):
            ui.label('Добавить копию').classes('text-lg font-semibold')
            ui.label('Из').classes('text-xs font-semibold s-muted')
            origin = ui.label().classes('copy-setup-path w-full break-all')
            upstream = None
            if all_copies:
                upstream = ui.select(upstream_choices, value=(direct or all_copies[0])['id'],
                                     label='Копировать из').props('dense outlined options-dense').classes('w-full')
            source_button = cloud_root = None
            if cloud_kind:
                with ui.row().classes('w-full gap-2 items-center'):
                    source_button = ui.button('Выбрать папку…', icon='folder_open', on_click=browse_source).props(
                        'flat dense no-caps color=green-9')
                    cloud_root = ui.button('Весь iCloud Drive', on_click=lambda: change_source('')).props(
                        'flat dense no-caps color=dark')

            #: Показывает фактический путь передачи и выбранную область iCloud.
            #: Использует photo_route для отображения промежуточных звеньев.
            def update_origin():
                if library:
                    origin.text = photo_route(library, upstream.value if upstream else '')
                elif cloud_kind and not source_path:
                    origin.text = 'Выбери папку iCloud Drive' if source_path is None else 'Весь iCloud Drive'
                else:
                    origin.text = scope_title(source_volume, source_path)

            if upstream:
                upstream.on_value_change(update_origin)
            update_origin()
            ui.label('Куда').classes('text-xs font-semibold s-muted')
            with ui.row().classes('w-full gap-2 items-center no-wrap'):
                selector = ui.select({i: scope_title(v, '') for i, v in volumes.items()},
                                     label='Том назначения').props('dense outlined options-dense').classes('grow min-w-0')
                shortcut = None
                if suggestion:
                    shortcut = ui.button('Из соседней панели', on_click=lambda: picker.navigate(**suggestion)).props(
                        'flat dense no-caps color=green-9').classes('text-xs shrink-0')
                    shortcut.tooltip(scope_title(volumes[suggestion['volume_id']], suggestion['path']))
            #: Согласует выбранный том, предложенный тип копии и доступность сохранения.
            #: Сбрасывает ошибку сохранения, когда меняется назначение.
            def update_destination():
                volume_id = picker.volume_id
                if kind and preferred_kind is None and state['kind_volume'] != volume_id:
                    kind.set_value('cold' if volumes[volume_id].get('removable') else 'copy')
                    state['kind_volume'] = volume_id
                selector.set_value(volume_id)
                problem.set_visibility(False)
                confirm.set_enabled(can_save())

            picker = CopyFolderPicker(self.ws, volumes, update_destination, up_label='На уровень выше')
            kind = ui.select(COPY_KINDS, value=preferred_kind or 'copy', label='Тип копии').props(
                'dense outlined options-dense').classes('w-full') if folder_kind else None
            problem = ui.label().classes('s-error text-xs break-words')
            problem.set_visibility(False)

            #: Обрабатывает выбор тома только для актуального значения поля.
            #: Асинхронно ожидает: picker.navigate.
            async def change_volume(event):
                if event.value == selector.value and event.value != picker.volume_id:
                    await picker.navigate(event.value)

            #: Отправляет подтверждённую связь и оставляет поля доступными для исправления ошибки.
            #: Асинхронно ожидает: self.save.
            async def submit():
                if not can_save():
                    return
                state['saving'] = True
                problem.set_visibility(False)
                controls = [control for control in (selector, shortcut, kind, upstream, source_button, cloud_root, cancel, confirm) if control]
                picker.set_locked(True)
                for control in controls:
                    control.disable()
                try:
                    target = dict(volume_id=picker.volume_id, path=picker.path)
                    result = await self.save(dict(source, path=source_path), target, kind.value if kind else None,
                                             upstream.value if upstream else None)
                except Exception as error:
                    problem.text = self.ws.error_text(error)
                    problem.set_visibility(True)
                else:
                    dialog.submit((result, target))
                finally:
                    state['saving'] = False
                    for control in controls:
                        control.enable()
                    picker.set_locked(False)
                    confirm.set_enabled(can_save())

            selector.on_value_change(change_volume)
            with ui.row().classes('w-full justify-end gap-2'):
                cancel = ui.button('Отмена', on_click=lambda: dialog.submit(None)).props('flat no-caps color=dark')
                confirm = ui.button('Сохранить связь', on_click=submit).props('unelevated no-caps color=green-9')
            confirm.disable()
            first = suggestion['volume_id'] if suggestion else next(iter(volumes))
            ui.timer(.01, lambda: picker.navigate(first), once=True)
        try:
            return await dialog
        finally:
            picker.set_locked(True)
            dialog.delete()
