import os
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from db.repositories import TranslationRepository, LanguageRepository
from app.services import LanguageService, TranslationService

DEFAULT_DB_PATH = os.getenv("VERNALA_DB_PATH", "vernala.db")


# Repository dependencies
@lru_cache()
def get_translation_repository() -> TranslationRepository:
    return TranslationRepository(DEFAULT_DB_PATH)


@lru_cache()
def get_language_repository() -> LanguageRepository:
    return LanguageRepository(DEFAULT_DB_PATH)


# Service dependencies
@lru_cache()
def get_language_service(
    language_repo: LanguageRepository = Depends(get_language_repository)
) -> LanguageService:
    """Get singleton LanguageService instance."""
    return LanguageService(language_repo=language_repo)


@lru_cache()
def get_translation_service(
    translation_repo: TranslationRepository = Depends(get_translation_repository),
    language_service: LanguageService = Depends(get_language_service)
) -> TranslationService:
    """Get singleton TranslationService instance."""
    return TranslationService(
        translation_repo=translation_repo,
        language_service=language_service
    )


# Type annotations for dependency injection
TranslationRepositoryDep = Annotated[TranslationRepository, Depends(get_translation_repository)]
LanguageRepositoryDep = Annotated[LanguageRepository, Depends(get_language_repository)]
LanguageServiceDep = Annotated[LanguageService, Depends(get_language_service)]
TranslationServiceDep = Annotated[TranslationService, Depends(get_translation_service)]