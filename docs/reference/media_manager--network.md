# Обнаружение NAS: `media_manager/network.py`

Bonjour через dns-sd, перечисление SMB-ресурсов через smbutil и запоминание серверов. Finder подключает ресурс по отдельной команде, пароли здесь не хранятся.

[Исходный модуль](../../media_manager/network.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_network.py](../../tests/test_network.py#L10).

## Оглавление определений

- [NetworkError](#symbol-networkerror) — Обозначает ошибку проверки адреса, обнаружения сервера или чтения SMB-ресурсов.
- [validate_host](#symbol-validate-host) — Проверяет допустимость имени сервера перед передачей системным командам.
- [validate_share](#symbol-validate-share) — Проверяет имя SMB-ресурса и исключает управляющие символы и разделители.
- [parse_browse](#symbol-parse-browse) — Разбирает вывод Bonjour в список экземпляров серверов SMB.
- [parse_resolve](#symbol-parse-resolve) — Извлекает адрес и порт из ответа разрешения Bonjour.
- [parse_shares](#symbol-parse-shares) — Разбирает список дисковых SMB-ресурсов, исключая служебные записи.
- [run](#symbol-run) — Исполняет сетевую системную команду с тайм-аутом и нормализацией ошибок.
- [discover_servers](#symbol-discover-servers) — Обнаруживает серверы SMB и параллельно разрешает их адреса.
- [discover_servers.resolve](#symbol-discover-servers-resolve) — Разрешает один Bonjour-экземпляр в адрес, порт и отображаемое имя сервера.
- [list_server_shares](#symbol-list-server-shares) — Запрашивает ресурсы сервера через существующий доступ macOS.
- [NetworkCatalog](#symbol-networkcatalog) — Хранит серверы и ресурсы NAS и связывает их с известными томами.
- [NetworkCatalog.__init__](#symbol-networkcatalog---init--) — Инициализирует NetworkCatalog и его рабочее состояние.
- [NetworkCatalog.servers](#symbol-networkcatalog-servers) — Возвращает запомненные серверы и результат последнего обнаружения.
- [NetworkCatalog.server](#symbol-networkcatalog-server) — Возвращает сервер по ID либо поднимает KeyError.
- [NetworkCatalog.scan](#symbol-networkcatalog-scan) — Обновляет обнаруженные серверы, сохраняя известные записи при ошибках.
- [NetworkCatalog.shares](#symbol-networkcatalog-shares) — Возвращает кэш ресурсов сервера или запрашивает обновление.
- [NetworkCatalog.remember](#symbol-networkcatalog-remember) — Запоминает выбранный SMB-ресурс в каталоге томов.
- [NetworkCatalog.open_in_finder](#symbol-networkcatalog-open-in-finder) — Открывает сохранённый сетевой адрес в Finder для подключения ресурса.

<a id="symbol-networkerror"></a>

## `NetworkError`

[media_manager/network.py:16](../../media_manager/network.py#L16)

Обозначает ошибку проверки адреса, обнаружения сервера или чтения SMB-ресурсов. Базовые типы: RuntimeError.

Базовые классы: `RuntimeError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-validate-host"></a>

## `validate_host`

[media_manager/network.py:22](../../media_manager/network.py#L22)

Проверяет допустимость имени сервера перед передачей системным командам. Явно отклоняет недопустимое состояние через NetworkError.

```python
def validate_host(host: str) -> str
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `host.rstrip`, `host.rstrip('.').lower`, `len`, `re.fullmatch`.

Явные `raise`:

- `NetworkError('Некорректный адрес NAS')`

Выражения возврата (ветви, без исполнения):

- `host`


<a id="symbol-validate-share"></a>

## `validate_share`

[media_manager/network.py:31](../../media_manager/network.py#L31)

Проверяет имя SMB-ресурса и исключает управляющие символы и разделители. Явно отклоняет недопустимое состояние через NetworkError.

```python
def validate_share(name: str) -> str
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `any`, `len`, `ord`.

Явные `raise`:

- `NetworkError('Некорректное имя сетевого ресурса')`

Выражения возврата (ветви, без исполнения):

- `name`


<a id="symbol-parse-browse"></a>

## `parse_browse`

[media_manager/network.py:39](../../media_manager/network.py#L39)

Разбирает вывод Bonjour в список экземпляров серверов SMB. Использует instances.pop, instances.values, match.groups, output.splitlines, re.match.

```python
def parse_browse(output: str) -> list[dict]
```

Прямые выражения вызова: `instances.pop`, `instances.values`, `list`, `match.groups`, `output.splitlines`, `re.match`, `unique.values`.

Выражения возврата (ветви, без исполнения):

- `list(unique.values())`


<a id="symbol-parse-resolve"></a>

## `parse_resolve`

[media_manager/network.py:57](../../media_manager/network.py#L57)

Извлекает адрес и порт из ответа разрешения Bonjour. Явно отклоняет недопустимое состояние через NetworkError.

```python
def parse_resolve(output: str) -> tuple[str, int]
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `int`, `match.groups`, `re.search`, [validate_host](../../media_manager/network.py#L22).

Явные `raise`:

- `NetworkError('Сервер объявлен в сети, но его адрес пока не получен')`
- `NetworkError('В этой версии поддерживается стандартный порт SMB 445')`

Выражения возврата (ветви, без исполнения):

- `(validate_host(host), int(port))`


<a id="symbol-parse-shares"></a>

## `parse_shares`

[media_manager/network.py:69](../../media_manager/network.py#L69)

Разбирает список дисковых SMB-ресурсов, исключая служебные записи. Явно отклоняет недопустимое состояние через NetworkError.

```python
def parse_shares(output: str) -> list[dict]
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `comment.strip`, `line.startswith`, `line.strip`, `match.groups`, `output.splitlines`, `re.fullmatch`, `re.match`, `shares.append`, [validate_share](../../media_manager/network.py#L31).

Явные `raise`:

- `NetworkError('Не удалось разобрать список ресурсов NAS')`
- `NetworkError('NAS не вернул полный список ресурсов')`

Выражения возврата (ветви, без исполнения):

- `shares`


<a id="symbol-run"></a>

## `run`

[media_manager/network.py:95](../../media_manager/network.py#L95)

Исполняет сетевую системную команду с тайм-аутом и нормализацией ошибок. Явно отклоняет недопустимое состояние через NetworkError.

```python
def run(command: list[str], timeout: int) -> str
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `subprocess.run`.

Явные `raise`:

- `NetworkError('NAS не ответил вовремя; сохранённые сведения оставлены')`
- `NetworkError('Не удалось запустить штатное средство macOS для поиска NAS')`
- `NetworkError('Не удалось получить сведения NAS без запроса пароля. Подключись к нему через Finder на M4 и повтори.')`

Перехватываемые типы: `subprocess.TimeoutExpired`, `OSError`.

Выражения возврата (ветви, без исполнения):

- `result.stdout`


<a id="symbol-discover-servers"></a>

## `discover_servers`

[media_manager/network.py:110](../../media_manager/network.py#L110)

Обнаруживает серверы SMB и параллельно разрешает их адреса. Явно отклоняет недопустимое состояние через NetworkError.

```python
def discover_servers() -> list[dict]
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `ThreadPoolExecutor`, `len`, `list`, `min`, [parse_browse](../../media_manager/network.py#L39), `pool.map`, [run](../../media_manager/network.py#L95), `servers.get`, `servers.values`, `set`, `sorted`.

Явные `raise`:

- `NetworkError('Найдено больше 32 SMB-серверов; поиск нужно сузить')`
- `NetworkError('Найдены объявления SMB, но адреса серверов не получены. Попробуй поиск ещё раз.')`

Выражения возврата (ветви, без исполнения):

- `list(servers.values())`


<a id="symbol-discover-servers-resolve"></a>

## `discover_servers.resolve`

[media_manager/network.py:118](../../media_manager/network.py#L118)

Разрешает один Bonjour-экземпляр в адрес, порт и отображаемое имя сервера. Поля результата: id, name, host, port, aliases.

```python
def resolve(instance)
```

Прямые выражения вызова: `any`, `f"{instance['name']}._smb._tcp.{instance['domain']}".rstrip`, `f"{instance['name']}._smb._tcp.{instance['domain']}".rstrip('.').lower`, `instance['name'].startswith`, `ord`, [parse_resolve](../../media_manager/network.py#L57), [run](../../media_manager/network.py#L95), `volume_key`.

Перехватываемые типы: `NetworkError`.

Выражения возврата (ветви, без исполнения):

- `None`
- `{'id': volume_key(f'nas:{host}:{port}'), 'name': instance['name'], 'host': host, 'port': port, 'aliases': [host, alias]}`


<a id="symbol-list-server-shares"></a>

## `list_server_shares`

[media_manager/network.py:147](../../media_manager/network.py#L147)

Запрашивает ресурсы сервера через существующий доступ macOS. Использует parse_shares, run, validate_host.

```python
def list_server_shares(server: dict) -> list[dict]
```

Прямые выражения вызова: [parse_shares](../../media_manager/network.py#L69), [run](../../media_manager/network.py#L95), [validate_host](../../media_manager/network.py#L22).

Выражения возврата (ветви, без исполнения):

- `parse_shares(run(['/usr/bin/smbutil', 'view', '-N', f'//{host}'], 12))`


<a id="symbol-networkcatalog"></a>

## `NetworkCatalog`

[media_manager/network.py:154](../../media_manager/network.py#L154)

Хранит серверы и ресурсы NAS и связывает их с известными томами. Зависимости конструктора: storage, discover, list_shares.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_scan_lock`, `_shares_lock`, `discover`, `list_shares`, `storage`.

Именованные методы: `__init__`, `servers`, `server`, `scan`, `shares`, `remember`, `open_in_finder`.

<a id="symbol-networkcatalog---init--"></a>

## `NetworkCatalog.__init__`

[media_manager/network.py:157](../../media_manager/network.py#L157)

Инициализирует NetworkCatalog и его рабочее состояние. Изменяет SQLite-таблицы: network_servers, network_shares.

```python
def __init__(self, storage, discover=discover_servers, list_shares=list_server_shares)
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `network_servers`, `network_shares`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_scan_lock`, `_shares_lock`, `discover`, `list_shares`, `storage`.

Прямые выражения вызова: `db.executescript`, `storage.connect`, `threading.Lock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-networkcatalog-servers"></a>

## `NetworkCatalog.servers`

[media_manager/network.py:179](../../media_manager/network.py#L179)

Возвращает запомненные серверы и результат последнего обнаружения. Поля результата: servers.

```python
def servers(self) -> dict
```

SQLite: чтение `network_servers`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `dict`, `json.loads`, `self.storage.connect`.

Выражения возврата (ветви, без исполнения):

- `{'servers': rows}`


<a id="symbol-networkcatalog-server"></a>

## `NetworkCatalog.server`

[media_manager/network.py:188](../../media_manager/network.py#L188)

Возвращает сервер по ID либо поднимает KeyError. Явно отклоняет недопустимое состояние через KeyError.

```python
def server(self, server_id: str) -> dict
```

Прямые выражения вызова: `KeyError`, `next`, [self.servers](../../media_manager/network.py#L179).

Явные `raise`:

- `KeyError('NAS не найден')`

Выражения возврата (ветви, без исполнения):

- `server`


<a id="symbol-networkcatalog-scan"></a>

## `NetworkCatalog.scan`

[media_manager/network.py:196](../../media_manager/network.py#L196)

Обновляет обнаруженные серверы, сохраняя известные записи при ошибках. Изменяет SQLite-таблицы: network_servers.

```python
def scan(self) -> dict
```

SQLite: чтение `network_servers`; запись/DDL `network_servers`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT aliases FROM network_servers WHERE id=?', (server['id'],)).fetchone`, `json.dumps`, `json.loads`, `now`, `self._scan_lock.acquire`, `self._scan_lock.release`, `self.discover`, [self.servers](../../media_manager/network.py#L179), `self.storage.connect`, `set`, `sorted`, `str`.

Перехватываемые типы: `NetworkError`.

Выражения возврата (ветви, без исполнения):

- `{**self.servers(), 'error': 'Поиск NAS уже выполняется', 'scanning': True}`
- `{**self.servers(), 'error': str(error)}`
- `{**self.servers(), 'error': None}`


<a id="symbol-networkcatalog-shares"></a>

## `NetworkCatalog.shares`

[media_manager/network.py:222](../../media_manager/network.py#L222)

Возвращает кэш ресурсов сервера или запрашивает обновление. Изменяет SQLite-таблицы: network_servers, network_shares.

```python
def shares(self, server_id: str, refresh: bool=False) -> dict
```

SQLite: чтение `network_shares`; запись/DDL `network_servers`, `network_shares`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `bool`, `db.execute`, `dict`, `now`, `self.list_shares`, [self.server](../../media_manager/network.py#L188), `self.storage.connect`, `self.storage.find_network_volume`, `str`.

Перехватываемые типы: `NetworkError`.

Выражения возврата (ветви, без исполнения):

- `{'server': server, 'shares': rows, 'error': error, 'cached': not refresh or bool(error)}`


<a id="symbol-networkcatalog-remember"></a>

## `NetworkCatalog.remember`

[media_manager/network.py:254](../../media_manager/network.py#L254)

Запоминает выбранный SMB-ресурс в каталоге томов. Явно отклоняет недопустимое состояние через KeyError.

```python
def remember(self, server_id: str, name: str) -> dict
```

Прямые выражения вызова: `KeyError`, `any`, [self.server](../../media_manager/network.py#L188), [self.shares](../../media_manager/network.py#L222), `self.storage.remember_network_volume`, [validate_share](../../media_manager/network.py#L31).

Явные `raise`:

- `KeyError('Ресурс не найден в сохранённом списке NAS')`

Выражения возврата (ветви, без исполнения):

- `self.storage.remember_network_volume(server['host'], server['aliases'], name)`


<a id="symbol-networkcatalog-open-in-finder"></a>

## `NetworkCatalog.open_in_finder`

[media_manager/network.py:263](../../media_manager/network.py#L263)

Открывает сохранённый сетевой адрес в Finder для подключения ресурса. Явно отклоняет недопустимое состояние через NetworkError, ValueError.

```python
def open_in_finder(self, volume_id: str) -> dict
```

Прямые выражения вызова: [NetworkError](../../media_manager/network.py#L16), `ValueError`, `self.storage.get_volume`, `subprocess.run`, `urlsplit`, [validate_host](../../media_manager/network.py#L22), `volume.get`.

Явные `raise`:

- `NetworkError('У этого тома нет адреса SMB. Сначала выбери его в поиске NAS.')`
- `ValueError('port')`
- `NetworkError('Некорректный порт SMB')`
- `NetworkError('Не удалось открыть подключение в Finder на M4')`

Перехватываемые типы: `ValueError`, `(OSError, subprocess.SubprocessError)`.

Выражения возврата (ветви, без исполнения):

- `{'url': url, 'status': 'finder_opened'}`
