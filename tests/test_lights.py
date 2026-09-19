import pytest

from shared.light_animation import build_animation


def test_light_types():
    for kind in ("strobo", "rotator", "ledbar"):
        animation = build_animation(kind)
        assert animation.light_type == kind
        assert animation.loop is True
        assert animation.frames


def test_light_fps_validation():
    with pytest.raises(ValueError):
        build_animation("strobo", 0)
    with pytest.raises(ValueError):
        build_animation("strobo", 241)
