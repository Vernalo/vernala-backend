from dataclasses import dataclass
from typing import Protocol

from app.models import TranslationResult
from db.query_builders import MatchType, DirectionType


class TranslationRepositoryProtocol(Protocol):
    def query_translations(
        self,
        source_lang: str,
        word: str,
        target_lang: str | None,
        match: MatchType,
        limit: int,
        direction: DirectionType
    ) -> list[dict]: ...


class LanguageServiceProtocol(Protocol):
    def validate_language_code(self, code: str) -> bool: ...
    def get_valid_language_codes(self) -> set[str]: ...
    def is_african_language(self, lang_code: str) -> bool: ...


class LanguageValidationError(ValueError):
    def __init__(self, language: str, valid_codes: set[str], is_source: bool = True):
        lang_type = "source" if is_source else "target"
        valid_codes_str = ", ".join(sorted(valid_codes))
        super().__init__(
            f"Unsupported {lang_type} language: {language}. Valid codes: {valid_codes_str}"
        )
        self.language = language
        self.valid_codes = valid_codes
        self.is_source = is_source


@dataclass
class TranslationQuery:
    source_lang: str
    word: str
    target_lang: str | None
    match: MatchType
    limit: int


class TranslationService:
    def __init__(
        self,
        translation_repo: TranslationRepositoryProtocol,
        language_service: LanguageServiceProtocol
    ):
        self.translation_repo = translation_repo
        self.language_service = language_service

    def validate_languages(self, source: str, target: str | None) -> None:
        valid_codes = self.language_service.get_valid_language_codes()

        if not self.language_service.validate_language_code(source):
            raise LanguageValidationError(source, valid_codes, is_source=True)

        if target and not self.language_service.validate_language_code(target):
            raise LanguageValidationError(target, valid_codes, is_source=False)

    def determine_direction(self, source_lang: str) -> DirectionType:
        """
        Determine query direction based on source language.

        Business rule:
        - Forward: English/French → African languages
        - Reverse: African languages → English/French

        Args:
            source_lang: Source language code

        Returns:
            'forward' or 'reverse'
        """
        is_african = self.language_service.is_african_language(source_lang)
        return "reverse" if is_african else "forward"

    def translate(self, query: TranslationQuery) -> list[TranslationResult]:
        """
        Translate a word from source to target language(s).

        Args:
            query: Translation query parameters

        Returns:
            List of translation results as Pydantic models

        Raises:
            LanguageValidationError: If language codes are invalid
        """
        self.validate_languages(query.source_lang, query.target_lang)

        direction = self.determine_direction(query.source_lang)

        raw_results = self.translation_repo.query_translations(
            source_lang=query.source_lang,
            word=query.word,
            target_lang=query.target_lang,
            match=query.match,
            limit=query.limit,
            direction=direction
        )

        return [TranslationResult(**result) for result in raw_results]
