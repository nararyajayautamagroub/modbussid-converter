from fastapi import APIRouter

from core.path_security import safe_repo_file
from core.template_classifier import template_info

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("/classify")
def classify(path: str):
    return template_info(safe_repo_file(path))


@router.get("/types")
def types():
    return {"ao": "AO", "texture": "Texture", "xor": "Kaca/XOR"}
