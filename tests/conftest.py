import pytest
from fastapi.testclient import TestClient

from app.main import app


# Creates a test client for the FastAPI application
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client