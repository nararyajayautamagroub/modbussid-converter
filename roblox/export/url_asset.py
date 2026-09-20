from __future__ import annotations

from pathlib import Path

from shared.asset_inspector import inspect_file
from shared.roblox_url import download_asset
from shared.version import APP_VERSION

VERSION = APP_VERSION


def fetch(url: str, destination: Path) -> dict:
    result = download_asset(url, destination)
    result["inspection"] = inspect_file(destination)
    result["version"] = VERSION
    return result


__all__ = ["VERSION", "fetch"]
