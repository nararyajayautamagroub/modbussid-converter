from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from shared.asset_export import export_found_asset
from shared.asset_inspector import inspect_archive, inspect_file
from shared.roblox_url import download_asset

router = APIRouter(prefix="/api/assets", tags=["assets"])
ROOT = Path(__file__).resolve().parent.parent
UPLOADS = ROOT / "uploads"
GENERATED = ROOT / "web" / "generated"
UPLOADS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def _safe_repo_path(raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser().resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="Path harus berada di dalam folder repository."
        ) from exc
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File tidak ditemukan.")
    return candidate


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file upload kosong.")

    target = (UPLOADS / Path(file.filename).name).resolve()
    try:
        target.relative_to(UPLOADS.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Nama file tidak valid.") from exc

    total = 0
    with target.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                target.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Upload melebihi 100 MB.")
            handle.write(chunk)

    return {"name": target.name, "path": target.relative_to(ROOT).as_posix(), "bytes": total}


@router.get("/inspect")
def inspect(path: str):
    source = _safe_repo_path(path)
    try:
        return {"file": inspect_file(source), "entries": inspect_archive(source)}
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/export")
def export(path: str, selected: list[str] | None = None):
    source = _safe_repo_path(path)
    output_name = f"{source.stem}_export.zip"
    output = GENERATED / output_name
    try:
        export_found_asset(source, output, selected)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(output, filename=output.name, media_type="application/zip")


@router.get("/roblox/url")
def roblox_url(url: str):
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "roblox_asset"
        try:
            result = download_asset(url, target)
            data = target.read_bytes()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    output = GENERATED / f"roblox_{result['asset_id']}.bin"
    output.write_bytes(data)
    return FileResponse(output, filename=output.name, media_type="application/octet-stream")
