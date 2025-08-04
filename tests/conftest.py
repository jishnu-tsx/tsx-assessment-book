import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage import storage

@pytest.fixture
def client() -> TestClient:
    """Provide a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear storage before each test"""
    storage.clear()
    yield
    storage.clear()
