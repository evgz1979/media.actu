"""Additional macOS sandbox rules for exclusive creation of missing copies."""
import json
import re


def copy_write_rules(root='/Volumes'):
    root = root.rstrip('/')
    temporary = '^' + re.escape(root).replace(r'\-', '-') + '/.*/[.]media-actu-copy-[a-f0-9]+-[a-f0-9]+[.]part$'
    return ('(allow file-write-create (subpath ' + json.dumps(root) + ')) '
            '(allow file-write* (regex #' + json.dumps(temporary) + '))')
