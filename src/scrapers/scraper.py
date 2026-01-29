import asyncio
import aiohttp

from config import PAGE_DELAY, LETTER_DELAY, QUERY_TEMPLATE
from api import fetch_html
from languages import LanguageConfig
from parser import extract_entries, extract_total_pages
from serializer import save_letter_json


async def scrape_letter(
    session: aiohttp.ClientSession,
    language: LanguageConfig,
    letter: str,
) -> None:
    entries = []

    first_url = (
        f"{language.base_url}"
        f"{QUERY_TEMPLATE.format(letter=letter, page=1)}"
    )

    soup = await fetch_html(session, first_url)
    entries.extend(extract_entries(soup))
    total_pages = extract_total_pages(soup)

    for page in range(2, total_pages + 1):
        await asyncio.sleep(PAGE_DELAY)
        url = (
            f"{language.base_url}"
            f"{QUERY_TEMPLATE.format(letter=letter, page=page)}"
        )
        soup = await fetch_html(session, url)
        entries.extend(extract_entries(soup))

    save_letter_json(language.name, letter, entries)
    print(f"  ✓ {language.name.upper()} {letter.upper()}: {len(entries)} entries")


async def scrape_language(language: LanguageConfig) -> None:
    async with aiohttp.ClientSession() as session:
        for letter in "abcdefghijklmnopqrstuvwxyz":
            await scrape_letter(session, language, letter)
            await asyncio.sleep(LETTER_DELAY)
