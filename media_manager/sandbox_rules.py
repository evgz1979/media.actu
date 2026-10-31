"""Narrow macOS sandbox exceptions for explicit disk writes."""
import json
import re


def marker_write_rules(root='/Volumes'):
    marker = '^' + re.escape(root.rstrip('/')).replace(r'\-', '-') + '/[^/]+/[.]media-actu-volume[.]json$'
    return ('(allow file-write-create file-write-data file-write-unlink (regex #'
            + json.dumps(marker) + '))')


def folder_marker_write_rules(root='/Volumes'):
    marker = '^' + re.escape(root.rstrip('/')).replace(r'\-', '-') + '/[^/]+/.+/[.]media-actu-folder[.]json$'
    return ('(allow file-write-create file-write-data file-write-unlink (regex #'
            + json.dumps(marker) + '))')


def copy_write_rules(root='/Volumes'):
    root = root.rstrip('/')
    temporary = '^' + re.escape(root).replace(r'\-', '-') + '/.*/[.]media-actu-copy-[a-f0-9]+-[a-f0-9]+[.]part$'
    return ('(allow file-write-create (subpath ' + json.dumps(root) + ')) '
            '(allow file-write* (regex #' + json.dumps(temporary) + '))')
