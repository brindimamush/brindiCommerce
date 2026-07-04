import structlog
from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.redis import redis_manager
from app.modules.audit.service import log_audit_event
from app.events.bus import event_bus
from app.core.handlers import setup_exception_handlers
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.store.router import router as store_router
from app.modules.audit.router import router as audit_router
from app.modules.dashboard.router import router as dashboard_router
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
    event_bus.subscribe("audit.record", log_audit_event)
    logger.info("Starting CommerceHub API...")
    # Future: Initialize Redis connections, startup tasks here
    await redis_manager.connect()
    logger.info("Redis connected.")
    yield
    logger.info("Shutting down CommerceHub API...")
    # Future: Close connections

    # Disconnect Redis
    await redis_manager.disconnect()
    logger.info("Redis disconnected.")

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

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(store_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Future: app.include_router(api_router, prefix=settings.API_V1_STR)