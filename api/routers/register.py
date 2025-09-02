# ==============================================================================
# register.py — User registration and authentication endpoints
# ==============================================================================
# Purpose: Handle user registration, validation, and account creation workflows
# Sections: Imports, Registration Models, Validation Logic, API Endpoints
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
import uuid
from typing import Dict, Any, Optional

# Third Party -------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Depends
from inngest import Event
from pydantic import BaseModel, EmailStr

# Core (App-wide) ---------------------------------------------------------------
from core.types.models import RegistrationRequest
# Service layer imports
from services.inngest import inngest_client

# Configure logging
logger = logging.getLogger(__name__)

# Create router with proper tags
router = APIRouter(
    prefix="/register",
    tags=["registration"],
    responses={
        400: {"description": "Bad request - validation error"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    },
)


@router.post("")
async def register_user(data: RegistrationRequest) -> Dict[str, Any]:
    """Register user and trigger background intelligence collection."""
    try:
        # 1️⃣ Generate unique request ID ----
        request_id = str(uuid.uuid4())
        
        # 2️⃣ Validate registration data ----
        # Note: Pydantic validation happens automatically when data is parsed
        # Additional validation can be added here if needed
        
        # 3️⃣ Trigger Inngest background job ----
        # Send event to Inngest to trigger background processing
        try:
            await inngest_client.send(
                Event(
                    name="registration.received",
                    data={
                        "request_id": request_id,
                        "registration_data": data.model_dump()
                    }
                )
            )
            
            logger.info("Successfully triggered background processing", extra={"request_id": request_id})
            
        except Exception as e:
            # Handle Inngest trigger failure
            logger.error("Failed to trigger background processing", extra={"request_id": request_id, "error": str(e)})
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Background processing failed",
                    "message": "Failed to queue registration for processing",
                    "request_id": request_id
                }
            )
        
        # 4️⃣ Return immediate response ----
        return {
            "request_id": request_id,
            "status": "queued",
            "message": "Registration received and queued for processing"
        }
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation error",
                "message": str(e),
                "request_id": request_id if 'request_id' in locals() else None
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like the one we raise above)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        logger.error("Unexpected error in registration endpoint", extra={"error": str(e), "request_id": request_id if 'request_id' in locals() else None}, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to process registration request",
                "request_id": request_id if 'request_id' in locals() else None
            }
        ) 