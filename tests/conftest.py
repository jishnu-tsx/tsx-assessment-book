import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage import storage


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear storage before each test"""
    storage.clear()
    yield
    storage.clear()
