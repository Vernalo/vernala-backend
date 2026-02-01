import pytest
from app.services.language_service import LanguageService
from app.models import LanguageInfo


class MockLanguageRepository:
    """Mock repository for testing."""
    def get_all_languages_raw(self):
        return [
            {"language_code": "en", "word_count": 100},
            {"language_code": "fr", "word_count": 200},
            {"language_code": "nnh", "word_count": 300},
        ]


class MockLanguageConfig:
    """Mock language config for testing."""
    def __init__(self, lang_code, name):
        self.lang_code = lang_code
        self.name = name


@pytest.fixture
def language_service():
    """Create LanguageService with mock repository."""
    repo = MockLanguageRepository()
    config = {
        "ngiemboon": MockLanguageConfig("nnh", "ngiemboon")
    }
    return LanguageService(language_repo=repo, language_config=config)


class TestLanguageService:
    """Tests for LanguageService business logic."""

    def test_get_valid_language_codes(self, language_service):
        """Test getting valid language codes."""
        codes = language_service.get_valid_language_codes()
        assert codes == {"en", "fr", "nnh"}

    def test_get_valid_language_codes_caching(self, language_service):
        """Test that language codes are cached."""
        codes1 = language_service.get_valid_language_codes()
        codes2 = language_service.get_valid_language_codes()
        assert codes1 is codes2  # Same object reference

    def test_validate_language_code_valid(self, language_service):
        """Test validating valid language codes."""
        assert language_service.validate_language_code("en") is True
        assert language_service.validate_language_code("fr") is True
        assert language_service.validate_language_code("nnh") is True

    def test_validate_language_code_invalid(self, language_service):
        """Test validating invalid language codes."""
        assert language_service.validate_language_code("xyz") is False
        assert language_service.validate_language_code("abc") is False

    def test_get_language_type_source(self, language_service):
        """Test getting language type for source languages."""
        assert language_service.get_language_type("en") == "source"
        assert language_service.get_language_type("fr") == "source"

    def test_get_language_type_target(self, language_service):
        """Test getting language type for target languages."""
        assert language_service.get_language_type("nnh") == "target"
        assert language_service.get_language_type("bfd") == "target"
        assert language_service.get_language_type("xyz") == "target"

    def test_is_african_language_false(self, language_service):
        """Test identifying non-African languages."""
        assert language_service.is_african_language("en") is False
        assert language_service.is_african_language("fr") is False

    def test_is_african_language_true(self, language_service):
        """Test identifying African languages."""
        assert language_service.is_african_language("nnh") is True
        assert language_service.is_african_language("bfd") is True
        assert language_service.is_african_language("xyz") is True

    def test_get_language_name_english(self, language_service):
        """Test getting English language name."""
        assert language_service.get_language_name("en") == "English"

    def test_get_language_name_french(self, language_service):
        """Test getting French language name."""
        assert language_service.get_language_name("fr") == "French"

    def test_get_language_name_african_from_config(self, language_service):
        """Test getting African language name from config."""
        assert language_service.get_language_name("nnh") == "Ngiemboon"

    def test_get_language_name_african_unknown(self, language_service):
        """Test getting unknown African language name."""
        # Falls back to uppercase code
        assert language_service.get_language_name("xyz") == "XYZ"

    def test_get_all_languages(self, language_service):
        """Test getting all languages with full metadata."""
        languages = language_service.get_all_languages()

        assert len(languages) == 3
        assert all(isinstance(lang, LanguageInfo) for lang in languages)

    def test_get_all_languages_english(self, language_service):
        """Test English language metadata."""
        languages = language_service.get_all_languages()
        en_lang = next(l for l in languages if l.code == "en")

        assert en_lang.name == "English"
        assert en_lang.type == "source"
        assert en_lang.word_count == 100

    def test_get_all_languages_french(self, language_service):
        """Test French language metadata."""
        languages = language_service.get_all_languages()
        fr_lang = next(l for l in languages if l.code == "fr")

        assert fr_lang.name == "French"
        assert fr_lang.type == "source"
        assert fr_lang.word_count == 200

    def test_get_all_languages_ngiemboon(self, language_service):
        """Test Ngiemboon language metadata."""
        languages = language_service.get_all_languages()
        nnh_lang = next(l for l in languages if l.code == "nnh")

        assert nnh_lang.name == "Ngiemboon"
        assert nnh_lang.type == "target"
        assert nnh_lang.word_count == 300

    def test_default_config_loading(self):
        """Test loading default config when none provided."""
        repo = MockLanguageRepository()
        service = LanguageService(language_repo=repo)  # No config provided

        # Should still work even without config
        assert isinstance(service.language_config, dict)
