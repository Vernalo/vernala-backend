from .base import BaseRepository
from ..query_builders import LanguageQueryBuilder


class LanguageRepository(BaseRepository):
    """
    Data access layer for language information.

    Returns raw database data without business logic.
    """

    def __init__(self, db_path: str | None = None):
        super().__init__(db_path)
        self._query_builder = LanguageQueryBuilder()

    def get_all_languages_raw(self) -> list[dict]:
        """
        Get all languages with word counts from database.

        Returns:
            List of dictionaries with keys:
                - language_code: ISO 639-3 code
                - word_count: Number of words in database
        """
        query_result = self._query_builder.build_all_languages_query()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = query_result.execute(cursor)

            return [
                {
                    "language_code": row["language_code"],
                    "word_count": row["word_count"]
                }
                for row in rows
            ]
