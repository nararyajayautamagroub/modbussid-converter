import hashlib
import json
import shutil
import tarfile
import zipfile
from pathlib import Path
from .format_detect import detect_magic
from .models import Asset, Inspection

TEXTURES = {".png", ".jpg", ".jpeg", ".webp", ".dds", ".tga", ".bmp", ".ktx", ".ktx2"}
MODELS = {".obj", ".fbx", ".dae", ".gltf", ".glb", ".blend"}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXTURES:
        return "texture"
    if suffix in MODELS:
        return "model"
    return "file"

def inspect(path: Path) -> Inspection:
    if path.is_file():
        return Inspection(path, path.stat().st_size, sha256(path), detect_magic(path))
    assets = []
    for p in path.rglob("*"):
        if p.is_file():
            assets.append(Asset(p.relative_to(path), classify(p), p.stat().st_size))
    return Inspection(path, sum(a.size for a in assets), "", "directory", assets)

def _safe_zip_extract(z: zipfile.ZipFile, output: Path):
    root = output.resolve()
    for info in z.infolist():
        target = (output / info.filename).resolve()
        if root not in target.parents and target != root:
            raise ValueError(f"Unsafe archive path: {info.filename}")
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with z.open(info) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)

def extract(path: Path, output: Path) -> Inspection:
    output.mkdir(parents=True, exist_ok=True)
    magic = detect_magic(path)
    if magic == "zip" or zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            _safe_zip_extract(z, output)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as t:
            t.extractall(output, filter="data")
    else:
        shutil.copy2(path, output / path.name)
    return inspect(output)

def write_report(result: Inspection, path: Path) -> None:
    data = {
        "source": str(result.source),
        "size": result.size,
        "sha256": result.sha256,
        "magic": result.magic,
        "assets": [
            {"path": str(a.path), "kind": a.kind, "size": a.size, "metadata": a.metadata}
            for a in result.assets
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
