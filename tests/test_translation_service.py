import pytest
from app.services.translation_service import (
    TranslationService,
    TranslationQuery,
    LanguageValidationError
)
from app.models import TranslationResult


class MockTranslationRepository:
    """Mock repository for testing."""
    def query_translations(self, source_lang, word, target_lang, match, limit, direction):
        return [
            {
                "source_word": "test",
                "source_language": source_lang,
                "target_word": "translated",
                "target_language": target_lang or "nnh",
                "webonary_link": "https://example.com"
            }
        ]


class MockLanguageService:
    """Mock language service for testing."""
    def validate_language_code(self, code):
        return code in {"en", "fr", "nnh", "bfd"}

    def get_valid_language_codes(self):
        return {"en", "fr", "nnh", "bfd"}

    def is_african_language(self, lang_code):
        return lang_code not in {"en", "fr"}


@pytest.fixture
def translation_service():
    """Create TranslationService with mocks."""
    repo = MockTranslationRepository()
    lang_service = MockLanguageService()
    return TranslationService(translation_repo=repo, language_service=lang_service)


class TestTranslationService:
    """Tests for TranslationService business logic."""

    def test_validate_languages_valid_both(self, translation_service):
        """Test validating valid source and target languages."""
        # Should not raise
        translation_service.validate_languages("en", "nnh")
        translation_service.validate_languages("fr", "bfd")

    def test_validate_languages_valid_source_only(self, translation_service):
        """Test validating valid source with no target."""
        # Should not raise
        translation_service.validate_languages("en", None)
        translation_service.validate_languages("nnh", None)

    def test_validate_languages_invalid_source(self, translation_service):
        """Test validating invalid source language."""
        with pytest.raises(LanguageValidationError) as exc:
            translation_service.validate_languages("xyz", "nnh")

        assert "source" in str(exc.value).lower()
        assert "xyz" in str(exc.value)
        assert exc.value.language == "xyz"
        assert exc.value.is_source is True

    def test_validate_languages_invalid_target(self, translation_service):
        """Test validating invalid target language."""
        with pytest.raises(LanguageValidationError) as exc:
            translation_service.validate_languages("en", "xyz")

        assert "target" in str(exc.value).lower()
        assert "xyz" in str(exc.value)
        assert exc.value.language == "xyz"
        assert exc.value.is_source is False

    def test_validate_languages_shows_valid_codes(self, translation_service):
        """Test that validation error shows valid codes."""
        with pytest.raises(LanguageValidationError) as exc:
            translation_service.validate_languages("xyz", "nnh")

        error_msg = str(exc.value)
        assert "en" in error_msg
        assert "fr" in error_msg
        assert "nnh" in error_msg
        assert "bfd" in error_msg

    def test_determine_direction_forward_english(self, translation_service):
        """Test direction determination for English source."""
        assert translation_service.determine_direction("en") == "forward"

    def test_determine_direction_forward_french(self, translation_service):
        """Test direction determination for French source."""
        assert translation_service.determine_direction("fr") == "forward"

    def test_determine_direction_reverse_african(self, translation_service):
        """Test direction determination for African source."""
        assert translation_service.determine_direction("nnh") == "reverse"
        assert translation_service.determine_direction("bfd") == "reverse"

    def test_translate_success(self, translation_service):
        """Test successful translation."""
        query = TranslationQuery(
            source_lang="en",
            word="test",
            target_lang="nnh",
            match="exact",
            limit=10
        )

        results = translation_service.translate(query)

        assert len(results) > 0
        assert all(isinstance(r, TranslationResult) for r in results)

    def test_translate_result_structure(self, translation_service):
        """Test translation result structure."""
        query = TranslationQuery(
            source_lang="en",
            word="test",
            target_lang="nnh",
            match="exact",
            limit=10
        )

        results = translation_service.translate(query)
        result = results[0]

        assert hasattr(result, "source_word")
        assert hasattr(result, "source_language")
        assert hasattr(result, "target_word")
        assert hasattr(result, "target_language")
        assert hasattr(result, "webonary_link")

    def test_translate_invalid_source(self, translation_service):
        """Test translation with invalid source language."""
        query = TranslationQuery(
            source_lang="xyz",
            word="test",
            target_lang="nnh",
            match="exact",
            limit=10
        )

        with pytest.raises(LanguageValidationError):
            translation_service.translate(query)

    def test_translate_invalid_target(self, translation_service):
        """Test translation with invalid target language."""
        query = TranslationQuery(
            source_lang="en",
            word="test",
            target_lang="xyz",
            match="exact",
            limit=10
        )

        with pytest.raises(LanguageValidationError):
            translation_service.translate(query)

    def test_translate_no_target(self, translation_service):
        """Test translation with no target language (all languages)."""
        query = TranslationQuery(
            source_lang="en",
            word="test",
            target_lang=None,
            match="exact",
            limit=10
        )

        results = translation_service.translate(query)
        assert len(results) > 0

    def test_translate_calls_repository_with_correct_params(self, translation_service):
        """Test that translation calls repository with correct parameters."""
        call_params = []

        class RecordingRepo:
            def query_translations(self, source_lang, word, target_lang, match, limit, direction):
                call_params.append({
                    "source_lang": source_lang,
                    "word": word,
                    "target_lang": target_lang,
                    "match": match,
                    "limit": limit,
                    "direction": direction
                })
                return []

        service = TranslationService(
            translation_repo=RecordingRepo(),
            language_service=MockLanguageService()
        )

        query = TranslationQuery(
            source_lang="en",
            word="abandon",
            target_lang="nnh",
            match="prefix",
            limit=20
        )

        service.translate(query)

        assert len(call_params) == 1
        params = call_params[0]
        assert params["source_lang"] == "en"
        assert params["word"] == "abandon"
        assert params["target_lang"] == "nnh"
        assert params["match"] == "prefix"
        assert params["limit"] == 20
        assert params["direction"] == "forward"  # en is not African

    def test_translation_query_dataclass(self):
        """Test TranslationQuery dataclass creation."""
        query = TranslationQuery(
            source_lang="en",
            word="test",
            target_lang="nnh",
            match="exact",
            limit=10
        )

        assert query.source_lang == "en"
        assert query.word == "test"
        assert query.target_lang == "nnh"
        assert query.match == "exact"
        assert query.limit == 10
