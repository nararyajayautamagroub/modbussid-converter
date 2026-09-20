from pathlib import Path
from zipfile import ZipFile
import json

from shared.package_export import export_light_package


def test_roblox_light_package_contains_studio_script(tmp_path: Path):
    result = export_light_package(
        "strobo",
        tmp_path / "roblox_strobo",
        "roblox",
    )

    with ZipFile(result) as archive:
        names = set(archive.namelist())
        assert "roblox_strobo.json" in names
        assert "roblox_strobo_studio.lua" in names
        manifest = json.loads(archive.read("roblox_strobo.json").decode("utf-8"))
        assert manifest["version"] == "3.0.0"
        assert "while model.Parent do" in archive.read(
            "roblox_strobo_studio.lua"
        ).decode("utf-8")
