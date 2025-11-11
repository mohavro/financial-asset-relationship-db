"""Lightweight database helpers for the API layer."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse


def _get_database_url() -> str:
    """Return the configured database URL, raising if it is missing."""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable must be set before using the database")
    return database_url


def _resolve_sqlite_path(url: str) -> str:
    """Resolve a SQLite URL (sqlite:///path.db) to a filesystem path."""

    parsed = urlparse(url)
    if parsed.scheme != "sqlite":
        raise ValueError("Only sqlite URLs are supported for DATABASE_URL")

    if parsed.path in {"", "/"} and parsed.netloc:
        path = f"/{parsed.netloc}"
    else:
        path = parsed.path

    # Handle in-memory databases.
    if path == "/:memory:":
        return ":memory:"

    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return str(resolved)


DATABASE_URL = _get_database_url()
DATABASE_PATH = _resolve_sqlite_path(DATABASE_URL)


_MEMORY_CONNECTION: sqlite3.Connection | None = None


def _connect() -> sqlite3.Connection:
    """
    Obtain a SQLite connection configured for the application's database.
    
    For an in-memory database (path ':memory:'), returns a single shared connection reused by callers.
    For a file-backed database, returns a new connection.
    
    Returns:
        sqlite3.Connection: Connection with detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False and row_factory=sqlite3.Row.
    """

    global _MEMORY_CONNECTION

    if DATABASE_PATH == ":memory:":
        if _MEMORY_CONNECTION is None:
            with _MEMORY_CONNECTION_LOCK:
                if _MEMORY_CONNECTION is None:
                    _MEMORY_CONNECTION = sqlite3.connect(
                        DATABASE_PATH,
                        detect_types=sqlite3.PARSE_DECLTYPES,
                        check_same_thread=False,
                    )
                    _MEMORY_CONNECTION.row_factory = sqlite3.Row
        return _MEMORY_CONNECTION

    connection = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Provide a context-managed SQLite connection for the configured database.
    
    Yields a `sqlite3.Connection` for use inside a with-statement. For file-backed databases the connection is closed when the context exits; for an in-memory database the shared connection is left open.
     
    Returns:
        sqlite3.Connection: The database connection to use within the context.
    """

    connection = _connect()
    try:
        yield connection
    finally:
        if DATABASE_PATH != ":memory:":
            connection.close()


def fetch_value(query: str, parameters: tuple | list | None = None):
    """
    Return the first column of the first row produced by the given SQL query.
    
    Parameters:
        query (str): SQL statement to execute.
        parameters (tuple | list | None): Parameters to bind to the SQL statement.
    
    Returns:
        The value of the first column of the first row, or None if the query returned no rows.
    """
    row = fetch_one(query, parameters)
    return row[0] if row is not None else None
    """Execute a write query within a managed connection."""

    with get_connection() as connection:
        connection.execute(query, parameters or ())
        connection.commit()


def fetch_one(query: str, parameters: tuple | list | None = None):
    """Return a single row for the given query."""

    with get_connection() as connection:
        cursor = connection.execute(query, parameters or ())
        return cursor.fetchone()


def fetch_value(query: str, parameters: tuple | list | None = None):
    """Return a single scalar value."""

    row = fetch_one(query, parameters)
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        return row[0]
    return row


def initialize_schema() -> None:
    """Ensure the credential table exists."""

    execute(
        """
        CREATE TABLE IF NOT EXISTS user_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            disabled INTEGER NOT NULL DEFAULT 0
        )
        """
    )