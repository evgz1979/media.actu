import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from comparison_tree_ui import ComparisonTree


class ComparisonTreeTests(unittest.IsolatedAsyncioTestCase):
    def navigable_tree(self, request):
        workspace = SimpleNamespace(request=request, job_id='job', active_index=0,
                                    report={'scans': [{'id': 1, 'side': 'target'}]}, render_volumes=Mock())
        workspace.set_active = lambda index: setattr(workspace, 'active_index', index)
        pane = SimpleNamespace(workspace=workspace, volume_id='disk', render=Mock())
        return ComparisonTree(pane)

    async def test_opened_folder_keeps_matches_and_breadcrumb_navigation_within_its_scope(self):
        calls = []

        async def request(_method, _endpoint, *, params, **_kwargs):
            calls.append((params['scan_id'], params['path']))
            return {'entries': [], 'total': 0}

        tree = self.navigable_tree(request)
        scope = {'scan_id': 1, 'volume_id': 'disk', 'volume_name': 'NAS', 'path': 'Private/Album', 'kind': 'directory'}
        tree.roots = [scope, dict(scope, scan_id=2, volume_id='second-disk')]
        await tree.open_folder(scope, scope)
        self.assertEqual(tree.focus, (scope, scope))
        self.assertEqual(len(tree.roots), 2)
        await tree.open_path('Private/Album/Sub')
        self.assertEqual(tree.focus[1]['path'], 'Private/Album/Sub')
        await tree.open_path('Private')
        self.assertEqual(calls, [(1, 'Private/Album'), (1, 'Private/Album/Sub')])
        tree.show_matches()
        self.assertIsNone(tree.focus)
        self.assertIsNone(tree.selected)
        self.assertEqual(len(tree.roots), 2)

    async def test_slow_folder_open_cannot_focus_previous_source_results(self):
        started, finish = asyncio.Event(), asyncio.Event()

        async def request(*_args, **_kwargs):
            started.set()
            await finish.wait()
            return {'entries': [], 'total': 0}

        tree = self.navigable_tree(request)
        scope = {'scan_id': 1, 'volume_id': 'disk', 'path': 'Album', 'kind': 'directory'}
        pending = asyncio.create_task(tree.open_folder(scope, scope))
        await started.wait()
        tree.reset(('job', 'other-source'))
        finish.set()
        await pending
        self.assertIsNone(tree.focus)
        self.assertIsNone(tree.selected)
        self.assertEqual(tree.roots, [])

    async def test_slow_folder_response_cannot_restore_results_from_previous_selection(self):
        for change in ('selection', 'job'):
            with self.subTest(change=change):
                started, finish = asyncio.Event(), asyncio.Event()

                async def request(*_args, **_kwargs):
                    started.set()
                    await finish.wait()
                    return {'entries': [{'name': 'old.txt'}], 'total': 1}

                workspace = SimpleNamespace(request=request, job_id='old-job')
                tree = ComparisonTree(SimpleNamespace(workspace=workspace))
                tree.reset(('old-job', 'Album'))
                pending = asyncio.create_task(tree.load({'scan_id': 1, 'path': 'Private/Album'}))
                await started.wait()
                if change == 'selection':
                    tree.reset(('old-job', 'Missing'))
                else:
                    workspace.job_id = 'new-job'
                finish.set()
                self.assertFalse(await pending)
                self.assertEqual(tree.folders, {})
                self.assertEqual(tree.roots, [])

    async def test_identical_paths_on_two_targets_have_independent_folder_pages(self):
        calls = []

        async def request(_method, _endpoint, *, params, **_kwargs):
            calls.append((params['scan_id'], params['offset']))
            suffix = 'next' if params['offset'] else 'first'
            return {'entries': [{'name': f"disk-{params['scan_id']}-{suffix}.txt"}], 'total': 2}

        tree = ComparisonTree(SimpleNamespace(workspace=SimpleNamespace(request=request, job_id='job')))
        first, second = {'scan_id': 1, 'path': 'Private/Album'}, {'scan_id': 2, 'path': 'Private/Album'}
        await tree.load(first)
        await tree.load(second)
        await tree.load(first, more=True)
        self.assertEqual(calls, [(1, 0), (2, 0), (1, 1)])
        self.assertEqual([e['name'] for e in tree.folders[(1, 'Private/Album')]['entries']],
                         ['disk-1-first.txt', 'disk-1-next.txt'])
        self.assertEqual([e['name'] for e in tree.folders[(2, 'Private/Album')]['entries']], ['disk-2-first.txt'])


if __name__ == '__main__':
    unittest.main()
