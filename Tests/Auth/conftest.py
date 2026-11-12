"""Shared setup for the endpoint tests. They run against a real database, which the backend
rebuilds when it is imported, so they are skipped when the database is unreachable."""

import importlib
import os
import sys

import pytest
from fastapi.testclient import TestClient

ADMIN_USERNAME = "test_admin"
ADMIN_PASSWORD = "test-admin-password"


@pytest.fixture(scope="module")
def client():
    os.environ["ADMIN_USERNAME"] = ADMIN_USERNAME
    os.environ["ADMIN_PASSWORD"] = ADMIN_PASSWORD
    # A fresh import gives this module its own connection and a freshly seeded database
    sys.modules.pop("backend.backend", None)
    try:
        backend = importlib.import_module("backend.backend")
    except RuntimeError:
        pytest.skip("Database container not reachable.")
    with TestClient(backend.app) as test_client:
        yield test_client
    # Closing releases the table locks, so other test files can rebuild the schema
    backend.connection.close()
    sys.modules.pop("backend.backend", None)


@pytest.fixture(scope="module")
def admin_headers(client):
    response = client.post(
        "/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}
