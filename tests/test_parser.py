from bs4 import BeautifulSoup

from scrapers.parser import extract_total_pages, extract_translations, extract_entries

class TestExtractTotalPages:
    
    def test_single_page_no_pagination(self):
        html = """
        <html>
            <body>
                <div>No pagination here</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 1
    
    def test_single_page_with_pagination(self):
        html = """
        <div id="wp_page_numbers">
            <ul>
                <li class="page_info">Page 1 of 1</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 1
    
    def test_multiple_pages(self):
        html = """
        <div id="wp_page_numbers">
            <ul>
                <li class="page_info">Page 1 of 16</li>
                <li><a href="?page=2">2</a></li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 16
    
    def test_current_page_not_first(self):
        html = """
        <div id="wp_page_numbers">
            <ul>
                <li class="page_info">Page 5 of 20</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 20
    
    def test_pagination_without_page_info(self):
        html = """
        <div id="wp_page_numbers">
            <ul>
                <li><a href="?page=1">1</a></li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 1
    
    def test_malformed_page_info(self):
        html = """
        <div id="wp_page_numbers">
            <ul>
                <li class="page_info">Some random text</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 1
    
    def test_large_page_count(self):
        html = """
        <div id="wp_page_numbers">
            <ul>
                <li class="page_info">Page 1 of 999</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_total_pages(soup) == 999

class TestExtractTranslations:
    
    def test_single_translation(self):
        html = """
        <div class="post">
            <span class="sensesrs">
                <span class="sensecontent">
                    <span class="sensesr">
                        <span class="headword">
                            <span lang="nnh">
                                <a href="https://example.com/word1">ńnyé</a>
                            </span>
                        </span>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert len(translations) == 1
        assert translations[0].word == "ńnyé"
        assert translations[0].link == "https://example.com/word1"
    
    def test_multiple_translations(self):
        html = """
        <div class="post">
            <span class="sensesrs">
                <span class="sensecontent">
                    <span class="sensesr">
                        <span class="headword">
                            <span lang="nnh">
                                <a href="https://example.com/word1">ńnyé</a>
                            </span>
                        </span>
                    </span>
                </span>
                <span class="sensecontent">
                    <span class="sensesr">
                        <span class="headword">
                            <span lang="nnh">
                                <a href="https://example.com/word2">ńkʉ́e</a>
                            </span>
                        </span>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert len(translations) == 2
        assert translations[0].word == "ńnyé"
        assert translations[1].word == "ńkʉ́e"
    
    def test_translation_with_superscript(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word1">ńnyé</a>
                    </span>
                    <span lang="fr" style="font-weight:bold;">
                        <a href="https://example.com/word1">2</a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert len(translations) == 1
        assert translations[0].word == "ńnyé"
    
    def test_no_translations(self):
        html = """
        <div class="post">
            <span class="reversalform">English word</span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert translations == []
    
    def test_translation_without_link(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">ńnyé</span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert translations == []
    
    def test_translation_without_headword(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <a href="https://example.com/word1">ńnyé</a>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert translations == []
    
    def test_empty_word_or_link(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href=""></a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert translations == []
    
    def test_special_characters_in_word(self):
        html = """
        <div class="post">
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word">ńẅɛ́ʉ̀ŋ</a>
                    </span>
                </span>
            </span>
        </div>
        """
        entry = BeautifulSoup(html, 'html.parser').find('div', class_='post')
        translations = extract_translations(entry, "nnh")
        
        assert len(translations) == 1
        assert translations[0].word == "ńẅɛ́ʉ̀ŋ"

class TestExtractEntries:
    
    def test_single_entry(self):
        html = """
        <div class="post">
            <span class="reversalform">
                <span lang="en">abandon</span>
            </span>
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
        assert len(entries[0].translations) == 1
        assert entries[0].translations[0].word == "ńnyé"
    
    def test_multiple_entries(self):
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
        assert entries[0].source_word == "abandon"
        assert entries[1].source_word == "above"
    
    def test_entry_with_multiple_translations(self):
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
            <span class="sensesr">
                <span class="headword">
                    <span lang="nnh">
                        <a href="https://example.com/word2">ńkʉ́e</a>
                    </span>
                </span>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")
        
        assert len(entries) == 1
        assert len(entries[0].translations) == 2
    
    def test_no_entries(self):
        html = """
        <html>
            <body>
                <div>No posts here</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")
        
        assert entries == []
    
    def test_post_without_reversalform(self):
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
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")
        
        assert entries == []
    
    def test_post_without_translations(self):
        html = """
        <div class="post">
            <span class="reversalform">abandon</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")
        
        assert entries == []
    
    def test_empty_english_word(self):
        html = """
        <div class="post">
            <span class="reversalform"></span>
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
        
        assert entries == []
    
    def test_whitespace_handling(self):
        html = """
        <div class="post">
            <span class="reversalform">
                
                abandon
                
            </span>
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
    
    def test_real_world_example(self):
        html = """
        <div class="post">
            <div class="reversalindexentry" id="g0ec444a8-06f6-48f7-93e8-fcb27ac0c82d">
                <span class="reversalform">
                    <span lang="en">abandon</span>
                </span>
                <span class="sensesrs">
                    <span class="sensecontent">
                        <span class="sensesr" entryguid="g8a5c2a0f-0af2-41ee-90a1-f06f2afa8fc9">
                            <span class="headword">
                                <span lang="nnh">
                                    <span lang="nnh">
                                        <a href="https://www.webonary.org/ngiemboon/g8a5c2a0f-0af2-41ee-90a1-f06f2afa8fc9?lang=en">ńnyé</a>
                                    </span>
                                    <span lang="fr" style="font-weight:bold;font-size:58%;">
                                        <a href="https://www.webonary.org/ngiemboon/g8a5c2a0f-0af2-41ee-90a1-f06f2afa8fc9?lang=en">2</a>
                                    </span>
                                </span>
                            </span>
                            <span class="morphosyntaxanalysis">
                                <span class="mlpartofspeech">
                                    <span lang="en">v.t</span>
                                </span>
                            </span>
                        </span>
                    </span>
                    <span class="sensecontent">
                        <span class="sensesr" entryguid="g09949799-9d87-4613-9bf8-4bd5b9ca3bce">
                            <span class="headword">
                                <span lang="nnh">
                                    <a href="https://www.webonary.org/ngiemboon/g09949799-9d87-4613-9bf8-4bd5b9ca3bce?lang=en">ńkʉ́e</a>
                                </span>
                            </span>
                        </span>
                    </span>
                </span>
            </div>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        entries = extract_entries(soup, "nnh")
        
        assert len(entries) == 1
        assert entries[0].source_word == "abandon"
        assert len(entries[0].translations) == 2
        assert entries[0].translations[0].word == "ńnyé2ńnyé"
        assert entries[0].translations[1].word == "ńkʉ́e"

class TestIntegration:
    
    def test_full_page_extraction(self):
        html = """
        <html>
            <body>
                <div id="wp_page_numbers">
                    <ul>
                        <li class="page_info">Page 1 of 16</li>
                    </ul>
                </div>
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
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract pagination
        total_pages = extract_total_pages(soup)
        assert total_pages == 16

        # Extract entries
        entries = extract_entries(soup, "nnh")
        assert len(entries) == 2
        assert entries[0].source_word == "abandon"
        assert entries[1].source_word == "above"

