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
    Resolve a SQLite URL to a filesystem path or the special in-memory indicator.
    
    Supports common SQLite URL forms such as `sqlite:///relative.db`, `sqlite:////absolute/path.db`
    and `sqlite:///:memory:`. Percent-encodings in the path are decoded before resolution.
    
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

    parsed = urlparse(url)
    if parsed.scheme != "sqlite":
        raise ValueError("Only sqlite URLs are supported for DATABASE_URL")

    if parsed.path in {"", "/"} and parsed.netloc:
        path = f"/{parsed.netloc}"
    else:
        path = parsed.path

# Handle three-slash relative paths (sqlite:///path.db)
if parsed.netloc == "" and path.startswith("/") and path != "/:memory:":
    relative_path = path[1:]  # Remove leading slash
    resolved = Path(relative_path)
else:
    resolved = Path(path).expanduser().resolve()
resolved.parent.mkdir(parents=True, exist_ok=True)
return str(resolved)
    return str(resolved)


DATABASE_URL = _get_database_url()
DATABASE_PATH = _resolve_sqlite_path(DATABASE_URL)


_MEMORY_CONNECTION: sqlite3.Connection | None = None


def _connect() -> sqlite3.Connection:
    """
    Open a configured SQLite connection for the module's database path.
    
    The returned connection has type detection enabled, allows use from multiple threads, and yields rows as sqlite3.Row.
    
    Returns:
        sqlite3.Connection: A connection to DATABASE_PATH with the module's preferred settings.
    """

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
        # Close connection only if not using any in-memory database (including URI-based)
        if not (
            DATABASE_PATH == ":memory:" or
            (DATABASE_PATH.startswith("file:") and ":memory:" in DATABASE_PATH)
        ):
            connection.close()


from typing import Any

def fetch_value(query: str, parameters: tuple | list | None = None) -> Any | None:
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
def execute(query: str, parameters: tuple | list | None = None) -> None:
    """
    Execute and commit a write SQL query using a managed SQLite connection.
    
    Parameters:
        query (str): SQL statement to execute.
        parameters (tuple | list | None): Sequence of values to bind to the query; pass None or an empty sequence if there are no parameters.
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