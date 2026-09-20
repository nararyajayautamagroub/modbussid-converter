from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from shared.light_animation import VALID_LIGHT_TYPES, build_animation, to_dict
from shared.package_export import export_light_package
from web.asset_api import router as asset_router
from web.catalog import repository_catalog, repository_tree
from web.template_api import router as template_router
from web.sprite_api import router as sprite_router
from web.scraper_api import router as scraper_router
from shared.version import APP_VERSION, PRODUCT_NAME

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
GENERATED.mkdir(exist_ok=True)

app = FastAPI(title=PRODUCT_NAME, version=APP_VERSION)
app.include_router(asset_router)
app.include_router(template_router)
app.include_router(sprite_router)
app.include_router(scraper_router)


@app.get("/", tags=["web"])
def index():
    return FileResponse(ROOT / "index.html")


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "service": "game-mod-asset-lab", "version": app.version}


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
