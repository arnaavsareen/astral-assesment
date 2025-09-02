# ==============================================================================
# health.py — Health check and system status endpoints
# ==============================================================================
# Purpose: Provide health check endpoints for monitoring and system status verification
# Sections: Imports, Health Check Endpoints, Status Validation
# ==============================================================================

# Standard Library --------------------------------------------------------------
import platform
import sys
from datetime import datetime
from typing import Dict, Any

# Third Party -------------------------------------------------------------------
from fastapi import APIRouter, HTTPException

# Core (App-wide) ---------------------------------------------------------------
from core.config.settings import settings
# Core client imports
from core.clients.firecrawl import firecrawl_client
from core.clients.openai import ai_client
from services.inngest import inngest_client
from domains.intelligence_collection.linkedin import analyze_linkedin_profile

# Create router with proper tags
router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint returning status and timestamp."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


async def _check_inngest_service() -> Dict[str, Any]:
    """Check Inngest service availability."""
    try:
        # Check if Inngest client is properly initialized
        app_id = inngest_client.app_id
        return {
            "status": "healthy",
            "app_id": app_id,
            "details": "Inngest client initialized successfully"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Inngest client initialization failed"
        }


async def _check_firecrawl_service() -> Dict[str, Any]:
    """Check Firecrawl service availability."""
    try:
        # Check if Firecrawl client is properly initialized
        has_api_key = bool(firecrawl_client.api_key and firecrawl_client.api_key.strip())
        return {
            "status": "healthy" if has_api_key else "limited",
            "has_api_key": has_api_key,
            "details": "Firecrawl client initialized successfully" if has_api_key else "Firecrawl client initialized (no API key - using mock responses)"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Firecrawl client initialization failed"
        }


async def _check_linkedin_service() -> Dict[str, Any]:
    """Check LinkedIn service availability."""
    try:
        # Check if LinkedIn service is properly initialized
        from core.clients.scrapingdog import ScrapingDogClient
        client = ScrapingDogClient()
        has_api_key = client._has_api_key()
        return {
            "status": "healthy" if has_api_key else "limited",
            "has_api_key": has_api_key,
            "details": "LinkedIn service initialized successfully" if has_api_key else "LinkedIn service initialized (no API key - limited functionality)"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "LinkedIn service initialization failed"
        }


async def _check_ai_service() -> Dict[str, Any]:
    """Check AI service availability."""
    try:
        # Check if AI client is properly initialized
        has_api_key = ai_client._has_api_key()
        return {
            "status": "healthy" if has_api_key else "limited",
            "has_api_key": has_api_key,
            "details": "AI service initialized successfully" if has_api_key else "AI service initialized (no API key - limited functionality)"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "AI service initialization failed"
        }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with comprehensive system information."""
    # 1️⃣ Basic app information ----
    app_info = {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # 2️⃣ Service status checks ----
    service_statuses = {
        "inngest": await _check_inngest_service(),
        "firecrawl": await _check_firecrawl_service(),
        "linkedin": await _check_linkedin_service(),
        "ai": await _check_ai_service()
    }
    
    # 3️⃣ System information ----
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_implementation": platform.python_implementation()
    }
    
    # 4️⃣ Overall health status ----
    all_services = list(service_statuses.values())
    healthy_services = [s for s in all_services if s["status"] == "healthy"]
    limited_services = [s for s in all_services if s["status"] == "limited"]
    unhealthy_services = [s for s in all_services if s["status"] == "unhealthy"]
    
    overall_status = "healthy"
    if unhealthy_services:
        overall_status = "unhealthy"
    elif limited_services:
        overall_status = "limited"
    
    return {
        "status": overall_status,
        "app_info": app_info,
        "services": service_statuses,
        "system_info": system_info,
        "summary": {
            "total_services": len(all_services),
            "healthy_services": len(healthy_services),
            "limited_services": len(limited_services),
            "unhealthy_services": len(unhealthy_services)
        }
    } 