"""Main FastAPI application for astral-assessment."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import inngest
import inngest.fast_api
from core.config.settings import settings
from services.inngest.client import inngest_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Verify Inngest client is initialized
    try:
        logger.info(f"Inngest app ID: {inngest_client.app_id}")
        logger.info("✅ Inngest client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Inngest client initialization failed: {e}")
        raise
    
    # Verify settings are loaded
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"App name: {settings.app_name}")
    logger.info(f"App version: {settings.app_version}")
    
    logger.info("🚀 Application startup completed successfully")
    
    yield  # Application runs here
    
    # Shutdown (if needed)
    logger.info("🛑 Application shutting down")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Business intelligence collection and analysis platform",
    lifespan=lifespan
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions globally."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Include routers from api.routers
from api.routers import health, register

# Include routers
app.include_router(health.router)
app.include_router(register.router)

# Import Inngest functions to register them
import services.inngest.functions

# Serve the Inngest endpoint using the proper FastAPI integration
inngest.fast_api.serve(app, inngest_client, [services.inngest.functions.process_registration_task])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health"
    } 