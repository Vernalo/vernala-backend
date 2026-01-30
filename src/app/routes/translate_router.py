"""Translation API endpoints."""

from fastapi import APIRouter, Query, HTTPException
from app.models import TranslateResponse, QueryInfo, TranslationResult, ErrorResponse
from app.dependencies import TranslationRepositoryDep, LanguageRepositoryDep

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.get(
    "",
    response_model=TranslateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid language code or parameters"},
        404: {"model": ErrorResponse, "description": "No translations found"}
    },
    summary="Translate a word",
    description="""
    Translate a word from one language to another.

    **Translation Directions:**
    - Forward: English/French → African languages (e.g., en → nnh)
    - Reverse: African languages → English/French (e.g., nnh → en)
    - Bidirectional: African language → All languages (omit target parameter)

    **Match Types:**
    - `exact`: Exact word match (default)
    - `prefix`: Words starting with the query (useful for autocomplete)
    - `contains`: Words containing the query

    **Examples:**
    - `/translate?source=en&target=nnh&word=abandon` - English to Ngiemboon
    - `/translate?source=nnh&target=en&word=ńnyé2ńnyé` - Ngiemboon to English
    - `/translate?source=nnh&word=ńnyé2ńnyé` - Ngiemboon to all languages
    - `/translate?source=en&target=nnh&word=aban&match=prefix` - Autocomplete
    """
)
async def translate(
    translation_repo: TranslationRepositoryDep,
    language_repo: LanguageRepositoryDep,
    source: str = Query(
        ...,
        min_length=2,
        max_length=3,
        description="Source language code (e.g., 'en', 'fr', 'nnh', 'bfd')",
        examples=["en"]
    ),
    word: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Word to translate",
        examples=["abandon"]
    ),
    target: str | None = Query(
        None,
        min_length=2,
        max_length=3,
        description="Target language code (omit for all languages)",
        examples=["nnh"]
    ),
    match: str = Query(
        "exact",
        pattern="^(exact|prefix|contains)$",
        description="Match type: exact, prefix, or contains",
        examples=["exact"]
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return",
        examples=[10]
    )
) -> TranslateResponse:
    """
    Translate a word from source language to target language(s).

    Returns a list of translation results with webonary links for African languages.
    """
    # Get valid languages from repository (cached)
    valid_languages = language_repo.get_language_codes()

    # Validate language codes
    if source not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source language: {source}. Valid codes: {', '.join(sorted(valid_languages))}"
        )

    if target and target not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target language: {target}. Valid codes: {', '.join(sorted(valid_languages))}"
        )

    # Determine translation direction
    # African languages (nnh, bfd, etc.) need reverse lookup when they're the source
    is_african_source = source not in {"en", "fr"}
    direction = "reverse" if is_african_source else "forward"

    try:
        # Query using repository with direction parameter
        results = translation_repo.query_translations(
            source_lang=source,
            word=word,
            target_lang=target,
            match=match,  # type: ignore
            limit=limit,
            direction=direction  # type: ignore
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Convert to Pydantic models
    translation_results = [
        TranslationResult(**result)
        for result in results
    ]

    return TranslateResponse(
        query=QueryInfo(
            source=source,
            target=target,
            word=word,
            match=match
        ),
        results=translation_results,
        count=len(translation_results)
    )
