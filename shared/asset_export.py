from __future__ import annotations
import json,zipfile
from pathlib import Path
from .asset_inspector import report
def export_found_asset(source:Path,destination:Path,selected:list[str]|None=None)->Path:
 destination.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as out:
  if selected is None: out.write(source,source.name)
  elif source.suffix.lower()==".zip":
   with zipfile.ZipFile(source) as src:
    for info in src.infolist():
     if info.filename in set(selected) and not info.is_dir(): out.writestr(info,src.read(info.filename))
  else: raise ValueError("Pemilihan entry hanya didukung untuk ZIP.")
  out.writestr("manifest.json",json.dumps({"source":source.name,"report":report(source),"selected":selected},indent=2))
 return destination
