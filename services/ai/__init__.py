"""AI services for business intelligence analysis."""

# Public API - all functions that should be accessible from this service
from services.ai.client import ai_client, AIClient

__all__ = [
    "ai_client",
    "AIClient"
] 