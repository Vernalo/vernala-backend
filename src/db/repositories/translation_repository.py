"""Repository for translation queries."""

from .base import BaseRepository
from db.query_builders import TranslationQueryBuilder, MatchType, DirectionType


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
        # Build query using query builder
        builder = TranslationQueryBuilder(
            source_lang=source_lang,
            word=word,
            direction=direction,
            target_lang=target_lang,
            match=match,
            limit=limit
        )

        query_result = builder.build()

        # Execute and convert to dicts
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = query_result.execute(cursor)

            return self._rows_to_dicts(rows)

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
