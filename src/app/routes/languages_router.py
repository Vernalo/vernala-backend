from fastapi import APIRouter, HTTPException
from app.models import LanguagesResponse, LanguageInfo, ErrorResponse
from app.dependencies import LanguageRepositoryDep

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
    language_repo: LanguageRepositoryDep
) -> LanguagesResponse:
    try:
        lang_info = language_repo.get_all_languages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    languages = [
        LanguageInfo(**lang)
        for lang in lang_info["languages"]
    ]

    return LanguagesResponse(
        languages=languages,
        count=len(languages)
    )
