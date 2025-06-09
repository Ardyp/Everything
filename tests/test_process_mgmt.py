from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_process_list():
    res = client.get("/process/list?limit=1")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
