from pathlib import Path
from zipfile import ZipFile

from shared.asset_export import export_found_asset


def test_zip_selected_export(tmp_path: Path):
    source = tmp_path / "source.zip"
    output = tmp_path / "output.zip"

    with ZipFile(source, "w") as archive:
        archive.writestr("vehicle/a.txt", b"A")
        archive.writestr("vehicle/b.txt", b"B")

    export_found_asset(source, output, ["vehicle/b.txt"])

    with ZipFile(output) as archive:
        assert archive.namelist() == ["vehicle/b.txt", "manifest.json"]
        assert archive.read("vehicle/b.txt") == b"B"
