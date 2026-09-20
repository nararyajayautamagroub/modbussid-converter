from fastapi import APIRouter, HTTPException

from shared.i18n import LANGUAGES, get_translations

router = APIRouter(prefix="/api/i18n", tags=["i18n"])


@router.get("")
def all_languages():
    return {"languages": LANGUAGES}


@router.get("/{language}")
def translations(language: str):
    if language not in LANGUAGES:
        raise HTTPException(status_code=404, detail="Bahasa tidak didukung.")
    return {
        "language": language,
        "label": LANGUAGES[language],
        "translations": get_translations(language),
    }
