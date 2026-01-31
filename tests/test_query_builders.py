"""Unit tests for query builders (no database required)."""

import pytest
from db.query_builders import (
    TranslationQueryBuilder,
    LanguageQueryBuilder,
    QueryResult
)


class TestTranslationQueryBuilder:
    """Unit tests for TranslationQueryBuilder (no database needed)."""

    def test_build_forward_exact_with_target(self):
        """Test building forward translation query with exact match and target."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="abandon",
            direction="forward",
            target_lang="nnh",
            match="exact",
            limit=10
        )

        result = builder.build()

        assert isinstance(result, QueryResult)
        assert "SELECT" in result.sql
        assert "FROM words source" in result.sql
        assert "JOIN translations t ON source.id = t.source_word_id" in result.sql
        assert "source.word_normalized = ?" in result.sql
        assert "AND target.language_code = ?" in result.sql
        assert "ORDER BY target.word" in result.sql
        assert "LIMIT ?" in result.sql

        # Check parameters
        assert result.params == ["en", "abandon", "nnh", 10]

    def test_build_forward_exact_without_target(self):
        """Test building forward query without target (all languages)."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="abandon",
            direction="forward",
            match="exact"
        )

        result = builder.build()

        # Should not have target language condition
        assert "AND target.language_code = ?" not in result.sql
        assert result.params == ["en", "abandon", 10]

    def test_build_reverse_query(self):
        """Test building reverse translation query."""
        builder = TranslationQueryBuilder(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            direction="reverse",
            target_lang="en",
            match="exact"
        )

        result = builder.build()

        # Reverse queries join on target_word_id
        assert "JOIN translations t ON source.id = t.target_word_id" in result.sql
        assert "JOIN words target ON t.source_word_id = target.id" in result.sql
        # Webonary link should come from source (African language)
        assert "source.webonary_link" in result.sql

    def test_build_prefix_match(self):
        """Test prefix match query."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="aban",
            direction="forward",
            match="prefix"
        )

        result = builder.build()

        assert "source.word_normalized LIKE ?" in result.sql
        assert result.params[1] == "aban%"

    def test_build_contains_match(self):
        """Test contains match query."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="llo",
            direction="forward",
            match="contains"
        )

        result = builder.build()

        assert "source.word_normalized LIKE ?" in result.sql
        assert result.params[1] == "%llo%"

    def test_invalid_match_type_raises_error(self):
        """Test that invalid match type raises ValueError."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="test",
            direction="forward",
            match="invalid"  # type: ignore
        )

        with pytest.raises(ValueError, match="Invalid match type"):
            builder.build()

    def test_with_target_immutability(self):
        """Test that with_target creates a new builder instance."""
        builder1 = TranslationQueryBuilder(
            source_lang="en",
            word="test",
            direction="forward"
        )

        builder2 = builder1.with_target("nnh")

        assert builder1.target_lang is None
        assert builder2.target_lang == "nnh"
        assert builder1 is not builder2

    def test_with_limit_immutability(self):
        """Test that with_limit creates a new builder instance."""
        builder1 = TranslationQueryBuilder(
            source_lang="en",
            word="test",
            direction="forward",
            limit=10
        )

        builder2 = builder1.with_limit(20)

        assert builder1.limit == 10
        assert builder2.limit == 20
        assert builder1 is not builder2

    def test_case_insensitive_word_matching(self):
        """Test that word is normalized to lowercase."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="ABANDON",
            direction="forward",
            match="exact"
        )

        result = builder.build()

        # Word parameter should be lowercase
        assert result.params[1] == "abandon"

    def test_forward_query_structure(self):
        """Test that forward queries have correct JOIN structure."""
        builder = TranslationQueryBuilder(
            source_lang="en",
            word="test",
            direction="forward"
        )

        result = builder.build()

        # Forward: source is source_word_id, target is target_word_id
        assert "source.id = t.source_word_id" in result.sql
        assert "t.target_word_id = target.id" in result.sql
        # Webonary link from target (African language)
        assert "target.webonary_link" in result.sql

    def test_reverse_query_structure(self):
        """Test that reverse queries have correct JOIN structure."""
        builder = TranslationQueryBuilder(
            source_lang="nnh",
            word="test",
            direction="reverse"
        )

        result = builder.build()

        # Reverse: source is target_word_id, target is source_word_id
        assert "source.id = t.target_word_id" in result.sql
        assert "t.source_word_id = target.id" in result.sql
        # Webonary link from source (African language)
        assert "source.webonary_link" in result.sql

    def test_limit_parameter_position(self):
        """Test that limit is always the last parameter."""
        builder_with_target = TranslationQueryBuilder(
            source_lang="en",
            word="test",
            direction="forward",
            target_lang="nnh",
            limit=5
        )
        result_with = builder_with_target.build()
        assert result_with.params[-1] == 5

        builder_without_target = TranslationQueryBuilder(
            source_lang="en",
            word="test",
            direction="forward",
            limit=15
        )
        result_without = builder_without_target.build()
        assert result_without.params[-1] == 15


class TestLanguageQueryBuilder:
    """Unit tests for LanguageQueryBuilder."""

    def test_build_all_languages_query(self):
        """Test building query for all languages."""
        builder = LanguageQueryBuilder()

        result = builder.build_all_languages_query()

        assert isinstance(result, QueryResult)
        assert "SELECT language_code, COUNT(*) as word_count" in result.sql
        assert "FROM words" in result.sql
        assert "GROUP BY language_code" in result.sql
        assert "ORDER BY language_code" in result.sql
        assert result.params == []

    def test_build_language_exists_query(self):
        """Test building query to check language existence."""
        builder = LanguageQueryBuilder()

        result = builder.build_language_exists_query("en")

        assert "SELECT COUNT(*) as count" in result.sql
        assert "FROM words" in result.sql
        assert "WHERE language_code = ?" in result.sql
        assert result.params == ["en"]

    def test_language_exists_query_different_codes(self):
        """Test language exists query with different language codes."""
        builder = LanguageQueryBuilder()

        result_en = builder.build_language_exists_query("en")
        result_fr = builder.build_language_exists_query("fr")
        result_nnh = builder.build_language_exists_query("nnh")

        assert result_en.params == ["en"]
        assert result_fr.params == ["fr"]
        assert result_nnh.params == ["nnh"]


class TestQueryResult:
    """Test QueryResult execution helper."""

    def test_execute_calls_cursor_correctly(self):
        """Test that QueryResult.execute properly calls cursor methods."""
        # Mock cursor
        class MockCursor:
            def __init__(self):
                self.executed_sql = None
                self.executed_params = None
                self.fetch_called = False

            def execute(self, sql, params):
                self.executed_sql = sql
                self.executed_params = params

            def fetchall(self):
                self.fetch_called = True
                return [{"test": "data"}]

        result = QueryResult(
            sql="SELECT * FROM words WHERE id = ?",
            params=[1]
        )

        cursor = MockCursor()
        rows = result.execute(cursor)

        assert cursor.executed_sql == "SELECT * FROM words WHERE id = ?"
        assert cursor.executed_params == [1]
        assert cursor.fetch_called
        assert rows == [{"test": "data"}]

    def test_execute_with_empty_params(self):
        """Test execute with no parameters."""
        class MockCursor:
            def __init__(self):
                self.executed_params = None

            def execute(self, sql, params):
                self.executed_params = params

            def fetchall(self):
                return []

        result = QueryResult(
            sql="SELECT * FROM words",
            params=[]
        )

        cursor = MockCursor()
        result.execute(cursor)

        assert cursor.executed_params == []

    def test_execute_with_multiple_params(self):
        """Test execute with multiple parameters."""
        class MockCursor:
            def __init__(self):
                self.executed_params = None

            def execute(self, sql, params):
                self.executed_params = params

            def fetchall(self):
                return []

        result = QueryResult(
            sql="SELECT * FROM words WHERE lang = ? AND word LIKE ? LIMIT ?",
            params=["en", "test%", 10]
        )

        cursor = MockCursor()
        result.execute(cursor)

        assert cursor.executed_params == ["en", "test%", 10]
