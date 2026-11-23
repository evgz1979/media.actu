import unittest

from copy_panels import copy_route, copy_upstream


#: Проверяет построение маршрута между связанными панелями.
#: Охватывает прямые связи, разветвления и отсутствующие источники.
class CopyRouteTests(unittest.TestCase):
    #: Создаёт корень маршрута и первое звено копирования.
    #: Использует числовые идентификаторы для проверки ссылки на нулевой корень.
    def setUp(self):
        self.root = dict(id=0, label='00-main')
        self.first = dict(id=1, number=1, label='01-copy', source=0)

    #: Проверяет предпочтение доступной ветки при открытии предыдущего звена.
    #: Проверяет сохранение явно выбранной ветки даже при недоступном назначении.
    def test_route_selects_an_available_continuation_without_changing_the_target(self):
        offline = dict(id=2, number=2, label='02-copy', source=1, availability='offline')
        online = dict(id=3, number=3, label='03-copy', source=1)
        end = dict(id=4, number=4, label='04-copy', source=3)
        copies = [self.first, offline, online, end]
        self.assertEqual(copy_route(self.root, copies, self.first, parent_key='source'),
                         (self.root, self.first, online, end))
        self.assertEqual(copy_route(self.root, copies, offline, parent_key='source'),
                         (self.root, self.first, offline))
        self.assertIs(copy_upstream(self.root, copies, end, parent_key='source'), online)

    #: Проверяет маршрут при отсутствии указанного предыдущего звена.
    #: Убеждается, что вместо корня показывается отметка недоступного источника.
    def test_missing_parent_does_not_replace_the_actual_upstream_with_root(self):
        target = dict(id='target', number=2, label='02-copy', volume_id='disk', source='gone')
        child = dict(id='child', number=3, label='03-copy', source='target')
        copies = [target, child]
        missing, actual, next_copy = copy_route(self.root, copies, target, parent_key='source')
        self.assertEqual(missing['label'], 'Недоступный источник')
        self.assertNotIn('volume_id', missing)
        self.assertEqual((actual, next_copy), (target, child))
        self.assertIsNone(copy_upstream(self.root, copies, target, parent_key='source'))
        self.assertIs(copy_upstream(self.root, copies, child, parent_key='source'), target)

    #: Проверяет обрыв ошибочного цикла без повторного звена и ложного корня.
    #: Не разрешает использовать циклическую связь как источник пары.
    def test_cycle_has_no_root_or_upstream(self):
        first = dict(self.first, source=2)
        target = dict(id=2, number=2, label='02-copy', source=1)
        copies = [first, target]
        route = copy_route(self.root, copies, target, parent_key='source')
        self.assertEqual(route, ({'label': 'Недоступный источник'}, first, target))
        self.assertIsNone(copy_upstream(self.root, copies, target, parent_key='source'))

    #: Проверяет прямую связь через явное значение, пустое поле и схему без поля.
    #: Проверяет, что независимые назначения iCloud не образуют цепочку.
    def test_direct_routes_stay_direct(self):
        sibling = dict(id=2, number=2, label='02-copy')
        for target, parent_key in ((self.first, 'source'), (sibling, 'source'), (sibling, None)):
            with self.subTest(target=target, parent_key=parent_key):
                self.assertEqual(copy_route(self.root, [self.first, sibling], target, parent_key=parent_key),
                                 (self.root, target))
                self.assertIs(copy_upstream(self.root, [self.first, sibling], target, parent_key=parent_key), self.root)
