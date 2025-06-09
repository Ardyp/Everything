from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_system_info():
    res = client.get("/system/info")
    assert res.status_code == 200
    assert "os" in res.json()
