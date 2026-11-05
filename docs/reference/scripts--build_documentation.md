# Генератор смысловых справочников: `scripts/build_documentation.py`

Строит подробные справочники по AST и помеченным пояснениям, формирует устойчивые якоря и проверяет актуальность, покрытие и локальные ссылки.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../scripts/build_documentation.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [app.py](app.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md).
Импортируется модулями: вход может выполняться через CLI или внешнюю конфигурацию.
Тестовые модули с прямым импортом: [tests/test_documentation.py](tests.md#module-tests.test_documentation).

## Оглавление определений

- [Definitions](#symbol-Definitions) — Собирает полные лексические имена классов, функций и вложенных обработчиков.
- [Definitions.__init__](#symbol-Definitions.__init__) — Создаёт стек лексических областей и список найденных объявлений.
- [Definitions.definition](#symbol-Definitions.definition) — Добавляет объявление с именами всех содержащих классов и функций.
- [DocumentationError](#symbol-DocumentationError) — Сообщает о нарушенной структуре справочника, комментариев или ссылок.
- [Symbol](#symbol-Symbol) — Хранит устойчивую идентичность определения и его пояснения.
- [all_native_symbols](#symbol-all_native_symbols) — Собирает именованные определения шести существующих нативных исходников.
- [build_documents](#symbol-build_documents) — Собирает все смысловые документы из текущих исходников и метаданных.
- [call_target](#symbol-call_target) — Разрешает локальное выражение вызова в запись по лексической области.
- [calls](#symbol-calls) — Находит прямые выражения вызовов в собственном теле метода.
- [closing_token](#symbol-closing_token) — Ищет закрывающую скобку для сбалансированного списка лексем.
- [comment_mask](#symbol-comment_mask) — Заменяет нативные комментарии пробелами для поиска многострочных объявлений.
- [constants](#symbol-constants) — Выбирает константы верхнего уровня с отдельными устойчивыми якорями.
- [definitions](#symbol-definitions) — Возвращает объявления Python с полными лексическими именами.
- [effects](#symbol-effects) — Выделяет известные таблицы чтения и изменения в SQL-литералах метода.
- [explanation_at](#symbol-explanation_at) — Получает ровно две помеченные строки пояснения перед объявлением.
- [fields](#symbol-fields) — Выбирает аннотированные поля класса с точными выражениями значений.
- [javascript_symbols](#symbol-javascript_symbols) — Разбирает именованные методы, watch и computed Vue-компонента.
- [link_from](#symbol-link_from) — Формирует относительную Markdown-ссылку с необязательным устойчивым якорем.
- [literal](#symbol-literal) — Экранирует короткое выражение для Markdown и таблиц.
- [load_metadata](#symbol-load_metadata) — Читает описания модулей и проверяет соответствие реестра исходному дереву.
- [main](#symbol-main) — Запускает генерацию или сравнение актуальности с последующей проверкой ссылок.
- [markdown_anchors](#symbol-markdown_anchors) — Вычисляет явные и GitHub-совместимые якоря Markdown-документа.
- [markdown_links](#symbol-markdown_links) — Извлекает локальные Markdown-ссылки за пределами примеров кода.
- [native_symbol](#symbol-native_symbol) — Создаёт описание нативного определения с проверкой двух строк пояснения.
- [native_tokens](#symbol-native_tokens) — Возвращает лексемы нативного исходника с координатами только для разбора.
- [objective_c_symbols](#symbol-objective_c_symbols) — Разбирает C-функции, Objective-C-классы и методы нативного helper.
- [own_assignments](#symbol-own_assignments) — Извлекает присваиваемые поля self из собственного тела определения.
- [project_imports](#symbol-project_imports) — Собирает абсолютные имена импортируемых модулей проекта.
- [python_symbols](#symbol-python_symbols) — Разбирает Python-модуль и проверяет покрытие пояснениями каждого определения.
- [reference_name](#symbol-reference_name) — Преобразует путь Python-модуля в имя страницы справочника.
- [render_api](#symbol-render_api) — Строит полный HTTP-справочник из актуального OpenAPI и комментариев обработчиков.
- [render_class](#symbol-render_class) — Описывает класс с наследованием, полями, состоянием и методами.
- [render_function](#symbol-render_function) — Описывает точную сигнатуру, вызовы, изменения состояния и ветви функции.
- [render_module](#symbol-render_module) — Строит подробную страницу одного Python-модуля.
- [render_native](#symbol-render_native) — Строит нативный справочник с сигнатурами, пояснениями и точками входа.
- [render_schema](#symbol-render_schema) — Строит полную схему SQLite с описаниями и устойчивыми источниками таблиц.
- [render_tests](#symbol-render_tests) — Формирует справочник всех существующих тестовых определений.
- [route_symbols](#symbol-route_symbols) — Связывает HTTP-маршруты с их именованными обработчиками текущего Core.
- [scope_nodes](#symbol-scope_nodes) — Выбирает узлы собственного тела определения для подробного справочника.
- [snapshot_runtime](#symbol-snapshot_runtime) — Выполняет изолированный снимок OpenAPI и пустых SQLite-схем текущего Core.
- [symbol_anchor](#symbol-symbol_anchor) — Строит непотерянный якорь по полному имени и номеру повторного объявления.
- [symbol_at_line](#symbol-symbol_at_line) — Находит владельца строки или объявления внутри AST для миграции старых ссылок.
- [symbol_link](#symbol-symbol_link) — Возвращает ссылку на полное определение в Python- или нативном справочнике.
- [synchronize](#symbol-synchronize) — Сравнивает построенные справочники с диском и обновляет только изменившиеся файлы.
- [table_origins](#symbol-table_origins) — Находит устойчивый источник определения SQL-таблицы в исходном коде.
- [validate_links](#symbol-validate_links) — Проверяет локальные пути, устойчивые якоря и запрет построчных ссылок.
- [write_runtime_snapshot](#symbol-write_runtime_snapshot) — Собирает схемы в дочернем процессе с временным каталогом данных.

## Константы и значения по умолчанию

<a id="constant-DEFINITION_TYPES"></a>

### `DEFINITION_TYPES`

`(ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)`

<a id="constant-GENERATED_NOTICE"></a>

### `GENERATED_NOTICE`

`'Собирается командой &#96;.venv/bin/python scripts/build_documentation.py&#96;. Проверка актуальности — та же команда с &#96;--check&#96;.'`

<a id="constant-METADATA_PATH"></a>

### `METADATA_PATH`

`Path('scripts/documentation_metadata.json')`

<a id="constant-PYTHON_GLOBS"></a>

### `PYTHON_GLOBS`

`('*.py', 'media_manager/*.py', 'scripts/*.py')`

<a id="constant-ROOT"></a>

### `ROOT`

`Path(__file__).resolve().parents[1]`

<a id="constant-TOKEN_PATTERN"></a>

### `TOKEN_PATTERN`

`re.compile('"(?:\\\\.&#124;[^"\\\\])*"&#124;\\\'(?:\\\\.&#124;[^\\\'\\\\])*\\\'&#124;&#96;(?:\\\\.&#124;[^&#96;\\\\])*&#96;&#124;//[^\\n]*&#124;/\\*[\\s\\S]*?\\*/&#124;\\s+&#124;[A-Za-z_][\\w]*&#124;[^\\s]', re.DOTALL)`


<a id="symbol-Definitions"></a>

## `Definitions`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `Definitions`

Собирает полные лексические имена классов, функций и вложенных обработчиков. Счётчик одноимённых объявлений различает повторные определения в одной области.

Базовые классы: `ast.NodeVisitor`.


Состояние, присваиваемое конструктором: `nodes`, `stack`.

Именованные методы: `__init__`, `definition`.

<a id="symbol-Definitions.__init__"></a>

## `Definitions.__init__`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `Definitions.__init__`

Создаёт стек лексических областей и список найденных объявлений. Для обхода одного AST используется отдельный экземпляр посетителя.

```python
def __init__(self)
```

Присваивания полям `self`: `nodes`, `stack`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-Definitions.definition"></a>

## `Definitions.definition`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `Definitions.definition`

Добавляет объявление с именами всех содержащих классов и функций. Обходит вложенные определения с восстановлением стека при выходе.

```python
def definition(self, node)
```

Прямые выражения вызова: `'.'.join`, `self.generic_visit`, `self.nodes.append`, `self.stack.append`, `self.stack.pop`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-DocumentationError"></a>

## `DocumentationError`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `DocumentationError`

Сообщает о нарушенной структуре справочника, комментариев или ссылок. Используется CLI и тестами для явного отказа проверки актуальности.

Базовые классы: `Exception`.


Именованные методы: собственных методов нет.

<a id="symbol-Symbol"></a>

## `Symbol`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `Symbol`

Хранит устойчивую идентичность определения и его пояснения. Позиции узла используются только при чтении исходника и не выводятся в справочник.

Базовые классы: `object`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `обязательное поле` |
| `name` | `str` | `обязательное поле` |
| `anchor` | `str` | `обязательное поле` |
| `node` | `ast.AST &#124; None` | `обязательное поле` |
| `explanation` | `tuple[str, str]` | `обязательное поле` |
| `signature` | `str` | `''` |
| `start` | `int` | `0` |
| `end` | `int` | `0` |

Именованные методы: собственных методов нет.

<a id="symbol-all_native_symbols"></a>

## `all_native_symbols`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `all_native_symbols`

Собирает именованные определения шести существующих нативных исходников. Скрипты JXA и AppleScript представлены собственными точками входа.

```python
def all_native_symbols(root, paths)
```

Прямые выражения вызова: `(root / path).read_text`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `enumerate`, [javascript_symbols](scripts--build_documentation.md#symbol-javascript_symbols), `len`, `line.strip`, `line.strip().startswith`, [native_symbol](scripts--build_documentation.md#symbol-native_symbol), `next`, [objective_c_symbols](scripts--build_documentation.md#symbol-objective_c_symbols), `path.endswith`, `result.append`, `result.extend`, `set`, `sorted`, `sum`, `text.splitlines`.

Явные `raise`:

- `DocumentationError('Повторный якорь нативного определения')`

Выражения возврата (ветви, без исполнения):

- `sorted(result, key=lambda symbol: symbol.anchor)`


<a id="symbol-build_documents"></a>

## `build_documents`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `build_documents`

Собирает все смысловые документы из текущих исходников и метаданных. Возвращает ожидаемое содержимое без записи, позволяя проверить нулевой diff.

```python
def build_documents(root, runtime_snapshot=None)
```

Прямые выражения вызова: `'\n'.join`, `'\n'.join(index).strip`, `(root / path).read_text`, [all_native_symbols](scripts--build_documentation.md#symbol-all_native_symbols), `index.append`, `inventory.items`, `isinstance`, `len`, [load_metadata](scripts--build_documentation.md#symbol-load_metadata), `metadata.get`, `path.read_text`, `path.relative_to`, `path.removesuffix`, `path.removesuffix('.py').replace`, [project_imports](scripts--build_documentation.md#symbol-project_imports), [python_symbols](scripts--build_documentation.md#symbol-python_symbols), [reference_name](scripts--build_documentation.md#symbol-reference_name), [render_api](scripts--build_documentation.md#symbol-render_api), [render_module](scripts--build_documentation.md#symbol-render_module), [render_native](scripts--build_documentation.md#symbol-render_native), [render_schema](scripts--build_documentation.md#symbol-render_schema), [render_tests](scripts--build_documentation.md#symbol-render_tests), `root.glob`, [snapshot_runtime](scripts--build_documentation.md#symbol-snapshot_runtime), `sorted`, `str`, `sum`, `test_imports[imported].append`, `texts.items`.

Выражения возврата (ветви, без исполнения):

- `documents`


<a id="symbol-call_target"></a>

## `call_target`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `call_target`

Разрешает локальное выражение вызова в запись по лексической области. Для повторных объявлений учитывает последнее найденное определение этого имени.

```python
def call_target(owner, expression, symbols)
```

Прямые выражения вызова: `'.'.join`, `candidates.append`, `expression.startswith`, `max`, `owner.name.split`, `parents.pop`.

Выражения возврата (ветви, без исполнения):

- `max(found, key=lambda symbol: symbol.node.lineno)`
- `None`


<a id="symbol-calls"></a>

## `calls`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `calls`

Находит прямые выражения вызовов в собственном теле метода. AST-представление вызова сохраняется независимо от форматирования исходника.

```python
def calls(node)
```

Прямые выражения вызова: `ast.unparse`, `isinstance`, [scope_nodes](scripts--build_documentation.md#symbol-scope_nodes), `sorted`.

Выражения возврата (ветви, без исполнения):

- `sorted({ast.unparse(part.func) for part in scope_nodes(node) if isinstance(part, ast.Call)})`


<a id="symbol-closing_token"></a>

## `closing_token`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `closing_token`

Ищет закрывающую скобку для сбалансированного списка лексем. Строки и комментарии уже выделены лексером и не меняют глубину скобок.

```python
def closing_token(tokens, start, opening='(', closing=')')
```

Прямые выражения вызова: [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `len`, `range`, `tokens[index].group`.

Явные `raise`:

- `DocumentationError('Несбалансированные скобки в нативном исходнике')`

Выражения возврата (ветви, без исполнения):

- `index`


<a id="symbol-comment_mask"></a>

## `comment_mask`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `comment_mask`

Заменяет нативные комментарии пробелами для поиска многострочных объявлений. Сохраняет длину текста и переводы строк, чтобы внутренние позиции совпадали.

```python
def comment_mask(text)
```

Прямые выражения вызова: `TOKEN_PATTERN.sub`.

Выражения возврата (ветви, без исполнения):

- `TOKEN_PATTERN.sub(lambda match: re.sub('[^\\n]', ' ', match.group()) if match.group().startswith(('//', '/*')) else match.group(), text)`


<a id="symbol-constants"></a>

## `constants`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `constants`

Выбирает константы верхнего уровня с отдельными устойчивыми якорями. Объёмные строковые значения сохраняют навигацию без дублирования CSS и SQL.

```python
def constants(text)
```

Прямые выражения вызова: `ast.parse`, `ast.unparse`, `isinstance`, `len`, `result.append`, `sorted`, `target.id.isupper`.

Выражения возврата (ветви, без исполнения):

- `sorted(result)`


<a id="symbol-definitions"></a>

## `definitions`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `definitions`

Возвращает объявления Python с полными лексическими именами. Разбор AST исключает влияние пробелов и обычных комментариев.

```python
def definitions(text)
```

Прямые выражения вызова: [Definitions](scripts--build_documentation.md#symbol-Definitions), `ast.parse`, `visitor.visit`.

Выражения возврата (ветви, без исполнения):

- `visitor.nodes`


<a id="symbol-effects"></a>

## `effects`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `effects`

Выделяет известные таблицы чтения и изменения в SQL-литералах метода. Фильтрует ключевые слова ON CONFLICT DO UPDATE SET по реестру таблиц.

```python
def effects(node, tables)
```

Прямые выражения вызова: `isinstance`, `re.findall`, `reads.update`, [scope_nodes](scripts--build_documentation.md#symbol-scope_nodes), `set`, `sorted`, `value.lower`, `writes.update`.

Выражения возврата (ветви, без исполнения):

- `(sorted((value for value in writes if value.lower() in tables)), sorted((value for value in reads if value.lower() in tables)))`


<a id="symbol-explanation_at"></a>

## `explanation_at`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `explanation_at`

Получает ровно две помеченные строки пояснения перед объявлением. Пропускает пустые строки и обычные комментарии между пояснением и кодом.

```python
def explanation_at(text, line, prefix='#:')
```

Прямые выражения вызова: [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `all`, `collected.append`, `len`, `raw.strip`, `reversed`, `text.splitlines`, `tuple`, `value.startswith`, `value[len(prefix):].strip`.

Явные `raise`:

- `DocumentationError(f'Перед объявлением требуются две строки {prefix} пояснения')`

Выражения возврата (ветви, без исполнения):

- `tuple(reversed(collected))`


<a id="symbol-fields"></a>

## `fields`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `fields`

Выбирает аннотированные поля класса с точными выражениями значений. Типы берутся из AST без исполнения кода и без предположений о неявных типах.

```python
def fields(node)
```

Прямые выражения вызова: `ast.unparse`, `isinstance`.

Выражения возврата (ветви, без исполнения):

- `[(part.target.id, ast.unparse(part.annotation), ast.unparse(part.value) if part.value else 'обязательное поле') for part in node.body if isinstance(part, ast.AnnAssign) and isinstance(part.target, ast.Name)]`


<a id="symbol-javascript_symbols"></a>

## `javascript_symbols`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `javascript_symbols`

Разбирает именованные методы, watch и computed Vue-компонента. Имена областей объекта различают одноимённые методы и обработчики.

```python
def javascript_symbols(path, text)
```

Прямые выражения вызова: `'.'.join`, [closing_token](scripts--build_documentation.md#symbol-closing_token), `enumerate`, `len`, [native_symbol](scripts--build_documentation.md#symbol-native_symbol), [native_tokens](scripts--build_documentation.md#symbol-native_tokens), `openings.get`, `re.fullmatch`, `result.append`, `scopes.append`, `scopes.pop`, `sorted`, `token.group`, `token.start`, `tokens[closing + 1].group`, `tokens[closing].end`, `tokens[closing_token(tokens, closing + 1, '{', '}')].end`, `tokens[index + 1].group`, `tokens[index - 1].group`, `tokens[index - 2].group`.

Выражения возврата (ветви, без исполнения):

- `sorted(result, key=lambda symbol: symbol.anchor)`


<a id="symbol-link_from"></a>

## `link_from`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `link_from`

Формирует относительную Markdown-ссылку с необязательным устойчивым якорем. Вычисление пути зависит от каталогов документов и не использует номера строк.

```python
def link_from(document, target, label, anchor='')
```

Прямые выражения вызова: `posixpath.dirname`, `posixpath.relpath`, `quote`.

Выражения возврата (ветви, без исполнения):

- `f'[{label}]({relative}{fragment})'`


<a id="symbol-literal"></a>

## `literal`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `literal`

Экранирует короткое выражение для Markdown и таблиц. Многострочный исходный текст нормализуется в одну строку представления.

```python
def literal(value)
```

Прямые выражения вызова: `str`, `str(value).replace`, `str(value).replace('&#124;', '&#124;').replace`, `str(value).replace('&#124;', '&#124;').replace('&#96;', '&#96;').replace`.

Выражения возврата (ветви, без исполнения):

- `'&#96;' + str(value).replace('&#124;', '&#124;').replace('&#96;', '&#96;').replace('\n', ' ') + '&#96;'`


<a id="symbol-load_metadata"></a>

## `load_metadata`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `load_metadata`

Читает описания модулей и проверяет соответствие реестра исходному дереву. Пропавший или новый модуль требует явного обновления смысловых метаданных.

```python
def load_metadata(root)
```

Прямые выражения вызова: `(root / METADATA_PATH).read_text`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `json.loads`, `path.relative_to`, `root.glob`, `set`, `sorted`, `str`.

Явные `raise`:

- `DocumentationError(f'Реестр модулей расходится с исходниками: новые={sorted(discovered - registered)}, пропавшие={sorted(registered - discovered)}')`

Выражения возврата (ветви, без исполнения):

- `metadata`


<a id="symbol-main"></a>

## `main`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `main`

Запускает генерацию или сравнение актуальности с последующей проверкой ссылок. Внутренний snapshot исполняется только в изолированном дочернем процессе.

```python
def main(argv=None)
```

Прямые выражения вызова: `Path`, `argparse.ArgumentParser`, `arguments.root.resolve`, [build_documents](scripts--build_documentation.md#symbol-build_documents), `len`, `parser.add_argument`, `parser.parse_args`, `print`, `str`, [synchronize](scripts--build_documentation.md#symbol-synchronize), [validate_links](scripts--build_documentation.md#symbol-validate_links), [write_runtime_snapshot](scripts--build_documentation.md#symbol-write_runtime_snapshot).

Перехватываемые типы: `(DocumentationError, SyntaxError, OSError, ValueError)`.

Выражения возврата (ветви, без исполнения):

- `0`
- `1`


<a id="symbol-markdown_anchors"></a>

## `markdown_anchors`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `markdown_anchors`

Вычисляет явные и GitHub-совместимые якоря Markdown-документа. Счётчик повторных заголовков обнаруживает ошибочные и неоднозначные ссылки.

```python
def markdown_anchors(text)
```

Прямые выражения вызова: `Counter`, `heading.lower`, `heading.lower().replace`, `re.findall`, `re.sub`, `re.sub('[^\\w\\- ]', '', heading.lower().replace('&#96;', '')).replace`, `result.add`, `set`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-markdown_links"></a>

## `markdown_links`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `markdown_links`

Извлекает локальные Markdown-ссылки за пределами примеров кода. Сохраняет подписи с inline-code и поддерживает скобки внутри URL.

```python
def markdown_links(text)
```

Прямые выражения вызова: `re.findall`, `re.sub`.

Выражения возврата (ветви, без исполнения):

- `re.findall(pattern, cleaned)`


<a id="symbol-native_symbol"></a>

## `native_symbol`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `native_symbol`

Создаёт описание нативного определения с проверкой двух строк пояснения. Якорь включает исходный файл и полное имя, позиции остаются внутри процесса.

```python
def native_symbol(path, text, name, signature, start, end, prefix='//:')
```

Прямые выражения вызова: `' '.join`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), [Symbol](scripts--build_documentation.md#symbol-Symbol), [explanation_at](scripts--build_documentation.md#symbol-explanation_at), [native_tokens](scripts--build_documentation.md#symbol-native_tokens), `path.replace`, [symbol_anchor](scripts--build_documentation.md#symbol-symbol_anchor), `text.count`, `token.group`.

Явные `raise`:

- `DocumentationError(f'{path} / {name}: {error}')`

Перехватываемые типы: `DocumentationError`.

Выражения возврата (ветви, без исполнения):

- `Symbol(path, qualified, symbol_anchor(qualified), None, explanation, normalized, start, end)`


<a id="symbol-native_tokens"></a>

## `native_tokens`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `native_tokens`

Возвращает лексемы нативного исходника с координатами только для разбора. Пробелы и обычные комментарии исключаются, строковые литералы сохраняются целиком.

```python
def native_tokens(text)
```

Прямые выражения вызова: `TOKEN_PATTERN.finditer`, `match.group`, `match.group().isspace`, `match.group().startswith`.

Выражения возврата (ветви, без исполнения):

- `[match for match in TOKEN_PATTERN.finditer(text) if not match.group().isspace() and (not match.group().startswith(('//', '/*')))]`


<a id="symbol-objective_c_symbols"></a>

## `objective_c_symbols`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `objective_c_symbols`

Разбирает C-функции, Objective-C-классы и методы нативного helper. Тела ограничиваются сбалансированными скобками, имя метода включает селекторы.

```python
def objective_c_symbols(path, text)
```

Прямые выражения вызова: `''.join`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `classes[-1].group`, [closing_token](scripts--build_documentation.md#symbol-closing_token), [comment_mask](scripts--build_documentation.md#symbol-comment_mask), `enumerate`, `len`, `list`, `match.end`, `match.group`, `match.group(1).strip`, `match.start`, [native_symbol](scripts--build_documentation.md#symbol-native_symbol), [native_tokens](scripts--build_documentation.md#symbol-native_tokens), `next`, `pattern.finditer`, `re.compile`, `re.findall`, `re.finditer`, `result.append`, `sorted`, `text.index`, `token.start`, `tokens[closing_token(tokens, opening, '{', '}')].end`.

Явные `raise`:

- `DocumentationError(f'Не найдена область Objective-C-метода в {path}')`

Выражения возврата (ветви, без исполнения):

- `sorted(result, key=lambda symbol: symbol.anchor)`


<a id="symbol-own_assignments"></a>

## `own_assignments`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `own_assignments`

Извлекает присваиваемые поля self из собственного тела определения. Сортировка полей обеспечивает одинаковое представление независимых присваиваний.

```python
def own_assignments(node)
```

Прямые выражения вызова: `isinstance`, [scope_nodes](scripts--build_documentation.md#symbol-scope_nodes), `sorted`.

Выражения возврата (ветви, без исполнения):

- `sorted({part.attr for part in scope_nodes(node) if isinstance(part, ast.Attribute) and isinstance(part.ctx, ast.Store) and isinstance(part.value, ast.Name) and (part.value.id == 'self')})`


<a id="symbol-project_imports"></a>

## `project_imports`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `project_imports`

Собирает абсолютные имена импортируемых модулей проекта. Относительные импорты разрешаются от пакета исходного файла.

```python
def project_imports(path, text, module_paths)
```

Прямые выражения вызова: `'.'.join`, `'.'.join([*prefix, node.module or '']).strip`, `(name + '.' + alias.name).strip`, `ast.parse`, `ast.walk`, `isinstance`, `len`, `path.removesuffix`, `path.removesuffix('.py').replace`, `path.removesuffix('.py').replace('/', '.').split`, `result.add`, `result.update`, `set`, `sorted`.

Выражения возврата (ветви, без исполнения):

- `sorted(result)`


<a id="symbol-python_symbols"></a>

## `python_symbols`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `python_symbols`

Разбирает Python-модуль и проверяет покрытие пояснениями каждого определения. Сортирует результат по устойчивым якорям, исключая физический порядок разных имён.

```python
def python_symbols(path, text)
```

Прямые выражения вызова: `Counter`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), [Symbol](scripts--build_documentation.md#symbol-Symbol), [definitions](scripts--build_documentation.md#symbol-definitions), [explanation_at](scripts--build_documentation.md#symbol-explanation_at), `min`, `result.append`, `sorted`, [symbol_anchor](scripts--build_documentation.md#symbol-symbol_anchor).

Явные `raise`:

- `DocumentationError(f'{path} / {name}: {error}')`

Перехватываемые типы: `DocumentationError`.

Выражения возврата (ветви, без исполнения):

- `sorted(result, key=lambda symbol: symbol.anchor)`


<a id="symbol-reference_name"></a>

## `reference_name`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `reference_name`

Преобразует путь Python-модуля в имя страницы справочника. Разделитель каталогов кодируется двойным дефисом, расширение убирается.

```python
def reference_name(path)
```

Прямые выражения вызова: `path.removesuffix`, `path.removesuffix('.py').replace`.

Выражения возврата (ветви, без исполнения):

- `path.removesuffix('.py').replace('/', '--') + '.md'`


<a id="symbol-render_api"></a>

## `render_api`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_api`

Строит полный HTTP-справочник из актуального OpenAPI и комментариев обработчиков. Сортировка маршрутов и JSON исключает случайный порядок и изменчивые operationId.

```python
def render_api(snapshot, inventory)
```

Прямые выражения вызова: `', '.join`, `'\n'.join`, `'\n'.join(output).strip`, `api['components']['schemas'].items`, `api['paths'].items`, `body.get`, `json.dumps`, [literal](scripts--build_documentation.md#symbol-literal), `method.upper`, `operation.get`, `operation['responses'].items`, `operations.items`, `output.append`, `parameter.get`, [route_symbols](scripts--build_documentation.md#symbol-route_symbols), `sorted`, [symbol_link](scripts--build_documentation.md#symbol-symbol_link).

Выражения возврата (ветви, без исполнения):

- `'\n'.join(output).strip() + '\n'`


<a id="symbol-render_class"></a>

## `render_class`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_class`

Описывает класс с наследованием, полями, состоянием и методами. Сохраняет подробности прежнего справочника через структурный разбор AST.

```python
def render_class(node)
```

Прямые выражения вызова: `', '.join`, `ast.unparse`, [fields](scripts--build_documentation.md#symbol-fields), `isinstance`, [literal](scripts--build_documentation.md#symbol-literal), `next`, [own_assignments](scripts--build_documentation.md#symbol-own_assignments).

Выражения возврата (ветви, без исполнения):

- `output`


<a id="symbol-render_function"></a>

## `render_function`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_function`

Описывает точную сигнатуру, вызовы, изменения состояния и ветви функции. Ссылки на соседние определения используют устойчивые лексические имена.

```python
def render_function(symbol, symbols, tables, document)
```

Прямые выражения вызова: `', '.join`, `any`, `ast.unparse`, [call_target](scripts--build_documentation.md#symbol-call_target), [calls](scripts--build_documentation.md#symbol-calls), `dict.fromkeys`, [effects](scripts--build_documentation.md#symbol-effects), `invoked.append`, `isinstance`, `list`, [literal](scripts--build_documentation.md#symbol-literal), [own_assignments](scripts--build_documentation.md#symbol-own_assignments), [scope_nodes](scripts--build_documentation.md#symbol-scope_nodes), [symbol_link](scripts--build_documentation.md#symbol-symbol_link).

Выражения возврата (ветви, без исполнения):

- `output`


<a id="symbol-render_module"></a>

## `render_module`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_module`

Строит подробную страницу одного Python-модуля. Собирает структуру импортов, константы и каждое определение без координат исходника.

```python
def render_module(path, text, symbols, metadata, imports, test_imports)
```

Прямые выражения вызова: `' '.join`, `', '.join`, `'\n'.join`, `'\n'.join(output).strip`, [constants](scripts--build_documentation.md#symbol-constants), `imports.items`, `isinstance`, `item.removesuffix`, `item.removesuffix('.py').replace`, [link_from](scripts--build_documentation.md#symbol-link_from), [literal](scripts--build_documentation.md#symbol-literal), `quote`, [reference_name](scripts--build_documentation.md#symbol-reference_name), [render_class](scripts--build_documentation.md#symbol-render_class), [render_function](scripts--build_documentation.md#symbol-render_function), `sorted`.

Выражения возврата (ветви, без исполнения):

- `'\n'.join(output).strip() + '\n'`


<a id="symbol-render_native"></a>

## `render_native`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_native`

Строит нативный справочник с сигнатурами, пояснениями и точками входа. Исходные файлы связаны по имени, а каждый метод имеет отдельный устойчивый якорь.

```python
def render_native(symbols)
```

Прямые выражения вызова: `' '.join`, `'\n'.join`, `'\n'.join(output).strip`, [link_from](scripts--build_documentation.md#symbol-link_from), `quote`.

Выражения возврата (ветви, без исполнения):

- `'\n'.join(output).strip() + '\n'`


<a id="symbol-render_schema"></a>

## `render_schema`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_schema`

Строит полную схему SQLite с описаниями и устойчивыми источниками таблиц. Данные берутся из новых временных баз после действующих миграций.

```python
def render_schema(snapshot, metadata, texts, inventory)
```

Прямые выражения вызова: `', '.join`, `'\n'.join`, `'\n'.join(output).strip`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `bool`, [literal](scripts--build_documentation.md#symbol-literal), `name.replace`, `snapshot['databases'].items`, `sorted`, `table['name'].replace`, [table_origins](scripts--build_documentation.md#symbol-table_origins).

Явные `raise`:

- `DocumentationError(f'Для новой таблицы {name} требуется смысловое описание')`

Выражения возврата (ветви, без исполнения):

- `'\n'.join(output).strip() + '\n'`


<a id="symbol-render_tests"></a>

## `render_tests`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `render_tests`

Формирует справочник всех существующих тестовых определений. Якоря включают модуль, класс, вложенное имя и номер повторного объявления.

```python
def render_tests(root, metadata)
```

Прямые выражения вызова: `'\n'.join`, `'\n'.join(output).strip`, `Counter`, `ast.unparse`, [definitions](scripts--build_documentation.md#symbol-definitions), `isinstance`, [link_from](scripts--build_documentation.md#symbol-link_from), `metadata.get`, `metadata.get('tests', {}).get`, `node.name.startswith`, `path.read_text`, `path.relative_to`, `relative.removesuffix`, `relative.removesuffix('.py').replace`, `root.glob`, `sorted`, `str`, [symbol_anchor](scripts--build_documentation.md#symbol-symbol_anchor).

Выражения возврата (ветви, без исполнения):

- `'\n'.join(output).strip() + '\n'`


<a id="symbol-route_symbols"></a>

## `route_symbols`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `route_symbols`

Связывает HTTP-маршруты с их именованными обработчиками текущего Core. Извлекает метод и путь из декораторов FastAPI без координат исходника.

```python
def route_symbols(inventory)
```

Прямые выражения вызова: `inventory.get`, `isinstance`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-scope_nodes"></a>

## `scope_nodes`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `scope_nodes`

Выбирает узлы собственного тела определения для подробного справочника. Вложенные функции, классы и lambda описываются в своих областях.

```python
def scope_nodes(node)
```

Прямые выражения вызова: `ast.iter_child_nodes`, `isinstance`, `list`, `pending.extend`, `pending.pop`, `result.append`, `reversed`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-snapshot_runtime"></a>

## `snapshot_runtime`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `snapshot_runtime`

Выполняет изолированный снимок OpenAPI и пустых SQLite-схем текущего Core. Каталог данных временный, PhotoKit отключён, lifespan и сервер не запускаются.

```python
def snapshot_runtime(root)
```

Прямые выражения вызова: [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `Path`, `Path(__file__).resolve`, `dict`, `json.loads`, `output.read_text`, `result.stderr.strip`, `str`, `subprocess.run`, `tempfile.TemporaryDirectory`.

Явные `raise`:

- `DocumentationError('Не удалось снять схему в изоляции: ' + result.stderr.strip())`

Выражения возврата (ветви, без исполнения):

- `json.loads(output.read_text())`


<a id="symbol-symbol_anchor"></a>

## `symbol_anchor`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `symbol_anchor`

Строит непотерянный якорь по полному имени и номеру повторного объявления. Регистр, точки и подчёркивания имён сохраняются для различения определений.

```python
def symbol_anchor(name, occurrence=1)
```

Выражения возврата (ветви, без исполнения):

- `'symbol-' + name + suffix`


<a id="symbol-symbol_at_line"></a>

## `symbol_at_line`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `symbol_at_line`

Находит владельца строки или объявления внутри AST для миграции старых ссылок. Выбирает самое глубокое содержащее определение, используя позиции только в памяти.

```python
def symbol_at_line(symbols, line)
```

Прямые выражения вызова: `min`.

Выражения возврата (ветви, без исполнения):

- `min(candidates, key=lambda symbol: symbol.node.end_lineno - symbol.node.lineno) if candidates else None`


<a id="symbol-symbol_link"></a>

## `symbol_link`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `symbol_link`

Возвращает ссылку на полное определение в Python- или нативном справочнике. Исходные файлы открываются отдельными ссылками без физического номера строки.

```python
def symbol_link(document, symbol, label=None)
```

Прямые выражения вызова: [link_from](scripts--build_documentation.md#symbol-link_from), [reference_name](scripts--build_documentation.md#symbol-reference_name), `symbol.path.endswith`.

Выражения возврата (ветви, без исполнения):

- `link_from(document, target, label or symbol.name, symbol.anchor)`


<a id="symbol-synchronize"></a>

## `synchronize`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `synchronize`

Сравнивает построенные справочники с диском и обновляет только изменившиеся файлы. Режим check выдаёт diff и ошибку при устаревшем описании или лишней странице реестра.

```python
def synchronize(root, documents, check=False)
```

Прямые выражения вызова: `''.join`, `', '.join`, `(root / 'docs/reference').glob`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `changed.append`, `current.splitlines`, `difflib.unified_diff`, `documents.items`, `path.relative_to`, `path.startswith`, `print`, `sorted`, `str`, `target.exists`, `target.parent.mkdir`, `target.read_text`, `target.write_text`, `text.splitlines`.

Явные `raise`:

- `DocumentationError('Страницы без соответствующего модуля: ' + ', '.join(sorted(extras)))`
- `DocumentationError('Устаревшие справочники: ' + ', '.join(changed))`

Выражения возврата (ветви, без исполнения):

- `changed`


<a id="symbol-table_origins"></a>

## `table_origins`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `table_origins`

Находит устойчивый источник определения SQL-таблицы в исходном коде. Ссылается на содержащий конструктор либо именованную константу схемы.

```python
def table_origins(table, texts, inventory, document)
```

Прямые выражения вызова: `ast.parse`, `ast.walk`, [constants](scripts--build_documentation.md#symbol-constants), `isinstance`, [link_from](scripts--build_documentation.md#symbol-link_from), `next`, `pattern.search`, `re.compile`, `re.escape`, [reference_name](scripts--build_documentation.md#symbol-reference_name), `result.append`, `set`, `sorted`, [symbol_at_line](scripts--build_documentation.md#symbol-symbol_at_line), [symbol_link](scripts--build_documentation.md#symbol-symbol_link), `texts.items`.

Выражения возврата (ветви, без исполнения):

- `sorted(set(result))`


<a id="symbol-validate_links"></a>

## `validate_links`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `validate_links`

Проверяет локальные пути, устойчивые якоря и запрет построчных ссылок. Учитывает ещё не записанные результаты генерации через виртуальный набор документов.

```python
def validate_links(root, documents)
```

Прямые выражения вызова: `'\n'.join`, `(root / 'README.md').exists`, `(root / 'README.md').read_text`, `(root / destination).is_file`, [DocumentationError](scripts--build_documentation.md#symbol-DocumentationError), `errors.append`, [markdown_anchors](scripts--build_documentation.md#symbol-markdown_anchors), [markdown_links](scripts--build_documentation.md#symbol-markdown_links), `path.read_text`, `path.relative_to`, `posixpath.dirname`, `posixpath.join`, `posixpath.normpath`, `re.fullmatch`, `root.glob`, `sorted`, `str`, `texts.items`, `texts.update`, `unquote`, `urlsplit`.

Явные `raise`:

- `DocumentationError('\n'.join(errors))`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-write_runtime_snapshot"></a>

## `write_runtime_snapshot`

[scripts/build_documentation.py](../../scripts/build_documentation.py) · `write_runtime_snapshot`

Собирает схемы в дочернем процессе с временным каталогом данных. Подмена supported запрещает обращение к реальному Photos при инициализации Core.

```python
def write_runtime_snapshot(root, output)
```

Прямые выражения вызова: `Path`, `api['paths'].values`, `app.app.openapi`, `database.execute`, `dict`, `isinstance`, `json.dumps`, `operation.pop`, `operations.values`, `output.write_text`, `patch.object`, `property`, `sorted`, `sqlite3.connect`, `str`, `sys.path.insert`, `tables.append`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
