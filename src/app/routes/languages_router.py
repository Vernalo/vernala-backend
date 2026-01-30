"""Languages API endpoint."""

from fastapi import APIRouter, HTTPException
from app.models import LanguagesResponse, LanguageInfo, ErrorResponse
from db import database

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.get(
    "",
    response_model=LanguagesResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Database error"}
    },
    summary="Get supported languages",
    description="""
    Get a list of all supported languages in the translation database.

    Returns language codes, names, types (source/target), and word counts.

    **Language Types:**
    - `source`: Languages you can translate FROM (English, French)
    - `target`: Languages you can translate TO (African languages like Ngiemboon, Bafut)

    Note: African languages can be both source and target for bidirectional lookups.
    """
)
async def get_languages() -> LanguagesResponse:
    """
    Get all supported languages with metadata.

    Returns:
        LanguagesResponse with list of languages and their details
    """
    try:
        lang_info = database.get_supported_languages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Convert to Pydantic models
    languages = [
        LanguageInfo(**lang)
        for lang in lang_info["languages"]
    ]

    return LanguagesResponse(
        languages=languages,
        count=len(languages)
    )
