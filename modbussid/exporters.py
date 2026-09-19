import shutil
import subprocess
from pathlib import Path

class ExportError(RuntimeError):
    pass

def find_model(root: Path):
    exts = {".obj", ".dae", ".fbx", ".gltf", ".glb"}
    return next((p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts), None)

def copy_textures(root: Path, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    exts = {".png",".jpg",".jpeg",".webp",".dds",".tga",".bmp",".ktx",".ktx2"}
    copied=[]
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            target=destination / p.name
            shutil.copy2(p, target)
            copied.append(target)
    return copied

def blender_export(source: Path, destination: Path, fmt: str, blender="blender"):
    destination.parent.mkdir(parents=True, exist_ok=True)
    script = Path(__file__).with_name("blender_export.py")
    cmd=[blender, "--background", "--python", str(script), "--", str(source), str(destination), fmt]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        raise ExportError("Blender was not found. Install Blender or pass --blender.") from e
    except subprocess.CalledProcessError as e:
        raise ExportError(f"Blender export failed with code {e.returncode}.") from e

def export_all(root: Path, out: Path, blender="blender"):
    model=find_model(root)
    if not model:
        raise ExportError("No supported extracted 3D model was found. A BUSSID-specific mesh decoder may be required.")
    out.mkdir(parents=True, exist_ok=True)
    copy_textures(root, out/"textures")
    if model.suffix.lower() == ".obj":
        shutil.copy2(model, out/"model.obj")
        mtl=model.with_suffix(".mtl")
        if mtl.exists(): shutil.copy2(mtl, out/"model.mtl")
    else:
        blender_export(model, out/"model.obj", "obj", blender)
    blender_export(model, out/"model.dae", "dae", blender)
    blender_export(model, out/"model.fbx", "fbx", blender)
    blender_export(model, out/"model.blend", "blend", blender)
