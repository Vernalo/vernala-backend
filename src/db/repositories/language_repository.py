"""Repository for language metadata queries."""

from db.repositories.base import BaseRepository


class LanguageRepository(BaseRepository):
    """Repository for language metadata queries."""

    def __init__(self, db_path: str | None = None, language_config: dict | None = None):
        """
        Initialize language repository.

        Args:
            db_path: Path to SQLite database file
            language_config: Language configuration dict (optional, loaded from scrapers.languages if None)
        """
        super().__init__(db_path)
        self.language_config = language_config or self._load_default_config()

    def _load_default_config(self) -> dict:
        """
        Load language configuration from scrapers package.

        Returns:
            Dictionary of language configurations
        """
        try:
            from scrapers.languages import LANGUAGES
            return LANGUAGES
        except ImportError:
            return {}

    def get_all_languages(self) -> dict:
        """
        Get all supported languages with metadata.

        Returns:
            Dictionary with keys:
                - languages: List of language info dicts
                - count: Total number of languages

        Each language dict contains:
                - code: Language code (e.g., 'en', 'fr', 'nnh')
                - name: Human-readable name
                - type: 'source' or 'target'
                - word_count: Number of words in this language

        Example:
            {
                "languages": [
                    {"code": "en", "name": "English", "type": "source", "word_count": 1234},
                    {"code": "nnh", "name": "Ngiemboon", "type": "target", "word_count": 5678}
                ],
                "count": 2
            }
        """
        query = """
            SELECT language_code, COUNT(*) as word_count
            FROM words
            GROUP BY language_code
            ORDER BY language_code
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            languages = []
            for row in rows:
                lang_code = row["language_code"]
                word_count = row["word_count"]

                lang_info = self._get_language_info(lang_code, word_count)
                languages.append(lang_info)

            return {
                "languages": languages,
                "count": len(languages)
            }

    def _get_language_info(self, lang_code: str, word_count: int) -> dict:
        """
        Get language information from code.

        Args:
            lang_code: Language code (e.g., 'en', 'fr', 'nnh')
            word_count: Number of words in this language

        Returns:
            Dictionary with language metadata
        """
        if lang_code == "en":
            return {
                "code": lang_code,
                "name": "English",
                "type": "source",
                "word_count": word_count
            }
        elif lang_code == "fr":
            return {
                "code": lang_code,
                "name": "French",
                "type": "source",
                "word_count": word_count
            }
        else:
            # African language - find name from config
            name = self._find_language_name(lang_code)
            return {
                "code": lang_code,
                "name": name,
                "type": "target",
                "word_count": word_count
            }

    def _find_language_name(self, lang_code: str) -> str:
        """
        Find language name from configuration.

        Args:
            lang_code: Language code to look up

        Returns:
            Human-readable language name (defaults to uppercase code if not found)
        """
        for lang_config in self.language_config.values():
            if lang_config.lang_code == lang_code:
                return lang_config.name.capitalize()
        return lang_code.upper()  # Fallback

    def get_language_codes(self) -> set[str]:
        """
        Get set of all language codes in database.

        Returns:
            Set of language code strings

        Example:
            {'en', 'fr', 'nnh', 'bfd'}
        """
        languages = self.get_all_languages()
        return {lang["code"] for lang in languages["languages"]}
