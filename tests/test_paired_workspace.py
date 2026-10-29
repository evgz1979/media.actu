"""File differences stay hidden until the user expands their folder."""
import unittest

from paired_workspace_ui import PairedWorkspace


class PairedWorkspaceTests(unittest.TestCase):
    def workspace(self):
        workspace = PairedWorkspace(None)
        workspace.report = {'mode': 'files'}
        workspace.differences_only = True
        workspace.rows = [
            dict(path='Album', kind='directory', status='both', depth=0),
            dict(path='Album/Sub', kind='directory', status='both', depth=1),
            dict(path='Album/Sub/different', kind='file', status='size_different', depth=2),
            dict(path='Album/different', kind='file', status='missing_copy', depth=1),
            dict(path='Album/same', kind='file', status='same_size', depth=1),
            dict(path='root-file', kind='file', status='extra_copy', depth=0),
        ]
        workspace.closed = {'Album', 'Album/Sub'}
        return workspace

    def test_expanding_one_folder_reveals_only_its_differing_files(self):
        workspace = self.workspace()
        paths = lambda: [r['path'] for r in workspace.visible_rows()]
        self.assertEqual(paths(), ['Album'])
        workspace.closed.remove('Album')
        self.assertEqual(paths(), ['Album', 'Album/Sub', 'Album/different'])
        workspace.closed.remove('Album/Sub')
        self.assertEqual(paths(), ['Album', 'Album/Sub', 'Album/Sub/different', 'Album/different'])

    def test_root_files_require_explicit_disclosure_even_after_navigation(self):
        workspace = self.workspace()
        workspace.root = 'Album'
        workspace.closed.remove('Album')
        paths = lambda: [r['path'] for r in workspace.visible_rows()]
        self.assertEqual(paths(), ['Album/Sub'])
        workspace.root_files_open = True
        self.assertEqual(paths(), ['Album/Sub', 'Album/different'])
