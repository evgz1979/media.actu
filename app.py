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
    SystemPhotosAdapter,
)
from media_manager.scanner import scan_sources
from media_manager.thumbnails import ThumbnailCacheUnavailable, ThumbnailService
from media_manager.thumbnail_workers import ThumbnailWorkerPool
from media_manager.watcher import SourceWatcher
from media_manager.storage import StorageCatalog
from media_manager.network import NetworkCatalog, NetworkError


ROOT = Path(__file__).parent
DATA_DIR = Path(os.environ.get("MEDIA_ACTU_DATA_DIR", str(ROOT / "data"))).expanduser()


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
photos_adapter = SystemPhotosAdapter(ROOT / "photos_adapter", DATA_DIR / "native")
thumbnails = ThumbnailService(catalog, local_thumbnail_cache_directory(), photos_adapter)
thumbnail_workers = ThumbnailWorkerPool(catalog, thumbnails)
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="media-scan")
scan_locks: dict[int, threading.Lock] = {}


def scan_source(source_id: int) -> dict[str, object]:
    source = catalog.get_source(source_id)
    if source is None:
        raise KeyError(source_id)
    lock = scan_locks.setdefault(source_id, threading.Lock())
    if not lock.acquire(blocking=False):
        return {"source_id": source_id, "status": "already_scanning"}
    try:
        catalog.set_source_status(source_id, "scanning")
        if source.get("kind") == "photos":
            assets = photos_adapter.scan()
            catalog.replace_photos_scan(source_id, assets)
            catalog.enqueue_source_thumbnails(source_id)
            catalog.set_source_status(source_id, "idle")
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


def schedule_scan(source_id: int) -> None:
    catalog.set_source_status(source_id, "scanning")
    executor.submit(scan_source, source_id)


watcher = SourceWatcher(schedule_scan)


@asynccontextmanager
async def lifespan(_: FastAPI):
    watcher.start()
    catalog.reset_stale_source_scans()
    photos_ready = False
    if photos_adapter.supported:
        photos_source = catalog.add_system_photos_source()
        indexed_photos = next(
            (
                source
                for source in catalog.list_sources()
                if source.get("kind") == "photos"
            ),
            None,
        )
        if indexed_photos and int(indexed_photos.get("media_count") or 0) > 0:
            photos_adapter.reuse_indexed_backend()
            catalog.set_source_status(int(photos_source["id"]), "idle")
            photos_ready = True
        else:
            try:
                await asyncio.to_thread(
                    photos_adapter.status, request_authorization=True
                )
                photos_ready = True
            except PhotosAccessDenied:
                catalog.set_source_status(
                    int(photos_source["id"]), "no_access", "Нет доступа к Photos"
                )
            except PhotosAdapterError as error:
                catalog.set_source_status(
                    int(photos_source["id"]), "error", str(error)
                )
    for source in catalog.list_sources():
        if source.get("kind") == "photos":
            if photos_ready and (
                int(source.get("media_count") or 0) == 0
                or not source.get("last_scan_at")
            ):
                schedule_scan(int(source["id"]))
            continue
        source_path = Path(str(source["path"]))
        if source_path.is_dir():
            watcher.watch(int(source["id"]), source_path)
            schedule_scan(int(source["id"]))
    thumbnail_workers.start()
    yield
    watcher.stop()
    thumbnail_workers.stop()
    executor.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="media.actu Core",
    version="0.1.0-dev",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)


class SourceRequest(BaseModel):
    path: str
    role: Literal["source", "storage"] = "source"
    label: str = ""
    comment: str = ""


class FolderChoiceRequest(BaseModel):
    role: Literal["source", "storage"] = "source"
    label: str = ""
    comment: str = ""


class SourceMetadataRequest(BaseModel):
    role: Literal["source", "storage"]
    label: str = ""
    comment: str = ""


class FolderRequest(BaseModel):
    folder: str = ""


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


@app.get("/health")
async def health() -> dict[str, object]:
    return {"status": "ok", "revision": catalog.revision()}


class StorageMetadataRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = ""
    purpose: Literal["", "media", "documents", "projects", "mixed"] | None = None
    role: Literal["", "primary", "copy", "archive", "temporary"] | None = None
    no_duplicate: bool | None = None
    planned_move: bool | None = None
    comment: str = Field(default="", max_length=4000)


@app.get("/api/storage/volumes")
async def storage_volumes(refresh: bool = False) -> dict:
    return await asyncio.to_thread(storage.refresh, refresh)


class NetworkShareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    share: str = Field(min_length=1, max_length=255)


@app.get("/api/storage/nas")
async def remembered_nas() -> dict:
    return await asyncio.to_thread(network.servers)


@app.post("/api/storage/nas/discover")
async def discover_nas() -> dict:
    return await asyncio.to_thread(network.scan)


@app.get("/api/storage/nas/{server_id}/shares")
async def nas_shares(server_id: str, refresh: bool = False) -> dict:
    try:
        return await asyncio.to_thread(network.shares, server_id, refresh)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="NAS не найден") from error


@app.post("/api/storage/nas/{server_id}/remember")
async def remember_nas_share(server_id: str, request: NetworkShareRequest) -> dict:
    try:
        return await asyncio.to_thread(network.remember, server_id, request.share)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except NetworkError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/storage/volumes/{volume_id}/connect")
async def connect_network_volume(volume_id: str) -> dict:
    try:
        return await asyncio.to_thread(network.open_in_finder, volume_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Том не найден") from error
    except NetworkError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/storage/volumes/{volume_id}/directory")
async def storage_directory(volume_id: str, path: str = "", refresh: bool = True) -> dict:
    try:
        return await asyncio.to_thread(storage.directory, volume_id, path, refresh)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Том не найден") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.patch("/api/storage/volumes/{volume_id}/metadata")
async def storage_metadata(volume_id: str, request: StorageMetadataRequest) -> dict:
    try:
        return await asyncio.to_thread(storage.annotate, volume_id, request.path, request.model_dump(exclude={"path"}))
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Том не найден") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/sources")
async def list_sources() -> dict[str, object]:
    return {"sources": catalog.list_sources(), "revision": catalog.revision()}


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


@app.post("/api/sources/{source_id}/scan")
async def scan_one_source(source_id: int) -> dict[str, object]:
    try:
        return await asyncio.to_thread(scan_source, source_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Источник не найден") from error


@app.post("/api/scan")
async def scan_all_sources() -> dict[str, object]:
    sources = catalog.list_sources()
    if not sources:
        raise HTTPException(status_code=400, detail="Сначала добавь хотя бы один источник")
    results = []
    for source in sources:
        if source.get("kind") == "photos" and source.get("status") == "no_access":
            results.append(
                {"source_id": int(source["id"]), "status": "no_access"}
            )
            continue
        results.append(await asyncio.to_thread(scan_source, int(source["id"])))
    return {"results": results, "summary": catalog.summary()}


@app.post("/api/photos/authorize")
async def authorize_system_photos() -> dict[str, object]:
    source = next(
        (
            source
            for source in catalog.list_sources()
            if source.get("kind") == "photos"
        ),
        None,
    )
    if source is None:
        raise HTTPException(status_code=404, detail="Источник Photos недоступен")
    try:
        status = await asyncio.to_thread(
            photos_adapter.status, request_authorization=True
        )
        result = await asyncio.to_thread(scan_source, int(source["id"]))
    except PhotosAccessDenied as error:
        catalog.set_source_status(
            int(source["id"]), "no_access", "Нет доступа к Photos"
        )
        raise HTTPException(
            status_code=403,
            detail="Разреши доступ в настройках macOS: Конфиденциальность → Фото",
        ) from error
    except PhotosAdapterError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return {"status": status, "scan": result}


@app.get("/api/catalog/summary")
async def catalog_summary() -> dict[str, int]:
    return catalog.summary()


@app.get("/api/sources/{source_id}/tree")
async def source_tree(source_id: int) -> dict[str, object]:
    if catalog.get_source(source_id) is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    return {"nodes": catalog.folder_tree(source_id), "revision": catalog.revision()}


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


@app.get("/api/thumbnails/status")
async def thumbnail_status() -> dict[str, object]:
    return thumbnail_workers.status()


@app.post("/api/thumbnails/pause")
async def pause_thumbnails() -> dict[str, object]:
    catalog.set_thumbnail_queue_paused(True)
    return thumbnail_workers.status()


@app.post("/api/thumbnails/resume")
async def resume_thumbnails() -> dict[str, object]:
    catalog.set_thumbnail_queue_paused(False)
    thumbnail_workers.wake()
    return thumbnail_workers.status()


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


@app.post("/api/media/{media_id}/open")
async def open_media_in_default_app(media_id: int) -> dict[str, str]:
    try:
        media = catalog.get_media(media_id)
        if media is None:
            raise KeyError(media_id)
        if media.get("source_kind") == "photos":
            await asyncio.to_thread(
                photos_adapter.open_asset, str(media["relative_path"])
            )
            return {"path": f"photos://system/{media['relative_path']}"}
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
