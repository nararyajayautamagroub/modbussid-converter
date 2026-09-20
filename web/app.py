from pathlib import Path
from tempfile import TemporaryDirectory
import os
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from shared.auth_db import init_db

from shared.light_animation import VALID_LIGHT_TYPES, build_animation, to_dict
from shared.package_export import export_light_package
from web.asset_api import router as asset_router
from web.catalog import repository_catalog, repository_tree
from web.template_api import router as template_router
from web.sprite_api import router as sprite_router
from web.scraper_api import router as scraper_router
from web.auth_api import GOOGLE_CONFIGURED, router as auth_router
from shared.version import APP_VERSION, PRODUCT_NAME
from web.i18n_api import router as i18n_router

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
GENERATED.mkdir(exist_ok=True)

app = FastAPI(title=PRODUCT_NAME, version=APP_VERSION)
init_db()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET") or secrets.token_hex(32),
    session_cookie="oauth_session",
    max_age=900,
    same_site="lax",
    https_only=os.getenv("COOKIE_SECURE", "0") == "1",
)
app.include_router(asset_router)
app.include_router(template_router)
app.include_router(sprite_router)
app.include_router(scraper_router)
app.include_router(auth_router)
app.include_router(i18n_router)


@app.get("/", tags=["web"])
def index():
    return FileResponse(ROOT / "index.html")


@app.get("/manifest.webmanifest", tags=["pwa"])
def manifest():
    return FileResponse(ROOT / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js", tags=["pwa"])
def service_worker():
    return FileResponse(ROOT / "sw.js", media_type="application/javascript")


@app.get("/icon.svg", tags=["pwa"])
def icon():
    return FileResponse(ROOT / "icon.svg", media_type="image/svg+xml")


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "service": "game-mod-asset-lab", "version": app.version, "google_login": GOOGLE_CONFIGURED}


@app.get("/api/categories", tags=["catalog"])
def categories():
    return repository_catalog()["categories"]


@app.get("/api/repository/tree", tags=["catalog"])
def repository_tree_endpoint(prefix: str = ""):
    return repository_tree(prefix)


@app.get("/api/repository", tags=["catalog"])
def repository():
    return repository_catalog()


@app.get("/api/capabilities", tags=["system"])
def capabilities():
    return {
        "inspect_archive": True,
        "selective_export": True,
        "template_classification": ["ao", "texture", "xor"],
        "light_animation_package": ["strobo", "rotator", "ledbar"],
        "roblox_public_asset_download": True,
        "roblox_studio_light_script_export": True,
        "native_rbxm_generation": False,
        "native_proprietary_game_format_decode": False,
        "encryption_drm_bypass": False,
        "repository_sync": True,
        "authentication": ["local_register", "local_login", "session_logout", "google_oauth"],
        "settings": ["profile", "language", "theme", "notifications", "password_change"],
        "languages": 10,
        "pwa": True,
        "scraper": True,
        "scraper_crawl": True,
        "version": APP_VERSION,
    }


@app.get("/api/lights/{light_type}", tags=["lights"])
def preview(light_type: str, fps: int = 30):
    if light_type not in VALID_LIGHT_TYPES:
        raise HTTPException(status_code=404, detail="Jenis lampu tidak dikenal.")
    try:
        return to_dict(build_animation(light_type, fps))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/lights/{light_type}/download", tags=["lights"])
def download(light_type: str, platform: str = "roblox"):
    if light_type not in VALID_LIGHT_TYPES:
        raise HTTPException(status_code=404, detail="Jenis lampu tidak dikenal.")
    if platform not in {"roblox", "bussid"}:
        raise HTTPException(status_code=400, detail="Platform tidak didukung.")

    with TemporaryDirectory() as tmp:
        path = export_light_package(
            light_type, Path(tmp) / f"{platform}_{light_type}", platform
        )
        data = path.read_bytes()

    output = GENERATED / path.name
    output.write_bytes(data)
    return FileResponse(output, filename=output.name, media_type="application/zip")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Referrer-Policy", "strict-origin-when-cross-origin"
    )
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    if request.url.path.startswith("/api/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response
