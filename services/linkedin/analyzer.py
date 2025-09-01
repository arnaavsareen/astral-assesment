"""LinkedIn profile analyzer for extracting professional information using ScrapingDog API."""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
from core.config.settings import settings
from services.linkedin.scrapingdog_client import ScrapingDogClient
from services.linkedin.profile_analyzer import LinkedInProfileAnalyzer
from services.linkedin.url_parser import is_valid_linkedin_url

# Configure logging
logger = logging.getLogger(__name__)


async def analyze_linkedin_profile(linkedin_url: str) -> Dict[str, Any]:
    """
    Analyze LinkedIn profile and extract professional information using ScrapingDog API.
    
    This function provides a comprehensive analysis of LinkedIn profiles,
    extracting key professional information, experience, education, and
    business intelligence insights.
    
    Args:
        linkedin_url: LinkedIn profile URL to analyze
        
    Returns:
        Dictionary containing analysis results with the following structure:
        {
            "status": "success" | "error",
            "url": str,
            "analysis": {
                "profile_summary": {...},
                "professional_info": {...},
                "experience": {...},
                "education": {...},
                "content_analysis": {...},
                "network_insights": {...},
                "business_intelligence": {...}
            },
            "raw_data": {...},
            "timestamp": str
        }
        
    Example:
        >>> result = await analyze_linkedin_profile("https://linkedin.com/in/johndoe")
        >>> print(result["analysis"]["profile_summary"]["full_name"])
        "John Doe"
    """
    try:
        # Validate LinkedIn URL
        if not is_valid_linkedin_url(linkedin_url):
            raise ValueError(f"Invalid LinkedIn URL format: {linkedin_url}")
        
        logger.info(f"Analyzing LinkedIn profile: {linkedin_url}")
        
        # Initialize ScrapingDog client and profile analyzer
        client = ScrapingDogClient()
        analyzer = LinkedInProfileAnalyzer()
        
        # Scrape profile data from ScrapingDog API
        raw_data = await client.scrape_profile(linkedin_url)
        
        # Analyze and structure the data
        analysis = analyzer.analyze_profile(raw_data)
        
        # Check if analysis failed
        if "error" in analysis:
            return {
                "status": "error",
                "url": linkedin_url,
                "error": analysis["error"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Prepare successful response
        analysis_result = {
            "status": "success",
            "url": linkedin_url,
            "analysis": analysis,
            "raw_data": raw_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"LinkedIn analysis completed successfully for: {linkedin_url}")
        return analysis_result
        
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error for LinkedIn profile {linkedin_url}: {e}")
        return {
            "status": "error",
            "url": linkedin_url,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        # Handle all other errors
        logger.error(f"Failed to analyze LinkedIn profile {linkedin_url}: {e}")
        return {
            "status": "error",
            "url": linkedin_url,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 