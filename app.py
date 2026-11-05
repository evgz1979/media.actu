from __future__ import annotations

import asyncio
import json
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

from media_manager.catalog import Catalog
from media_manager.photos_adapter import (
    PhotosAccessDenied,
    PhotosAdapterError,
    PhotosLibraryUnavailable,
    SystemPhotosAdapter,
)
from media_manager.scanner import scan_sources
from media_manager.thumbnails import ThumbnailCacheUnavailable, ThumbnailService
from media_manager.thumbnail_workers import ThumbnailWorkerPool
from media_manager.watcher import SourceWatcher
from media_manager.storage import StorageCatalog
from media_manager.network import NetworkCatalog, NetworkError
from media_manager.comparison import ComparisonCatalog
from media_manager.copies import CopyCatalog, COPY_KINDS, FOLDER_LABELS
from media_manager.folder_tracking import FolderTrackingService
from media_manager.folder_markers import FolderMarkerService
from media_manager.paired_comparison import PairedComparisonCatalog, DECISIONS
from media_manager.copy_files import MissingCopyCatalog
from media_manager.directory_sizes import DirectorySizeService
from media_manager.storage_previews import StoragePreviewService
from media_manager.photo_libraries import PhotoLibraries
from media_manager.photos_browser import PhotosBrowser
from media_manager.photos_originals import PhotosOriginals
from media_manager.photos_schedule import PhotosSyncSchedule


ROOT = Path(__file__).parent
DATA_DIR = Path(os.environ.get("MEDIA_ACTU_DATA_DIR", str(ROOT / "data"))).expanduser()


#: Выбирает каталог превью из config.local.json либо MEDIA_ACTU_DATA_DIR.
#: Использует Path, Path(str(configured)).expanduser, config_path.is_file, config_path.read_text, json.loads.
def local_thumbnail_cache_directory() -> Path:
    config_path = ROOT / "config.local.json"
    if not config_path.is_file():
        return DATA_DIR / "thumbnails"
    settings = json.loads(config_path.read_text(encoding="utf-8"))
    configured = settings.get("thumbnail_cache_directory")
    return Path(str(configured)).expanduser() if configured else DATA_DIR / "thumbnails"


catalog = Catalog(DATA_DIR / "catalog.sqlite3")
storage = StorageCatalog(DATA_DIR / "storage.sqlite3")
network = NetworkCatalog(storage)
comparison = ComparisonCatalog(storage)
copies = CopyCatalog(storage)
folder_tracking = FolderTrackingService(copies)
folder_markers = FolderMarkerService(copies)
paired_comparison = PairedComparisonCatalog(storage, copies, comparison)
missing_copies = MissingCopyCatalog(paired_comparison)
directory_sizes = DirectorySizeService(storage)
comparison_gate = threading.RLock()
photos_adapter = SystemPhotosAdapter(ROOT / "photos_adapter", DATA_DIR / "native")
photo_libraries = PhotoLibraries(catalog, storage, photos_adapter)
photos_browser = PhotosBrowser(photo_libraries)
photos_originals_adapter = SystemPhotosAdapter(ROOT / "photos_adapter", DATA_DIR / "native")
photos_originals = PhotosOriginals(photo_libraries, photos_originals_adapter)
photo_libraries.originals = photos_originals
photos_schedule = PhotosSyncSchedule(photo_libraries, photos_originals)
thumbnails = ThumbnailService(catalog, local_thumbnail_cache_directory(), photos_adapter, photo_libraries)
storage_previews = StoragePreviewService(storage, local_thumbnail_cache_directory())
thumbnail_workers = ThumbnailWorkerPool(catalog, thumbnails)
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="media-scan")
scan_locks: dict[int, threading.Lock] = {}


#: Сканирует один источник под отдельной блокировкой и обновляет его состояние.
#: Явно отклоняет недопустимое состояние через KeyError.
def scan_source(source_id: int) -> dict[str, object]:
    source = catalog.get_source(source_id)
    if source is None:
        raise KeyError(source_id)
    lock = scan_locks.setdefault(source_id, threading.Lock())
    if not lock.acquire(blocking=False):
        return {"source_id": source_id, "status": "already_scanning"}
    try:
        if source.get('kind') == 'photos':
            photo_libraries._require_active(source_id)
        catalog.set_source_status(source_id, "scanning")
        if source.get("kind") == "photos":
            assets = photo_libraries.scan(source_id)
            thumbnail_workers.wake()
            return {"source_id": source_id, "total": len(assets)}
        report = scan_sources([str(source["path"])])
        catalog.replace_source_scan(source_id, report)
        catalog.enqueue_source_thumbnails(source_id)
        catalog.set_source_status(
            source_id,
            "warning" if report.errors else "idle",
            "\n".join(error.message for error in report.errors[:20]) or None,
        )
        thumbnail_workers.wake()
        return {"source_id": source_id, **report.to_dict()["summary"]}
    except Exception as error:
        catalog.set_source_status(source_id, "error", str(error))
        raise
    finally:
        lock.release()


#: Ставит сканирование источника в пул из двух потоков Core.
#: Использует catalog.set_source_status, executor.submit.
def schedule_scan(source_id: int) -> None:
    catalog.set_source_status(source_id, "scanning")
    executor.submit(scan_source, source_id)


watcher = SourceWatcher(schedule_scan)


#: Запускает фоновые службы FastAPI и закрывает их при завершении Core.
#: Асинхронно ожидает: asyncio.to_thread.
@asynccontextmanager
async def lifespan(_: FastAPI):
    watcher.start()
    folder_tracking.start()
    folder_markers.start()
    catalog.reset_stale_source_scans()
    if photos_adapter.supported:
        await asyncio.to_thread(photo_libraries.refresh_connection)
    for source in catalog.list_sources():
        if source.get("kind") == "photos":
            profile = photo_libraries.profile(int(source['id']))
            if profile['active'] and (
                int(source.get("media_count") or 0) == 0
                or not source.get("last_scan_at")
            ):
                schedule_scan(int(source["id"]))
            continue
        source_path = Path(str(source["path"]))
        if source_path.is_dir():
            watcher.watch(int(source["id"]), source_path)
            schedule_scan(int(source["id"]))
    photos_schedule.start()
    thumbnail_workers.start()
    #: Проверяет подключение Photos каждые 30 секунд и пробуждает очередь превью.
    #: Асинхронно ожидает: asyncio.sleep, asyncio.to_thread.
    async def monitor_libraries():
        while True:
            await asyncio.sleep(30)
            await asyncio.to_thread(photo_libraries.refresh_connection,
                                    restart=photo_libraries.connection.get('state') != 'ready')
            thumbnail_workers.wake()
    photos_monitor = asyncio.create_task(monitor_libraries()) if photos_adapter.supported else None
    yield
    if photos_monitor:
        photos_monitor.cancel()
    folder_tracking.close()
    folder_markers.close()
    directory_sizes.close()
    photos_schedule.close()
    photos_originals.close()
    missing_copies.close()
    paired_comparison.close()
    comparison.close()
    watcher.stop()
    thumbnail_workers.stop()
    photos_adapter.close()
    executor.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="media.actu Core",
    version="0.1.0-dev",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)


#: Определяет Pydantic-контракт регистрации обычного источника.
#: Поля: path, role, label, comment.
class SourceRequest(BaseModel):
    path: str
    role: Literal["source", "storage"] = "source"
    label: str = ""
    comment: str = ""


#: Определяет Pydantic-контракт выбора папок macOS.
#: Поля: role, label, comment.
class FolderChoiceRequest(BaseModel):
    role: Literal["source", "storage"] = "source"
    label: str = ""
    comment: str = ""


#: Определяет Pydantic-контракт изменения метаданных источника.
#: Поля: role, label, comment.
class SourceMetadataRequest(BaseModel):
    role: Literal["source", "storage"]
    label: str = ""
    comment: str = ""


#: Определяет Pydantic-контракт открытия папки источника.
#: Поля: folder.
class FolderRequest(BaseModel):
    folder: str = ""


#: Открывает системный диалог выбора нескольких папок на машине Core.
#: Явно отклоняет недопустимое состояние через RuntimeError.
def choose_folders_macos(prompt: str) -> list[str]:
    script = f"""
set chosenFolders to choose folder with prompt "{prompt}" with multiple selections allowed
set output to ""
repeat with chosenFolder in chosenFolders
    set output to output & POSIX path of chosenFolder & linefeed
end repeat
return output
"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    if result.returncode != 0:
        if "User canceled" in result.stderr or "-128" in result.stderr:
            return []
        raise RuntimeError(result.stderr.strip() or "Не удалось открыть выбор папки")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


#: Возвращает готовность HTTP-процесса и текущую ревизию каталога.
#: Поля результата: status, revision.
@app.get("/health")
async def health() -> dict[str, object]:
    return {"status": "ok", "revision": catalog.revision()}


#: Определяет Pydantic-контракт отметок файлового расположения.
#: Поля: path, purpose, role, no_duplicate, planned_move, comment.
class StorageMetadataRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = ""
    purpose: Literal["", "media", "documents", "projects", "mixed"] | None = None
    role: Literal["", "primary", "copy", "archive", "temporary"] | None = None
    no_duplicate: bool | None = None
    planned_move: bool | None = None
    comment: str = Field(default="", max_length=4000)


#: Определяет Pydantic-контракт меток папки.
#: Поля: path, tags.
class FolderTagsRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    path: str = Field(default='', max_length=4096)
    tags: list[Literal['old_copy', 'sort', 'check']] = Field(max_length=3)


#: Возвращает обнаруженные и сохранённые тома через API Core.
#: Асинхронно ожидает: asyncio.to_thread.
@app.get("/api/storage/volumes")
async def storage_volumes(refresh: bool = False) -> dict:
    return await asyncio.to_thread(storage.refresh, refresh)


#: Определяет Pydantic-контракт названия сменного носителя.
#: Поля: name.
class VolumeNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120)


#: Регистрирует сменный носитель с выбранным названием.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/storage/volumes/{volume_id}/register-removable")
async def register_removable(volume_id: str, request: VolumeNameRequest) -> dict:
    try:
        return await asyncio.to_thread(storage.register_removable, volume_id, request.name)
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Меняет название подтверждённого сменного носителя.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.patch('/api/storage/volumes/{volume_id}/name')
async def rename_removable(volume_id: str, request: VolumeNameRequest) -> dict:
    try:
        return await asyncio.to_thread(storage.rename_removable, volume_id, request.name)
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Определяет Pydantic-контракт запоминания SMB-ресурса.
#: Поля: share.
class NetworkShareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    share: str = Field(min_length=1, max_length=255)


#: Возвращает список сохранённых серверов NAS.
#: Асинхронно ожидает: asyncio.to_thread.
@app.get("/api/storage/nas")
async def remembered_nas() -> dict:
    return await asyncio.to_thread(network.servers)


#: Запускает обнаружение NAS через Bonjour на машине Core.
#: Асинхронно ожидает: asyncio.to_thread.
@app.post("/api/storage/nas/discover")
async def discover_nas() -> dict:
    return await asyncio.to_thread(network.scan)


#: Возвращает сохранённые либо обновлённые ресурсы выбранного NAS.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get("/api/storage/nas/{server_id}/shares")
async def nas_shares(server_id: str, refresh: bool = False) -> dict:
    try:
        return await asyncio.to_thread(network.shares, server_id, refresh)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="NAS не найден") from error


#: Сохраняет выбранный SMB-ресурс без подключения.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/storage/nas/{server_id}/remember")
async def remember_nas_share(server_id: str, request: NetworkShareRequest) -> dict:
    try:
        return await asyncio.to_thread(network.remember, server_id, request.share)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except NetworkError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Открывает подключение сетевого тома в Finder на машине Core.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/storage/volumes/{volume_id}/connect")
async def connect_network_volume(volume_id: str) -> dict:
    try:
        return await asyncio.to_thread(network.open_in_finder, volume_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Том не найден") from error
    except NetworkError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Возвращает список выбранной папки тома с признаками снимка и ошибок.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get("/api/storage/volumes/{volume_id}/directory")
async def storage_directory(volume_id: str, path: str = "", refresh: bool = True, discover: bool = True) -> dict:
    try:
        return await asyncio.to_thread(storage.directory, volume_id, path, refresh, discover=discover)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Том не найден") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Возвращает JPEG-превью обычного файла выбранного тома.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get('/api/storage/volumes/{volume_id}/preview')
async def storage_preview(volume_id: str, path: str, large: bool = False) -> FileResponse:
    try:
        target = await asyncio.to_thread(storage_previews.get_or_create, volume_id, path, large=large)
    except KeyError as error:
        raise HTTPException(status_code=404, detail='Том не найден') from error
    except ThumbnailCacheUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return FileResponse(target, media_type='image/jpeg', headers={'Cache-Control': 'no-cache'})


#: Определяет Pydantic-контракт открытия пути тома.
#: Поля: path.
class StoragePathRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    path: str = Field(default='', max_length=4096)


#: Определяет Pydantic-контракт подсчёта размеров папок.
#: Поля: paths, start, refresh.
class DirectorySizesRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    paths: list[str] = Field(min_length=1, max_length=500)
    start: bool = True
    refresh: bool = False


#: Возвращает размеры папок и при разрешении ставит их в очередь подсчёта.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post('/api/storage/volumes/{volume_id}/directory-sizes')
async def storage_directory_sizes(volume_id: str, request: DirectorySizesRequest) -> dict:
    try:
        return await asyncio.to_thread(directory_sizes.request, volume_id, request.paths,
                                       start=request.start, refresh=request.refresh)
    except KeyError as error:
        raise HTTPException(status_code=404, detail='Том не найден') from error
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Передаёт Finder проверенный путь выбранного тома.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post('/api/storage/volumes/{volume_id}/open-in-finder')
async def open_storage_path_in_finder(volume_id: str, request: StoragePathRequest) -> dict:
    try:
        return await asyncio.to_thread(storage.open_in_finder, volume_id, request.path)
    except KeyError as error:
        raise HTTPException(status_code=404, detail='Том не найден') from error
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Сохраняет пользовательские отметки расположения в каталоге.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.patch("/api/storage/volumes/{volume_id}/metadata")
async def storage_metadata(volume_id: str, request: StorageMetadataRequest) -> dict:
    try:
        return await asyncio.to_thread(storage.annotate, volume_id, request.path, request.model_dump(exclude={"path"}))
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Том не найден") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Сохраняет смысловые метки выбранной папки.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.patch('/api/storage/volumes/{volume_id}/folder-tags')
async def storage_folder_tags(volume_id: str, request: FolderTagsRequest) -> dict:
    try:
        return await asyncio.to_thread(storage.set_folder_tags, volume_id, request.path, request.tags)
    except KeyError as error:
        raise HTTPException(status_code=404, detail='Том не найден') from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Определяет Pydantic-контракт области сверки на файловом томе.
#: Поля: volume_id, path.
class ComparisonScope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    volume_id: str = Field(min_length=1, max_length=128)
    path: str = Field(default="", max_length=4096)


#: Определяет Pydantic-контракт привязки папки-копии.
#: Поля: kind.
class CopyLocationRequest(ComparisonScope):
    kind: Literal['copy', 'cold', 'cloud'] = 'copy'


#: Определяет Pydantic-контракт типа копии.
#: Поля: kind.
class CopyKindRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['copy', 'cold', 'cloud']


#: Определяет Pydantic-контракт снимка текущего номера копии.
#: Поля: id, number.
class CopyNumberSnapshot(CopyKindRequest):
    id: str = Field(min_length=1, max_length=128)
    number: int = Field(gt=0)


#: Определяет Pydantic-контракт освобождения номера копии.
#: Поля: number.
class CopyNumberReleaseRequest(CopyKindRequest):
    number: int = Field(gt=0, strict=True)


#: Определяет Pydantic-контракт перенумерации копий.
#: Поля: copies.
class CopyRenumberRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    copies: list[CopyNumberSnapshot]


#: Определяет Pydantic-контракт настроек основной папки.
#: Поля: tracking, label.
class CopyGroupSettingsRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tracking: bool | None = Field(default=None, strict=True)
    label: Literal['', 'temporary', 'inbox', 'archive'] | None = None


#: Определяет Pydantic-контракт подтверждения версии изменения.
#: Поля: changed_at.
class CopyGroupAcknowledgeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    changed_at: str = Field(min_length=1, max_length=64)


#: Определяет Pydantic-контракт подключения или отключения связи.
#: Поля: connected.
class CopyConnectionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    connected: bool = Field(strict=True)


#: Определяет Pydantic-контракт выбора источника копирования.
#: Поля: source_id.
class CopySourceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source_id: str | None = Field(default=None, min_length=1, max_length=128)


#: Меняет источник копии под общей блокировкой запуска сверок.
#: Явно отклоняет недопустимое состояние через ValueError.
def set_folder_copy_source(location_id, source_id):
    with comparison_gate:
        if paired_comparison.busy():
            raise ValueError('Сначала приостанови сверку или дождись завершения копирования')
        return copies.set_copy_source(location_id, source_id)


#: Обрабатывает изменение источника копирования обычной папки.
#: Асинхронно ожидает: copy_catalog_action.
@app.patch('/api/storage/copy-locations/{location_id}/source')
async def storage_copy_source(location_id: str, request: CopySourceRequest) -> dict:
    return await copy_catalog_action(set_folder_copy_source, location_id, request.source_id)


#: Меняет подключение связи с защитой от конфликтующего копирования.
#: Явно отклоняет недопустимое состояние через ValueError.
def set_copy_connection(action, identifier, connected):
    with comparison_gate:
        if not connected and missing_copies.busy():
            raise ValueError('Сначала дождись завершения копирования.')
        return action(identifier, connected)


#: Выполняет команду каталога копий в потоке и пробуждает запись маркеров.
#: Явно отклоняет недопустимое состояние через HTTPException.
async def copy_catalog_action(action, *args):
    try:
        result = await asyncio.to_thread(action, *args)
        folder_markers.wake()
        return result
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Возвращает наборы папок с типами, метками и состоянием наблюдателей.
#: Поля результата: groups, kinds, labels.
@app.get('/api/storage/copy-groups')
async def storage_copy_groups() -> dict:
    groups = await copy_catalog_action(copies.groups)
    return {'groups': [dict(group, **folder_tracking.status(group['id'])) for group in groups],
            'kinds': COPY_KINDS, 'labels': FOLDER_LABELS}


#: Возвращает состояние очереди служебных описаний папок.
#: Асинхронно ожидает: asyncio.to_thread.
@app.get('/api/storage/folder-markers')
async def storage_folder_markers() -> dict:
    return await asyncio.to_thread(folder_markers.status)


#: Регистрирует выбранную папку как основную область набора.
#: Асинхронно ожидает: copy_catalog_action.
@app.post('/api/storage/copy-groups')
async def storage_main_folder(request: ComparisonScope) -> dict:
    return await copy_catalog_action(copies.create_main, request.volume_id, request.path)


#: Обновляет настройки набора и пробуждает отслеживание изменений.
#: Асинхронно ожидает: copy_catalog_action.
@app.patch('/api/storage/copy-groups/{group_id}')
async def storage_copy_group_settings(group_id: str, request: CopyGroupSettingsRequest) -> dict:
    result = await copy_catalog_action(copies.update_group, group_id, request.model_dump(exclude_unset=True))
    folder_tracking.wake()
    return result


#: Подтверждает конкретную версию уведомления об изменении папки.
#: Асинхронно ожидает: copy_catalog_action.
@app.post('/api/storage/copy-groups/{group_id}/acknowledge')
async def storage_acknowledge_folder_changes(group_id: str, request: CopyGroupAcknowledgeRequest) -> dict:
    return await copy_catalog_action(copies.acknowledge_changes, group_id, request.changed_at)


#: Меняет подключение всего набора папок.
#: Асинхронно ожидает: copy_catalog_action.
@app.patch('/api/storage/copy-groups/{group_id}/connection')
async def storage_copy_group_connection(group_id: str, request: CopyConnectionRequest) -> dict:
    result = await copy_catalog_action(set_copy_connection, copies.set_group_connected, group_id, request.connected)
    folder_tracking.wake()
    return result


#: Меняет подключение одной обычной копии.
#: Асинхронно ожидает: copy_catalog_action.
@app.patch('/api/storage/copy-locations/{location_id}/connection')
async def storage_copy_location_connection(location_id: str, request: CopyConnectionRequest) -> dict:
    return await copy_catalog_action(set_copy_connection, copies.set_copy_connected, location_id, request.connected)


#: Добавляет папку копии к существующему набору.
#: Асинхронно ожидает: copy_catalog_action.
@app.post('/api/storage/copy-groups/{group_id}/copies')
async def storage_copy_location(group_id: str, request: CopyLocationRequest) -> dict:
    return await copy_catalog_action(copies.add_copy, group_id, request.volume_id, request.path, request.kind)


#: Освобождает подтверждённый номер под блокировкой запуска сверок.
#: Явно отклоняет недопустимое состояние через ValueError.
def release_copy_number(location_id, number, kind):
    with comparison_gate:
        if paired_comparison.busy():
            raise ValueError('Сначала дождись завершения сверки и копирования.')
        return copies.release_copy_number(location_id, number, kind)


#: Архивирует прежнюю привязку и освобождает её номер.
#: Асинхронно ожидает: copy_catalog_action.
@app.post('/api/storage/copy-locations/{location_id}/release-number')
async def storage_release_copy_number(location_id: str, request: CopyNumberReleaseRequest) -> dict:
    return await copy_catalog_action(release_copy_number, location_id, request.number, request.kind)


#: Меняет тип зарегистрированной копии.
#: Асинхронно ожидает: copy_catalog_action.
@app.patch('/api/storage/copy-locations/{location_id}')
async def storage_copy_kind(location_id: str, request: CopyKindRequest) -> dict:
    return await copy_catalog_action(copies.change_kind, location_id, request.kind)


#: Применяет подтверждённую нумерацию по снимку текущих связей.
#: Асинхронно ожидает: copy_catalog_action.
@app.post('/api/storage/copy-groups/{group_id}/renumber')
async def storage_renumber_copies(group_id: str, request: CopyRenumberRequest) -> dict:
    return await copy_catalog_action(copies.renumber_copies, group_id, [copy.model_dump() for copy in request.copies])


#: Удаляет связь копии из каталога без удаления пользовательских файлов.
#: Поля результата: removed.
@app.delete('/api/storage/copy-locations/{location_id}')
async def storage_remove_copy(location_id: str) -> dict:
    await copy_catalog_action(copies.remove_copy, location_id)
    return {'removed': True}


#: Удаляет набор папок из каталога без удаления пользовательских файлов.
#: Поля результата: removed.
@app.delete('/api/storage/copy-groups/{group_id}')
async def storage_remove_copy_group(group_id: str) -> dict:
    await copy_catalog_action(copies.remove_group, group_id)
    return {'removed': True}


#: Определяет Pydantic-контракт общей сверки имён.
#: Поля: source, targets, reread, reuse_index.
class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: ComparisonScope
    targets: list[ComparisonScope] = Field(min_length=1, max_length=16)
    reread: bool = False  # accepted for older clients; content is never read
    reuse_index: bool = True


#: Выполняет команду сверки в потоке и преобразует доменные ошибки в HTTP.
#: Явно отклоняет недопустимое состояние через HTTPException.
async def comparison_call(function, *args, **kwargs):
    try:
        return await asyncio.to_thread(function, *args, **kwargs)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, OSError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Проверяет отсутствие конфликтующей работы под общей блокировкой запуска.
#: Явно отклоняет недопустимое состояние через ValueError.
def start_comparison_exclusive(action, *args, **kwargs):
    with comparison_gate:
        if paired_comparison.busy():
            raise ValueError('Сверка пары ещё выполняется. Сначала останови её.')
        return action(*args, **kwargs)


#: Определяет Pydantic-контракт сверки связанной пары.
#: Поля: copy_id, mode, base_job_id, method.
class PairedComparisonRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    copy_id: str = Field(min_length=1, max_length=128)
    mode: Literal['folders', 'files'] = 'folders'
    base_job_id: str | None = None
    method: Literal['size', 'sha256'] = 'size'


#: Определяет Pydantic-контракт планового решения для лишнего элемента.
#: Поля: path, action.
class PairedDecisionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    path: str = Field(max_length=4096)
    action: Literal['keep', 'add_main', 'move', 'remove'] | None


#: Возвращает историю парных сверок и допустимые решения для лишних элементов.
#: Поля результата: jobs, decisions.
@app.get('/api/storage/paired-comparisons')
async def paired_jobs(copy_id: str | None = None) -> dict:
    return {'jobs': await comparison_call(paired_comparison.jobs, copy_id), 'decisions': DECISIONS}


#: Создаёт и запускает сверку зарегистрированной пары папок.
#: Асинхронно ожидает: comparison_call.
@app.post('/api/storage/paired-comparisons', status_code=201)
async def start_paired_comparison(request: PairedComparisonRequest) -> dict:
    return await comparison_call(start_comparison_exclusive, paired_comparison.create,
                                 request.copy_id, request.mode, request.base_job_id, method=request.method)


#: Возвращает состояние одной парной сверки.
#: Асинхронно ожидает: comparison_call.
@app.get('/api/storage/paired-comparisons/{job_id}')
async def paired_job(job_id: str) -> dict:
    return await comparison_call(paired_comparison.job, job_id)


#: Возвращает страницу выровненных строк парной сверки.
#: Асинхронно ожидает: comparison_call.
@app.get('/api/storage/paired-comparisons/{job_id}/rows')
async def paired_rows(job_id: str, offset: int = Query(0, ge=0), limit: int = Query(1000, ge=1, le=5000),
                      differences_only: bool = False) -> dict:
    return await comparison_call(paired_comparison.rows, job_id, offset, limit, differences_only)


#: Запрашивает паузу парной сверки.
#: Асинхронно ожидает: comparison_call.
@app.post('/api/storage/paired-comparisons/{job_id}/pause')
async def pause_paired_job(job_id: str) -> dict:
    return await comparison_call(paired_comparison.pause, job_id)


#: Продолжает парную сверку после проверки конфликтующих операций.
#: Асинхронно ожидает: comparison_call.
@app.post('/api/storage/paired-comparisons/{job_id}/resume')
async def resume_paired_job(job_id: str) -> dict:
    return await comparison_call(start_comparison_exclusive, paired_comparison.resume, job_id)


#: Сохраняет плановое решение для элемента только в копии.
#: Асинхронно ожидает: comparison_call.
@app.patch('/api/storage/paired-comparisons/{job_id}/decision')
async def paired_decision(job_id: str, request: PairedDecisionRequest) -> dict:
    return await comparison_call(paired_comparison.decide, job_id, request.path, request.action)


#: Возвращает историю общей сверки имён и старых отчётов.
#: Поля результата: jobs.
@app.get("/api/storage/comparisons")
async def comparison_jobs() -> dict:
    return {"jobs": await comparison_call(comparison.jobs)}


#: Создаёт сохранённый план копирования по завершённому файловому отчёту.
#: Асинхронно ожидает: comparison_call.
@app.post('/api/storage/paired-comparisons/{job_id}/copy-plan', status_code=201)
async def missing_copy_plan(job_id: str) -> dict:
    return await comparison_call(missing_copies.plan, job_id)


#: Возвращает состояние операции копирования отсутствующих элементов.
#: Асинхронно ожидает: comparison_call.
@app.get('/api/storage/copy-operations/{operation_id}')
async def missing_copy_job(operation_id: str) -> dict:
    return await comparison_call(missing_copies.job, operation_id)


#: Возвращает страницу элементов сохранённого плана копирования.
#: Асинхронно ожидает: comparison_call.
@app.get('/api/storage/copy-operations/{operation_id}/items')
async def missing_copy_items(operation_id: str, offset: int = Query(0, ge=0),
                             limit: int = Query(200, ge=1, le=1000)) -> dict:
    return await comparison_call(missing_copies.items, operation_id, offset, limit)


#: Запускает подтверждённую операцию создания отсутствующих копий.
#: Асинхронно ожидает: comparison_call.
@app.post('/api/storage/copy-operations/{operation_id}/start')
async def start_missing_copy(operation_id: str) -> dict:
    return await comparison_call(start_comparison_exclusive, missing_copies.start, operation_id)


#: Запрашивает остановку операции копирования.
#: Асинхронно ожидает: comparison_call.
@app.post('/api/storage/copy-operations/{operation_id}/stop')
async def stop_missing_copy(operation_id: str) -> dict:
    return await comparison_call(missing_copies.stop, operation_id)


#: Создаёт общую сверку имён исходной области и выбранных целей.
#: Асинхронно ожидает: comparison_call.
@app.post("/api/storage/comparisons", status_code=201)
async def start_comparison(request: ComparisonRequest) -> dict:
    return await comparison_call(start_comparison_exclusive, comparison.create, request.source.model_dump(),
                                 [t.model_dump() for t in request.targets], reuse_index=request.reuse_index)


#: Возвращает состояние и области общей сверки.
#: Асинхронно ожидает: comparison_call.
@app.get("/api/storage/comparisons/{job_id}")
async def comparison_job(job_id: str) -> dict:
    return await comparison_call(comparison.job, job_id)


#: Запрашивает паузу общей сверки имён.
#: Асинхронно ожидает: comparison_call.
@app.post("/api/storage/comparisons/{job_id}/pause")
async def pause_comparison(job_id: str) -> dict:
    return await comparison_call(comparison.pause, job_id)


#: Продолжает сверку имён либо создаёт новую вместо старой проверки содержимого.
#: Асинхронно ожидает: comparison_call.
@app.post("/api/storage/comparisons/{job_id}/resume")
async def resume_comparison(job_id: str) -> dict:
    return await comparison_call(start_comparison_exclusive, comparison.resume, job_id)


#: Возвращает страницу исходного дерева общей сверки с фильтром статуса.
#: Асинхронно ожидает: comparison_call.
@app.get("/api/storage/comparisons/{job_id}/tree")
async def comparison_tree(job_id: str, path: str | None = None, status: str = "",
                          offset: int = Query(0, ge=0), limit: int = Query(200, ge=1, le=500)) -> dict:
    return await comparison_call(comparison.tree, job_id, path, status, offset, limit)


#: Возвращает страницу сохранённого дерева выбранной цели общей сверки.
#: Асинхронно ожидает: comparison_call.
@app.get("/api/storage/comparisons/{job_id}/target-tree")
async def comparison_target_tree(job_id: str, scan_id: int = Query(..., ge=1), path: str | None = None,
                                 offset: int = Query(0, ge=0), limit: int = Query(200, ge=1, le=500)) -> dict:
    return await comparison_call(comparison.target_tree, job_id, scan_id, path, offset, limit)


#: Возвращает найденные совпадения и подробности элемента отчёта.
#: Асинхронно ожидает: comparison_call.
@app.get("/api/storage/comparisons/{job_id}/detail")
async def comparison_detail(job_id: str, path: str | None = None) -> dict:
    return await comparison_call(comparison.detail, job_id, path)


#: Возвращает события общей сверки с обратной пагинацией.
#: Поля результата: events.
@app.get("/api/storage/comparisons/{job_id}/events")
async def comparison_events(job_id: str, before: int | None = Query(None, ge=1)) -> dict:
    return {"events": await comparison_call(comparison.events, job_id, before)}


#: Возвращает сохранённые источники медиаиндекса.
#: Поля результата: sources, revision.
@app.get("/api/sources")
async def list_sources() -> dict[str, object]:
    return {"sources": catalog.list_sources(), "revision": catalog.revision()}


#: Регистрирует обычный источник, устанавливает наблюдение и запускает сканирование.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/sources")
async def create_source(request: SourceRequest) -> dict[str, object]:
    try:
        source = catalog.add_source(
            request.path,
            role=request.role,
            label=request.label,
            comment=request.comment,
        )
        watcher.watch(int(source["id"]), str(source["path"]))
        schedule_scan(int(source["id"]))
    except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"sources": catalog.list_sources()}


#: Регистрирует выбранные системным диалогом папки и запускает их сканирование.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/sources/choose")
async def choose_sources(request: FolderChoiceRequest) -> dict[str, object]:
    try:
        prompt = (
            "Выбери источник медиафайлов"
            if request.role == "source"
            else "Выбери хранилище копий"
        )
        selected = await asyncio.to_thread(choose_folders_macos, prompt)
        for path in selected:
            source = catalog.add_source(
                path,
                role=request.role,
                label=request.label,
                comment=request.comment,
            )
            watcher.watch(int(source["id"]), str(source["path"]))
            schedule_scan(int(source["id"]))
    except (RuntimeError, FileNotFoundError, NotADirectoryError, PermissionError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"cancelled": not selected, "sources": catalog.list_sources()}


#: Обновляет роль, название и комментарий обычного источника.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.patch("/api/sources/{source_id}")
async def update_source(
    source_id: int, request: SourceMetadataRequest
) -> dict[str, object]:
    try:
        source = catalog.update_source_metadata(
            source_id,
            role=request.role,
            label=request.label,
            comment=request.comment,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Папка не найдена") from error
    return {"source": source, "sources": catalog.list_sources()}


#: Снимает наблюдение и удаляет источник из медиаиндекса.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int) -> dict[str, object]:
    source = catalog.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    if source.get("kind") == "photos":
        raise HTTPException(
            status_code=400,
            detail="Предустановленный источник Photos нельзя удалить",
        )
    watcher.unwatch(source_id)
    catalog.remove_source(source_id)
    return {"sources": catalog.list_sources()}


#: Проверяет источник и выполняет его ручное сканирование.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/sources/{source_id}/scan")
async def scan_one_source(source_id: int) -> dict[str, object]:
    try:
        return await asyncio.to_thread(scan_source, source_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Источник не найден") from error
    except PhotosLibraryUnavailable as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PhotosAccessDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


#: Запускает сканирование зарегистрированных источников.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/scan")
async def scan_all_sources() -> dict[str, object]:
    sources = catalog.list_sources()
    if not sources:
        raise HTTPException(status_code=400, detail="Сначала добавь хотя бы один источник")
    results = []
    for source in sources:
        if source.get('kind') == 'photos' and not photo_libraries.profile(int(source['id']))['active']:
            results.append({'source_id': source['id'], 'status': 'offline'})
            continue
        if source.get("kind") == "photos" and source.get("status") == "no_access":
            results.append(
                {"source_id": int(source["id"]), "status": "no_access"}
            )
            continue
        results.append(await asyncio.to_thread(scan_source, int(source["id"])))
    return {"results": results, "summary": catalog.summary()}


#: Запрашивает разрешение Photos и возвращает состояние доступа.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/photos/authorize")
async def authorize_system_photos() -> dict[str, object]:
    try:
        status = await asyncio.to_thread(photo_libraries.authorize)
    except PhotosAccessDenied as error:
        raise HTTPException(
            status_code=403,
            detail="Разреши доступ в настройках macOS: Конфиденциальность → Фото",
        ) from error
    except PhotosAdapterError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    if status.get('source_id'):
        source = catalog.get_source(status['source_id'])
        if not source.get('last_scan_at'):
            schedule_scan(status['source_id'])
    thumbnail_workers.wake()
    return {'status': status}


#: Выполняет команду Photos в потоке с переводом ошибок доступа в HTTP.
#: Явно отклоняет недопустимое состояние через HTTPException.
async def library_call(method, *args, **kwargs):
    try:
        return await asyncio.to_thread(method, *args, **kwargs)
    except PhotosAccessDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except PhotosLibraryUnavailable as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, OSError, PhotosAdapterError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


#: Определяет Pydantic-контракт названия медиатеки.
#: Поля: label.
class LibraryNameRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    label: str = Field(min_length=1, max_length=120)


#: Определяет Pydantic-контракт папки-копии медиатеки.
#: Поля: volume_id, path.
class LibraryCopyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    volume_id: str = Field(min_length=1, max_length=128)
    path: str = Field(min_length=1, max_length=4096)


#: Определяет Pydantic-контракт временного окна Photos.
#: Поля: night_only, start_hour, end_hour, timezone.
class PhotosSyncScheduleRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    night_only: bool = Field(strict=True)
    start_hour: int = Field(default=0, ge=0, le=23, strict=True)
    end_hour: int = Field(default=7, ge=0, le=23, strict=True)
    timezone: Literal['Europe/Moscow'] = 'Europe/Moscow'


#: Сохраняет часы синхронизации выбранной медиатеки.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.patch('/api/photos/libraries/{source_id}/sync-schedule')
async def set_photos_sync_schedule(source_id: int, request: PhotosSyncScheduleRequest) -> dict:
    await library_call(photos_schedule.configure, source_id, **request.model_dump())
    thumbnail_workers.wake()
    return await list_photo_libraries()


#: Возвращает медиатеки, состояние подключения, превью и привязанные копии.
#: Асинхронно ожидает: library_call.
@app.get('/api/photos/libraries')
async def list_photo_libraries() -> dict:
    return await library_call(photo_libraries.list)


#: Повторяет сопоставление системной медиатеки и пробуждает превью.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.post('/api/photos/libraries/connect')
async def connect_photo_library() -> dict:
    await library_call(photo_libraries.refresh_connection)
    thumbnail_workers.wake()
    return await list_photo_libraries()


#: Возвращает виртуальную папку Photos и повышает приоритет её превью.
#: Асинхронно ожидает: library_call.
@app.get('/api/photos/libraries/{source_id}/browse')
async def browse_photo_library(source_id: int, path: str = '',
                               offset: int = Query(default=0, ge=0),
                               limit: int = Query(default=150, ge=1, le=1000)) -> dict:
    result = await library_call(lambda: photos_browser.browse(source_id, path, offset=offset, limit=limit))
    thumbnail_workers.wake()
    return result


#: Возвращает готовые превью выбранных объектов медиатеки.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get('/api/photos/libraries/{source_id}/preview-status')
async def photo_preview_status(source_id: int, ids: list[int] = Query(default=[])) -> dict:
    if len(ids) > 1000:
        raise HTTPException(status_code=400, detail='Слишком много объектов')
    return await library_call(photos_browser.preview_status, source_id, ids)


#: Регистрирует текущую медиатеку и ставит её первый скан в очередь.
#: Асинхронно ожидает: library_call.
@app.post('/api/photos/libraries', status_code=201)
async def register_photo_library(request: LibraryNameRequest) -> dict:
    profile = await library_call(photo_libraries.register, request.label)
    schedule_scan(profile['source_id'])
    return profile


#: Меняет название медиатеки и возвращает обновлённый список.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.patch('/api/photos/libraries/{source_id}')
async def rename_photo_library(source_id: int, request: LibraryNameRequest) -> dict:
    await library_call(photo_libraries.rename, source_id, request.label)
    return await list_photo_libraries()


#: Включает ручную паузу выбранной медиатеки.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.post('/api/photos/libraries/{source_id}/pause')
async def pause_photo_library(source_id: int) -> dict:
    await library_call(photo_libraries.set_paused, source_id, True)
    return await list_photo_libraries()


#: Снимает ручную паузу медиатеки и пробуждает очередь превью.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.post('/api/photos/libraries/{source_id}/resume')
async def resume_photo_library(source_id: int) -> dict:
    await library_call(photo_libraries.set_paused, source_id, False)
    thumbnail_workers.wake()
    return await list_photo_libraries()


#: Привязывает выбранную папку как копию медиатеки.
#: Асинхронно ожидает: library_call.
@app.post('/api/photos/libraries/{source_id}/copies', status_code=201)
async def bind_photo_library_copy(source_id: int, request: LibraryCopyRequest) -> dict:
    return await library_call(photo_libraries.bind_copy, source_id, request.volume_id, request.path)


#: Отключает привязку копии медиатеки и возвращает обновлённый список.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.delete('/api/photos/libraries/{source_id}/copies/{link_id}')
async def unbind_photo_library_copy(source_id: int, link_id: str) -> dict:
    await library_call(photo_libraries.unbind_copy, source_id, link_id)
    return await list_photo_libraries()


#: Меняет источник привязанной копии Photos.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.patch('/api/photos/libraries/{source_id}/copies/{link_id}/source')
async def photo_copy_source(source_id: int, link_id: str, request: CopySourceRequest) -> dict:
    await library_call(photo_libraries.set_copy_source, source_id, link_id, request.source_id)
    return await list_photo_libraries()


#: Ставит выбранную копию Photos первой по номеру без изменения маршрутов.
#: Асинхронно ожидает: library_call, list_photo_libraries.
@app.post('/api/photos/libraries/{source_id}/copies/{link_id}/make-first')
async def photo_copy_first(source_id: int, link_id: str) -> dict:
    await library_call(photo_libraries.make_first_copy, source_id, link_id)
    return await list_photo_libraries()


#: Запускает или планирует сохранение оригиналов в цепочку копий Photos.
#: Асинхронно ожидает: library_call.
@app.post('/api/photos/libraries/{source_id}/copies/{link_id}/originals/start')
async def start_photo_originals(source_id: int, link_id: str) -> dict:
    return await library_call(photos_originals.start, link_id, source_id)


#: Запрашивает паузу сохранения оригиналов выбранной медиатеки.
#: Асинхронно ожидает: library_call.
@app.post('/api/photos/libraries/{source_id}/copies/{link_id}/originals/pause')
async def pause_photo_originals(source_id: int, link_id: str) -> dict:
    return await library_call(photos_originals.pause, link_id, source_id)


#: Возвращает состояние оригиналов после проверки принадлежности копии медиатеке.
#: Асинхронно ожидает: library_call.
@app.get('/api/photos/libraries/{source_id}/copies/{link_id}/originals')
async def photo_originals_status(source_id: int, link_id: str) -> dict:
    await library_call(photos_originals._link, link_id, source_id)
    return await library_call(photos_originals.summary, link_id)


#: Возвращает журнал оригиналов и пути незавершённых записей.
#: Асинхронно ожидает: library_call.
@app.get('/api/photos/libraries/{source_id}/copies/{link_id}/originals/journal')
async def photo_originals_journal(source_id: int, link_id: str) -> dict:
    return await library_call(photos_originals.journal, link_id, source_id)


#: Возвращает суммарные показатели сохранённого медиаиндекса.
#: Использует catalog.summary.
@app.get("/api/catalog/summary")
async def catalog_summary() -> dict[str, int]:
    return catalog.summary()


#: Возвращает дерево виртуальных папок зарегистрированного источника.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get("/api/sources/{source_id}/tree")
async def source_tree(source_id: int) -> dict[str, object]:
    if catalog.get_source(source_id) is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    return {"nodes": catalog.folder_tree(source_id), "revision": catalog.revision()}


#: Возвращает файлы папки источника и повышает приоритет их превью.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get("/api/sources/{source_id}/files")
async def source_files(
    source_id: int,
    folder: str = "",
    limit: int = Query(default=300, ge=1, le=1000),
) -> dict[str, object]:
    if catalog.get_source(source_id) is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    catalog.prioritize_folder_thumbnails(source_id, folder)
    thumbnail_workers.wake()
    return {
        "files": catalog.list_files(source_id, folder=folder, limit=limit),
        "folder": folder,
        "revision": catalog.revision(),
    }


#: Возвращает очередь превью и диагностическое состояние её воркеров.
#: Использует thumbnail_workers.status.
@app.get("/api/thumbnails/status")
async def thumbnail_status() -> dict[str, object]:
    return thumbnail_workers.status()


#: Сохраняет общую ручную паузу фоновой очереди превью.
#: Использует catalog.set_thumbnail_queue_paused, thumbnail_workers.status.
@app.post("/api/thumbnails/pause")
async def pause_thumbnails() -> dict[str, object]:
    catalog.set_thumbnail_queue_paused(True)
    return thumbnail_workers.status()


#: Снимает общую паузу превью и пробуждает воркеры.
#: Использует catalog.set_thumbnail_queue_paused, thumbnail_workers.status, thumbnail_workers.wake.
@app.post("/api/thumbnails/resume")
async def resume_thumbnails() -> dict[str, object]:
    catalog.set_thumbnail_queue_paused(False)
    thumbnail_workers.wake()
    return thumbnail_workers.status()


#: Открывает проверенную папку обычного источника в Finder.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.post("/api/sources/{source_id}/open-in-finder")
async def open_source_folder_in_finder(
    source_id: int, request: FolderRequest
) -> dict[str, str]:
    try:
        folder = catalog.resolve_source_folder(source_id, request.folder)
        await asyncio.to_thread(
            subprocess.run,
            ["open", str(folder)],
            check=True,
            capture_output=True,
            text=True,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Источник не найден") from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Каталог не найден") from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except subprocess.CalledProcessError as error:
        raise HTTPException(
            status_code=500,
            detail=error.stderr.strip() or "Не удалось открыть Finder",
        ) from error
    return {"path": str(folder)}


#: Отдаёт только готовый JPEG из кэша медиаиндекса.
#: Явно отклоняет недопустимое состояние через HTTPException.
@app.get("/api/media/{media_id}/thumbnail")
async def media_thumbnail(media_id: int) -> FileResponse:
    try:
        thumbnail = await asyncio.to_thread(thumbnails.get_cached, media_id)
    except ThumbnailCacheUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (FileNotFoundError, PermissionError, OSError, PhotosAdapterError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if thumbnail is None:
        raise HTTPException(status_code=404, detail="Превью готовится")
    return FileResponse(
        thumbnail,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


#: Открывает обычный файл системной командой или выделяет объект Photos.
#: Явно отклоняет недопустимое состояние через HTTPException, KeyError.
@app.post("/api/media/{media_id}/open")
async def open_media_in_default_app(media_id: int) -> dict[str, str]:
    try:
        media = catalog.get_media(media_id)
        if media is None:
            raise KeyError(media_id)
        if media.get("source_kind") == "photos":
            await asyncio.to_thread(
                photo_libraries.open_asset, int(media['source_id']), str(media["relative_path"])
            )
            return {"path": f"{media['source_path']}/{media['relative_path']}"}
        else:
            original = catalog.resolve_media_file(media_id)
        await asyncio.to_thread(
            subprocess.run,
            ["open", str(original)],
            check=True,
            capture_output=True,
            text=True,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Файл не найден в каталоге") from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Оригинал файла не найден") from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except PhotosLibraryUnavailable as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PhotosAccessDenied as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except PhotosAdapterError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except subprocess.CalledProcessError as error:
        raise HTTPException(
            status_code=500,
            detail=error.stderr.strip() or "Не удалось открыть файл",
        ) from error
    return {"path": str(original)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=18765)
