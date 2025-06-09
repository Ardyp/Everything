from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_get_appointment():
    appointment = {
        "title": "Doctor",
        "start_time": "2030-01-01T09:00:00",
        "end_time": "2030-01-01T10:00:00"
    }
    res = client.post("/appointments/", json=appointment)
    assert res.status_code == 200
    appointment_id = res.json()["id"]

    res = client.get("/appointments/")
    assert res.status_code == 200
    assert any(a["id"] == appointment_id for a in res.json())
