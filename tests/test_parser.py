from bs4 import BeautifulSoup
from src.scrapers.parser import extract_entries

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
    assert entries[0].ngiemboon[0].word == "mbʉ̀"
