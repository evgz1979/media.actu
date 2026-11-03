# UI превью и плиток: `storage_preview_ui.py`

Показывает выбранный файл или папку в соседней панели: JPEG, кадр видео, плитки, дозагрузку и готовность Photos-превью.

[Исходный модуль](../../storage_preview_ui.py)
 · [Общий справочник](README.md) · [Языковые механизмы](../development/language.md)

## Связи модуля

Импортирует из проекта: [media_manager/scanner.py](media_manager--scanner.md), [media_manager/storage.py](media_manager--storage.md).
Импортируется модулями: [workspace_ui.py](workspace_ui.md).
Тестовые модули с прямым импортом: [tests/test_storage_previews.py](../../tests/test_storage_previews.py#L17).

## Оглавление определений

- [StoragePreview](#symbol-storagepreview) — Управляет превью выбранного файла или плитками папки одной панели.
- [StoragePreview.__init__](#symbol-storagepreview---init--) — Инициализирует StoragePreview и его рабочее состояние.
- [StoragePreview.snapshot](#symbol-storagepreview-snapshot) — Возвращает компактное состояние превью для восстановления вкладки.
- [StoragePreview.show](#symbol-storagepreview-show) — Загружает выбранный объект или папку и отбрасывает устаревшие ответы.
- [StoragePreview.open_folder](#symbol-storagepreview-open-folder) — Открывает папку внутри текущей панели превью.
- [StoragePreview.parent](#symbol-storagepreview-parent) — Переходит к родительскому пути текущего превью.
- [StoragePreview.refresh](#symbol-storagepreview-refresh) — Повторно загружает текущую папку или объект превью.
- [StoragePreview.update_header](#symbol-storagepreview-update-header) — Обновляет путь и подписи панели превью.
- [StoragePreview.image_url](#symbol-storagepreview-image-url) — Выбирает URL готового Photos-превью или производного JPEG файлового тома.
- [StoragePreview.image](#symbol-storagepreview-image) — Создаёт элемент изображения с выбранным размером превью.
- [StoragePreview.refresh_pending](#symbol-storagepreview-refresh-pending) — Проверяет готовность ожидаемых Photos-превью и обновляет изображения.
- [StoragePreview.more](#symbol-storagepreview-more) — Догружает следующую страницу плиток текущей папки.
- [StoragePreview.render](#symbol-storagepreview-render) — Перерисовывает выбранный файл, состояние ожидания или плитки папки.
- [StoragePreview.render_folder](#symbol-storagepreview-render-folder) — Показывает плитки папок и файлов с командами открытия и выбора.

<a id="symbol-storagepreview"></a>

## `StoragePreview`

[storage_preview_ui.py:36](../../storage_preview_ui.py#L36)

Управляет превью выбранного файла или плитками папки одной панели. Зависимости конструктора: pane.

Базовые классы: `object`.


Состояние, присваиваемое конструктором: `content`, `data`, `entry`, `generation`, `kind`, `limit`, `loading`, `pane`, `path`, `pending_images`, `preview_revision`, `volume_id`, `ws`.

Именованные методы: `__init__`, `snapshot`, `show`, `open_folder`, `parent`, `refresh`, `update_header`, `image_url`, `image`, `refresh_pending`, `more`, `render`, `render_folder`.

<a id="symbol-storagepreview---init--"></a>

## `StoragePreview.__init__`

[storage_preview_ui.py:39](../../storage_preview_ui.py#L39)

Инициализирует StoragePreview и его рабочее состояние. Обновляет состояние объекта: content, data, entry, generation, kind, limit, loading, pane, path, pending_images, preview_revision, volume_id, ws.

```python
def __init__(self, pane)
```

Присваивания полям `self`: `content`, `data`, `entry`, `generation`, `kind`, `limit`, `loading`, `pane`, `path`, `pending_images`, `preview_revision`, `volume_id`, `ws`.

Прямые выражения вызова: `self.content.set_visibility`, `ui.column`, `ui.column().classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-snapshot"></a>

## `StoragePreview.snapshot`

[storage_preview_ui.py:57](../../storage_preview_ui.py#L57)

Возвращает компактное состояние превью для восстановления вкладки. Поля результата: volume_id, path, kind.

```python
def snapshot(self)
```

Прямые выражения вызова: `dict`.

Выражения возврата (ветви, без исполнения):

- `None`
- `dict(volume_id=self.volume_id, path=self.path, kind=self.kind)`


<a id="symbol-storagepreview-show"></a>

## `StoragePreview.show`

[storage_preview_ui.py:64](../../storage_preview_ui.py#L64)

Загружает выбранный объект или папку и отбрасывает устаревшие ответы. Обновляет состояние объекта: data, entry, generation, kind, limit, loading, path, preview_revision, volume_id.

```python
async def show(self, volume_id, entry)
```

Присваивания полям `self`: `data`, `entry`, `generation`, `kind`, `limit`, `loading`, `path`, `preview_revision`, `volume_id`.

Прямые выражения вызова: `data.get`, `data.get('volume', {}).get`, `dict`, `entry.get`, `relative_path`, `self.pending_images.clear`, [self.render](../../storage_preview_ui.py#L202), `self.ws.error_text`, `self.ws.is_photos`, `self.ws.notice`, `self.ws.persist_workspace`, `self.ws.read_directory`.

Перехватываемые типы: `Exception`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-storagepreview-open-folder"></a>

## `StoragePreview.open_folder`

[storage_preview_ui.py:110](../../storage_preview_ui.py#L110)

Открывает папку внутри текущей панели превью. Асинхронно ожидает: self.show.

```python
async def open_folder(self, path)
```

Прямые выражения вызова: `PurePosixPath`, `dict`, [self.show](../../storage_preview_ui.py#L64).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-parent"></a>

## `StoragePreview.parent`

[storage_preview_ui.py:115](../../storage_preview_ui.py#L115)

Переходит к родительскому пути текущего превью. Асинхронно ожидает: self.open_folder.

```python
async def parent(self)
```

Прямые выражения вызова: `PurePosixPath`, `relative_path`, [self.open_folder](../../storage_preview_ui.py#L110), `str`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-refresh"></a>

## `StoragePreview.refresh`

[storage_preview_ui.py:120](../../storage_preview_ui.py#L120)

Повторно загружает текущую папку или объект превью. Асинхронно ожидает: self.show.

```python
async def refresh(self)
```

Прямые выражения вызова: [self.show](../../storage_preview_ui.py#L64).

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-update-header"></a>

## `StoragePreview.update_header`

[storage_preview_ui.py:126](../../storage_preview_ui.py#L126)

Обновляет путь и подписи панели превью. Использует (self.entry or {}).get, data.get, pane.folder_size.set_visibility, pane.hidden.set_visibility, pane.location.set_visibility.

```python
def update_header(self)
```

Прямые выражения вызова: `(self.entry or {}).get`, `bool`, `data.get`, `len`, `pane.folder_size.set_visibility`, `pane.hidden.set_visibility`, `pane.location.set_visibility`, `pane.navigation.set_visibility`, `pane.parent_button.set_enabled`, `pane.path_bar.clear`, `pane.path_bar.set_visibility`, `pane.refresh_button.set_enabled`, `pane.render_path`, `pane.result_filter.set_visibility`, `pane.root_button.set_enabled`, `pane.toolbar.set_visibility`, `pane.update_volume_select`, `pane.volume_select.set_enabled`, `pane.volume_select.set_visibility`, `self.ws.format_date`, `self.ws.is_photos`, `ui.label`, `ui.label('Выбери папку или файл в соседнем дереве').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-image-url"></a>

## `StoragePreview.image_url`

[storage_preview_ui.py:158](../../storage_preview_ui.py#L158)

Выбирает URL готового Photos-превью или производного JPEG файлового тома. Использует entry.get, quote, self.ws.core_url.rstrip, str(large).lower, urlencode.

```python
def image_url(self, entry, *, large=False)
```

Прямые выражения вызова: `dict`, `entry.get`, `quote`, `self.ws.core_url.rstrip`, `str`, `str(large).lower`, `urlencode`.

Выражения возврата (ветви, без исполнения):

- `self.ws.core_url.rstrip('/') + f"/api/media/{entry['media_id']}/thumbnail?v={self.preview_revision or 0}"`
- `self.ws.core_url.rstrip('/') + f"/api/storage/volumes/{quote(self.volume_id, safe='')}/preview?" + urlencode(params)`


<a id="symbol-storagepreview-image"></a>

## `StoragePreview.image`

[storage_preview_ui.py:166](../../storage_preview_ui.py#L166)

Создаёт элемент изображения с выбранным размером превью. Использует entry.get, preview.add_slot, self.image_url, ui.image, ui.image(self.image_url(entry, large=large)).props.

```python
def image(self, entry, *, large=False)
```

Прямые выражения вызова: `entry.get`, `preview.add_slot`, [self.image_url](../../storage_preview_ui.py#L158), `ui.image`, `ui.image(self.image_url(entry, large=large)).props`, `ui.image(self.image_url(entry, large=large)).props('fit=contain loading=lazy').classes`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-refresh-pending"></a>

## `StoragePreview.refresh_pending`

[storage_preview_ui.py:174](../../storage_preview_ui.py#L174)

Проверяет готовность ожидаемых Photos-превью и обновляет изображения. Обновляет состояние объекта: preview_revision.

```python
async def refresh_pending(self, revision)
```

Присваивания полям `self`: `preview_revision`.

Прямые выражения вызова: `dict`, `len`, `list`, `preview.set_source`, `range`, [self.image_url](../../storage_preview_ui.py#L158), `self.pending_images.pop`, `self.ws.request`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-storagepreview-more"></a>

## `StoragePreview.more`

[storage_preview_ui.py:193](../../storage_preview_ui.py#L193)

Догружает следующую страницу плиток текущей папки. Обновляет состояние объекта: data, limit.

```python
async def more(self)
```

Присваивания полям `self`: `data`, `limit`.

Прямые выражения вызова: `dict`, `len`, `self.data.get`, [self.render](../../storage_preview_ui.py#L202), `self.ws.read_directory`.

Явного `return` в собственном теле нет: обычное завершение возвращает `None`.


<a id="symbol-storagepreview-render"></a>

## `StoragePreview.render`

[storage_preview_ui.py:202](../../storage_preview_ui.py#L202)

Перерисовывает выбранный файл, состояние ожидания или плитки папки. Использует ' · '.join, Path, PurePosixPath, details.append, entry.get.

```python
def render(self)
```

Прямые выражения вызова: `' · '.join`, `Path`, `PurePosixPath`, `details.append`, `entry.get`, `media_kind`, `self.content.clear`, [self.image](../../storage_preview_ui.py#L166), `self.pending_images.clear`, [self.render_folder](../../storage_preview_ui.py#L238), [self.update_header](../../storage_preview_ui.py#L126), `self.ws.format_bytes`, `self.ws.format_date`, `ui.button`, `ui.button('К папке', icon='arrow_back', on_click=self.parent).props`, `ui.button('Открыть в Photos', icon='open_in_new', on_click=lambda : self.ws.open_photo(entry['media_id'])).props`, `ui.icon`, `ui.icon('link' if self.kind == 'symlink' else 'insert_drive_file', size='64px').classes`, `ui.label`, `ui.label(' · '.join(details)).classes`, `ui.label('Выбери папку или файл в соседнем дереве.').classes`, `ui.label('Для этого типа файла доступна информация без изображения.').classes`, `ui.label('Кадр видео').classes`, `ui.label(entry.get('name') or PurePosixPath(self.path).name).classes`.

Выражения возврата (ветви, без исполнения):

- `None`


<a id="symbol-storagepreview-render-folder"></a>

## `StoragePreview.render_folder`

[storage_preview_ui.py:238](../../storage_preview_ui.py#L238)

Показывает плитки папок и файлов с командами открытия и выбора. Использует Path, data.get, e['name'].startswith, entry.get, media_kind.

```python
def render_folder(self)
```

Прямые выражения вызова: `Path`, `data.get`, `e['name'].startswith`, `entry.get`, `len`, `media_kind`, [self.image](../../storage_preview_ui.py#L166), `self.ws.is_photos`, `ui.button`, `ui.button(f'Показать ещё ({total - self.limit})', on_click=self.more).props`, `ui.button(on_click=lambda e=entry: self.show(self.volume_id, e)).props`, `ui.button(on_click=lambda e=entry: self.show(self.volume_id, e)).props('flat no-caps').classes`, `ui.element`, `ui.element('div').classes`, `ui.icon`, `ui.label`, `ui.label('Нет видимых элементов' if data.get('entries') else 'Папка пуста' if data.get('scanned_at') else 'Снимок папки не сохранён.').classes`, `ui.label('Читаю папку…').classes`, `ui.label(data['error']).classes`, `ui.label(entry['name']).classes`, `ui.row`, `ui.row().classes`, `ui.spinner`, `{'directory': 'folder', 'symlink': 'link', 'mount': 'storage'}.get`.

Выражения возврата (ветви, без исполнения):

- `None`
