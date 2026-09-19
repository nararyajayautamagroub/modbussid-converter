from __future__ import annotations

import re
from pathlib import Path

TEMPLATES = {"ao": "AO", "texture": "Texture", "xor": "Kaca/XOR"}
_TOKEN_SPLIT = re.compile(r"[^a-z0-9]+")


def _tokens(name: str) -> set[str]:
    return {token for token in _TOKEN_SPLIT.split(name.lower()) if token}


def classify_template(path: Path) -> str:
    tokens = _tokens(path.stem)
    normalized = path.stem.lower().replace("_", " ").replace("-", " ")

    if {"ambient", "occlusion"} <= tokens or "ambient occlusion" in normalized:
        return "ao"
    if "ao" in tokens:
        return "ao"
    if tokens.intersection({"kaca", "glass", "window", "windowglass", "xor"}):
        return "xor"
    return "texture"


def template_info(path: Path) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    kind = classify_template(path)
    return {
        "name": path.name,
        "template": kind,
        "label": TEMPLATES[kind],
        "extension": path.suffix.lower(),
        "size": path.stat().st_size,
    }
