from .base import BaseRepository
from ..query_builders import LanguageQueryBuilder


class LanguageRepository(BaseRepository):
    def __init__(self, db_path: str | None = None, language_config: dict | None = None):
        super().__init__(db_path)
        self.language_config = language_config or self._load_default_config()
        self._query_builder = LanguageQueryBuilder()

    def _load_default_config(self) -> dict:
        try:
            from scrapers.languages import LANGUAGES
            return LANGUAGES
        except ImportError:
            return {}

    def get_all_languages(self) -> dict:
        query_result = self._query_builder.build_all_languages_query()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = query_result.execute(cursor)

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
