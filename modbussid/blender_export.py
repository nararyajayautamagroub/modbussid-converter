import bpy
import sys
from pathlib import Path

def args():
    marker = sys.argv.index("--")
    return Path(sys.argv[marker+1]), Path(sys.argv[marker+2]), sys.argv[marker+3]

def main():
    source, destination, fmt = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ext = source.suffix.lower()
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(source))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(source))
    elif ext == ".dae":
        bpy.ops.wm.collada_import(filepath=str(source))
    elif ext in {".gltf", ".glb"}:
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        raise RuntimeError(f"Unsupported source: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "obj":
        bpy.ops.wm.obj_export(filepath=str(destination), export_materials=True)
    elif fmt == "dae":
        bpy.ops.wm.collada_export(filepath=str(destination))
    elif fmt == "fbx":
        bpy.ops.export_scene.fbx(filepath=str(destination), path_mode="COPY")
    elif fmt == "blend":
        bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    else:
        raise RuntimeError(fmt)

if __name__ == "__main__":
    main()
