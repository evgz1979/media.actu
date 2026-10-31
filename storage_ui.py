"""Storage workspace; communicates with Core, never reads mounted files itself."""
from __future__ import annotations

from itertools import count

from nicegui import ui



FOLDER_ICON_IDS = count()

# The tree element survives row rendering, so the second click is recognized even
# when selecting/expanding the folder has already replaced its button.
FOLDER_CLICK_JS = '''event => {
    const tree = event.currentTarget;
    const item = event.target.closest('[data-folder-key]');
    if (!item || !tree.contains(item)) { tree.folderClick = null; return; }
    const key = item.dataset.folderKey;
    const now = performance.now();
    const last = tree.folderClick;
    const twice = event.detail > 1 || (event.detail > 0 && last && last.key === key &&
        now - last.time < 500 && Math.abs(event.clientX - last.x) < 6 && Math.abs(event.clientY - last.y) < 6);
    tree.folderClick = twice || event.detail === 0 ? null : {key, time: now, x: event.clientX, y: event.clientY};
    emit({key, double: Boolean(twice)});
}'''


def folder_icon(size=16):
    gradient = f'folder-blue-{next(FOLDER_ICON_IDS)}'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 16" width="100%" height="100%" aria-hidden="true" focusable="false">
        <defs><linearGradient id="{gradient}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#91daf2"/><stop offset="1" stop-color="#4eb7dc"/></linearGradient></defs>
        <path d="M1.25 5V3.25A1.25 1.25 0 0 1 2.5 2h4.1l1.6 1.8h7.3a1.25 1.25 0 0 1 1.25 1.25V13a1 1 0 0 1-1 1H2.25a1 1 0 0 1-1-1Z" fill="#b4e2f1" stroke="#5ba5bf" stroke-width=".65"/>
        <rect x="1.25" y="5" width="15.5" height="9" rx="1" fill="url(#{gradient})" stroke="#4c9fbd" stroke-width=".65"/>
        <path d="M2 5.8h14" stroke="#d7f2fa" stroke-width=".6"/>
        </svg>"""
    return ui.html(svg, sanitize=False).classes('s-folder-icon').style(f'width:{size}px;height:{size}px')


CSS = """
:root { --s-ink:#243129; --s-muted:#7c847e; --s-line:#e2e6df; --s-paper:#f5f6f2; --s-green:#365f43; }
html, body { overscroll-behavior-y:none; }
body { background:var(--s-paper); color:var(--s-ink); font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif; }
.q-page { background:var(--s-paper); } .nicegui-content { padding:0; gap:0; }
.s-header { background:white; border-bottom:1px solid var(--s-line); padding:16px 26px; min-height:72px; }
.s-brand { font-size:19px; letter-spacing:-.5px; font-weight:750; }
.s-nav { color:var(--s-muted); text-decoration:none; font-size:14px; padding:8px 14px; border-radius:8px; }
.s-nav.active { background:#edf2e9; color:var(--s-green); font-weight:650; }
.s-intro { padding:26px 26px 20px; } .s-title { font-size:28px; font-weight:650; letter-spacing:-.7px; }
.s-muted { color:var(--s-muted); } .s-caption { font-size:10px; font-weight:700; letter-spacing:1.2px; color:var(--s-muted); }
.s-layout { display:grid; grid-template-columns:270px minmax(340px,1fr) 280px; gap:16px; padding:0 26px 26px; width:100%; align-items:start; }
.s-panel { background:white; border:1px solid var(--s-line); border-radius:12px; overflow:hidden; min-width:0; }
.s-panel-head { padding:17px 18px; border-bottom:1px solid var(--s-line); }
.s-volumes { max-height:calc(100vh - 330px); overflow-y:auto; }
.s-volume-group { padding:6px 8px 3px; font-size:11px; font-weight:650; color:#687466; gap:7px; }
.s-volume-row { width:100%; min-height:46px; padding:4px 9px; border:1px solid transparent; border-radius:6px; }
.s-volume-row.with-channel { height:64px; min-height:64px; }
.s-volume-row .q-btn__content { width:100%; flex-wrap:nowrap; justify-content:flex-start; gap:8px; }
.s-volume-row:hover { background:#f6f8f2; } .s-volume-row.chosen { border-color:#b7c8b0; background:#edf3e7; }
.s-volume-name { min-width:0; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; text-align:left; font-size:13px; font-weight:500; line-height:22px; }
.s-volume-role { flex-shrink:0; max-width:64px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#4e7149; background:#eef3e9; border-radius:4px; padding:0 4px; font-size:10px; line-height:15px; }
.s-volume-removable { color:#536a89; background:#edf1f7; }
.s-volume-channel { width:100%; text-align:left; font-size:11px; line-height:15px; font-weight:400; color:#63716a; }
.s-volume-capacity { width:100%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; text-align:left; font-size:10px; color:var(--s-muted); line-height:16px; font-weight:400; }
.s-volume-archive { border-top:1px solid var(--s-line); }
.s-volume-archive > .q-expansion-item__container > .q-item { min-height:38px; padding:6px 16px; font-size:12px; color:#687466; }
.s-volume-archive .q-item__section--avatar { min-width:25px; padding-right:7px; }
.s-volume-archive .q-item__section--avatar .q-icon { font-size:17px; }
.s-archive-volumes { max-height:230px; overflow-y:auto; }
.s-volume-status { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
.s-tag { font-size:11px; padding:3px 7px; border-radius:5px; line-height:1.4; background:#f0f1ed; color:#747b72; white-space:normal; }
.s-tag.purpose { color:#536a89; background:#edf1f7; } .s-tag.role { color:#3f6744; background:#eaf2e6; }
.s-tag.flag { color:#9b7435; background:#fbf3df; }
.s-path { overflow-wrap:anywhere; font-family:ui-monospace,Menlo,monospace; font-size:11px; }
.s-tree-toolbar { min-height:28px; padding:2px 10px; gap:8px; }
.s-tree { max-height:calc(100vh - 285px); min-height:320px; overflow:auto; padding:0; }
.s-list-grid { display:grid; grid-template-columns:minmax(220px,1fr) 132px 66px 72px; width:100%; min-width:520px; align-items:center; }
.s-tree-heading { height:25px; min-height:25px; position:sticky; top:0; z-index:2; background:#fff; border-bottom:1px solid #d9dddf; color:#7e8589; font-size:11px; line-height:20px; }
.s-tree-heading > div { padding:0 8px; border-right:1px solid #e2e5e7; overflow:hidden; white-space:nowrap; }
.s-tree-heading > div:first-child { padding-left:40px; }
.s-tree-heading > div:last-child { border-right:0; }
.s-entry { height:22px; min-height:22px; background:#fff; }
.s-entry.alt { background:#f3f4f5; }
.s-entry:hover { background:#edf2f6; }
.s-entry.selected, .s-entry.selected:hover { background:#dce9f8; }
.s-name-cell { min-width:0; height:22px; flex-wrap:nowrap; align-items:center; gap:3px; padding-right:6px; }
.s-folder-icon { flex:0 0 auto; display:flex; align-items:center; justify-content:center; line-height:0; }
.s-tree-toggle.q-btn { width:16px; min-width:16px; height:20px; min-height:20px; padding:0; border-radius:2px; flex-shrink:0; }
.s-tree-toggle .q-icon { font-size:14px; }
.s-tree-spacer { width:16px; flex-shrink:0; }
.s-entry-name.q-btn { flex:1; min-width:0; min-height:20px; height:20px; padding:0 2px; border-radius:2px; font-size:12px; line-height:18px; font-weight:400; color:#263129; text-align:left; }
.s-entry-name .q-btn__content { width:100%; min-width:0; flex-wrap:nowrap; justify-content:flex-start; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.s-entry-name .block { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.s-entry-name .q-focus-helper { display:none; }
.s-entry-name:focus-visible { outline:1px solid #9cb8d5; outline-offset:-1px; }
.s-tree-role { flex-shrink:0; max-width:48px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#597456; background:#e9eee5; border-radius:3px; padding:0 4px; font-size:10px; line-height:14px; }
.s-entry-cell { min-width:0; padding:0 8px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#85898d; font-size:11px; line-height:20px; }
.s-entry-size { text-align:right; }
.s-note { background:#f6f7f3; border-radius:8px; padding:11px 12px; font-size:12px; color:#6b776a; line-height:1.5; }
.s-error { background:#fff5e9; color:#9b6725; border-radius:8px; padding:10px 12px; font-size:12px; }
.q-btn { box-shadow:none !important; border-radius:7px; } .s-divider { width:100%; height:1px; background:var(--s-line); margin:4px 0; }
@media(max-width:1150px) { .s-layout { grid-template-columns:270px minmax(0,1fr); } .s-properties { grid-column:2; } .s-tree { max-height:520px; } }
@media(max-width:700px) { .s-header { padding:14px 16px; flex-wrap:wrap; gap:10px; } .s-intro { padding:20px 16px 16px; } .s-layout { grid-template-columns:1fr; padding:0 16px 20px; } .s-properties { grid-column:1; } .s-volumes { max-height:290px; overflow:auto; } .s-tree { max-height:480px; } .s-header .s-readonly { display:none; } }
"""


def register_storage_page(request, format_bytes, format_date, core_url='http://127.0.0.1:18765'):
    from workspace_ui import register_workspace_page
    register_workspace_page(request, format_bytes, format_date, core_url)
