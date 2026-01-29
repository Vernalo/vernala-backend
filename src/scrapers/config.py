HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT: int = 30
PAGE_DELAY: float = 3.0  # Base delay between pages (seconds)
LETTER_DELAY: float = 8.0  # Base delay between letters (seconds)
JITTER_MIN: float = 0.5  # Minimum random jitter to add (seconds)
JITTER_MAX: float = 2.0  # Maximum random jitter to add (seconds)
MAX_RETRIES: int = 3  # Maximum number of retries for failed requests
RETRY_BASE_DELAY: float = 5.0  # Base delay for exponential backoff (seconds)

QUERY_TEMPLATE: str = "?letter={letter}&key=en&pagenr={page}&lang=en"


def build_query_params(source_lang: str, letter: str, page: int) -> str:
    """Build query parameters for webonary.org URLs.

    Args:
        source_lang: Source language code ('en' or 'fr')
        letter: Letter to scrape (a-z)
        page: Page number

    Returns:
        Query string like "?letter=b&key=fr&pagenr=1&lang=fr"
    """
    return f"?letter={letter}&key={source_lang}&pagenr={page}&lang={source_lang}"
