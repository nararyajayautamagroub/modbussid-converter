from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
import re

MAX_ASSET_BYTES = 50 * 1024 * 1024
ROBLOX_SUFFIX = ".roblox.com"
_ASSET_PATH = re.compile(
    r"/(?:library|catalog|asset|store/asset|develop/library)/([0-9]+)"
)
_RBXASSET = re.compile(r"^rbxassetid://([0-9]+)$", re.IGNORECASE)


def asset_id_from_url(url: str) -> int:
    raw = url.strip()
    rbx_match = _RBXASSET.fullmatch(raw)
    if rbx_match:
        asset_id = int(rbx_match.group(1))
        if asset_id <= 0:
            raise ValueError("Asset ID Roblox harus lebih besar dari 0.")
        return asset_id

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (
        host == "roblox.com" or host.endswith(ROBLOX_SUFFIX)
    ):
        raise ValueError(
            "Gunakan URL HTTPS resmi Roblox (*.roblox.com) atau rbxassetid://."
        )

    values = parse_qs(parsed.query).get("id", [])
    if not values:
        match = _ASSET_PATH.search(parsed.path)
        values = [match.group(1)] if match else []

    if not values:
        raise ValueError("Asset ID Roblox tidak ditemukan.")

    try:
        asset_id = int(values[0])
    except ValueError as exc:
        raise ValueError("Asset ID Roblox tidak valid.") from exc

    if asset_id <= 0:
        raise ValueError("Asset ID Roblox harus lebih besar dari 0.")
    return asset_id


def download_asset(url: str, target: Path) -> dict:
    asset_id = asset_id_from_url(url)
    request = Request(
        f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}",
        headers={"User-Agent": "Game-Mod-Asset-Lab/2.0"},
    )
    target.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(request, timeout=20) as response:
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > MAX_ASSET_BYTES:
                    raise ValueError("Asset melebihi batas 50 MB.")
            except ValueError as exc:
                if "melebihi" in str(exc):
                    raise
                # Content-Length yang tidak valid diabaikan; batas tetap dicek saat streaming.

        total = 0
        with target.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ASSET_BYTES:
                    target.unlink(missing_ok=True)
                    raise ValueError("Asset melebihi batas 50 MB.")
                handle.write(chunk)

    return {
        "asset_id": asset_id,
        "bytes": total,
        "max_bytes": MAX_ASSET_BYTES,
        "delivery_endpoint": "https://assetdelivery.roblox.com/v1/asset/",
    }
