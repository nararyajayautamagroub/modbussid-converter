from __future__ import annotations

import hashlib
import tarfile
import zipfile
from pathlib import Path

KNOWN_EXTENSIONS = {
    ".bussidmod": "BUSSID mod",
    ".bussidvehicle": "BUSSID vehicle",
    ".scs": "ETS2/ATS SCS archive",
    ".sii": "SCS unit",
    ".sui": "SCS include",
    ".pmd": "SCS model descriptor",
    ".pmg": "SCS model geometry",
    ".pma": "SCS animation",
    ".pmc": "SCS collision",
    ".ppd": "SCS prefab",
    ".pip": "SCS map",
    ".mat": "SCS material",
    ".dds": "texture",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".tga": "image",
    ".bmp": "image",
    ".obj": "OBJ model",
    ".dae": "Collada model",
    ".fbx": "FBX model",
    ".blend": "Blender project",
    ".rbxmx": "Roblox model XML",
    ".rbxm": "Roblox model",
    ".rbxlx": "Roblox place XML",
    ".rbxl": "Roblox place",
    ".lua": "Lua script",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_container(path: Path) -> str:
    try:
        if zipfile.is_zipfile(path):
            return "zip"
        if tarfile.is_tarfile(path):
            return "tar"
    except (OSError, tarfile.TarError, ValueError):
        return "file"
    return "file"


def inspect_file(path: Path) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    stat = path.stat()
    return {
        "name": path.name,
        "size": stat.st_size,
        "extension": path.suffix.lower(),
        "type": KNOWN_EXTENSIONS.get(path.suffix.lower(), "unknown"),
        "container": detect_container(path),
        "sha256": sha256(path),
    }


def inspect_archive(path: Path) -> list[dict]:
    kind = detect_container(path)
    if kind == "zip":
        with zipfile.ZipFile(path) as archive:
            return [
                {
                    "name": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                    "is_dir": info.is_dir(),
                }
                for info in archive.infolist()
            ]
    if kind == "tar":
        with tarfile.open(path) as archive:
            return [
                {"name": info.name, "size": info.size, "is_dir": info.isdir()}
                for info in archive.getmembers()
                if info.isfile() or info.isdir()
            ]
    return []


def report(path: Path) -> dict:
    data = inspect_file(path)
    entries = inspect_archive(path)
    data["entry_count"] = len(entries)
    data["entries"] = entries
    return data
