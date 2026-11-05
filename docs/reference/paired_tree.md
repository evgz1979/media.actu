# Python-обёртка Vue-дерева: `paired_tree.py`

Связывает компонент paired_tree.js с NiceGUI: свойства строк и обработчики выбора, открытия, раскрытия, контекстного меню и файлов корня.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../paired_tree.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [paired_workspace_ui.py](paired_workspace_ui.md).
Тестовые модули с прямым импортом: прямых импортов нет.

## Оглавление определений

- [PairedTree](#symbol-PairedTree) — Связывает виртуальное дерево Vue с событиями и данными NiceGUI.
- [PairedTree.__init__](#symbol-PairedTree.__init__) — Инициализирует PairedTree и его рабочее состояние.
- [PairedTree.set_rows](#symbol-PairedTree.set_rows) — Передаёт компоненту новый список строк и текущий выбранный путь.

<a id="symbol-PairedTree"></a>

## `PairedTree`

[paired_tree.py](../../paired_tree.py) · `PairedTree`

Связывает виртуальное дерево Vue с событиями и данными NiceGUI. Зависимости конструктора: side, on_select, on_open, on_toggle, on_context, on_toggle_files, on_menu_state.

Базовые классы: `Element`.


Состояние, присваиваемое конструктором: .

Именованные методы: `__init__`, `set_rows`.

<a id="symbol-PairedTree.__init__"></a>

## `PairedTree.__init__`

[paired_tree.py](../../paired_tree.py) · `PairedTree.__init__`

Инициализирует PairedTree и его рабочее состояние. Использует self._props.update, self.on, super, super().__init__.

```python
def __init__(self, side, on_select, on_open, on_toggle, on_context, on_toggle_files, on_menu_state)
```

Прямые выражения вызова: `self._props.update`, `self.on`, `super`, `super().__init__`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-PairedTree.set_rows"></a>

## `PairedTree.set_rows`

[paired_tree.py](../../paired_tree.py) · `PairedTree.set_rows`

Передаёт компоненту новый список строк и текущий выбранный путь. Использует self._props.update, self.update.

```python
def set_rows(self, rows, selected)
```

Прямые выражения вызова: `self._props.update`, `self.update`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
