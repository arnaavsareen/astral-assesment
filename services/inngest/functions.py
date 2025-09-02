# ==============================================================================
# functions.py — Inngest workflow function definitions
# ==============================================================================
# Purpose: Define and configure Inngest workflow functions for background processing
# Sections: Imports, Function Definitions, Workflow Configuration, Error Handling
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
from typing import Any, Dict, Optional

# Third Party -------------------------------------------------------------------
from inngest import TriggerEvent

# Core (App-wide) ---------------------------------------------------------------
from core.types.models import RegistrationRequest
from core.utils.json_handler import save_analysis
from domains.intelligence_collection import process_registration
from services.inngest import inngest_client

# Configure logging
logger = logging.getLogger(__name__)


@inngest_client.create_function(
    fn_id="process-registration",
    trigger=TriggerEvent(event="registration.received")
)
async def process_registration_task(ctx):
    """Process registration request and perform business intelligence analysis."""
    request_id = None  # Initialize request_id at function start
    
    try:
        # 1️⃣ Extract and validate registration data ----
        # Inngest context structure: ctx.event.data contains the event payload
        event_data = getattr(ctx.event, 'data', {})
        if not event_data:
            # Try alternative access patterns
            event_data = getattr(ctx.event, 'body', {})
        
        request_id = event_data.get("request_id") if isinstance(event_data, dict) else None
        registration_data = event_data.get("registration_data", {}) if isinstance(event_data, dict) else {}
        
        if not request_id:
            raise ValueError("Missing request_id in event data")
        
        if not registration_data:
            raise ValueError("Missing registration_data in event data")
        
        logger.info("Processing registration request", extra={"request_id": request_id})
        
        # 2️⃣ Create RegistrationRequest from event data ----
        try:
            registration_request = RegistrationRequest(**registration_data)
        except Exception as e:
            logger.error("Invalid registration data", extra={"request_id": request_id, "error": str(e)})
            raise ValueError(f"Invalid registration data: {str(e)}")
        
        # 3️⃣ Process registration using domain logic ----
        logger.info("Starting intelligence collection", extra={"request_id": request_id})
        analysis_result = await process_registration(registration_request)
        
        # Note: process_registration already calls save_analysis internally,
        # so we don't need to save again here
        
        # 4️⃣ Return completion status ----
        logger.info("Successfully completed processing", extra={"request_id": request_id})
        
        return {
            "status": "completed",
            "request_id": request_id,
            "event_id": getattr(ctx.event, 'id', 'unknown'),
            "analysis_result": {
                "has_linkedin_analysis": analysis_result.linkedin_analysis is not None,
                "has_website_analysis": analysis_result.website_analysis is not None,
                "timestamp": analysis_result.timestamp.isoformat()
            },
            "message": "Registration processing completed successfully"
        }
        
    except ValueError as e:
        # Validation errors - don't retry, log and fail
        logger.error("Validation error for request", extra={"request_id": request_id, "error": str(e)})
        raise
        
    except Exception as e:
        # Unexpected errors - Inngest will retry automatically
        logger.error("Unexpected error processing registration", extra={"request_id": request_id, "error": str(e)}, exc_info=True)
        raise 