import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure location service uses mock data
os.environ.setdefault("MOCK_LOCATION_SERVICE", "true")

# Use a temporary SQLite database during tests
@pytest.fixture(scope="session", autouse=True)
def temp_db(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    yield
    os.environ.pop("DATABASE_URL", None)

@pytest.fixture
def client():
    from main import app
    return TestClient(app)
