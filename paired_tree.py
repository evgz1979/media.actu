from nicegui.element import Element


#: Связывает виртуальное дерево Vue с событиями и данными NiceGUI.
#: Зависимости конструктора: side, on_select, on_open, on_toggle, on_context, on_toggle_files, on_menu_state.
class PairedTree(Element, component='paired_tree.js'):
    """Only visible rows are mounted; both sides share ordering and scroll position."""

    #: Инициализирует PairedTree и его рабочее состояние.
    #: Использует self._props.update, self.on, super, super().__init__.
    def __init__(self, side, on_select, on_open, on_toggle, on_context, on_toggle_files, on_menu_state):
        super().__init__()
        self._props.update(rows=[], side=side, selected='', empty_text='Папок нет', root_file_count=0, root_files_open=False, sizes={})
        self.on('select', on_select)
        self.on('open', on_open)
        self.on('toggle', on_toggle)
        self.on('context', on_context)
        self.on('menu_state', on_menu_state)
        self.on('toggle_files', on_toggle_files)

    #: Передаёт компоненту новый список строк и текущий выбранный путь.
    #: Использует self._props.update, self.update.
    def set_rows(self, rows, selected):
        self._props.update(rows=rows, selected=selected)
        self.update()
