import unittest

from tests import test_copy_files as fixture


class CopySourceTests(unittest.TestCase):
    def setUp(self):
        fixture.MissingCopyTests.setUp(self)
        (self.copy/'Second').mkdir()
        self.storage.directory('copy',refresh=True)
        group = self.copies.add_copy(self.group['id'],'copy','Second')
        self.first = self.copy_location
        self.second = next(c for c in group['copies'] if c['path']=='Second')

    def test_second_copy_uses_first_in_comparison_and_actual_transfer(self):
        self.put = fixture.MissingCopyTests.put.__get__(self)
        self.put('left','only-original',b'original')
        self.put('right','only-first',b'from first copy')
        self.copies.set_copy_source(self.second['id'],self.first['id'])
        self.copy_location = self.second
        self.compare = fixture.MissingCopyTests.compare.__get__(self)
        report = self.compare()
        self.assertEqual(self.pairs.job(report)['scopes']['left']['id'],self.first['id'])
        plan = self.transfers.plan(report)
        fixture.MissingCopyTests.run_plan(self,plan)
        self.assertEqual((self.copy/'Second/only-first').read_bytes(),b'from first copy')
        self.assertFalse((self.copy/'Second/only-original').exists())

    def test_cycles_cross_group_sources_and_self_sources_are_rejected(self):
        self.copies.set_copy_source(self.second['id'],self.first['id'])
        for target,source in [(self.first['id'],self.second['id']),(self.first['id'],self.first['id']),
                              (self.second['id'],'unknown')]:
            with self.subTest(target=target,source=source),self.assertRaises(ValueError):
                self.copies.set_copy_source(target,source)

    def test_disconnected_or_removed_source_never_falls_back_to_original(self):
        self.copies.set_copy_source(self.second['id'],self.first['id'])
        self.copies.set_copy_connected(self.first['id'],False)
        with self.assertRaises(ValueError):self.pairs._pair(self.second['id'])
        self.copies.remove_copy(self.first['id'])
        with self.assertRaises(ValueError):self.pairs._pair(self.second['id'])
        self.copies.set_copy_source(self.second['id'],None)
        self.assertEqual(self.pairs._pair(self.second['id'])['left']['id'],self.group['main']['id'])

    def test_change_invalidates_an_old_paused_comparison_and_plan(self):
        before = self.pairs.create(self.second['id'],background=False)
        self.copies.set_copy_source(self.second['id'],self.first['id'])
        with self.assertRaises(ValueError):self.pairs.resume(before['id'])

    def test_old_copy_plan_is_rejected_after_changing_its_source(self):
        fixture.MissingCopyTests.put(self,'left','new',b'from main')
        self.copy_location = self.second
        report = fixture.MissingCopyTests.compare(self)
        plan = self.transfers.plan(report)
        self.copies.set_copy_source(self.second['id'],self.first['id'])
        with self.assertRaises(ValueError):self.transfers.start(plan['id'],background=False)
        self.assertFalse((self.copy/'Second/new').exists())
