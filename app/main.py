import structlog
from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.handlers import setup_exception_handlers
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import SecurityHeadersMiddleware

# Setup structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
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

# 1. Setup Exception Handlers
setup_exception_handlers(app)

# 2. Add Middlewares (Executes Bottom to Top)

# Adds security headers to responses
app.add_middleware(SecurityHeadersMiddleware)

# Handles Request IDs, Logging, and Performance Timing
app.add_middleware(RequestContextMiddleware)

# Compresses responses larger than 1000 bytes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Handles Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Future: app.include_router(api_router, prefix=settings.API_V1_STR)