from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_location_details():
    res = client.get("/location/details/test")
    assert res.status_code == 200
    assert "formatted_address" in res.json()
