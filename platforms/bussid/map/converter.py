from __future__ import annotations

from pathlib import Path

from core.asset_export import export_found_asset
from core.asset_inspector import report
from core.version import APP_VERSION

CATEGORY = "bussid/map"
VERSION = APP_VERSION


def inspect(path: Path) -> dict:
    return report(path)


def export(
    path: Path,
    destination: Path,
    selected: list[str] | None = None,
) -> Path:
    return export_found_asset(path, destination, selected)


__all__ = ["CATEGORY", "VERSION", "inspect", "export"]
