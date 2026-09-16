import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import WaitlistStore, get_store


@pytest.fixture
def store() -> WaitlistStore:
    return WaitlistStore()


@pytest.fixture
def client(store: WaitlistStore):
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
