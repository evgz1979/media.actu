from __future__ import annotations

import asyncio
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from media_manager.catalog import Catalog
from media_manager.scanner import scan_sources
from media_manager.thumbnails import ThumbnailService
from media_manager.watcher import SourceWatcher


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
catalog = Catalog(DATA_DIR / "catalog.sqlite3")
thumbnails = ThumbnailService(catalog, DATA_DIR / "thumbnails")
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
        report = scan_sources([str(source["path"])])
        catalog.replace_source_scan(source_id, report)
        return {"source_id": source_id, **report.to_dict()["summary"]}
    except Exception as error:
        catalog.set_source_status(source_id, "error", str(error))
        raise
    finally:
        lock.release()


def schedule_scan(source_id: int) -> None:
    executor.submit(scan_source, source_id)


watcher = SourceWatcher(schedule_scan)


@asynccontextmanager
async def lifespan(_: FastAPI):
    watcher.start()
    for source in catalog.list_sources():
        source_path = Path(str(source["path"]))
        if source_path.is_dir():
            watcher.watch(int(source["id"]), source_path)
            schedule_scan(int(source["id"]))
    yield
    watcher.stop()
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
    if catalog.get_source(source_id) is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
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
        results.append(await asyncio.to_thread(scan_source, int(source["id"])))
    return {"results": results, "summary": catalog.summary()}


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
    return {
        "files": catalog.list_files(source_id, folder=folder, limit=limit),
        "folder": folder,
        "revision": catalog.revision(),
    }


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
        thumbnail = await asyncio.to_thread(thumbnails.get_or_create, media_id)
    except (FileNotFoundError, PermissionError, OSError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if thumbnail is None:
        raise HTTPException(status_code=404, detail="Превью недоступно")
    return FileResponse(
        thumbnail,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/media/{media_id}/open")
async def open_media_in_default_app(media_id: int) -> dict[str, str]:
    try:
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
    except subprocess.CalledProcessError as error:
        raise HTTPException(
            status_code=500,
            detail=error.stderr.strip() or "Не удалось открыть файл",
        ) from error
    return {"path": str(original)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
