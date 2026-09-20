#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import tempfile

import httpx


async def run_smoke() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["GAME_MOD_DB"] = str(Path(tmp) / "smoke.db")
        from web.app import app

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://smoke.test",
        ) as client:
            checks = [
                ("/api/health", 200),
                ("/api/capabilities", 200),
                ("/api/auth/status", 200),
                ("/api/gateway/health", 200),
                ("/api/i18n/en", 200),
                ("/styles.css", 200),
                ("/app.js", 200),
                ("/manifest.webmanifest", 200),
                ("/sw.js", 200),
                (
                    "/api/scraper/fetch?url="
                    "http%3A%2F%2F127.0.0.1%3A8000%2F",
                    400,
                ),
            ]
            for path, expected in checks:
                response = await client.get(path)
                if response.status_code != expected:
                    raise RuntimeError(
                        f"Smoke check failed: {path}: "
                        f"{response.status_code} != {expected}"
                    )

            health = (await client.get("/api/health")).json()
            if health["version"] != "4.2.0":
                raise RuntimeError("Backend version is not v4.2.0.")

            gateway = (await client.get("/api/gateway/health")).json()
            capabilities = (await client.get("/api/capabilities")).json()
            if capabilities["languages"] != 10:
                raise RuntimeError("Expected exactly 10 supported languages.")
            if not capabilities["scraper"] or not capabilities["scraper_crawl"]:
                raise RuntimeError("Scraper capabilities are not enabled.")
            if "profile" not in capabilities["settings"]:
                raise RuntimeError("Profile settings capability is missing.")

            translations = (await client.get("/api/i18n/en")).json()["translations"]
            required = {
                "account",
                "settings",
                "logout_all",
                "asset_inspector_exporter",
                "scraper",
                "lights",
            }
            missing = sorted(key for key in required if key not in translations)
            if missing:
                raise RuntimeError(
                    "Missing English translation keys: " + ", ".join(missing)
                )


def main() -> int:
    asyncio.run(run_smoke())
    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
