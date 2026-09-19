from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from shared.light_animation import build_animation,to_dict
from shared.package_export import export_light_package
from web.asset_api import router as asset_router
ROOT=Path(__file__).resolve().parent
app=FastAPI(title="Game Mod Asset Lab")
app.include_router(asset_router)
@app.get("/")
def index(): return FileResponse(ROOT/"index.html")
@app.get("/api/categories")
def categories():
 return {"bussid":["vehicle","map","kodename","sprite-sheet","lights"],"ets2":["vehicle","map"],"roblox":["vehicle","lights","export"]}
@app.get("/api/lights/{light_type}")
def preview(light_type:str):
 if light_type not in {"strobo","rotator","ledbar"}: raise HTTPException(404,"Jenis lampu tidak dikenal.")
 return to_dict(build_animation(light_type))
@app.get("/api/lights/{light_type}/download")
def download(light_type:str,platform:str="roblox"):
 if light_type not in {"strobo","rotator","ledbar"}: raise HTTPException(404,"Jenis lampu tidak dikenal.")
 if platform not in {"roblox","bussid"}: raise HTTPException(400,"Platform tidak didukung.")
 with TemporaryDirectory() as tmp:
  path=export_light_package(light_type,Path(tmp)/f"{platform}_{light_type}",platform); data=path.read_bytes()
 out=ROOT/"generated"; out.mkdir(exist_ok=True); saved=out/path.name; saved.write_bytes(data)
 return FileResponse(saved,filename=saved.name,media_type="application/zip")
