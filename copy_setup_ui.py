"""Create copy bindings from the two workspace trees."""
from pathlib import PurePosixPath

from nicegui import ui

from copy_panels import copy_route
from media_manager.copies import COPY_KINDS
from media_manager.icloud_copies import ICLOUD_VOLUME_ID


COPY_SETUP_CSS = """
.commander-trees.copy-configuring { --copy-width:clamp(154px,24%,205px);
    grid-template-columns:minmax(0,1fr) var(--copy-width) minmax(0,1fr); gap:7px; }
.commander-trees.copy-configuring.copy-configuring-chain { --copy-width:clamp(190px,31%,285px); }
.commander-trees.copy-configuring > .commander-pane:nth-child(2) { grid-column:3; grid-row:1; }
.commander-trees.copy-configuring > .commander-pane { border-color:#b0c4a7; }
.commander-trees.copy-configuring > .active-pane { border-color:#75986c; }
.copy-setup-panel { grid-column:2; grid-row:1; align-self:start; min-width:0; gap:7px; padding:9px;
    background:#f5f8f3; border:1px solid #cad8c5; border-radius:9px; color:#344734; }
.copy-setup-label { font-size:10px; color:#597157; font-weight:650; }
.copy-setup-address { font-size:12px; line-height:1.4; overflow-wrap:anywhere; }
.copy-setup-target { width:100%; background:#e7f0e4; border-radius:4px; padding:4px 5px; }
.copy-setup-panel .q-btn { width:100%; text-align:center; font-size:11px; min-height:28px; padding:3px 5px; }
.copy-setup-panel .q-field__label, .copy-setup-panel .q-field__native { font-size:11px; }
@media(max-width:900px) {
 .commander-trees.copy-configuring, .commander-trees.copy-configuring.copy-configuring-chain {
    grid-template-columns:repeat(2,minmax(0,1fr)); grid-template-rows:auto minmax(0,1fr); }
 .commander-trees.copy-configuring > .commander-pane:first-child { grid-row:2; }
 .commander-trees.copy-configuring > .commander-pane:nth-child(2) { grid-column:2; grid-row:2; }
 .copy-setup-panel { grid-column:1 / -1; }
}
"""


#: Формирует читаемый путь по короткому имени тома и пути внутри него.
#: Для корневой папки возвращает имя тома.
def scope_title(volume, path):
    name = volume.get('display_name') or volume['name']
    return f'{name} /{path}' if path else name


#: Определяет подключённый том, пригодный для назначения копии.
#: Проверяет доступность и сохранённую идентичность тома.
def copy_volume(volume):
    return bool(volume and volume['kind'] not in ('photos', 'icloud') and volume['availability'] == 'online'
                and volume.get('identity_status') not in ('unverified', 'legacy'))


#: Показывает адрес и предыдущие звенья выбранной копии.
#: Использует фактические связи, включая отсутствующий источник.
def copy_origin_route(label, copies, link_id, *, parent_key='source_link_id', root_id=None):
    if not link_id:
        return label
    copies = [dict(copy, label=f"{copy.get('label') or f'{copy['number']:02d}-copy'} · {copy['volume_name']}")
              for copy in copies]
    target = next((copy for copy in copies if copy['id'] == link_id), None)
    if not target:
        return 'Недоступный источник'
    route = copy_route(dict(id=root_id, label=label), copies, target, parent_key=parent_key, downstream=False)
    return ' → '.join(node['label'] for node in route)


#: Управляет выбором готовой папки назначения в правом дереве.
#: Держит источник и тип копии до явного сохранения или отмены.
class CopySetupUI:
    #: Инициализирует состояние выбора и защищает создание от двойного нажатия.
    #: Состояние черновика хранится только на открытой странице.
    def __init__(self, workspace):
        self.ws = workspace
        self.draft = None
        self.opening = self.saving = False
        self.previous = None
        self.destination_key = None

    #: Размещает путь, тип и подтверждение в отдельной центральной колонке.
    #: Обе панели остаются обычными деревьями во время выбора.
    def build(self):
        with ui.column().classes('copy-setup-panel').props('role="group" aria-label="Добавление копии"') as self.panel:
            ui.label('Из').classes('copy-setup-label')
            self.origin = ui.label().classes('copy-setup-address')
            ui.icon('south', size='16px').classes('text-green-9')
            ui.label('Куда').classes('copy-setup-label')
            self.destination = ui.label().classes('copy-setup-address copy-setup-target')
            self.kind = ui.select(COPY_KINDS, value='copy', label='Тип копии').props(
                'dense outlined options-dense').classes('w-full')
            self.problem = ui.label().classes('s-error text-xs break-words')
            self.problem.set_visibility(False)
            self.confirm = ui.button('Связать как копию', on_click=self.submit).props('unelevated dense no-caps color=green-9')
            self.cancel_button = ui.button('Отмена', on_click=self.cancel).props('flat dense no-caps color=dark')
        self.panel.set_visibility(False)

    #: Определяет выбранный источник и его роль в цепочке.
    #: Для физических копий проверяет точный корень привязки.
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
        libraries = getattr(self.ws, 'photo_libraries', None)
        if libraries:
            for copy in libraries.cloud.get('copies', []):
                if (copy['volume_id'], copy['path']) == (volume_id, path):
                    return dict(kind='icloud', volume_id=ICLOUD_VOLUME_ID, path=copy['source_path'], source_link_id=copy['id'])
            for library in libraries.libraries:
                for copy in library.get('copies', []):
                    if (copy['volume_id'], copy['path']) == (volume_id, path) and copy.get('connected', True):
                        return dict(kind='photos', volume_id=f"photos-{library['id']}", path='',
                                    library=library, source_link_id=copy['id'])
        member = self.ws.copies.membership(volume_id, path)
        if member and not member['is_root']:
            return None
        source = dict(kind='folder', volume_id=volume_id, path=path)
        if member and member['number']:
            source.update(source_location_id=member['id'], group_id=member['group_id'])
        return source

    #: Подписывает полный маршрут от корня до выбранного источника.
    #: Для прямого источника показывает полный путь выбранной папки.
    def describe(self, source):
        volume = self.ws.resolve_volume(source['volume_id'])
        label = scope_title(volume, source['path'])
        link_id = source.get('source_link_id')
        if library := source.get('library'):
            return copy_origin_route(label, library.get('copies', []), link_id)
        if link_id:
            return copy_origin_route(label, self.ws.photo_libraries.cloud.get('copies', []), link_id)
        if location := source.get('source_location_id'):
            group = next((group for group in self.ws.copies.groups if group['id'] == source['group_id']), None)
            if group:
                main = group['main']
                main_volume = self.ws.resolve_volume(main['volume_id']) or dict(name=main['volume_name'])
                root = scope_title(main_volume, main['path'])
                return copy_origin_route(root, group['copies'], location, parent_key='source_location_id', root_id=main['id'])
        return label

    #: Выбирает правую папку, если том доступен и пути не пересекаются.
    #: Путь хранится вместе с ID тома, а файл и корень тома непригодны как назначение.
    def target(self):
        pane = self.ws.panes[1]
        if pane.view_mode != 'tree' or pane.kind != 'directory' or not pane.path or not copy_volume(pane.volume):
            return None
        origin, path = self.draft['anchor']
        if pane.volume_id == origin:
            left, right = PurePosixPath(path), PurePosixPath(pane.path)
            if left.is_relative_to(right) or right.is_relative_to(left):
                return None
        return dict(volume_id=pane.volume_id, path=pane.path)

    #: Отображает выбранное назначение и доступность подтверждения без пересборки деревьев.
    #: Закрывает устаревший черновик при выборе другой области слева.
    def refresh(self):
        if not self.draft or self.opening or self.saving:
            return
        left = self.ws.panes[0]
        if (left.volume_id, left.path) != self.draft['anchor'] or left.kind != 'directory':
            self.clear()
            return
        target = self.target()
        key = (target['volume_id'], target['path']) if target else None
        if key != self.destination_key:
            self.problem.set_visibility(False)
        self.destination_key = key
        self.destination.text = scope_title(self.ws.panes[1].volume, target['path']) if target else 'Выбери папку справа'
        if target and target['volume_id'] != self.draft['suggested_volume']:
            self.draft['suggested_volume'] = target['volume_id']
            kind = self.draft['preferred_kind'] or ('cold' if self.ws.panes[1].volume.get('removable') else 'copy')
            self.kind.set_value(kind)
        self.confirm.set_enabled(target is not None)

    #: Переводит рабочее пространство в выбор назначения между двумя деревьями.
    #: Открытая правая папка подставляется сразу, а предыдущая связанная пара доступна после отмены.
    async def open(self, volume_id, path='', *, index=None, preferred_kind=None):
        if self.opening or self.saving:
            return
        source = self.source(volume_id, path)
        if not source:
            ui.notify('Выбери папку-источник, медиатеку или подключённую копию.', type='info')
            return
        ws = self.ws
        anchor = (volume_id, '' if ws.is_photos(volume_id) else path)
        panes = ws.panes
        if index is None:
            active = ws.active_index
            order = (active, 1 - active)
            index = next((i for i in order if (panes[i].volume_id, panes[i].path) == anchor),
                         next((i for i in order if panes[i].volume_id == volume_id), 0))
        previous = self.previous
        active_pair = ws.pair.active
        report = ws.report or (ws.pair.report if active_pair else None)
        if previous is None and (active_pair or report or any(pane.view_mode == 'preview' for pane in panes)):
            previous = ws.workspace_snapshot()
        self.clear()
        self.opening = True
        try:
            other = panes[1 - index].save_browse_state()
            if active_pair:
                await ws.pair.unlink(stop_work=False)
            if ws.report:
                await ws.browse()
            for pane in panes:
                if pane.view_mode == 'preview':
                    await pane.set_mode('tree')
            if (index == 1 or active_pair or report) and other['volume_id']:
                if report:
                    folder = other['path'] if other['kind'] == 'directory' else other['root_path']
                    await panes[1].show_volume(other['volume_id'], folder, activate=False)
                else:
                    panes[1].restore_browse_state(other)
            if (panes[0].volume_id, panes[0].path) != anchor or panes[0].kind != 'directory':
                await panes[0].show_volume(*anchor, activate=False)
            self.previous = previous
            self.draft = dict(source=source, anchor=anchor, preferred_kind=preferred_kind, suggested_volume=None)
            chain = bool(source.get('source_location_id') or source.get('source_link_id'))
            origin = self.describe(source)
            self.origin.text = f'{origin} /{anchor[1]}' if chain else origin
            self.kind.set_visibility(source['kind'] == 'folder')
            self.kind.set_value(preferred_kind or 'copy')
            self.panel.set_visibility(True)
            ws.trees.classes(add='copy-configuring')
            ws.trees.classes(add='copy-configuring-chain' if chain else '',
                             remove='' if chain else 'copy-configuring-chain')
            for pane in panes:
                pane.mode_switch.disable()
            ws.set_active(1)
            panes[1].focus_tree()
        except Exception as error:
            self.clear()
            ws.notice(error)
        finally:
            self.opening = False
            ws.update_scopes()

    #: Убирает редактор и возвращает обычные команды панелей.
    #: Используется также при переходе к другой паре.
    def clear(self):
        if not self.draft:
            return
        self.draft = self.previous = self.destination_key = None
        self.problem.set_visibility(False)
        self.panel.set_visibility(False)
        self.ws.trees.classes(remove='copy-configuring copy-configuring-chain')
        for pane in self.ws.panes:
            pane.mode_switch.enable()

    #: Отменяет выбор и возвращает прежний отчёт или связанную пару, если они были открыты.
    #: Независимая навигация по двум деревьям сохраняется.
    async def cancel(self):
        if self.saving or self.opening or not self.draft:
            return
        previous = self.previous
        self.clear()
        if previous:
            self.opening = True
            try:
                await self.ws.restore_workspace(previous)
            except Exception as error:
                self.ws.notice(error)
            finally:
                self.opening = False
        self.ws.update_scopes()

    #: Проверяет выбранную папку и сохраняет связь, затем показывает созданную пару.
    #: Файловая операция может быть запущена отдельно из открытой пары.
    async def submit(self):
        if not self.draft or self.saving or not (target := self.target()):
            return
        source = self.draft['source']
        kind = self.kind.value
        self.saving = True
        saved = False
        self.problem.set_visibility(False)
        self.confirm.disable()
        self.cancel_button.disable()
        self.kind.disable()
        try:
            listing = await self.ws.read_directory(target['volume_id'], target['path'], refresh=True)
            if listing.get('cached') or listing.get('error'):
                raise ValueError(listing.get('error') or 'Папка назначения сейчас недоступна.')
            result = await self.save(source, target, kind)
            saved = True
            self.clear()
            ui.notify('Связь копии сохранена', type='positive')
            await self.show_saved(source, target, result)
        except Exception as error:
            if saved or not self.draft:
                self.ws.notice(error)
            else:
                self.problem.text = self.ws.error_text(error)
                self.problem.set_visibility(True)
        finally:
            self.saving = False
            self.cancel_button.enable()
            self.kind.enable()
            self.ws.update_scopes()

    #: Сохраняет связь через API выбранного источника.
    #: Для цепочки передаёт постоянный ID предыдущего звена.
    async def save(self, source, target, kind):
        if source['kind'] == 'folder':
            origin = {key: source[key] for key in ('volume_id', 'path')}
            return await self.ws.request('POST', '/api/storage/folder-copy-bindings', json=dict(
                source=origin, destination=dict(target, kind=kind), source_location_id=source.get('source_location_id')))
        if source['kind'] == 'photos':
            return await self.ws.request('POST', f"/api/photos/libraries/{source['library']['id']}/copies",
                                         json=dict(target, source_link_id=source.get('source_link_id')))
        return await self.ws.request('POST', '/api/icloud/copies',
                                     json=dict(target, source_path=source['path'], source_link_id=source.get('source_link_id')))

    #: Обновляет боковую колонку и открывает именно сохранённое назначение.
    #: Нужная копия выбирается по адресу или ID из результата Core.
    async def show_saved(self, source, target, result):
        if source['kind'] == 'folder':
            copies = self.ws.copies
            copies.expanded.add(result['id'])
            await copies.changed()
            copies.section.open()
            copy = next(c for c in result['copies'] if all(c[key] == value for key, value in target.items()))
            await copies.open_copy(result, copy)
        else:
            libraries = self.ws.photo_libraries
            key = source['library']['id'] if source['kind'] == 'photos' else (ICLOUD_VOLUME_ID, source['path'])
            libraries.expanded.add(key)
            libraries.signature = None
            await libraries.refresh(wait=True)
            section = libraries.library_section if source['kind'] == 'photos' else self.ws.copies.section
            section.open()
            await libraries.open_copy(source['volume_id'], result['id'])
