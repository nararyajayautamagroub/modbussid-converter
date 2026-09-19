from pathlib import Path

MAGICS = {
    b"PK\\x03\\x04": "zip",
    b"Rar!\\x1a\\x07\\x00": "rar4",
    b"Rar!\\x1a\\x07\\x01\\x00": "rar5",
    b"7z\\xbc\\xaf\\x27\\x1c": "7z",
    b"\\x1f\\x8b": "gzip",
    b"\\xfd7zXZ\\x00": "xz",
}

def detect_magic(path: Path) -> str:
    with path.open("rb") as f:
        head = f.read(16)
    for signature, name in MAGICS.items():
        if head.startswith(signature):
            return name
    return "unknown"
