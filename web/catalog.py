from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
GITHUB_REPO = os.getenv(
    "GITHUB_REPO", "nararyajayautamagroub/modbussid-converter"
)
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
_REMOTE_CACHE: tuple[float, dict] | None = None
CACHE_SECONDS = 15
IGNORED_LOCAL_PARTS = {"__pycache__", ".git", "uploads", "generated"}


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_LOCAL_PARTS for part in path.parts)


def _local_catalog() -> dict:
    categories = {}
    for platform in ("bussid", "ets2", "roblox"):
        platform_root = ROOT / platform
        if not platform_root.is_dir():
            continue
        categories[platform] = {}
        for folder in sorted(p for p in platform_root.iterdir() if p.is_dir()):
            files = [
                p.relative_to(folder).as_posix()
                for p in sorted(folder.rglob("*"))
                if p.is_file() and not _is_ignored(p)
            ]
            categories[platform][folder.name] = {"files": files, "count": len(files)}

    template_root = ROOT / "templates"
    templates = [
        p.relative_to(ROOT).as_posix()
        for p in sorted(template_root.rglob("*"))
        if p.is_file() and not _is_ignored(p)
    ] if template_root.is_dir() else []

    return {
        "source": "local_repository",
        "repository": GITHUB_REPO,
        "commit": None,
        "categories": categories,
        "templates": templates,
    }


def _github_catalog() -> dict:
    global _REMOTE_CACHE
    now = time.time()
    if _REMOTE_CACHE and now - _REMOTE_CACHE[0] < CACHE_SECONDS:
        return _REMOTE_CACHE[1]

    request = Request(
        f"{GITHUB_API}/git/trees/main?recursive=1",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Game-Mod-Asset-Lab/2.0",
        },
    )
    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    files = [
        item["path"]
        for item in payload.get("tree", [])
        if item.get("type") == "blob"
    ]
    data = {
        "source": "github",
        "repository": GITHUB_REPO,
        "commit": payload.get("sha"),
        "file_count": len(files),
        "files": files,
        "truncated": bool(payload.get("truncated", False)),
        "updated_at": time.time(),
    }
    _REMOTE_CACHE = (now, data)
    return data


def repository_catalog() -> dict:
    local = _local_catalog()
    try:
        local["remote"] = _github_catalog()
        local["remote_status"] = "ok"
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        local["remote"] = None
        local["remote_status"] = f"unavailable: {exc}"
    return local
