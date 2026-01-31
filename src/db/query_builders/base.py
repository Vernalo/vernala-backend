"""Base classes for query builders."""

from dataclasses import dataclass
from typing import Protocol, Sequence, Any

class Cursor(Protocol):
    def execute(
        self,
        sql: str,
        parameters: Sequence[Any] = (),
        /,
    ) -> "Cursor": ...

    def fetchall(self) -> list[Any]: ...


@dataclass
class QueryResult:
    sql: str
    params: list

    def execute(self, cursor: Cursor):
        cursor.execute(self.sql, self.params)
        return cursor.fetchall()


class QueryBuilder(Protocol):
    def build(self) -> QueryResult:
        ...
