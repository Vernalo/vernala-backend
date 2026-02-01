from fastapi import APIRouter, Query, HTTPException
from app.models import TranslateResponse, QueryInfo, ErrorResponse
from app.dependencies import TranslationServiceDep
from app.services import TranslationQuery, LanguageValidationError

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.get(
    "",
    response_model=TranslateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid language code or parameters"},
        404: {"model": ErrorResponse, "description": "No translations found"}
    },
    summary="Translate a word",
)
async def translate(
    translation_service: TranslationServiceDep,
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
    query = TranslationQuery(
        source_lang=source,
        word=word,
        target_lang=target,
        match=match, # type: ignore
        limit=limit
    )

    try:
        results = translation_service.translate(query)
    except LanguageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return TranslateResponse(
        query=QueryInfo(
            source=source,
            target=target,
            word=word,
            match=match
        ),
        results=results,
        count=len(results)
    )
