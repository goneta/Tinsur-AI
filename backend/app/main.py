"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.core.config import settings
# Force reload trigger - KYC Auth Fix
from app.core.database import Base, engine

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-tenant Insurance Management SaaS Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# app is in backend/app, uploads is in backend/uploads
# Actually, BASE_DIR here is backend/app.
# So uploads is .. / uploads
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
    
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application")


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
    """Health check endpoint."""
    return {"status": "healthy"}


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
