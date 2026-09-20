from dataclasses import asdict, dataclass
from typing import Literal

LightType = Literal["strobo", "rotator", "ledbar"]
VALID_LIGHT_TYPES = frozenset({"strobo", "rotator", "ledbar"})


@dataclass(frozen=True)
class LightFrame:
    time: float
    intensity: float
    enabled: bool
    phase: float = 0.0


@dataclass(frozen=True)
class LightAnimation:
    name: str
    light_type: LightType
    fps: int
    loop: bool
    frames: list[LightFrame]


def build_animation(light_type: LightType, fps: int = 30) -> LightAnimation:
    if light_type not in VALID_LIGHT_TYPES:
        raise ValueError("Jenis lampu tidak dikenal.")
    if not isinstance(fps, int) or isinstance(fps, bool) or not 1 <= fps <= 240:
        raise ValueError("FPS harus bilangan bulat 1-240.")

    if light_type == "strobo":
        frames = [
            LightFrame(0.0, 1.0, True),
            LightFrame(0.06, 0.0, False),
            LightFrame(0.12, 1.0, True),
            LightFrame(0.18, 0.0, False),
        ]
    elif light_type == "rotator":
        frames = [
            LightFrame(0.0, 1.0, True, 0.0),
            LightFrame(0.25, 1.0, True, 90.0),
            LightFrame(0.5, 1.0, True, 180.0),
            LightFrame(0.75, 1.0, True, 270.0),
        ]
    else:
        frames = [
            LightFrame(0.0, 1.0, True),
            LightFrame(0.2, 0.35, True),
            LightFrame(0.4, 1.0, True),
            LightFrame(0.6, 0.35, True),
            LightFrame(0.8, 1.0, True),
        ]

    return LightAnimation(
        name=f"{light_type}_animation",
        light_type=light_type,
        fps=fps,
        loop=True,
        frames=frames,
    )


def to_dict(animation: LightAnimation) -> dict:
    data = asdict(animation)
    data["format"] = "game-mod-light-animation-v1"
    return data
