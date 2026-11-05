# Сканирование обычных источников: `media_manager/scanner.py`

Рекурсивный индексатор медиа по расширениям. Возвращает dataclass-отчёт с файлами и ошибками; не изменяет оригиналы и не считает неизвестные форматы медиа.

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

[Исходный модуль](../../media_manager/scanner.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [app.py](app.md), [media_manager/catalog.py](media_manager--catalog.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [storage_preview_ui.py](storage_preview_ui.md).
Тестовые модули с прямым импортом: [tests/test_catalog.py](tests.md#module-tests.test_catalog), [tests/test_scanner.py](tests.md#module-tests.test_scanner), [tests/test_thumbnails.py](tests.md#module-tests.test_thumbnails).

## Оглавление определений

- [MediaFile](#symbol-MediaFile) — Представляет метаданные одного обнаруженного фото или видео.
- [MediaFile.to_dict](#symbol-MediaFile.to_dict) — Преобразует данные объекта в словарь для каталога или API.
- [ScanError](#symbol-ScanError) — Представляет путь и сообщение ошибки обхода источника.
- [ScanError.to_dict](#symbol-ScanError.to_dict) — Преобразует данные объекта в словарь для каталога или API.
- [ScanReport](#symbol-ScanReport) — Объединяет источники, обнаруженные медиафайлы и ошибки рекурсивного обхода.
- [ScanReport.photo_count](#symbol-ScanReport.photo_count) — Подсчитывает обнаруженные файлы с видом photo.
- [ScanReport.to_dict](#symbol-ScanReport.to_dict) — Преобразует данные объекта в словарь для каталога или API.
- [ScanReport.total_size](#symbol-ScanReport.total_size) — Суммирует логические размеры обнаруженных медиафайлов.
- [ScanReport.video_count](#symbol-ScanReport.video_count) — Подсчитывает обнаруженные файлы с видом video.
- [media_kind](#symbol-media_kind) — Определяет photo или video по расширению имени файла.
- [normalize_source](#symbol-normalize_source) — Разрешает путь источника и требует существующий каталог.
- [scan_sources](#symbol-scan_sources) — Рекурсивно собирает метаданные медиа без изменения исходных файлов.
- [scan_sources.on_walk_error](#symbol-scan_sources.on_walk_error) — Сохраняет ошибку os.walk в отчёте, позволяя продолжить обработку остальных папок.

## Константы и значения по умолчанию

<a id="constant-IGNORED_DIRECTORY_NAMES"></a>

### `IGNORED_DIRECTORY_NAMES`

`{'__MACOSX', '.DocumentRevisions-V100', '.Spotlight-V100', '.TemporaryItems', '.Trashes', '.fseventsd'}`

<a id="constant-IGNORED_FILE_NAMES"></a>

### `IGNORED_FILE_NAMES`

`{'.DS_Store'}`

<a id="constant-PHOTO_EXTENSIONS"></a>

### `PHOTO_EXTENSIONS`

`{'.avif', '.bmp', '.gif', '.heic', '.heif', '.jpeg', '.jpg', '.png', '.tif', '.tiff', '.webp'}`

<a id="constant-VIDEO_EXTENSIONS"></a>

### `VIDEO_EXTENSIONS`

`{'.3gp', '.avi', '.m4v', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.webm'}`


<a id="symbol-MediaFile"></a>

## `MediaFile`

[media_manager/scanner.py](../../media_manager/scanner.py) · `MediaFile`

Представляет метаданные одного обнаруженного фото или видео. Базовые типы: обычный объект Python.

Базовые классы: `object`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `source` | `str` | `обязательное поле` |
| `relative_path` | `str` | `обязательное поле` |
| `kind` | `str` | `обязательное поле` |
| `size` | `int` | `обязательное поле` |
| `modified_at` | `str` | `обязательное поле` |

Именованные методы: `to_dict`.

<a id="symbol-MediaFile.to_dict"></a>

## `MediaFile.to_dict`

[media_manager/scanner.py](../../media_manager/scanner.py) · `MediaFile.to_dict`

Преобразует данные объекта в словарь для каталога или API. Использует asdict.

```python
def to_dict(self) -> dict[str, str | int]
```

Прямые выражения вызова: `asdict`.

Выражения возврата (ветви, без исполнения):

- `asdict(self)`


<a id="symbol-ScanError"></a>

## `ScanError`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanError`

Представляет путь и сообщение ошибки обхода источника. Базовые типы: обычный объект Python.

Базовые классы: `object`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `обязательное поле` |
| `message` | `str` | `обязательное поле` |

Именованные методы: `to_dict`.

<a id="symbol-ScanError.to_dict"></a>

## `ScanError.to_dict`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanError.to_dict`

Преобразует данные объекта в словарь для каталога или API. Использует asdict.

```python
def to_dict(self) -> dict[str, str]
```

Прямые выражения вызова: `asdict`.

Выражения возврата (ветви, без исполнения):

- `asdict(self)`


<a id="symbol-ScanReport"></a>

## `ScanReport`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanReport`

Объединяет источники, обнаруженные медиафайлы и ошибки рекурсивного обхода. Базовые типы: обычный объект Python.

Базовые классы: `object`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `files` | `list[MediaFile]` | `обязательное поле` |
| `errors` | `list[ScanError]` | `обязательное поле` |

Именованные методы: `photo_count`, `video_count`, `total_size`, `to_dict`.

<a id="symbol-ScanReport.photo_count"></a>

## `ScanReport.photo_count`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanReport.photo_count`

Подсчитывает обнаруженные файлы с видом photo. Использует sum.

```python
def photo_count(self) -> int
```

Декораторы: `property`.

Прямые выражения вызова: `sum`.

Выражения возврата (ветви, без исполнения):

- `sum((item.kind == 'photo' for item in self.files))`


<a id="symbol-ScanReport.to_dict"></a>

## `ScanReport.to_dict`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanReport.to_dict`

Преобразует данные объекта в словарь для каталога или API. Поля результата: files, errors, summary.

```python
def to_dict(self) -> dict[str, object]
```

Прямые выражения вызова: `error.to_dict`, `item.to_dict`, `len`.

Выражения возврата (ветви, без исполнения):

- `{'files': [item.to_dict() for item in self.files], 'errors': [error.to_dict() for error in self.errors], 'summary': {'total': len(self.files), 'photos': self.photo_count, 'videos': self.video_count, 'bytes': self.total_size, 'errors': len(self.errors)}}`


<a id="symbol-ScanReport.total_size"></a>

## `ScanReport.total_size`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanReport.total_size`

Суммирует логические размеры обнаруженных медиафайлов. Использует sum.

```python
def total_size(self) -> int
```

Декораторы: `property`.

Прямые выражения вызова: `sum`.

Выражения возврата (ветви, без исполнения):

- `sum((item.size for item in self.files))`


<a id="symbol-ScanReport.video_count"></a>

## `ScanReport.video_count`

[media_manager/scanner.py](../../media_manager/scanner.py) · `ScanReport.video_count`

Подсчитывает обнаруженные файлы с видом video. Использует sum.

```python
def video_count(self) -> int
```

Декораторы: `property`.

Прямые выражения вызова: `sum`.

Выражения возврата (ветви, без исполнения):

- `sum((item.kind == 'video' for item in self.files))`


<a id="symbol-media_kind"></a>

## `media_kind`

[media_manager/scanner.py](../../media_manager/scanner.py) · `media_kind`

Определяет photo или video по расширению имени файла. Использует path.suffix.lower.

```python
def media_kind(path: Path) -> str | None
```

Прямые выражения вызова: `path.suffix.lower`.

Выражения возврата (ветви, без исполнения):

- `'photo'`
- `'video'`
- `None`


<a id="symbol-normalize_source"></a>

## `normalize_source`

[media_manager/scanner.py](../../media_manager/scanner.py) · `normalize_source`

Разрешает путь источника и требует существующий каталог. Явно отклоняет недопустимое состояние через NotADirectoryError.

```python
def normalize_source(path: str | Path) -> Path
```

Прямые выражения вызова: `NotADirectoryError`, `Path`, `Path(path).expanduser`, `Path(path).expanduser().resolve`, `source.is_dir`.

Явные `raise`:

- `NotADirectoryError(f'Не является папкой: {source}')`

Выражения возврата (ветви, без исполнения):

- `source`


<a id="symbol-scan_sources"></a>

## `scan_sources`

[media_manager/scanner.py](../../media_manager/scanner.py) · `scan_sources`

Рекурсивно собирает метаданные медиа без изменения исходных файлов. Обрабатывает ошибки: (FileNotFoundError, NotADirectoryError, PermissionError), (FileNotFoundError, PermissionError, OSError).

```python
def scan_sources(sources: Iterable[str | Path]) -> ScanReport
```

Прямые выражения вызова: `(current_path / name).is_symlink`, [MediaFile](media_manager--scanner.md#symbol-MediaFile), `Path`, [ScanError](media_manager--scanner.md#symbol-ScanError), [ScanReport](media_manager--scanner.md#symbol-ScanReport), `datetime.fromtimestamp`, `datetime.fromtimestamp(stat.st_mtime).astimezone`, `datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat`, `errors.append`, `file_name.startswith`, `files.append`, `files.sort`, [media_kind](media_manager--scanner.md#symbol-media_kind), [normalize_source](media_manager--scanner.md#symbol-normalize_source), `os.walk`, `path.is_symlink`, `path.relative_to`, `path.stat`, `str`.

Перехватываемые типы: `(FileNotFoundError, NotADirectoryError, PermissionError)`, `(FileNotFoundError, PermissionError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `ScanReport(files=files, errors=errors)`


<a id="symbol-scan_sources.on_walk_error"></a>

## `scan_sources.on_walk_error`

[media_manager/scanner.py](../../media_manager/scanner.py) · `scan_sources.on_walk_error`

Сохраняет ошибку os.walk в отчёте, позволяя продолжить обработку остальных папок. Использует ScanError, errors.append.

```python
def on_walk_error(error: OSError) -> None
```

Прямые выражения вызова: [ScanError](media_manager--scanner.md#symbol-ScanError), `errors.append`, `str`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
