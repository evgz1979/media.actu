"""Small, per-tab navigation snapshots; file lists and file contents stay on Core."""
import re

from media_manager.storage import relative_path


STORAGE_KEY = 'media-actu.workspace.v1'


def identifier(value):
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
        raise ValueError('Некорректный ID в сохранённом состоянии')
    return value


def path(value):
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError('Некорректный путь в сохранённом состоянии')
    return relative_path(value)


def pane_snapshot(pane):
    data = pane if isinstance(pane, dict) else vars(pane)
    hidden = data.get('hidden', False)
    return dict(volume_id=data.get('volume_id'), root_path=data.get('root_path', ''),
                path=data.get('path', ''), kind=data.get('kind', 'directory'),
                hidden=hidden if isinstance(hidden, bool) else bool(hidden.value))


def normalize_state(value):
    try:
        if not isinstance(value, dict) or value.get('version') != 1:
            return None
        result = dict(version=1, active=1 if value.get('active') == 1 else 0)
        for key in ('panes', 'browse'):
            panes = value.get(key)
            if panes is None and key == 'browse':
                continue
            if not isinstance(panes, list) or len(panes) != 2:
                return None
            result[key] = [dict(volume_id=identifier(p['volume_id']), root_path=path(p.get('root_path', '')),
                                path=path(p.get('path', '')), kind='directory' if p.get('kind') == 'directory' else 'file',
                                hidden=bool(p.get('hidden'))) for p in panes]
        result['job_id'] = identifier(value.get('job_id'))
        result['target_focus'] = bool(value.get('target_focus'))
        if isinstance(pair := value.get('pair'), dict):
            expanded = pair.get('expanded')
            if expanded is not None and not isinstance(expanded, list):
                return None
            result['pair'] = dict(copy_id=identifier(pair['copy_id']), job_id=identifier(pair.get('job_id')),
                                  root=path(pair.get('root', '')), selected=path(pair.get('selected', '')),
                                  differences_only=bool(pair.get('differences_only')), hidden=bool(pair.get('hidden')),
                                  root_files_open=bool(pair.get('root_files_open')),
                                  expanded=[path(p) for p in expanded[:2000]] if expanded is not None else None)
            if isinstance(pending := pair.get('pending'), dict):
                result['pair']['pending'] = dict(since=str(pending['since'])[:40], mode=pending['mode'], method=pending['method'])
        return result
    except (KeyError, TypeError, ValueError, AttributeError):
        return None
