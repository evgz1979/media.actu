from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from nicegui import app as nicegui_app, ui
from starlette.responses import RedirectResponse


CORE_URL = "http://127.0.0.1:18765"
_core_client: httpx.AsyncClient | None = None


async def close_core_client() -> None:
    global _core_client
    if _core_client is not None:
        await _core_client.aclose()
        _core_client = None


nicegui_app.on_shutdown(close_core_client)


def format_bytes(value: int) -> str:
    if not value:
        return "0 Б"
    units = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    size = float(value)
    unit = units[0]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            break
        size /= 1024
    precision = 0 if unit in {"Б", "КБ"} else 1
    return f"{size:.{precision}f} {unit}"


def format_date(value: str | None) -> str:
    if not value:
        return "—"
    return datetime.fromisoformat(value).astimezone().strftime("%d.%m.%Y %H:%M")


def format_percent(done: int, total: int) -> str:
    if not total:
        return "0.0%"
    percent = done / total * 100
    precision = 2 if 0 < percent < 0.1 else 1
    return f"{percent:.{precision}f}%"


async def core_request(
    method: str, path: str, *, timeout: float = 20, **kwargs: Any
) -> dict[str, Any]:
    global _core_client
    if _core_client is None or _core_client.is_closed:
        _core_client = httpx.AsyncClient(base_url=CORE_URL,
                                        limits=httpx.Limits(max_connections=30, max_keepalive_connections=10, keepalive_expiry=60))
    response = await _core_client.request(method, path, timeout=timeout, **kwargs)
    response.raise_for_status()
    return response.json()


@nicegui_app.get('/media', include_in_schema=False)
async def old_media_page(source: int | None = None):
    return RedirectResponse('/?source=photos-' + str(source) if source is not None else '/')


from storage_ui import register_storage_page

register_storage_page(core_request, format_bytes, format_date, lambda: CORE_URL)

from comparison_ui import register_comparison_page

register_comparison_page(core_request, format_bytes, format_date)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host="127.0.0.1",
        port=8090,
        title="media.actu",
        favicon="",
        reload=False,
        show=False,
        storage_secret="media-actu-local",
    )
