from __future__ import annotations

from pathlib import Path

from core.asset_inspector import inspect_file
from core.roblox_url import download_asset
from core.version import APP_VERSION

VERSION = APP_VERSION


def fetch(url: str, destination: Path) -> dict:
    result = download_asset(url, destination)
    result["inspection"] = inspect_file(destination)
    result["version"] = VERSION
    return result


__all__ = ["VERSION", "fetch"]
