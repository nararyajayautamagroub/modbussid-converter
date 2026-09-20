from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tga"}


def inspect_image(path: Path) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    try:
        with Image.open(path) as image:
            return {
                "name": path.name,
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "frames": getattr(image, "n_frames", 1),
                "animated": bool(getattr(image, "is_animated", False)),
            }
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("File bukan image yang didukung Pillow.") from exc


def extract_sprites(
    source: Path,
    destination: Path,
    columns: int,
    rows: int,
) -> Path:
    if not 1 <= columns <= 64 or not 1 <= rows <= 64:
        raise ValueError("Columns dan rows harus berada di antara 1-64.")

    source = source.resolve()
    destination = destination.resolve()

    try:
        with Image.open(source) as image:
            image = image.convert("RGBA")
            frame_width = image.width // columns
            frame_height = image.height // rows

            if frame_width < 1 or frame_height < 1:
                raise ValueError("Grid lebih besar daripada ukuran image.")

            with zipfile.ZipFile(
                destination,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            ) as archive:
                frame_number = 0
                for row in range(rows):
                    for column in range(columns):
                        left = column * frame_width
                        top = row * frame_height
                        frame = image.crop(
                            (left, top, left + frame_width, top + frame_height)
                        )
                        name = f"frame_{frame_number:04d}.png"
                        buffer = BytesIO()
                        frame.save(buffer, format="PNG")
                        archive.writestr(name, buffer.getvalue())
                        frame_number += 1
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("Source bukan image yang dapat diproses.") from exc

    return destination
