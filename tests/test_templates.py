from pathlib import Path

from core.template_classifier import classify_template


def test_template_defaults(tmp_path: Path):
    assert classify_template(tmp_path / "bus.png") == "texture"
    assert classify_template(tmp_path / "bus_ao.png") == "ao"
    assert classify_template(tmp_path / "ao_bus.png") == "ao"
    assert classify_template(tmp_path / "radio.png") == "texture"
    assert classify_template(tmp_path / "ambient_occlusion.png") == "ao"
    assert classify_template(tmp_path / "window_glass.png") == "xor"
    assert classify_template(tmp_path / "glass_bus.png") == "xor"
