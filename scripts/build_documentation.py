"""Rebuild semantic documentation and validate stable symbol links."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
import difflib
import json
import os
from pathlib import Path
import posixpath
import re
import sqlite3
import subprocess
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = Path('scripts/documentation_metadata.json')
DEFINITION_TYPES = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
PYTHON_GLOBS = ('*.py', 'media_manager/*.py', 'scripts/*.py')
GENERATED_NOTICE = 'Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.'
TOKEN_PATTERN = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`'
    r'|//[^\n]*|/\*[\s\S]*?\*/|\s+|[A-Za-z_][\w]*|[^\s]',
    re.DOTALL,
)


#: Сообщает о нарушенной структуре справочника, комментариев или ссылок.
#: Используется CLI и тестами для явного отказа проверки актуальности.
class DocumentationError(Exception):
    pass


#: Хранит устойчивую идентичность определения и его пояснения.
#: Позиции узла используются только при чтении исходника и не выводятся в справочник.
@dataclass
class Symbol:
    path: str
    name: str
    anchor: str
    node: ast.AST | None
    explanation: tuple[str, str]
    signature: str = ''
    start: int = 0
    end: int = 0


#: Собирает полные лексические имена классов, функций и вложенных обработчиков.
#: Счётчик одноимённых объявлений различает повторные определения в одной области.
class Definitions(ast.NodeVisitor):
    #: Создаёт стек лексических областей и список найденных объявлений.
    #: Для обхода одного AST используется отдельный экземпляр посетителя.
    def __init__(self):
        self.stack = []
        self.nodes = []

    #: Добавляет объявление с именами всех содержащих классов и функций.
    #: Обходит вложенные определения с восстановлением стека при выходе.
    def definition(self, node):
        name = '.'.join([*self.stack, node.name])
        self.nodes.append((name, node))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_ClassDef = definition
    visit_FunctionDef = definition
    visit_AsyncFunctionDef = definition


#: Возвращает объявления Python с полными лексическими именами.
#: Разбор AST исключает влияние пробелов и обычных комментариев.
def definitions(text):
    visitor = Definitions()
    visitor.visit(ast.parse(text))
    return visitor.nodes


#: Выбирает узлы собственного тела определения для подробного справочника.
#: Вложенные функции, классы и lambda описываются в своих областях.
def scope_nodes(node):
    result = []
    pending = list(reversed(node.body))
    while pending:
        current = pending.pop()
        if isinstance(current, (*DEFINITION_TYPES, ast.Lambda)):
            continue
        result.append(current)
        pending.extend(reversed(list(ast.iter_child_nodes(current))))
    return result


#: Получает ровно две помеченные строки пояснения перед объявлением.
#: Пропускает пустые строки и обычные комментарии между пояснением и кодом.
def explanation_at(text, line, prefix='#:'):
    collected = []
    for raw in reversed(text.splitlines()[:line - 1]):
        value = raw.strip()
        if value.startswith(prefix):
            collected.append(value[len(prefix):].strip())
        elif value and not value.startswith(('#', '//', '--')):
            break
    if len(collected) != 2 or not all(collected):
        raise DocumentationError(f'Перед объявлением требуются две строки {prefix} пояснения')
    return tuple(reversed(collected))


#: Строит непотерянный якорь по полному имени и номеру повторного объявления.
#: Регистр, точки и подчёркивания имён сохраняются для различения определений.
def symbol_anchor(name, occurrence=1):
    suffix = f'--declaration-{occurrence}' if occurrence > 1 else ''
    return 'symbol-' + name + suffix


#: Разбирает Python-модуль и проверяет покрытие пояснениями каждого определения.
#: Сортирует результат по устойчивым якорям, исключая физический порядок разных имён.
def python_symbols(path, text):
    counts = Counter()
    result = []
    for name, node in definitions(text):
        counts[name] += 1
        start = min([node.lineno, *[d.lineno for d in node.decorator_list]])
        try:
            explanation = explanation_at(text, start)
        except DocumentationError as error:
            raise DocumentationError(f'{path} / {name}: {error}') from error
        result.append(Symbol(path, name, symbol_anchor(name, counts[name]), node, explanation))
    return sorted(result, key=lambda symbol: symbol.anchor)


#: Преобразует путь Python-модуля в имя страницы справочника.
#: Разделитель каталогов кодируется двойным дефисом, расширение убирается.
def reference_name(path):
    return path.removesuffix('.py').replace('/', '--') + '.md'


#: Формирует относительную Markdown-ссылку с необязательным устойчивым якорем.
#: Вычисление пути зависит от каталогов документов и не использует номера строк.
def link_from(document, target, label, anchor=''):
    relative = posixpath.relpath(target, posixpath.dirname(document) or '.')
    fragment = '#' + quote(anchor, safe='._-') if anchor else ''
    return f'[{label}]({relative}{fragment})'


#: Возвращает ссылку на полное определение в Python- или нативном справочнике.
#: Исходные файлы открываются отдельными ссылками без физического номера строки.
def symbol_link(document, symbol, label=None):
    target = ('docs/reference/' + reference_name(symbol.path)
              if symbol.path.endswith('.py') else 'docs/reference/native.md')
    return link_from(document, target, label or symbol.name, symbol.anchor)


#: Экранирует короткое выражение для Markdown и таблиц.
#: Многострочный исходный текст нормализуется в одну строку представления.
def literal(value):
    return '`' + str(value).replace('|', '&#124;').replace('`', '&#96;').replace('\n', ' ') + '`'


#: Извлекает присваиваемые поля self из собственного тела определения.
#: Сортировка полей обеспечивает одинаковое представление независимых присваиваний.
def own_assignments(node):
    return sorted({part.attr for part in scope_nodes(node)
                   if isinstance(part, ast.Attribute) and isinstance(part.ctx, ast.Store)
                   and isinstance(part.value, ast.Name) and part.value.id == 'self'})


#: Выбирает аннотированные поля класса с точными выражениями значений.
#: Типы берутся из AST без исполнения кода и без предположений о неявных типах.
def fields(node):
    return [(part.target.id, ast.unparse(part.annotation),
             ast.unparse(part.value) if part.value else 'обязательное поле')
            for part in node.body if isinstance(part, ast.AnnAssign)
            and isinstance(part.target, ast.Name)]


#: Находит прямые выражения вызовов в собственном теле метода.
#: AST-представление вызова сохраняется независимо от форматирования исходника.
def calls(node):
    return sorted({ast.unparse(part.func) for part in scope_nodes(node)
                   if isinstance(part, ast.Call)})


#: Выделяет известные таблицы чтения и изменения в SQL-литералах метода.
#: Фильтрует ключевые слова ON CONFLICT DO UPDATE SET по реестру таблиц.
def effects(node, tables):
    writes, reads = set(), set()
    for part in scope_nodes(node):
        if not isinstance(part, ast.Constant) or not isinstance(part.value, str):
            continue
        writes.update(re.findall(
            r'\b(?:INSERT(?: OR \w+)? INTO|UPDATE|DELETE FROM|ALTER TABLE|CREATE TABLE IF NOT EXISTS)\s+([a-z_][a-z_0-9]*)',
            part.value, re.IGNORECASE,
        ))
        reads.update(re.findall(r'\b(?:FROM|JOIN)\s+([a-z_][a-z_0-9]*)', part.value, re.IGNORECASE))
    return sorted(value for value in writes if value.lower() in tables), sorted(value for value in reads if value.lower() in tables)


#: Собирает абсолютные имена импортируемых модулей проекта.
#: Относительные импорты разрешаются от пакета исходного файла.
def project_imports(path, text, module_paths):
    result = set()
    package = path.removesuffix('.py').replace('/', '.').split('.')[:-1]
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ImportFrom):
            prefix = package[:len(package) - node.level + 1] if node.level else []
            name = '.'.join([*prefix, node.module or '']).strip('.')
            if name in module_paths:
                result.add(module_paths[name])
            for alias in node.names:
                child = (name + '.' + alias.name).strip('.')
                if child in module_paths:
                    result.add(module_paths[child])
        elif isinstance(node, ast.Import):
            result.update(module_paths[alias.name] for alias in node.names if alias.name in module_paths)
    return sorted(result)


#: Разрешает локальное выражение вызова в запись по лексической области.
#: Для повторных объявлений учитывает последнее найденное определение этого имени.
def call_target(owner, expression, symbols):
    candidates = []
    if expression.startswith('self.'):
        parents = owner.name.split('.')[:-1]
        while parents:
            candidates.append('.'.join(parents) + '.' + expression[5:])
            parents.pop()
    elif '.' not in expression:
        parents = owner.name.split('.')[:-1]
        while parents:
            candidates.append('.'.join([*parents, expression]))
            parents.pop()
        candidates.append(expression)
    for name in candidates:
        found = [symbol for symbol in symbols if symbol.name == name]
        if found:
            return max(found, key=lambda symbol: symbol.node.lineno)
    return None


#: Описывает класс с наследованием, полями, состоянием и методами.
#: Сохраняет подробности прежнего справочника через структурный разбор AST.
def render_class(node):
    output = ['Базовые классы: ' + literal(', '.join(ast.unparse(base) for base in node.bases) or 'object') + '.', '']
    class_fields = fields(node)
    if class_fields:
        output += ['| Поле | Аннотация | Значение / ограничение |', '| --- | --- | --- |']
        output += [f'| {literal(name)} | {literal(annotation)} | {literal(default)} |'
                   for name, annotation, default in class_fields]
    init = next((part for part in node.body if isinstance(part, ast.FunctionDef) and part.name == '__init__'), None)
    if init:
        output += ['', 'Состояние, присваиваемое конструктором: ' + ', '.join(literal(name) for name in own_assignments(init)) + '.']
    methods = [literal(part.name) for part in node.body if isinstance(part, (ast.FunctionDef, ast.AsyncFunctionDef))]
    output += ['', 'Именованные методы: ' + (', '.join(methods) or 'собственных методов нет') + '.']
    return output


#: Описывает точную сигнатуру, вызовы, изменения состояния и ветви функции.
#: Ссылки на соседние определения используют устойчивые лексические имена.
def render_function(symbol, symbols, tables, document):
    node = symbol.node
    signature = ('async def ' if isinstance(node, ast.AsyncFunctionDef) else 'def ') + node.name + '(' + ast.unparse(node.args) + ')'
    if node.returns:
        signature += ' -> ' + ast.unparse(node.returns)
    output = ['```python', signature, '```', '']
    if node.decorator_list:
        output += ['Декораторы: ' + ', '.join(literal(ast.unparse(item)) for item in node.decorator_list) + '.', '']
    writes, reads = effects(node, tables)
    if reads or writes:
        output += ['SQLite: чтение ' + (', '.join(literal(name) for name in reads) or 'не найдено')
                   + '; запись/DDL ' + (', '.join(literal(name) for name in writes) or 'не найдена')
                   + '. См. [схему данных](../data-model.md).', '']
    assigned = own_assignments(node)
    if assigned:
        output += ['Присваивания полям `self`: ' + ', '.join(literal(name) for name in assigned) + '.', '']
    invoked = []
    for expression in calls(node):
        target = call_target(symbol, expression, symbols)
        invoked.append(symbol_link(document, target, expression) if target else literal(expression))
    if invoked:
        output += ['Прямые выражения вызова: ' + ', '.join(invoked) + '.', '']
    own = scope_nodes(node)
    raised = list(dict.fromkeys(ast.unparse(part.exc) for part in own if isinstance(part, ast.Raise) and part.exc))
    handled = list(dict.fromkeys(ast.unparse(part.type) if part.type else 'BaseException (bare except)'
                                for part in own if isinstance(part, ast.ExceptHandler)))
    if raised:
        output += ['Явные `raise`:', ''] + ['- ' + literal(value) for value in raised] + ['']
    if handled:
        output += ['Перехватываемые типы: ' + ', '.join(literal(value) for value in handled) + '.', '']
    returned = list(dict.fromkeys(ast.unparse(part.value) if part.value else 'None'
                                 for part in own if isinstance(part, ast.Return)))
    if returned:
        output += ['Выражения возврата (ветви, без исполнения):', ''] + ['- ' + literal(value) for value in returned] + ['']
    elif any(isinstance(part, (ast.Yield, ast.YieldFrom)) for part in own):
        output += ['Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.', '']
    else:
        output += ['Явного `return` в собственном теле нет: обычное завершение возвращает `None`.', '']
    return output


#: Выбирает константы верхнего уровня с отдельными устойчивыми якорями.
#: Объёмные строковые значения сохраняют навигацию без дублирования CSS и SQL.
def constants(text):
    result = []
    for node in ast.parse(text).body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                value = ast.unparse(node.value)
                result.append((target.id, value if len(value) < 550 else 'Объёмное значение см. в исходном модуле', node))
    return sorted(result)


#: Строит подробную страницу одного Python-модуля.
#: Собирает структуру импортов, константы и каждое определение без координат исходника.
def render_module(path, text, symbols, metadata, imports, test_imports):
    document = 'docs/reference/' + reference_name(path)
    details = metadata['modules'][path]
    output = [f'# {details["title"]}: `{path}`', '', details['description'], '', GENERATED_NOTICE, '',
              link_from(document, path, 'Исходный модуль'),
              ' · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)', '',
              '## Связи модуля', '']
    output += ['Импортирует из проекта: ' + (', '.join(link_from(document, 'docs/reference/' + reference_name(item), item) for item in imports[path]) or 'прямых импортов нет') + '.']
    incoming = sorted(item for item, dependencies in imports.items() if path in dependencies)
    output += ['Импортируется модулями: ' + (', '.join(link_from(document, 'docs/reference/' + reference_name(item), item) for item in incoming) or 'вход может выполняться через CLI или внешнюю конфигурацию') + '.']
    output += ['Тестовые модули с прямым импортом: ' + (', '.join(link_from(document, 'docs/reference/tests.md', item, 'module-' + item.removesuffix('.py').replace('/', '.')) for item in test_imports[path]) or 'прямых импортов нет') + '.', '', '## Оглавление определений', '']
    output += [f'- [{symbol.name}](#{quote(symbol.anchor, safe="._-")}) — {symbol.explanation[0]}' for symbol in symbols]
    entries = constants(text)
    if entries:
        output += ['', '## Константы и значения по умолчанию', '']
        for name, value, node in entries:
            output += [f'<a id="constant-{name}"></a>', '', f'### `{name}`', '', literal(value), '']
    for symbol in symbols:
        output += ['', f'<a id="{symbol.anchor}"></a>', '', f'## `{symbol.name}`', '',
                   link_from(document, path, path) + ' · `' + symbol.name + '`', '',
                   ' '.join(symbol.explanation), '']
        output += render_class(symbol.node) if isinstance(symbol.node, ast.ClassDef) else render_function(symbol, symbols, metadata['tables'], document)
    return '\n'.join(output).strip() + '\n'


#: Читает описания модулей и проверяет соответствие реестра исходному дереву.
#: Пропавший или новый модуль требует явного обновления смысловых метаданных.
def load_metadata(root):
    metadata = json.loads((root / METADATA_PATH).read_text())
    discovered = {str(path.relative_to(root)) for pattern in PYTHON_GLOBS for path in root.glob(pattern)}
    registered = set(metadata['modules'])
    if discovered != registered:
        raise DocumentationError(f'Реестр модулей расходится с исходниками: новые={sorted(discovered - registered)}, пропавшие={sorted(registered - discovered)}')
    return metadata


#: Формирует справочник всех существующих тестовых определений.
#: Якоря включают модуль, класс, вложенное имя и номер повторного объявления.
def render_tests(root, metadata):
    output = ['# Справочник тестовых сценариев', '', GENERATED_NOTICE, '',
              'Имена отражают проверяемые утверждения; точные fixture и assert приведены в исходном модуле.', '']
    for path in sorted(root.glob('tests/test_*.py')):
        relative = str(path.relative_to(root))
        module = relative.removesuffix('.py').replace('/', '.')
        output += [f'<a id="module-{module}"></a>', '', f'## `{path.name}`', '', metadata.get('tests', {}).get(relative, 'Проверки модуля проекта') + '.', '', link_from('docs/reference/tests.md', relative, relative), '']
        counts = Counter()
        for name, node in sorted(definitions(path.read_text()), key=lambda item: item[0]):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith('test_'):
                continue
            counts[name] += 1
            anchor = symbol_anchor(module + '.' + name, counts[name])
            output += [f'<a id="{anchor}"></a>', '', f'### `{name}`', '',
                       '```python', ('async def ' if isinstance(node, ast.AsyncFunctionDef) else 'def ') + node.name + '(' + ast.unparse(node.args) + ')', '```', '']
    return '\n'.join(output).strip() + '\n'


#: Выполняет изолированный снимок OpenAPI и пустых SQLite-схем текущего Core.
#: Каталог данных временный, PhotoKit отключён, lifespan и сервер не запускаются.
def snapshot_runtime(root):
    with tempfile.TemporaryDirectory(prefix='media-actu-docs-') as directory:
        output = Path(directory) / 'schema.json'
        environment = dict(os.environ, MEDIA_ACTU_DATA_DIR=directory, PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--snapshot', str(root), str(output)],
                                cwd=directory, env=environment, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise DocumentationError('Не удалось снять схему в изоляции: ' + result.stderr.strip())
        return json.loads(output.read_text())


#: Собирает схемы в дочернем процессе с временным каталогом данных.
#: Подмена supported запрещает обращение к реальному Photos при инициализации Core.
def write_runtime_snapshot(root, output):
    from unittest.mock import patch
    sys.path.insert(0, str(root))
    from media_manager.photos_adapter import SystemPhotosAdapter
    with patch.object(SystemPhotosAdapter, 'supported', property(lambda self: False)):
        import app
    databases = {}
    for filename in ('catalog.sqlite3', 'storage.sqlite3'):
        with sqlite3.connect(Path(os.environ['MEDIA_ACTU_DATA_DIR']) / filename) as database:
            database.row_factory = sqlite3.Row
            tables = []
            for row in database.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
                tables.append(dict(row,
                    columns=[dict(value) for value in database.execute('PRAGMA table_info(' + row['name'] + ')')],
                    foreign_keys=[dict(value) for value in database.execute('PRAGMA foreign_key_list(' + row['name'] + ')')],
                    indexes=sorted([dict(value) for value in database.execute('PRAGMA index_list(' + row['name'] + ')')], key=lambda value: value['name'])))
            databases[filename] = tables
    api = app.app.openapi()
    for operations in api['paths'].values():
        for operation in operations.values():
            if isinstance(operation, dict):
                operation.pop('operationId', None)
    output.write_text(json.dumps({'databases': databases, 'api': api}, ensure_ascii=False, sort_keys=True))


#: Находит владельца строки или объявления внутри AST для миграции старых ссылок.
#: Выбирает самое глубокое содержащее определение, используя позиции только в памяти.
def symbol_at_line(symbols, line):
    candidates = [symbol for symbol in symbols if symbol.node is not None
                  and min([symbol.node.lineno, *[item.lineno for item in symbol.node.decorator_list]]) <= line <= symbol.node.end_lineno]
    return min(candidates, key=lambda symbol: symbol.node.end_lineno - symbol.node.lineno) if candidates else None


#: Находит устойчивый источник определения SQL-таблицы в исходном коде.
#: Ссылается на содержащий конструктор либо именованную константу схемы.
def table_origins(table, texts, inventory, document):
    result = []
    pattern = re.compile(r'CREATE TABLE IF NOT EXISTS\s+' + re.escape(table) + r'\b')
    for path, text in texts.items():
        for node in ast.walk(ast.parse(text)):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str) or not pattern.search(node.value):
                continue
            owner = symbol_at_line(inventory[path], node.lineno)
            if owner:
                result.append(symbol_link(document, owner, path + ' / ' + owner.name))
            else:
                constant = next((name for name, value, entry in constants(text) if entry.lineno <= node.lineno <= entry.end_lineno), None)
                target = 'docs/reference/' + reference_name(path)
                result.append(link_from(document, target, path + ' / ' + (constant or 'модуль'), 'constant-' + constant if constant else ''))
    return sorted(set(result))


#: Строит полную схему SQLite с описаниями и устойчивыми источниками таблиц.
#: Данные берутся из новых временных баз после действующих миграций.
def render_schema(snapshot, metadata, texts, inventory):
    output = ['# Схема данных', '', GENERATED_NOTICE, '',
              'Схема получена на пустых временных базах после инициализации служб Core. PhotoKit отключён, lifespan не запускается.', '',
              'Базы независимы. volume_id в копиях Photos проверяется прикладным кодом. Состояние потоков и очередей в памяти описано в [архитектуре](architecture.md).', '',
              '## Владение и транзакции', '',
              '`Catalog.connect` включает внешние ключи, WAL, sqlite3.Row и тайм-аут 30 секунд. `StorageCatalog.connect` фиксирует или откатывает блок и закрывает соединение. WAL для storage этим методом явно не включается. Блокировки процесса и BEGIN IMMEDIATE согласуют изменения в пределах соответствующей базы.', '',
              '## Оглавление таблиц', '']
    for filename, tables in sorted(snapshot['databases'].items()):
        output += [f'### `{filename}`', '']
        output += [f'- [{table["name"]}](#table-{table["name"].replace("_", "-")})' for table in tables] + ['']
    for filename, tables in sorted(snapshot['databases'].items()):
        for table in tables:
            name = table['name']
            if name not in metadata['tables']:
                raise DocumentationError(f'Для новой таблицы {name} требуется смысловое описание')
            output += [f'<a id="table-{name.replace("_", "-")}"></a>', '', f'## `{name}`', '',
                       f'База: `{filename}`. Определение: ' + ', '.join(table_origins(name, texts, inventory, 'docs/data-model.md')) + '.', '',
                       metadata['tables'][name], '', '| Поле | Тип SQLite | NOT NULL | По умолчанию | Позиция PK |', '| --- | --- | --- | --- | --- |']
            output += [f'| `{column["name"]}` | `{column["type"]}` | {bool(column["notnull"])} | {literal(column["dflt_value"]) if column["dflt_value"] is not None else "не задано"} | {column["pk"]} |' for column in table['columns']]
            output += ['', 'Полное DDL с CHECK, UNIQUE и добавленными полями:', '', '```sql', table['sql'] + ';', '```', '']
            if table['foreign_keys']:
                output += ['Внешние ключи:', ''] + [f'- `{key["from"]}` → `{key["table"]}.{key["to"]}`, ON DELETE `{key["on_delete"]}`, ON UPDATE `{key["on_update"]}`.' for key in table['foreign_keys']] + ['']
            output += ['Индексы: ' + (', '.join(f'`{index["name"]}` (unique={bool(index["unique"])}, partial={bool(index["partial"])})' for index in table['indexes']) or 'нет') + '.', '']
    return '\n'.join(output).strip() + '\n'


#: Связывает HTTP-маршруты с их именованными обработчиками текущего Core.
#: Извлекает метод и путь из декораторов FastAPI без координат исходника.
def route_symbols(inventory):
    result = {}
    for symbol in inventory.get('app.py', []):
        if isinstance(symbol.node, ast.ClassDef):
            continue
        for decorator in symbol.node.decorator_list:
            if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                    and isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == 'app'
                    and decorator.args and isinstance(decorator.args[0], ast.Constant)):
                result[decorator.func.attr, decorator.args[0].value] = symbol
    return result


#: Строит полный HTTP-справочник из актуального OpenAPI и комментариев обработчиков.
#: Сортировка маршрутов и JSON исключает случайный порядок и изменчивые operationId.
def render_api(snapshot, inventory):
    api = snapshot['api']
    routes = route_symbols(inventory)
    entries = [(method, path, operation) for path, operations in sorted(api['paths'].items())
               for method, operation in sorted(operations.items()) if method in {'get', 'post', 'patch', 'put', 'delete'}]
    output = ['# HTTP API Core', '', GENERATED_NOTICE, '',
              'OpenAPI получен из текущих контрактов FastAPI на временных данных. Core по умолчанию доступен на http://127.0.0.1:18765, UI на 8090, интерактивная схема на /docs.', '',
              'Обработчики могут переводить доменные ошибки в HTTPException дополнительно к ответам OpenAPI. Точные raise и перехваты приведены в [справочнике app.py](reference/app.md). GET может пополнять кэш, снимки или приоритеты превью. План и старт копирования — отдельные действия.', '',
              '`422` означает отказ валидации Pydantic/Query. Обработчики используют `400` для недопустимых параметров или состояния и `404` для отсутствующей записи либо ресурса. Photos дополнительно использует `403`, `409` и `503` по контракту конкретного маршрута.', '',
              '## Все маршруты', '', '| Метод | Путь | Назначение и обработчик |', '| --- | --- | --- |']
    for method, path, operation in entries:
        symbol = routes[method, path]
        output.append(f'| `{method.upper()}` | `{path}` | {symbol_link("docs/api.md", symbol)} — {symbol.explanation[0]} |')
    output += ['', '## Параметры и ответы по маршрутам', '']
    for method, path, operation in entries:
        symbol = routes[method, path]
        output += [f'### `{method.upper()} {path}`', '', symbol_link('docs/api.md', symbol) + '. ' + symbol.explanation[0], '']
        if operation.get('parameters'):
            output += ['| Параметр | Где | Обязательный | Тип, пределы и значение по умолчанию |', '| --- | --- | --- | --- |']
            output += [f'| `{parameter["name"]}` | `{parameter["in"]}` | {parameter.get("required", False)} | {literal(json.dumps(parameter.get("schema", {}), ensure_ascii=False, sort_keys=True))} |' for parameter in operation['parameters']] + ['']
        body = operation.get('requestBody')
        if body:
            output += ['Тело JSON: ' + literal(json.dumps(body['content']['application/json']['schema'], ensure_ascii=False, sort_keys=True)) + f'; обязательное: {body.get("required", False)}.', '']
        output += ['Декларированные ответы: ' + ', '.join(f'`{code}` {response["description"]}' for code, response in sorted(operation['responses'].items())) + '.', '']
    output += ['## Схемы Pydantic и валидации', '',
               'required задаёт обязательность поля, null в anyOf допускает None, additionalProperties=false запрещает лишние поля. Унаследованные поля раскрыты в схеме.', '']
    for name, schema in sorted(api['components']['schemas'].items()):
        output += [f'### `{name}`', '', '```json', json.dumps(schema, ensure_ascii=False, sort_keys=True, indent=2), '```', '']
    return '\n'.join(output).strip() + '\n'


#: Возвращает лексемы нативного исходника с координатами только для разбора.
#: Пробелы и обычные комментарии исключаются, строковые литералы сохраняются целиком.
def native_tokens(text):
    return [match for match in TOKEN_PATTERN.finditer(text)
            if not match.group().isspace() and not match.group().startswith(('//', '/*'))]


#: Заменяет нативные комментарии пробелами для поиска многострочных объявлений.
#: Сохраняет длину текста и переводы строк, чтобы внутренние позиции совпадали.
def comment_mask(text):
    return TOKEN_PATTERN.sub(
        lambda match: re.sub(r'[^\n]', ' ', match.group())
        if match.group().startswith(('//', '/*')) else match.group(), text)


#: Ищет закрывающую скобку для сбалансированного списка лексем.
#: Строки и комментарии уже выделены лексером и не меняют глубину скобок.
def closing_token(tokens, start, opening='(', closing=')'):
    depth = 0
    for index in range(start, len(tokens)):
        value = tokens[index].group()
        depth += value == opening
        depth -= value == closing
        if depth == 0:
            return index
    raise DocumentationError('Несбалансированные скобки в нативном исходнике')


#: Создаёт описание нативного определения с проверкой двух строк пояснения.
#: Якорь включает исходный файл и полное имя, позиции остаются внутри процесса.
def native_symbol(path, text, name, signature, start, end, prefix='//:'):
    line = text.count('\n', 0, start) + 1
    try:
        explanation = explanation_at(text, line, prefix)
    except DocumentationError as error:
        raise DocumentationError(f'{path} / {name}: {error}') from error
    qualified = path.replace('/', '.') + '.' + name
    normalized = ' '.join(token.group() for token in native_tokens(signature))
    return Symbol(path, qualified, symbol_anchor(qualified), None, explanation, normalized, start, end)


#: Разбирает C-функции, Objective-C-классы и методы нативного helper.
#: Тела ограничиваются сбалансированными скобками, имя метода включает селекторы.
def objective_c_symbols(path, text):
    result = []
    tokens = native_tokens(text)
    masked = comment_mask(text)
    pattern = re.compile(r'^(?:static\s+[^;{]*?|int)\s+\*?(\w+)\([^;{}]*\)\s*\{', re.MULTILINE)
    for match in pattern.finditer(masked):
        opening = next(index for index, token in enumerate(tokens) if token.start() == match.end() - 1)
        end = tokens[closing_token(tokens, opening, '{', '}')].end()
        result.append(native_symbol(path, text, match.group(1), text[match.start():match.end() - 1], match.start(), end))
    for match in re.finditer(r'^@interface\s+(\w+)[^\n]*', masked, re.MULTILINE):
        end = text.index('@end', match.end()) + len('@end')
        result.append(native_symbol(path, text, match.group(1), match.group(), match.start(), end))
    for match in re.finditer(r'^[-+]\s*\([^)]*\)\s*([^;{]+)\{', masked, re.MULTILINE):
        classes = list(re.finditer(r'@implementation\s+(\w+)', text[:match.start()]))
        if not classes:
            raise DocumentationError(f'Не найдена область Objective-C-метода в {path}')
        selectors = re.findall(r'(\w+)\s*:', match.group(1))
        name = ''.join(value + ':' for value in selectors) or match.group(1).strip()
        opening = next(index for index, token in enumerate(tokens) if token.start() == match.end() - 1)
        end = tokens[closing_token(tokens, opening, '{', '}')].end()
        result.append(native_symbol(path, text, classes[-1].group(1) + '.' + name,
                                    match.group()[:-1], match.start(), end))
    return sorted(result, key=lambda symbol: symbol.anchor)


#: Разбирает именованные методы, watch и computed Vue-компонента.
#: Имена областей объекта различают одноимённые методы и обработчики.
def javascript_symbols(path, text):
    tokens = native_tokens(text)
    result, scopes, openings = [], [], {}
    controls = {'if', 'for', 'while', 'switch', 'catch', 'with'}
    for index, token in enumerate(tokens):
        value = token.group()
        if value == '{':
            label = openings.get(index, '')
            if index > 1 and tokens[index - 1].group() == ':':
                label = tokens[index - 2].group()
            scopes.append(label)
        elif value == '}':
            scopes.pop()
        elif (re.fullmatch(r'[A-Za-z_]\w*', value) and value not in controls
              and index + 1 < len(tokens) and tokens[index + 1].group() == '('
              and (index == 0 or tokens[index - 1].group() in {'{', ','})):
            closing = closing_token(tokens, index + 1)
            if closing + 1 >= len(tokens) or tokens[closing + 1].group() != '{':
                continue
            end = tokens[closing_token(tokens, closing + 1, '{', '}')].end()
            name = '.'.join([scope for scope in scopes if scope] + [value])
            result.append(native_symbol(path, text, name, text[token.start():tokens[closing].end()], token.start(), end))
            openings[closing + 1] = value
    return sorted(result, key=lambda symbol: symbol.anchor)


#: Собирает именованные определения шести существующих нативных исходников.
#: Скрипты JXA и AppleScript представлены собственными точками входа.
def all_native_symbols(root, paths):
    result = []
    for path in sorted(paths):
        text = (root / path).read_text()
        if path.endswith('.m'):
            result.extend(objective_c_symbols(path, text))
        elif path == 'paired_tree.js':
            result.extend(javascript_symbols(path, text))
        else:
            prefix = '--:' if path.endswith('.applescript') else '//:'
            name = 'run' if path.endswith('.applescript') else 'module'
            lines = text.splitlines()
            first = next(index for index, line in enumerate(lines) if line.strip() and not line.strip().startswith(('--', '//')))
            start = sum(len(line) + 1 for line in lines[:first])
            result.append(native_symbol(path, text, name, lines[first], start, len(text), prefix))
    anchors = [symbol.anchor for symbol in result]
    if len(anchors) != len(set(anchors)):
        raise DocumentationError('Повторный якорь нативного определения')
    return sorted(result, key=lambda symbol: symbol.anchor)


#: Строит нативный справочник с сигнатурами, пояснениями и точками входа.
#: Исходные файлы связаны по имени, а каждый метод имеет отдельный устойчивый якорь.
def render_native(symbols):
    output = ['# Нативные определения', '', GENERATED_NOTICE, '',
              'Разбор языков, владения ресурсами, протокола и UI приведён в [подробном руководстве](../development/native.md).', '',
              '## Оглавление', '']
    output += [f'- [{symbol.name}](#{quote(symbol.anchor, safe="._-")}) — {symbol.explanation[0]}' for symbol in symbols]
    for symbol in symbols:
        output += ['', f'<a id="{symbol.anchor}"></a>', '', f'## `{symbol.name}`', '',
                   link_from('docs/reference/native.md', symbol.path, symbol.path), '',
                   ' '.join(symbol.explanation), '', '```text', symbol.signature, '```', '']
    return '\n'.join(output).strip() + '\n'


#: Собирает все смысловые документы из текущих исходников и метаданных.
#: Возвращает ожидаемое содержимое без записи, позволяя проверить нулевой diff.
def build_documents(root, runtime_snapshot=None):
    metadata = load_metadata(root)
    texts = {path: (root / path).read_text() for path in sorted(metadata['modules'])}
    inventory = {path: python_symbols(path, text) for path, text in texts.items()}
    module_paths = {path.removesuffix('.py').replace('/', '.'): path for path in texts}
    imports = {path: project_imports(path, text, module_paths) for path, text in texts.items()}
    test_imports = {path: [] for path in texts}
    for path in sorted(root.glob('tests/test_*.py')):
        relative = str(path.relative_to(root))
        for imported in project_imports(relative, path.read_text(), module_paths):
            test_imports[imported].append(relative)
    documents = {'docs/reference/' + reference_name(path): render_module(path, text, inventory[path], metadata, imports, test_imports)
                 for path, text in texts.items()}
    index = ['# Справочник реализации', '', GENERATED_NOTICE, '',
             'Определения связаны по полному лексическому имени. Повторное объявление одного имени имеет суффикс declaration. Физические координаты исходника исключены из версионируемых записей.', '',
             'Каждая запись содержит сигнатуру, два пояснения, поля, вызовы, SQL, явные исключения и выражения возврата. Статический список вызовов отражает собственное тело определения.', '',
             '| Модуль | Назначение | Классы / функции |', '| --- | --- | --- |']
    for path, symbols in inventory.items():
        classes = sum(isinstance(symbol.node, ast.ClassDef) for symbol in symbols)
        index.append(f'| [{path}]({reference_name(path)}) | {metadata["modules"][path]["title"]} | {classes} / {len(symbols) - classes} |')
    index += ['', '- [Нативные определения](native.md)', '- [Тестовые сценарии](tests.md)',
              '- [Как обновлять и проверять справочники](../development/documentation.md)',
              '- [HTTP API](../api.md)', '- [Схема данных](../data-model.md)']
    documents['docs/reference/README.md'] = '\n'.join(index).strip() + '\n'
    documents['docs/reference/tests.md'] = render_tests(root, metadata)
    documents['docs/reference/native.md'] = render_native(all_native_symbols(root, metadata.get('native', [])))
    if 'app.py' in inventory:
        snapshot = runtime_snapshot if runtime_snapshot is not None else snapshot_runtime(root)
        documents['docs/api.md'] = render_api(snapshot, inventory)
        documents['docs/data-model.md'] = render_schema(snapshot, metadata, texts, inventory)
    return documents


#: Извлекает локальные Markdown-ссылки за пределами примеров кода.
#: Сохраняет подписи с inline-code и поддерживает скобки внутри URL.
def markdown_links(text):
    cleaned = re.sub(r'^```.*?^```\s*$', '', text, flags=re.MULTILINE | re.DOTALL)
    cleaned = re.sub(r'`[^`\n]*`', '', cleaned)
    pattern = r'\[[^\]]*\]\(([^\s()]+(?:\([^()]*\)[^\s()]*)*)\)'
    return re.findall(pattern, cleaned)


#: Вычисляет явные и GitHub-совместимые якоря Markdown-документа.
#: Счётчик повторных заголовков обнаруживает ошибочные и неоднозначные ссылки.
def markdown_anchors(text):
    result = set(re.findall(r'<a\s+id="([^"]+)"', text))
    counts = Counter()
    cleaned = re.sub(r'^```.*?^```\s*$', '', text, flags=re.MULTILINE | re.DOTALL)
    for heading in re.findall(r'^#+\s+(.+)', cleaned, flags=re.MULTILINE):
        slug = re.sub(r'[^\w\- ]', '', heading.lower().replace('`', '')).replace(' ', '-')
        suffix = f'-{counts[slug]}' if counts[slug] else ''
        counts[slug] += 1
        result.add(slug + suffix)
    return result


#: Проверяет локальные пути, устойчивые якоря и запрет построчных ссылок.
#: Учитывает ещё не записанные результаты генерации через виртуальный набор документов.
def validate_links(root, documents):
    texts = {str(path.relative_to(root)): path.read_text() for path in root.glob('docs/**/*.md')}
    if (root / 'README.md').exists():
        texts['README.md'] = (root / 'README.md').read_text()
    texts.update(documents)
    errors = []
    for path, text in sorted(texts.items()):
        for target in markdown_links(text):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                continue
            destination = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(parts.path))) if parts.path else path
            if re.fullmatch(r'L\d+(?:-L?\d+)?', parts.fragment):
                errors.append(f'{path}: нестабильная ссылка {target}')
                continue
            if destination not in texts and not (root / destination).is_file():
                errors.append(f'{path}: отсутствует файл {target}')
                continue
            if parts.fragment:
                if destination not in texts:
                    errors.append(f'{path}: для исходника требуется ссылка на именованное определение {target}')
                elif unquote(parts.fragment) not in markdown_anchors(texts[destination]):
                    errors.append(f'{path}: отсутствует якорь {target}')
    if errors:
        raise DocumentationError('\n'.join(errors))


#: Сравнивает построенные справочники с диском и обновляет только изменившиеся файлы.
#: Режим check выдаёт diff и ошибку при устаревшем описании или лишней странице реестра.
def synchronize(root, documents, check=False):
    existing = {str(path.relative_to(root)) for path in (root / 'docs/reference').glob('*.md')}
    expected = {path for path in documents if path.startswith('docs/reference/')}
    extras = existing - expected
    if extras:
        raise DocumentationError('Страницы без соответствующего модуля: ' + ', '.join(sorted(extras)))
    changed = []
    for path, text in sorted(documents.items()):
        target = root / path
        current = target.read_text() if target.exists() else ''
        if current == text:
            continue
        changed.append(path)
        if check:
            diff = ''.join(difflib.unified_diff(current.splitlines(keepends=True), text.splitlines(keepends=True), fromfile=path, tofile=path + ' (ожидается)'))
            print(diff, end='')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
    if check and changed:
        raise DocumentationError('Устаревшие справочники: ' + ', '.join(changed))
    return changed


#: Запускает генерацию или сравнение актуальности с последующей проверкой ссылок.
#: Внутренний snapshot исполняется только в изолированном дочернем процессе.
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='сравнить построенные документы без записи')
    parser.add_argument('--root', type=Path, default=ROOT, help='корень проекта или изолированного примера')
    parser.add_argument('--snapshot', nargs=2, metavar=('ROOT', 'OUTPUT'), help=argparse.SUPPRESS)
    arguments = parser.parse_args(argv)
    if arguments.snapshot:
        write_runtime_snapshot(Path(arguments.snapshot[0]), Path(arguments.snapshot[1]))
        return 0
    root = arguments.root.resolve()
    try:
        documents = build_documents(root)
        validate_links(root, documents)
        changed = synchronize(root, documents, arguments.check)
    except (DocumentationError, SyntaxError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f'Справочники актуальны. Изменено файлов: {len(changed)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
