import asyncio

from scrapers.languages import LANGUAGES
from scrapers.scraper import scrape_language


async def main() -> None:
    for key in ("ngiemboon", "bahut", "duala"):
        language = LANGUAGES[key]
        print(f"Scraping {language.name.upper()}")
        await scrape_language(language)


if __name__ == "__main__":
    asyncio.run(main())
