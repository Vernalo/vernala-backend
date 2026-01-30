"""Repository for translation queries."""

from typing import Literal
from .base import BaseRepository

MatchType = Literal["exact", "prefix", "contains"]
DirectionType = Literal["forward", "reverse"]


class TranslationRepository(BaseRepository):
    """Repository for translation queries."""

    def query_translations(
        self,
        source_lang: str,
        word: str,
        target_lang: str | None = None,
        match: MatchType = "exact",
        limit: int = 10,
        direction: DirectionType = "forward"
    ) -> list[dict]:
        """
        Query translations in either direction.

        Consolidates query_translation and query_reverse_translation logic.

        Args:
            source_lang: Source language code
            word: Word to translate
            target_lang: Target language code (None for all languages)
            match: Match type (exact, prefix, contains)
            limit: Maximum results
            direction: Query direction (forward or reverse)

        Returns:
            List of translation dictionaries with keys:
                - source_word: The source word
                - source_language: Source language code
                - target_word: The translated word
                - target_language: Target language code
                - webonary_link: Link to webonary (if available)

        Raises:
            ValueError: If match type is invalid

        Examples:
            # Forward: English → Ngiemboon
            repo.query_translations("en", "abandon", "nnh", direction="forward")

            # Reverse: Ngiemboon → English
            repo.query_translations("nnh", "ńnyé2ńnyé", "en", direction="reverse")

            # Bidirectional: Ngiemboon → All languages
            repo.query_translations("nnh", "ńnyé2ńnyé", direction="reverse")
        """
        word_normalized = word.lower()

        # Build word condition based on match type
        word_condition, word_param = self._build_word_condition(word_normalized, match)

        # Build target language condition
        target_condition, params = self._build_target_condition(
            source_lang, word_param, target_lang, limit
        )

        # Build query based on direction
        query = self._build_query(direction, word_condition, target_condition)

        # Execute and convert to dicts
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return self._rows_to_dicts(rows)

    def _build_word_condition(self, word_normalized: str, match: MatchType) -> tuple[str, str]:
        """
        Build WHERE clause for word matching.

        Args:
            word_normalized: Lowercase word to match
            match: Match type (exact, prefix, contains)

        Returns:
            Tuple of (SQL condition, parameter value)

        Raises:
            ValueError: If match type is invalid
        """
        if match == "exact":
            return "source.word_normalized = ?", word_normalized
        elif match == "prefix":
            return "source.word_normalized LIKE ?", f"{word_normalized}%"
        elif match == "contains":
            return "source.word_normalized LIKE ?", f"%{word_normalized}%"
        else:
            raise ValueError(f"Invalid match type: {match}. Must be 'exact', 'prefix', or 'contains'")

    def _build_target_condition(
        self,
        source_lang: str,
        word_param: str,
        target_lang: str | None,
        limit: int
    ) -> tuple[str, list]:
        """
        Build target language condition and parameters.

        Args:
            source_lang: Source language code
            word_param: Word parameter value
            target_lang: Target language code (optional)
            limit: Result limit

        Returns:
            Tuple of (SQL condition, parameter list)
        """
        if target_lang:
            return "AND target.language_code = ?", [source_lang, word_param, target_lang, limit]
        else:
            return "", [source_lang, word_param, limit]

    def _build_query(self, direction: DirectionType, word_condition: str, target_condition: str) -> str:
        """
        Build SQL query based on direction.

        Args:
            direction: Query direction (forward or reverse)
            word_condition: Word WHERE clause
            target_condition: Target language WHERE clause

        Returns:
            SQL query string
        """
        if direction == "forward":
            # Forward lookup: English/French → African languages
            return f"""
                SELECT
                    source.word as source_word,
                    source.language_code as source_language,
                    target.word as target_word,
                    target.language_code as target_language,
                    target.webonary_link as webonary_link
                FROM words source
                JOIN translations t ON source.id = t.source_word_id
                JOIN words target ON t.target_word_id = target.id
                WHERE source.language_code = ?
                  AND {word_condition}
                  {target_condition}
                ORDER BY target.word
                LIMIT ?
            """
        else:  # reverse
            # Reverse lookup: African languages → English/French
            return f"""
                SELECT
                    source.word as source_word,
                    source.language_code as source_language,
                    target.word as target_word,
                    target.language_code as target_language,
                    source.webonary_link as webonary_link
                FROM words source
                JOIN translations t ON source.id = t.target_word_id
                JOIN words target ON t.source_word_id = target.id
                WHERE source.language_code = ?
                  AND {word_condition}
                  {target_condition}
                ORDER BY target.word
                LIMIT ?
            """

    def _rows_to_dicts(self, rows: list) -> list[dict]:
        """
        Convert database rows to dictionaries.

        Args:
            rows: List of sqlite3.Row objects

        Returns:
            List of dictionaries with translation data
        """
        return [
            {
                "source_word": row["source_word"],
                "source_language": row["source_language"],
                "target_word": row["target_word"],
                "target_language": row["target_language"],
                "webonary_link": row["webonary_link"]
            }
            for row in rows
        ]
