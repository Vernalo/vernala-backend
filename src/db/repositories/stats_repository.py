"""Repository for database statistics."""

from pathlib import Path
from db.repositories.base import BaseRepository


class StatsRepository(BaseRepository):
    """Repository for database statistics."""

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics:
                - total_words: Total number of unique words
                - total_translations: Total number of translation pairs
                - languages: Number of languages
                - db_size_bytes: Database file size in bytes

        Example:
            {
                "total_words": 12345,
                "total_translations": 67890,
                "languages": 5,
                "db_size_bytes": 7340032
            }
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

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
        db_path = Path(self.db_path)
        db_size = db_path.stat().st_size if db_path.exists() else 0

        return {
            "total_words": total_words,
            "total_translations": total_translations,
            "languages": language_count,
            "db_size_bytes": db_size
        }
