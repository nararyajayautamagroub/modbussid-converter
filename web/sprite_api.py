from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from shared.image_tools import create_spritesheet, inspect_image
from shared.path_security import ROOT, safe_repo_file

router = APIRouter(prefix="/api/sprite-sheet", tags=["sprite-sheet"])
GENERATED = ROOT / "web" / "generated"
GENERATED.mkdir(exist_ok=True)


@router.get("/inspect")
def inspect(path: str):
    source = safe_repo_file(path)
    try:
        return inspect_image(source)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/create")
def create(path: str, columns: int = 4, rows: int = 4):
    source = safe_repo_file(path)
    if source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tga"}:
        raise HTTPException(
            status_code=400,
            detail="Sprite Sheet hanya menerima image raster yang didukung.",
        )

    output = GENERATED / f"{source.stem}_spritesheet.png"
    try:
        create_spritesheet(source, output, columns, rows)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return FileResponse(output, filename=output.name, media_type="image/png")
