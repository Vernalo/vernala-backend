import asyncio
from scrapers.scraper import scrape_all_letters
from scrapers.serializer import save_json


async def main() -> None:
    entries = await scrape_all_letters()
    save_json("complete_dictionary.json", entries)
    print(f"Scraped {len(entries)} entries")


if __name__ == "__main__":
    asyncio.run(main())
