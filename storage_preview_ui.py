"""A pane-local preview follows selections from the opposite tree."""
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlencode

from nicegui import ui

from media_manager.scanner import media_kind
from media_manager.storage import relative_path


PREVIEW_CSS = '''
.pane-mode .q-btn { min-height:25px; padding:2px 7px; font-size:11px; }
.pane-mode { flex-shrink:0; }
.commander-pane .pane-heading { flex:1; min-width:0; overflow:hidden; }
.pane-heading .q-btn__content { flex-wrap:nowrap; white-space:nowrap; justify-content:flex-start; overflow:hidden; }
.pane-heading .block { overflow:hidden; text-overflow:ellipsis; }
.storage-preview { flex:1; min-height:0; width:100%; overflow:auto; padding:12px; gap:12px; align-content:start; }
.preview-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(120px,1fr)); gap:10px; width:100%; }
.preview-tile.q-btn { width:100%; min-width:0; padding:0; border:0; background:transparent; align-self:start; }
.preview-tile .q-btn__content { width:100%; display:flex; flex-direction:column; gap:4px; flex-wrap:nowrap; }
.preview-tile .q-img { width:100%; height:100px; border-radius:2px; background:transparent; }
.preview-tile-symbol { display:flex; align-items:center; justify-content:center; width:100%; height:100px; color:#6a94b1; }
.preview-tile-name { width:100%; font-size:11px; line-height:14px; color:#65715f; text-align:center; overflow-wrap:anywhere; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.preview-image { width:100%; min-height:220px; height:clamp(220px,48vh,650px); background:#f3f5ef; border-radius:6px; }
.preview-title { font-size:15px; font-weight:600; overflow-wrap:anywhere; }
.preview-info { font-size:12px; color:#75806e; overflow-wrap:anywhere; }
.preview-image-error { display:flex; align-items:center; justify-content:center; text-align:center; padding:12px; width:100%; height:100%; font-size:12px; color:#788173; background:#f3f5ef; }
.preview-connection { color:#3f7a9f; border-color:#adc8da; background:#ecf5fc; }
.commander-trees.preview-linked .commander-pane { border-color:#b1c9d8; }
.commander-trees.preview-linked .commander-pane.active-pane { border-color:#6d9fbb; }
'''


# Управляет превью выбранного файла или плитками папки одной панели.
# Зависимости конструктора: pane.
class StoragePreview:
    # Инициализирует StoragePreview и его рабочее состояние.
    # Обновляет состояние объекта: content, data, entry, generation, kind, limit, loading, pane, path, pending_images, preview_revision, volume_id, ws.
    def __init__(self, pane):
        self.pane = pane
        self.ws = pane.workspace
        self.volume_id = None
        self.path = ''
        self.kind = 'directory'
        self.entry = None
        self.data = None
        self.loading = False
        self.generation = 0
        self.limit = 120
        self.pending_images = {}
        self.preview_revision = None
        self.content = ui.column().classes('storage-preview')
        self.content.set_visibility(False)

    # Возвращает компактное состояние превью для восстановления вкладки.
    # Поля результата: volume_id, path, kind.
    def snapshot(self):
        if self.volume_id is None:
            return None
        return dict(volume_id=self.volume_id, path=self.path, kind=self.kind)

    # Загружает выбранный объект или папку и отбрасывает устаревшие ответы.
    # Обновляет состояние объекта: data, entry, generation, kind, limit, loading, path, preview_revision, volume_id.
    async def show(self, volume_id, entry):
        self.generation += 1
        generation = self.generation
        self.volume_id = volume_id
        self.path = relative_path(entry['path'])
        self.kind = entry['kind']
        self.entry = dict(entry)
        self.pending_images.clear()
        self.preview_revision = None
        self.data = None
        self.limit = 120
        self.loading = self.kind == 'directory'
        self.pane.path_signature = None
        self.render()
        self.ws.persist_workspace()
        if volume_id and self.ws.is_photos(volume_id) and self.kind == 'file' and not entry.get('media_id'):
            try:
                data = await self.ws.read_directory(volume_id, self.path)
                if generation == self.generation:
                    self.entry = data['entry']
                    self.render()
            except Exception as error:
                self.ws.notice(error)
        if not volume_id or self.kind != 'directory':
            return
        try:
            data = await self.ws.read_directory(volume_id, self.path, limit=300)
            if generation != self.generation or self.ws.client.is_deleted:
                return
            self.data = data
            self.render()
            if data.get('volume', {}).get('availability') == 'online':
                data = await self.ws.read_directory(volume_id, self.path, refresh=True)
                if generation != self.generation or self.ws.client.is_deleted:
                    return
                self.data = data
        except Exception as error:
            if generation != self.generation or self.ws.client.is_deleted:
                return
            self.data = dict(self.data or {}, error=self.ws.error_text(error), cached=True)
        if generation == self.generation and not self.ws.client.is_deleted:
            self.loading = False
            self.render()

    # Открывает папку внутри текущей панели превью.
    # Асинхронно ожидает: self.show.
    async def open_folder(self, path):
        await self.show(self.volume_id, dict(path=path, kind='directory', name=PurePosixPath(path).name))

    # Переходит к родительскому пути текущего превью.
    # Асинхронно ожидает: self.open_folder.
    async def parent(self):
        await self.open_folder(relative_path(str(PurePosixPath(self.path).parent)))

    # Повторно загружает текущую папку или объект превью.
    # Асинхронно ожидает: self.show.
    async def refresh(self):
        if self.volume_id:
            await self.show(self.volume_id, self.entry)

    # Обновляет путь и подписи панели превью.
    # Использует (self.entry or {}).get, data.get, pane.folder_size.set_visibility, pane.hidden.set_visibility, pane.location.set_visibility.
    def update_header(self):
        pane = self.pane
        pane.heading.text = pane.title
        pane.location.set_visibility(True)
        pane.path_bar.set_visibility(True)
        pane.navigation.set_visibility(True)
        pane.toolbar.set_visibility(True)
        pane.result_filter.set_visibility(False)
        pane.folder_size.set_visibility(False)
        pane.volume_select.set_visibility(True)
        pane.volume_select.set_enabled(True)
        pane.update_volume_select(self.volume_id)
        pane.hidden.set_visibility(not self.ws.is_photos(self.volume_id))
        pane.parent_button.set_enabled(bool(self.volume_id and self.path))
        pane.root_button.set_enabled(bool(self.volume_id and self.path))
        pane.refresh_button.set_enabled(bool(self.volume_id and not self.loading))
        if self.volume_id:
            pane.render_path(self.volume_id, self.path, self.kind, navigate=self.open_folder,
                             entry_name=(self.entry or {}).get('name'))
        else:
            pane.path_bar.clear()
            pane.path_signature = None
            with pane.path_bar:
                ui.label('Выбери папку или файл в соседнем дереве').classes('pane-path-prefix')
        pane.snapshot_label.text = 'Плитки папки' if self.kind == 'directory' else 'Превью файла'
        data = self.data or {}
        pane.footer.text = ('Читаю папку…' if self.loading else
                            'Сохранённый список · ' + self.ws.format_date(data.get('scanned_at')) if data.get('cached') else
                            f"Элементов: {data.get('total', len(data.get('entries', [])))}" if self.kind == 'directory' else 'Превью · оригинал только для чтения')

    # Выбирает URL готового Photos-превью или производного JPEG файлового тома.
    # Использует entry.get, quote, self.ws.core_url.rstrip, str(large).lower, urlencode.
    def image_url(self, entry, *, large=False):
        if entry.get('media_id'):
            return self.ws.core_url.rstrip('/') + f"/api/media/{entry['media_id']}/thumbnail?v={self.preview_revision or 0}"
        params = dict(path=entry['path'], large=str(large).lower(), v=entry.get('modified_at') or entry.get('mtime_ns') or '')
        return self.ws.core_url.rstrip('/') + f'/api/storage/volumes/{quote(self.volume_id, safe="")}/preview?' + urlencode(params)

    # Создаёт элемент изображения с выбранным размером превью.
    # Использует entry.get, preview.add_slot, self.image_url, ui.image, ui.image(self.image_url(entry, large=large)).props.
    def image(self, entry, *, large=False):
        preview = ui.image(self.image_url(entry, large=large)).props('fit=contain loading=lazy').classes('preview-image' if large else '')
        preview.add_slot('error', '<div class="preview-image-error">Превью недоступно</div>')
        if entry.get('media_id') and not entry.get('preview_ready'):
            self.pending_images[entry['media_id']] = (preview, entry)

    # Проверяет готовность ожидаемых Photos-превью и обновляет изображения.
    # Обновляет состояние объекта: preview_revision.
    async def refresh_pending(self, revision):
        if not self.pending_images or self.preview_revision == revision or self.loading:
            return
        self.preview_revision = revision
        generation = self.generation
        items = dict(self.pending_images)
        for offset in range(0, len(items), 1000):
            ids = list(items)[offset:offset + 1000]
            data = await self.ws.request('GET', f'/api/photos/libraries/{self.volume_id[7:]}/preview-status', params={'ids': ids})
            if generation != self.generation or self.ws.client.is_deleted:
                return
            for media_id in data['ready']:
                preview, entry = items[media_id]
                entry['preview_ready'] = True
                preview.set_source(self.image_url(entry))
                self.pending_images.pop(media_id, None)

    # Догружает следующую страницу плиток текущей папки.
    # Обновляет состояние объекта: data, limit.
    async def more(self):
        self.limit += 120
        if self.data and self.data.get('has_more') and self.limit > len(self.data['entries']):
            data = await self.ws.read_directory(self.volume_id, self.path, offset=len(self.data['entries']), limit=300)
            self.data = dict(data, entries=self.data['entries'] + data['entries'])
        self.render()

    # Перерисовывает выбранный файл, состояние ожидания или плитки папки.
    # Использует ' · '.join, Path, PurePosixPath, details.append, entry.get.
    def render(self):
        if self.pane.view_mode != 'preview':
            return
        self.update_header()
        self.content.clear()
        self.pending_images.clear()
        with self.content:
            if not self.volume_id:
                ui.label('Выбери папку или файл в соседнем дереве.').classes('s-muted text-sm')
                return
            if self.kind == 'directory':
                self.render_folder()
                return
            if self.path:
                ui.button('К папке', icon='arrow_back', on_click=self.parent).props('flat dense no-caps color=dark')
            entry = self.entry or {}
            ui.label(entry.get('name') or PurePosixPath(self.path).name).classes('preview-title')
            kind = entry.get('media_kind') or media_kind(Path(entry.get('name') or self.path))
            if self.kind == 'file' and kind:
                self.image(entry, large=True)
                if kind == 'video':
                    ui.label('Кадр видео').classes('preview-info')
                if entry.get('media_id'):
                    ui.button('Открыть в Photos', icon='open_in_new', on_click=lambda: self.ws.open_photo(entry['media_id'])).props('flat dense no-caps color=dark')
            else:
                ui.icon('link' if self.kind == 'symlink' else 'insert_drive_file', size='64px').classes('s-muted')
                ui.label('Для этого типа файла доступна информация без изображения.').classes('preview-info')
            details = []
            if entry.get('size') is not None:
                details.append(self.ws.format_bytes(entry['size']))
            if entry.get('modified_at'):
                details.append(self.ws.format_date(entry['modified_at']))
            ui.label(' · '.join(details)).classes('preview-info')

    # Показывает плитки папок и файлов с командами открытия и выбора.
    # Использует Path, data.get, e['name'].startswith, entry.get, media_kind.
    def render_folder(self):
        data = self.data or {}
        if data.get('error'):
            ui.label(data['error']).classes('s-error w-full')
        if self.loading:
            with ui.row().classes('items-center gap-2'):
                ui.spinner(size='18px')
                ui.label('Читаю папку…').classes('preview-info')
        if self.loading and not self.data:
            return
        entries = [e for e in data.get('entries', []) if self.ws.is_photos(self.volume_id) or self.pane.hidden.value or not e['name'].startswith('.')]
        if not entries:
            ui.label('Нет видимых элементов' if data.get('entries') else 'Папка пуста' if data.get('scanned_at') else 'Снимок папки не сохранён.').classes('preview-info')
            return
        with ui.element('div').classes('preview-grid'):
            for entry in entries[:self.limit]:
                with ui.button(on_click=lambda e=entry: self.show(self.volume_id, e)).props('flat no-caps').classes('preview-tile'):
                    kind = (entry.get('media_kind') or media_kind(Path(entry['name']))) if entry['kind'] == 'file' else None
                    if kind:
                        self.image(entry)
                    else:
                        with ui.element('div').classes('preview-tile-symbol'):
                            ui.icon({'directory': 'folder', 'symlink': 'link', 'mount': 'storage'}.get(entry['kind'], 'insert_drive_file'), size='52px')
                    ui.label(entry['name']).classes('preview-tile-name')
        total = data.get('total', len(entries))
        if total > self.limit:
            ui.button(f'Показать ещё ({total - self.limit})', on_click=self.more).props('flat no-caps color=dark')
