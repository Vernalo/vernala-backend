import sqlite3
from contextlib import contextmanager
from typing import Protocol, runtime_checkable


@runtime_checkable
class DatabaseConnection(Protocol):
    """Protocol defining database connection interface."""

    def cursor(self) -> sqlite3.Cursor: ...
    def commit(self) -> None: ...
    def close(self) -> None: ...
    row_factory: sqlite3.Row | None


class BaseRepository:
    """Base repository with shared connection management."""

    def __init__(self, db_path: str | None = None):
        """
        Initialize repository.

        Args:
            db_path: Path to SQLite database file (defaults to vernala.db)
        """
        self.db_path = db_path or "vernala.db"
        self._connection: sqlite3.Connection | None = None

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection configured with Row factory

        Example:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM words")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _execute_query(self, query: str, params: tuple | list) -> list[sqlite3.Row]:
        """
        Execute query and return rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of sqlite3.Row objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
