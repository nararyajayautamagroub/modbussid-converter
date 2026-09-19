import subprocess
from pathlib import Path

class SpriteSheetError(RuntimeError):
    pass

def video_to_spritesheet(video: Path, out: Path, columns=5, fps=1, width=320, ffmpeg="ffmpeg"):
    if columns < 1 or fps <= 0 or width < 1:
        raise SpriteSheetError("columns, fps, dan width harus valid.")
    out.mkdir(parents=True, exist_ok=True)
    frames = out / "frames"
    frames.mkdir(exist_ok=True)
    pattern = frames / "frame_%06d.png"
    try:
        subprocess.run([ffmpeg, "-y", "-i", str(video), "-vf", f"fps={fps},scale={width}:-1", str(pattern)], check=True)
    except FileNotFoundError as e:
        raise SpriteSheetError("FFmpeg tidak ditemukan.") from e
    except subprocess.CalledProcessError as e:
        raise SpriteSheetError(f"FFmpeg gagal: {e.returncode}") from e
    files = sorted(frames.glob("frame_*.png"))
    if not files:
        raise SpriteSheetError("Tidak ada frame yang dihasilkan.")
    try:
        from PIL import Image
    except ImportError as e:
        raise SpriteSheetError("Pillow diperlukan untuk membuat sprite-sheet.") from e
    first = Image.open(files[0]).convert("RGBA")
    rows = (len(files) + columns - 1) // columns
    sheet = Image.new("RGBA", (first.width * columns, first.height * rows), (0, 0, 0, 0))
    for i, p in enumerate(files):
        with Image.open(p) as im:
            sheet.paste(im.convert("RGBA"), ((i % columns) * first.width, (i // columns) * first.height))
    target = out / "spritesheet.png"
    sheet.save(target)
    return {"spritesheet": str(target), "frames": len(files), "columns": columns, "rows": rows}
