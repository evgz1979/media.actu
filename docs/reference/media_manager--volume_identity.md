# Идентичность носителей: `media_manager/volume_identity.py`

Проверяет и создаёт маркеры сменных носителей, ограничивает пути и открывает корень тома по дескриптору. Отделяет служебные файлы приложения от пользовательского дерева.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/volume_identity.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/directory_sizes.py](media_manager--directory_sizes.md), [media_manager/folder_markers.py](media_manager--folder_markers.md), [media_manager/folder_tracking.py](media_manager--folder_tracking.md), [media_manager/paired_comparison.py](media_manager--paired_comparison.md), [media_manager/storage.py](media_manager--storage.md), [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_folder_markers.py](tests.md#module-tests.test_folder_markers), [tests/test_volume_identity.py](tests.md#module-tests.test_volume_identity).

## Оглавление определений

- [_read_marker_document](#symbol-_read_marker_document) — Читает ограниченный JSON носителя и проверяет UUID, версию и имя.
- [canonical_host](#symbol-canonical_host) — Нормализует адрес сервера, включая суффикс Bonjour SMB.
- [copy_temporary](#symbol-copy_temporary) — Распознаёт только собственный формат промежуточного имени копирования.
- [create_marker](#symbol-create_marker) — Создаёт новый маркер носителя без замены существующего файла.
- [mounted_root](#symbol-mounted_root) — Открывает корневой каталог без symlink и проверяет ожидаемый device.
- [read_capacity](#symbol-read_capacity) — Вычисляет ёмкость и доступное место по fstatvfs открытого тома.
- [read_marker](#symbol-read_marker) — Возвращает проверенный ID и название маркера носителя либо None.
- [rename_marker](#symbol-rename_marker) — Атомарно меняет название только у подтверждённого маркера носителя.
- [service_file](#symbol-service_file) — Определяет служебные файлы приложения, исключаемые из обхода и сверок.
- [usb_share](#symbol-usb_share) — Распознаёт имя сменного USB-ресурса NAS вида usbshare.
- [validate_name](#symbol-validate_name) — Проверяет длину и допустимые символы названия носителя.
- [verify_identity](#symbol-verify_identity) — Проверяет подтверждённость тома и соответствие текущего служебного ID.

## Константы и значения по умолчанию

<a id="constant-COPY_TEMP_PATTERN"></a>

### `COPY_TEMP_PATTERN`

`re.compile('\\.media-actu-copy-[a-f0-9]{32}-[a-f0-9]{32}\\.part\\Z')`

<a id="constant-FOLDER_MARKER_FILES"></a>

### `FOLDER_MARKER_FILES`

`frozenset((FOLDER_MARKER_NAME, '._' + FOLDER_MARKER_NAME))`

<a id="constant-FOLDER_MARKER_NAME"></a>

### `FOLDER_MARKER_NAME`

`'.media-actu-folder.json'`

<a id="constant-MARKER_FILES"></a>

### `MARKER_FILES`

`frozenset((MARKER_NAME, '._' + MARKER_NAME))`

<a id="constant-MARKER_LIMIT"></a>

### `MARKER_LIMIT`

`4096`

<a id="constant-MARKER_NAME"></a>

### `MARKER_NAME`

`'.media-actu-volume.json'`


<a id="symbol-_read_marker_document"></a>

## `_read_marker_document`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `_read_marker_document`

Читает ограниченный JSON носителя и проверяет UUID, версию и имя. Явно отклоняет недопустимое состояние через OSError, ValueError.

```python
def _read_marker_document(root: int) -> dict | None
```

Прямые выражения вызова: `OSError`, `ValueError`, `isinstance`, `json.loads`, `len`, `marker.get`, `os.close`, `os.fdopen`, `os.fstat`, `os.open`, `stat.S_ISREG`, `str`, `stream.read`, `type`, `uuid.UUID`, [validate_name](media_manager--volume_identity.md#symbol-validate_name).

Явные `raise`:

- `OSError('Некорректный служебный файл носителя')`
- `OSError('Служебный файл носителя слишком большой')`
- `ValueError('version')`
- `ValueError('empty UUID')`
- `OSError('Не удалось подтвердить ID в служебном файле носителя')`

Перехватываемые типы: `FileNotFoundError`, `(ValueError, TypeError, KeyError, AttributeError)`.

Выражения возврата (ветви, без исполнения):

- `None`
- `marker`


<a id="symbol-canonical_host"></a>

## `canonical_host`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `canonical_host`

Нормализует адрес сервера, включая суффикс Bonjour SMB. Использует host.endswith, host.rstrip, host.rstrip('.').casefold, host[:-len(suffix)].removesuffix.

```python
def canonical_host(host: str) -> str
```

Прямые выражения вызова: `host.endswith`, `host.rstrip`, `host.rstrip('.').casefold`, `host[:-len(suffix)].removesuffix`, `len`.

Выражения возврата (ветви, без исполнения):

- `host`


<a id="symbol-copy_temporary"></a>

## `copy_temporary`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `copy_temporary`

Распознаёт только собственный формат промежуточного имени копирования. Использует COPY_TEMP_PATTERN.fullmatch.

```python
def copy_temporary(name: str) -> bool
```

Прямые выражения вызова: `COPY_TEMP_PATTERN.fullmatch`, `bool`.

Выражения возврата (ветви, без исполнения):

- `bool(COPY_TEMP_PATTERN.fullmatch(name))`


<a id="symbol-create_marker"></a>

## `create_marker`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `create_marker`

Создаёт новый маркер носителя без замены существующего файла. Явно отклоняет недопустимое состояние через OSError.

```python
def create_marker(path: str, device: int | None, name: str) -> dict
```

Прямые выражения вызова: `(json.dumps(marker, ensure_ascii=False, indent=2) + '\n').encode`, `OSError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `json.dumps`, [mounted_root](media_manager--volume_identity.md#symbol-mounted_root), `name.strip`, `os.fdopen`, `os.fsync`, `os.open`, [read_marker](media_manager--volume_identity.md#symbol-read_marker), `str`, `stream.fileno`, `stream.flush`, `stream.write`, `uuid.uuid4`, [validate_name](media_manager--volume_identity.md#symbol-validate_name).

Явные `raise`:

- `OSError('Диск изменился во время регистрации')`

Выражения возврата (ветви, без исполнения):

- `marker`


<a id="symbol-mounted_root"></a>

## `mounted_root`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `mounted_root`

Открывает корневой каталог без symlink и проверяет ожидаемый device. Явно отклоняет недопустимое состояние через OSError.

```python
def mounted_root(path: str, device: int | None=None)
```

Декораторы: `contextmanager`.

Прямые выражения вызова: `OSError`, `os.close`, `os.fstat`, `os.open`.

Явные `raise`:

- `OSError('Том был отключён или заменён')`

Передаёт управление через `yield`; освобождение ресурса описано в теле контекстного менеджера.


<a id="symbol-read_capacity"></a>

## `read_capacity`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `read_capacity`

Вычисляет ёмкость и доступное место по fstatvfs открытого тома. Явно отклоняет недопустимое состояние через OSError.

```python
def read_capacity(root: int) -> dict
```

Прямые выражения вызова: `OSError`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `os.fstatvfs`.

Явные `raise`:

- `OSError('Том не сообщил корректные сведения о свободном месте')`

Выражения возврата (ветви, без исполнения):

- `{'total_bytes': total, 'used_bytes': total - free, 'free_bytes': free, 'available_bytes': available, 'checked_at': datetime.now(timezone.utc).isoformat()}`


<a id="symbol-read_marker"></a>

## `read_marker`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `read_marker`

Возвращает проверенный ID и название маркера носителя либо None. Использует _read_marker_document, marker['name'].strip, uuid.UUID.

```python
def read_marker(root: int) -> dict | None
```

Прямые выражения вызова: [_read_marker_document](media_manager--volume_identity.md#symbol-_read_marker_document), `marker['name'].strip`, `str`, `uuid.UUID`.

Выражения возврата (ветви, без исполнения):

- `{'id': str(uuid.UUID(marker['id'])), 'name': marker['name'].strip()} if marker else None`


<a id="symbol-rename_marker"></a>

## `rename_marker`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `rename_marker`

Атомарно меняет название только у подтверждённого маркера носителя. Явно отклоняет недопустимое состояние через OSError, ValueError.

```python
def rename_marker(path: str, device: int | None, marker_id: str, name: str) -> dict
```

Прямые выражения вызова: `(json.dumps(updated, ensure_ascii=False, indent=2) + '\n').encode`, `OSError`, `ValueError`, [_read_marker_document](media_manager--volume_identity.md#symbol-_read_marker_document), `json.dumps`, `len`, [mounted_root](media_manager--volume_identity.md#symbol-mounted_root), `name.strip`, `os.fdopen`, `os.fsync`, `os.open`, `os.replace`, `os.stat`, `os.unlink`, [read_marker](media_manager--volume_identity.md#symbol-read_marker), `stat.S_IMODE`, `str`, `stream.fileno`, `stream.flush`, `stream.write`, `uuid.UUID`, `uuid.uuid4`, [validate_name](media_manager--volume_identity.md#symbol-validate_name).

Явные `raise`:

- `OSError('Сменный диск был отключён или заменён')`
- `ValueError('Новое имя не помещается в служебный файл носителя')`
- `OSError('Служебный файл диска изменился во время переименования')`
- `OSError('Не удалось подтвердить новое имя диска')`

Перехватываемые типы: `FileNotFoundError`.

Выражения возврата (ветви, без исполнения):

- `confirmed`


<a id="symbol-service_file"></a>

## `service_file`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `service_file`

Определяет служебные файлы приложения, исключаемые из обхода и сверок. Использует copy_temporary.

```python
def service_file(name: str, *, volume_root: bool=False) -> bool
```

Прямые выражения вызова: [copy_temporary](media_manager--volume_identity.md#symbol-copy_temporary).

Выражения возврата (ветви, без исполнения):

- `copy_temporary(name) or name in FOLDER_MARKER_FILES or (volume_root and name in MARKER_FILES)`


<a id="symbol-usb_share"></a>

## `usb_share`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `usb_share`

Распознаёт имя сменного USB-ресурса NAS вида usbshare. Использует re.fullmatch.

```python
def usb_share(name: str) -> bool
```

Прямые выражения вызова: `bool`, `re.fullmatch`.

Выражения возврата (ветви, без исполнения):

- `bool(re.fullmatch('usbshare\\d+(?:[-_].*)?', name, re.IGNORECASE))`


<a id="symbol-validate_name"></a>

## `validate_name`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `validate_name`

Проверяет длину и допустимые символы названия носителя. Явно отклоняет недопустимое состояние через ValueError.

```python
def validate_name(name: str) -> None
```

Прямые выражения вызова: `ValueError`, `any`, `isinstance`, `len`, `name.strip`, `ord`.

Явные `raise`:

- `ValueError('Нужно имя носителя длиной от 1 до 120 символов без управляющих знаков')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-verify_identity"></a>

## `verify_identity`

[media_manager/volume_identity.py](../../media_manager/volume_identity.py) · `verify_identity`

Проверяет подтверждённость тома и соответствие текущего служебного ID. Явно отклоняет недопустимое состояние через OSError.

```python
def verify_identity(root: int, volume: dict) -> None
```

Прямые выражения вызова: `OSError`, [read_marker](media_manager--volume_identity.md#symbol-read_marker), `volume.get`.

Явные `raise`:

- `OSError('Носитель не подтверждён. Сначала зарегистрируй сменный диск.')`
- `OSError('Сменный диск был отключён или заменён')`

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
