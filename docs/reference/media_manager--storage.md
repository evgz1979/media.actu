# Тома и снимки каталогов: `media_manager/storage.py`

Обнаруживает смонтированные тома macOS, поддерживает их устойчивую идентичность, снимки каталогов и пользовательские отметки в storage.sqlite3.

[Исходный модуль](../../media_manager/storage.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/copies.py](media_manager--copies.md), [media_manager/volume_identity.py](media_manager--volume_identity.md).
Импортируется модулями: [app.py](app.md), [media_manager/comparison.py](media_manager--comparison.md), [media_manager/copy_files.py](media_manager--copy_files.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [media_manager/network.py](media_manager--network.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/photo_libraries.py](media_manager--photo_libraries.md), [media_manager/photos_browser.py](media_manager--photos_browser.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [storage_preview_ui.py](storage_preview_ui.md), [workspace_state.py](workspace_state.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_comparison.py](../../tests/test_comparison.py#L13), [tests/test_copies.py](../../tests/test_copies.py#L7), [tests/test_copy_connections.py](../../tests/test_copy_connections.py#L13), [tests/test_copy_files.py](../../tests/test_copy_files.py#L14), [tests/test_copy_number_release.py](../../tests/test_copy_number_release.py#L15), [tests/test_directory_sizes.py](../../tests/test_directory_sizes.py#L13), [tests/test_folder_markers.py](../../tests/test_folder_markers.py#L16), [tests/test_folder_tags.py](../../tests/test_folder_tags.py#L8), [tests/test_folder_tracking.py](../../tests/test_folder_tracking.py#L14), [tests/test_network.py](../../tests/test_network.py#L14), [tests/test_paired_comparison.py](../../tests/test_paired_comparison.py#L11), [tests/test_photo_libraries.py](../../tests/test_photo_libraries.py#L11), [tests/test_photos_browser.py](../../tests/test_photos_browser.py#L9), [tests/test_photos_originals.py](../../tests/test_photos_originals.py#L9), [tests/test_refresh_renamed_folder.py](../../tests/test_refresh_renamed_folder.py#L8), [tests/test_storage.py](../../tests/test_storage.py#L11), [tests/test_storage_previews.py](../../tests/test_storage_previews.py#L15), [tests/test_volume_identity.py](../../tests/test_volume_identity.py#L16).

## Оглавление определений

- [now](#symbol-now) — Возвращает текущее время UTC в формате ISO 8601.
- [relative_path](#symbol-relative-path) — Проверяет и нормализует путь относительно корня выбранного тома.
- [volume_key](#symbol-volume-key) — Получает короткий стабильный ID из строки идентичности тома.
- [discover_volumes](#symbol-discover-volumes) — Читает существующие монтирования macOS и собирает доступные тома.
- [_inspect_volume](#symbol--inspect-volume) — Определяет идентичность, тип, ресурс NAS и ёмкость одного тома.
- [StorageCatalog](#symbol-storagecatalog) — Хранит зарегистрированные тома, снимки папок и пользовательские отметки.
- [StorageCatalog.__init__](#symbol-storagecatalog---init--) — Инициализирует StorageCatalog и его рабочее состояние.
- [StorageCatalog.connect](#symbol-storagecatalog-connect) — Предоставляет транзакционное соединение storage.sqlite3 с гарантированным закрытием.
- [StorageCatalog.refresh](#symbol-storagecatalog-refresh) — Обновляет обнаруженные тома либо возвращает их сохранённое состояние.
- [StorageCatalog._volume_details](#symbol-storagecatalog--volume-details) — Дополняет запись тома сохранёнными сведениями об идентичности.
- [StorageCatalog.register_removable](#symbol-storagecatalog-register-removable) — Создаёт служебный ID сменного носителя и повторно обнаруживает тома.
- [StorageCatalog.rename_removable](#symbol-storagecatalog-rename-removable) — Переименовывает зарегистрированный носитель через его служебный маркер.
- [StorageCatalog.volume_group](#symbol-storagecatalog-volume-group) — Определяет группу отображения тома по типу и сведениям о NAS.
- [StorageCatalog.network_keys](#symbol-storagecatalog-network-keys) — Строит возможные ID ресурса по основному адресу и псевдонимам сервера.
- [StorageCatalog.find_network_volume](#symbol-storagecatalog-find-network-volume) — Ищет ранее известный сетевой том по адресам и имени ресурса.
- [StorageCatalog.remember_network_volume](#symbol-storagecatalog-remember-network-volume) — Запоминает SMB-ресурс и его псевдонимы без монтирования.
- [StorageCatalog.get_volume](#symbol-storagecatalog-get-volume) — Возвращает известный том с сохранёнными сведениями либо поднимает KeyError.
- [StorageCatalog.open_in_finder](#symbol-storagecatalog-open-in-finder) — Проверяет выбранный путь и передаёт его Finder на машине Core.
- [StorageCatalog.metadata](#symbol-storagecatalog-metadata) — Возвращает наследуемые отметки и роль папки из каталога.
- [StorageCatalog._tags](#symbol-storagecatalog--tags) — Читает пользовательские метки папок одного тома.
- [StorageCatalog.set_folder_tags](#symbol-storagecatalog-set-folder-tags) — Сохраняет проверенный набор меток для выбранной папки.
- [StorageCatalog._metadata](#symbol-storagecatalog--metadata) — Вычисляет наследование назначения, роли и флагов от родительских папок.
- [StorageCatalog.annotate](#symbol-storagecatalog-annotate) — Сохраняет назначение, прежнюю роль, флаги и комментарий расположения.
- [StorageCatalog._snapshot](#symbol-storagecatalog--snapshot) — Читает сохранённый список одной папки без обращения к носителю.
- [StorageCatalog.directory](#symbol-storagecatalog-directory) — Возвращает живой список папки или снимок с явной отметкой кэша.
- [StorageCatalog._read_directory](#symbol-storagecatalog--read-directory) — Перечисляет один каталог через проверенный дескриптор тома.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [PURPOSES](../../media_manager/storage.py#L28) | `{'': 'Не назначено', 'media': 'Медиа', 'documents': 'Документы', 'projects': 'Проекты', 'mixed': 'Разные данные'}` |
| [ROLES](../../media_manager/storage.py#L29) | `{'': 'Не назначено', 'primary': 'Основное хранение', 'copy': 'Вторая копия', 'archive': 'Архив', 'temporary': 'Временное'}` |
| [FLAGS](../../media_manager/storage.py#L30) | `{'no_duplicate': 'Не дублировать', 'planned_move': 'Планируется перенос'}` |
| [FOLDER_TAGS](../../media_manager/storage.py#L31) | `{'old_copy': 'старая копия', 'sort': 'разобрать', 'check': 'проверить'}` |

<a id="symbol-now"></a>

## `now`

[media_manager/storage.py:36](../../media_manager/storage.py#L36)

Возвращает текущее время UTC в формате ISO 8601. Использует datetime.now, datetime.now(timezone.utc).isoformat.

```python
def now() -> str
```

Прямые выражения вызова: `datetime.now`, `datetime.now(timezone.utc).isoformat`.

Выражения возврата (ветви, без исполнения):

- `datetime.now(timezone.utc).isoformat()`


<a id="symbol-relative-path"></a>

## `relative_path`

[media_manager/storage.py:42](../../media_manager/storage.py#L42)

Проверяет и нормализует путь относительно корня выбранного тома. Явно отклоняет недопустимое состояние через ValueError.

```python
def relative_path(value: str) -> str
```

Прямые выражения вызова: `PurePosixPath`, `ValueError`, `str`, `value.split`, `value.startswith`.

Явные `raise`:

- `ValueError('Нужен путь внутри выбранного тома')`

Выражения возврата (ветви, без исполнения):

- `'' if path == '.' else path`


<a id="symbol-volume-key"></a>

## `volume_key`

[media_manager/storage.py:51](../../media_manager/storage.py#L51)

Получает короткий стабильный ID из строки идентичности тома. Использует hashlib.sha256, hashlib.sha256(identity.encode()).hexdigest, identity.encode.

```python
def volume_key(identity: str) -> str
```

Прямые выражения вызова: `hashlib.sha256`, `hashlib.sha256(identity.encode()).hexdigest`, `identity.encode`.

Выражения возврата (ветви, без исполнения):

- `hashlib.sha256(identity.encode()).hexdigest()[:24]`


<a id="symbol-discover-volumes"></a>

## `discover_volumes`

[media_manager/storage.py:57](../../media_manager/storage.py#L57)

Читает существующие монтирования macOS и собирает доступные тома. Обрабатывает ошибки: (OSError, ValueError, subprocess.SubprocessError).

```python
def discover_volumes() -> list[dict[str, Any]]
```

Прямые выражения вызова: [_inspect_volume](../../media_manager/storage.py#L85), `match.groups`, `mount_path.startswith`, `options.split`, `re.match`, `re.sub`, `result.stdout.splitlines`, `subprocess.run`, `volumes.append`.

Перехватываемые типы: `(OSError, ValueError, subprocess.SubprocessError)`.

Выражения возврата (ветви, без исполнения):

- `volumes`


<a id="symbol--inspect-volume"></a>

## `_inspect_volume`

[media_manager/storage.py:85](../../media_manager/storage.py#L85)

Определяет идентичность, тип, ресурс NAS и ёмкость одного тома. Явно отклоняет недопустимое состояние через OSError.

```python
def _inspect_volume(device: str, mount_path: str, filesystem: str) -> dict[str, Any] | None
```

Прямые выражения вызова: `OSError`, `Path`, `bool`, `canonical_host`, `device.removeprefix`, `device.removeprefix('//').split`, `endpoint.casefold`, `endpoint.split`, `endpoint.split('/', 1)[0].rstrip`, `info.get`, `mounted_root`, `os.stat`, `plistlib.loads`, `quote`, `read_capacity`, `read_marker`, `share_name.casefold`, `subprocess.run`, `unquote`, `usb_share`, [volume_key](../../media_manager/storage.py#L51).

Явные `raise`:

- `OSError('identity changed')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `None`
- `volume`


<a id="symbol-storagecatalog"></a>

## `StorageCatalog`

[media_manager/storage.py:159](../../media_manager/storage.py#L159)

Хранит зарегистрированные тома, снимки папок и пользовательские отметки. Зависимости конструктора: database, discover.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_checked`, `_discovery_error`, `_lock`, `_mounted`, `database`, `discover`.

Именованные методы: `__init__`, `connect`, `refresh`, `_volume_details`, `register_removable`, `rename_removable`, `volume_group`, `network_keys`, `find_network_volume`, `remember_network_volume`, `get_volume`, `open_in_finder`, `metadata`, `_tags`, `set_folder_tags`, `_metadata`, `annotate`, `_snapshot`, `directory`, `_read_directory`.

<a id="symbol-storagecatalog---init--"></a>

## `StorageCatalog.__init__`

[media_manager/storage.py:162](../../media_manager/storage.py#L162)

Инициализирует StorageCatalog и его рабочее состояние. Изменяет SQLite-таблицы: annotations, directories, directory_tags, network_volume_links, volume_aliases, volume_capacity, volume_details, volume_origins, volumes.

```python
def __init__(self, database: Path, discover: Callable=discover_volumes) -> None
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `annotations`, `directories`, `directory_tags`, `network_volume_links`, `volume_aliases`, `volume_capacity`, `volume_details`, `volume_origins`, `volumes`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_checked`, `_discovery_error`, `_lock`, `_mounted`, `database`, `discover`.

Прямые выражения вызова: `db.execute`, `db.executescript`, [self.connect](../../media_manager/storage.py#L204), `self.database.parent.mkdir`, `threading.RLock`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagecatalog-connect"></a>

## `StorageCatalog.connect`

[media_manager/storage.py:204](../../media_manager/storage.py#L204)

Предоставляет транзакционное соединение storage.sqlite3 с гарантированным закрытием. Использует db.close, db.execute, sqlite3.connect.

```python
def connect(self)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `db.close`, `db.execute`, `sqlite3.connect`.

Передаёт управление через `yield`; ресурс и освобождение см. в теле контекстного менеджера.


<a id="symbol-storagecatalog-refresh"></a>

## `StorageCatalog.refresh`

[media_manager/storage.py:216](../../media_manager/storage.py#L216)

Обновляет обнаруженные тома либо возвращает их сохранённое состояние. cached_only не запускает обнаружение; обычный результат кэшируется на 10 секунд.

```python
def refresh(self, force: bool=False, *, cached_only: bool=False) -> dict
```

SQLite: чтение `network_servers`, `network_volume_links`, `volume_aliases`, `volume_capacity`, `volume_details`, `volume_origins`, `volumes`; запись/DDL `network_volume_links`, `volume_capacity`, `volume_details`, `volume_origins`, `volumes`. См. [схему данных](../data-model.md).

Присваивания полям `self`: `_checked`, `_discovery_error`, `_mounted`.

Прямые выражения вызова: `bool`, `capacities.get`, `db.execute`, `db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='network_servers'").fetchone`, `db.execute('SELECT volume_id FROM volume_aliases WHERE alias_id=?', (volume['id'],)).fetchone`, `details.get`, `dict`, `int`, `mounted.get`, [now](../../media_manager/storage.py#L36), `nullcontext`, `origins.get`, `row.update`, `self._mounted.get`, `self._mounted.get(row['id'], {}).get`, [self._volume_details](../../media_manager/storage.py#L287), [self.connect](../../media_manager/storage.py#L204), `self.discover`, [self.metadata](../../media_manager/storage.py#L471), [self.volume_group](../../media_manager/storage.py#L335), `str`, `sum`, `time.monotonic`, `volume.get`, `volume.update`, [volume_key](../../media_manager/storage.py#L51).

Перехватываемые типы: `(OSError, ValueError, subprocess.SubprocessError)`.

Выражения возврата (ветви, без исполнения):

- `{'volumes': rows, 'error': self._discovery_error, 'checked_at': now(), 'purposes': PURPOSES, 'roles': ROLES}`


<a id="symbol-storagecatalog--volume-details"></a>

## `StorageCatalog._volume_details`

[media_manager/storage.py:287](../../media_manager/storage.py#L287)

Дополняет запись тома сохранёнными сведениями об идентичности. Использует usb_share.

```python
def _volume_details(volume: dict, details: dict | None) -> dict
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `bool`, `dict`, `usb_share`.

Выражения возврата (ветви, без исполнения):

- `result`


<a id="symbol-storagecatalog-register-removable"></a>

## `StorageCatalog.register_removable`

[media_manager/storage.py:302](../../media_manager/storage.py#L302)

Создаёт служебный ID сменного носителя и повторно обнаруживает тома. Явно отклоняет недопустимое состояние через ValueError.

```python
def register_removable(self, volume_id: str, name: str) -> dict
```

Прямые выражения вызова: `ValueError`, `create_marker`, `next`, [self.refresh](../../media_manager/storage.py#L216), [volume_key](../../media_manager/storage.py#L51).

Явные `raise`:

- `ValueError('Носитель отключён или заменён. Обнови список томов.')`
- `ValueError('Этот том уже определён или не является сменным носителем')`
- `ValueError('Файл ID создан, но подтвердить носитель не удалось. Обнови список томов.')`

Выражения возврата (ветви, без исполнения):

- `registered`


<a id="symbol-storagecatalog-rename-removable"></a>

## `StorageCatalog.rename_removable`

[media_manager/storage.py:319](../../media_manager/storage.py#L319)

Переименовывает зарегистрированный носитель через его служебный маркер. Явно отклоняет недопустимое состояние через ValueError.

```python
def rename_removable(self, volume_id: str, name: str) -> dict
```

Прямые выражения вызова: `ValueError`, `next`, `rename_marker`, [self.refresh](../../media_manager/storage.py#L216), `volume.get`.

Явные `raise`:

- `ValueError('Диск отключён или недоступен. Подключи его и обнови список томов.')`
- `ValueError('Переименовать можно только зарегистрированный сменный диск')`
- `ValueError('Имя записано на диск, но обновить сведения не удалось. Обнови список томов.')`

Выражения возврата (ветви, без исполнения):

- `renamed`


<a id="symbol-storagecatalog-volume-group"></a>

## `StorageCatalog.volume_group`

[media_manager/storage.py:335](../../media_manager/storage.py#L335)

Определяет группу отображения тома по типу и сведениям о NAS. Поля результата: id, name, kind.

```python
def volume_group(volume: dict, origin: str | None, servers: list[dict]) -> dict
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `StorageCatalog.network_keys`, `a.rstrip`, `a.rstrip('.').casefold`, `host.rstrip`, `host.rstrip('.').casefold`, `json.loads`, `len`, `name.casefold`, `normalized.endswith`, `server['host'].rstrip`, `server['host'].rstrip('.').casefold`, `urlsplit`, `volume.get`.

Выражения возврата (ветви, без исполнения):

- `{'id': 'm4', 'name': 'M4', 'kind': 'local'}`
- `{'id': 'network-unknown', 'name': 'Сетевые тома', 'kind': 'network'}`
- `{'id': 'nas:' + server['host'].rstrip('.').casefold(), 'name': server['name'], 'kind': 'network'}`
- `{'id': 'nas:' + normalized, 'name': name, 'kind': 'network'}`


<a id="symbol-storagecatalog-network-keys"></a>

## `StorageCatalog.network_keys`

[media_manager/storage.py:365](../../media_manager/storage.py#L365)

Строит возможные ID ресурса по основному адресу и псевдонимам сервера. Использует dict.fromkeys, host.rstrip, host.rstrip('.').casefold, name.casefold, quote.

```python
def network_keys(hosts: list[str], share: str) -> list[str]
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `dict.fromkeys`, `host.rstrip`, `host.rstrip('.').casefold`, `list`, `name.casefold`, `quote`, [volume_key](../../media_manager/storage.py#L51).

Выражения возврата (ветви, без исполнения):

- `list(dict.fromkeys((volume_key(f"smbfs:{host.rstrip('.').casefold()}/{name.casefold()}") for host in hosts for name in (share, quote(share, safe='')))))`


<a id="symbol-storagecatalog-find-network-volume"></a>

## `StorageCatalog.find_network_volume`

[media_manager/storage.py:371](../../media_manager/storage.py#L371)

Ищет ранее известный сетевой том по адресам и имени ресурса. Читает SQLite-таблицы: volume_aliases, volumes.

```python
def find_network_volume(self, hosts: list[str], share: str) -> dict | None
```

SQLite: чтение `volume_aliases`, `volumes`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `(mounted.get('share_name') or '').casefold`, `canonical_host`, `db.execute`, `db.execute('SELECT * FROM volumes WHERE id=?', (alias['volume_id'] if alias else candidate,)).fetchone`, `db.execute('SELECT 1 FROM volumes WHERE id=?', (placeholder,)).fetchone`, `db.execute('SELECT volume_id FROM volume_aliases WHERE alias_id=?', (candidate,)).fetchone`, `dict`, `mounted.get`, `self._mounted.values`, [self.connect](../../media_manager/storage.py#L204), [self.get_volume](../../media_manager/storage.py#L421), [self.network_keys](../../media_manager/storage.py#L365), `share.casefold`, `usb_share`, [volume_key](../../media_manager/storage.py#L51).

Выражения возврата (ветви, без исполнения):

- `self.get_volume(mounted['id'])`
- `self.get_volume(placeholder)`
- `None`
- `dict(row)`


<a id="symbol-storagecatalog-remember-network-volume"></a>

## `StorageCatalog.remember_network_volume`

[media_manager/storage.py:394](../../media_manager/storage.py#L394)

Запоминает SMB-ресурс и его псевдонимы без монтирования. Изменяет SQLite-таблицы: network_volume_links, volume_aliases, volume_details, volumes.

```python
def remember_network_volume(self, host: str, aliases: list[str], share: str) -> dict
```

SQLite: чтение `volumes`; запись/DDL `network_volume_links`, `volume_aliases`, `volume_details`, `volumes`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `canonical_host`, `db.execute`, `db.execute('SELECT id FROM volumes WHERE id=? AND id!=?', (key, volume_id)).fetchone`, `dict.fromkeys`, `list`, [now](../../media_manager/storage.py#L36), `quote`, [self.connect](../../media_manager/storage.py#L204), [self.find_network_volume](../../media_manager/storage.py#L371), [self.get_volume](../../media_manager/storage.py#L421), [self.network_keys](../../media_manager/storage.py#L365), `share.casefold`, `usb_share`, [volume_key](../../media_manager/storage.py#L51).

Выражения возврата (ветви, без исполнения):

- `self.get_volume(volume_id)`


<a id="symbol-storagecatalog-get-volume"></a>

## `StorageCatalog.get_volume`

[media_manager/storage.py:421](../../media_manager/storage.py#L421)

Возвращает известный том с сохранёнными сведениями либо поднимает KeyError. Явно отклоняет недопустимое состояние через KeyError.

```python
def get_volume(self, volume_id: str) -> dict
```

SQLite: чтение `network_volume_links`, `volume_details`, `volumes`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `db.execute`, `db.execute('SELECT * FROM volume_details WHERE volume_id=?', (volume_id,)).fetchone`, `db.execute('SELECT v.*, l.url AS network_url FROM volumes v LEFT JOIN network_volume_links l ON l.volume_id=v.id WHERE v.id=?', (volume_id,)).fetchone`, `dict`, [self._volume_details](../../media_manager/storage.py#L287), [self.connect](../../media_manager/storage.py#L204), `volume.update`.

Явные `raise`:

- `KeyError('Том не найден')`

Выражения возврата (ветви, без исполнения):

- `volume`


<a id="symbol-storagecatalog-open-in-finder"></a>

## `StorageCatalog.open_in_finder`

[media_manager/storage.py:433](../../media_manager/storage.py#L433)

Проверяет выбранный путь и передаёт его Finder на машине Core. Явно отклоняет недопустимое состояние через KeyError, OSError, ValueError.

```python
def open_in_finder(self, volume_id: str, path: str='') -> dict
```

Прямые выражения вызова: `KeyError`, `OSError`, `Path`, `Path(volume['mount_path']).joinpath`, `PurePosixPath`, `ValueError`, `descriptors.append`, `mounted_root`, `next`, `os.close`, `os.fstat`, `os.open`, `os.stat`, [relative_path](../../media_manager/storage.py#L42), `reversed`, [self.refresh](../../media_manager/storage.py#L216), `stat.S_ISDIR`, `str`, `subprocess.run`, `verify_identity`, `volume.get`.

Явные `raise`:

- `KeyError('Том не найден')`
- `ValueError(volume.get('identity_error') or 'Том недоступен. Подключи его и повтори.')`
- `OSError('Переход на другой том запрещён')`
- `ValueError('Не удалось открыть Finder')`

Перехватываемые типы: `subprocess.SubprocessError`.

Выражения возврата (ветви, без исполнения):

- `{'path': str(target)}`


<a id="symbol-storagecatalog-metadata"></a>

## `StorageCatalog.metadata`

[media_manager/storage.py:471](../../media_manager/storage.py#L471)

Возвращает наследуемые отметки и роль папки из каталога. Поля результата: copy, tags.

```python
def metadata(self, volume_id: str, path: str) -> dict
```

SQLite: чтение `annotations`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `active_locations`, `db.execute`, `dict`, `inherited_location`, [relative_path](../../media_manager/storage.py#L42), [self._metadata](../../media_manager/storage.py#L514), [self._tags](../../media_manager/storage.py#L484), [self.connect](../../media_manager/storage.py#L204), [self.get_volume](../../media_manager/storage.py#L421), `tags.get`.

Выражения возврата (ветви, без исполнения):

- `{**self._metadata(path, annotations), 'copy': inherited_location(path, locations), 'tags': tags.get(path, [])}`


<a id="symbol-storagecatalog--tags"></a>

## `StorageCatalog._tags`

[media_manager/storage.py:484](../../media_manager/storage.py#L484)

Читает пользовательские метки папок одного тома. Читает SQLite-таблицы: directory_tags.

```python
def _tags(db, volume_id)
```

Декораторы: `staticmethod`.

SQLite: чтение `directory_tags`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `json.loads`.

Выражения возврата (ветви, без исполнения):

- `{row['path']: json.loads(row['tags']) for row in db.execute('SELECT path,tags FROM directory_tags WHERE volume_id=?', (volume_id,))}`


<a id="symbol-storagecatalog-set-folder-tags"></a>

## `StorageCatalog.set_folder_tags`

[media_manager/storage.py:490](../../media_manager/storage.py#L490)

Сохраняет проверенный набор меток для выбранной папки. Изменяет SQLite-таблицы: directory_tags.

```python
def set_folder_tags(self, volume_id: str, path: str, tags: list[str]) -> dict
```

SQLite: чтение `directory_tags`; запись/DDL `directory_tags`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `ValueError`, `any`, `db.execute`, `isinstance`, `json.dumps`, [relative_path](../../media_manager/storage.py#L42), [self._snapshot](../../media_manager/storage.py#L559), [self.connect](../../media_manager/storage.py#L204), [self.get_volume](../../media_manager/storage.py#L421), [self.metadata](../../media_manager/storage.py#L471), `str`.

Явные `raise`:

- `ValueError('Сначала зарегистрируй сменный диск')`
- `ValueError('Неизвестная ручная метка папки')`
- `ValueError('Метки можно назначать только известным каталогам')`

Выражения возврата (ветви, без исполнения):

- `self.metadata(volume_id, path)`


<a id="symbol-storagecatalog--metadata"></a>

## `StorageCatalog._metadata`

[media_manager/storage.py:514](../../media_manager/storage.py#L514)

Вычисляет наследование назначения, роли и флагов от родительских папок. Поля результата: own, effective, inherited_from.

```python
def _metadata(path: str, annotations: dict) -> dict
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `PurePosixPath`, `ancestors.append`, `annotations.get`, `annotations.get(ancestor, {}).get`, `bool`, `own.get`, [relative_path](../../media_manager/storage.py#L42), `str`.

Выражения возврата (ветви, без исполнения):

- `{'own': {key: own.get(key) for key in ('purpose', 'role', *FLAGS, 'comment')}, 'effective': effective, 'inherited_from': inherited_from}`


<a id="symbol-storagecatalog-annotate"></a>

## `StorageCatalog.annotate`

[media_manager/storage.py:533](../../media_manager/storage.py#L533)

Сохраняет назначение, прежнюю роль, флаги и комментарий расположения. Изменяет SQLite-таблицы: annotations.

```python
def annotate(self, volume_id: str, path: str, values: dict) -> dict
```

SQLite: нет статически найденных SELECT-таблиц; запись/DDL `annotations`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `PurePosixPath`, `ValueError`, `any`, `db.execute`, [relative_path](../../media_manager/storage.py#L42), [self._snapshot](../../media_manager/storage.py#L559), [self.connect](../../media_manager/storage.py#L204), [self.get_volume](../../media_manager/storage.py#L421), [self.metadata](../../media_manager/storage.py#L471), `snapshot.get`, `str`, `values.get`.

Явные `raise`:

- `ValueError('Сначала зарегистрируй сменный диск; отметки должны относиться к конкретному носителю')`
- `ValueError('Неизвестное назначение')`
- `ValueError('Неизвестная роль')`
- `ValueError('Роли можно назначать только известным каталогам')`

Выражения возврата (ветви, без исполнения):

- `self.metadata(volume_id, path)`


<a id="symbol-storagecatalog--snapshot"></a>

## `StorageCatalog._snapshot`

[media_manager/storage.py:559](../../media_manager/storage.py#L559)

Читает сохранённый список одной папки без обращения к носителю. Читает SQLite-таблицы: directories.

```python
def _snapshot(db, volume_id: str, path: str) -> dict
```

Декораторы: `staticmethod`.

SQLite: чтение `directories`; нет статически найденных изменений таблиц. См. [схему данных](../data-model.md).

Прямые выражения вызова: `db.execute`, `db.execute('SELECT * FROM directories WHERE volume_id=? AND path=?', (volume_id, path)).fetchone`, `json.loads`.

Выражения возврата (ветви, без исполнения):

- `{'entries': json.loads(row['entries']), 'scanned_at': row['scanned_at']} if row else {'entries': [], 'scanned_at': None}`


<a id="symbol-storagecatalog-directory"></a>

## `StorageCatalog.directory`

[media_manager/storage.py:566](../../media_manager/storage.py#L566)

Возвращает живой список папки или снимок с явной отметкой кэша. Изменяет SQLite-таблицы: directories.

```python
def directory(self, volume_id: str, path: str='', refresh: bool=True, *, discover: bool=True) -> dict
```

SQLite: чтение `annotations`; запись/DDL `directories`. См. [схему данных](../data-model.md).

Прямые выражения вызова: `KeyError`, `active_locations`, `db.execute`, `dict`, `inherited_location`, `json.dumps`, `next`, [now](../../media_manager/storage.py#L36), [relative_path](../../media_manager/storage.py#L42), [self._metadata](../../media_manager/storage.py#L514), [self._read_directory](../../media_manager/storage.py#L602), [self._snapshot](../../media_manager/storage.py#L559), [self._tags](../../media_manager/storage.py#L484), [self.connect](../../media_manager/storage.py#L204), [self.metadata](../../media_manager/storage.py#L471), [self.refresh](../../media_manager/storage.py#L216), `str`, `tags.get`, `volume.get`.

Явные `raise`:

- `KeyError('Том не найден')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `{**snapshot, 'path': path, 'volume': volume, 'cached': cached, 'error': error, 'error_code': error_code, 'metadata': self.metadata(volume_id, path)}`


<a id="symbol-storagecatalog--read-directory"></a>

## `StorageCatalog._read_directory`

[media_manager/storage.py:602](../../media_manager/storage.py#L602)

Перечисляет один каталог через проверенный дескриптор тома. Явно отклоняет недопустимое состояние через OSError.

```python
def _read_directory(volume: dict, path: str) -> list[dict]
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `OSError`, `PurePosixPath`, `datetime.fromtimestamp`, `datetime.fromtimestamp(info.st_mtime, timezone.utc).isoformat`, `descriptors.append`, `entries.append`, `entry.update`, `f'{path}/{item.name}'.lstrip`, `item.is_dir`, `item.is_symlink`, `item.stat`, `os.close`, `os.fstat`, `os.open`, `os.scandir`, `reversed`, `service_file`, `sorted`, `stat.S_ISREG`, `str`, `verify_identity`, `volume.get`.

Явные `raise`:

- `OSError('Том был отключён или заменён во время чтения')`
- `OSError('Каталог относится к другому тому')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `sorted(entries, key=lambda e: (e['kind'] != 'directory', e['name'].casefold()))`
