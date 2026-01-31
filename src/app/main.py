from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health_router import router as health_router
from app.routes.translate_router import router as translate_router
from app.routes.languages_router import router as languages_router

app = FastAPI(
    title="Vernala Translation API",
    version="1.0.0",
    summary="Vernala Translation API provides access to English/French translations of African languages.",
    contact={
        "name": "Vernala Project",
    },
)

app.include_router(health_router)
app.include_router(translate_router)
app.include_router(languages_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
