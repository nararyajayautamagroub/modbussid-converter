from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_ROOTS = tuple(
    (ROOT / name).resolve()
    for name in ("uploads", "bussid", "ets2", "roblox", "templates")
)


def safe_repo_file(raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser().resolve()
    if not any(candidate == root or root in candidate.parents for root in ALLOWED_ROOTS):
        raise HTTPException(
            status_code=400,
            detail="Path harus berada di folder asset yang diizinkan.",
        )
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File tidak ditemukan.")
    return candidate
