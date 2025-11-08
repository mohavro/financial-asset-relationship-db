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
    """Resolve a SQLite URL (sqlite:///path.db) to a filesystem path, handling query parameters and relative paths."""

    from urllib.parse import urlparse, unquote

    parsed = urlparse(url)
    if parsed.scheme != "sqlite":
        raise ValueError(f"Not a valid sqlite URI: {url}")

    # Handle in-memory database
    if parsed.path == "/:memory:" or parsed.path == ":memory:":
        return ":memory:"

    # Remove leading slash for relative paths (sqlite:///foo.db)
    # For absolute paths (sqlite:////abs/path.db), keep leading slash
    path = unquote(parsed.path)
    if path.startswith("/") and not path.startswith("//"):
        # This is an absolute path
        resolved_path = Path(path).resolve()
    elif path.startswith("//"):
        # Remove one leading slash for absolute path
        resolved_path = Path(path[1:]).resolve()
    else:
        # Relative path
        resolved_path = Path(path.lstrip("/")).resolve()

    return str(resolved_path)

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


def _connect() -> sqlite3.Connection:
    """Create a new SQLite connection with sensible defaults."""

    connection = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Context manager that yields a database connection and ensures cleanup."""

    connection = _connect()
    try:
        yield connection
    finally:
        connection.close()


def execute(query: str, parameters: tuple | list | None = None) -> None:
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
    return row[0] if isinstance(row, sqlite3.Row) else row


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
