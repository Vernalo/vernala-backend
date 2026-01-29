"""
Unit tests for URL building functionality
"""
from scrapers.config import build_query_params
from scrapers.languages import LANGUAGES


class TestBuildQueryParams:
    """Test suite for build_query_params function"""

    def test_english_query_params(self):
        """Should build correct query params for English"""
        result = build_query_params("en", "a", 1)
        assert result == "?letter=a&key=en&pagenr=1&lang=en"

    def test_french_query_params(self):
        """Should build correct query params for French"""
        result = build_query_params("fr", "b", 1)
        assert result == "?letter=b&key=fr&pagenr=1&lang=fr"

    def test_different_letters(self):
        """Should handle different letters correctly"""
        result_a = build_query_params("en", "a", 1)
        result_z = build_query_params("en", "z", 1)
        assert "letter=a" in result_a
        assert "letter=z" in result_z

    def test_different_pages(self):
        """Should handle different page numbers correctly"""
        result_1 = build_query_params("en", "a", 1)
        result_10 = build_query_params("en", "a", 10)
        assert "pagenr=1" in result_1
        assert "pagenr=10" in result_10


class TestLanguageConfig:
    """Test suite for language configuration"""

    def test_ngiemboon_config(self):
        """Should have correct Ngiemboon configuration"""
        config = LANGUAGES["ngiemboon"]
        assert config.name == "ngiemboon"
        assert config.lang_code == "nnh"
        assert config.english_path == "browse/browse-english/"
        assert config.french_path == "browse/francais/"

    def test_bafut_config(self):
        """Should have correct Bafut configuration"""
        config = LANGUAGES["bafut"]
        assert config.name == "bafut"
        assert config.lang_code == "bfd"
        assert config.english_path == "browse/browse-english/"
        assert config.french_path == "browse/francais/"

    def test_all_languages_have_required_fields(self):
        """Should verify all languages have required configuration fields"""
        for lang_key, config in LANGUAGES.items():
            assert config.name, f"{lang_key} missing name"
            assert config.lang_code, f"{lang_key} missing lang_code"
            assert config.english_path, f"{lang_key} missing english_path"
            assert config.french_path, f"{lang_key} missing french_path"


class TestURLConstruction:
    """Test suite for full URL construction"""

    def test_english_url_structure(self):
        """Should construct correct English URL"""
        config = LANGUAGES["ngiemboon"]
        base_url = f"https://www.webonary.org/{config.name}/"
        path = config.english_path
        query = build_query_params("en", "a", 1)
        full_url = f"{base_url}{path}{query}"

        assert full_url == "https://www.webonary.org/ngiemboon/browse/browse-english/?letter=a&key=en&pagenr=1&lang=en"

    def test_french_url_structure(self):
        """Should construct correct French URL"""
        config = LANGUAGES["ngiemboon"]
        base_url = f"https://www.webonary.org/{config.name}/"
        path = config.french_path
        query = build_query_params("fr", "b", 1)
        full_url = f"{base_url}{path}{query}"

        assert full_url == "https://www.webonary.org/ngiemboon/browse/francais/?letter=b&key=fr&pagenr=1&lang=fr"

    def test_url_with_pagination(self):
        """Should construct correct URL with pagination"""
        config = LANGUAGES["ngiemboon"]
        base_url = f"https://www.webonary.org/{config.name}/"
        path = config.english_path
        query = build_query_params("en", "a", 5)
        full_url = f"{base_url}{path}{query}"

        assert "pagenr=5" in full_url

    def test_bafut_url_construction(self):
        """Should construct correct URL for Bafut language"""
        config = LANGUAGES["bafut"]
        base_url = f"https://www.webonary.org/{config.name}/"
        path = config.french_path
        query = build_query_params("fr", "c", 2)
        full_url = f"{base_url}{path}{query}"

        assert full_url == "https://www.webonary.org/bafut/browse/francais/?letter=c&key=fr&pagenr=2&lang=fr"
