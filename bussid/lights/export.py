from __future__ import annotations

from pathlib import Path

from shared.package_export import export_light_package
from shared.version import APP_VERSION

VERSION = APP_VERSION


def export(light_type: str, output: Path) -> Path:
    return export_light_package(light_type, output, "bussid")


__all__ = ["VERSION", "export"]
