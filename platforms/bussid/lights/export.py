from __future__ import annotations

from pathlib import Path

from core.package_export import export_light_package
from core.version import APP_VERSION

VERSION = APP_VERSION


def export(light_type: str, output: Path) -> Path:
    return export_light_package(light_type, output, "bussid")


__all__ = ["VERSION", "export"]
