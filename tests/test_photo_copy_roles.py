from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from photo_libraries_ui import PhotoLibrariesUI
from workspace_ui import folder_membership


class PhotoCopyRoleTests(unittest.TestCase):
    def setUp(self):
        self.pane = SimpleNamespace(view_mode='tree', volume_id='disk', render=Mock())
        self.ws = SimpleNamespace(copies=SimpleNamespace(membership=Mock(return_value=None)),
                                  context_menu_open=False, editing=False, panes=[self.pane],
                                  is_photos=lambda volume: str(volume).startswith('photos-'))
        self.libraries = PhotoLibrariesUI(self.ws)
        self.ws.photo_libraries = self.libraries
        self.libraries.libraries = [dict(id=5, label='Photos evgz', active=False,
            copies=[dict(id='link', volume_id='disk', path='Apple/evgz', number=1, connected=1)])]

    def test_bound_copy_has_its_own_number_and_library_tag_while_photos_is_offline(self):
        role = folder_membership(self.ws, 'disk', 'Apple/evgz')
        self.assertEqual(role['label'], '01-copy')
        self.assertEqual(role['media_library'], 'Photos evgz')
        self.assertTrue(role['is_root'])
        self.ws.copies.membership.assert_not_called()
        self.libraries.libraries[0]['copies'][0]['number'] = 3
        self.assertEqual(folder_membership(self.ws, 'disk', 'Apple/evgz')['label'], '03-copy')

    def test_only_the_exact_bound_folder_gets_the_library_role(self):
        for volume, path in [('other', 'Apple/evgz'), ('disk', 'Apple'),
                             ('disk', 'Apple/evgz/2026'), ('disk', 'Apple/evgz-other')]:
            with self.subTest(volume=volume, path=path):
                self.assertIsNone(folder_membership(self.ws, volume, path))

    def test_disconnecting_library_copy_removes_its_tags_and_preserves_other_roles(self):
        self.libraries.libraries[0]['copies'][0]['connected'] = 0
        self.assertIsNone(folder_membership(self.ws, 'disk', 'Apple/evgz'))
        ordinary = dict(label='00-main', path='Docs', number=0, is_root=True)
        self.ws.copies.membership.return_value = ordinary
        self.assertIs(folder_membership(self.ws, 'disk', 'Docs'), ordinary)
        self.libraries.libraries[0]['copies'] = []
        self.ws.copies.membership.return_value = None
        self.assertIsNone(folder_membership(self.ws, 'disk', 'Apple/evgz'))

    def test_refresh_updates_tags_after_rebinding_but_not_on_progress_changes(self):
        self.libraries.refresh_copy_roles()
        self.pane.render.assert_called_once()
        self.pane.render.reset_mock()
        self.libraries.libraries[0]['copies'][0]['originals'] = dict(state='saving', done_assets=123)
        self.libraries.refresh_copy_roles()
        self.pane.render.assert_not_called()
        self.ws.context_menu_open = True
        self.libraries.libraries[0]['copies'][0]['path'] = 'Photos/evgz'
        self.libraries.refresh_copy_roles()
        self.pane.render.assert_not_called()
        self.ws.context_menu_open = False
        self.libraries.refresh_copy_roles()
        self.pane.render.assert_called_once()
        self.assertIsNone(folder_membership(self.ws, 'disk', 'Apple/evgz'))
        self.assertEqual(folder_membership(self.ws, 'disk', 'Photos/evgz')['label'], '01-copy')
