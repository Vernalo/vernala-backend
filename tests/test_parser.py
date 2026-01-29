from bs4 import BeautifulSoup
from scrapers.parser import extract_entries, extract_total_pages

def test_extract_entries():
    html = """
    <div class="post">
      <span class="reversalform">dog</span>
      <span class="sensesr">
        <span class="headword">
          <span lang="nnh"><a>mbʉ̀</a></span>
          <a href="/word/mbu"></a>
        </span>
      </span>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    entries = extract_entries(soup)

    assert len(entries) == 1
    assert entries[0].english == "dog"
    assert entries[0].vernacular[0].word == "mbʉ̀"

def test_extract_total_pages():
    html = """
    <div id="wp_page_numbers">
        <li class="page_info">Page 1 of 16</li>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    assert extract_total_pages(soup) == 16
