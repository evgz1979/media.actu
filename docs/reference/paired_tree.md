# Python-обёртка Vue-дерева: `paired_tree.py`

Связывает компонент paired_tree.js с NiceGUI: свойства строк и обработчики выбора, открытия, раскрытия, контекстного меню и файлов корня.

[Исходный модуль](../../paired_tree.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [paired_workspace_ui.py](paired_workspace_ui.md).
Тестовые модули с прямым импортом: нет; возможна косвенная проверка через вызывающие компоненты.

## Оглавление определений

- [PairedTree](#symbol-pairedtree) — Связывает виртуальное дерево Vue с событиями и данными NiceGUI.
- [PairedTree.__init__](#symbol-pairedtree---init--) — Инициализирует PairedTree и его рабочее состояние.
- [PairedTree.set_rows](#symbol-pairedtree-set-rows) — Передаёт компоненту новый список строк и текущий выбранный путь.

<a id="symbol-pairedtree"></a>

## `PairedTree`

[paired_tree.py:6](../../paired_tree.py#L6)

Связывает виртуальное дерево Vue с событиями и данными NiceGUI. Зависимости конструктора: side, on_select, on_open, on_toggle, on_context, on_toggle_files, on_menu_state.

Базовые классы: `Element`.


Состояние, присваиваемое конструктором: .

Именованные методы: `__init__`, `set_rows`.

<a id="symbol-pairedtree---init--"></a>

## `PairedTree.__init__`

[paired_tree.py:11](../../paired_tree.py#L11)

Инициализирует PairedTree и его рабочее состояние. Использует self._props.update, self.on, super, super().__init__.

```python
def __init__(self, side, on_select, on_open, on_toggle, on_context, on_toggle_files, on_menu_state)
```

Прямые выражения вызова: `self._props.update`, `self.on`, `super`, `super().__init__`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-pairedtree-set-rows"></a>

## `PairedTree.set_rows`

[paired_tree.py:23](../../paired_tree.py#L23)

Передаёт компоненту новый список строк и текущий выбранный путь. Использует self._props.update, self.update.

```python
def set_rows(self, rows, selected)
```

Прямые выражения вызова: `self._props.update`, `self.update`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
