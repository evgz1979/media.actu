# Превью файлов на томах: `media_manager/storage_previews.py`

Создаёт превью файлов вне медиаиндекса по запросу UI. Читает через проверенный дескриптор; видео декодирует FFmpeg либо нативный AVFoundation-helper.

[Исходный модуль](../../media_manager/storage_previews.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/comparison.py](media_manager--comparison.md), [media_manager/scanner.py](media_manager--scanner.md), [media_manager/storage.py](media_manager--storage.md), [media_manager/thumbnails.py](media_manager--thumbnails.md).
Импортируется модулями: [app.py](app.md).
Тестовые модули с прямым импортом: [tests/test_storage_previews.py](../../tests/test_storage_previews.py#L16).

## Оглавление определений

- [StoragePreviewService](#symbol-storagepreviewservice) — Создаёт кэшированные фото и кадры видео вне зарегистрированного медиаиндекса.
- [StoragePreviewService.__init__](#symbol-storagepreviewservice---init--) — Инициализирует StoragePreviewService и его рабочее состояние.
- [StoragePreviewService.get_or_create](#symbol-storagepreviewservice-get-or-create) — Возвращает или создаёт JPEG проверенного файла тома в выбранном размере.
- [StoragePreviewService._native_video_command](#symbol-storagepreviewservice--native-video-command) — Собирает и выбирает нативный декодер AVFoundation по хешу его исходника.
- [StoragePreviewService._video_frame](#symbol-storagepreviewservice--video-frame) — Получает первый кадр видео через FFmpeg или нативный декодер дескриптора.

<a id="symbol-storagepreviewservice"></a>

## `StoragePreviewService`

[media_manager/storage_previews.py:24](../../media_manager/storage_previews.py#L24)

Создаёт кэшированные фото и кадры видео вне зарегистрированного медиаиндекса. Зависимости конструктора: storage, cache_directory.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_native_lock`, `_slots`, `cache_directory`, `storage`.

Именованные методы: `__init__`, `get_or_create`, `_native_video_command`, `_video_frame`.

<a id="symbol-storagepreviewservice---init--"></a>

## `StoragePreviewService.__init__`

[media_manager/storage_previews.py:27](../../media_manager/storage_previews.py#L27)

Инициализирует StoragePreviewService и его рабочее состояние. Обновляет состояние объекта: _native_lock, _slots, cache_directory, storage.

```python
def __init__(self, storage, cache_directory)
```

Присваивания полям `self`: `_native_lock`, `_slots`, `cache_directory`, `storage`.

Прямые выражения вызова: `Path`, `threading.Lock`, `threading.Semaphore`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreviewservice-get-or-create"></a>

## `StoragePreviewService.get_or_create`

[media_manager/storage_previews.py:35](../../media_manager/storage_previews.py#L35)

Возвращает или создаёт JPEG проверенного файла тома в выбранном размере. Явно отклоняет недопустимое состояние через KeyError, OSError, ThumbnailCacheUnavailable, ValueError.

```python
def get_or_create(self, volume_id, path, *, large=False)
```

Прямые выражения вызова: `Image.new`, `Image.open`, `ImageOps.exif_transpose`, `KeyError`, `OSError`, `Path`, `Path('/Volumes', parts[2]).is_dir`, `Path(path).suffix[1:].lower`, `ThumbnailCacheUnavailable`, `ValueError`, `background.paste`, `directory.mkdir`, `encoded.getvalue`, `f'{volume_id}\x00{path}\x00{before.st_dev}\x00{before.st_ino}\x00{before.st_size}\x00{before.st_mtime_ns}\x00{before.st_ctime_ns}\x00{large}'.encode`, `hashlib.sha256`, `hashlib.sha256(f'{volume_id}\x00{path}\x00{before.st_dev}\x00{before.st_ino}\x00{before.st_size}\x00{before.st_mtime_ns}\x00{before.st_ctime_ns}\x00{large}'.encode()).hexdigest`, `image.copy`, `image.getbands`, `image.getchannel`, `image.save`, `image.thumbnail`, `io.BytesIO`, `len`, `media_kind`, `next`, `open_readonly`, `os.dup`, `os.fdopen`, `os.fstat`, `relative_path`, [self._video_frame](../../media_manager/storage_previews.py#L115), `self.storage.refresh`, `target.is_file`, `temporary.replace`, `temporary.unlink`, `temporary.write_bytes`, `uuid.uuid4`, `volume.get`.

Явные `raise`:

- `ValueError('Для этого типа файла доступна только информация о файле')`
- `KeyError('Том не найден')`
- `OSError(volume.get('identity_error') or 'Том отключён или недоступен')`
- `ThumbnailCacheUnavailable('Том кэша превью не подключён')`
- `ThumbnailCacheUnavailable('Кэш превью недоступен')`
- `OSError('Файл изменился во время создания превью. Выбери его ещё раз.')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `target`


<a id="symbol-storagepreviewservice--native-video-command"></a>

## `StoragePreviewService._native_video_command`

[media_manager/storage_previews.py:91](../../media_manager/storage_previews.py#L91)

Собирает и выбирает нативный декодер AVFoundation по хешу его исходника. Явно отклоняет недопустимое состояние через ValueError.

```python
def _native_video_command(self, descriptor, width, height, extension)
```

Прямые выражения вызова: `Path`, `Path(__file__).with_name`, `ValueError`, `directory.mkdir`, `hashlib.sha256`, `hashlib.sha256(source.read_bytes()).hexdigest`, `source.read_bytes`, `str`, `subprocess.run`, `target.is_file`, `temporary.replace`, `temporary.unlink`, `uuid.uuid4`.

Явные `raise`:

- `ValueError('Для превью видео нужен FFmpeg')`

Выражения возврата (ветви, без исполнения):

- `[str(target), str(descriptor), str(width), str(height), extension]`


<a id="symbol-storagepreviewservice--video-frame"></a>

## `StoragePreviewService._video_frame`

[media_manager/storage_previews.py:115](../../media_manager/storage_previews.py#L115)

Получает первый кадр видео через FFmpeg или нативный декодер дескриптора. Явно отклоняет недопустимое состояние через ValueError.

```python
def _video_frame(self, descriptor, large, extension)
```

Прямые выражения вызова: `Image.open`, `ValueError`, `frame.copy`, `io.BytesIO`, [self._native_video_command](../../media_manager/storage_previews.py#L91), `shutil.which`, `subprocess.run`.

Явные `raise`:

- `ValueError('Не удалось получить кадр видео')`

Перехватываемые типы: `(subprocess.SubprocessError, OSError)`.

Выражения возврата (ветви, без исполнения):

- `frame.copy()`
