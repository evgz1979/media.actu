from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from nicegui import ui


CORE_URL = "http://127.0.0.1:8765"


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


async def core_request(
    method: str, path: str, *, timeout: float = 20, **kwargs: Any
) -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=CORE_URL, timeout=timeout) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()


@ui.page("/")
async def index_page() -> None:
    ui.add_head_html('<meta name="color-scheme" content="light">')
    ui.add_css(
        """
        :root { --ink:#171717; --muted:#70706b; --line:#d4d4cf; --paper:#f3f3f0; --white:#fff; --accent:#214f3b; }
        body { background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif; }
        .q-layout, .q-page { background:var(--paper); }
        .utility-header { height:64px; border-bottom:1px solid #999; background:var(--white); padding:0 28px; }
        .brand { font-size:14px; font-weight:750; letter-spacing:.09em; }
        .muted { color:var(--muted); }
        .readonly { color:var(--accent); font-size:11px; font-weight:700; letter-spacing:.08em; }
        .workspace { width:calc(100% - 32px); max-width:none; margin:16px; }
        .panel { background:var(--white); border:1px solid var(--line); border-radius:0; box-shadow:none; }
        .section-index { color:var(--muted); font-size:10px; font-weight:700; letter-spacing:.12em; }
        .section-title { font-size:20px; font-weight:650; letter-spacing:-.01em; }
        .source-row { border-top:1px solid var(--line); min-height:46px; }
        .source-name { font-size:14px; font-weight:650; }
        .location-columns { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; align-items:stretch; }
        .location-columns > .q-card { height:100%; }
        .path { font-family:ui-monospace,"SFMono-Regular",Menlo,monospace; font-size:12px; }
        .stat { border-left:1px solid var(--line); padding:10px 18px; min-width:120px; }
        .stat:first-child { border-left:0; }
        .stat-value { font-size:20px; font-weight:650; }
        .stat-label { color:var(--muted); font-size:10px; letter-spacing:.08em; text-transform:uppercase; }
        .tree-pane { width:290px; min-width:290px; border-right:1px solid var(--line); }
        .content-pane { min-width:0; flex:1; }
        .media-card { width:190px; border:1px solid var(--line); background:var(--white); }
        .media-preview { width:188px; height:136px; object-fit:cover; border-bottom:1px solid var(--line); background:#e8e8e4; cursor:zoom-in; }
        .video-placeholder { width:188px; height:136px; display:flex; align-items:center; justify-content:center; background:#e8e8e4; border-bottom:1px solid var(--line); font-weight:700; font-size:11px; letter-spacing:.08em; cursor:pointer; }
        .q-btn { border-radius:2px; box-shadow:none !important; }
        .q-tree__node-header { min-height:28px; }
        @media (max-width:1000px) { .location-columns { grid-template-columns:minmax(0,1fr); } }
        """
    )

    selected_source_id: int | None = None
    selected_folder = ""
    selected_folders: dict[int, str] = {}
    expanded_folders: dict[int, set[str]] = {}
    source_kinds: dict[int, str] = {}
    last_revision = -1

    with ui.row().classes("utility-header w-full items-center justify-between no-wrap"):
        with ui.row().classes("items-center gap-4"):
            ui.label("MEDIA.ACTU").classes("brand")
            connection_label = ui.label("CORE: проверка…").classes("muted text-xs")
        ui.label("ОРИГИНАЛЫ: ТОЛЬКО ЧТЕНИЕ").classes("readonly")

    with ui.column().classes("workspace gap-4"):
        with ui.element("div").classes("location-columns w-full"):
            with ui.card().classes("panel w-full p-5"):
                with ui.row().classes("w-full items-start justify-between"):
                    with ui.column().classes("gap-1"):
                        ui.label("01 / ИСТОЧНИКИ").classes("section-index")
                        ui.label("Источники").classes("section-title")
                    with ui.row().classes("gap-2"):
                        ui.button(
                            "Добавить источник",
                            on_click=lambda: choose_sources("source"),
                        ).props("unelevated color=dark no-caps")
                        scan_button = ui.button(
                            "Сканировать всё", on_click=lambda: scan_all()
                        ).props("outline color=dark no-caps")
                ui.label(
                    "Флешки, SSD и каталоги, откуда позже будут поступать файлы. "
                    "Сейчас выполняется только чтение и индексирование."
                ).classes("muted text-sm")
                sources_container = ui.column().classes("w-full gap-0 mt-3")

            with ui.card().classes("panel w-full p-5"):
                with ui.row().classes("w-full items-start justify-between"):
                    with ui.column().classes("gap-1"):
                        ui.label("02 / ХРАНИЛИЩА КОПИЙ").classes("section-index")
                        ui.label("Хранилища копий").classes("section-title")
                    ui.button(
                        "Добавить хранилище",
                        on_click=lambda: choose_sources("storage"),
                    ).props("unelevated color=dark no-caps")
                ui.label(
                    "NAS и другие независимые места для будущих проверяемых копий. "
                    "RAID не считается отдельной копией."
                ).classes("muted text-sm")
                storages_container = ui.column().classes("w-full gap-0 mt-3")

        with ui.card().classes("panel w-full"):
            summary_container = ui.row().classes("w-full no-wrap")

        with ui.card().classes("panel w-full min-h-[520px]"):
            with ui.row().classes("w-full no-wrap items-stretch"):
                with ui.column().classes("tree-pane p-4 gap-3"):
                    ui.label("КАТАЛОГ").classes("section-index")
                    source_select = ui.select(
                        options={}, label="Расположение", on_change=lambda e: select_source(e.value)
                    ).props("outlined dense options-dense").classes("w-full")
                    tree_container = ui.column().classes("w-full")
                with ui.column().classes("content-pane p-4 gap-3"):
                    with ui.row().classes("w-full items-center justify-between no-wrap"):
                        folder_label = ui.label("Выбери источник").classes("section-title")
                        finder_button = ui.button(
                            "Открыть в Finder", on_click=lambda: open_in_finder()
                        ).props("outline color=dark no-caps")
                        finder_button.disable()
                    status_label = ui.label("Ожидание данных Core").classes("muted text-sm")
                    files_container = ui.row().classes("w-full gap-3 items-start")

    async def report_error(error: Exception) -> None:
        status_label.text = str(error)
        status_label.classes(add="text-negative", remove="muted")
        ui.notify(str(error), type="negative")

    async def refresh_sources() -> None:
        nonlocal selected_source_id
        try:
            payload = await core_request("GET", "/api/sources")
            sources = payload["sources"]
            connection_label.text = "CORE: подключён · :8765"
            connection_label.classes(add="text-positive", remove="muted")
            scan_button.set_enabled(bool(sources))
            source_kinds.clear()
            source_kinds.update(
                {
                    int(source["id"]): str(source.get("kind") or "folder")
                    for source in sources
                }
            )
            source_select.options = {
                int(source["id"]): (
                    f"{source.get('label') or source['path']} — {source['path']}"
                )
                for source in sources
            }
            source_select.update()
            sources_container.clear()
            storages_container.clear()

            def render_group(container: Any, group: list[dict[str, Any]], empty: str) -> None:
                with container:
                    if not group:
                        ui.label(empty).classes("muted py-3")
                    for source in group:
                        with ui.row().classes("source-row w-full items-center no-wrap"):
                            with ui.column().classes("gap-0 grow min-w-0 py-2"):
                                ui.label(
                                    str(source.get("label") or Path(str(source["path"])).name)
                                ).classes("source-name truncate w-full")
                                ui.label(str(source["path"])).classes("path truncate w-full")
                                if source.get("comment"):
                                    ui.label(str(source["comment"])).classes("muted text-xs")
                                if source.get("error"):
                                    ui.label(str(source["error"])).classes("text-negative text-xs")
                                ui.label(
                                    f"{source['media_count']} файлов · "
                                    f"{format_bytes(int(source['total_size']))} · "
                                    f"{source['status']} · {format_date(source['last_scan_at'])}"
                                ).classes("muted text-xs")
                            if source.get("kind") != "photos":
                                ui.button(
                                    "Изменить",
                                    on_click=lambda source=dict(source): edit_source(source),
                                ).props("flat dense no-caps color=dark")
                            if (
                                source.get("kind") == "photos"
                                and source.get("status") == "no_access"
                            ):
                                ui.button(
                                    "Разрешить доступ",
                                    on_click=lambda: authorize_photos(),
                                ).props("flat dense no-caps color=dark")
                            else:
                                ui.button(
                                    "Сканировать",
                                    on_click=lambda source_id=int(source["id"]): scan_one(source_id),
                                ).props("flat dense no-caps color=dark")
                            if source.get("kind") != "photos":
                                ui.button(
                                    "Убрать",
                                    on_click=lambda source_id=int(source["id"]): remove_source(source_id),
                                ).props("flat dense no-caps color=negative")

            render_group(
                sources_container,
                [source for source in sources if source.get("role") == "source"],
                "Источники пока не добавлены.",
            )
            render_group(
                storages_container,
                [source for source in sources if source.get("role") == "storage"],
                "Хранилища копий пока не добавлены.",
            )
            if selected_source_id not in source_select.options:
                selected_source_id = next(iter(source_select.options), None)
                source_select.value = selected_source_id
                source_select.update()
        except Exception as error:
            connection_label.text = "CORE: недоступен · :8765"
            connection_label.classes(add="text-negative", remove="muted text-positive")
            await report_error(error)

    async def refresh_summary() -> None:
        try:
            summary = await core_request("GET", "/api/catalog/summary")
            summary_container.clear()
            with summary_container:
                for label, value in [
                    ("Всего", str(summary["total"])),
                    ("Фото", str(summary["photos"])),
                    ("Видео", str(summary["videos"])),
                    ("Размер", format_bytes(int(summary["bytes"]))),
                    ("Ревизия", str(summary["revision"])),
                ]:
                    with ui.column().classes("stat gap-1"):
                        ui.label(value).classes("stat-value")
                        ui.label(label).classes("stat-label")
        except Exception as error:
            await report_error(error)

    async def source_metadata_dialog(
        *, role: str, label: str = "", comment: str = "", editing: bool = False
    ) -> dict[str, str] | None:
        with ui.dialog() as dialog, ui.card().classes("w-[520px] panel p-5 gap-4"):
            ui.label(
                "Параметры расположения" if editing else "Новое расположение"
            ).classes("section-title")
            role_input = ui.select(
                {"source": "Источник", "storage": "Хранилище копий"},
                value=role,
                label="Роль",
            ).props("outlined dense options-dense").classes("w-full")
            label_input = ui.input(
                "Название", value=label, placeholder="Например: NAS — MediaCopy1"
            ).props("outlined dense").classes("w-full")
            comment_input = ui.input(
                "Комментарий", value=comment, placeholder="Назначение, место, особенности"
            ).props("outlined dense").classes("w-full")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Отмена", on_click=lambda: dialog.submit(None)).props(
                    "flat color=dark no-caps"
                )
                ui.button(
                    "Сохранить" if editing else "Выбрать папку",
                    on_click=lambda: dialog.submit(
                        {
                            "role": str(role_input.value),
                            "label": str(label_input.value or ""),
                            "comment": str(comment_input.value or ""),
                        }
                    ),
                ).props("unelevated color=dark no-caps")
        return await dialog

    async def choose_sources(role: str) -> None:
        metadata = await source_metadata_dialog(role=role)
        if metadata is None:
            return
        status_label.text = "Ожидание выбора папки…"
        try:
            await core_request(
                "POST", "/api/sources/choose", timeout=305, json=metadata
            )
            await asyncio.gather(refresh_sources(), refresh_summary())
            if selected_source_id:
                await load_tree()
        except Exception as error:
            await report_error(error)

    async def edit_source(source: dict[str, Any]) -> None:
        metadata = await source_metadata_dialog(
            role=str(source.get("role") or "source"),
            label=str(source.get("label") or ""),
            comment=str(source.get("comment") or ""),
            editing=True,
        )
        if metadata is None:
            return
        try:
            await core_request(
                "PATCH", f"/api/sources/{source['id']}", json=metadata
            )
            await refresh_sources()
        except Exception as error:
            await report_error(error)

    async def authorize_photos() -> None:
        status_label.text = "Ожидание разрешения macOS для Photos…"
        try:
            await core_request("POST", "/api/photos/authorize", timeout=700)
            await asyncio.gather(refresh_sources(), refresh_summary())
            if selected_source_id is not None:
                await load_tree()
        except Exception as error:
            await report_error(error)

    async def remove_source(source_id: int) -> None:
        try:
            await core_request("DELETE", f"/api/sources/{source_id}")
            await asyncio.gather(refresh_sources(), refresh_summary())
            await load_tree()
        except Exception as error:
            await report_error(error)

    async def scan_one(source_id: int) -> None:
        status_label.text = "Сканирование источника…"
        try:
            await core_request("POST", f"/api/sources/{source_id}/scan", timeout=600)
            await asyncio.gather(refresh_sources(), refresh_summary())
            if selected_source_id == source_id:
                await load_tree()
        except Exception as error:
            await report_error(error)

    async def scan_all() -> None:
        status_label.text = "Сканирование всех источников…"
        scan_button.disable()
        try:
            await core_request("POST", "/api/scan", timeout=1200)
            await asyncio.gather(refresh_sources(), refresh_summary())
            await load_tree()
        except Exception as error:
            await report_error(error)
        finally:
            scan_button.enable()

    async def select_source(value: Any) -> None:
        nonlocal selected_source_id, selected_folder
        selected_source_id = int(value) if value is not None else None
        selected_folder = (
            selected_folders.get(selected_source_id, "")
            if selected_source_id is not None
            else ""
        )
        await load_tree()

    async def select_folder(value: Any) -> None:
        nonlocal selected_folder
        selected_folder = "" if value == "__root__" else str(value or "")
        if selected_source_id is not None:
            selected_folders[selected_source_id] = selected_folder
        await load_files()

    def remember_expanded_folders(value: Any) -> None:
        if selected_source_id is None:
            return
        expanded_folders[selected_source_id] = {
            str(folder) for folder in (value or [])
        }

    async def open_in_finder() -> None:
        if selected_source_id is None:
            return
        try:
            await core_request(
                "POST",
                f"/api/sources/{selected_source_id}/open-in-finder",
                json={"folder": selected_folder},
            )
        except Exception as error:
            await report_error(error)

    async def open_media(media_id: int) -> None:
        try:
            await core_request("POST", f"/api/media/{media_id}/open")
        except Exception as error:
            await report_error(error)

    async def load_tree() -> None:
        tree_container.clear()
        files_container.clear()
        if selected_source_id is None:
            folder_label.text = "Выбери источник"
            finder_button.disable()
            return
        finder_button.set_enabled(source_kinds.get(selected_source_id) == "folder")
        try:
            payload = await core_request(
                "GET", f"/api/sources/{selected_source_id}/tree"
            )
            with tree_container:
                tree = ui.tree(
                    payload["nodes"],
                    node_key="id",
                    label_key="label",
                    on_select=lambda e: select_folder(e.value),
                    on_expand=lambda e: remember_expanded_folders(e.value),
                ).classes("w-full")
                tree.select(selected_folder or "__root__")
                tree.expand(
                    list(expanded_folders.setdefault(selected_source_id, {"__root__"}))
                )
            await load_files()
        except Exception as error:
            await report_error(error)

    async def load_files() -> None:
        files_container.clear()
        if selected_source_id is None:
            return
        folder_label.text = selected_folder or "Корень"
        try:
            payload = await core_request(
                "GET",
                f"/api/sources/{selected_source_id}/files",
                params={"folder": selected_folder, "limit": 300},
            )
            files = payload["files"]
            status_label.text = f"Файлов в папке: {len(files)}"
            status_label.classes(add="muted", remove="text-negative")
            with files_container:
                if not files:
                    ui.label("В этой папке нет медиафайлов.").classes("muted")
                for media in files:
                    with ui.column().classes("media-card gap-0"):
                        if media["kind"] == "photo":
                            thumbnail_version = hashlib.sha256(
                                (
                                    f"{selected_source_id}\0{media['relative_path']}\0"
                                    f"{media['size']}\0{media['modified_at']}"
                                ).encode()
                            ).hexdigest()[:16]
                            preview = ui.image(
                                f"{CORE_URL}/api/media/{media['id']}/thumbnail"
                                f"?v={thumbnail_version}"
                            ).classes("media-preview")
                            preview.on(
                                "dblclick",
                                lambda _, media_id=int(media["id"]): open_media(media_id),
                            )
                        else:
                            preview = ui.html(
                                "<div class='video-placeholder'>ВИДЕО</div>"
                            )
                            preview.on(
                                "dblclick",
                                lambda _, media_id=int(media["id"]): open_media(media_id),
                            )
                        with ui.column().classes("p-3 gap-1 w-full"):
                            ui.label(media["name"]).classes("path truncate w-full")
                            ui.label(format_bytes(int(media["size"]))).classes(
                                "muted text-xs"
                            )
                            ui.label(format_date(media["modified_at"])).classes(
                                "muted text-xs"
                            )
        except Exception as error:
            await report_error(error)

    async def poll_revision() -> None:
        nonlocal last_revision
        try:
            payload = await core_request("GET", "/health", timeout=3)
            revision = int(payload["revision"])
            if revision != last_revision:
                last_revision = revision
                await asyncio.gather(refresh_sources(), refresh_summary())
                if selected_source_id is not None:
                    await load_tree()
        except Exception:
            connection_label.text = "CORE: недоступен · :8765"
            connection_label.classes(add="text-negative", remove="text-positive muted")

    await refresh_sources()
    await refresh_summary()
    if selected_source_id is not None:
        await load_tree()
    ui.timer(3.0, poll_revision)


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
