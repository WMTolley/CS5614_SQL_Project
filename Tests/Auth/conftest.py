"""Shared setup for the endpoint tests. They run against a real database, which the backend
rebuilds when it is imported, so they are skipped when the database is unreachable."""

import importlib
import os

import pytest
from fastapi.testclient import TestClient

from db import sql_commands

ADMIN_USERNAME = "test_admin"
ADMIN_PASSWORD = "test-admin-password"


@pytest.fixture(scope="session")
def client():
    os.environ["ADMIN_USERNAME"] = ADMIN_USERNAME
    os.environ["ADMIN_PASSWORD"] = ADMIN_PASSWORD
    # Lets the tests point at a database that isn't the dev container's
    sql_commands.DB_CONFIG["host"] = os.environ.get(
        "TEST_DB_HOST", sql_commands.DB_CONFIG["host"]
    )
    sql_commands.DB_CONFIG["port"] = int(
        os.environ.get("TEST_DB_PORT", sql_commands.DB_CONFIG["port"])
    )
    try:
        backend = importlib.import_module("backend.backend")
    except RuntimeError:
        pytest.skip("Database container not reachable.")
    with TestClient(backend.app) as test_client:
        yield test_client
    backend.connection.close()


@pytest.fixture(scope="session")
def admin_headers(client):
    response = client.post(
        "/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}
