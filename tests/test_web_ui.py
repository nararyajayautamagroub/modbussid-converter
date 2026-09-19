from pathlib import Path


def test_web_ui_has_green_theme_and_hamburger():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "--green:#16a34a" in html
    assert 'id="menuButton"' in html
    assert 'aria-label="Buka menu"' in html
    assert 'class="drawer"' in html
    assert "/api/repository/tree" in html
