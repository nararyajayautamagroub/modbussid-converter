from pathlib import Path

from fastapi import APIRouter, HTTPException

from shared.template_classifier import template_info

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("/classify")
def classify(path: str):
    try:
        return template_info(Path(path))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="File tidak ditemukan.") from exc


@router.get("/types")
def types():
    return {"ao": "AO", "texture": "Texture", "xor": "Kaca/XOR"}
