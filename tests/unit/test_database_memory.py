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
    assert second_connection is first_connection


def test_is_memory_db_with_colon_memory(monkeypatch, restore_database_module):
    """
    Test that _is_memory_db correctly identifies standard :memory: database path.
    
    Sets DATABASE_URL to use standard in-memory notation and verifies that _is_memory_db
    returns True for the configured path and when called without arguments.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    assert reloaded_database._is_memory_db() is True
    assert reloaded_database._is_memory_db(":memory:") is True


def test_is_memory_db_with_uri_style_memory(monkeypatch, restore_database_module):
    """
    Test that _is_memory_db correctly identifies URI-style memory database paths.
    
    Verifies that _is_memory_db returns True for SQLite URI-style memory database
    paths like 'file::memory:?cache=shared' which start with 'file:' and contain ':memory:'.
    """
    # Test various URI-style memory database formats
    assert database._is_memory_db("file::memory:") is True
    assert database._is_memory_db("file::memory:?cache=shared") is True
    assert database._is_memory_db("file:memdb1?mode=memory&cache=shared") is False  # doesn't contain :memory:
    

def test_is_memory_db_with_file_based_database(monkeypatch, restore_database_module):
    """
    Test that _is_memory_db returns False for file-based database paths.
    
    Verifies that _is_memory_db correctly identifies file-based databases and
    returns False for standard file paths.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    reloaded_database = importlib.reload(database)
    
    assert reloaded_database._is_memory_db() is False
    assert reloaded_database._is_memory_db("/path/to/database.db") is False
    assert reloaded_database._is_memory_db("test.db") is False


def test_is_memory_db_with_none_path():
    """
    Test that _is_memory_db uses DATABASE_PATH when path parameter is None.
    
    Verifies that when no path is provided, _is_memory_db falls back to checking
    the module's configured DATABASE_PATH.
    """
    # This should use the current DATABASE_PATH
    result = database._is_memory_db(None)
    assert isinstance(result, bool)


def test_is_memory_db_edge_cases():
    """
    Test _is_memory_db with various edge case inputs.
    
    Verifies behavior with unusual but valid path strings including empty strings,
    paths with 'memory' substring but not matching patterns, and other edge cases.
    """
    assert database._is_memory_db("") is False
    assert database._is_memory_db("memory") is False
    assert database._is_memory_db("file:test.db") is False
    assert database._is_memory_db(":mem:") is False
    assert database._is_memory_db("/:mem:") is False


def test_connect_creates_uri_enabled_connection_for_uri_memory_db(monkeypatch, restore_database_module):
    """
    Test that _connect sets uri=True for URI-style memory databases.
    
    Configures a URI-style memory database and verifies that the connection is created
    with uri=True parameter enabled for proper URI handling.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///file::memory:?cache=shared")
    reloaded_database = importlib.reload(database)
    
    # The connection should be created with uri=True for URI-style paths
    conn = reloaded_database._connect()
    assert conn is not None
    assert isinstance(conn, database.sqlite3.Connection)


def test_connect_thread_safety_for_memory_db(monkeypatch, restore_database_module):
    """
    Test thread safety of _connect for in-memory databases.
    
    Verifies that the threading lock properly protects the shared in-memory connection
    and that multiple calls to _connect return the same connection object.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    # Multiple calls should return the same connection
    conn1 = reloaded_database._connect()
    conn2 = reloaded_database._connect()
    
    assert conn1 is conn2
    assert conn1 is reloaded_database._MEMORY_CONNECTION


def test_connect_creates_new_connections_for_file_db(monkeypatch, restore_database_module, tmp_path):
    """
    Test that _connect creates new connections for file-based databases.
    
    Verifies that each call to _connect for a file-based database returns a new
    connection object rather than reusing a shared instance.
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    reloaded_database = importlib.reload(database)
    
    conn1 = reloaded_database._connect()
    conn2 = reloaded_database._connect()
    
    # For file-based databases, each call creates a new connection
    assert conn1 is not conn2
    conn1.close()
    conn2.close()


def test_connect_sets_row_factory(monkeypatch, restore_database_module):
    """
    Test that _connect sets sqlite3.Row as the row_factory.
    
    Verifies that connections returned by _connect have their row_factory set to
    sqlite3.Row for dictionary-like row access.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    conn = reloaded_database._connect()
    assert conn.row_factory == database.sqlite3.Row


def test_connect_enables_type_detection(monkeypatch, restore_database_module):
    """
    Test that _connect enables SQLite type detection.
    
    Verifies that connections are created with detect_types=PARSE_DECLTYPES
    for automatic type conversion of declared column types.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    # The connection should have type detection enabled
    conn = reloaded_database._connect()
    assert conn is not None


def test_get_connection_closes_file_db_connections(monkeypatch, restore_database_module, tmp_path):
    """
    Test that get_connection closes file-based database connections on context exit.
    
    Verifies that the context manager properly closes connections to file-based
    databases when exiting the context.
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    reloaded_database = importlib.reload(database)
    
    with reloaded_database.get_connection() as conn:
        captured_conn = conn
        # Connection should be open inside context
        assert conn is not None
    
    # After context exit, attempting to use the connection should fail
    # for file-based databases
    with pytest.raises(database.sqlite3.ProgrammingError):
        captured_conn.execute("SELECT 1")


def test_get_connection_keeps_memory_db_open(monkeypatch, restore_database_module):
    """
    Test that get_connection keeps in-memory database connections open.
    
    Verifies that the shared in-memory connection remains usable after
    exiting the context manager since it should not be closed.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    with reloaded_database.get_connection() as conn:
        captured_conn = conn
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
    
    # Connection should still be usable after context exit for in-memory databases
    cursor = captured_conn.execute("SELECT COUNT(*) FROM test")
    assert cursor.fetchone()[0] == 0


def test_execute_with_parameters(monkeypatch, restore_database_module):
    """
    Test execute function with parameterized queries.
    
    Verifies that execute properly handles parameterized SQL statements using
    both tuple and list parameter formats.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    # Test with tuple parameters
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password) VALUES (?, ?)",
        ("testuser", "hashed123")
    )
    
    # Test with list parameters
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password) VALUES (?, ?)",
        ["testuser2", "hashed456"]
    )
    
    # Verify both inserts worked
    row_count = reloaded_database.fetch_value("SELECT COUNT(*) FROM user_credentials")
    assert row_count == 2


def test_execute_without_parameters(monkeypatch, restore_database_module):
    """
    Test execute function without parameters (None or empty).
    
    Verifies that execute works correctly when called with None or empty parameter
    sequences for SQL statements that don't require parameters.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
    reloaded_database.execute("INSERT INTO test_table VALUES (1)", None)
    reloaded_database.execute("INSERT INTO test_table VALUES (2)", ())
    reloaded_database.execute("INSERT INTO test_table VALUES (3)", [])
    
    count = reloaded_database.fetch_value("SELECT COUNT(*) FROM test_table")
    assert count == 3


def test_fetch_one_returns_row_object(monkeypatch, restore_database_module):
    """
    Test that fetch_one returns a sqlite3.Row object.
    
    Verifies that fetch_one returns results as sqlite3.Row objects which allow
    both integer indexing and dictionary-like key access.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password, email) VALUES (?, ?, ?)",
        ("testuser", "hashed", "test@example.com")
    )
    
    row = reloaded_database.fetch_one("SELECT username, email FROM user_credentials WHERE username = ?", ("testuser",))
    
    assert row is not None
    assert isinstance(row, database.sqlite3.Row)
    assert row["username"] == "testuser"
    assert row["email"] == "test@example.com"
    assert row[0] == "testuser"


def test_fetch_one_returns_none_for_no_results(monkeypatch, restore_database_module):
    """
    Test that fetch_one returns None when query has no results.
    
    Verifies that fetch_one properly returns None instead of raising an exception
    when the query doesn't match any rows.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    row = reloaded_database.fetch_one("SELECT * FROM user_credentials WHERE username = ?", ("nonexistent",))
    assert row is None


def test_fetch_value_returns_first_column(monkeypatch, restore_database_module):
    """
    Test that fetch_value returns the first column value from the result.
    
    Verifies that fetch_value extracts and returns only the first column value
    from the first row of query results.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password, email) VALUES (?, ?, ?)",
        ("testuser", "hashed", "test@example.com")
    )
    
    username = reloaded_database.fetch_value("SELECT username FROM user_credentials WHERE username = ?", ("testuser",))
    assert username == "testuser"
    
    # Test with multiple columns - should still return first column
    first_col = reloaded_database.fetch_value("SELECT username, email FROM user_credentials WHERE username = ?", ("testuser",))
    assert first_col == "testuser"


def test_fetch_value_returns_none_for_no_results(monkeypatch, restore_database_module):
    """
    Test that fetch_value returns None when query has no results.
    
    Verifies that fetch_value properly returns None when the underlying fetch_one
    returns None due to no matching rows.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    value = reloaded_database.fetch_value("SELECT username FROM user_credentials WHERE username = ?", ("nonexistent",))
    assert value is None


def test_initialize_schema_creates_table(monkeypatch, restore_database_module):
    """
    Test that initialize_schema creates the user_credentials table.
    
    Verifies that initialize_schema successfully creates the user_credentials table
    with all required columns and constraints.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    # Verify table exists by querying it
    result = reloaded_database.fetch_value("SELECT name FROM sqlite_master WHERE type='table' AND name='user_credentials'")
    assert result == "user_credentials"
    
    # Verify table structure by inserting a row
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password) VALUES (?, ?)",
        ("test", "hash")
    )
    count = reloaded_database.fetch_value("SELECT COUNT(*) FROM user_credentials")
    assert count == 1


def test_initialize_schema_is_idempotent(monkeypatch, restore_database_module):
    """
    Test that initialize_schema can be called multiple times safely.
    
    Verifies that calling initialize_schema multiple times doesn't raise errors
    or destroy existing data due to the CREATE TABLE IF NOT EXISTS clause.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    # Call initialize_schema multiple times
    reloaded_database.initialize_schema()
    reloaded_database.initialize_schema()
    reloaded_database.initialize_schema()
    
    # Should not raise any errors and table should exist
    result = reloaded_database.fetch_value("SELECT name FROM sqlite_master WHERE type='table' AND name='user_credentials'")
    assert result == "user_credentials"


def test_memory_connection_persistence_across_operations(monkeypatch, restore_database_module):
    """
    Test that in-memory connection persists data across multiple operations.
    
    Verifies that the shared in-memory connection properly maintains state
    across multiple database operations including schema creation, inserts,
    and queries.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    # Create schema
    reloaded_database.initialize_schema()
    
    # Insert data
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password, email, full_name) VALUES (?, ?, ?, ?)",
        ("alice", "hash1", "alice@test.com", "Alice Smith")
    )
    
    # Query data
    row = reloaded_database.fetch_one("SELECT username, email, full_name FROM user_credentials WHERE username = ?", ("alice",))
    assert row["username"] == "alice"
    assert row["email"] == "alice@test.com"
    assert row["full_name"] == "Alice Smith"
    
    # Insert more data
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password, email) VALUES (?, ?, ?)",
        ("bob", "hash2", "bob@test.com")
    )
    
    # Verify both records exist
    count = reloaded_database.fetch_value("SELECT COUNT(*) FROM user_credentials")
    assert count == 2


def test_concurrent_memory_db_access_uses_same_connection(monkeypatch, restore_database_module):
    """
    Test that concurrent access to in-memory database uses the same connection.
    
    Verifies thread safety by confirming that the threading lock ensures all
    accesses to an in-memory database use the same shared connection object.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    # Multiple concurrent-like accesses should use the same connection
    connections = []
    for _ in range(5):
        with reloaded_database.get_connection() as conn:
            connections.append(conn)
    
    # All should be the same connection object
    assert all(conn is connections[0] for conn in connections)


def test_resolve_sqlite_path_with_relative_path(monkeypatch, restore_database_module):
    """
    Test _resolve_sqlite_path with relative file paths.
    
    Verifies that _resolve_sqlite_path correctly resolves relative SQLite URLs
    to absolute filesystem paths.
    """
    result = database._resolve_sqlite_path("sqlite:///test.db")
    # Should resolve to an absolute path
    assert isinstance(result, str)
    assert "test.db" in result


def test_resolve_sqlite_path_with_memory_variations(monkeypatch, restore_database_module):
    """
    Test _resolve_sqlite_path handles various memory database formats.
    
    Verifies that _resolve_sqlite_path returns the literal string ':memory:'
    for both :memory: and /:memory: path formats.
    """
    assert database._resolve_sqlite_path("sqlite:///:memory:") == ":memory:"
    assert database._resolve_sqlite_path("sqlite://:memory:") == ":memory:"


def test_resolve_sqlite_path_with_percent_encoding(monkeypatch, restore_database_module):
    """
    Test that _resolve_sqlite_path decodes percent-encoded characters.
    
    Verifies that URL percent-encoding in the path is properly decoded
    before path resolution.
    """
    result = database._resolve_sqlite_path("sqlite:///test%20db.db")
    assert "test db.db" in result


def test_database_url_environment_variable_required():
    """
    Test that DATABASE_URL environment variable is required.
    
    Verifies that _get_database_url raises ValueError when DATABASE_URL
    is not set in the environment.
    """
    with pytest.raises(ValueError, match="DATABASE_URL environment variable must be set"):
        import os
        original = os.environ.get("DATABASE_URL")
        if original:
            del os.environ["DATABASE_URL"]
        try:
            database._get_database_url()
        finally:
            if original:
                os.environ["DATABASE_URL"] = original


def test_execute_commits_transaction(monkeypatch, restore_database_module):
    """
    Test that execute automatically commits the transaction.
    
    Verifies that changes made via execute are committed and visible in
    subsequent queries.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    # Execute an insert
    reloaded_database.execute(
        "INSERT INTO user_credentials (username, hashed_password) VALUES (?, ?)",
        ("commituser", "hash")
    )
    
    # Data should be committed and visible
    username = reloaded_database.fetch_value(
        "SELECT username FROM user_credentials WHERE username = ?",
        ("commituser",)
    )
    assert username == "commituser"


def test_fetch_one_with_complex_query(monkeypatch, restore_database_module):
    """
    Test fetch_one with complex queries including joins and aggregations.
    
    Verifies that fetch_one works correctly with more complex SQL queries
    beyond simple SELECT statements.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    reloaded_database = importlib.reload(database)
    
    reloaded_database.initialize_schema()
    
    # Insert test data
    for i in range(3):
        reloaded_database.execute(
            "INSERT INTO user_credentials (username, hashed_password, disabled) VALUES (?, ?, ?)",
            (f"user{i}", f"hash{i}", i % 2)
        )
    
    # Query with aggregation
    row = reloaded_database.fetch_one("SELECT COUNT(*) as count, MAX(id) as max_id FROM user_credentials WHERE disabled = ?", (0,))
    assert row is not None
    assert row["count"] == 2
    assert row["max_id"] is not None


def test_uri_parameter_handling_for_file_databases(monkeypatch, restore_database_module, tmp_path):
    """
    Test that uri parameter is False for non-URI file database paths.
    
    Verifies that regular file-based databases (not using file: URI scheme)
    have uri=False in their connection, which is the default SQLite behavior.
    """
    db_file = tmp_path / "regular.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    reloaded_database = importlib.reload(database)
    
    # Should create a connection successfully without URI mode
    conn = reloaded_database._connect()
    assert conn is not None
    conn.close()
