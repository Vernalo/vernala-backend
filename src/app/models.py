"""Pydantic models for API request/response validation."""

from pydantic import BaseModel, Field


class TranslationResult(BaseModel):
    """A single translation result."""

    source_word: str = Field(..., description="The source word")
    source_language: str = Field(..., description="Source language code (e.g., 'en', 'fr', 'nnh')")
    target_word: str = Field(..., description="The translated word")
    target_language: str = Field(..., description="Target language code (e.g., 'en', 'fr', 'nnh')")
    webonary_link: str | None = Field(None, description="Link to webonary (for African languages)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source_word": "abandon",
                    "source_language": "en",
                    "target_word": "ńnyé2ńnyé",
                    "target_language": "nnh",
                    "webonary_link": "https://www.webonary.org/ngiemboon/g8a5c2a0f-0af2-41ee-90a1-f06f2afa8fc9?lang=en"
                }
            ]
        }
    }


class QueryInfo(BaseModel):
    """Information about the query that was executed."""

    source: str = Field(..., description="Source language code")
    target: str | None = Field(None, description="Target language code (None for all languages)")
    word: str = Field(..., description="The word that was queried")
    match: str = Field("exact", description="Match type: exact, prefix, or contains")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "en",
                    "target": "nnh",
                    "word": "abandon",
                    "match": "exact"
                }
            ]
        }
    }


class TranslateResponse(BaseModel):
    """Response for translation queries."""

    query: QueryInfo = Field(..., description="Details about the query")
    results: list[TranslationResult] = Field(..., description="List of translation results")
    count: int = Field(..., description="Number of results returned")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": {
                        "source": "en",
                        "target": "nnh",
                        "word": "abandon",
                        "match": "exact"
                    },
                    "results": [
                        {
                            "source_word": "abandon",
                            "source_language": "en",
                            "target_word": "ńnyé2ńnyé",
                            "target_language": "nnh",
                            "webonary_link": "https://www.webonary.org/ngiemboon/test"
                        }
                    ],
                    "count": 1
                }
            ]
        }
    }


class LanguageInfo(BaseModel):
    """Information about a supported language."""

    code: str = Field(..., description="ISO 639-3 language code")
    name: str = Field(..., description="Human-readable language name")
    type: str = Field(..., description="Language type: 'source' or 'target'")
    word_count: int = Field(..., description="Number of words in this language")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "nnh",
                    "name": "Ngiemboon",
                    "type": "target",
                    "word_count": 13562
                }
            ]
        }
    }


class LanguagesResponse(BaseModel):
    """Response for supported languages query."""

    languages: list[LanguageInfo] = Field(..., description="List of supported languages")
    count: int = Field(..., description="Number of languages")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "languages": [
                        {"code": "en", "name": "English", "type": "source", "word_count": 8001},
                        {"code": "fr", "name": "French", "type": "source", "word_count": 7612},
                        {"code": "nnh", "name": "Ngiemboon", "type": "target", "word_count": 13562}
                    ],
                    "count": 3
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"detail": "Unsupported source language: xyz"}
            ]
        }
    }
