from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from core.image_tools import extract_sprites, inspect_image


def test_image_info(tmp_path: Path):
    source = tmp_path / "input.png"
    Image.new("RGBA", (120, 80)).save(source)

    info = inspect_image(source)
    assert info["width"] == 120
    assert info["height"] == 80


def test_extract_sprites(tmp_path: Path):
    source = tmp_path / "input.png"
    output = tmp_path / "frames.zip"
    Image.new("RGBA", (120, 80)).save(source)

    extract_sprites(source, output, 3, 2)

    with ZipFile(output) as archive:
        assert len(archive.namelist()) == 6
