# Сканирование обычных источников: `media_manager/scanner.py`

Рекурсивный индексатор медиа по расширениям. Возвращает dataclass-отчёт с файлами и ошибками; не изменяет оригиналы и не считает неизвестные форматы медиа.

[Исходный модуль](../../media_manager/scanner.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: прямых импортов нет.
Импортируется модулями: [app.py](app.md), [media_manager/catalog.py](media_manager--catalog.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [storage_preview_ui.py](storage_preview_ui.md).
Тестовые модули с прямым импортом: [tests/test_catalog.py](../../tests/test_catalog.py#L8), [tests/test_scanner.py](../../tests/test_scanner.py#L8), [tests/test_thumbnails.py](../../tests/test_thumbnails.py#L12).

## Оглавление определений

- [MediaFile](#symbol-mediafile) — Представляет метаданные одного обнаруженного фото или видео.
- [MediaFile.to_dict](#symbol-mediafile-to-dict) — Преобразует данные объекта в словарь для каталога или API.
- [ScanError](#symbol-scanerror) — Представляет путь и сообщение ошибки обхода источника.
- [ScanError.to_dict](#symbol-scanerror-to-dict) — Преобразует данные объекта в словарь для каталога или API.
- [ScanReport](#symbol-scanreport) — Объединяет источники, обнаруженные медиафайлы и ошибки рекурсивного обхода.
- [ScanReport.photo_count](#symbol-scanreport-photo-count) — Подсчитывает обнаруженные файлы с видом photo.
- [ScanReport.video_count](#symbol-scanreport-video-count) — Подсчитывает обнаруженные файлы с видом video.
- [ScanReport.total_size](#symbol-scanreport-total-size) — Суммирует логические размеры обнаруженных медиафайлов.
- [ScanReport.to_dict](#symbol-scanreport-to-dict) — Преобразует данные объекта в словарь для каталога или API.
- [media_kind](#symbol-media-kind) — Определяет photo или video по расширению имени файла.
- [normalize_source](#symbol-normalize-source) — Разрешает путь источника и требует существующий каталог.
- [scan_sources](#symbol-scan-sources) — Рекурсивно собирает метаданные медиа без изменения исходных файлов.
- [scan_sources.on_walk_error](#symbol-scan-sources-on-walk-error) — Сохраняет ошибку os.walk в отчёте, позволяя продолжить обработку остальных папок.

## Константы и значения по умолчанию

| Имя | Выражение в коде |
| --- | --- |
| [PHOTO_EXTENSIONS](../../media_manager/scanner.py#L10) | `{'.avif', '.bmp', '.gif', '.heic', '.heif', '.jpeg', '.jpg', '.png', '.tif', '.tiff', '.webp'}` |
| [VIDEO_EXTENSIONS](../../media_manager/scanner.py#L24) | `{'.3gp', '.avi', '.m4v', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.webm'}` |
| [IGNORED_DIRECTORY_NAMES](../../media_manager/scanner.py#L36) | `{'__MACOSX', '.DocumentRevisions-V100', '.Spotlight-V100', '.TemporaryItems', '.Trashes', '.fseventsd'}` |
| [IGNORED_FILE_NAMES](../../media_manager/scanner.py#L44) | `{'.DS_Store'}` |

<a id="symbol-mediafile"></a>

## `MediaFile`

[media_manager/scanner.py:50](../../media_manager/scanner.py#L50)

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

<a id="symbol-mediafile-to-dict"></a>

## `MediaFile.to_dict`

[media_manager/scanner.py:59](../../media_manager/scanner.py#L59)

Преобразует данные объекта в словарь для каталога или API. Использует asdict.

```python
def to_dict(self) -> dict[str, str | int]
```

Прямые выражения вызова: `asdict`.

Выражения возврата (ветви, без исполнения):

- `asdict(self)`


<a id="symbol-scanerror"></a>

## `ScanError`

[media_manager/scanner.py:66](../../media_manager/scanner.py#L66)

Представляет путь и сообщение ошибки обхода источника. Базовые типы: обычный объект Python.

Базовые классы: `object`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `path` | `str` | `обязательное поле` |
| `message` | `str` | `обязательное поле` |

Именованные методы: `to_dict`.

<a id="symbol-scanerror-to-dict"></a>

## `ScanError.to_dict`

[media_manager/scanner.py:72](../../media_manager/scanner.py#L72)

Преобразует данные объекта в словарь для каталога или API. Использует asdict.

```python
def to_dict(self) -> dict[str, str]
```

Прямые выражения вызова: `asdict`.

Выражения возврата (ветви, без исполнения):

- `asdict(self)`


<a id="symbol-scanreport"></a>

## `ScanReport`

[media_manager/scanner.py:79](../../media_manager/scanner.py#L79)

Объединяет источники, обнаруженные медиафайлы и ошибки рекурсивного обхода. Базовые типы: обычный объект Python.

Базовые классы: `object`.

| Поле | Аннотация | Значение / ограничение |
| --- | --- | --- |
| `files` | `list[MediaFile]` | `обязательное поле` |
| `errors` | `list[ScanError]` | `обязательное поле` |

Именованные методы: `photo_count`, `video_count`, `total_size`, `to_dict`.

<a id="symbol-scanreport-photo-count"></a>

## `ScanReport.photo_count`

[media_manager/scanner.py:86](../../media_manager/scanner.py#L86)

Подсчитывает обнаруженные файлы с видом photo. Использует sum.

```python
def photo_count(self) -> int
```

Декораторы: `property`.

Прямые выражения вызова: `sum`.

Выражения возврата (ветви, без исполнения):

- `sum((item.kind == 'photo' for item in self.files))`


<a id="symbol-scanreport-video-count"></a>

## `ScanReport.video_count`

[media_manager/scanner.py:92](../../media_manager/scanner.py#L92)

Подсчитывает обнаруженные файлы с видом video. Использует sum.

```python
def video_count(self) -> int
```

Декораторы: `property`.

Прямые выражения вызова: `sum`.

Выражения возврата (ветви, без исполнения):

- `sum((item.kind == 'video' for item in self.files))`


<a id="symbol-scanreport-total-size"></a>

## `ScanReport.total_size`

[media_manager/scanner.py:98](../../media_manager/scanner.py#L98)

Суммирует логические размеры обнаруженных медиафайлов. Использует sum.

```python
def total_size(self) -> int
```

Декораторы: `property`.

Прямые выражения вызова: `sum`.

Выражения возврата (ветви, без исполнения):

- `sum((item.size for item in self.files))`


<a id="symbol-scanreport-to-dict"></a>

## `ScanReport.to_dict`

[media_manager/scanner.py:103](../../media_manager/scanner.py#L103)

Преобразует данные объекта в словарь для каталога или API. Поля результата: files, errors, summary.

```python
def to_dict(self) -> dict[str, object]
```

Прямые выражения вызова: `error.to_dict`, `item.to_dict`, `len`.

Выражения возврата (ветви, без исполнения):

- `{'files': [item.to_dict() for item in self.files], 'errors': [error.to_dict() for error in self.errors], 'summary': {'total': len(self.files), 'photos': self.photo_count, 'videos': self.video_count, 'bytes': self.total_size, 'errors': len(self.errors)}}`


<a id="symbol-media-kind"></a>

## `media_kind`

[media_manager/scanner.py:119](../../media_manager/scanner.py#L119)

Определяет photo или video по расширению имени файла. Использует path.suffix.lower.

```python
def media_kind(path: Path) -> str | None
```

Прямые выражения вызова: `path.suffix.lower`.

Выражения возврата (ветви, без исполнения):

- `'photo'`
- `'video'`
- `None`


<a id="symbol-normalize-source"></a>

## `normalize_source`

[media_manager/scanner.py:130](../../media_manager/scanner.py#L130)

Разрешает путь источника и требует существующий каталог. Явно отклоняет недопустимое состояние через NotADirectoryError.

```python
def normalize_source(path: str | Path) -> Path
```

Прямые выражения вызова: `NotADirectoryError`, `Path`, `Path(path).expanduser`, `Path(path).expanduser().resolve`, `source.is_dir`.

Явные `raise`:

- `NotADirectoryError(f'Не является папкой: {source}')`

Выражения возврата (ветви, без исполнения):

- `source`


<a id="symbol-scan-sources"></a>

## `scan_sources`

[media_manager/scanner.py:139](../../media_manager/scanner.py#L139)

Рекурсивно собирает метаданные медиа без изменения исходных файлов. Обрабатывает ошибки: (FileNotFoundError, NotADirectoryError, PermissionError), (FileNotFoundError, PermissionError, OSError).

```python
def scan_sources(sources: Iterable[str | Path]) -> ScanReport
```

Прямые выражения вызова: `(current_path / name).is_symlink`, [MediaFile](../../media_manager/scanner.py#L50), `Path`, [ScanError](../../media_manager/scanner.py#L66), [ScanReport](../../media_manager/scanner.py#L79), `datetime.fromtimestamp`, `datetime.fromtimestamp(stat.st_mtime).astimezone`, `datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat`, `errors.append`, `file_name.startswith`, `files.append`, `files.sort`, [media_kind](../../media_manager/scanner.py#L119), [normalize_source](../../media_manager/scanner.py#L130), `os.walk`, `path.is_symlink`, `path.relative_to`, `path.stat`, `str`.

Перехватываемые типы: `(FileNotFoundError, NotADirectoryError, PermissionError)`, `(FileNotFoundError, PermissionError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `ScanReport(files=files, errors=errors)`


<a id="symbol-scan-sources-on-walk-error"></a>

## `scan_sources.on_walk_error`

[media_manager/scanner.py:153](../../media_manager/scanner.py#L153)

Сохраняет ошибку os.walk в отчёте, позволяя продолжить обработку остальных папок. Использует ScanError, errors.append.

```python
def on_walk_error(error: OSError) -> None
```

Прямые выражения вызова: [ScanError](../../media_manager/scanner.py#L66), `errors.append`, `str`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.
