"""Health check router for API endpoints."""

import sys
import platform
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from core.config.settings import settings
from services.inngest.client import inngest_client
from services.firecrawl.client import firecrawl_client

# Create router with proper tags
router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status with timestamp
    """
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


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint with comprehensive system information.
    
    Returns:
        Detailed health status including app info, service statuses, and system info
    """
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
        "firecrawl": await _check_firecrawl_service()
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
        overall_status = "degraded"
    
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