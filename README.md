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
# Run the scraper (scrapes all languages)
uv run src/main.py

# Scrape just letter 'a' for Ngiemboon
uv run src/main.py --language ngiemboon --letter a

# Scrape multiple letters for Ngiemboon
uv run src/main.py --language ngiemboon --letter a b c

# Scrape all letters for Bafut
uv run src/main.py --language bafut

# Scrape with French as source language
uv run src/main.py --language ngiemboon --letter a b --source-language fr

# Show help and available languages
uv run src/main.py --help

# Run the FastAPI server
uv run uvicorn src.app.main:app --reload
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

## Marimo Notebooks

```bash
# Run marimo
uv run marimo explore notebooks/exploration.py

# Edit the notebook in your browser (the notebook will be saved automatically)
uv run edit notebooks/exploration.py

# Stop marimo
# Press Ctrl+C in the terminal

```


## Adding Languages

Add a new `LanguageConfig` entry to `LANGUAGES` in [src/scrapers/languages.py](src/scrapers/languages.py) with the language's webonary.org base URL.

## Troubleshooting

If you encounter issues with marimo, try the following:

```bash
# Restart marimo
uv run marimo stop
uv run marimo explore notebooks/exploration.py
```

If you encounter import errors, try reinstalling the package:

```bash
uv pip install -e .
```

## Data sources

- [Ngiemboon](https://www.webonary.org/ngiemboon/browse/browse-vernacular-english/?lang=en)
- [Bafut](https://www.webonary.org/bafut/)