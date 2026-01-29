import asyncio
import aiohttp
from typing import List

from .config import PAGE_DELAY, LETTER_DELAY, QUERY_TEMPLATE
from .api import fetch_html
from .languages import LanguageConfig
from .models import DictionaryEntry
from .parser import extract_entries, extract_total_pages


async def scrape_letter(
    session: aiohttp.ClientSession,
    language: LanguageConfig,
    letter: str,
) -> List[DictionaryEntry]:
    results: List[DictionaryEntry] = []

    first_url = (
        f"{language.base_url}"
        f"{QUERY_TEMPLATE.format(letter=letter, page=1)}"
    )

    soup = await fetch_html(session, first_url)
    results.extend(extract_entries(soup))
    total_pages = extract_total_pages(soup)

    for page in range(2, total_pages + 1):
        await asyncio.sleep(PAGE_DELAY)
        url = (
            f"{language.base_url}"
            f"{QUERY_TEMPLATE.format(letter=letter, page=page)}"
        )
        soup = await fetch_html(session, url)
        results.extend(extract_entries(soup))

    return results


async def scrape_language(language: LanguageConfig) -> List[DictionaryEntry]:
    all_entries: List[DictionaryEntry] = []

    async with aiohttp.ClientSession() as session:
        for letter in "abcdefghijklmnopqrstuvwxyz":
            all_entries.extend(
                await scrape_letter(session, language, letter)
            )
            await asyncio.sleep(LETTER_DELAY)

    return all_entries
