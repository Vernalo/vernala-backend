import sqlite3
from contextlib import contextmanager
from typing import Protocol, runtime_checkable


@runtime_checkable
class DatabaseConnection(Protocol):
    def cursor(self) -> sqlite3.Cursor: ...
    def commit(self) -> None: ...
    def close(self) -> None: ...
    row_factory: sqlite3.Row | None


class BaseRepository:

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or "vernala.db"
        self._connection: sqlite3.Connection | None = None

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _execute_query(self, query: str, params: tuple | list) -> list[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
