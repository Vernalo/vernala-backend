import asyncio
import aiohttp
from typing import List

from .config import BASE_URL, PAGE_DELAY, LETTER_DELAY
from .api import fetch_html
from .models import DictionaryEntry
from .parser import extract_entries, extract_total_pages


async def scrape_letter(
    session: aiohttp.ClientSession,
    letter: str,
) -> List[DictionaryEntry]:
    entries: List[DictionaryEntry] = []

    first_url = BASE_URL.format(letter=letter, page=1)
    soup = await fetch_html(session, first_url)

    entries.extend(extract_entries(soup))
    total_pages = extract_total_pages(soup)

    for page in range(2, total_pages + 1):
        await asyncio.sleep(PAGE_DELAY)
        url = BASE_URL.format(letter=letter, page=page)
        soup = await fetch_html(session, url)
        entries.extend(extract_entries(soup))

    return entries


async def scrape_all_letters() -> List[DictionaryEntry]:
    all_entries: List[DictionaryEntry] = []

    async with aiohttp.ClientSession() as session:
        for letter in "abcdefghijklmnopqrstuvwxyz":
            all_entries.extend(await scrape_letter(session, letter))
            await asyncio.sleep(LETTER_DELAY)

    return all_entries
