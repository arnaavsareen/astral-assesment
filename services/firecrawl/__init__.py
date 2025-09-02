"""Firecrawl web scraping services."""

# Public API - all functions that should be accessible from this service
from services.firecrawl.client import firecrawl_client, FirecrawlClient

__all__ = [
    "firecrawl_client",
    "FirecrawlClient"
] 