import asyncio
import random
import aiohttp

from core.logger import logger
from .config import PAGE_DELAY, LETTER_DELAY, JITTER_MIN, JITTER_MAX, build_query_params
from .api import fetch_html
from .languages import LanguageConfig
from .parser import extract_entries, extract_total_pages
from .serializer import save_letter_json


async def scrape_letter(
    session: aiohttp.ClientSession,
    language: LanguageConfig,
    letter: str,
    source_lang: str = "en",
) -> None:
    entries = []

    # Build URL with correct path based on source language
    base_url = f"https://www.webonary.org/{language.name}/"
    path = language.french_path if source_lang == "fr" else language.english_path
    query = build_query_params(source_lang, letter, 1)
    first_url = f"{base_url}{path}{query}"

    soup = await fetch_html(session, first_url)
    entries.extend(extract_entries(soup, language.lang_code))
    total_pages = extract_total_pages(soup)

    for page in range(2, total_pages + 1):
        jitter = random.uniform(JITTER_MIN, JITTER_MAX)
        await asyncio.sleep(PAGE_DELAY + jitter)
        query = build_query_params(source_lang, letter, page)
        url = f"{base_url}{path}{query}"
        soup = await fetch_html(session, url)
        entries.extend(extract_entries(soup, language.lang_code))

    save_letter_json(language.name, letter, entries, source_lang)
    logger.info(f"  ✓ {language.name.upper()} {letter.upper()}: {len(entries)} entries")


async def scrape_language(language: LanguageConfig, source_lang: str = "en") -> None:
    async with aiohttp.ClientSession() as session:
        for letter in "abcdefghijklmnopqrstuvwxyz":
            await scrape_letter(session, language, letter, source_lang)
            jitter = random.uniform(JITTER_MIN, JITTER_MAX)
            await asyncio.sleep(LETTER_DELAY + jitter)
