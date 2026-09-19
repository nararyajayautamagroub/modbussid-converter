from __future__ import annotations
import hashlib, tarfile, zipfile
from pathlib import Path
KNOWN_EXTENSIONS={".bussidmod":"BUSSID mod",".bussidvehicle":"BUSSID vehicle",".scs":"ETS2/ATS SCS archive",".sii":"SCS unit",".sui":"SCS include",".pmd":"SCS model descriptor",".pmg":"SCS model geometry",".pma":"SCS animation",".pmc":"SCS collision",".ppd":"SCS prefab",".pip":"SCS map",".mat":"SCS material",".dds":"texture",".png":"image",".jpg":"image",".jpeg":"image",".webp":"image",".obj":"OBJ model",".dae":"Collada model",".fbx":"FBX model",".blend":"Blender project",".rbxmx":"Roblox model XML"}
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
 return h.hexdigest()
def detect_container(path:Path)->str:
 try:
  if zipfile.is_zipfile(path): return "zip"
  if tarfile.is_tarfile(path): return "tar"
 except (OSError,tarfile.TarError): pass
 return "file"
def inspect_file(path:Path)->dict:
 if not path.is_file(): raise FileNotFoundError(path)
 return {"name":path.name,"size":path.stat().st_size,"extension":path.suffix.lower(),"type":KNOWN_EXTENSIONS.get(path.suffix.lower(),"unknown"),"container":detect_container(path),"sha256":sha256(path)}
def inspect_archive(path:Path)->list[dict]:
 kind=detect_container(path)
 if kind=="zip":
  with zipfile.ZipFile(path) as z: return [{"name":i.filename,"size":i.file_size,"compressed_size":i.compress_size} for i in z.infolist()]
 if kind=="tar":
  with tarfile.open(path) as t: return [{"name":i.name,"size":i.size} for i in t.getmembers() if i.isfile()]
 return []
def report(path:Path)->dict:
 d=inspect_file(path); d["entries"]=inspect_archive(path); return d
