"""Test for shared in-memory SQLite connections."""

import os
import tempfile
import pytest
from unittest.mock import patch


@pytest.fixture
def memory_database():
    """Set up in-memory database for testing."""
    with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'}):
        # Need to reimport to pick up the environment change
        import api.database
        # Force reload of the module
        import importlib
        importlib.reload(api.database)
        yield api.database


def test_shared_memory_connection_first_call(memory_database):
    """Test that first connection call creates a connection."""
    from api.database import _connect

    # Get the module to check its state
    import api.database

    # Ensure memory connection starts as None
    assert api.database._MEMORY_CONNECTION is None

    # First call should create and store the connection
    conn1 = _connect()

    # Connection should be stored in module variable
    assert api.database._MEMORY_CONNECTION is conn1
    assert conn1 is not None

    # Close the connection for cleanup
    conn1.close()


def test_shared_memory_connection_second_call(memory_database):
    """Test that second connection call returns the same connection."""
    from api.database import _connect

    # Get the module to check its state
    import api.database

    # Create first connection
    conn1 = _connect()
    first_connection = api.database._MEMORY_CONNECTION

    # Create second connection
    conn2 = _connect()
    second_connection = api.database._MEMORY_CONNECTION

    # Both connections and the stored connection should be the same
    assert conn1 is conn2
    assert second_connection is first_connection
    assert second_connection is conn1

    # Cleanup
    conn1.close()


def test_memory_connection_settings(memory_database):
    """Test that memory connections have correct settings."""
    from api.database import _connect, DATABASE_PATH
    import sqlite3

    conn = _connect()

    # Check row_factory is set correctly
    assert conn.row_factory == sqlite3.Row

    # Check that it's actually an in-memory database
    assert DATABASE_PATH == ":memory:"

    # Test that we can execute queries
    conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO test VALUES (1, 'test')")
    conn.commit()

    cursor = conn.execute("SELECT * FROM test")
    row = cursor.fetchone()
    assert row['id'] == 1
    assert row['name'] == 'test'

    conn.close()


def test_file_based_connection_creates_new(memory_database):
    """Test that file-based connections still create new connections."""
    import tempfile
    from api.database import _connect, DATABASE_PATH

    # Temporarily change to file-based for this test
    import api.database
    
    # Use tempfile to create a proper temporary file path
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        temp_path = tmp.name
    
    original_path = api.database.DATABASE_PATH
    api.database.DATABASE_PATH = temp_path
    api.database._MEMORY_CONNECTION = None  # Reset the memory connection

    try:
        # Create two file-based connections
        conn1 = _connect()
        conn2 = _connect()

        # They should be different objects
        assert conn1 is not conn2

        # Both should have correct settings
        import sqlite3
        assert conn1.row_factory == sqlite3.Row
        assert conn2.row_factory == sqlite3.Row

        conn1.close()
        conn2.close()
    finally:
        # Restore original state
        api.database.DATABASE_PATH = original_path
        # Clean up temp file
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)