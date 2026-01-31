from dataclasses import dataclass
from .base import QueryResult


@dataclass
class LanguageQueryBuilder:
    def build_all_languages_query(self) -> QueryResult:
        sql = """
            SELECT language_code, COUNT(*) as word_count
            FROM words
            GROUP BY language_code
            ORDER BY language_code
        """
        return QueryResult(sql=sql, params=[])

    def build_language_exists_query(self, lang_code: str) -> QueryResult:
        sql = """
            SELECT COUNT(*) as count
            FROM words
            WHERE language_code = ?
        """
        return QueryResult(sql=sql, params=[lang_code])
