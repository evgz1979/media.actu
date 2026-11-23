"""Shared selection and presentation of copy pairs."""
from pathlib import PurePosixPath


#: Проверяет доступность привязанной папки по состоянию связи и тома.
#: Используется для выбора пары и отображения отключённых записей.
def disconnected(location):
    return not location.get('connected', True) or location.get('availability') == 'offline'


#: Выбирает копию с наименьшим номером среди доступных.
#: При недоступности всех назначений возвращает первую сохранённую связь.
def first_copy(copies):
    return min(copies, key=lambda copy: (disconnected(copy), copy['number']), default=None)


#: Проверяет принадлежность выбранного пути области на томе.
#: Сравнивает компоненты пути, включая пустой корень.
def contains_path(scope, volume_id, path):
    return scope['volume_id'] == volume_id and PurePosixPath(path).is_relative_to(scope['path'])


#: Формирует подпись источника, действующей копии или архивного назначения.
#: Для копии может дописать сохранённое предыдущее звено маршрута.
def copy_heading(scope, *, target=False, historical=False):
    label = scope['label']
    if not target:
        return f'{label} (источник копирования)'
    if historical:
        return f'Прежняя {label}'
    upstream = scope.get('upstream')
    suffix = f' · из {upstream}' if upstream else ''
    return f"{label} (копия №{scope['number']}){suffix}"
