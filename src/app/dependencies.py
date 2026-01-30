"""FastAPI dependencies for repository injection."""

import os
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from db.repositories import TranslationRepository, LanguageRepository, StatsRepository

# Default database path (can be overridden via environment variable)
DEFAULT_DB_PATH = os.getenv("VERNALA_DB_PATH", "vernala.db")


@lru_cache()
def get_translation_repository() -> TranslationRepository:
    """
    Dependency for translation repository (cached singleton).

    Returns:
        TranslationRepository instance

    Example:
        @router.get("/translate")
        def translate(repo: TranslationRepositoryDep):
            results = repo.query_translations(...)
    """
    return TranslationRepository(DEFAULT_DB_PATH)


@lru_cache()
def get_language_repository() -> LanguageRepository:
    """
    Dependency for language repository (cached singleton).

    Returns:
        LanguageRepository instance

    Example:
        @router.get("/languages")
        def get_languages(repo: LanguageRepositoryDep):
            return repo.get_all_languages()
    """
    return LanguageRepository(DEFAULT_DB_PATH)


@lru_cache()
def get_stats_repository() -> StatsRepository:
    """
    Dependency for stats repository (cached singleton).

    Returns:
        StatsRepository instance

    Example:
        @router.get("/stats")
        def get_stats(repo: StatsRepositoryDep):
            return repo.get_stats()
    """
    return StatsRepository(DEFAULT_DB_PATH)


# Type aliases for cleaner annotations in route handlers
TranslationRepositoryDep = Annotated[TranslationRepository, Depends(get_translation_repository)]
LanguageRepositoryDep = Annotated[LanguageRepository, Depends(get_language_repository)]
StatsRepositoryDep = Annotated[StatsRepository, Depends(get_stats_repository)]
