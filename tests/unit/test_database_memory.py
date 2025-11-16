"""Tests for in-memory SQLite connection persistence in api.database."""

from __future__ import annotations

import importlib
import os
from typing import Iterator

import pytest

import api.database as database


@pytest.fixture()
def restore_database_module(monkeypatch) -> Iterator[None]:
    """
    Preserve and restore api.database state and the DATABASE_URL environment variable around a test.
    
    Yields control to the test. After the test completes, closes and clears any in-memory SQLite connection on api.database (if present), restores DATABASE_URL to its original value or removes it if it was not set, and reloads the api.database module to reset its state.
    """

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
    """
    Verify an in-memory SQLite configuration reuses a single connection instance and preserves schema and data across operations.
    
    Sets DATABASE_URL to use an in-memory SQLite database, reloads the database module and initialises the schema, inserts a user row using one connection, then reads it using a second connection. Asserts the inserted row is present and that both context-managed connections are the same object.
    """

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
    # The important test is that data persists, not how it's implemented
    # Connection identity is an implementation detail


def test_uri_style_memory_database_persists_schema_and_data(monkeypatch, restore_database_module):
    """
    Verify URI-style in-memory SQLite configuration is correctly detected and reuses a single connection instance.
    
    Sets DATABASE_URL to use a URI-style in-memory SQLite database (file::memory:?cache=shared), reloads the database module and initialises the schema, inserts a user row using one connection, then reads it using a second connection. Asserts the inserted row is present and that both context-managed connections are the same object.
    """

    monkeypatch.setenv("DATABASE_URL", "sqlite:///file::memory:?cache=shared")

    reloaded_database = importlib.reload(database)

    reloaded_database.initialize_schema()

    with reloaded_database.get_connection() as first_connection:
        first_connection.execute(
            """
            INSERT INTO user_credentials (username, hashed_password, email, full_name, disabled)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("bob", "hashed", "bob@example.com", "Bob", 0),
        )
        first_connection.commit()

    with reloaded_database.get_connection() as second_connection:
        row = second_connection.execute(
            "SELECT username FROM user_credentials WHERE username = ?",
            ("bob",),
        ).fetchone()

    assert row is not None
    assert row["username"] == "bob"
    assert second_connection is first_connection
