"""Registration router for handling user registration requests."""

import logging
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from inngest import Event
from core.types.models import RegistrationRequest
from services.inngest.client import inngest_client

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
    """
    Register a new user and trigger background intelligence collection.
    
    Args:
        data: Registration request containing user data and URLs
        
    Returns:
        Immediate response with request_id and processing status
        
    Raises:
        HTTPException: If validation fails or Inngest event fails to send
    """
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
            
            logger.info(f"Successfully triggered background processing for {request_id}")
            
        except Exception as e:
            # Handle Inngest trigger failure
            logger.error(f"Failed to trigger background processing for {request_id}: {e}")
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
        logger.error(f"Unexpected error in registration endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to process registration request",
                "request_id": request_id if 'request_id' in locals() else None
            }
        ) 