from contextlib import nullcontext
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from comparison_tree_ui import ComparisonTree
from paired_workspace_ui import PairedWorkspace
from workspace_ui import BrowserPane, StorageWorkspace, TREE_FOCUS_JS, TREE_KEY_JS


def client():
    result = nullcontext()
    result.is_deleted = False
    return result


class TreeKeyboardTests(unittest.IsolatedAsyncioTestCase):
    def pane(self):
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace = SimpleNamespace(client=client(), editing=False, context_menu_open=False)
        pane.view_mode = 'tree'
        pane.navigation_entries = {'row': ({'path': 'Album', 'kind': 'directory'}, None, Mock())}
        pane.select = AsyncMock()
        return pane

    async def test_arrow_selection_does_not_toggle_or_rebuild_a_folder(self):
        pane = self.pane()
        await pane.keyboard_selected(SimpleNamespace(args={'key': 'row'}))
        pane.select.assert_awaited_once_with({'path': 'Album', 'kind': 'directory'}, render=False)

    async def test_stale_events_and_dialog_or_preview_focus_do_not_move_the_tree(self):
        pane = self.pane()
        await pane.keyboard_selected(SimpleNamespace(args={'key': 'old-volume-row'}))
        for field in ('editing', 'context_menu_open'):
            setattr(pane.workspace, field, True)
            await pane.keyboard_selected(SimpleNamespace(args={'key': 'row'}))
            setattr(pane.workspace, field, False)
        pane.view_mode = 'preview'
        await pane.keyboard_selected(SimpleNamespace(args={'key': 'row'}))
        pane.select.assert_not_awaited()

    async def test_comparison_arrow_selection_preserves_collapsed_folders(self):
        ws = SimpleNamespace(active_index=1, report={'scans': [{'id': 3}]},
            set_active=Mock(), preview_selection=AsyncMock(), request=AsyncMock())
        pane = SimpleNamespace(workspace=ws, volume_id='disk', render=Mock(),
            update_navigation_selection=Mock(), update_header=Mock())
        comparison = ComparisonTree(pane)
        entry = dict(scan_id=3, path='Album', kind='directory')
        scope = dict(volume_id='disk', path='')
        await comparison.select(entry, scope, toggle=False, render=False)
        self.assertEqual(comparison.expanded, set())
        ws.request.assert_not_awaited()
        pane.render.assert_not_called()
        pane.update_navigation_selection.assert_called_once_with(entry, scope)
        ws.preview_selection.assert_awaited_once_with(pane)

    async def test_paired_arrow_keeps_a_collapsed_folder_closed_and_updates_both_sides(self):
        ws = SimpleNamespace(client=client(), set_active=Mock(), preview_selection=AsyncMock(),
                             panes=[SimpleNamespace(), SimpleNamespace()])
        pair = PairedWorkspace(ws)
        pair.scopes = {'left': {'path': 'Main'}, 'right': {'path': 'Copy'}}
        pair.by_path = {'Album': dict(path='Album', kind='directory',
            left={'path': 'Main/Album', 'kind': 'directory'}, right=None)}
        pair.closed = {'Album'}
        pair.redraw = Mock()
        await pair.on_select(SimpleNamespace(args=dict(path='Album', side='right', keyboard=True)))
        self.assertEqual(pair.closed, {'Album'})
        self.assertEqual([p.path for p in ws.panes], ['Main/Album', 'Copy/Album'])
        pair.redraw.assert_called_once_with(rows_changed=False)
        ws.preview_selection.assert_awaited_once_with(ws.panes[1])

    async def test_disconnected_sources_are_hidden_but_the_current_caption_is_preserved(self):
        ws = StorageWorkspace.__new__(StorageWorkspace)
        ws.volumes = [dict(id='disk', name='Online', kind='external', availability='online', mounted=True),
                      dict(id='cold', name='Offline disk', kind='external', availability='offline', mounted=False),
                      dict(id='unknown', name='Unknown', kind='network', availability='unknown', mounted=False)]
        ws.photo_libraries = SimpleNamespace(volumes=lambda: [
            dict(id='photos-1', name='Active', kind='photos', availability='online', mounted=False),
            dict(id='photos-2', name='Saved', kind='photos', availability='offline', mounted=False)])
        pane = BrowserPane.__new__(BrowserPane)
        pane.workspace = ws
        pane.volume_select = SimpleNamespace(props={}, set_options=Mock())
        pane.update_volume_select('cold')
        options = pane.volume_select.set_options.call_args.args[0]
        self.assertEqual(set(options), {'disk', 'unknown', 'photos-1'})
        self.assertIsNone(pane.volume_select.set_options.call_args.kwargs['value'])
        self.assertEqual(pane.volume_select.props['display-value'], 'Offline disk')
        pane.update_volume_select('disk')
        self.assertNotIn('display-value', pane.volume_select.props)


NODE = shutil.which('node')
if not NODE and Path('/Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node').is_file():
    NODE = '/Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node'


@unittest.skipUnless(NODE, 'JavaScript checks need Node.js')
class TreeKeyboardJavaScriptTests(unittest.TestCase):
    def run_js(self, script, data=None):
        result = subprocess.run([NODE, '--input-type=module', '-e', script],
                                input=json.dumps(data), text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rendered_rows_boundaries_inputs_and_new_render_revision(self):
        self.run_js('''
import assert from 'node:assert/strict';
import fs from 'node:fs';
const source=JSON.parse(fs.readFileSync(0,'utf8')), emitted=[];
const rows=['folder','child','next'].map(key=>({dataset:{treeKey:key},selected:false,
 classList:{toggle(name,value){rows.find(r=>r.dataset.treeKey===key).selected=value;}},
 setAttribute(){},scrollIntoView(){this.scrolled=true;}}));
const tree={dataset:{navigationRevision:'1'},querySelectorAll:()=>rows,
 querySelector:()=>rows.find(row=>row.selected),focus(){this.focused=true;}};
const move=Function('emit','return '+source.key)(event=>emitted.push(event));
const event=key=>({key,currentTarget:tree,target:{closest:()=>null},preventDefault(){},stopPropagation(){}});
move(event('ArrowDown')); move(event('ArrowDown')); move(event('ArrowDown')); move(event('ArrowDown'));
assert.deepEqual(emitted.map(e=>e.key),['folder','child','next']);
move(event('ArrowUp')); assert.equal(emitted.at(-1).key,'child');
const before=emitted.length;
move({...event('ArrowDown'),target:{closest:()=>({})}});
move({...event('ArrowDown'),ctrlKey:true});
assert.equal(emitted.length,before);
tree.dataset.navigationRevision='2'; rows.forEach(row=>row.selected=row.dataset.treeKey==='folder');
move(event('ArrowDown')); assert.equal(emitted.at(-1).key,'child');
assert.ok(rows[1].scrolled);
const focus=Function('emit','return '+source.focus)(()=>{});
focus({...event('click'),target:{closest:selector=>selector==='[data-tree-key]'?rows[2]:null}});
assert.equal(tree.dataset.keyboardKey,'next');assert.ok(tree.focused);
''', dict(key=TREE_KEY_JS, focus=TREE_FOCUS_JS))

    def test_virtual_tree_moves_beyond_the_viewport_and_ignores_old_server_selection(self):
        source = str(Path(__file__).resolve().parents[1] / 'paired_tree.js')
        self.run_js('''
import assert from 'node:assert/strict';
import fs from 'node:fs';
const filename=JSON.parse(fs.readFileSync(0,'utf8'));
const component=(await import('data:text/javascript;base64,'+fs.readFileSync(filename).toString('base64'))).default;
const emitted=[],viewport={scrollTop:0,clientHeight:56,focus(){}};
const context={rows:Array.from({length:200},(_,i)=>({path:'row'+i})),side:'left',selection:'row0',keyboardCursor:null,
 $refs:{viewport},$emit:(...args)=>emitted.push(args),scrolled(){}};
const event=()=>({key:'ArrowDown',target:{closest:()=>null},preventDefault(){},stopPropagation(){}});
for(let i=0;i<30;i++) {component.methods.keyDown.call(context,event());context.selection='row0';}
assert.equal(context.keyboardCursor,'row30');assert.ok(viewport.scrollTop>0);
assert.equal(emitted.at(-1)[1].keyboard,true);
for(let i=0;i<300;i++) component.methods.keyDown.call(context,event());
assert.equal(context.keyboardCursor,'row199');assert.equal(emitted.length,199);
''', source)
