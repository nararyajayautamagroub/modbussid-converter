import hashlib
import json
import mimetypes
import struct
from pathlib import Path

IMAGE_EXTS={".png",".jpg",".jpeg",".webp",".dds",".tga",".bmp",".gif",".ktx",".ktx2",".hdr",".exr"}
AUDIO_EXTS={".wav",".mp3",".ogg",".opus",".flac",".aac",".m4a"}
VIDEO_EXTS={".mp4",".mkv",".mov",".avi",".webm",".wmv"}
MODEL_EXTS={".obj",".fbx",".dae",".gltf",".glb",".blend",".3ds",".ply",".stl"}
TEXT_EXTS={".json",".xml",".txt",".ini",".cfg",".csv",".yaml",".yml",".lua",".shader",".mat",".mtl"}

def _sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def _kind(path):
    e=path.suffix.lower()
    if e in IMAGE_EXTS:return "texture"
    if e in MODEL_EXTS:return "model"
    if e in AUDIO_EXTS:return "audio"
    if e in VIDEO_EXTS:return "video"
    if e in TEXT_EXTS:return "metadata"
    return "binary"

def _image_info(path):
    b=path.read_bytes()[:64]
    if b.startswith(b"\\x89PNG") and len(b)>=24:
        return {"format":"PNG","width":struct.unpack(">I",b[16:20])[0],"height":struct.unpack(">I",b[20:24])[0]}
    if b[:2]==b"\\xff\\xd8":
        return {"format":"JPEG"}
    return {"format":path.suffix.lstrip(".").upper()}

def inspect_assets(root):
    assets=[]
    for p in sorted(root.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        item={"path":str(rel),"name":p.name,"extension":p.suffix.lower(),"kind":_kind(p),
              "size":p.stat().st_size,"sha256":_sha256(p),"mime":mimetypes.guess_type(p.name)[0]}
        if item["kind"]=="texture": item["details"]=_image_info(p)
        assets.append(item)
    return assets

def write_detailed_report(root,out):
    assets=inspect_assets(root)
    summary={}
    for a in assets: summary[a["kind"]]=summary.get(a["kind"],0)+1
    data={"root":str(root),"total_assets":len(assets),"summary":summary,"assets":assets}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    return data
