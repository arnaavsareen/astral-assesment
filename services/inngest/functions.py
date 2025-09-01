"""Inngest background job functions for registration processing."""

import logging
from typing import Dict, Any
from inngest import TriggerEvent
from services.inngest.client import inngest_client

# Domain imports
from domains.intelligence_collection import process_registration
from core.utils.json_handler import save_analysis
from core.types.models import RegistrationRequest

# Configure logging
logger = logging.getLogger(__name__)


@inngest_client.create_function(
    fn_id="process-registration",
    trigger=TriggerEvent(event="registration.received")
)
async def process_registration_task(step, event):
    """
    Process registration request and perform comprehensive business intelligence analysis.
    
    This function demonstrates why Inngest is valuable for this use case:
    
    1. **Reliability**: Built-in retries handle transient failures (API timeouts, network issues)
    2. **Observability**: Full execution logs and metrics in Inngest dashboard
    3. **No Infrastructure**: No Redis/RabbitMQ to manage - Inngest handles the queue
    4. **Async by Default**: Perfect for I/O heavy operations (web scraping, API calls)
    5. **Error Handling**: Automatic retries with exponential backoff
    6. **Monitoring**: Real-time visibility into function execution and performance
    
    Args:
        step: Inngest step context for orchestrating the workflow
        event: Event data containing registration information
        
    Returns:
        Dict with processing status and results
        
    Raises:
        ValueError: If registration data is invalid
        Exception: For other processing errors (Inngest will retry automatically)
    """
    try:
        # 1️⃣ Extract and validate registration data ----
        event_data = event.get("data", {})
        request_id = event_data.get("request_id")
        registration_data = event_data.get("registration_data", {})
        
        if not request_id:
            raise ValueError("Missing request_id in event data")
        
        if not registration_data:
            raise ValueError("Missing registration_data in event data")
        
        logger.info(f"Processing registration request: {request_id}")
        
        # 2️⃣ Create RegistrationRequest from event data ----
        try:
            registration_request = RegistrationRequest(**registration_data)
        except Exception as e:
            logger.error(f"Invalid registration data for {request_id}: {e}")
            raise ValueError(f"Invalid registration data: {str(e)}")
        
        # 3️⃣ Process registration using domain logic ----
        logger.info(f"Starting intelligence collection for {request_id}")
        analysis_result = await process_registration(registration_request)
        
        # 4️⃣ Save analysis results ----
        # Note: process_registration already calls save_analysis internally,
        # but we'll also save the final result here for redundancy
        try:
            file_path = await save_analysis(analysis_result.model_dump(), request_id)
            logger.info(f"Analysis saved to {file_path} for {request_id}")
        except Exception as e:
            logger.warning(f"Failed to save analysis for {request_id}: {e}")
            # Don't fail the entire process if saving fails
        
        # 5️⃣ Return completion status ----
        logger.info(f"Successfully completed processing for {request_id}")
        
        return {
            "status": "completed",
            "request_id": request_id,
            "event_id": event.get("id"),
            "analysis_result": {
                "has_linkedin_analysis": analysis_result.linkedin_analysis is not None,
                "has_website_analysis": analysis_result.website_analysis is not None,
                "timestamp": analysis_result.timestamp.isoformat()
            },
            "message": "Registration processing completed successfully"
        }
        
    except ValueError as e:
        # Validation errors - don't retry, log and fail
        logger.error(f"Validation error for request {request_id}: {e}")
        raise
        
    except Exception as e:
        # Unexpected errors - Inngest will retry automatically
        logger.error(f"Unexpected error processing registration {request_id}: {e}", exc_info=True)
        raise 