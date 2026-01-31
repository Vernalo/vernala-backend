import argparse
import asyncio
import sys

import aiohttp

from core.logger import logger
from .scrapers.languages import LANGUAGES
from .scrapers.scraper import scrape_language, scrape_letter

EPILOG = f"""
Available languages:
  {', '.join(LANGUAGES.keys())}

Examples:
  python src/main.py --language ngiemboon --letter a
  python src/main.py --language ngiemboon --letter a b c
  python src/main.py --language ngiemboon --letter b --source-language fr
  python src/main.py --language bafut
  python src/main.py --language bafut --source-language fr
  python src/main.py  # Scrapes all languages (English by default)
"""
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape African language dictionaries from webonary.org",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
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
        nargs="+",
        help="Specific letter(s) to scrape (a-z). Can specify multiple letters. If not provided, scrapes all letters.",
        choices=list("abcdefghijklmnopqrstuvwxyz"),
    )
    parser.add_argument(
        "-s",
        "--source-language",
        type=str,
        default="en",
        choices=["en", "fr"],
        help="Source language for translations (default: en)",
    )
    return parser.parse_args()


async def main() -> None:
    try:
        args = parse_args()

        # If letter is specified but no language, error
        if args.letter and not args.language:
            logger.error("--letter requires --language to be specified")
            sys.exit(1)

        # If specific language and letter(s)
        if args.language and args.letter:
            language_config = LANGUAGES[args.language]
            source = "French" if args.source_language == "fr" else "English"
            letters_str = ", ".join([l.upper() for l in args.letter])
            logger.info(f"Scraping {language_config.name.upper()} - Letters {letters_str} ({source})")
            async with aiohttp.ClientSession() as session:
                for letter in args.letter:
                    await scrape_letter(session, language_config, letter, args.source_language)
        # If specific language but all letters
        elif args.language:
            language_config = LANGUAGES[args.language]
            source = "French" if args.source_language == "fr" else "English"
            logger.info(f"Scraping {language_config.name.upper()} - All letters ({source})")
            await scrape_language(language_config, args.source_language)
        # If no arguments, scrape all languages
        else:
            source = "French" if args.source_language == "fr" else "English"
            logger.info(f"Scraping all languages ({source})...")
            for language in LANGUAGES:
                language_config = LANGUAGES[language]
                logger.info(f"\nScraping {language_config.name.upper()}")
                await scrape_language(language_config, args.source_language)
    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
