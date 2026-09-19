from pathlib import Path

from shared.asset_inspector import inspect_file


def test_inspector_metadata(tmp_path: Path):
    image = tmp_path / "bussid" / "vehicle" / "bus_ao.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"not-real-png")

    data = inspect_file(image)
    assert data["category"] == "bussid/vehicle"
    assert data["template"] == "ao"
