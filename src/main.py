import argparse
import asyncio
import sys

import aiohttp

from scrapers.languages import LANGUAGES
from scrapers.scraper import scrape_language, scrape_letter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape African language dictionaries from webonary.org",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available languages:
  {', '.join(LANGUAGES.keys())}

Examples:
  python src/main.py --language ngiemboon --letter a
  python src/main.py --language bafut
  python src/main.py  # Scrapes all languages
        """,
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        help="Language to scrape (e.g., ngiemboon, bafut)",
        choices=list(LANGUAGES.keys()),
    )
    parser.add_argument(
        "-t",
        "--letter",
        type=str,
        help="Specific letter to scrape (a-z). If not provided, scrapes all letters.",
        choices=list("abcdefghijklmnopqrstuvwxyz"),
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    # If letter is specified but no language, error
    if args.letter and not args.language:
        print("Error: --letter requires --language to be specified", file=sys.stderr)
        sys.exit(1)

    # If specific language and letter
    if args.language and args.letter:
        language_config = LANGUAGES[args.language]
        print(f"Scraping {language_config.name.upper()} - Letter {args.letter.upper()}")
        async with aiohttp.ClientSession() as session:
            await scrape_letter(session, language_config, args.letter)
    # If specific language but all letters
    elif args.language:
        language_config = LANGUAGES[args.language]
        print(f"Scraping {language_config.name.upper()} - All letters")
        await scrape_language(language_config)
    # If no arguments, scrape all languages
    else:
        print("Scraping all languages...")
        for language in LANGUAGES:
            language_config = LANGUAGES[language]
            print(f"\nScraping {language_config.name.upper()}")
            await scrape_language(language_config)


if __name__ == "__main__":
    asyncio.run(main())
