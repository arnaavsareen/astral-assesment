"""Content extraction module for intelligence collection domain."""

import asyncio
import logging
from typing import List, Dict
from services.firecrawl.client import firecrawl_client

# Configure logging for this module
logger = logging.getLogger(__name__)


async def _scrape_single_url(url: str) -> tuple[str, str]:
    """
    Scrape content from a single URL with error handling.
    
    Args:
        url: URL to scrape
        
    Returns:
        Tuple of (url, content) where content is markdown or error message
    """
    try:
        logger.debug(f"Scraping URL: {url}")
        content = await firecrawl_client.scrape_url(url)
        logger.debug(f"Successfully scraped {url} ({len(content)} characters)")
        return url, content
        
    except Exception as e:
        error_msg = f"Failed to scrape {url}: {str(e)}"
        logger.warning(error_msg)
        return url, error_msg


async def extract_content(filtered_urls: List[Dict]) -> Dict[str, str]:
    """
    Extract content with performance optimizations.
    
    Args:
        filtered_urls: List of dictionaries with {"url": ..., "reason": ...}
        
    Returns:
        Dictionary mapping URL to markdown content
        
    Features:
    - Concurrent scraping with semaphore to prevent overwhelming
    - Graceful error handling - skips failed URLs
    - Rate limit handling - returns partial results if limits hit
    - Logging for debugging and monitoring
    """
    if not filtered_urls:
        logger.info("No URLs to extract content from")
        return {}
    
    # 1️⃣ Extract URLs from filtered data ----
    urls = [url_data["url"] for url_data in filtered_urls]
    logger.info(f"Starting content extraction for {len(urls)} URLs")
    
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
                logger.error(f"Scraping task failed: {result}")
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
        logger.info(
            f"Content extraction completed: "
            f"{successful_scrapes} successful, {failed_scrapes} failed"
        )
        
        if successful_scrapes == 0:
            logger.warning("No content was successfully extracted")
        elif failed_scrapes > 0:
            logger.warning(f"{failed_scrapes} URLs failed to scrape")
        
        return content_map
        
    except asyncio.CancelledError:
        # 6️⃣ Handle cancellation (e.g., rate limits) ----
        logger.warning("Content extraction was cancelled - possible rate limit")
        return {}
        
    except Exception as e:
        # 7️⃣ Handle unexpected errors ----
        logger.error(f"Unexpected error during content extraction: {e}")
        return {} 