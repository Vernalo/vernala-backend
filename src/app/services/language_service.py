from typing import Protocol

from app.models import LanguageInfo


class LanguageRepositoryProtocol(Protocol):
    def get_all_languages_raw(self) -> list[dict]: ...


class LanguageService:
    def __init__(
        self,
        language_repo: LanguageRepositoryProtocol,
        language_config: dict | None = None
    ):
        self.language_repo = language_repo
        self.language_config = language_config or self._load_default_config()
        self._valid_languages_cache: set[str] | None = None

    def _load_default_config(self) -> dict:
        try:
            from cli.scrapers.languages import LANGUAGES
            return LANGUAGES
        except ImportError:
            return {}

    def get_valid_language_codes(self) -> set[str]:
        """
        Get set of all valid language codes.

        Returns:
            Set of language codes (e.g., {'en', 'fr', 'nnh', 'bfd'})
        """
        if self._valid_languages_cache is None:
            raw_languages = self.language_repo.get_all_languages_raw()
            self._valid_languages_cache = {lang["language_code"] for lang in raw_languages}
        return self._valid_languages_cache

    def validate_language_code(self, code: str) -> bool:
        """
        Check if a language code is supported.

        Args:
            code: Language code to validate

        Returns:
            True if valid, False otherwise
        """
        return code in self.get_valid_language_codes()

    def get_language_type(self, lang_code: str) -> str:
        """
        Determine language type: 'source' or 'target'.

        English and French are source languages,
        African languages are target languages.

        Args:
            lang_code: Language code (e.g., 'en', 'fr', 'nnh')

        Returns:
            'source' or 'target'
        """
        if lang_code in {"en", "fr"}:
            return "source"
        return "target"

    def is_african_language(self, lang_code: str) -> bool:
        return lang_code not in {"en", "fr"}

    def get_language_name(self, lang_code: str) -> str:
        """
        Get human-readable name for a language code.

        Args:
            lang_code: Language code

        Returns:
            Language name (e.g., "English", "Ngiemboon")
        """
        if lang_code == "en":
            return "English"
        elif lang_code == "fr":
            return "French"
        else:
            # Look up African language name from config
            for lang_config in self.language_config.values():
                if lang_config.lang_code == lang_code:
                    return lang_config.name.capitalize()
            return lang_code.upper()

    def get_all_languages(self) -> list[LanguageInfo]:
        raw_languages = self.language_repo.get_all_languages_raw()

        return [
            LanguageInfo(
                code=lang["language_code"],
                name=self.get_language_name(lang["language_code"]),
                type=self.get_language_type(lang["language_code"]),
                word_count=lang["word_count"]
            )
            for lang in raw_languages
        ]
