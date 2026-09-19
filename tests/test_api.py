from fastapi.testclient import TestClient

from web.app import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_template_types():
    response = client.get("/api/templates/types")
    assert response.status_code == 200
    assert response.json()["xor"] == "Kaca/XOR"


def test_capabilities():
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    assert response.json()["repository_sync"] is True


def test_repository_catalog_contains_platforms():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert "bussid" in data
    assert "ets2" in data
    assert "roblox" in data
