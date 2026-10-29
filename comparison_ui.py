"""Two-pane inventory comparison UI. All filesystem work belongs to Core."""
from __future__ import annotations

import asyncio

from nicegui import ui

from media_manager.comparison import LABELS, NAME_STATUSES
from storage_ui import CSS, folder_icon


COLORS = {'names_found': '#39754d', 'other_folder': '#8b743e', 'names_missing': '#b87626', 'found': '#39754d', 'cached': '#657891', 'missing': '#b87626',
          'candidate': '#77736c', 'unverified': '#ab5751', 'skipped': '#8b8f92'}
STATES = {'running': 'Выполняется', 'pausing': 'Останавливается', 'paused': 'Остановлено',
          'completed': 'Завершено', 'failed': 'Ошибка'}
COMPARE_CSS = '''
.c-body { padding:20px 26px 26px; width:100%; gap:14px; }
.c-config { display:grid; grid-template-columns:1fr 1fr; gap:18px; width:100%; }
.c-config .q-field__control { min-height:36px; }
.c-panes { display:grid; grid-template-columns:minmax(360px,1.15fr) minmax(320px,1fr); gap:14px; width:100%; align-items:start; }
.c-tree { max-height:calc(100vh - 440px); min-height:260px; overflow:auto; width:100%; }
.c-row { display:flex; align-items:center; gap:4px; height:24px; min-height:24px; padding-right:8px; width:100%; }
.c-row:nth-child(even) { background:#f3f4f5; } .c-row.selected { background:#dce9f8; }
.c-name.q-btn { flex:1; min-width:0; height:22px; min-height:22px; padding:0 2px; text-align:left; border-radius:2px; font-size:12px; font-weight:400; }
.c-name .q-btn__content { width:100%; justify-content:flex-start; flex-wrap:nowrap; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.c-name .block { overflow:hidden; text-overflow:ellipsis; }
.c-status { font-size:10px; white-space:nowrap; max-width:160px; overflow:hidden; text-overflow:ellipsis; }
.c-count { font-size:10px; line-height:16px; padding:0 4px; border-radius:3px; background:#f0f2f0; }
.c-size { width:62px; text-align:right; flex-shrink:0; font-size:10px; color:#93999a; }
.c-filters { padding:6px 10px; border-bottom:1px solid var(--s-line); }
.c-filters .q-btn { padding:2px 7px; min-height:24px; font-size:11px; }
.c-target-place { min-width:0; flex:0 1 45%; max-width:45%; font-size:10px; color:#8b9195; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; text-align:right; }
.c-progress { padding:12px 16px; width:100%; gap:6px; }
@media(max-width:850px) { .c-config,.c-panes { grid-template-columns:1fr; } .c-body { padding:16px; } .c-tree { max-height:440px; } }
'''


def register_comparison_page(request, format_bytes, format_date):
    @ui.page('/compare')
    async def comparison_page(source: str = '', path: str = ''):
        ui.add_head_html('<meta name="color-scheme" content="light">')
        ui.add_css(CSS + COMPARE_CSS)
        volumes = []
        job_id = None
        report = None
        selected_path = None
        expanded = set()
        cache = {}
        status_filter = ''
        target_paths = {}
        lock = asyncio.Lock()
        last_phase = None
        journal_before = None
        filter_signature = None
        right_context = None
        right_generation = 0
        right_roots = []
        right_expanded = set()
        right_cache = {}
        right_selected = None
        right_limit = 100

        async def error_message(error):
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
                    ui.link('Хранилища', '/').classes('s-nav')
                    ui.link('Сверка', '/compare').classes('s-nav active')
                    ui.link('Медиа', '/media').classes('s-nav')
            with ui.row().classes('items-center gap-2 s-readonly'):
                ui.icon('lock_outline', size='15px').classes('s-muted')
                ui.label('Файлы только для чтения').classes('s-muted text-xs')
        with ui.column().classes('c-body'):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.column().classes('gap-1'):
                    ui.label('Сверка с NAS').classes('s-title')
                    ui.label('Поиск по именам папок и файлов. Дальнейшие решения принимаешь ты.').classes('s-muted text-sm')
                history = ui.select({}, label='Сохранённые проверки', on_change=lambda e: choose_job(e.value)).props('outlined dense').classes('w-80')
            with ui.column().classes('s-panel w-full p-4 gap-3'):
                with ui.element('div').classes('c-config'):
                    with ui.column().classes('gap-2 w-full'):
                        ui.label('ИСТОЧНИК').classes('s-caption')
                        source_select = ui.select({}, label='Том', on_change=lambda: update_targets()).props('outlined dense').classes('w-full')
                        source_path = ui.input('Папка внутри тома', value=path, placeholder='Весь том').props('outlined dense').classes('w-full')
                    with ui.column().classes('gap-2 w-full'):
                        ui.label('ГДЕ ИСКАТЬ КОПИИ').classes('s-caption')
                        target_select = ui.select({}, value=[], label='Тома NAS', multiple=True, on_change=lambda: render_target_paths()).props('outlined dense use-chips').classes('w-full')
                        with ui.expansion('Ограничить поиск папками', icon='folder_open').classes('w-full text-xs'):
                            paths_container = ui.column().classes('w-full gap-2')
                with ui.row().classes('w-full items-center justify-between gap-2'):
                    refresh_lists = ui.checkbox('Обновить списки с дисков', value=False).props('dense size=sm').classes('text-xs')
                    start_button = ui.button('Сверить по именам', icon='compare_arrows', on_click=lambda: start()).props('unelevated no-caps color=green-9')
                ui.label('Используем готовые списки. Если списка ещё нет, соберём имена с диска. Содержимое файлов не открывается.').classes('s-muted text-xs')
            with ui.column().classes('s-panel c-progress'):
                with ui.row().classes('w-full items-center justify-between'):
                    phase_label = ui.label('Готово к сверке имён').classes('font-semibold text-sm')
                    with ui.row().classes('gap-2'):
                        pause_button = ui.button('Остановить', icon='pause', on_click=lambda: control('pause')).props('flat dense no-caps color=dark')
                        resume_button = ui.button('Продолжить', icon='play_arrow', on_click=lambda: control('resume')).props('flat dense no-caps color=green-9')
                        journal_button = ui.button('Журнал', icon='receipt_long', on_click=lambda: show_journal()).props('flat dense no-caps color=dark')
                progress = ui.linear_progress(value=0, show_value=False).props('color=green-8').classes('w-full')
                progress_text = ui.label('Готовые списки сохраняются на M4 и используются повторно.').classes('s-muted text-xs')
                current_label = ui.label('').classes('s-path s-muted w-full truncate')
                message_label = ui.label('').classes('text-xs s-muted')
            with ui.element('div').classes('c-panes'):
                with ui.column().classes('s-panel w-full gap-0'):
                    with ui.row().classes('s-panel-head w-full items-center justify-between'):
                        with ui.column().classes('gap-1 min-w-0'):
                            tree_title = ui.label('Дерево источника').classes('font-semibold')
                            tree_subtitle = ui.label('После сканирования здесь появятся все папки и файлы.').classes('s-path s-muted')
                        ui.button(icon='vertical_align_top', on_click=lambda: select_root()).props('flat dense round color=dark aria-label="Результат для всего источника"')
                    filters = ui.row().classes('c-filters w-full gap-1')
                    tree = ui.column().classes('c-tree gap-0')
                with ui.column().classes('s-panel w-full gap-0'):
                    with ui.row().classes('s-panel-head w-full items-center'):
                        ui.label('Что найдено на NAS').classes('font-semibold')
                    evidence = ui.column().classes('c-tree gap-0')
            ui.label('Сопоставляем имя файла и имя его папки без учёта регистра. Размеры, даты и содержимое не сравниваются.').classes('s-muted text-xs')

        def render_target_paths():
            for vid, field in list(target_paths.items()):
                target_paths[vid] = field.value if hasattr(field, 'value') else field
            paths_container.clear()
            with paths_container:
                for vid in target_select.value or []:
                    previous = target_paths.get(vid, '')
                    name = next((v['name'] for v in volumes if v['id'] == vid), vid)
                    target_paths[vid] = ui.input(name, value=previous, placeholder='Весь том').props('outlined dense').classes('w-full')

        def update_targets():
            options = {v['id']: (v.get('display_name') or v['name']) + (' · отключён' if v['availability'] != 'online' else '') for v in volumes
                       if v['kind'] == 'network' and v['id'] != source_select.value and v.get('identity_status') != 'unverified'}
            target_select.options = options
            target_select.value = [v for v in target_select.value or [] if v in options]
            target_select.update()
            render_target_paths()

        async def start():
            nonlocal job_id
            if not source_select.value or not target_select.value:
                ui.notify('Выбери источник и хотя бы один том NAS', type='warning')
                return
            start_button.disable()
            try:
                payload = {'source': {'volume_id': source_select.value, 'path': source_path.value or ''},
                           'targets': [{'volume_id': vid, 'path': target_paths[vid].value if hasattr(target_paths.get(vid), 'value') else target_paths.get(vid, '')}
                                       for vid in target_select.value], 'reuse_index': not bool(refresh_lists.value)}
                created = await request('POST', '/api/storage/comparisons', json=payload, timeout=30)
                await refresh_history()
                await choose_job(created['id'])
            except Exception as error:
                await error_message(error)
            finally:
                start_button.enable()

        async def choose_job(value):
            nonlocal job_id, selected_path, report, last_phase, status_filter
            if not value or value == job_id:
                return
            async with lock:
                job_id = value
                selected_path = None
                status_filter = ''
                expanded.clear()
                cache.clear()
                last_phase = None
                history.set_value(value)
                try:
                    report = await request('GET', f'/api/storage/comparisons/{job_id}')
                    src = next(s for s in report['scans'] if s['side'] == 'source')
                    source_select.set_value(src['volume_id'])
                    source_path.set_value(src['root_path'])
                    update_targets()
                    target_select.set_value([s['volume_id'] for s in report['scans'] if s['side'] == 'target'])
                    render_target_paths()
                    for scan in report['scans']:
                        field = target_paths.get(scan['volume_id'])
                        if scan['side'] == 'target' and hasattr(field, 'set_value'):
                            field.set_value(scan['root_path'])
                    refresh_lists.set_value(not bool(report.get('reuse_index', True)))
                    render_progress()
                    await refresh_tree()
                    await render_evidence()
                except Exception as error:
                    await error_message(error)

        async def refresh_history():
            data = await request('GET', '/api/storage/comparisons')
            history.options = {j['id']: format_date(j['created_at']) + ' · ' + STATES.get(j['state'], j['state']) for j in data['jobs']}
            history.update()
            return data['jobs']

        async def control(action):
            nonlocal report
            if not job_id:
                return
            try:
                updated = await request('POST', f'/api/storage/comparisons/{job_id}/{action}')
                if updated['id'] != job_id:
                    await refresh_history()
                    await choose_job(updated['id'])
                else:
                    report = updated
                    render_progress()
            except Exception as error:
                await error_message(error)

        def render_progress():
            active = report and report['state'] in ('running', 'pausing')
            pause_button.set_visibility(bool(report and report['state'] in ('running', 'pausing')))
            pause_button.set_enabled(bool(report and report['state'] == 'running'))
            legacy = bool(report and report.get('mode') != 'names')
            resume_button.set_visibility(bool(report and (report['state'] in ('paused', 'failed') or (legacy and not active))))
            resume_button.text = 'Сверить по именам' if legacy else 'Продолжить'
            journal_button.set_enabled(bool(report))
            if not report:
                return
            label = format_date(report['created_at']) + ' · ' + STATES.get(report['state'], report['state'])
            if job_id in history.options and history.options[job_id] != label:
                history.options[job_id] = label
                history.update()
            phase = {'index': 'Подготовка списков', 'names': 'Сравнение имён', 'hash': 'Предыдущий отчёт по содержимому', 'done': 'Сверка имён' if not legacy else 'Предыдущий отчёт'}.get(report['phase'], '')
            phase_label.text = phase + ' · ' + STATES.get(report['state'], report['state'])
            progress.value = 1 if report['state'] == 'completed' else 0
            if active:
                progress.props('indeterminate')
            else:
                progress.props(remove='indeterminate')
            reused = sum(bool(s.get('reused_from')) for s in report['scans'])
            progress_text.text = f"Файлов в списках: {report['indexed_files']:,} · папок: {report['indexed_directories']:,}" + (f" · готовых списков: {reused}/{len(report['scans'])}" if reused else '')
            current_label.text = '' if legacy else report['current_path']
            message_label.text = ('Это старый отчёт. Нажми «Сверить по именам»: готовые списки уже сохранены.' if legacy else report['message']) + (f" Ошибок в журнале: {report['errors']}." if report['errors'] else '')
            scans = report['scans']
            src = next(s for s in scans if s['side'] == 'source')
            tree_title.text = src['volume_name']
            tree_subtitle.text = '/' + src['root_path'] + ' · список от ' + format_date(src['finished_at'] or src['started_at'])
            render_filters()

        def render_filters():
            nonlocal filter_signature
            signature = (status_filter, (report or {}).get('mode'), tuple(sorted((report or {}).get('counts', {}).items())))
            if signature == filter_signature:
                return
            filter_signature = signature
            filters.clear()
            with filters:
                choices = ([('', 'Все'), ('names_found', 'Совпали имена'), ('other_folder', 'Другая папка'),
                            ('names_missing', 'Не найдено'), ('unverified', 'Не проверено'), ('skipped', 'Пропущено')]
                           if not report or report.get('mode') == 'names' else
                           [('', 'Старый отчёт'), ('found', 'По содержимому'), ('missing', 'Не найдено'),
                            ('candidate', 'Кандидаты'), ('unverified', 'Не проверено')])
                for status, label in choices:
                    count = report['counts'].get(status, 0) if report and status else None
                    ui.button(label + (f' {count}' if count is not None else ''), on_click=lambda s=status: set_filter(s)).props(('unelevated color=grey-3 text-color=dark' if status == status_filter else 'flat color=grey-7') + ' dense no-caps')

        async def set_filter(value):
            nonlocal status_filter
            status_filter = value
            cache.clear()
            render_filters()
            await refresh_tree()

        async def load_folder(path, more=False):
            if not job_id:
                return
            requested_job, requested_filter = job_id, status_filter
            offset = len(cache[path]['entries']) if more and path in cache else 0
            data = await request('GET', f'/api/storage/comparisons/{requested_job}/tree', params={'path': path, 'status': requested_filter, 'offset': offset})
            if requested_job != job_id or requested_filter != status_filter:
                return
            if more and path in cache:
                data['entries'] = cache[path]['entries'] + data['entries']
            cache[path] = data

        async def refresh_tree():
            if not report:
                return
            root = next(s['root_path'] for s in report['scans'] if s['side'] == 'source')
            expanded.add(root)
            for folder in list(expanded):
                if folder not in cache:
                    await load_folder(folder)
            render_tree()

        async def select(entry, toggle=False):
            nonlocal selected_path
            selected_path = entry['path']
            if entry['kind'] == 'directory' and toggle:
                if entry['path'] in expanded:
                    expanded.remove(entry['path'])
                else:
                    expanded.add(entry['path'])
                    if entry['path'] not in cache:
                        await load_folder(entry['path'])
            render_tree()
            await render_evidence()

        async def select_root():
            nonlocal selected_path
            selected_path = None
            render_tree()
            await render_evidence()

        async def show_more(path):
            await load_folder(path, more=True)
            render_tree()

        def render_tree():
            tree.clear()
            if not report:
                return
            root = next(s['root_path'] for s in report['scans'] if s['side'] == 'source')
            def branch(path, depth=0):
                data = cache.get(path, {})
                for entry in data.get('entries', []):
                    directory = entry['kind'] == 'directory'
                    with ui.row().classes('c-row no-wrap' + (' selected' if entry['path'] == selected_path else '')).style(f'padding-left:{8 + depth * 14}px'):
                        if directory:
                            ui.button(icon='expand_more' if entry['path'] in expanded else 'chevron_right', on_click=lambda e=entry: select(e, True)).props('flat dense round color=grey-7').classes('s-tree-toggle')
                            folder_icon()
                        else:
                            ui.element('span').classes('s-tree-spacer')
                            ui.icon('insert_drive_file' if entry['kind'] == 'file' else 'link', size='14px').classes('s-muted')
                        ui.button(entry['name'], on_click=lambda e=entry: select(e, e['kind'] == 'directory')).props('flat dense no-caps color=dark').classes('c-name')
                        if directory:
                            if entry.get('error'):
                                ui.label('Ошибка чтения').classes('c-status').style('color:' + COLORS['unverified'])
                            if report.get('mode') == 'names' and entry.get('status') in ('names_found', 'names_missing'):
                                ui.icon('check' if entry['status'] == 'names_found' else 'remove', size='12px').style('color:' + COLORS[entry['status']])
                            for status in (NAME_STATUSES if report.get('mode') == 'names' else ('found', 'cached', 'missing', 'unverified', 'candidate')):
                                count = entry.get('counts', {}).get(status, 0)
                                if count:
                                    ui.label(str(count)).classes('c-count').style('color:' + COLORS[status])
                        else:
                            status = entry.get('status') or 'unverified'
                            ui.label(LABELS[status]).classes('c-status').style('color:' + COLORS[status])
                    if directory and entry['path'] in expanded:
                        branch(entry['path'], depth + 1)
                if len(data.get('entries', [])) < data.get('total', 0):
                    ui.button('Показать ещё…', on_click=lambda p=path: show_more(p)).props('flat dense no-caps color=grey-7').style(f'margin-left:{depth * 14 + 24}px')
            with tree:
                branch(root)
                if not cache.get(root, {}).get('entries'):
                    ui.label('Подходящих элементов пока нет.' if status_filter else 'Пустая папка или обход ещё не завершён.').classes('s-muted text-xs p-4')

        def render_right_tree():
            evidence.clear()
            with evidence:
                if not right_roots:
                    return
                def node(entry, scope, depth=0, root=False):
                    key = (entry['scan_id'], entry['path'])
                    directory = entry['kind'] == 'directory'
                    with ui.row().classes('c-row no-wrap' + (' selected' if key == right_selected else '')).style(f'padding-left:{8 + depth * 14}px'):
                        if directory:
                            ui.button(icon='expand_more' if key in right_expanded else 'chevron_right', on_click=lambda e=entry: select_right(e)).props('flat dense round color=grey-7 aria-label="Раскрыть папку NAS"').classes('s-tree-toggle')
                            folder_icon()
                        else:
                            ui.element('span').classes('s-tree-spacer')
                            ui.icon('insert_drive_file' if entry['kind'] == 'file' else 'link', size='14px').classes('s-muted')
                        ui.button(entry['name'], on_click=lambda e=entry: select_right(e)).props('flat dense no-caps color=dark').classes('c-name')
                        if entry.get('error'):
                            ui.icon('error_outline', size='12px').style('color:' + COLORS['unverified'])
                        if root:
                            parent = entry['path'].rpartition('/')[0]
                            ui.label(scope['volume_name'] + ' /' + parent).classes('c-target-place')
                    if directory and key in right_expanded:
                        data = right_cache.get(key, {})
                        for child in data.get('entries', []):
                            node(child, scope, depth + 1)
                        if data.get('error'):
                            ui.label(data['error']).classes('text-xs text-orange-800 py-1 px-6')
                        elif not data.get('entries'):
                            ui.label('Пустая папка').classes('s-muted text-xs py-1').style(f'padding-left:{36 + (depth + 1) * 14}px')
                        if len(data.get('entries', [])) < data.get('total', 0):
                            ui.button('Показать ещё…', on_click=lambda e=entry: more_right(e)).props('flat dense no-caps color=grey-7').style(f'margin-left:{28 + depth * 14}px')
                for entry in right_roots:
                    node(entry, entry, root=True)
                if len(right_roots) == right_limit:
                    ui.label('Показаны первые 100 найденных путей.').classes('s-muted text-xs p-3')

        async def load_right(entry, more=False):
            key = (entry['scan_id'], entry['path'])
            requested_job, generation = job_id, right_generation
            offset = len(right_cache[key]['entries']) if more and key in right_cache else 0
            try:
                data = await request('GET', f'/api/storage/comparisons/{requested_job}/target-tree', params={'scan_id': key[0], 'path': key[1], 'offset': offset})
            except Exception as error:
                if generation == right_generation:
                    await error_message(error)
                return False
            if requested_job != job_id or generation != right_generation:
                return False
            if more and key in right_cache:
                data['entries'] = right_cache[key]['entries'] + data['entries']
            right_cache[key] = data
            return True

        async def select_right(entry):
            nonlocal right_selected
            key = (entry['scan_id'], entry['path'])
            right_selected = key
            if entry['kind'] == 'directory':
                if key in right_expanded:
                    right_expanded.remove(key)
                else:
                    if key not in right_cache and not await load_right(entry):
                        return
                    right_expanded.add(key)
            render_right_tree()

        async def more_right(entry):
            if await load_right(entry, more=True):
                render_right_tree()

        async def render_evidence():
            nonlocal right_context, right_generation, right_roots, right_selected, right_limit
            context = (job_id, selected_path)
            if context != right_context:
                right_context = context
                right_generation += 1
                right_roots = []
                right_expanded.clear()
                right_cache.clear()
                right_selected = None
                evidence.clear()
            if not report or selected_path is None:
                evidence.clear()
                with evidence:
                    ui.label('Выбери папку или файл слева.').classes('s-muted text-xs p-4')
                return
            if report.get('mode') != 'names':
                evidence.clear()
                with evidence:
                    ui.label('Для этого отчёта сначала выполни сверку по именам.').classes('s-muted text-xs p-4')
                return
            requested_job, requested_path, generation = job_id, selected_path, right_generation
            try:
                data = await request('GET', f'/api/storage/comparisons/{requested_job}/detail', params={'path': requested_path})
            except Exception:
                if generation == right_generation:
                    evidence.clear()
                    with evidence:
                        ui.label('Эта часть списка ещё не готова.').classes('s-muted text-xs p-4')
                return
            if requested_job != job_id or requested_path != selected_path or generation != right_generation:
                return
            right_roots = data['matches']
            right_limit = data['matches_limit']
            render_right_tree()
            if not right_roots:
                with evidence:
                    ui.label('Совпадений по имени не найдено.' if data['entry'].get('status') == 'names_missing' else 'Найденных путей пока нет.').classes('s-muted text-xs p-4')

        async def show_journal():
            nonlocal journal_before
            journal_before = None
            with ui.dialog() as dialog, ui.card().classes('w-full max-w-3xl'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Журнал сверки').classes('text-lg font-semibold')
                    ui.button(icon='close', on_click=dialog.close).props('flat round dense')
                log = ui.column().classes('w-full gap-2 max-h-96 overflow-auto')
                async def load(older=False):
                    nonlocal journal_before
                    data = await request('GET', f'/api/storage/comparisons/{job_id}/events', params={'before': journal_before} if older and journal_before else {})
                    if not older:
                        log.clear()
                    with log:
                        for event in data['events']:
                            with ui.column().classes('gap-0 w-full border-b pb-2'):
                                ui.label(format_date(event['at']) + ' · ' + event['message']).classes('text-xs' + (' text-orange-800' if event['level'] != 'info' else ''))
                                if event['path']:
                                    ui.label(event['path']).classes('s-path s-muted')
                    if data['events']:
                        journal_before = data['events'][-1]['id']
                    older_button.set_enabled(len(data['events']) == 100)
                with ui.row().classes('w-full justify-between'):
                    older_button = ui.button('Более ранние записи', on_click=lambda: load(True)).props('flat no-caps')
                    ui.button('Обновить', on_click=lambda: load()).props('flat no-caps')
            await load()
            dialog.open()

        async def poll():
            nonlocal report, last_phase
            if not job_id or lock.locked() or (report and report['state'] == 'completed' and last_phase == ('done', 'completed')):
                return
            async with lock:
                try:
                    previous = report
                    report = await request('GET', f'/api/storage/comparisons/{job_id}')
                    render_progress()
                    marker = (report['phase'], report['state'])
                    if marker != last_phase or (report['phase'] == 'index' and report['state'] == 'running'):
                        cache.clear()
                        await refresh_tree()
                        await render_evidence()
                        last_phase = marker
                    elif previous and previous['state'] != report['state']:
                        await render_evidence()
                except Exception:
                    phase_label.text = 'Нет связи с Core — сохранённые результаты остаются в базе'

        render_progress()
        await render_evidence()
        try:
            volumes = (await request('GET', '/api/storage/volumes', timeout=45))['volumes']
            selectable = [v for v in volumes if v.get('identity_status') != 'unverified']
            source_select.options = {v['id']: (v.get('display_name') or v['name']) + (' · сменный' if v.get('removable') else '') + (' · отключён' if v['availability'] != 'online' else '') for v in selectable}
            default = source if source in source_select.options else next((v['id'] for v in selectable if v.get('removable') and v['availability'] == 'online'), None)
            source_select.set_value(default)
            update_targets()
            target_select.set_value([v['id'] for v in volumes if v['name'] in ('Media-copy01', 'Media-copy02') and v['id'] != default])
            render_target_paths()
            jobs = await refresh_history()
            if jobs and not source:
                await choose_job(jobs[0]['id'])
        except Exception as error:
            await error_message(error)
        ui.timer(2, poll)
