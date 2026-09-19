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
    if path.suffix.lower() in TEXTURES:
        return "texture"
    if path.suffix.lower() in MODELS:
        return "model"
    return "file"

def inspect(path: Path) -> Inspection:
    assets = []
    if path.is_dir():
        for p in path.rglob("*"):
            if p.is_file():
                assets.append(Asset(p, classify(p), p.stat().st_size))
    return Inspection(path, path.stat().st_size, sha256(path), detect_magic(path))

def extract(path: Path, output: Path) -> Inspection:
    output.mkdir(parents=True, exist_ok=True)
    magic = detect_magic(path)
    if magic == "zip" or zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            z.extractall(output)
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
        "assets": [{"path": str(a.path), "kind": a.kind, "size": a.size, "metadata": a.metadata} for a in result.assets],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
