from pathlib import Path


def test_v50_ui_has_auth_settings_and_pwa():
    html = Path("frontend/index.html").read_text(encoding="utf-8")
    assert 'id="loggedOut"' in html
    assert 'id="loggedIn"' in html
    assert 'data-action="googleLogin"' in html
    assert 'id="settingsLanguage"' in html
    assert 'id="settingsTheme"' in html
    assert 'id="menuButton"' in html
    assert '/manifest.webmanifest' in html
    app_js = Path("frontend/app.js").read_text(encoding="utf-8")
    assert 'navigator.serviceWorker.register("/sw.js")' in app_js
    assert 'PT. NARARYA JAYA UTAMA GROUB - All Right Reserved' in html

    sw = Path("frontend/sw.js").read_text(encoding="utf-8")
    assert 'game-mod-asset-lab-v5.0' in sw
    assert 'data-i18n="logout_all"' in html
    app_js = Path("frontend/app.js").read_text(encoding="utf-8")
    assert 'data-i18n="bussid_zip"' in app_js
    assert 'data-i18n="upload_inspect"' in html
