from bs4 import BeautifulSoup
from src.scrapers.parser import extract_total_pages


def test_extract_total_pages():
    html = """
    <div id="wp_page_numbers">
        <li class="page_info">Page 1 of 16</li>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    assert extract_total_pages(soup) == 16
