from __future__ import annotations

import asyncio
import subprocess
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from media_manager.scanner import normalize_source, scan_sources


ROOT = Path(__file__).parent
STATIC_DIR = ROOT / "static"

app = FastAPI(title="media.actu", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_sources: list[Path] = []
_sources_lock = threading.RLock()


class SourceRequest(BaseModel):
    path: str


def source_snapshot() -> list[Path]:
    with _sources_lock:
        return list(_sources)


def add_source(path: str | Path) -> Path:
    source = normalize_source(path)
    with _sources_lock:
        if source not in _sources:
            _sources.append(source)
            _sources.sort(key=lambda item: str(item).casefold())
    return source


def choose_folders_macos() -> list[str]:
    script = """
set chosenFolders to choose folder with prompt "Выбери папки для сканирования" with multiple selections allowed
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


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/sources")
async def list_sources() -> dict[str, list[str]]:
    return {"sources": [str(source) for source in source_snapshot()]}


@app.post("/api/sources")
async def create_source(request: SourceRequest) -> dict[str, object]:
    try:
        add_source(request.path)
    except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"sources": [str(source) for source in source_snapshot()]}


@app.post("/api/sources/choose")
async def choose_sources() -> dict[str, object]:
    try:
        selected = await asyncio.to_thread(choose_folders_macos)
        for path in selected:
            add_source(path)
    except (RuntimeError, FileNotFoundError, NotADirectoryError, PermissionError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "cancelled": not selected,
        "sources": [str(source) for source in source_snapshot()],
    }


@app.delete("/api/sources")
async def delete_source(request: SourceRequest) -> dict[str, list[str]]:
    candidate = Path(request.path).expanduser()
    with _sources_lock:
        _sources[:] = [source for source in _sources if source != candidate]
    return {"sources": [str(source) for source in source_snapshot()]}


@app.post("/api/scan")
async def scan() -> dict[str, object]:
    sources = source_snapshot()
    if not sources:
        raise HTTPException(status_code=400, detail="Сначала добавь хотя бы один источник")
    report = await asyncio.to_thread(scan_sources, sources)
    return report.to_dict()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
