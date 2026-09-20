import asyncio
from pathlib import Path

import httpx


def test_local_register_login_logout(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("GAME_MOD_DB", str(tmp_path / "auth.db"))
    from shared.auth_db import init_db

    init_db()

    from web.app import app

    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            register = await client.post(
                "/api/auth/register",
                json={
                    "name": "Test User",
                    "email": "test@example.com",
                    "password": "StrongPass1",
                    "language": "en",
                },
            )
            assert register.status_code == 200
            assert register.json()["user"]["email"] == "test@example.com"

            me = await client.get("/api/auth/me")
            assert me.status_code == 200
            assert me.json()["language"] == "en"

            settings = await client.put(
                "/api/auth/settings",
                json={
                    "language": "ja",
                    "theme": "dark",
                    "notifications": False,
                },
            )
            assert settings.status_code == 200
            assert settings.json()["user"]["language"] == "ja"

            change = await client.put(
                "/api/auth/password",
                json={
                    "current_password": "StrongPass1",
                    "new_password": "NewStrong2",
                },
            )
            assert change.status_code == 200

            logout = await client.post("/api/auth/logout")
            assert logout.status_code == 200

            me_after_logout = await client.get("/api/auth/me")
            assert me_after_logout.status_code == 401

            login = await client.post(
                "/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "NewStrong2",
                },
            )
            assert login.status_code == 200

    asyncio.run(run())


def test_auth_status_and_i18n():
    from web.app import app

    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            status = await client.get("/api/auth/status")
            assert status.status_code == 200
            assert len(status.json()["languages"]) == 10

            i18n = await client.get("/api/i18n/en")
            assert i18n.status_code == 200
            assert i18n.json()["translations"]["login"] == "Login"

            health = await client.get("/api/health")
            assert health.status_code == 200
            assert health.json()["version"] == "4.1.0"
            feature_i18n = await client.get("/api/i18n/en")
            assert feature_i18n.json()["translations"]["asset_inspector_exporter"] == "Asset Inspector & Exporter"

    asyncio.run(run())


def test_auth_rate_limit_helpers(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("GAME_MOD_DB", str(tmp_path / "rate.db"))
    from shared.auth_db import (
        AUTH_RATE_MAX_FAILURES,
        auth_rate_limited,
        clear_auth_failures,
        init_db,
        record_auth_failure,
    )

    init_db()
    rate_key = "test:login-rate"
    clear_auth_failures(rate_key)
    for _ in range(AUTH_RATE_MAX_FAILURES):
        record_auth_failure(rate_key)
    assert auth_rate_limited(rate_key) > 0
    clear_auth_failures(rate_key)
    assert auth_rate_limited(rate_key) == 0
