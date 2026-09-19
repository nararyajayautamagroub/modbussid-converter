from pathlib import Path
from fastapi import APIRouter,HTTPException
from shared.template_classifier import template_info
router=APIRouter(prefix="/api/templates")
@router.get("/classify")
def classify(path:str):
 p=Path(path)
 if not p.is_file(): raise HTTPException(404,"File tidak ditemukan.")
 return template_info(p)
@router.get("/types")
def types(): return {"ao":"AO","texture":"Texture","xor":"Kaca/XOR"}
