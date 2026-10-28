"""Lets every test run against a database that isn't the dev container's, by setting
TEST_DB_HOST / TEST_DB_PORT (for example a throwaway Postgres on localhost)."""

import os

import pytest

from db import sql_commands


@pytest.fixture(scope="session", autouse=True)
def test_database_config():
    sql_commands.DB_CONFIG["host"] = os.environ.get(
        "TEST_DB_HOST", sql_commands.DB_CONFIG["host"]
    )
    sql_commands.DB_CONFIG["port"] = int(
        os.environ.get("TEST_DB_PORT", sql_commands.DB_CONFIG["port"])
    )
