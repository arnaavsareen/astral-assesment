# ==============================================================================
# main.py — FastAPI application entry point and configuration
# ==============================================================================
# Purpose: Main FastAPI application setup, middleware configuration, and router registration
# Sections: Imports, App Configuration, Middleware, Router Registration, Main Entry
# ==============================================================================

"""Main FastAPI application for astral-assessment."""

# Standard Library --------------------------------------------------------------
import logging
from contextlib import asynccontextmanager

# Third Party -------------------------------------------------------------------
import inngest
import inngest.fast_api
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core (App-wide) ---------------------------------------------------------------
from core.config.settings import settings
# Service layer imports
from services.inngest import inngest_client

# Internal (Current Module) -----------------------------------------------------
from api.routers import health, register
import services.inngest.functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    # Startup
    logger.info("Starting application", extra={"app_name": settings.app_name, "app_version": settings.app_version})
    
    # Verify Inngest client is initialized
    try:
        inngest_client = services.inngest.client.inngest_client
        logger.info("Inngest client initialized", extra={"app_id": inngest_client.app_id})
    except Exception as e:
        logger.error("Inngest client initialization failed", extra={"error": str(e)})
        raise
    
    # Verify settings are loaded
    logger.info("Application configuration loaded", extra={"environment": settings.environment, "app_name": settings.app_name, "app_version": settings.app_version})
    
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
    logger.error("Unhandled exception", extra={"error": str(exc)}, exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Include routers from api.routers
app.include_router(health.router)
app.include_router(register.router)

# Import Inngest functions to register them
# Serve the Inngest endpoint using the proper FastAPI integration
inngest.fast_api.serve(
    app, 
    inngest_client, 
    [services.inngest.functions.process_registration_task],
    serve_path="/api/inngest"  # Explicitly mount at /api/inngest as required
)


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