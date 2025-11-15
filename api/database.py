"""Lightweight database helpers for the API layer."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse


def _get_database_url() -> str:
    """
    Read the DATABASE_URL environment variable and return its value.
    
    Returns:
        The value of the `DATABASE_URL` environment variable.
    
    Raises:
        ValueError: If the `DATABASE_URL` environment variable is not set.
    """

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable must be set before using the database")
    return database_url


def _resolve_sqlite_path(url: str) -> str:
    """
    Resolve a SQLite URL to either a filesystem path or the special in-memory indicator.
    
    Accepts SQLite URLs with schemes like `sqlite:///relative.db`, `sqlite:////absolute/path.db`
    and `sqlite:///:memory:`. Percent-encodings in the URL path are decoded before resolution.
    For in-memory URLs (`:memory:` or `/:memory:`) the literal string `":memory:"` is returned.
    
    Parameters:
        url (str): SQLite URL to resolve.
    
    Returns:
        str: Filesystem path for file-based URLs, or the literal string `":memory:"` for in-memory databases.
    """

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


DATABASE_URL = _get_database_url()
DATABASE_PATH = _resolve_sqlite_path(DATABASE_URL)


_memory_connection_lock = threading.Lock()
_MEMORY_CONNECTION: sqlite3.Connection | None = None


def _connect() -> sqlite3.Connection:
    """
    Open a configured SQLite connection for the module's database path.
    
    The returned connection has type detection enabled, allows use from multiple threads, and yields rows as sqlite3.Row.
    
    Returns:
        sqlite3.Connection: A connection to DATABASE_PATH with the module's preferred settings.
    """
    global _MEMORY_CONNECTION
    
    is_memory = DATABASE_PATH == ":memory:" or (DATABASE_PATH.startswith("file:") and ":memory:" in DATABASE_PATH)
    
    if is_memory:
        if _MEMORY_CONNECTION is None:
            _MEMORY_CONNECTION = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
            _MEMORY_CONNECTION.row_factory = sqlite3.Row
        return _MEMORY_CONNECTION

    connection = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Yield a SQLite connection for the configured database as a context manager.
    
    For file-backed databases the connection is closed when the context exits; for in-memory databases the shared connection is kept open.
    
    Returns:
        sqlite3.Connection: The connection object; closed on context exit for file-backed databases, kept open for in-memory databases.
    """
    is_memory = DATABASE_PATH == ":memory:" or (DATABASE_PATH.startswith("file:") and ":memory:" in DATABASE_PATH)
    
    connection = _connect()
    try:
        yield connection
    finally:
        if not is_memory:
            connection.close()


def execute(query: str, parameters: tuple | list | None = None) -> None:
    """
    Execute a SQL write statement and commit the transaction using the module's managed SQLite connection.
    
    Parameters:
        query (str): SQL statement to execute.
        parameters (tuple | list | None): Sequence of values to bind to the statement; use `None` or an empty sequence if there are no parameters.
    """

    with get_connection() as connection:
        connection.execute(query, parameters or ())
        connection.commit()


def fetch_one(query: str, parameters: tuple | list | None = None):
    """
    Retrieve the first row produced by an SQL query.
    
    Parameters:
        query (str): SQL statement to execute.
        parameters (tuple | list | None): Optional sequence of parameters to bind into the query.
    
    Returns:
        sqlite3.Row | None: The first row of the result set as a `sqlite3.Row`, or `None` if the query returned no rows.
    """

    with get_connection() as connection:
        cursor = connection.execute(query, parameters or ())
        return cursor.fetchone()


def fetch_value(query: str, parameters: tuple | list | None = None):
    """
    Fetches the first column value from the first row of a query result.
    
    Parameters:
        query (str): SQL query to execute; may include parameter placeholders.
        parameters (tuple | list | None): Sequence of parameters for the query placeholders.
    
    Returns:
        The first column value if a row is returned, `None` otherwise.
    """

    row = fetch_one(query, parameters)
    if row is None:
        return None
    return row[0] if isinstance(row, sqlite3.Row) else row


def initialize_schema() -> None:
    """
    Create the user_credentials table if it does not already exist.
    
    Creates a table named `user_credentials` with columns:
    - `id` INTEGER PRIMARY KEY AUTOINCREMENT
    - `username` TEXT UNIQUE NOT NULL
    - `email` TEXT
    - `full_name` TEXT
    - `hashed_password` TEXT NOT NULL
    - `disabled` INTEGER NOT NULL DEFAULT 0
    """

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