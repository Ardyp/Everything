from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_get_device():
    device = {"name": "Lamp", "type": "light", "location": "living"}
    res = client.post("/home/devices", json=device)
    assert res.status_code == 200
    device_id = res.json()["id"]

    res = client.get("/home/devices")
    assert res.status_code == 200
    assert any(d["id"] == device_id for d in res.json())
