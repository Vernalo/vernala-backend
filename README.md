# vernala-backend

Async web scraper for African language dictionaries from webonary.org. Extracts English-to-African language translations and saves them as structured JSON files.

## Features

- Asynchronous scraping with aiohttp for concurrent requests
- Automatic pagination handling
- Built-in rate limiting to respect server resources
- Support for multiple African languages
- Organized JSON output by language and letter

## Installation

Requires Python 3.14+ and uv package manager.

```bash
# Install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate
```

## Usage

```bash
# Run the scraper
uv run src/main.py
```

Output is saved to `scraped_data/{language}/{letter}.json`

## Development

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check

# Format code
uv run ruff format
```

## Adding Languages

Add a new `LanguageConfig` entry to `LANGUAGES` in [src/scrapers/languages.py](src/scrapers/languages.py) with the language's webonary.org base URL.