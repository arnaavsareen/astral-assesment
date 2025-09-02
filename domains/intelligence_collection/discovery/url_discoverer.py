# ==============================================================================
# url_discoverer.py — URL discovery and crawling functionality
# ==============================================================================
# Purpose: Discover and extract URLs from web pages and content for intelligence gathering
# Sections: Imports, URL Discovery Logic, Content Parsing, Link Extraction
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
from typing import List

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from core.utils.url_utils import normalize_url
from services.firecrawl import firecrawl_client

# Configure logging for this module
logger = logging.getLogger(__name__)


async def discover_company_urls(website: str) -> List[str]:
    """Discover all URLs on a company website using Firecrawl."""
    try:
        # 1️⃣ Normalize the website URL ----
        normalized_website = normalize_url(website)
        logger.info("Starting URL discovery", extra={"website": normalized_website})
        
        # 2️⃣ Use FirecrawlClient to discover URLs ----
        discovered_urls = await firecrawl_client.map_website(normalized_website)
        
        # 3️⃣ Log discovery results ----
        logger.info("Discovered URLs", extra={"website": normalized_website, "urls_discovered": len(discovered_urls)})
        
        if discovered_urls:
            logger.debug("Sample discovered URLs", extra={"website": normalized_website, "sample_urls": discovered_urls[:3]})
        
        return discovered_urls
        
    except Exception as e:
        logger.error("Failed to discover URLs", extra={"website": website, "error": str(e)})
        logger.debug("Error details", extra={"website": website, "error_type": type(e).__name__, "error_details": str(e)})
        return [] 