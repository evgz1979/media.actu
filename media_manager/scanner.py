from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


PHOTO_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}

VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
}

IGNORED_DIRECTORY_NAMES = {
    "__MACOSX",
    ".DocumentRevisions-V100",
    ".Spotlight-V100",
    ".TemporaryItems",
    ".Trashes",
    ".fseventsd",
}
IGNORED_FILE_NAMES = {".DS_Store"}


@dataclass(frozen=True, slots=True)
class MediaFile:
    source: str
    relative_path: str
    kind: str
    size: int
    modified_at: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScanError:
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class ScanReport:
    files: list[MediaFile]
    errors: list[ScanError]

    @property
    def photo_count(self) -> int:
        return sum(item.kind == "photo" for item in self.files)

    @property
    def video_count(self) -> int:
        return sum(item.kind == "video" for item in self.files)

    @property
    def total_size(self) -> int:
        return sum(item.size for item in self.files)

    def to_dict(self) -> dict[str, object]:
        return {
            "files": [item.to_dict() for item in self.files],
            "errors": [error.to_dict() for error in self.errors],
            "summary": {
                "total": len(self.files),
                "photos": self.photo_count,
                "videos": self.video_count,
                "bytes": self.total_size,
                "errors": len(self.errors),
            },
        }


def media_kind(path: Path) -> str | None:
    extension = path.suffix.lower()
    if extension in PHOTO_EXTENSIONS:
        return "photo"
    if extension in VIDEO_EXTENSIONS:
        return "video"
    return None


def normalize_source(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_dir():
        raise NotADirectoryError(f"Не является папкой: {source}")
    return source


def scan_sources(sources: Iterable[str | Path]) -> ScanReport:
    """Recursively read media metadata without modifying source files."""
    files: list[MediaFile] = []
    errors: list[ScanError] = []

    for raw_source in sources:
        try:
            source = normalize_source(raw_source)
        except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
            errors.append(ScanError(str(raw_source), str(error)))
            continue

        def on_walk_error(error: OSError) -> None:
            errors.append(ScanError(error.filename or str(source), str(error)))

        for current, directory_names, file_names in os.walk(
            source, topdown=True, onerror=on_walk_error, followlinks=False
        ):
            current_path = Path(current)
            directory_names[:] = [
                name
                for name in directory_names
                if name not in IGNORED_DIRECTORY_NAMES
                and not (current_path / name).is_symlink()
            ]

            for file_name in file_names:
                if file_name in IGNORED_FILE_NAMES or file_name.startswith("._"):
                    continue
                path = current_path / file_name
                kind = media_kind(path)
                if kind is None or path.is_symlink():
                    continue

                try:
                    stat = path.stat(follow_symlinks=False)
                except (FileNotFoundError, PermissionError, OSError) as error:
                    errors.append(ScanError(str(path), str(error)))
                    continue

                files.append(
                    MediaFile(
                        source=str(source),
                        relative_path=str(path.relative_to(source)),
                        kind=kind,
                        size=stat.st_size,
                        modified_at=datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                    )
                )

    files.sort(key=lambda item: (item.source.casefold(), item.relative_path.casefold()))
    return ScanReport(files=files, errors=errors)
