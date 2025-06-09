from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_get_reminder():
    reminder = {"title": "Buy milk", "due_date": "2030-01-01T10:00:00"}
    res = client.post("/reminders/", json=reminder)
    assert res.status_code == 200
    reminder_id = res.json()["id"]

    res = client.get("/reminders/")
    assert res.status_code == 200
    assert any(r["id"] == reminder_id for r in res.json())
