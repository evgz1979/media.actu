import asyncio
import unittest
from types import SimpleNamespace

from comparison_tree_ui import ComparisonTree


class ComparisonTreeTests(unittest.IsolatedAsyncioTestCase):
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
