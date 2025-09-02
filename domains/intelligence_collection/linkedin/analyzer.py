# ==============================================================================
# analyzer.py — LinkedIn profile analysis and intelligence extraction
# ==============================================================================
# Purpose: Analyze LinkedIn profiles to extract business intelligence and insights
# Sections: Imports, Profile Analysis, Intelligence Extraction, Data Processing
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
from datetime import datetime, timezone
from typing import Dict, Any

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from core.clients.scrapingdog import ScrapingDogClient

# Internal domain modules
from .profile_analyzer import LinkedInProfileAnalyzer
from .url_parser import is_valid_linkedin_url

# Configure logging
logger = logging.getLogger(__name__)


async def analyze_linkedin_profile(linkedin_url: str) -> Dict[str, Any]:
    """Analyze LinkedIn profile and extract professional information using ScrapingDog API."""
    try:
        # 1️⃣ Validate LinkedIn URL format ----
        if not is_valid_linkedin_url(linkedin_url):
            raise ValueError(f"Invalid LinkedIn URL format: {linkedin_url}")
        
        logger.info("Analyzing LinkedIn profile", extra={"linkedin_url": linkedin_url})
        
        # 2️⃣ Initialize clients and analyzers ----
        client = ScrapingDogClient()
        analyzer = LinkedInProfileAnalyzer()
        
        # 3️⃣ Scrape profile data from ScrapingDog API ----
        raw_data = await client.scrape_profile(linkedin_url)
        
        # 4️⃣ Analyze and structure the data ----
        analysis = await analyzer.analyze_profile(raw_data)
        
        # 5️⃣ Check if analysis failed ----
        if "error" in analysis:
            return {
                "status": "error",
                "url": linkedin_url,
                "error": analysis["error"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # 6️⃣ Prepare successful response ----
        analysis_result = {
            "status": "success",
            "url": linkedin_url,
            "analysis": analysis,
            "raw_data": raw_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("LinkedIn analysis completed successfully", extra={"linkedin_url": linkedin_url})
        return analysis_result
        
    except ValueError as e:
        # Handle validation errors
        logger.warning("Validation error for LinkedIn profile", extra={"linkedin_url": linkedin_url, "error": str(e)})
        return {
            "status": "error",
            "url": linkedin_url,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        # Handle all other errors
        logger.error("Failed to analyze LinkedIn profile", extra={"linkedin_url": linkedin_url, "error": str(e)})
        return {
            "status": "error",
            "url": linkedin_url,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 