# ==============================================================================
# content_extractor.py — Content extraction and processing from web sources
# ==============================================================================
# Purpose: Extract and process text content, metadata, and structured data from web pages
# Sections: Imports, Content Extraction, Text Processing, Metadata Extraction
# ==============================================================================

# Standard Library --------------------------------------------------------------
import asyncio
import logging
from typing import Dict, List

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from core.clients.firecrawl import firecrawl_client

# Configure logging for this module
logger = logging.getLogger(__name__)


async def _scrape_single_url(url: str) -> tuple[str, str]:
    """Scrape content from a single URL with error handling."""
    try:
        logger.debug("Scraping URL", extra={"url": url})
        content = await firecrawl_client.scrape_url(url)
        logger.debug("Successfully scraped URL", extra={"url": url, "content_length": len(content)})
        return url, content
        
    except Exception as e:
        error_msg = f"Failed to scrape {url}: {str(e)}"
        logger.warning("Failed to scrape URL", extra={"url": url, "error": str(e)})
        return url, error_msg


async def extract_content(filtered_urls: List[Dict]) -> Dict[str, str]:
    """Extract content with concurrent scraping and error handling."""
    if not filtered_urls:
        logger.info("No URLs to extract content from")
        return {}
    
    # 1️⃣ Extract URLs from filtered data ----
    urls = [url_data["url"] for url_data in filtered_urls]
    logger.info("Starting content extraction", extra={"urls_count": len(urls)})
    
    # 2️⃣ Create scraping tasks with semaphore ----
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
    
    async def scrape_with_semaphore(url_data: dict):
        async with semaphore:
            url = url_data["url"]
            content = await firecrawl_client.scrape_url(url)
            return url, content
    
    # 3️⃣ Gather all scrapes concurrently ----
    tasks = [scrape_with_semaphore(url_data) for url_data in filtered_urls]
    
    try:
        logger.debug("Executing concurrent scraping tasks with semaphore")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 4️⃣ Process results and handle errors ----
        content_map = {}
        successful_scrapes = 0
        failed_scrapes = 0
        
        for result in results:
            if isinstance(result, Exception):
                # Task failed completely
                failed_scrapes += 1
                logger.error("Scraping task failed", extra={"error": str(result)})
                continue
            
            url, content = result
            
            if content.startswith("Failed to scrape") or content.startswith("Error scraping"):
                # Individual URL failed
                failed_scrapes += 1
                content_map[url] = content
            else:
                # Successful scrape
                successful_scrapes += 1
                content_map[url] = content
        
        # 5️⃣ Log extraction results ----
        logger.info("Content extraction completed", extra={"successful_scrapes": successful_scrapes, "failed_scrapes": failed_scrapes})
        
        if successful_scrapes == 0:
            logger.warning("No content was successfully extracted")
        elif failed_scrapes > 0:
            logger.warning("URLs failed to scrape", extra={"failed_count": failed_scrapes})
        
        return content_map
        
    except asyncio.CancelledError:
        # 6️⃣ Handle cancellation (e.g., rate limits) ----
        logger.warning("Content extraction was cancelled - possible rate limit")
        return {}
        
    except Exception as e:
        # 7️⃣ Handle unexpected errors ----
        logger.error("Unexpected error during content extraction", extra={"error": str(e)})
        return {} 