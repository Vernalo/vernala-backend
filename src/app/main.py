from fastapi import FastAPI
from app.routes.health_router import router as health_router
from app.routes.translate_router import router as translate_router
from app.routes.languages_router import router as languages_router

app = FastAPI(
    title="Vernala Translation API",
    version="1.0.0",
    description="""
    Vernala Translation API provides access to English/French translations of African languages.

    **Features:**
    - Translate English/French words to African languages (Ngiemboon, Bafut, etc.)
    - Reverse lookup African language words to find English/French meanings
    - Bidirectional lookup to see all translations for a word
    - Autocomplete support via prefix matching
    - Direct links to webonary.org for detailed word information

    **Available Endpoints:**
    - `/translate` - Translate words between languages
    - `/languages` - Get list of supported languages
    - `/health` - Health check endpoint
    """,
    contact={
        "name": "Vernala Project",
    },
    license_info={
        "name": "MIT",
    }
)

# Include routers
app.include_router(health_router)
app.include_router(translate_router)
app.include_router(languages_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
