import os
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from db.repositories import TranslationRepository, LanguageRepository

DEFAULT_DB_PATH = os.getenv("VERNALA_DB_PATH", "vernala.db")


@lru_cache()
def get_translation_repository() -> TranslationRepository:
    return TranslationRepository(DEFAULT_DB_PATH)


@lru_cache()
def get_language_repository() -> LanguageRepository:
    return LanguageRepository(DEFAULT_DB_PATH)


TranslationRepositoryDep = Annotated[TranslationRepository, Depends(get_translation_repository)]
LanguageRepositoryDep = Annotated[LanguageRepository, Depends(get_language_repository)]