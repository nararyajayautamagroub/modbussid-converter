from __future__ import annotations

from fastapi import APIRouter

from core.version import APP_VERSION, PRODUCT_NAME

router = APIRouter(prefix="/api/gateway", tags=["gateway"])


@router.get("/health")
def gateway_health() -> dict:
    return {
        "status": "ok",
        "gateway": "fastapi",
        "service": PRODUCT_NAME,
        "version": APP_VERSION,
        "frontend": "/",
        "api_prefix": "/api",
        "auth": "/api/auth/status",
        "i18n": "/api/i18n",
        "scraper": "/api/scraper",
        "repository_folders": "/api/repository/folders",
    }


@router.get("/routes")
def gateway_routes() -> dict:
    return {
        "frontend": ["/", "/styles.css", "/app.js", "/manifest.webmanifest", "/sw.js"],
        "api": [
            "/api/health",
            "/api/capabilities",
            "/api/auth/*",
            "/api/i18n/*",
            "/api/assets/*",
            "/api/templates/*",
            "/api/sprite-sheet/*",
            "/api/repository/*",
            "/api/scraper/*",
            "/api/lights/*",
        ],
    }
