from __future__ import annotations
from pathlib import Path

TEMPLATES={"ao":"AO","texture":"Texture","xor":"Kaca/XOR"}

def classify_template(path:Path)->str:
    name=path.name.lower()
    if any(x in name for x in ("ao","ambient_occlusion","ambient-occlusion")): return "ao"
    if any(x in name for x in ("kaca","glass","window","xor")): return "xor"
    return "texture"

def template_info(path:Path)->dict:
    kind=classify_template(path)
    return {"name":path.name,"template":kind,"label":TEMPLATES[kind],"extension":path.suffix.lower(),"size":path.stat().st_size if path.is_file() else 0}
