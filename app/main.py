import structlog
from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager

# Setup structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CommerceHub API...")
    # Future: Initialize Redis connections, startup tasks here
    yield
    logger.info("Shutting down CommerceHub API...")
    # Future: Close connections

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Future: app.include_router(api_router, prefix=settings.API_V1_STR)