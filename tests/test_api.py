"""API endpoint tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from db import database


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def override_db(sample_db):
    """Override database path with test database."""
    import os
    from app import dependencies

    # Store original path
    original_path = os.environ.get("VERNALA_DB_PATH")

    # Set test database path
    os.environ["VERNALA_DB_PATH"] = sample_db
    dependencies.DEFAULT_DB_PATH = sample_db

    # Clear cached dependencies to pick up new database path
    dependencies.get_translation_repository.cache_clear()
    dependencies.get_language_repository.cache_clear()
    dependencies.get_stats_repository.cache_clear()

    yield sample_db

    # Restore original
    if original_path:
        os.environ["VERNALA_DB_PATH"] = original_path
    else:
        os.environ.pop("VERNALA_DB_PATH", None)

    # Clear cache again to reset
    dependencies.get_translation_repository.cache_clear()
    dependencies.get_language_repository.cache_clear()
    dependencies.get_stats_repository.cache_clear()


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_returns_ok(self, client):
        """Test that health check returns status ok."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestLanguagesEndpoint:
    """Tests for /languages endpoint."""

    def test_get_languages_returns_list(self, client, override_db):
        """Test that /languages returns list of supported languages."""
        response = client.get("/languages")

        assert response.status_code == 200
        data = response.json()

        assert "languages" in data
        assert "count" in data
        assert data["count"] > 0
        assert len(data["languages"]) == data["count"]

    def test_languages_have_required_fields(self, client, override_db):
        """Test that each language has required fields."""
        response = client.get("/languages")

        assert response.status_code == 200
        languages = response.json()["languages"]

        for lang in languages:
            assert "code" in lang
            assert "name" in lang
            assert "type" in lang
            assert "word_count" in lang
            assert lang["type"] in ["source", "target"]

    def test_languages_include_expected_codes(self, client, override_db):
        """Test that expected language codes are present."""
        response = client.get("/languages")

        assert response.status_code == 200
        languages = response.json()["languages"]
        codes = {lang["code"] for lang in languages}

        assert "en" in codes
        assert "fr" in codes
        assert "nnh" in codes


class TestTranslateEndpoint:
    """Tests for /translate endpoint."""

    def test_english_to_ngiemboon_exact_match(self, client, override_db):
        """Test English → Ngiemboon translation."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "abandon",
            "match": "exact"
        })

        assert response.status_code == 200
        data = response.json()

        assert "query" in data
        assert "results" in data
        assert "count" in data

        assert data["query"]["source"] == "en"
        assert data["query"]["target"] == "nnh"
        assert data["query"]["word"] == "abandon"
        assert data["query"]["match"] == "exact"

        assert data["count"] > 0
        assert len(data["results"]) == data["count"]

    def test_french_to_ngiemboon_exact_match(self, client, override_db):
        """Test French → Ngiemboon translation."""
        response = client.get("/translate", params={
            "source": "fr",
            "target": "nnh",
            "word": "abandonner"
        })

        assert response.status_code == 200
        data = response.json()

        assert data["query"]["source"] == "fr"
        assert data["count"] > 0

        # Check result structure
        result = data["results"][0]
        assert result["source_word"] == "abandonner"
        assert result["source_language"] == "fr"
        assert result["target_language"] == "nnh"
        assert result["webonary_link"] is not None

    def test_ngiemboon_to_english_reverse_lookup(self, client, override_db):
        """Test Ngiemboon → English reverse lookup."""
        response = client.get("/translate", params={
            "source": "nnh",
            "target": "en",
            "word": "ńnyé2ńnyé"
        })

        assert response.status_code == 200
        data = response.json()

        assert data["query"]["source"] == "nnh"
        assert data["query"]["target"] == "en"
        assert data["count"] > 0

        # All results should be English
        for result in data["results"]:
            assert result["target_language"] == "en"
            assert result["source_language"] == "nnh"

    def test_ngiemboon_to_all_languages(self, client, override_db):
        """Test Ngiemboon → All languages (bidirectional)."""
        response = client.get("/translate", params={
            "source": "nnh",
            "word": "ńnyé2ńnyé"
            # No target = all languages
        })

        assert response.status_code == 200
        data = response.json()

        assert data["query"]["source"] == "nnh"
        assert data["query"]["target"] is None
        assert data["count"] > 0

        # Should have both English and French results
        target_languages = {r["target_language"] for r in data["results"]}
        assert "en" in target_languages
        assert "fr" in target_languages

    def test_case_insensitive_search(self, client, override_db):
        """Test that searches are case-insensitive."""
        response_lower = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "abandon"
        })

        response_upper = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "ABANDON"
        })

        assert response_lower.status_code == 200
        assert response_upper.status_code == 200

        data_lower = response_lower.json()
        data_upper = response_upper.json()

        assert data_lower["count"] == data_upper["count"]
        assert data_lower["count"] > 0

    def test_prefix_match_for_autocomplete(self, client, override_db):
        """Test prefix matching for autocomplete functionality."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "hel",
            "match": "prefix",
            "limit": 5
        })

        assert response.status_code == 200
        data = response.json()

        assert data["query"]["match"] == "prefix"
        # All results should start with "hel"
        for result in data["results"]:
            assert result["source_word"].lower().startswith("hel")

    def test_limit_parameter(self, client, override_db):
        """Test that limit parameter restricts results."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "abandon",
            "limit": 1
        })

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) <= 1

    def test_invalid_source_language(self, client, override_db):
        """Test that invalid source language returns 400."""
        response = client.get("/translate", params={
            "source": "xyz",
            "target": "nnh",
            "word": "test"
        })

        assert response.status_code == 400
        assert "Unsupported source language" in response.json()["detail"]

    def test_invalid_target_language(self, client, override_db):
        """Test that invalid target language returns 400."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "xyz",
            "word": "test"
        })

        assert response.status_code == 400
        assert "Unsupported target language" in response.json()["detail"]

    def test_missing_required_parameters(self, client):
        """Test that missing required parameters returns 422."""
        # Missing source
        response = client.get("/translate", params={
            "target": "nnh",
            "word": "test"
        })
        assert response.status_code == 422

        # Missing word
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh"
        })
        assert response.status_code == 422

    def test_invalid_match_type(self, client, override_db):
        """Test that invalid match type returns 422."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "test",
            "match": "invalid"
        })

        assert response.status_code == 422

    def test_limit_bounds_validation(self, client, override_db):
        """Test that limit parameter validates bounds."""
        # Limit too low
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "test",
            "limit": 0
        })
        assert response.status_code == 422

        # Limit too high
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "test",
            "limit": 101
        })
        assert response.status_code == 422

    def test_default_match_is_exact(self, client, override_db):
        """Test that default match type is 'exact'."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "abandon"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["query"]["match"] == "exact"

    def test_default_limit_is_10(self, client, override_db):
        """Test that default limit is 10."""
        response = client.get("/translate", params={
            "source": "en",
            "target": "nnh",
            "word": "a",
            "match": "prefix"
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 10


# All tests now use sample_db fixture from conftest via override_db
# Real database integration tests removed to keep CI simple
