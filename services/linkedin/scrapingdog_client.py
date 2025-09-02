# ==============================================================================
# scrapingdog_client.py — ScrapingDog API client for LinkedIn scraping
# ==============================================================================
# Purpose: Client for ScrapingDog API to scrape LinkedIn profiles and data
# Sections: Imports, API Client Configuration, Scraping Methods, Response Handling
# ==============================================================================

# Standard Library --------------------------------------------------------------
import asyncio
import logging
from typing import Dict, Any, Optional

# Third Party -------------------------------------------------------------------
import httpx

# Core (App-wide) ---------------------------------------------------------------
from core.config.settings import settings
from services.linkedin.url_parser import extract_profile_id

# Configure logging
logger = logging.getLogger(__name__)


class ScrapingDogClient:
    """
    ScrapingDog LinkedIn API client for profile scraping.
    
    Documentation: https://www.scrapingdog.com/linkedin-scraper-api
    Cost: 50 credits per successful request
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ScrapingDog client.
        
        Args:
            api_key: ScrapingDog API key. If None, uses settings.scrapingdog_api_key
        """
        self.api_key = api_key or settings.scrapingdog_api_key
        self.base_url = "https://api.scrapingdog.com/linkedin/"
        self.timeout = getattr(settings, 'scrapingdog_timeout', 30)
        self.max_retries = getattr(settings, 'scrapingdog_max_retries', 3)
        
        if not self.api_key:
            logger.warning("No ScrapingDog API key provided - client will return mock data")
    
    def _has_api_key(self) -> bool:
        """Check if API key is available and not empty."""
        return bool(self.api_key and self.api_key.strip())
    
    async def _make_request(self, params: Dict[str, Any], max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Make HTTP request to ScrapingDog API with retry logic.
        
        Args:
            params: Query parameters for the request
            max_retries: Maximum number of retry attempts (defaults to self.max_retries)
            
        Returns:
            API response as dictionary
            
        Raises:
            httpx.HTTPStatusError: If request fails after all retries
            ValueError: If API key is missing
        """
        if not self._has_api_key():
            # Return mock data for testing without API key
            return self._get_mock_response(params.get('linkId', 'test-profile'))
        
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    logger.info("ScrapingDog API request successful for profile", extra={"profile_id": params.get('linkId')})
                    
                    return data
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt < max_retries:
                        wait_time = 2 ** attempt
                        logger.warning("Rate limited, retrying", extra={"attempt": attempt + 1, "max_retries": max_retries, "wait_time": wait_time})
                        await asyncio.sleep(wait_time)
                        attempt += 1
                        continue
                    else:
                        logger.error("ScrapingDog API error", extra={"status_code": e.response.status_code, "response_text": e.response.text})
                        raise httpx.HTTPStatusError("Rate limit exceeded", request=None, response=response)
                elif e.response.status_code == 401:
                    raise ValueError("Invalid ScrapingDog API key")
                elif e.response.status_code == 404:
                    raise ValueError(f"LinkedIn profile not found: {params.get('linkId')}")
                else:
                    logger.error("ScrapingDog API error", extra={"status_code": e.response.status_code, "response_text": e.response.text})
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning("Request failed, retrying", extra={"attempt": attempt + 1, "max_retries": max_retries, "wait_time": wait_time, "error": str(e)})
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error("ScrapingDog API request failed after all attempts", extra={"max_retries": max_retries, "error": str(e)})
                    raise
        
        raise Exception(f"ScrapingDog API request failed after {max_retries} attempts")
    
    async def scrape_profile(self, linkedin_url: str, premium: bool = True) -> Dict[str, Any]:
        """
        Scrape LinkedIn profile using ScrapingDog API.
        
        Args:
            linkedin_url: LinkedIn profile URL
            premium: Use premium proxies (default: True)
            
        Returns:
            LinkedIn profile data from ScrapingDog API
            
        Raises:
            ValueError: If URL is invalid or API key is missing
        """
        try:
            # Extract profile ID from URL
            profile_id = extract_profile_id(linkedin_url)
            
            # Prepare API request parameters
            params = {
                "api_key": self.api_key,
                "type": "profile",
                "linkId": profile_id,
                "premium": premium
            }
            
            logger.info("Scraping LinkedIn profile", extra={"profile_id": profile_id})
            
            # Make API request
            response = await self._make_request(params)
            
            return response
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error("Failed to scrape LinkedIn profile", extra={"linkedin_url": linkedin_url, "error": str(e)})
            return None
    
    def _get_mock_response(self, profile_id: str) -> Dict[str, Any]:
        """
        Return mock response for testing without API key.
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            Mock LinkedIn profile data
        """
        return {
            "fullName": f"Mock User {profile_id}",
            "first_name": "Mock",
            "last_name": "User",
            "public_identifier": profile_id,
            "headline": "Software Engineer at Mock Company",
            "location": "San Francisco, CA",
            "followers": "1,234 followers",
            "connections": "500+ connections",
            "about": "This is a mock LinkedIn profile for testing purposes.",
            "experience": [
                {
                    "position": "Software Engineer",
                    "company_name": "Mock Company",
                    "location": "San Francisco, CA",
                    "summary": "Building amazing software solutions",
                    "starts_at": "Jan 2022",
                    "ends_at": "Present",
                    "duration": "2 years"
                }
            ],
            "education": [
                {
                    "school": "Mock University",
                    "degree": "Bachelor of Science in Computer Science",
                    "field_of_study": "Computer Science",
                    "starts_at": "2018",
                    "ends_at": "2022"
                }
            ],
            "articles": [],
            "activities": [],
            "people_also_viewed": [],
            "similar_profiles": [],
            "recommendations": [],
            "publications": [],
            "courses": [],
            "languages": [],
            "organizations": [],
            "projects": [],
            "awards": [],
            "score": []
        }
    
    async def get_credits_remaining(self) -> Optional[int]:
        """
        Get remaining credits (if API supports it).
        
        Returns:
            Number of remaining credits or None if not supported
        """
        # Note: ScrapingDog may not provide a credits endpoint
        # This is a placeholder for future implementation
        logger.info("Credits remaining check not implemented for ScrapingDog API")
        return None
    
    async def test_connection(self) -> bool:
        """
        Test API connection and key validity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self._has_api_key():
                logger.warning("No API key available for connection test")
                return False
            
            # Try to scrape a test profile (this will validate the API key)
            test_url = "https://linkedin.com/in/test-profile"
            await self.scrape_profile(test_url)
            return True
            
        except ValueError as e:
            if "Invalid ScrapingDog API key" in str(e):
                logger.error("Invalid ScrapingDog API key")
                return False
            else:
                # Other validation errors are expected for test profiles
                logger.info("API connection test successful (expected validation error for test profile)")
                return True
        except Exception as e:
            logger.error("API connection test failed", extra={"error": str(e)})
            return False 