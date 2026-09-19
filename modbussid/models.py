from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Asset:
    path: Path
    kind: str
    size: int
    metadata: dict = field(default_factory=dict)

@dataclass
class Inspection:
    source: Path
    size: int
    sha256: str
    magic: str
    assets: list[Asset] = field(default_factory=list)
