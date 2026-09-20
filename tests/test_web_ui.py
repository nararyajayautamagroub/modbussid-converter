from pathlib import Path


def test_v42_ui_has_auth_settings_and_pwa():
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
    assert 'game-mod-asset-lab-v4.2' in sw
    assert 'data-i18n="logout_all"' in html
    assert 'data-i18n="bussid_zip"' in html
    assert 'data-i18n="upload_inspect"' in html
