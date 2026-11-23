"""Shared layout and menu controls for the storage sidebar."""
from contextlib import contextmanager

from nicegui import ui


SIDEBAR_CSS = """
.commander-sidebar { max-height:calc(100vh - 108px); overflow-y:auto; min-width:0; }
.commander-sidebar .sidebar-section { border-bottom:1px solid var(--s-line); }
.commander-sidebar .sidebar-section:last-child { border-bottom:0; }
.commander-sidebar .nicegui-expansion-content { padding:0; gap:0; }
.commander-sidebar .sidebar-section > .q-expansion-item__container > .q-item {
    min-height:36px; padding:5px 9px; font-size:12px; font-weight:650; color:#596753;
}
.commander-sidebar .sidebar-archive > .q-expansion-item__container > .q-item {
    min-height:29px; padding:2px 9px 2px 16px; font-size:11px; color:#6d776a;
}
.commander-sidebar .q-expansion-item__container > .q-item > .q-item__section--main { white-space:nowrap; }
.commander-sidebar .q-item__section--avatar { min-width:23px; padding-right:5px; }
.commander-sidebar .q-item__section--avatar .q-icon { font-size:16px; }
.sidebar-list { padding:2px 5px 4px; gap:1px; }
.sidebar-caption { min-height:20px; padding:1px 5px; gap:5px; font-size:10px; font-weight:650; color:#636f5f; }
.sidebar-row { min-width:0; min-height:27px; gap:3px; padding:0 2px; border-radius:4px; color:#344334; }
.sidebar-row.chosen { background:#e9f1e5; }
.sidebar-row.offline { color:#737c73; }
.sidebar-row.indented { padding-left:24px; min-height:25px; }
.sidebar-row.copy-dependent { padding-left:calc(24px + var(--copy-depth,0) * 10px); }
.sidebar-row .sidebar-branch-arrow { flex:0 0 auto; color:#668368; }
.sidebar-row .q-btn { min-height:23px; padding:1px 3px; color:inherit; }
.sidebar-row .sidebar-name { width:100%; min-width:0; font-size:11px; }
.sidebar-name .q-btn__content { width:100%; justify-content:flex-start; flex-wrap:nowrap; overflow:hidden; }
.sidebar-name .block { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.sidebar-entry { flex:1; min-width:0; }
.sidebar-copy-origin { max-width:100%; margin:-3px 0 2px 3px; font-size:10px; line-height:13px; color:#526d56; }
.sidebar-copy-summary.q-btn { align-self:flex-start; margin-left:24px; padding:0 3px; max-width:calc(100% - 25px);
    min-height:18px; font-size:10px; line-height:15px; color:#3d6e4c; }
.sidebar-copy-summary .q-btn__content { min-width:0; flex-wrap:nowrap; justify-content:flex-start; gap:3px; }
.sidebar-copy-summary .q-icon { margin:0; font-size:12px; }
.sidebar-copy-summary .block { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.sidebar-leading { flex:0 0 19px; text-align:center; }
.sidebar-readout { flex-shrink:0; max-width:40%; color:#5d6b57; font-size:10px; white-space:nowrap; }
.sidebar-note { padding:2px 6px 2px 25px; color:#64705f; font-size:10px; }
.sidebar-empty { padding:3px 7px; color:#687467; font-size:11px; }
"""


#: Создаёт компактную строку с общими отступами и подсказкой полного названия.
#: В контексте строки размещаются статус и необязательное меню действий.
@contextmanager
def sidebar_line(name, on_open, *, tooltip=None, icon=None, icon_color='', toggle=None,
                 chosen=False, offline=False, indented=False, depth=0, origin=''):
    with ui.row().classes('sidebar-row w-full items-center no-wrap') as line:
        line.classes(add=' '.join(label for label, enabled in
                                  (('chosen', chosen), ('offline', offline), ('indented', indented)) if enabled))
        if toggle:
            toggle()
        elif icon:
            with ui.element('span').classes('sidebar-leading'):
                ui.icon(icon, size='13px').classes(icon_color)
        if origin:
            line.classes('copy-dependent').style(f'--copy-depth:{min(depth, 3)}')
            ui.icon('subdirectory_arrow_right', size='11px').classes('sidebar-branch-arrow')
        with ui.column().classes('sidebar-entry gap-0'):
            button = ui.button(name, color=None, on_click=on_open).props('flat dense no-caps align=left').classes('sidebar-name')
            if tooltip:
                button.tooltip(tooltip)
            if origin:
                ui.label(origin).classes('sidebar-copy-origin truncate')
        yield line


#: Показывает одно и то же меню по кнопке команд и по правому клику на строке.
#: Возвращает контейнер для пунктов меню.
@contextmanager
def sidebar_menu(row):
    with ui.button(icon='more_horiz', color=None).props('flat dense size=sm aria-label="Команды"'):
        with ui.menu().props('anchor="bottom right" self="top right"') as menu:
            yield menu
    row.on('contextmenu', menu.open, js_handler='event => { event.preventDefault(); emit(); }')


#: Рисует заголовок и раскрываемые под ним копии в общей боковой колонке.
#: Сохраняет раскрытие и показывает короткий маршрут в свёрнутом виде.
@contextmanager
def sidebar_branch(expanded, key, copies, header, *, summary=''):
    with ui.column().classes('w-full gap-0'):
        button = None

        #: Отображает актуальный значок и доступное имя переключателя копий.
        #: Использует состояние раскрытия по ключу.
        def update():
            opened = key in expanded
            button.props['icon'] = 'expand_more' if opened else 'chevron_right'
            button.props['aria-expanded'] = str(opened).lower()
            button.props['aria-label'] = 'Свернуть копии' if opened else 'Показать копии'

        #: Переключает видимость копий без пересборки строк источника.
        #: Меняет набор раскрытых ключей.
        def change():
            if key in expanded:
                expanded.remove(key)
            else:
                expanded.add(key)
            children.set_visibility(key in expanded)
            if route is not None:
                route.set_visibility(key not in expanded)
            update()

        #: Создаёт кнопку раскрытия в общей позиции значка строки.
        #: Использует update для начальной подписи SVG и доступного имени.
        def control():
            nonlocal button
            button = ui.button(color=None, on_click=change).props('flat dense size=sm').classes('sidebar-leading')
            update()

        readout = header(control if copies else None)
        route = None
        if summary:
            route = ui.button(summary, icon='account_tree', on_click=change).props(
                'flat dense no-caps').classes('sidebar-copy-summary')
            route.tooltip('Раскрыть цепочку копирования')
            route.set_visibility(key not in expanded)
        with ui.column().classes('w-full gap-0') as children:
            yield readout
        children.set_visibility(key in expanded)
