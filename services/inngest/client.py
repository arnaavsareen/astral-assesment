# ==============================================================================
# client.py — Inngest workflow orchestration client
# ==============================================================================
# Purpose: Client for Inngest workflow orchestration and event-driven processing
# Sections: Imports, Client Configuration, Event Publishing, Workflow Management
# ==============================================================================

# Standard Library --------------------------------------------------------------
import json
import logging
import os
from typing import Any, Dict, List, Optional

# Third Party -------------------------------------------------------------------
from inngest import Inngest, Event

# Core (App-wide) ---------------------------------------------------------------
from core.config.settings import settings


# Singleton Inngest client instance
# Use development mode if INNGEST_DEV is set or if we're in test mode
is_dev_mode = os.getenv("INNGEST_DEV", "0") == "1" or settings.test_mode

if is_dev_mode:
    # Development mode - no signing key required
    inngest_client = Inngest(
        app_id=settings.inngest_app_id or "astral-assessment-dev",
        logger=logging.getLogger("uvicorn")
    )
else:
    # Production mode - requires signing key
    inngest_client = Inngest(
        app_id=settings.inngest_app_id,
        signing_key=settings.inngest_signing_key,
        logger=logging.getLogger("uvicorn")
    ) 