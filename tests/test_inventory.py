from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_get_item():
    item = {"name": "Apples", "category": "fruit", "quantity": 5}
    res = client.post("/inventory/items", json=item)
    assert res.status_code == 200
    item_id = res.json()["id"]

    res = client.get("/inventory/items")
    assert res.status_code == 200
    assert any(i["id"] == item_id for i in res.json())
