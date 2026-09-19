import shutil
import tempfile
import zipfile
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from modbussid.extractor import extract, inspect, write_report
from modbussid.exporters import export_all, ExportError

BASE=Path(__file__).parent
app=FastAPI(title="modbussid-converter")
app.mount("/static",StaticFiles(directory=BASE/"static"),name="static")

@app.get("/")
def home():
    return FileResponse(BASE/"index.html")

@app.post("/api/convert")
async def convert(file: UploadFile=File(...), format: str=Form("all")):
    allowed={"all","obj","dae","fbx","blend"}
    if format not in allowed: raise HTTPException(400,"Format tidak didukung")
    if not file.filename: raise HTTPException(400,"Nama file kosong")
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); source=root/"input"+Path(file.filename).suffix
        with source.open("wb") as f: shutil.copyfileobj(file.file,f)
        extracted=root/"extracted"; result=extract(source,extracted)
        out=root/"exports"; target=out/"all"
        try:
            export_all(extracted,target)
        except ExportError as e:
            raise HTTPException(422,str(e))
        report=out/"report.json"; write_report(result,report)
        archive=root/"result.zip"
        with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
            for p in out.rglob("*"):
                if p.is_file(): z.write(p,p.relative_to(out))
        return FileResponse(archive,filename="modbussid-converter-result.zip",media_type="application/zip")
