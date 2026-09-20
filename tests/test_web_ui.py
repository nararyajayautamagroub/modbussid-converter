from pathlib import Path


def test_v4_ui_has_auth_settings_and_pwa():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert 'id="loggedOut"' in html
    assert 'id="loggedIn"' in html
    assert 'onclick="googleLogin()"' in html
    assert 'id="settingsLanguage"' in html
    assert 'id="settingsTheme"' in html
    assert 'id="menuButton"' in html
    assert '/manifest.webmanifest' in html
    assert '/sw.js' in html

    sw = Path("web/sw.js").read_text(encoding="utf-8")
    assert 'asset-lab-v4.1' in sw
    assert 'data-i18n="upload_inspect"' in html
