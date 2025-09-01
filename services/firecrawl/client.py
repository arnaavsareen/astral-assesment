"""Firecrawl client wrapper for web scraping and URL discovery."""

import asyncio
import logging
from typing import List, Optional
import httpx
from core.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class FirecrawlClient:
    """
    Firecrawl client with optimal API usage.
    
    Strategy: Use Firecrawl's map endpoint for URL discovery and scrape endpoint for content extraction.
    - Map endpoint: Fast, lightweight URL discovery
    - Scrape endpoint: Content extraction in markdown format
    
    API Documentation: https://docs.firecrawl.dev/api-reference/v2-introduction
    """
    
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
        """
        Discover URLs using Firecrawl's map endpoint.
        
        Map is optimal because:
        1. Extremely fast - designed for getting site structure
        2. Lighter on credits than crawl
        3. Returns all URLs without content (perfect for filtering first)
        
        Args:
            url: Base URL of the website to map
            
        Returns:
            List of discovered URLs
            
        Raises:
            ValueError: If no API key is provided
            httpx.HTTPStatusError: If API call fails
        """
        if not self._has_api_key():
            raise ValueError("Firecrawl API key required for URL discovery")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/map",
                    json={"url": url, "limit": 50, "sitemap": "include"},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                logger.debug(f"Firecrawl map API response: {data}")
                
                # Extract URLs from map response based on documented structure
                urls = []
                if "links" in data:
                    # Extract URLs from links array
                    for link in data["links"]:
                        if isinstance(link, dict) and "url" in link:
                            urls.append(link["url"])
                        elif isinstance(link, str):
                            urls.append(link)
                
                logger.info(f"Discovered {len(urls)} URLs for {url}")
                return urls
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Map API call failed for {url}: HTTP {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during map API call for {url}: {e}")
            raise
    
    async def scrape_url(self, url: str) -> str:
        """
        Scrape single URL using Firecrawl's scrape endpoint.
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped content in markdown format
            
        Raises:
            ValueError: If no API key is provided
            httpx.HTTPStatusError: If API call fails
        """
        if not self._has_api_key():
            raise ValueError("Firecrawl API key required for content scraping")
        
        return await self._scrape_with_backoff(url)
    
    async def _scrape_with_backoff(self, url: str, attempt: int = 0) -> str:
        """
        Scrape with exponential backoff for rate limits.
        
        Args:
            url: URL to scrape
            attempt: Current attempt number for backoff calculation
            
        Returns:
            Scraped content in markdown format
            
        Raises:
            httpx.HTTPStatusError: If API call fails after all retries
        """
        try:
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
                
                if response.status_code == 429:  # Rate limited
                    if attempt < 3:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning(f"Rate limited for {url}, waiting {wait_time}s (attempt {attempt + 1}/3)")
                        await asyncio.sleep(wait_time)
                        return await self._scrape_with_backoff(url, attempt + 1)
                    logger.error(f"Rate limit exceeded for {url} after 3 attempts")
                    raise httpx.HTTPStatusError("Rate limit exceeded", request=None, response=response)
                
                response.raise_for_status()
                data = response.json()
                
                # Extract markdown content
                if "data" in data and "markdown" in data["data"]:
                    content = data["data"]["markdown"]
                    logger.debug(f"Successfully scraped {url} ({len(content)} characters)")
                    return content
                else:
                    logger.warning(f"No markdown content found in response for {url}")
                    raise ValueError(f"No markdown content available for: {url}")
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping {url}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
            raise


# Global singleton instance
firecrawl_client = FirecrawlClient() 