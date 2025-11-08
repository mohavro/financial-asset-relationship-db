"""Tests for in-memory SQLite connection persistence in api.database."""

from __future__ import annotations

import importlib
import os
from typing import Iterator

import pytest

import api.database as database


@pytest.fixture()
def restore_database_module(monkeypatch) -> Iterator[None]:
    """Reload api.database after test and restore DATABASE_URL env."""

    original_url = os.environ.get("DATABASE_URL")

    yield

    # Close any in-memory connection that may have been created during the test.
    if getattr(database, "_MEMORY_CONNECTION", None) is not None:
        database._MEMORY_CONNECTION.close()
        database._MEMORY_CONNECTION = None

    if original_url is None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("DATABASE_URL", original_url)

    importlib.reload(database)


def test_in_memory_database_persists_schema_and_data(monkeypatch, restore_database_module):
    """In-memory configuration should reuse a single connection for all helpers."""

    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    reloaded_database = importlib.reload(database)

    reloaded_database.initialize_schema()

    with reloaded_database.get_connection() as first_connection:
        first_connection.execute(
            """
            INSERT INTO user_credentials (username, hashed_password, email, full_name, disabled)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("alice", "hashed", "alice@example.com", "Alice", 0),
        )
        first_connection.commit()

    with reloaded_database.get_connection() as second_connection:
        row = second_connection.execute(
            "SELECT username FROM user_credentials WHERE username = ?",
            ("alice",),
        ).fetchone()

    assert row is not None
    assert row["username"] == "alice"
    assert second_connection is first_connection
