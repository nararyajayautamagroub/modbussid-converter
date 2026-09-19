import asyncio

import httpx

from web.app import app


def request(path: str) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.get(path)

    return asyncio.run(run())


def test_health():
    response = request("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_template_types():
    response = request("/api/templates/types")
    assert response.status_code == 200
    assert response.json()["xor"] == "Kaca/XOR"


def test_capabilities():
    response = request("/api/capabilities")
    assert response.status_code == 200
    assert response.json()["repository_sync"] is True


def test_repository_catalog_contains_platforms():
    response = request("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert "bussid" in data
    assert "ets2" in data
    assert "roblox" in data


def test_path_security_blocks_outside_files():
    response = request("/api/templates/classify?path=/etc/passwd")
    assert response.status_code == 400
