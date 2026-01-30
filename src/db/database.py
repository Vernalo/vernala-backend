"""
Database query layer for Vernala translation API.

Provides functions to query translations between languages using SQLite.
"""

import sqlite3
from pathlib import Path
from typing import Literal

# Import language configs for metadata
from scrapers.languages import LANGUAGES


# Database path (configurable)
DEFAULT_DB_PATH = "vernala.db"

MatchType = Literal["exact", "prefix", "contains"]


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        sqlite3.Connection configured for dictionary access
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def query_translation(
    source_lang: str,
    word: str,
    target_lang: str | None = None,
    match: MatchType = "exact",
    limit: int = 10,
    db_path: str = DEFAULT_DB_PATH
) -> list[dict]:
    """
    Query translations for a word from source language to target language(s).

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
    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        # Build the WHERE clause based on match type
        word_normalized = word.lower()

        if match == "exact":
            word_condition = "source.word_normalized = ?"
            word_param = word_normalized
        elif match == "prefix":
            word_condition = "source.word_normalized LIKE ?"
            word_param = f"{word_normalized}%"
        elif match == "contains":
            word_condition = "source.word_normalized LIKE ?"
            word_param = f"%{word_normalized}%"
        else:
            raise ValueError(f"Invalid match type: {match}")

        # Build target language condition
        if target_lang:
            target_condition = "AND target.language_code = ?"
            params = [source_lang, word_param, target_lang, limit]
        else:
            target_condition = ""
            params = [source_lang, word_param, limit]

        # Query for translations
        query = f"""
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

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert to list of dicts
        results = []
        for row in rows:
            results.append({
                "source_word": row["source_word"],
                "source_language": row["source_language"],
                "target_word": row["target_word"],
                "target_language": row["target_language"],
                "webonary_link": row["webonary_link"]
            })

        return results

    finally:
        conn.close()


def query_reverse_translation(
    source_lang: str,
    word: str,
    target_lang: str | None = None,
    match: MatchType = "exact",
    limit: int = 10,
    db_path: str = DEFAULT_DB_PATH
) -> list[dict]:
    """
    Query reverse translations (e.g., Ngiemboon → English/French).

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
    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        # Build WHERE clause based on match type
        word_normalized = word.lower()

        if match == "exact":
            word_condition = "source.word_normalized = ?"
            word_param = word_normalized
        elif match == "prefix":
            word_condition = "source.word_normalized LIKE ?"
            word_param = f"{word_normalized}%"
        elif match == "contains":
            word_condition = "source.word_normalized LIKE ?"
            word_param = f"%{word_normalized}%"
        else:
            raise ValueError(f"Invalid match type: {match}")

        # Build target language condition
        if target_lang:
            target_condition = "AND target.language_code = ?"
            params = [source_lang, word_param, target_lang, limit]
        else:
            target_condition = ""
            params = [source_lang, word_param, limit]

        # Query for reverse translations (swap source and target in JOIN)
        query = f"""
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

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert to list of dicts
        results = []
        for row in rows:
            results.append({
                "source_word": row["source_word"],
                "source_language": row["source_language"],
                "target_word": row["target_word"],
                "target_language": row["target_language"],
                "webonary_link": row["webonary_link"]
            })

        return results

    finally:
        conn.close()


def get_supported_languages(db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Get list of all supported languages in the database.

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
    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        # Get all language codes and word counts from database
        cursor.execute("""
            SELECT language_code, COUNT(*) as word_count
            FROM words
            GROUP BY language_code
            ORDER BY language_code
        """)

        rows = cursor.fetchall()

        languages = []
        for row in rows:
            lang_code = row["language_code"]
            word_count = row["word_count"]

            # Determine language name and type
            if lang_code == "en":
                name = "English"
                lang_type = "source"
            elif lang_code == "fr":
                name = "French"
                lang_type = "source"
            else:
                # African language - find name from config
                name = None
                for lang_config in LANGUAGES.values():
                    if lang_config.lang_code == lang_code:
                        name = lang_config.name.capitalize()
                        break

                if not name:
                    name = lang_code.upper()  # Fallback

                lang_type = "target"

            languages.append({
                "code": lang_code,
                "name": name,
                "type": lang_type,
                "word_count": word_count
            })

        return {
            "languages": languages,
            "count": len(languages)
        }

    finally:
        conn.close()


def get_database_stats(db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Get statistics about the database.

    Returns:
        Dictionary with database statistics:
            - total_words: Total number of unique words
            - total_translations: Total number of translation pairs
            - languages: Number of languages
            - db_size_bytes: Database file size in bytes
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        # Count words
        cursor.execute("SELECT COUNT(*) as count FROM words")
        total_words = cursor.fetchone()["count"]

        # Count translations
        cursor.execute("SELECT COUNT(*) as count FROM translations")
        total_translations = cursor.fetchone()["count"]

        # Count languages
        cursor.execute("SELECT COUNT(DISTINCT language_code) as count FROM words")
        language_count = cursor.fetchone()["count"]

        # Get file size
        db_size = Path(db_path).stat().st_size if Path(db_path).exists() else 0

        return {
            "total_words": total_words,
            "total_translations": total_translations,
            "languages": language_count,
            "db_size_bytes": db_size
        }

    finally:
        conn.close()
