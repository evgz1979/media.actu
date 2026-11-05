import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts import build_documentation as documentation


SOURCE = '''#: Форматирует переданное значение.
#: Использует явно переданный масштаб.
def format_value(value: int, scale: int = 1) -> int:
    return value * scale

#: Проверяет переданное значение.
#: Возвращает признак положительного числа.
def positive(value: int) -> bool:
    return value > 0
'''


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'example.py'
        self.source.write_text(SOURCE)
        metadata = {'modules': {'example.py': {'title': 'Пример', 'description': 'Изолированный пример.'}},
                    'tables': {}, 'tests': {}, 'native': []}
        target = self.root / documentation.METADATA_PATH
        target.parent.mkdir()
        target.write_text(json.dumps(metadata, ensure_ascii=False))
        for path in ('docs/development/language.md', 'docs/development/documentation.md', 'docs/development/native.md',
                     'docs/api.md', 'docs/data-model.md'):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('# Объяснение\n')

    def build(self):
        return documentation.build_documents(self.root)

    def write_current(self):
        documents = self.build()
        documentation.validate_links(self.root, documents)
        documentation.synchronize(self.root, documents)
        return documents

    def test_line_shifts_and_ordinary_comments_produce_no_document_changes(self):
        before = self.write_current()
        shifted = '\n\n# Обычный комментарий в начале модуля.\n' + SOURCE
        shifted = shifted.replace('def format_value', '\n# Дополнительное пояснение для читателя.\n\ndef format_value')
        shifted = shifted.replace('    return value * scale', '    # Внутренний комментарий.\n\n    return value * scale')
        self.source.write_text(shifted)
        after = self.build()
        self.assertEqual(before, after)
        documentation.validate_links(self.root, after)
        self.assertEqual(documentation.synchronize(self.root, after, check=True), [])

    def test_contract_change_updates_only_its_definition(self):
        before = self.write_current()
        self.source.write_text(SOURCE.replace('scale: int = 1', 'scale: int = 2'))
        after = self.build()
        changed = [path for path in before if before[path] != after[path]]
        self.assertEqual(changed, ['docs/reference/example.md'])
        self.assertEqual(before[changed[0]].replace('scale: int=1', 'scale: int=2'), after[changed[0]])
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(documentation.DocumentationError, 'Устаревшие'):
            documentation.synchronize(self.root, after, check=True)

    def test_missing_explanation_is_detected_even_with_ordinary_comments(self):
        self.source.write_text(SOURCE.replace('#: Использует явно переданный масштаб.', '# Обычное пояснение.\n# Ещё одно пояснение.'))
        with self.assertRaisesRegex(documentation.DocumentationError, 'две строки'):
            self.build()

    def test_changed_marked_explanation_updates_corresponding_description(self):
        before = self.build()
        self.source.write_text(SOURCE.replace('Форматирует переданное значение.', 'Масштабирует переданное значение.'))
        after = self.build()
        changed = {path for path in before if before[path] != after[path]}
        self.assertEqual(changed, {'docs/reference/example.md'})
        self.assertEqual(before['docs/reference/example.md'].replace('Форматирует переданное значение.', 'Масштабирует переданное значение.'), after['docs/reference/example.md'])

    def test_duplicate_names_preserve_scope_case_and_declaration_identity(self):
        source = '''#: Верхний класс.
#: Содержит свойство.
class Upper:
    #: Читает свойство.
    #: Возвращает число.
    @property
    def value(self):
        return 1

    #: Изменяет свойство.
    #: Принимает число.
    @value.setter
    def value(self, number):
        pass

#: Другой класс.
#: Сохраняет отдельное имя.
class upper:
    #: Читает другой метод.
    #: Возвращает число.
    def value(self):
        return 2
'''
        symbols = documentation.python_symbols('example.py', source)
        anchors = [symbol.anchor for symbol in symbols]
        self.assertEqual(len(anchors), len(set(anchors)))
        self.assertIn('symbol-Upper.value', anchors)
        self.assertIn('symbol-Upper.value--declaration-2', anchors)
        self.assertIn('symbol-upper.value', anchors)
        shifted = documentation.python_symbols('example.py', '# Сдвиг\n\n' + source)
        self.assertEqual(anchors, [symbol.anchor for symbol in shifted])
        repeated = '\n'.join('#: Объявление.\n#: Его контракт.\ndef repeat(value=' + str(number) + '):\n    return value\n'
                             for number in range(12))
        repeated_symbols = documentation.python_symbols('example.py', repeated)
        owner = documentation.Symbol('example.py', 'caller', 'symbol-caller', None, ('Вызов.', 'Его контракт.'))
        target = documentation.call_target(owner, 'repeat', repeated_symbols)
        self.assertEqual(target.anchor, 'symbol-repeat--declaration-12')

    def test_removed_function_is_reported_as_stale(self):
        self.write_current()
        self.source.write_text(SOURCE[:SOURCE.index('#: Проверяет')])
        documents = self.build()
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(documentation.DocumentationError, 'Устаревшие'):
            documentation.synchronize(self.root, documents, check=True)

    def test_link_to_removed_definition_is_detected(self):
        self.write_current()
        (self.root / 'README.md').write_text('[Проверка](docs/reference/example.md#symbol-positive)\n')
        self.source.write_text(SOURCE[:SOURCE.index('#: Проверяет')])
        with self.assertRaisesRegex(documentation.DocumentationError, 'отсутствует якорь'):
            documentation.validate_links(self.root, self.build())

    def test_missing_file_and_physical_line_link_are_detected(self):
        for target in ('absent.md', 'example.py#L1'):
            with self.subTest(target=target):
                (self.root / 'README.md').write_text('[Цель](' + target + ')\n')
                with self.assertRaises(documentation.DocumentationError):
                    documentation.validate_links(self.root, self.build())

    def test_missing_module_and_unregistered_module_are_detected(self):
        self.source.unlink()
        with self.assertRaisesRegex(documentation.DocumentationError, 'пропавшие'):
            self.build()
        self.source.write_text(SOURCE)
        (self.root / 'unknown.py').write_text('')
        with self.assertRaisesRegex(documentation.DocumentationError, 'новые'):
            self.build()

    def test_orphaned_reference_page_is_detected(self):
        documents = self.write_current()
        (self.root / 'docs/reference/orphan.md').write_text('# Старый модуль\n')
        with self.assertRaisesRegex(documentation.DocumentationError, 'Страницы без соответствующего модуля'):
            documentation.synchronize(self.root, documents, check=True)

    def test_release_hash_is_preserved_as_semantic_constant(self):
        digest = 'fedcba9876543210' * 4
        self.source.write_text(SOURCE + '\nRELEASE_SHA256 = ' + repr(digest) + '\n')
        page = self.build()['docs/reference/example.md']
        self.assertIn(digest, page)
        self.assertIn('constant-RELEASE_SHA256', page)

    def test_native_definition_ignores_line_shifts_and_ordinary_comments(self):
        source = '''//: Выполняет действие.
//: Возвращает статус.
static int action(int value) {
    return value;
}
'''
        before = documentation.render_native(documentation.objective_c_symbols('helper.m', source))
        changed = '\n// Обычный комментарий.\n\n' + source.replace('static int', '// Ещё один комментарий.\n\nstatic int')
        after = documentation.render_native(documentation.objective_c_symbols('helper.m', changed))
        self.assertEqual(before, after)
        multiline = source.replace('int value', 'int\n\n// Комментарий с { и } внутри параметров.\nvalue')
        self.assertEqual(before, documentation.render_native(documentation.objective_c_symbols('helper.m', multiline)))

    def test_vue_watch_and_method_with_same_name_have_distinct_anchors(self):
        source = '''export default {
    watch: {
        //: Следит за состоянием.
        //: Принимает значение.
        state(value) { this.selected = value; },
    },
    methods: {
        //: Читает состояние.
        //: Возвращает значение.
        state() { return this.selected; },
    },
};
'''
        symbols = documentation.javascript_symbols('paired_tree.js', source)
        self.assertEqual({symbol.name for symbol in symbols}, {'paired_tree.js.watch.state', 'paired_tree.js.methods.state'})
        self.assertEqual(len({symbol.anchor for symbol in symbols}), 2)


if __name__ == '__main__':
    unittest.main()
