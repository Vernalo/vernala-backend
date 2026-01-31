# vernala-backend

Async web scraper for African language dictionaries from webonary.org. Extracts English-to-African language translations and saves them as structured JSON files.

## Features

- Asynchronous scraping with aiohttp for concurrent requests
- Automatic pagination handling
- Built-in rate limiting to respect server resources
- Support for multiple African languages
- Organized JSON output by language and letter

## Installation

### Option 1: Local Installation

Requires Python 3.14+ and uv package manager.

```bash
# Install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate
```

### Option 2: Docker Installation

Requires Docker and Docker Compose.

```bash
# Build and start the API server
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop the server
docker-compose down
```

The API will be available at `http://localhost:8000`

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

## Migrating JSON files to SQLite

```bash
# Run the migration
uv run python src/db/migrate.py

# Query the database
sqlite3 vernala.db "SELECT * FROM words WHERE language_code = 'nnh' LIMIT 5"
```

## Translation API

### Starting the API Server

```bash
# Make sure you've created the database first
uv run python src/db/migrate.py

# Start the API server
uv run python -m app.main
```

The server will start at `http://localhost:8000`

### Interactive API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Supported Languages
```bash
curl http://localhost:8000/languages
```

#### Translate Words

**English → Ngiemboon:**
```bash
curl "http://localhost:8000/translate?source=en&target=nnh&word=abandon"
```

**French → Ngiemboon:**
```bash
curl "http://localhost:8000/translate?source=fr&target=nnh&word=abandonner"
```

**Ngiemboon → English (Reverse):**
```bash
curl "http://localhost:8000/translate?source=nnh&target=en&word=ńnyé2ńnyé"
```

**Ngiemboon → All Languages (Bidirectional):**
```bash
curl "http://localhost:8000/translate?source=nnh&word=ńnyé2ńnyé"
```

**Prefix Search (Autocomplete):**
```bash
curl "http://localhost:8000/translate?source=en&target=nnh&word=aban&match=prefix&limit=5"
```

**Query Parameters:**
- `source` (required): Source language code (e.g., "en", "fr", "nnh")
- `word` (required): Word to translate
- `target` (optional): Target language code; omit for all languages
- `match` (optional): Match type - "exact" (default), "prefix", or "contains"
- `limit` (optional): Max results (1-100, default 10)

**Language Codes:**
- `en` - English
- `fr` - French (Français)
- `nnh` - Ngiemboon
- `bfd` - Bafut (if scraped)

## Docker Deployment

The project includes Docker support for easy deployment.

### Quick Start

```bash
# 1. Make sure you have the SQLite database ready
# If you need to create it from scraped data:
uv run python src/db/migrate.py

# 2. Copy the database to the data directory
mkdir -p data
cp vernala.db data/

# 3. Start the container
docker-compose up -d

# 4. Check the API
curl http://localhost:8000/health
```

### Docker Commands

```bash
# Build the image
docker-compose build

# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Restart the container
docker-compose restart

# Stop and remove containers
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Docker Configuration

- **Port**: The API runs on port 8000 (mapped to host port 8000)
- **Database**: SQLite database is stored in `./data/vernala.db` (persisted via volume mount)
- **Health Check**: Automatic health checks every 30 seconds at `/health` endpoint
- **Auto-restart**: Container restarts automatically unless stopped manually

### Accessing the Database in Docker

```bash
# Connect to the container
docker exec -it vernala-api bash

# Run SQLite commands inside the container
sqlite3 /app/data/vernala.db "SELECT COUNT(*) FROM words"
```

### Optional: SQLite Web Viewer

Uncomment the `db-viewer` service in [docker-compose.yml](docker-compose.yml) to add a web-based SQLite browser at `http://localhost:8080`.

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