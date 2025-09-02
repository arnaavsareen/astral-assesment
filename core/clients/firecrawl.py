# ==============================================================================
# firecrawl.py — Firecrawl web scraping service client
# ==============================================================================
# Purpose: Client for Firecrawl web scraping service with async support
# Sections: Imports, Client Configuration, Scraping Methods, Response Processing
# ==============================================================================

# Standard Library --------------------------------------------------------------
import asyncio
import logging
from typing import List, Optional

# Third Party -------------------------------------------------------------------
import httpx

# Core (App-wide) ---------------------------------------------------------------
from core.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class FirecrawlClient:
    """Firecrawl client for web scraping with URL discovery and content extraction."""
    
    _instance: Optional['FirecrawlClient'] = None
    _base_url = "https://api.firecrawl.dev/v2"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.api_key = settings.firecrawl_api_key
            self._initialized = True
            
            if not self._has_api_key():
                logger.warning("No Firecrawl API key provided - client will not function")
            else:
                logger.info("Firecrawl client initialized with API key")
    
    def _has_api_key(self) -> bool:
        """Check if API key is available and not empty."""
        return bool(self.api_key and self.api_key.strip())
    
    async def map_website(self, url: str) -> List[str]:
        """Discover URLs using Firecrawl's map endpoint for fast site structure."""
        if not self._has_api_key():
            raise ValueError("Firecrawl API key required for URL discovery")
        
        try:
            # 1️⃣ Prepare HTTP client and request ----
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/map",
                    json={"url": url, "limit": 50, "sitemap": "include"},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                logger.debug("Firecrawl map API response received", extra={"response_keys": list(data.keys())})
                
                # 2️⃣ Extract URLs from response data ----
                urls = []
                if "links" in data:
                    # Extract URLs from links array
                    for link in data["links"]:
                        if isinstance(link, dict) and "url" in link:
                            urls.append(link["url"])
                        elif isinstance(link, str):
                            urls.append(link)
                
                # 3️⃣ Log results and return ----
                logger.info("Discovered URLs", extra={"urls_discovered": len(urls), "source_url": url})
                return urls
                
        except httpx.HTTPStatusError as e:
            logger.error("Map API call failed", extra={"url": url, "status_code": e.response.status_code})
            raise
        except Exception as e:
            logger.error("Unexpected error during map API call", extra={"url": url, "error": str(e)})
            raise
    
    async def scrape_url(self, url: str) -> str:
        """Scrape single URL using Firecrawl's scrape endpoint."""
        if not self._has_api_key():
            raise ValueError("Firecrawl API key required for content scraping")
        
        return await self._scrape_with_backoff(url)
    
    async def _scrape_with_backoff(self, url: str, attempt: int = 0) -> str:
        """Scrape with exponential backoff for rate limits."""
        try:
            # 1️⃣ Prepare HTTP client and request ----
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/scrape",
                    json={
                        "url": url, 
                        "formats": ["markdown"]
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=35.0  # Slightly longer than API timeout
                )
                
                # 2️⃣ Handle rate limiting with exponential backoff ----
                if response.status_code == 429:  # Rate limited
                    if attempt < 3:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning("Rate limited, waiting", extra={"url": url, "attempt": attempt + 1, "max_attempts": 3, "wait_time": wait_time})
                        await asyncio.sleep(wait_time)
                        return await self._scrape_with_backoff(url, attempt + 1)
                    logger.error("Rate limit exceeded after all attempts", extra={"url": url, "max_attempts": 3})
                    raise httpx.HTTPStatusError("Rate limit exceeded", request=None, response=response)
                
                # 3️⃣ Validate response and extract content ----
                response.raise_for_status()
                data = response.json()
                
                # Extract markdown content
                if "data" in data and "markdown" in data["data"]:
                    content = data["data"]["markdown"]
                    logger.debug("Successfully scraped URL", extra={"url": url, "content_length": len(content)})
                    return content
                else:
                    logger.warning("No markdown content found in response", extra={"url": url, "response_keys": list(data.keys())})
                    raise ValueError(f"No markdown content available for: {url}")
                    
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error scraping URL", extra={"url": url, "status_code": e.response.status_code})
            raise
        except Exception as e:
            logger.error("Scrape failed", extra={"url": url, "error": str(e)})
            raise


# Global singleton instance
firecrawl_client = FirecrawlClient() 