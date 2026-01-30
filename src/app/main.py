from fastapi import FastAPI
from src.app.routes.health_router import router as health_router

app = FastAPI(
    title="Vernala Backend",
    version="0.1.0",
)

app.include_router(health_router)
