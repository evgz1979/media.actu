# Кэш превью медиаиндекса: `media_manager/thumbnails.py`

Производные JPEG обычных фото и объектов Photos. Отдельные ограничения параллелизма; готовые пути привязаны к версии медиа. Полного экспорта оригиналов для миниатюр нет.

[Исходный модуль](../../media_manager/thumbnails.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/catalog.py](media_manager--catalog.md), [media_manager/photos_adapter.py](media_manager--photos_adapter.md).
Импортируется модулями: [app.py](app.md), [media_manager/storage_previews.py](media_manager--storage_previews.md), [media_manager/thumbnail_workers.py](media_manager--thumbnail_workers.md).
Тестовые модули с прямым импортом: [tests/test_photo_libraries.py](../../tests/test_photo_libraries.py#L12), [tests/test_thumbnails.py](../../tests/test_thumbnails.py#L13).

## Оглавление определений

- [ThumbnailCacheUnavailable](#symbol-thumbnailcacheunavailable) — Обозначает недоступность настроенного диска или каталога кэша превью.
- [ThumbnailService](#symbol-thumbnailservice) — Создаёт и находит версионированные JPEG-превью объектов медиаиндекса.
- [ThumbnailService.__init__](#symbol-thumbnailservice---init--) — Инициализирует ThumbnailService и его рабочее состояние.
- [ThumbnailService.get_or_create](#symbol-thumbnailservice-get-or-create) — Сериализует создание превью одного media_id и возвращает готовый путь.
- [ThumbnailService.get_cached](#symbol-thumbnailservice-get-cached) — Возвращает только существующее превью без вызова генерации или PhotoKit.
- [ThumbnailService._cache_target](#symbol-thumbnailservice--cache-target) — Проверяет доступность диска кэша и строит двухуровневый хеш-путь JPEG.
- [ThumbnailService._usable_photos_preview](#symbol-thumbnailservice--usable-photos-preview) — Проверяет готовый JPEG Photos и требует размер больше прежних 64 пикселей.
- [ThumbnailService._get_or_create](#symbol-thumbnailservice--get-or-create) — Создаёт превью через PhotoKit или Pillow с ограничением параллелизма.

<a id="symbol-thumbnailcacheunavailable"></a>

## `ThumbnailCacheUnavailable`

[media_manager/thumbnails.py:19](../../media_manager/thumbnails.py#L19)

Обозначает недоступность настроенного диска или каталога кэша превью. Базовые типы: RuntimeError.

Базовые классы: `RuntimeError`.


Именованные методы: собственных методов нет; используется поведение базового типа.

<a id="symbol-thumbnailservice"></a>

## `ThumbnailService`

[media_manager/thumbnails.py:25](../../media_manager/thumbnails.py#L25)

Создаёт и находит версионированные JPEG-превью объектов медиаиндекса. Зависимости конструктора: catalog, cache_directory, photos_adapter, photo_libraries.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `_folder_slots`, `_locks_guard`, `_media_locks`, `_photos_slots`, `cache_directory`, `catalog`, `photo_libraries`, `photos_adapter`.

Именованные методы: `__init__`, `get_or_create`, `get_cached`, `_cache_target`, `_usable_photos_preview`, `_get_or_create`.

<a id="symbol-thumbnailservice---init--"></a>

## `ThumbnailService.__init__`

[media_manager/thumbnails.py:28](../../media_manager/thumbnails.py#L28)

Инициализирует ThumbnailService и его рабочее состояние. Обновляет состояние объекта: _folder_slots, _locks_guard, _media_locks, _photos_slots, cache_directory, catalog, photo_libraries, photos_adapter.

```python
def __init__(self, catalog: Catalog, cache_directory: str | Path, photos_adapter: SystemPhotosAdapter | None=None, photo_libraries=None) -> None
```

Присваивания полям `self`: `_folder_slots`, `_locks_guard`, `_media_locks`, `_photos_slots`, `cache_directory`, `catalog`, `photo_libraries`, `photos_adapter`.

Прямые выражения вызова: `Path`, `threading.Lock`, `threading.Semaphore`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-thumbnailservice-get-or-create"></a>

## `ThumbnailService.get_or_create`

[media_manager/thumbnails.py:46](../../media_manager/thumbnails.py#L46)

Сериализует создание превью одного media_id и возвращает готовый путь. Использует self._get_or_create, self._media_locks.setdefault, threading.Lock.

```python
def get_or_create(self, media_id: int) -> Path | None
```

Прямые выражения вызова: [self._get_or_create](../../media_manager/thumbnails.py#L112), `self._media_locks.setdefault`, `threading.Lock`.

Выражения возврата (ветви, без исполнения):

- `self._get_or_create(media_id)`


<a id="symbol-thumbnailservice-get-cached"></a>

## `ThumbnailService.get_cached`

[media_manager/thumbnails.py:54](../../media_manager/thumbnails.py#L54)

Возвращает только существующее превью без вызова генерации или PhotoKit. Использует Path, Path(str(media['source_path'])).resolve, candidate.is_symlink, candidate.resolve и ещё 1.

```python
def get_cached(self, media_id: int) -> Path | None
```

Прямые выражения вызова: `Path`, `Path(str(media['source_path'])).resolve`, `candidate.is_symlink`, `candidate.resolve`, `f"{media['relative_path']}\x00{media['modified_at']}".encode`, `f'{original}\x00{stat.st_size}\x00{stat.st_mtime_ns}'.encode`, `hashlib.sha256`, `hashlib.sha256(f"{media['relative_path']}\x00{media['modified_at']}".encode()).hexdigest`, `hashlib.sha256(f'{original}\x00{stat.st_size}\x00{stat.st_mtime_ns}'.encode()).hexdigest`, `media.get`, `original.is_relative_to`, `original.stat`, [self._cache_target](../../media_manager/thumbnails.py#L79), `self.catalog.get_media`, `str`, `target.is_file`.

Выражения возврата (ветви, без исполнения):

- `None`
- `target if target.is_file() else None`


<a id="symbol-thumbnailservice--cache-target"></a>

## `ThumbnailService._cache_target`

[media_manager/thumbnails.py:79](../../media_manager/thumbnails.py#L79)

Проверяет доступность диска кэша и строит двухуровневый хеш-путь JPEG. Явно отклоняет недопустимое состояние через ThumbnailCacheUnavailable.

```python
def _cache_target(self, media_id: int, fingerprint: str) -> Path
```

Прямые выражения вызова: `Path`, [ThumbnailCacheUnavailable](../../media_manager/thumbnails.py#L19), `directory.mkdir`, `len`, `volume.is_dir`.

Явные `raise`:

- `ThumbnailCacheUnavailable(f'Том кэша превью не подключён: {volume}')`
- `ThumbnailCacheUnavailable(f'Кэш превью недоступен: {self.cache_directory}')`

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `directory / f'{media_id}-{fingerprint}.jpg'`


<a id="symbol-thumbnailservice--usable-photos-preview"></a>

## `ThumbnailService._usable_photos_preview`

[media_manager/thumbnails.py:99](../../media_manager/thumbnails.py#L99)

Проверяет готовый JPEG Photos и требует размер больше прежних 64 пикселей. Обрабатывает ошибки: OSError.

```python
def _usable_photos_preview(target: Path) -> bool
```

Декораторы: `staticmethod`.

Прямые выражения вызова: `Image.open`, `max`, `target.is_file`.

Перехватываемые типы: `OSError`.

Выражения возврата (ветви, без исполнения):

- `False`
- `max(image.size) > 64`


<a id="symbol-thumbnailservice--get-or-create"></a>

## `ThumbnailService._get_or_create`

[media_manager/thumbnails.py:112](../../media_manager/thumbnails.py#L112)

Создаёт превью через PhotoKit или Pillow с ограничением параллелизма. Использует Image.new, Image.open, ImageOps.exif_transpose, Path, Path(str(media['source_path'])).resolve.

```python
def _get_or_create(self, media_id: int) -> Path | None
```

Прямые выражения вызова: `Image.new`, `Image.open`, `ImageOps.exif_transpose`, `Path`, `Path(str(media['source_path'])).resolve`, `background.paste`, `candidate.is_symlink`, `candidate.resolve`, `f"{media['relative_path']}\x00{media['modified_at']}".encode`, `f'{original}\x00{stat.st_size}\x00{stat.st_mtime_ns}'.encode`, `hashlib.sha256`, `hashlib.sha256(f"{media['relative_path']}\x00{media['modified_at']}".encode()).hexdigest`, `hashlib.sha256(f'{original}\x00{stat.st_size}\x00{stat.st_mtime_ns}'.encode()).hexdigest`, `image.getbands`, `image.getchannel`, `image.save`, `image.thumbnail`, `int`, `media.get`, `original.is_relative_to`, `original.stat`, [self._cache_target](../../media_manager/thumbnails.py#L79), [self._usable_photos_preview](../../media_manager/thumbnails.py#L99), `self.catalog.get_media`, `self.photo_libraries.create_thumbnail`, `self.photos_adapter.create_thumbnail`, `str`, `target.exists`.

Выражения возврата (ветви, без исполнения):

- `None`
- `target`
- `self.photo_libraries.create_thumbnail(int(media['source_id']), str(media['relative_path']), target)`
- `self.photos_adapter.create_thumbnail(str(media['relative_path']), target)`
