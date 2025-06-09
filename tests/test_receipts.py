from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_get_receipt():
    receipt = {
        "store_name": "Market",
        "purchase_date": "2030-01-01T12:00:00",
        "items": [{"item_name": "Bread", "quantity": 1, "unit_price": 2.5, "total_price": 2.5}],
        "total_amount": 2.5,
        "payment_method": "cash"
    }
    res = client.post("/receipts/", json=receipt)
    assert res.status_code == 200
    receipt_id = res.json()["id"]

    res = client.get("/receipts/")
    assert res.status_code == 200
    assert any(r["id"] == receipt_id for r in res.json())
