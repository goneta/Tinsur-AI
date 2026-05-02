"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Explicitly load .env files from potential locations (Backend root and Project root)
# Navigate up from app/main.py
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_root)

load_dotenv(os.path.join(backend_root, ".env"))
load_dotenv(os.path.join(project_root, ".env"))

from app.core.config import settings
from app.core.operations_middleware import RequestCorrelationMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
# Force reload trigger - KYC Auth Fix
from app.core.database import Base, engine

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Ensure all models are registered
    import app.models
    # Create database tables
    Base.metadata.create_all(bind=engine)

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"DEBUG_CHECK: DATABASE_URL={settings.DATABASE_URL}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Application started successfully")
    try:
        yield
    finally:
        logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-tenant Insurance Management SaaS Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS (MUST be before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ] + settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestCorrelationMiddleware, header_name=settings.REQUEST_ID_HEADER)


# Mount uploads directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# app is in backend/app, uploads is in backend/uploads
# Actually, BASE_DIR here is backend/app.
# So uploads is .. / uploads
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
    
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Lightweight liveness check for load balancers and container supervisors."""
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/ready")
async def readiness_check():
    """Readiness probe with sanitized operational dependency evidence."""
    checks = {
        "database": "unknown",
        "dev_endpoints_enabled": bool(settings.ENABLE_DEV_ENDPOINTS),
    }

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover - defensive operational path
        checks["database"] = "error"
        logger.warning("readiness_database_check_failed", extra={"error_type": type(exc).__name__})
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": checks,
    }

@app.get("/test_main")
def test_main():
    return {"message": "ok main"}


# Include API routers
from app.api.v1.router import api_router
# from app.routers import admin_rbac  # Removed duplicated admin rbac

app.include_router(api_router, prefix="/api/v1")
# app.include_router(admin_rbac.router, prefix="/api/v1")  # Moved to api_router

# Register Chat Router
from app.api.v1.endpoints import chat
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
    # Reload trigger
    # Reload trigger 2
    # Reload trigger 3
    # Reload trigger 4
    # Reload trigger 5
    # Reload trigger 6
    # Reload trigger 7
    # Reload trigger 9
