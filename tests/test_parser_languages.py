from bs4 import BeautifulSoup
import pytest

from scrapers.parser import extract_translations, extract_entries


class TestMultipleLanguageCodes:

    def test_ngiemboon_language_code(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ńnyé</a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")

        assert len(translations) == 1
        assert translations[0].word == "ńnyé"

    def test_bafut_language_code(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="bfd">
                        <a href="https://example.com/word1">àbùŋ</a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "bfd")

        assert len(translations) == 1
        assert translations[0].word == "àbùŋ"

    def test_wrong_language_code_returns_empty(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ńnyé</a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        # Using bfd code for nnh content
        translations = extract_translations(entry, "bfd")

        assert translations == []

    @pytest.mark.parametrize("lang_code,expected_word", [
        ("nnh", "ńnyé"),
        ("bfd", "àbùŋ"),
        ("xyz", "testword"),
    ])
    def test_parametrized_language_codes(self, lang_code, expected_word):
        html = f"""
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="{lang_code}">
                        <a href="https://example.com/word1">{expected_word}</a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, lang_code)

        assert len(translations) == 1
        assert translations[0].word == expected_word


class TestEntriesWithDifferentLanguages:

    def test_ngiemboon_entries(self):
        html = """
        <div class="post">
            <span class="reversalform">abandon</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ńnyé</a>
                    </span>
                </span>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")

        assert len(entries) == 1
        assert entries[0].source_word == "abandon"
        assert entries[0].translations[0].word == "ńnyé"

    def test_bafut_entries(self):
        html = """
        <div class="post">
            <span class="reversalform">abandon</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="bfd">
                        <a href="https://example.com/word1">àbùŋ</a>
                    </span>
                </span>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "bfd")

        assert len(entries) == 1
        assert entries[0].source_word == "abandon"
        assert entries[0].translations[0].word == "àbùŋ"

    def test_multiple_entries_same_language(self):
        html = """
        <div class="post">
            <span class="reversalform">abandon</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ńnyé</a>
                    </span>
                </span>
            </span>
        </div>
        <div class="post">
            <span class="reversalform">above</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word2">ndùm</a>
                    </span>
                </span>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")

        assert len(entries) == 2
        assert entries[0].translations[0].word == "ńnyé"
        assert entries[1].translations[0].word == "ndùm"


class TestFrenchSourceLanguage:


    def test_french_to_ngiemboon(self):
        html = """
        <div class="post">
            <span class="reversalform">abandonner</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ńnyé</a>
                    </span>
                </span>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")

        assert len(entries) == 1
        assert entries[0].source_word == "abandonner"
        assert entries[0].translations[0].word == "ńnyé"

    def test_french_special_characters(self):
        html = """
        <div class="post">
            <span class="reversalform">être</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ŋwa</a>
                    </span>
                </span>
            </span>
        </div>
        <div class="post">
            <span class="reversalform">école</span>
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word2">kùlé</a>
                    </span>
                </span>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")

        assert len(entries) == 2
        assert entries[0].source_word == "être"
        assert entries[1].source_word == "école"

    def test_french_accented_words(self):
        """Should preserve French accents in source words"""
        test_words = ["café", "naïve", "résumé", "château", "œuvre"]

        for word in test_words:
            html = f"""
            <div class="post">
                <span class="reversalform">{word}</span>
                <span class="sensesr">
                    <span class="headword">
                        <span lang="nnh">
                            <a href="https://example.com/word">test</a>
                        </span>
                    </span>
                </span>
            </div>
            """
            soup = BeautifulSoup(html, 'html.parser')
            entries = extract_entries(soup, "nnh")

            assert len(entries) == 1
            assert entries[0].source_word == word
