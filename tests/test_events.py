from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_get_event():
    event = {
        "device_id": 1,
        "event_type": "motion",
        "description": "motion detected"
    }
    res = client.post("/events/", json=event)
    assert res.status_code == 200
    event_id = res.json()["id"]

    res = client.get("/events/")
    assert res.status_code == 200
    assert any(e["id"] == event_id for e in res.json())
