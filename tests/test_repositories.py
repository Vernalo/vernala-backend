"""Unit tests for repository pattern implementation."""

import pytest
from db.repositories import TranslationRepository, LanguageRepository, StatsRepository


class TestTranslationRepository:
    """Tests for TranslationRepository."""

    def test_query_translations_forward_exact(self, translation_repo):
        """Test forward translation with exact match."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            direction="forward"
        )

        assert len(results) == 2
        assert all(r["source_word"] == "abandon" for r in results)
        assert all(r["source_language"] == "en" for r in results)
        assert all(r["target_language"] == "nnh" for r in results)
        # Check for both target words
        target_words = {r["target_word"] for r in results}
        assert "ńnyé2ńnyé" in target_words
        assert "ńkʉ́e" in target_words

    def test_query_translations_reverse_exact(self, translation_repo):
        """Test reverse translation with exact match."""
        results = translation_repo.query_translations(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            target_lang="en",
            match="exact",
            direction="reverse"
        )

        assert len(results) == 2
        assert all(r["source_word"] == "ńnyé2ńnyé" for r in results)
        assert all(r["source_language"] == "nnh" for r in results)
        assert all(r["target_language"] == "en" for r in results)
        # Check for both English words
        target_words = {r["target_word"] for r in results}
        assert "abandon" in target_words
        assert "leave" in target_words

    def test_query_translations_forward_all_targets(self, translation_repo):
        """Test forward translation to all target languages."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="hello",
            target_lang=None,  # All languages
            match="exact",
            direction="forward"
        )

        assert len(results) == 1
        assert results[0]["source_word"] == "hello"
        assert results[0]["target_word"] == "mbwámnò"
        assert results[0]["target_language"] == "nnh"

    def test_query_translations_reverse_all_targets(self, translation_repo):
        """Test reverse translation to all target languages."""
        results = translation_repo.query_translations(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            target_lang=None,  # All languages
            match="exact",
            direction="reverse"
        )

        # Should find English and French translations
        assert len(results) == 4
        languages = {r["target_language"] for r in results}
        assert "en" in languages
        assert "fr" in languages

    def test_query_translations_case_insensitive(self, translation_repo):
        """Test that queries are case-insensitive."""
        # Query with uppercase
        results = translation_repo.query_translations(
            source_lang="en",
            word="ABANDON",
            target_lang="nnh",
            match="exact",
            direction="forward"
        )

        assert len(results) == 2
        assert all(r["source_word"] == "abandon" for r in results)

    def test_query_translations_prefix_match(self, translation_repo):
        """Test prefix matching for autocomplete."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="aban",
            target_lang="nnh",
            match="prefix",
            direction="forward"
        )

        # Should find "abandon"
        assert len(results) >= 2
        assert all(r["source_word"].startswith("aban") for r in results)

    def test_query_translations_contains_match(self, translation_repo):
        """Test contains matching for fuzzy search."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="llo",
            target_lang="nnh",
            match="contains",
            direction="forward"
        )

        # Should find "hello"
        assert len(results) >= 1
        assert any(r["source_word"] == "hello" for r in results)

    def test_query_translations_limit(self, translation_repo):
        """Test result limiting."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            limit=1,
            direction="forward"
        )

        # Should respect limit
        assert len(results) == 1

    def test_query_translations_nonexistent_word(self, translation_repo):
        """Test query with nonexistent word returns empty list."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="nonexistent",
            target_lang="nnh",
            match="exact",
            direction="forward"
        )

        assert len(results) == 0

    def test_query_translations_invalid_match_type(self, translation_repo):
        """Test that invalid match type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid match type"):
            translation_repo.query_translations(
                source_lang="en",
                word="test",
                target_lang="nnh",
                match="invalid",  # type: ignore
                direction="forward"
            )

    def test_query_translations_webonary_link_forward(self, translation_repo):
        """Test that webonary links are included in forward lookup."""
        results = translation_repo.query_translations(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            direction="forward"
        )

        # African language words should have webonary links
        assert all(r["webonary_link"] is not None for r in results)
        assert all(r["webonary_link"].startswith("https://www.webonary.org/") for r in results)

    def test_query_translations_webonary_link_reverse(self, translation_repo):
        """Test that webonary links are included in reverse lookup."""
        results = translation_repo.query_translations(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            target_lang="en",
            match="exact",
            direction="reverse"
        )

        # Source is African language, should have webonary link
        assert all(r["webonary_link"] is not None for r in results)
        assert all("webonary" in r["webonary_link"] for r in results)


class TestLanguageRepository:
    """Tests for LanguageRepository."""

    def test_get_all_languages(self, language_repo):
        """Test getting all languages."""
        result = language_repo.get_all_languages()

        assert "languages" in result
        assert "count" in result
        assert result["count"] == 3

        codes = {lang["code"] for lang in result["languages"]}
        assert "en" in codes
        assert "fr" in codes
        assert "nnh" in codes

    def test_get_language_codes(self, language_repo):
        """Test getting language code set."""
        codes = language_repo.get_language_codes()

        assert isinstance(codes, set)
        assert "en" in codes
        assert "fr" in codes
        assert "nnh" in codes
        assert len(codes) == 3

    def test_language_metadata_english(self, language_repo):
        """Test English language metadata."""
        result = language_repo.get_all_languages()

        en_lang = next(l for l in result["languages"] if l["code"] == "en")
        assert en_lang["name"] == "English"
        assert en_lang["type"] == "source"
        assert en_lang["word_count"] == 3

    def test_language_metadata_french(self, language_repo):
        """Test French language metadata."""
        result = language_repo.get_all_languages()

        fr_lang = next(l for l in result["languages"] if l["code"] == "fr")
        assert fr_lang["name"] == "French"
        assert fr_lang["type"] == "source"
        assert fr_lang["word_count"] == 3

    def test_language_metadata_ngiemboon(self, language_repo):
        """Test Ngiemboon language metadata."""
        result = language_repo.get_all_languages()

        nnh_lang = next(l for l in result["languages"] if l["code"] == "nnh")
        assert nnh_lang["name"] == "Ngiemboon"
        assert nnh_lang["type"] == "target"
        assert nnh_lang["word_count"] == 3

    def test_language_word_counts(self, language_repo):
        """Test that word counts are accurate."""
        result = language_repo.get_all_languages()

        for lang in result["languages"]:
            assert lang["word_count"] > 0
            assert isinstance(lang["word_count"], int)


class TestStatsRepository:
    """Tests for StatsRepository."""

    def test_get_stats(self, stats_repo):
        """Test database statistics."""
        stats = stats_repo.get_stats()

        assert "total_words" in stats
        assert "total_translations" in stats
        assert "languages" in stats
        assert "db_size_bytes" in stats

        # Verify counts match test data
        assert stats["total_words"] == 9  # 3 English + 3 French + 3 Ngiemboon
        assert stats["total_translations"] == 7  # 7 translation pairs
        assert stats["languages"] == 3  # en, fr, nnh
        assert stats["db_size_bytes"] > 0

    def test_stats_types(self, stats_repo):
        """Test that statistics have correct types."""
        stats = stats_repo.get_stats()

        assert isinstance(stats["total_words"], int)
        assert isinstance(stats["total_translations"], int)
        assert isinstance(stats["languages"], int)
        assert isinstance(stats["db_size_bytes"], int)

    def test_stats_positive_values(self, stats_repo):
        """Test that statistics are positive."""
        stats = stats_repo.get_stats()

        assert stats["total_words"] > 0
        assert stats["total_translations"] > 0
        assert stats["languages"] > 0
        assert stats["db_size_bytes"] > 0


class TestBaseRepository:
    """Tests for BaseRepository base class."""

    def test_connection_context_manager(self, sample_db):
        """Test that connection context manager works correctly."""
        from db.repositories import BaseRepository

        repo = BaseRepository(sample_db)

        # Test connection context manager
        with repo.get_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM words")
            result = cursor.fetchone()
            assert result["count"] == 9

    def test_execute_query(self, sample_db):
        """Test _execute_query helper method."""
        from db.repositories import BaseRepository

        repo = BaseRepository(sample_db)

        # Test query execution
        rows = repo._execute_query(
            "SELECT * FROM words WHERE language_code = ?",
            ["en"]
        )

        assert len(rows) == 3
        assert all(row["language_code"] == "en" for row in rows)

    def test_db_path_configuration(self, sample_db):
        """Test that db_path is configurable."""
        from db.repositories import BaseRepository

        repo = BaseRepository(sample_db)
        assert repo.db_path == sample_db

        # Test default path
        default_repo = BaseRepository()
        assert default_repo.db_path == "vernala.db"
