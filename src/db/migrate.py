"""
Database migration script: JSON files → SQLite database.

Reads scraped dictionary data from JSON files and populates a SQLite database
with a generic multi-language schema that supports unlimited languages.
"""

import json
import sqlite3
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass

# Import language configs to map folder names to ISO 639-3 codes
from cli.scrapers.languages import LANGUAGES


@dataclass
class MigrationStats:
    """Statistics collected during migration."""
    words_per_language: dict[str, int]
    translation_pairs: int
    duplicate_words_skipped: int
    files_processed: int


class DatabaseMigrator:
    """Handles migration of JSON data to SQLite database."""

    def __init__(self, db_path: str = "vernala.db", scraped_data_dir: str = "scraped_data"):
        self.db_path = db_path
        self.scraped_data_dir = Path(scraped_data_dir)
        self.stats = MigrationStats(
            words_per_language=defaultdict(int),
            translation_pairs=0,
            duplicate_words_skipped=0,
            files_processed=0
        )

    def create_schema(self, conn: sqlite3.Connection) -> None:
        """Create database schema with tables and indexes."""
        cursor = conn.cursor()

        # Generic words table for ALL languages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                word_normalized TEXT NOT NULL,
                language_code TEXT NOT NULL,
                webonary_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(word, language_code, webonary_link)
            )
        """)

        # Generic translations table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                source_word_id INTEGER NOT NULL,
                target_word_id INTEGER NOT NULL,
                PRIMARY KEY (source_word_id, target_word_id),
                FOREIGN KEY (source_word_id) REFERENCES words(id) ON DELETE CASCADE,
                FOREIGN KEY (target_word_id) REFERENCES words(id) ON DELETE CASCADE
            )
        """)

        # Performance indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_normalized ON words(word_normalized, language_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_language ON words(language_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_source ON translations(source_word_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_target ON translations(target_word_id)")

        conn.commit()
        print("✓ Database schema created")

    def get_or_create_word(
        self,
        cursor: sqlite3.Cursor,
        word: str,
        language_code: str,
        webonary_link: str | None = None
    ) -> int:
        """
        Get existing word ID or insert new word.
        Returns word ID.
        """
        word_normalized = word.lower()

        # Try to find existing word
        cursor.execute(
            """
            SELECT id FROM words
            WHERE word = ? AND language_code = ? AND
                  (webonary_link = ? OR (webonary_link IS NULL AND ? IS NULL))
            """,
            (word, language_code, webonary_link, webonary_link)
        )
        result = cursor.fetchone()

        if result:
            self.stats.duplicate_words_skipped += 1
            return result[0]

        # Insert new word
        cursor.execute(
            """
            INSERT INTO words (word, word_normalized, language_code, webonary_link)
            VALUES (?, ?, ?, ?)
            """,
            (word, word_normalized, language_code, webonary_link)
        )
        self.stats.words_per_language[language_code] += 1
        return cursor.lastrowid

    def process_json_file(
        self,
        conn: sqlite3.Connection,
        json_file: Path,
        source_lang_code: str,
        target_lang_code: str,
        target_lang_name: str
    ) -> None:
        """Process a single JSON file containing dictionary entries."""
        cursor = conn.cursor()

        with open(json_file, 'r', encoding='utf-8') as f:
            entries = json.load(f)

        # Determine source language key in JSON ("english" or "french")
        source_key = "english" if source_lang_code == "en" else "french"

        for entry in entries:
            # Get source word (English or French)
            source_word = entry.get(source_key)
            if not source_word:
                continue

            # Insert source word (no webonary link for English/French)
            source_word_id = self.get_or_create_word(cursor, source_word, source_lang_code)

            # Process all target language translations using the language name as key
            target_translations = entry.get(target_lang_name, [])

            for translation in target_translations:
                target_word = translation.get("word")
                target_link = translation.get("link")

                if not target_word:
                    continue

                # Insert target word (with webonary link)
                target_word_id = self.get_or_create_word(
                    cursor,
                    target_word,
                    target_lang_code,
                    target_link
                )

                # Create translation link (skip duplicates)
                try:
                    cursor.execute(
                        "INSERT INTO translations (source_word_id, target_word_id) VALUES (?, ?)",
                        (source_word_id, target_word_id)
                    )
                    self.stats.translation_pairs += 1
                except sqlite3.IntegrityError:
                    # Translation pair already exists
                    pass

        self.stats.files_processed += 1

    def migrate(self) -> None:
        """Run the full migration process."""
        print(f"Starting migration: {self.scraped_data_dir} → {self.db_path}")
        print()

        # Connect to database
        conn = sqlite3.connect(self.db_path)

        try:
            # Create schema
            self.create_schema(conn)
            print()

            # Iterate through all languages in scraped_data/
            for lang_folder in sorted(self.scraped_data_dir.iterdir()):
                if not lang_folder.is_dir():
                    continue

                lang_name = lang_folder.name

                # Get language config
                if lang_name not in LANGUAGES:
                    print(f"⚠ Skipping unknown language: {lang_name}")
                    continue

                lang_config = LANGUAGES[lang_name]
                target_lang_code = lang_config.lang_code

                print(f"Processing {lang_name} ({target_lang_code})...")

                # Process English source files
                en_dir = lang_folder / "en"
                if en_dir.exists():
                    json_files = sorted(en_dir.glob("*.json"))
                    for json_file in json_files:
                        self.process_json_file(conn, json_file, "en", target_lang_code, lang_name)
                    print(f"  ✓ Processed {len(json_files)} English files")

                # Process French source files
                fr_dir = lang_folder / "fr"
                if fr_dir.exists():
                    json_files = sorted(fr_dir.glob("*.json"))
                    for json_file in json_files:
                        self.process_json_file(conn, json_file, "fr", target_lang_code, lang_name)
                    print(f"  ✓ Processed {len(json_files)} French files")

                print()

            # Commit all changes
            conn.commit()

            # Print summary
            self.print_summary(conn)

        finally:
            conn.close()

    def print_summary(self, conn: sqlite3.Connection) -> None:
        """Print migration summary statistics."""
        cursor = conn.cursor()

        print("=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print()

        print("Words by Language:")
        for lang_code in sorted(self.stats.words_per_language.keys()):
            count = self.stats.words_per_language[lang_code]
            lang_name = self._get_language_name(lang_code)
            print(f"  {lang_code} ({lang_name}): {count:,}")
        print()

        # Total counts
        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]

        print(f"Total unique words: {total_words:,}")
        print(f"Total translation pairs: {self.stats.translation_pairs:,}")
        print(f"Duplicate words skipped: {self.stats.duplicate_words_skipped:,}")
        print(f"JSON files processed: {self.stats.files_processed}")
        print()

        # Database file size
        db_size_bytes = Path(self.db_path).stat().st_size
        db_size_kb = db_size_bytes / 1024
        print(f"Database size: {db_size_kb:.1f} KB ({db_size_bytes:,} bytes)")
        print()

        # Sample queries
        print("Sample Queries:")
        print("-" * 60)

        # English → Target language (first available)
        cursor.execute("""
            SELECT target.word, target.language_code, target.webonary_link
            FROM words source
            JOIN translations t ON source.id = t.source_word_id
            JOIN words target ON t.target_word_id = target.id
            WHERE source.language_code = 'en' AND source.word = 'abandon'
            LIMIT 3
        """)
        results = cursor.fetchall()
        if results:
            print("English 'abandon' →")
            for word, lang, link in results:
                print(f"  {word} ({lang}): {link}")
        print()

        print("=" * 60)
        print(f"✓ Migration complete: {self.db_path}")
        print("=" * 60)

    def _get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name from code."""
        if lang_code == "en":
            return "English"
        elif lang_code == "fr":
            return "French"
        else:
            # Find in LANGUAGES config
            for lang_config in LANGUAGES.values():
                if lang_config.lang_code == lang_code:
                    return lang_config.name.capitalize()
            return "Unknown"


def main():
    """Run migration script."""
    migrator = DatabaseMigrator()
    migrator.migrate()


if __name__ == "__main__":
    main()
