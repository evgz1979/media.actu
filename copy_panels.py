"""Shared selection and presentation of copy pairs."""


#: Проверяет доступность привязанной папки по состоянию связи и тома.
#: Используется для выбора пары и отображения отключённых записей.
def disconnected(location):
    return not location.get('connected', True) or location.get('availability') == 'offline'


#: Выбирает копию с наименьшим номером среди доступных.
#: При недоступности всех назначений возвращает первую сохранённую связь.
def first_copy(copies):
    return min(copies, key=lambda copy: (disconnected(copy), copy['number']), default=None)


#: Поднимается от выбранной копии к корню по сохранённым ссылкам.
#: Возвращает путь и признак цикла, отмечает отсутствующий источник без подстановки корня.
def _copy_ancestry(root, copies, target, parent_key):
    by_id = {copy['id']: copy for copy in copies}
    by_id[root['id']] = root
    nodes = [target]
    seen = {target['id']}
    cycle = False
    while nodes[-1]['id'] != root['id']:
        parent_id = nodes[-1].get(parent_key)
        if parent_id in (None, ''):
            nodes.append(root)
            break
        parent = by_id.get(parent_id)
        cycle = parent_id in seen
        if parent is None or cycle:
            nodes.append(dict(label='Недоступный источник'))
            break
        nodes.append(parent)
        seen.add(parent_id)
    return list(reversed(nodes)), cycle


#: Возвращает фактический источник выбранной копии, учитывая тип хранимой ссылки.
#: При отсутствующем непосредственном источнике или цикле возвращает None.
def copy_upstream(root, copies, target, *, parent_key):
    if parent_key is None:
        return root
    nodes, cycle = _copy_ancestry(root, copies, target, parent_key)
    if len(nodes) > 1 and not cycle and 'id' in nodes[-2]:
        return nodes[-2]
    return None


#: Строит маршрут через выбранную копию по фактическим связям источников.
#: По умолчанию продолжает маршрут первой доступной копией каждого следующего звена.
def copy_route(root, copies, target, *, parent_key, downstream=True):
    if parent_key is None:
        return root, target
    copies = tuple(copies)
    nodes, _ = _copy_ancestry(root, copies, target, parent_key)
    if not downstream:
        return tuple(nodes)
    seen = {node['id'] for node in nodes if 'id' in node}
    while True:
        current_id = nodes[-1]['id']
        child = first_copy(copy for copy in copies if copy['id'] not in seen and copy.get(parent_key) == current_id)
        if child is None:
            return tuple(nodes)
        nodes.append(child)
        seen.add(child['id'])


#: Формирует подпись источника, действующей копии или архивного назначения.
#: Заголовок показывает роль относительно выбранного перехода.
def copy_heading(scope, *, target=False, historical=False):
    label = scope['label']
    if not target:
        return f'{label} (источник копирования)'
    if historical:
        return f'Прежняя {label}'
    return f"{label} (копия №{scope['number']})"
