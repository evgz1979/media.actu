from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from media_manager.scanner import PHOTO_EXTENSIONS, VIDEO_EXTENSIONS


class PhotosAdapterError(RuntimeError):
    pass


class PhotosAccessDenied(PhotosAdapterError):
    pass


class SystemPhotosAdapter:
    BUNDLE_IDENTIFIER = "actu.media.photos-adapter"

    def __init__(self, source_directory: Path, build_directory: Path) -> None:
        self.source_directory = source_directory
        self.build_directory = build_directory
        self.app_directory = build_directory / "media-actu-photos.app"
        self.executable = self.app_directory / "Contents" / "MacOS" / "media-actu-photos"
        self._build_lock = threading.Lock()
        self._operation_lock = threading.RLock()
        self._backend: str | None = None

    @property
    def supported(self) -> bool:
        return os.uname().sysname == "Darwin" and shutil.which("clang") is not None

    def reuse_indexed_backend(self) -> None:
        self._backend = "applescript"

    def ensure_built(self) -> None:
        if not self.supported:
            raise PhotosAdapterError("PhotoKit доступен только на macOS")
        source = self.source_directory / "main.m"
        plist = self.source_directory / "Info.plist"
        if self.executable.exists() and self.executable.stat().st_mtime_ns >= max(
            source.stat().st_mtime_ns, plist.stat().st_mtime_ns
        ):
            return

        with self._build_lock:
            contents = self.app_directory / "Contents"
            macos = contents / "MacOS"
            macos.mkdir(parents=True, exist_ok=True)
            shutil.copy2(plist, contents / "Info.plist")
            environment = os.environ.copy()
            environment["CLANG_MODULE_CACHE_PATH"] = str(
                self.build_directory / "clang-module-cache"
            )
            command = [
                "clang",
                "-fobjc-arc",
                "-fblocks",
                str(source),
                "-o",
                str(self.executable),
                "-framework",
                "Foundation",
                "-framework",
                "AppKit",
                "-framework",
                "Photos",
                "-Wl,-sectcreate,__TEXT,__info_plist," + str(plist),
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=environment,
                timeout=120,
                check=False,
            )
            if result.returncode != 0:
                raise PhotosAdapterError(result.stderr.strip() or "Не удалось собрать PhotoKit-адаптер")
            subprocess.run(
                [
                    "codesign",
                    "--force",
                    "--sign",
                    "-",
                    "--identifier",
                    self.BUNDLE_IDENTIFIER,
                    str(self.app_directory),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

    def _run(self, *arguments: str, timeout: int = 120) -> dict[str, Any]:
        self.ensure_built()
        result = subprocess.run(
            [str(self.executable), *arguments],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = result.stdout.strip() or result.stderr.strip()
        try:
            payload = json.loads(output) if output else {}
        except json.JSONDecodeError as error:
            raise PhotosAdapterError(output or "PhotoKit-адаптер не вернул JSON") from error
        if result.returncode == 2:
            raise PhotosAccessDenied(str(payload.get("status") or payload.get("error")))
        if result.returncode != 0:
            raise PhotosAdapterError(str(payload.get("error") or output))
        return payload

    def status(self, *, request_authorization: bool = False) -> dict[str, Any]:
        payload = self._run("check")
        if payload.get("status") == "not_determined" and request_authorization:
            subprocess.run(
                ["open", "-W", "-n", str(self.app_directory), "--args", "status"],
                capture_output=True,
                text=True,
                timeout=305,
                check=False,
            )
            payload = self._run("check")
        if payload.get("status") in {"authorized", "limited"}:
            self._backend = "photokit"
            return {**payload, "backend": self._backend}
        try:
            fallback = self._applescript_status()
        except PhotosAdapterError as error:
            raise PhotosAccessDenied(str(payload.get("status") or "denied")) from error
        self._backend = "applescript"
        return {**fallback, "backend": self._backend}

    def scan(self) -> list[dict[str, Any]]:
        with self._operation_lock:
            if self._backend is None:
                self.status()
            if self._backend == "applescript":
                return self._applescript_scan()
            payload = self._run("scan", timeout=600)
            return list(payload.get("assets", []))

    def create_thumbnail(
        self, asset_identifier: str, target: Path, width: int = 640, height: int = 480
    ) -> Path:
        with self._operation_lock:
            if self._backend is None:
                self.status()
            if self._backend == "applescript":
                return self._applescript_thumbnail(
                    asset_identifier, target, width, height
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            self._run(
                "thumbnail",
                asset_identifier,
                str(target),
                str(width),
                str(height),
                timeout=600,
            )
            if not target.is_file():
                raise PhotosAdapterError("PhotoKit не создал превью")
            return target

    def open_asset(self, asset_identifier: str) -> None:
        result = subprocess.run(
            [
                "osascript",
                str(self.source_directory / "open.applescript"),
                asset_identifier,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            raise PhotosAdapterError(
                result.stderr.strip() or "Не удалось открыть объект в Photos"
            )

    def _applescript_status(self) -> dict[str, Any]:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Photos" to count media items'],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            raise PhotosAdapterError(result.stderr.strip() or "Нет доступа к Photos")
        return {"status": "authorized", "count": int(result.stdout.strip() or 0)}

    def _applescript_scan(self) -> list[dict[str, Any]]:
        result = subprocess.run(
            [
                "osascript",
                "-l",
                "JavaScript",
                str(self.source_directory / "scan.js"),
            ],
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
        if result.returncode != 0:
            raise PhotosAdapterError(result.stderr.strip() or "Не удалось прочитать Photos")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise PhotosAdapterError("Photos вернул некорректный каталог") from error

        assets = []
        for asset in payload.get("assets", []):
            extension = Path(str(asset.get("name") or "")).suffix.lower()
            if extension in PHOTO_EXTENSIONS:
                kind = "photo"
            elif extension in VIDEO_EXTENSIONS:
                kind = "video"
            else:
                continue
            assets.append({**asset, "kind": kind})
        return assets

    def _applescript_thumbnail(
        self, asset_identifier: str, target: Path, width: int, height: int
    ) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="photos-export-", dir=target.parent
        ) as directory:
            result = subprocess.run(
                [
                    "osascript",
                    str(self.source_directory / "export.applescript"),
                    asset_identifier,
                    directory,
                ],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            if result.returncode != 0:
                raise PhotosAdapterError(
                    result.stderr.strip() or "Photos не создал превью"
                )
            exported = next(
                (path for path in Path(directory).iterdir() if path.is_file()), None
            )
            if exported is None:
                raise PhotosAdapterError("Photos не экспортировал изображение")
            with Image.open(exported) as image:
                image = ImageOps.exif_transpose(image)
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(target, "JPEG", quality=86, optimize=True)
        return target
