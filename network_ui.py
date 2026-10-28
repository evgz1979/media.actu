"""NAS selection dialog. All discovery and connection actions run on Core's Mac."""
from __future__ import annotations

from nicegui import ui


async def show_network_dialog(request, format_date, on_changed):
    servers = []
    selected = None
    shares_data = None
    ui.add_css('''
        .nas-grid { display:grid; grid-template-columns:220px minmax(0,1fr); gap:18px; width:100%; }
        .nas-servers { border-right:1px solid #e2e6df; padding-right:14px; }
        .nas-choice { text-align:left; padding:12px; border-radius:8px; border:1px solid transparent; cursor:pointer; width:100%; }
        .nas-choice.selected { background:#edf3e8; border-color:#b7c8b0; }
        .nas-choice:hover { background:#f5f7f1; }
        .nas-shares { max-height:58vh; overflow:auto; width:100%; }
        .nas-share { border-bottom:1px solid #e2e6df; padding:12px 2px; }
        @media(max-width:700px) { .nas-grid { grid-template-columns:1fr; } .nas-servers { border-right:0; border-bottom:1px solid #e2e6df; padding-bottom:12px; max-height:180px; overflow:auto; } }
    ''')
    with ui.dialog() as dialog, ui.card().classes('w-[1000px] max-w-[95vw] p-6 gap-4'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label('NAS в локальной сети').classes('text-xl font-semibold')
                ui.label('Поиск выполняется на M4. Ресурсы можно запомнить без подключения.').classes('s-muted text-sm')
            ui.button(icon='close', on_click=dialog.close).props('flat round dense color=dark aria-label="Закрыть поиск NAS"')
        with ui.row().classes('w-full items-center justify-between'):
            search_status = ui.label('Поиск NAS…').classes('s-muted text-sm')
            scan_button = ui.button('Повторить поиск', icon='search', on_click=lambda: scan()).props('outline no-caps color=dark')
        warning = ui.label('').classes('s-error w-full')
        warning.set_visibility(False)
        with ui.element('div').classes('nas-grid'):
            server_list = ui.column().classes('nas-servers w-full gap-2')
            with ui.column().classes('w-full gap-3 min-w-0'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('gap-1 min-w-0'):
                        shares_title = ui.label('Выбери NAS').classes('font-semibold text-base')
                        shares_status = ui.label('Здесь появятся его сетевые ресурсы.').classes('s-muted text-xs')
                    reload_button = ui.button(icon='refresh', on_click=lambda: load_shares(True)).props('flat round dense color=dark aria-label="Обновить ресурсы NAS"')
                    reload_button.disable()
                share_list = ui.column().classes('nas-shares gap-0')
        ui.label('«Добавить» сохраняет ресурс в списке томов. «Подключить на M4» открывает Finder на M4; пароль приложение не запрашивает.').classes('s-note w-full')

    def show_warning(message):
        warning.text = message or ''
        warning.set_visibility(bool(message))

    def render_servers():
        server_list.clear()
        with server_list:
            if not servers:
                ui.label('NAS пока не найдены. Устройство должно быть включено и находиться в доступной M4 сети.').classes('s-muted text-sm')
            for server in servers:
                with ui.column().classes('nas-choice gap-1' + (' selected' if server['id'] == selected else '')).on('click', lambda s=server: choose_server(s['id'])):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('dns', size='20px').classes('text-green-900')
                        ui.label(server['name']).classes('font-semibold text-sm break-all')
                    ui.label(server['host']).classes('s-path s-muted')
                    ui.label('Найден в последнем поиске' if server['discovered'] else 'Сохранён ранее').classes('s-muted text-xs')

    def render_shares():
        share_list.clear()
        if not shares_data:
            return
        server = shares_data['server']
        shares_title.text = server['name']
        count = len(shares_data['shares'])
        date = format_date(server.get('shares_at'))
        shares_status.text = f'Ресурсов: {count} · ' + ('сохранённый список: ' if shares_data['cached'] else 'прочитано: ') + date
        show_warning(shares_data.get('error'))
        with share_list:
            if not shares_data['shares']:
                ui.label('Список ресурсов ещё не получен.' if not server.get('shares_at') else 'Файловые ресурсы не найдены.').classes('s-muted text-sm py-4')
            for share in shares_data['shares']:
                with ui.row().classes('nas-share w-full items-center justify-between gap-3'):
                    with ui.column().classes('gap-1 grow min-w-0'):
                        ui.label(share['name']).classes('text-sm font-semibold break-all')
                        if share['comment']:
                            ui.label(share['comment']).classes('s-muted text-xs')
                        if not share['present']:
                            ui.label('Не найден в последнем списке').classes('s-muted text-xs')
                    with ui.row().classes('items-center gap-2'):
                        if share['volume_id']:
                            ui.label('В списке томов').classes('s-tag role')
                        else:
                            ui.button('Добавить', on_click=lambda s=share: remember_share(s)).props('outline dense no-caps color=dark')
                        ui.button('Подключить на M4', on_click=lambda s=share: remember_share(s, True)).props('flat dense no-caps color=dark')

    async def remember_share(share, connect=False):
        server_id = selected
        try:
            volume = await request('POST', f'/api/storage/nas/{server_id}/remember', json={'share': share['name']})
            if connect:
                await request('POST', f'/api/storage/volumes/{volume["id"]}/connect')
                ui.notify('Заверши подключение в Finder на M4', type='info')
            else:
                ui.notify('Ресурс добавлен в список томов', type='positive')
            await on_changed()
            if selected == server_id:
                await load_shares(False)
        except Exception:
            show_warning('Не удалось выполнить действие. Проверь соединение с Core M4 и повтори.')

    async def choose_server(server_id):
        nonlocal selected, shares_data
        selected, shares_data = server_id, None
        render_servers()
        share_list.clear()
        await load_shares(True)

    async def load_shares(refresh):
        nonlocal shares_data
        if not selected:
            return
        server_id = selected
        reload_button.disable()
        shares_status.text = 'Чтение ресурсов NAS…' if refresh else 'Загрузка сохранённого списка…'
        show_warning(None)
        try:
            data = await request('GET', f'/api/storage/nas/{server_id}/shares', params={'refresh': refresh}, timeout=20)
            if selected == server_id:
                shares_data = data
                render_shares()
        except Exception:
            if selected == server_id:
                show_warning('Не удалось прочитать список ресурсов. Попробуй обновить его ещё раз.')
        finally:
            reload_button.set_enabled(bool(selected))

    async def scan():
        nonlocal servers
        scan_button.disable()
        search_status.text = 'Поиск NAS на M4…'
        show_warning(None)
        try:
            data = await request('POST', '/api/storage/nas/discover', timeout=45)
            servers = data['servers']
            count = sum(bool(s['discovered']) for s in servers)
            search_status.text = f'Найдено серверов: {count} · сохранено: {len(servers)}'
            render_servers()
            show_warning(data.get('error'))
        except Exception:
            search_status.text = 'Поиск не завершён'
            show_warning('Проверь доступность Core M4 и повтори поиск.')
        finally:
            scan_button.enable()

    dialog.open()
    try:
        data = await request('GET', '/api/storage/nas')
        servers = data['servers']
        render_servers()
    except Exception:
        pass
    await scan()
