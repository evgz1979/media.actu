from nicegui.element import Element


class PairedTree(Element, component='paired_tree.js'):
    """Only visible rows are mounted; both sides share ordering and scroll position."""

    def __init__(self, side, on_select, on_open, on_toggle, on_context):
        super().__init__()
        self._props.update(rows=[], side=side, selected='', empty_text='Папок нет')
        self.on('select', on_select)
        self.on('open', on_open)
        self.on('toggle', on_toggle)
        self.on('context', on_context)

    def set_rows(self, rows, selected):
        self._props.update(rows=rows, selected=selected)
        self.update()
