"""URL discovery module for intelligence collection domain."""

import logging
from typing import List
from core.utils.url_utils import normalize_url
from services.firecrawl.client import firecrawl_client

# Configure logging for this module
logger = logging.getLogger(__name__)


async def discover_company_urls(website: str) -> List[str]:
    """
    Discover all URLs on a company website using Firecrawl.
    
    Args:
        website: Base URL of the company website to crawl
        
    Returns:
        List of discovered URLs, or empty list if discovery fails
        
    Note:
        This function discovers all URLs on the website. Filtering for valuable
        URLs happens separately in the validation layer. Target valuable paths
        include: /about, /team, /services, /blog, /case-studies, etc.
    """
    try:
        # 1️⃣ Normalize the website URL ----
        normalized_website = normalize_url(website)
        logger.info(f"Starting URL discovery for: {normalized_website}")
        
        # 2️⃣ Use FirecrawlClient to discover URLs ----
        discovered_urls = await firecrawl_client.map_website(normalized_website)
        
        # 3️⃣ Log discovery results ----
        logger.info(f"Discovered {len(discovered_urls)} URLs for {normalized_website}")
        
        if discovered_urls:
            logger.debug(f"Sample discovered URLs: {discovered_urls[:3]}")
        
        return discovered_urls
        
    except Exception as e:
        # 4️⃣ Handle errors gracefully ----
        logger.error(f"Failed to discover URLs for {website}: {str(e)}")
        logger.debug(f"Error details: {type(e).__name__}: {e}")
        
        # Return empty list on failure
        return [] 