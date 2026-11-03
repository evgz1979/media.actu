"""Narrow macOS sandbox exceptions for explicit disk writes."""
import json
import re


# Формирует правило записи служебного маркера в корне носителя.
# Использует json.dumps, re.escape, re.escape(root.rstrip('/')).replace, root.rstrip.
def marker_write_rules(root='/Volumes'):
    marker = '^' + re.escape(root.rstrip('/')).replace(r'\-', '-') + '/[^/]+/[.]media-actu-volume[.]json$'
    return ('(allow file-write-create file-write-data file-write-unlink (regex #'
            + json.dumps(marker) + '))')


# Формирует правило записи служебного описания внутри зарегистрированной папки.
# Использует json.dumps, re.escape, re.escape(root.rstrip('/')).replace, root.rstrip.
def folder_marker_write_rules(root='/Volumes'):
    marker = '^' + re.escape(root.rstrip('/')).replace(r'\-', '-') + '/[^/]+/.+/[.]media-actu-folder[.]json$'
    return ('(allow file-write-create file-write-data file-write-unlink (regex #'
            + json.dumps(marker) + '))')


# Формирует правила создания новых копий и собственных временных файлов.
# Использует json.dumps, re.escape, re.escape(root).replace, root.rstrip.
def copy_write_rules(root='/Volumes'):
    root = root.rstrip('/')
    temporary = '^' + re.escape(root).replace(r'\-', '-') + '/.*/[.]media-actu-copy-[a-f0-9]+-[a-f0-9]+[.]part$'
    return ('(allow file-write-create (subpath ' + json.dumps(root) + ')) '
            '(allow file-write* (regex #' + json.dumps(temporary) + '))')
