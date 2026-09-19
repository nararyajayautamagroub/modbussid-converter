from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import APIRouter,HTTPException
from fastapi.responses import FileResponse
from shared.asset_inspector import inspect_file,inspect_archive
from shared.asset_export import export_found_asset
from shared.roblox_url import download_asset
router=APIRouter(prefix="/api/assets")
BASE=Path(__file__).resolve().parent/"generated"; BASE.mkdir(exist_ok=True)
@router.get("/inspect")
def inspect(path:str):
 try: return {"file":inspect_file(Path(path)),"entries":inspect_archive(Path(path))}
 except Exception as e: raise HTTPException(400,str(e))
@router.get("/export")
def export(path:str):
 p=Path(path)
 if not p.is_file(): raise HTTPException(404,"File tidak ditemukan.")
 out=BASE/(p.stem+"_export.zip")
 try: export_found_asset(p,out); return FileResponse(out,filename=out.name,media_type="application/zip")
 except Exception as e: raise HTTPException(400,str(e))
@router.get("/roblox/url")
def roblox_url(url:str):
 with TemporaryDirectory() as tmp:
  target=Path(tmp)/"roblox_asset"
  try: result=download_asset(url,target); data=target.read_bytes()
  except Exception as e: raise HTTPException(400,str(e))
 out=BASE/f"roblox_{result['asset_id']}.bin"; out.write_bytes(data)
 return FileResponse(out,filename=out.name,media_type="application/octet-stream")
