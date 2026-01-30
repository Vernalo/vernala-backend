"""Unit tests for database query layer."""

import pytest
from db import database


class TestGetConnection:
    """Tests for get_connection function."""

    def test_connection_returns_valid_connection(self, sample_db):
        """Test that get_connection returns a valid SQLite connection."""
        conn = database.get_connection(sample_db)
        assert conn is not None

        # Verify we can query the database
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM words")
        result = cursor.fetchone()
        assert result["count"] > 0

        conn.close()

    def test_connection_has_row_factory(self, sample_db):
        """Test that connection has row_factory set for dict-like access."""
        conn = database.get_connection(sample_db)
        cursor = conn.cursor()

        cursor.execute("SELECT word, language_code FROM words LIMIT 1")
        row = cursor.fetchone()

        # Should be able to access columns by name
        assert "word" in row.keys()
        assert "language_code" in row.keys()

        conn.close()


class TestQueryTranslation:
    """Tests for query_translation function (forward lookups)."""

    def test_english_to_ngiemboon_exact_match(self, sample_db):
        """Test English → Ngiemboon exact match."""
        results = database.query_translation(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 2  # abandon -> ńnyé2ńnyé and ńkʉ́e
        assert all(r["source_language"] == "en" for r in results)
        assert all(r["target_language"] == "nnh" for r in results)
        assert all(r["source_word"] == "abandon" for r in results)

        # Check translations
        target_words = {r["target_word"] for r in results}
        assert "ńnyé2ńnyé" in target_words
        assert "ńkʉ́e" in target_words

    def test_french_to_ngiemboon_exact_match(self, sample_db):
        """Test French → Ngiemboon exact match."""
        results = database.query_translation(
            source_lang="fr",
            word="abandonner",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 1
        assert results[0]["source_word"] == "abandonner"
        assert results[0]["source_language"] == "fr"
        assert results[0]["target_word"] == "ńnyé2ńnyé"
        assert results[0]["target_language"] == "nnh"
        assert results[0]["webonary_link"] is not None

    def test_case_insensitive_search(self, sample_db):
        """Test that searches are case-insensitive."""
        results_lower = database.query_translation(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        results_upper = database.query_translation(
            source_lang="en",
            word="ABANDON",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        results_mixed = database.query_translation(
            source_lang="en",
            word="AbAnDoN",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        # All should return the same results
        assert len(results_lower) == len(results_upper) == len(results_mixed)
        assert len(results_lower) > 0

    def test_no_results_for_nonexistent_word(self, sample_db):
        """Test that nonexistent words return empty results."""
        results = database.query_translation(
            source_lang="en",
            word="nonexistentword",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 0
        assert results == []

    def test_webonary_link_included(self, sample_db):
        """Test that webonary links are included for African language targets."""
        results = database.query_translation(
            source_lang="en",
            word="hello",
            target_lang="nnh",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 1
        assert results[0]["webonary_link"] is not None
        assert "webonary.org" in results[0]["webonary_link"]


class TestQueryReverseTranslation:
    """Tests for query_reverse_translation (reverse lookups)."""

    def test_ngiemboon_to_english(self, sample_db):
        """Test Ngiemboon → English reverse lookup."""
        results = database.query_reverse_translation(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            target_lang="en",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 2  # abandon and leave
        assert all(r["source_language"] == "nnh" for r in results)
        assert all(r["target_language"] == "en" for r in results)
        assert all(r["source_word"] == "ńnyé2ńnyé" for r in results)

        target_words = {r["target_word"] for r in results}
        assert "abandon" in target_words
        assert "leave" in target_words

    def test_ngiemboon_to_french(self, sample_db):
        """Test Ngiemboon → French reverse lookup."""
        results = database.query_reverse_translation(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            target_lang="fr",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 2  # abandonner and laisser
        assert all(r["source_language"] == "nnh" for r in results)
        assert all(r["target_language"] == "fr" for r in results)

        target_words = {r["target_word"] for r in results}
        assert "abandonner" in target_words
        assert "laisser" in target_words

    def test_ngiemboon_to_all_languages(self, sample_db):
        """Test Ngiemboon → All languages (bidirectional)."""
        results = database.query_reverse_translation(
            source_lang="nnh",
            word="ńnyé2ńnyé",
            target_lang=None,  # No target = all languages
            match="exact",
            db_path=sample_db
        )

        # Should return both English and French translations
        assert len(results) == 4  # abandon, leave, abandonner, laisser

        # Check we have both languages
        target_languages = {r["target_language"] for r in results}
        assert "en" in target_languages
        assert "fr" in target_languages

    def test_reverse_lookup_includes_webonary_link(self, sample_db):
        """Test that reverse lookups include webonary link from source."""
        results = database.query_reverse_translation(
            source_lang="nnh",
            word="mbwámnò",
            target_lang="en",
            match="exact",
            db_path=sample_db
        )

        assert len(results) == 1
        assert results[0]["webonary_link"] is not None
        assert "webonary.org" in results[0]["webonary_link"]


class TestMatchTypes:
    """Tests for different match types (exact, prefix, contains)."""

    def test_prefix_match(self, sample_db):
        """Test prefix matching."""
        # Add more test data for prefix testing
        conn = database.get_connection(sample_db)
        cursor = conn.cursor()

        # Add words starting with 'aban'
        cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                      ("abandoned", "abandoned", "en"))
        abandoned_id = cursor.lastrowid

        cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                      ("abandonment", "abandonment", "en"))
        abandonment_id = cursor.lastrowid

        # Link to a Ngiemboon word
        cursor.execute("SELECT id FROM words WHERE word = ? AND language_code = ?",
                      ("ńkʉ́e", "nnh"))
        nnh_id = cursor.fetchone()["id"]

        cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                      (abandoned_id, nnh_id))
        cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                      (abandonment_id, nnh_id))

        conn.commit()
        conn.close()

        # Test prefix search
        results = database.query_translation(
            source_lang="en",
            word="aban",
            target_lang="nnh",
            match="prefix",
            db_path=sample_db
        )

        assert len(results) >= 3  # abandon, abandoned, abandonment
        assert all(r["source_word"].startswith("aban") for r in results)

    def test_invalid_match_type_raises_error(self, sample_db):
        """Test that invalid match type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid match type"):
            database.query_translation(
                source_lang="en",
                word="test",
                target_lang="nnh",
                match="invalid",  # type: ignore
                db_path=sample_db
            )


class TestGetSupportedLanguages:
    """Tests for get_supported_languages function."""

    def test_returns_all_languages(self, sample_db):
        """Test that all languages in database are returned."""
        result = database.get_supported_languages(db_path=sample_db)

        assert "languages" in result
        assert "count" in result
        assert result["count"] == 3  # en, fr, nnh

        # Extract language codes
        codes = {lang["code"] for lang in result["languages"]}
        assert "en" in codes
        assert "fr" in codes
        assert "nnh" in codes

    def test_language_metadata(self, sample_db):
        """Test that language metadata is correct."""
        result = database.get_supported_languages(db_path=sample_db)

        # Find English
        en_lang = next(l for l in result["languages"] if l["code"] == "en")
        assert en_lang["name"] == "English"
        assert en_lang["type"] == "source"
        assert en_lang["word_count"] > 0

        # Find Ngiemboon
        nnh_lang = next(l for l in result["languages"] if l["code"] == "nnh")
        assert nnh_lang["name"] == "Ngiemboon"
        assert nnh_lang["type"] == "target"
        assert nnh_lang["word_count"] > 0


class TestGetDatabaseStats:
    """Tests for get_database_stats function."""

    def test_returns_correct_stats(self, sample_db):
        """Test that database statistics are correct."""
        stats = database.get_database_stats(db_path=sample_db)

        assert "total_words" in stats
        assert "total_translations" in stats
        assert "languages" in stats
        assert "db_size_bytes" in stats

        assert stats["total_words"] == 9  # 3 en + 3 fr + 3 nnh
        assert stats["total_translations"] == 7  # Number of translation pairs
        assert stats["languages"] == 3  # en, fr, nnh
        assert stats["db_size_bytes"] > 0


class TestLimitParameter:
    """Tests for limit parameter."""

    def test_limit_restricts_results(self, sample_db):
        """Test that limit parameter restricts number of results."""
        # Query with limit 1
        results = database.query_translation(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            limit=1,
            db_path=sample_db
        )

        assert len(results) == 1

    def test_limit_larger_than_results(self, sample_db):
        """Test that limit larger than results returns all results."""
        results = database.query_translation(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="exact",
            limit=100,
            db_path=sample_db
        )

        assert len(results) == 2  # Only 2 results available


# All tests now use sample_db fixture from conftest
# Real database integration tests removed to keep CI simple
