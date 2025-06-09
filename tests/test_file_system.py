from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_directory(tmp_path):
    tmp_dir = tmp_path
    res = client.get(f"/files/list?path={tmp_dir}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
