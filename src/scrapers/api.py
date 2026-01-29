import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .config import HEADERS, REQUEST_TIMEOUT


async def fetch_html(session: ClientSession, url: str) -> BeautifulSoup:
    async with session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT) as resp:
        resp.raise_for_status()
        html = await resp.text()
        return BeautifulSoup(html, "html.parser")
