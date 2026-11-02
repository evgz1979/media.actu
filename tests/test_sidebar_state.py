from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from nicegui.persistence.file_persistent_dict import FilePersistentDict

from copy_groups_ui import CopyGroupsUI
from workspace_state import SIDEBAR_DEFAULTS, SIDEBAR_STORAGE_KEY, normalize_sidebar
from workspace_ui import StorageWorkspace


class SidebarStateTests(unittest.TestCase):
    def workspace(self, storage):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.sidebar_storage = storage
        ws.sidebar_state = normalize_sidebar(storage.get(SIDEBAR_STORAGE_KEY))
        return ws

    def expansion(self, ws, key):
        element = ws.sidebar_expansion(key, key, icon='folder')
        self.addCleanup(element.delete)
        return element

    def test_browser_state_survives_new_page_and_storage_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'browser.json'
            storage = FilePersistentDict(file)
            storage.initialize_sync()
            ws = self.workspace(storage)
            chosen = dict(volumes=True, volume_archive=True, libraries=False,
                          copy_groups=False, copy_archive=True)
            for key, value in chosen.items():
                self.expansion(ws, key).set_value(value)

            reopened = FilePersistentDict(file)
            reopened.initialize_sync()
            page = self.workspace(reopened)
            for key, value in chosen.items():
                self.assertIs(self.expansion(page, key).value, value)
            self.assertEqual(dict(reopened), {SIDEBAR_STORAGE_KEY: chosen})

    def test_first_page_has_stable_defaults_without_creating_preferences(self):
        storage = {}
        ws = self.workspace(storage)
        for key, value in SIDEBAR_DEFAULTS.items():
            self.assertIs(self.expansion(ws, key).value, value)
        self.assertEqual(storage, {})

    def test_another_tab_changing_one_section_preserves_the_others(self):
        storage = {}
        first, second = self.workspace(storage), self.workspace(storage)
        first_section = self.expansion(first, 'volumes')
        second_section = self.expansion(second, 'libraries')
        first_section.open()
        second_section.close()
        page = self.workspace(storage)
        self.assertTrue(self.expansion(page, 'volumes').value)
        self.assertFalse(self.expansion(page, 'libraries').value)

    def test_invalid_preferences_do_not_expand_or_hide_unrelated_sections(self):
        value = normalize_sidebar(dict(volumes='false', libraries=0, copy_groups=False,
                                       volume_archive=True, unknown=True))
        self.assertEqual(value, dict(SIDEBAR_DEFAULTS, copy_groups=False, volume_archive=True))
        self.assertEqual(normalize_sidebar(None), SIDEBAR_DEFAULTS)


class SidebarRefreshTests(unittest.IsolatedAsyncioTestCase):
    async def test_loading_or_polling_copy_groups_never_toggles_volumes(self):
        ws = SimpleNamespace(volumes_section=Mock(), request=AsyncMock(
            side_effect=[{'groups': []}, {'groups': [{'id': 'group'}]}]))
        copies = CopyGroupsUI(ws)
        copies.render_sidebar, copies.render_controls = Mock(), Mock()
        await copies.refresh()
        await copies.refresh()
        ws.volumes_section.assert_not_called()
        self.assertEqual(ws.volumes_section.mock_calls, [])


if __name__ == '__main__':
    unittest.main()
