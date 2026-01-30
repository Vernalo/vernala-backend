"""
Database query layer for Vernala translation API.

DEPRECATED: This module provides backward-compatible functions.
New code should use repositories from db.repositories instead.

Provides functions to query translations between languages using SQLite.
"""

import sqlite3
from typing import Literal
from db.repositories import TranslationRepository, LanguageRepository, StatsRepository

# Database path (configurable)
DEFAULT_DB_PATH = "vernala.db"

MatchType = Literal["exact", "prefix", "contains"]

# Singleton repository instances for backward compatibility
_translation_repo: TranslationRepository | None = None
_language_repo: LanguageRepository | None = None
_stats_repo: StatsRepository | None = None


def _get_translation_repo(db_path: str | None = None) -> TranslationRepository:
    """Get or create translation repository singleton."""
    global _translation_repo
    actual_path = db_path or DEFAULT_DB_PATH
    if _translation_repo is None or _translation_repo.db_path != actual_path:
        _translation_repo = TranslationRepository(actual_path)
    return _translation_repo


def _get_language_repo(db_path: str | None = None) -> LanguageRepository:
    """Get or create language repository singleton."""
    global _language_repo
    actual_path = db_path or DEFAULT_DB_PATH
    if _language_repo is None or _language_repo.db_path != actual_path:
        _language_repo = LanguageRepository(actual_path)
    return _language_repo


def _get_stats_repo(db_path: str | None = None) -> StatsRepository:
    """Get or create stats repository singleton."""
    global _stats_repo
    actual_path = db_path or DEFAULT_DB_PATH
    if _stats_repo is None or _stats_repo.db_path != actual_path:
        _stats_repo = StatsRepository(actual_path)
    return _stats_repo


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.

    Args:
        db_path: Path to the SQLite database file (uses DEFAULT_DB_PATH if None)

    Returns:
        sqlite3.Connection configured for dictionary access
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def query_translation(
    source_lang: str,
    word: str,
    target_lang: str | None = None,
    match: MatchType = "exact",
    limit: int = 10,
    db_path: str | None = None
) -> list[dict]:
    """
    Query translations for a word from source language to target language(s).

    DEPRECATED: Use TranslationRepository.query_translations() with direction='forward'.

    Args:
        source_lang: Source language code (e.g., 'en', 'fr', 'nnh')
        word: Word to translate
        target_lang: Target language code (optional, omit for all languages)
        match: Match type - 'exact', 'prefix', or 'contains'
        limit: Maximum number of results to return
        db_path: Path to SQLite database

    Returns:
        List of translation dictionaries with keys:
            - source_word: The source word
            - source_language: Source language code
            - target_word: The translated word
            - target_language: Target language code
            - webonary_link: Link to webonary (if target is African language)
    """
    repo = _get_translation_repo(db_path)
    return repo.query_translations(
        source_lang=source_lang,
        word=word,
        target_lang=target_lang,
        match=match,  # type: ignore
        limit=limit,
        direction="forward"
    )


def query_reverse_translation(
    source_lang: str,
    word: str,
    target_lang: str | None = None,
    match: MatchType = "exact",
    limit: int = 10,
    db_path: str | None = None
) -> list[dict]:
    """
    Query reverse translations (e.g., Ngiemboon → English/French).

    DEPRECATED: Use TranslationRepository.query_translations() with direction='reverse'.

    This queries in the opposite direction from query_translation.
    For African languages with webonary links, this finds what English/French
    words translate TO the given African language word.

    Args:
        source_lang: Source language code (e.g., 'nnh' for Ngiemboon)
        word: Word to look up
        target_lang: Target language code (optional, omit for all languages)
        match: Match type - 'exact', 'prefix', or 'contains'
        limit: Maximum number of results
        db_path: Path to SQLite database

    Returns:
        List of translation dictionaries
    """
    repo = _get_translation_repo(db_path)
    return repo.query_translations(
        source_lang=source_lang,
        word=word,
        target_lang=target_lang,
        match=match,  # type: ignore
        limit=limit,
        direction="reverse"
    )


def get_supported_languages(db_path: str | None = None) -> dict:
    """
    Get list of all supported languages in the database.

    DEPRECATED: Use LanguageRepository.get_all_languages().

    Returns:
        Dictionary with keys:
            - languages: List of language info dicts
            - count: Total number of languages

    Each language dict contains:
            - code: Language code (e.g., 'en', 'fr', 'nnh')
            - name: Human-readable name
            - type: 'source' or 'target' (African languages can be both)
            - word_count: Number of words in this language
    """
    repo = _get_language_repo(db_path)
    return repo.get_all_languages()


def get_database_stats(db_path: str | None = None) -> dict:
    """
    Get statistics about the database.

    DEPRECATED: Use StatsRepository.get_stats().

    Returns:
        Dictionary with database statistics:
            - total_words: Total number of unique words
            - total_translations: Total number of translation pairs
            - languages: Number of languages
            - db_size_bytes: Database file size in bytes
    """
    repo = _get_stats_repo(db_path)
    return repo.get_stats()
