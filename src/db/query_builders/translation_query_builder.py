from dataclasses import dataclass
from typing import Literal
from .base import QueryResult

MatchType = Literal["exact", "prefix", "contains"]
DirectionType = Literal["forward", "reverse"]


@dataclass
class TranslationQueryBuilder:
    source_lang: str
    word: str
    direction: DirectionType
    target_lang: str | None = None
    match: MatchType = "exact"
    limit: int = 10

    def build(self) -> QueryResult:
        word_normalized = self.word.lower()
        word_condition, word_param = self._build_word_condition(word_normalized)
        target_condition, params = self._build_params(word_param)
        sql = self._build_query(word_condition, target_condition)

        return QueryResult(sql=sql, params=params)

    def with_target(self, target_lang: str) -> "TranslationQueryBuilder":
        return TranslationQueryBuilder(
            source_lang=self.source_lang,
            word=self.word,
            direction=self.direction,
            target_lang=target_lang,
            match=self.match,
            limit=self.limit
        )

    def with_limit(self, limit: int) -> "TranslationQueryBuilder":
        """
        Create a new builder with a different limit.

        Args:
            limit: Maximum number of results

        Returns:
            New TranslationQueryBuilder instance
        """
        return TranslationQueryBuilder(
            source_lang=self.source_lang,
            word=self.word,
            direction=self.direction,
            target_lang=self.target_lang,
            match=self.match,
            limit=limit
        )

    def _build_word_condition(self, word_normalized: str) -> tuple[str, str]:
        """
        Build WHERE clause for word matching.
        Returns:
            Tuple of (SQL condition, parameter value)
        """
        if self.match == "exact":
            return "source.word_normalized = ?", word_normalized
        elif self.match == "prefix":
            return "source.word_normalized LIKE ?", f"{word_normalized}%"
        elif self.match == "contains":
            return "source.word_normalized LIKE ?", f"%{word_normalized}%"
        else:
            raise ValueError(
                f"Invalid match type: {self.match}. Must be 'exact', 'prefix', or 'contains'"
            )

    def _build_params(self, word_param: str) -> tuple[str, list]:
        """
        Build target language condition and complete parameter list.

        Args:
            word_param: Word parameter value from _build_word_condition

        Returns:
            Tuple of (target condition SQL, full parameter list)
        """
        if self.target_lang:
            condition = "AND target.language_code = ?"
            params = [self.source_lang, word_param, self.target_lang, self.limit]
        else:
            condition = ""
            params = [self.source_lang, word_param, self.limit]

        return condition, params

    def _build_query(self, word_condition: str, target_condition: str) -> str:
        """
        Build complete SQL query based on direction.

        Args:
            word_condition: Word WHERE clause
            target_condition: Target language WHERE clause

        Returns:
            Complete SQL query string
        """
        if self.direction == "forward":
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
