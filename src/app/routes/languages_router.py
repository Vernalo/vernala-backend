from fastapi import APIRouter, HTTPException
from app.models import LanguagesResponse, ErrorResponse
from app.dependencies import LanguageServiceDep

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.get(
    "",
    response_model=LanguagesResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Database error"}
    },
    summary="Get supported languages",
)
async def get_languages(
    language_service: LanguageServiceDep
) -> LanguagesResponse:
    try:
        languages = language_service.get_all_languages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return LanguagesResponse(
        languages=languages,
        count=len(languages)
    )
