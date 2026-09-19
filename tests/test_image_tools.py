from pathlib import Path

from PIL import Image

from shared.image_tools import create_spritesheet, inspect_image


def test_image_info(tmp_path: Path):
    source = tmp_path / "input.png"
    Image.new("RGBA", (120, 80)).save(source)

    info = inspect_image(source)
    assert info["width"] == 120
    assert info["height"] == 80


def test_create_spritesheet(tmp_path: Path):
    source = tmp_path / "input.png"
    output = tmp_path / "output.png"
    Image.new("RGBA", (120, 80)).save(source)

    create_spritesheet(source, output, 3, 2)

    with Image.open(output) as image:
        assert image.size == (120, 80)
