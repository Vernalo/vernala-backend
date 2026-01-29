import asyncio
from aiohttp import ClientSession, ClientResponseError, ClientTimeout
from bs4 import BeautifulSoup

from core.logger import logger
from .config import HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BASE_DELAY


async def fetch_html(session: ClientSession, url: str) -> BeautifulSoup:
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url, headers=HEADERS, timeout=timeout) as resp:
                resp.raise_for_status()
                html = await resp.text()
                return BeautifulSoup(html, "html.parser")
        except ClientResponseError as e:
            if e.status == 503 and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning(f"  ⚠ Rate limited (503), retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(delay)
            else:
                raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning(f"  ⚠ Request failed: {e}, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(delay)
            else:
                raise

    raise Exception(f"Failed to fetch {url} after {MAX_RETRIES} attempts")
