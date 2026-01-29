import asyncio

from scrapers.languages import LANGUAGES
from scrapers.scraper import scrape_language


async def main() -> None:
    for language in LANGUAGES:
        language_config = LANGUAGES[language]
        print(f"Scraping {language_config.name.upper()}")
        await scrape_language(language_config)


if __name__ == "__main__":
    asyncio.run(main())
