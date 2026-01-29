HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT: int = 30
PAGE_DELAY: float = 1.0
LETTER_DELAY: float = 2.0

QUERY_TEMPLATE: str = "?letter={letter}&key=en&pagenr={page}&lang=en"
