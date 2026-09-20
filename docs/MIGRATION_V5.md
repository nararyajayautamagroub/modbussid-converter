# Migration to v5.0.0

The v5 rebuild reorganizes the repository while keeping the supported application features.

## Folder renames

- `web/` → `backend/` for Python APIs and `frontend/` for HTML/CSS/JavaScript/PWA.
- `shared/` → `core/`.
- `scripts/` → `tooling/`.
- `bussid/` → `platforms/bussid/`.
- `ets2/` → `platforms/ets2_ats/`.
- `roblox/` → `platforms/roblox/`.
- `download/` → `artifacts/downloads/`.
- `templates/` → `assets/templates/`.
- `bussid/sprite-sheet/` → `platforms/bussid/sprite_sheet/`.

## Runtime updates

- Uvicorn entrypoint: `backend.app:app`.
- Static web root: `frontend/`.
- Generated output: `artifacts/generated/`.
- Folder descriptions: `/api/repository/folders`.
- CI and npm scripts use v5 paths.
- Legacy top-level directories are rejected by `tooling/repository_audit.py`.
