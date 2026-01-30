"""Pytest configuration and fixtures for Vernala tests."""

import pytest
import sqlite3
import tempfile
from pathlib import Path


@pytest.fixture
def test_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    yield db_path

    # Cleanup after test
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_db(test_db_path):
    """
    Create a sample database with test data.

    Schema:
    - words: Contains sample English, French, and Ngiemboon words
    - translations: Contains sample translation pairs
    """
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create schema
    cursor.execute("""
        CREATE TABLE words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            word_normalized TEXT NOT NULL,
            language_code TEXT NOT NULL,
            webonary_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(word, language_code, webonary_link)
        )
    """)

    cursor.execute("""
        CREATE TABLE translations (
            source_word_id INTEGER NOT NULL,
            target_word_id INTEGER NOT NULL,
            PRIMARY KEY (source_word_id, target_word_id),
            FOREIGN KEY (source_word_id) REFERENCES words(id) ON DELETE CASCADE,
            FOREIGN KEY (target_word_id) REFERENCES words(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_words_normalized ON words(word_normalized, language_code)")
    cursor.execute("CREATE INDEX idx_words_language ON words(language_code)")
    cursor.execute("CREATE INDEX idx_translations_source ON translations(source_word_id)")
    cursor.execute("CREATE INDEX idx_translations_target ON translations(target_word_id)")

    # Insert sample words
    # English words
    cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                   ("abandon", "abandon", "en"))
    en_abandon_id = cursor.lastrowid

    cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                   ("leave", "leave", "en"))
    en_leave_id = cursor.lastrowid

    cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                   ("hello", "hello", "en"))
    en_hello_id = cursor.lastrowid

    # French words
    cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                   ("abandonner", "abandonner", "fr"))
    fr_abandonner_id = cursor.lastrowid

    cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                   ("laisser", "laisser", "fr"))
    fr_laisser_id = cursor.lastrowid

    cursor.execute("INSERT INTO words (word, word_normalized, language_code) VALUES (?, ?, ?)",
                   ("bonjour", "bonjour", "fr"))
    fr_bonjour_id = cursor.lastrowid

    # Ngiemboon words (with webonary links)
    cursor.execute("INSERT INTO words (word, word_normalized, language_code, webonary_link) VALUES (?, ?, ?, ?)",
                   ("ńnyé2ńnyé", "ńnyé2ńnyé", "nnh", "https://www.webonary.org/ngiemboon/test1"))
    nnh_nye_id = cursor.lastrowid

    cursor.execute("INSERT INTO words (word, word_normalized, language_code, webonary_link) VALUES (?, ?, ?, ?)",
                   ("ńkʉ́e", "ńkʉ́e", "nnh", "https://www.webonary.org/ngiemboon/test2"))
    nnh_kue_id = cursor.lastrowid

    cursor.execute("INSERT INTO words (word, word_normalized, language_code, webonary_link) VALUES (?, ?, ?, ?)",
                   ("mbwámnò", "mbwámnò", "nnh", "https://www.webonary.org/ngiemboon/test3"))
    nnh_mbwamno_id = cursor.lastrowid

    # Create translation pairs
    # abandon (en) -> ńnyé2ńnyé (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (en_abandon_id, nnh_nye_id))

    # leave (en) -> ńnyé2ńnyé (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (en_leave_id, nnh_nye_id))

    # abandon (en) -> ńkʉ́e (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (en_abandon_id, nnh_kue_id))

    # abandonner (fr) -> ńnyé2ńnyé (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (fr_abandonner_id, nnh_nye_id))

    # laisser (fr) -> ńnyé2ńnyé (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (fr_laisser_id, nnh_nye_id))

    # hello (en) -> mbwámnò (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (en_hello_id, nnh_mbwamno_id))

    # bonjour (fr) -> mbwámnò (nnh)
    cursor.execute("INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                   (fr_bonjour_id, nnh_mbwamno_id))

    conn.commit()
    conn.close()

    return test_db_path


# real_db_path fixture removed - all tests now use sample_db


@pytest.fixture
def translation_repo(sample_db):
    """Fixture for TranslationRepository with test database."""
    from db.repositories import TranslationRepository
    return TranslationRepository(sample_db)


@pytest.fixture
def language_repo(sample_db):
    """Fixture for LanguageRepository with test database."""
    from db.repositories import LanguageRepository
    return LanguageRepository(sample_db)


@pytest.fixture
def stats_repo(sample_db):
    """Fixture for StatsRepository with test database."""
    from db.repositories import StatsRepository
    return StatsRepository(sample_db)
