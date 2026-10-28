"""Storage workspace; communicates with Core, never reads mounted files itself."""
from __future__ import annotations

import asyncio
from pathlib import PurePosixPath
from itertools import count

from nicegui import ui

from media_manager.storage import FLAGS, PURPOSES, ROLES
from network_ui import show_network_dialog


FOLDER_ICON_IDS = count()


def folder_icon(size=16):
    gradient = f'folder-blue-{next(FOLDER_ICON_IDS)}'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 16" width="100%" height="100%" aria-hidden="true" focusable="false">
        <defs><linearGradient id="{gradient}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#91daf2"/><stop offset="1" stop-color="#4eb7dc"/></linearGradient></defs>
        <path d="M1.25 5V3.25A1.25 1.25 0 0 1 2.5 2h4.1l1.6 1.8h7.3a1.25 1.25 0 0 1 1.25 1.25V13a1 1 0 0 1-1 1H2.25a1 1 0 0 1-1-1Z" fill="#b4e2f1" stroke="#5ba5bf" stroke-width=".65"/>
        <rect x="1.25" y="5" width="15.5" height="9" rx="1" fill="url(#{gradient})" stroke="#4c9fbd" stroke-width=".65"/>
        <path d="M2 5.8h14" stroke="#d7f2fa" stroke-width=".6"/>
        </svg>"""
    return ui.html(svg, sanitize=False).classes('s-folder-icon').style(f'width:{size}px;height:{size}px')


CSS = """
:root { --s-ink:#243129; --s-muted:#7c847e; --s-line:#e2e6df; --s-paper:#f5f6f2; --s-green:#365f43; }
body { background:var(--s-paper); color:var(--s-ink); font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif; }
.q-page { background:var(--s-paper); } .nicegui-content { padding:0; gap:0; }
.s-header { background:white; border-bottom:1px solid var(--s-line); padding:16px 26px; min-height:72px; }
.s-brand { font-size:19px; letter-spacing:-.5px; font-weight:750; }
.s-nav { color:var(--s-muted); text-decoration:none; font-size:14px; padding:8px 14px; border-radius:8px; }
.s-nav.active { background:#edf2e9; color:var(--s-green); font-weight:650; }
.s-intro { padding:26px 26px 20px; } .s-title { font-size:28px; font-weight:650; letter-spacing:-.7px; }
.s-muted { color:var(--s-muted); } .s-caption { font-size:10px; font-weight:700; letter-spacing:1.2px; color:var(--s-muted); }
.s-layout { display:grid; grid-template-columns:240px minmax(340px,1fr) 280px; gap:16px; padding:0 26px 26px; width:100%; align-items:start; }
.s-panel { background:white; border:1px solid var(--s-line); border-radius:12px; overflow:hidden; min-width:0; }
.s-panel-head { padding:17px 18px; border-bottom:1px solid var(--s-line); }
.s-volumes { max-height:calc(100vh - 330px); overflow-y:auto; }
.s-volume-group { padding:6px 8px 3px; font-size:11px; font-weight:650; color:#687466; gap:7px; }
.s-volume-row { width:100%; min-height:24px; height:24px; padding:0 9px; border:1px solid transparent; border-radius:6px; }
.s-volume-row .q-btn__content { width:100%; flex-wrap:nowrap; justify-content:flex-start; gap:8px; }
.s-volume-row:hover { background:#f6f8f2; } .s-volume-row.chosen { border-color:#b7c8b0; background:#edf3e7; }
.s-volume-name { min-width:0; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; text-align:left; font-size:13px; font-weight:500; line-height:22px; }
.s-volume-role { flex-shrink:0; max-width:64px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#4e7149; background:#eef3e9; border-radius:4px; padding:0 4px; font-size:10px; line-height:15px; }
.s-volume-status { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
.s-tag { font-size:11px; padding:3px 7px; border-radius:5px; line-height:1.4; background:#f0f1ed; color:#747b72; white-space:normal; }
.s-tag.purpose { color:#536a89; background:#edf1f7; } .s-tag.role { color:#3f6744; background:#eaf2e6; }
.s-tag.flag { color:#9b7435; background:#fbf3df; }
.s-path { overflow-wrap:anywhere; font-family:ui-monospace,Menlo,monospace; font-size:11px; }
.s-tree-toolbar { min-height:28px; padding:2px 10px; gap:8px; }
.s-tree { max-height:calc(100vh - 285px); min-height:320px; overflow:auto; padding:0; }
.s-list-grid { display:grid; grid-template-columns:minmax(220px,1fr) 132px 66px 72px; width:100%; min-width:520px; align-items:center; }
.s-tree-heading { height:25px; min-height:25px; position:sticky; top:0; z-index:2; background:#fff; border-bottom:1px solid #d9dddf; color:#7e8589; font-size:11px; line-height:20px; }
.s-tree-heading > div { padding:0 8px; border-right:1px solid #e2e5e7; overflow:hidden; white-space:nowrap; }
.s-tree-heading > div:first-child { padding-left:40px; }
.s-tree-heading > div:last-child { border-right:0; }
.s-entry { height:22px; min-height:22px; background:#fff; }
.s-entry.alt { background:#f3f4f5; }
.s-entry:hover { background:#edf2f6; }
.s-entry.selected, .s-entry.selected:hover { background:#dce9f8; }
.s-name-cell { min-width:0; height:22px; flex-wrap:nowrap; align-items:center; gap:3px; padding-right:6px; }
.s-folder-icon { flex:0 0 auto; display:flex; align-items:center; justify-content:center; line-height:0; }
.s-tree-toggle.q-btn { width:16px; min-width:16px; height:20px; min-height:20px; padding:0; border-radius:2px; flex-shrink:0; }
.s-tree-toggle .q-icon { font-size:14px; }
.s-tree-spacer { width:16px; flex-shrink:0; }
.s-entry-name.q-btn { flex:1; min-width:0; min-height:20px; height:20px; padding:0 2px; border-radius:2px; font-size:12px; line-height:18px; font-weight:400; color:#263129; text-align:left; }
.s-entry-name .q-btn__content { width:100%; min-width:0; flex-wrap:nowrap; justify-content:flex-start; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.s-entry-name .block { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.s-entry-name .q-focus-helper { display:none; }
.s-entry-name:focus-visible { outline:1px solid #9cb8d5; outline-offset:-1px; }
.s-tree-role { flex-shrink:0; max-width:48px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#597456; background:#e9eee5; border-radius:3px; padding:0 4px; font-size:10px; line-height:14px; }
.s-entry-cell { min-width:0; padding:0 8px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#85898d; font-size:11px; line-height:20px; }
.s-entry-size { text-align:right; }
.s-note { background:#f6f7f3; border-radius:8px; padding:11px 12px; font-size:12px; color:#6b776a; line-height:1.5; }
.s-error { background:#fff5e9; color:#9b6725; border-radius:8px; padding:10px 12px; font-size:12px; }
.q-btn { box-shadow:none !important; border-radius:7px; } .s-divider { width:100%; height:1px; background:var(--s-line); margin:4px 0; }
@media(max-width:1150px) { .s-layout { grid-template-columns:220px minmax(0,1fr); } .s-properties { grid-column:2; } .s-tree { max-height:520px; } }
@media(max-width:700px) { .s-header { padding:14px 16px; flex-wrap:wrap; gap:10px; } .s-intro { padding:20px 16px 16px; } .s-layout { grid-template-columns:1fr; padding:0 16px 20px; } .s-properties { grid-column:1; } .s-volumes { max-height:290px; overflow:auto; } .s-tree { max-height:480px; } .s-header .s-readonly { display:none; } }
"""


def register_storage_page(request, format_bytes, format_date):
    @ui.page('/')
    async def storage_page():
        ui.add_head_html('<meta name="color-scheme" content="light">')
        ui.add_css(CSS)
        volumes = []
        selected_volume = None
        selected_path = ''
        selected_kind = 'directory'
        selected_entry = None
        folders = {}
        expanded = {''}
        limits = {}
        lock = asyncio.Lock()
        editing = False

        def tags(metadata, empty=True):
            values = metadata.get('effective', {})
            items = []
            if values.get('purpose'):
                items.append((PURPOSES[values['purpose']], 'purpose'))
            if values.get('role'):
                items.append((ROLES[values['role']], 'role'))
            items.extend((label, 'flag') for key, label in FLAGS.items() if values.get(key))
            for label, style in items:
                ui.label(label).classes(f's-tag {style}')
            if not items and empty:
                ui.label('Роль не назначена').classes('s-tag')

        def current_volume():
            return next((v for v in volumes if v['id'] == selected_volume), None)

        async def error_notice(error):
            detail = str(error)
            if hasattr(error, 'response'):
                try:
                    detail = error.response.json().get('detail', detail)
                except ValueError:
                    pass
            ui.notify(detail, type='negative')

        with ui.row().classes('s-header w-full items-center justify-between no-wrap'):
            with ui.row().classes('items-center gap-8'):
                ui.label('media.actu').classes('s-brand')
                with ui.row().classes('items-center gap-1'):
                    ui.link('Хранилища', '/').classes('s-nav active')
                    ui.link('Медиа', '/media').classes('s-nav')
            with ui.row().classes('items-center gap-2 s-readonly'):
                ui.icon('lock_outline', size='15px').classes('s-muted')
                ui.label('Файлы только для чтения').classes('s-muted text-xs')
        with ui.row().classes('s-intro w-full items-end justify-between'):
            with ui.column().classes('gap-1'):
                ui.label('Хранилища').classes('s-title')
                overview = ui.label('Загрузка томов M4…').classes('s-muted text-sm')
            with ui.row().classes('gap-2'):
                ui.button('Найти NAS', icon='lan', on_click=lambda: show_network_dialog(request, format_date, refresh_volumes)).props('unelevated no-caps color=green-9')
                refresh_button = ui.button('Обновить тома', icon='refresh', on_click=lambda: refresh_volumes(True)).props('outline no-caps color=dark')
        with ui.element('div').classes('s-layout'):
            with ui.column().classes('s-panel w-full gap-0'):
                with ui.row().classes('s-panel-head w-full items-center justify-between'):
                    ui.label('ТОМА').classes('s-caption')
                    volume_count = ui.label('—').classes('s-muted text-xs')
                volume_list = ui.column().classes('s-volumes w-full p-2 gap-0')
                with ui.column().classes('px-4 pb-4 pt-2 gap-1'):
                    ui.label('Отключённые остаются в списке.').classes('s-muted text-xs')
                    ui.link('Системная медиатека Photos →', '/media').classes('text-xs text-green-900 no-underline')
            with ui.column().classes('s-panel w-full gap-0'):
                with ui.row().classes('s-panel-head w-full items-center justify-between gap-2'):
                    with ui.column().classes('gap-1 min-w-0'):
                        tree_title = ui.label('Дерево файлов').classes('font-semibold text-base')
                        tree_path = ui.label('Выбери том').classes('s-path s-muted')
                    with ui.row().classes('items-center gap-1'):
                        ui.button(icon='vertical_align_top', on_click=lambda: select_root()).props('flat round dense color=dark').tooltip('Свойства тома')
                        ui.button(icon='refresh', on_click=lambda: refresh_folder()).props('flat round dense color=dark').tooltip('Перечитать выбранную папку')
                with ui.row().classes('s-tree-toolbar w-full items-center justify-between no-wrap'):
                    snapshot_label = ui.label('Просмотренные папки сохраняются для работы без подключения.').classes('s-muted text-xs')
                    show_hidden = ui.checkbox('Скрытые файлы', value=False, on_change=lambda: render_tree()).props('dense size=xs').classes('text-xs s-muted')
                tree_list = ui.column().classes('s-tree w-full gap-0')
            properties = ui.column().classes('s-panel s-properties w-full p-5 gap-4')

        def render_volumes():
            volume_list.clear()
            online = sum(v['availability'] == 'online' for v in volumes)
            overview.text = f'Томов: {len(volumes)} · подключено: {online} · недоступно или отключено: {len(volumes) - online}'
            volume_count.text = str(len(volumes))
            with volume_list:
                if not volumes:
                    ui.label('Пока нет сохранённых томов.').classes('s-muted text-sm p-3')
                groups = {}
                for volume in volumes:
                    group = volume.get('group') or {'id': 'm4' if volume['kind'] != 'network' else 'network-unknown', 'name': 'M4' if volume['kind'] != 'network' else 'Сетевые тома', 'kind': 'local' if volume['kind'] != 'network' else 'network'}
                    groups.setdefault(group['id'], {'details': group, 'volumes': []})['volumes'].append(volume)
                for group in sorted(groups.values(), key=lambda g: (g['details']['kind'] == 'local', g['details']['name'].casefold())):
                    details = group['details']
                    with ui.row().classes('s-volume-group w-full items-center no-wrap'):
                        ui.icon('dns' if details['kind'] == 'network' else 'computer', size='15px')
                        ui.label(details['name']).classes('grow truncate')
                        ui.label(str(len(group['volumes']))).classes('s-muted font-normal')
                    for volume in group['volumes']:
                        available = volume['availability']
                        status = {'online': 'Подключён', 'offline': 'Отключён' if volume['mount_path'] else 'Не подключён', 'unknown': 'Доступность неизвестна'}[available]
                        values = volume['metadata']['effective']
                        role = values.get('role') or ''
                        description = f"{volume['name']} · {status} · {ROLES[role]}"
                        if values.get('purpose'):
                            description += ' · ' + PURPOSES[values['purpose']]
                        with ui.button(on_click=lambda v=volume: choose_volume(v['id'])).props('flat no-caps color=dark').classes('s-volume-row' + (' chosen' if volume['id'] == selected_volume else '')).tooltip(description):
                            ui.icon('circle', size='7px').classes('shrink-0 ' + {'online': 'text-green-700', 'offline': 'text-grey-5', 'unknown': 'text-amber-700'}[available])
                            ui.label(volume['name']).classes('s-volume-name')
                            if role:
                                ui.label({'primary': 'Осн.', 'copy': 'Копия', 'archive': 'Архив', 'temporary': 'Врем.'}[role]).classes('s-volume-role')
                            ui.label(status).classes('s-volume-status')

        async def load_folder(path, refresh=True):
            volume_id = selected_volume
            data = await request('GET', f'/api/storage/volumes/{volume_id}/directory', params={'path': path, 'refresh': refresh}, timeout=30)
            if selected_volume == volume_id:
                folders[path] = data
            return data

        async def choose_volume(volume_id):
            nonlocal selected_volume, selected_path, selected_kind, selected_entry
            async with lock:
                selected_volume, selected_path, selected_kind, selected_entry = volume_id, '', 'directory', None
                folders.clear()
                expanded.clear()
                expanded.add('')
                limits.clear()
                render_volumes()
                tree_list.clear()
                with tree_list:
                    ui.spinner(size='24px').classes('m-5')
                try:
                    await load_folder('')
                except Exception as error:
                    await error_notice(error)
                render_tree()
                render_properties()

        async def select_root():
            nonlocal selected_path, selected_kind, selected_entry
            selected_path, selected_kind, selected_entry = '', 'directory', None
            render_tree()
            render_properties()

        async def select_entry(entry, toggle=False):
            nonlocal selected_path, selected_kind, selected_entry
            async with lock:
                selected_path, selected_kind, selected_entry = entry['path'], entry['kind'], entry
                if selected_kind == 'directory':
                    if toggle and selected_path in expanded:
                        expanded.remove(selected_path)
                    else:
                        try:
                            if selected_path not in folders:
                                await load_folder(selected_path)
                            expanded.add(selected_path)
                        except Exception as error:
                            await error_notice(error)
                render_tree()
                render_properties()

        def show_more(path):
            limits[path] = limits.get(path, 150) + 150
            render_tree()

        def render_tree():
            visible_rows = count()
            volume = current_volume()
            if not volume:
                return
            tree_title.text = volume['name']
            tree_path.text = volume['mount_path'] or volume.get('network_url') or 'Не подключён'
            tree_list.clear()
            selected_snapshot = folders.get(selected_path, folders.get('', {}))
            if selected_snapshot.get('scanned_at'):
                prefix = 'Сохранённый снимок' if selected_snapshot.get('cached') or volume['availability'] != 'online' else 'Папка прочитана'
                snapshot_label.text = f'{prefix}: {format_date(selected_snapshot["scanned_at"])}'
            else:
                snapshot_label.text = 'Эта папка ещё не прочитана; сохранённого снимка нет.'

            def branch(path, depth):
                data = folders.get(path)
                if not data:
                    return
                if data.get('error'):
                    ui.label(data['error']).classes('s-error mx-3 mb-2')
                if not data.get('scanned_at'):
                    ui.label('Снимок папки не сохранён. Подключи том и открой её.').classes('s-note mx-3 mb-2')
                    return
                entries = [e for e in data['entries'] if show_hidden.value or not e['name'].startswith('.')]
                if not entries:
                    ui.label('Нет видимых элементов' if data['entries'] else 'Папка пуста').classes('s-muted text-xs p-4')
                limit = limits.get(path, 150)
                for entry in entries[:limit]:
                    is_directory = entry['kind'] == 'directory'
                    stripe = ' alt' if next(visible_rows) % 2 else ''
                    with ui.element('div').classes('s-entry s-list-grid' + stripe + (' selected' if entry['path'] == selected_path else '')):
                        with ui.row().classes('s-name-cell').style(f'padding-left:{4 + depth * 14}px'):
                            if is_directory:
                                ui.button(icon='expand_more' if entry['path'] in expanded else 'chevron_right', on_click=lambda e=entry: select_entry(e, True)).props('flat dense color=grey-7').classes('s-tree-toggle').tooltip('Свернуть' if entry['path'] in expanded else 'Раскрыть папку')
                            else:
                                ui.element('span').classes('s-tree-spacer')
                            if is_directory:
                                folder_icon()
                            else:
                                ui.icon({'file': 'insert_drive_file', 'symlink': 'link', 'mount': 'storage'}[entry['kind']], size='14px').classes('s-muted shrink-0')
                            ui.button(entry['name'], on_click=lambda e=entry: select_entry(e)).props('flat dense no-caps color=dark').classes('s-entry-name').tooltip(entry['name'])
                            if is_directory:
                                values = entry['metadata']['effective']
                                role = values.get('role') or ''
                                if role:
                                    ui.label({'primary': 'Осн.', 'copy': 'Копия', 'archive': 'Архив', 'temporary': 'Врем.'}[role]).classes('s-tree-role').tooltip(ROLES[role])
                                for flag, icon in [('no_duplicate', 'block'), ('planned_move', 'drive_file_move')]:
                                    if values.get(flag):
                                        ui.icon(icon, size='12px').classes('s-muted shrink-0').tooltip(FLAGS[flag])
                        ui.label(format_date(entry.get('modified_at'))).classes('s-entry-cell')
                        ui.label(format_bytes(entry['size']) if entry.get('size') is not None else '—').classes('s-entry-cell s-entry-size')
                        kind = {'directory': 'Папка', 'symlink': 'Ссылка', 'mount': 'Том'}.get(entry['kind'])
                        if kind is None:
                            kind = PurePosixPath(entry['name']).suffix[1:].upper() or 'Файл'
                        ui.label(kind).classes('s-entry-cell').tooltip(kind)
                    if is_directory and entry['path'] in expanded:
                        branch(entry['path'], depth + 1)
                if len(entries) > limit:
                    ui.button(f'Ещё {len(entries) - limit} элементов', on_click=lambda p=path: show_more(p)).props('flat no-caps color=dark').classes('ml-8')
            with tree_list:
                with ui.element('div').classes('s-tree-heading s-list-grid'):
                    for title in ['Имя', 'Дата изменения', 'Размер', 'Тип']:
                        with ui.element('div'):
                            ui.label(title)
                branch('', 0)

        def render_properties():
            if editing:
                return
            volume = current_volume()
            properties.clear()
            if not volume:
                with properties:
                    ui.label('Выбери том или папку').classes('s-muted text-sm')
                return
            metadata = folders.get(selected_path, {}).get('metadata') if selected_kind == 'directory' else None
            metadata = metadata or (selected_entry or {}).get('metadata') or volume['metadata']
            with properties:
                ui.label('СВОЙСТВА').classes('s-caption')
                with ui.column().classes('gap-2 w-full'):
                    if selected_path and selected_kind == 'directory':
                        folder_icon(28)
                    else:
                        ui.icon('storage' if not selected_path else 'insert_drive_file', size='30px').classes('text-green-900')
                    ui.label(PurePosixPath(selected_path).name if selected_path else volume['name']).classes('text-lg font-semibold break-all')
                    ui.label(str(PurePosixPath(volume['mount_path']) / selected_path) if volume['mount_path'] else volume.get('network_url') or 'Не подключён').classes('s-path s-muted')
                with ui.row().classes('gap-1 w-full'):
                    tags(metadata)
                for field, mapping, title in [('purpose', PURPOSES, 'Назначение'), ('role', ROLES, 'Хранение')]:
                    value = metadata['effective'][field]
                    with ui.column().classes('gap-1 w-full'):
                        ui.label(title).classes('s-muted text-xs')
                        ui.label(mapping[value]).classes('text-sm font-medium')
                        origin = metadata['inherited_from'].get(field)
                        if origin is not None:
                            ui.label('От тома' if not origin else f'От папки: {origin}').classes('s-muted text-xs')
                if volume.get('network_url') and volume['availability'] != 'online':
                    ui.button('Подключить на M4', icon='lan', on_click=lambda v=volume: connect_volume(v['id'])).props('outline no-caps color=dark').classes('w-full')
                if selected_kind == 'directory':
                    ui.button('Изменить роли', icon='edit_note', on_click=lambda: edit_metadata(metadata)).props('outline no-caps color=dark').classes('w-full')
                if metadata['effective'].get('role') == 'copy':
                    ui.label('Назначена роль копии. Совпадение файлов ещё не проверялось.').classes('s-note')
                comment = metadata['own'].get('comment')
                if comment:
                    ui.label(comment).classes('text-sm whitespace-pre-wrap break-all')
                ui.element('div').classes('s-divider')
                ui.label({'internal': 'Внутренний диск M4', 'external': 'Внешний диск M4', 'network': 'Сетевой том NAS'}.get(volume['kind'], 'Том')).classes('s-muted text-xs')
                ui.label(f'Последнее обнаружение: {format_date(volume["last_seen"])}').classes('s-muted text-xs')
                if selected_entry and selected_entry.get('modified_at'):
                    ui.label(f'Изменён: {format_date(selected_entry["modified_at"])}').classes('s-muted text-xs')
                if selected_kind in {'symlink', 'mount'}:
                    ui.label('Переход по ссылкам и на вложенные тома отключён.').classes('s-note')
                ui.label('Отметки хранятся в приложении. Имена и содержимое файлов не меняются.').classes('s-note')
                ui.label('Для отключённого тома доступны только ранее просмотренные папки.').classes('s-muted text-xs')

        async def edit_metadata(metadata):
            nonlocal editing
            editing = True
            volume_id, path = selected_volume, selected_path
            own = metadata['own']
            inherit = '__inherit__'
            with ui.dialog() as dialog, ui.card().classes('w-[460px] max-w-full p-6 gap-4'):
                ui.label('Роли и назначение').classes('text-lg font-semibold')
                ui.label(PurePosixPath(path).name if path else current_volume()['name']).classes('s-muted text-sm break-all')
                default_label = 'От родительской папки / тома' if path else 'Не назначено'
                purpose = ui.select({inherit: default_label, **PURPOSES}, value=own['purpose'] if own['purpose'] is not None else inherit, label='Что здесь хранится').props('outlined dense').classes('w-full')
                role = ui.select({inherit: default_label, **ROLES}, value=own['role'] if own['role'] is not None else inherit, label='Роль хранения').props('outlined dense').classes('w-full')
                flag_inputs = {}
                for key, label in FLAGS.items():
                    value = inherit if own[key] is None else 'yes' if own[key] else 'no'
                    flag_inputs[key] = ui.select({inherit: default_label if path else 'Не задано', 'yes': 'Да', 'no': 'Нет'}, value=value, label=label).props('outlined dense').classes('w-full')
                comment = ui.textarea('Комментарий', value=own.get('comment') or '').props('outlined autogrow maxlength=4000').classes('w-full')
                ui.label('Сохраняются только отметки в базе приложения.').classes('s-muted text-xs')
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Отмена', on_click=lambda: dialog.submit(False)).props('flat no-caps color=dark')
                    ui.button('Сохранить отметки', on_click=lambda: dialog.submit(True)).props('unelevated no-caps color=green-9')
            try:
                saved = await dialog
            finally:
                editing = False
            if not saved:
                return
            payload = {'path': path, 'purpose': None if purpose.value == inherit else purpose.value, 'role': None if role.value == inherit else role.value, 'comment': comment.value or ''}
            payload.update({key: None if control.value == inherit else control.value == 'yes' for key, control in flag_inputs.items()})
            try:
                await request('PATCH', f'/api/storage/volumes/{volume_id}/metadata', json=payload)
                if selected_volume == volume_id:
                    for folder in list(folders):
                        await load_folder(folder, False)
                await refresh_volumes()
                render_tree()
                render_properties()
                ui.notify('Отметки сохранены', type='positive')
            except Exception as error:
                await error_notice(error)

        async def connect_volume(volume_id):
            try:
                await request('POST', f'/api/storage/volumes/{volume_id}/connect')
                ui.notify('Заверши подключение в Finder на M4', type='info')
            except Exception as error:
                await error_notice(error)

        async def refresh_folder():
            if not selected_volume:
                return
            path = selected_path if selected_kind == 'directory' else str(PurePosixPath(selected_path).parent)
            path = '' if path == '.' else path
            async with lock:
                try:
                    await load_folder(path)
                    # Discard visible children from this session: they may no longer exist.
                    for descendant in list(folders):
                        if descendant != path and (not path or descendant.startswith(path + '/')):
                            folders.pop(descendant)
                            expanded.discard(descendant)
                    render_tree()
                    render_properties()
                except Exception as error:
                    await error_notice(error)

        async def refresh_volumes(force=False):
            nonlocal volumes
            refresh_button.disable()
            try:
                data = await request('GET', '/api/storage/volumes', params={'refresh': force}, timeout=45)
                volumes = data['volumes']
                render_volumes()
                if folders and not editing:
                    render_tree()
                render_properties()
                if data.get('error'):
                    ui.notify('Не удалось обновить подключение томов. Показаны сохранённые сведения.', type='warning')
            except Exception as error:
                overview.text = 'Нет соединения с Core M4'
                await error_notice(error)
            finally:
                refresh_button.enable()

        await refresh_volumes()
        if volumes:
            initial = next((v for v in volumes if v['name'] == 'Media-copy01'), volumes[0])
            await choose_volume(initial['id'])
        else:
            render_properties()
        ui.timer(30, refresh_volumes)
