# ==============================================================================
# url_parser.py — LinkedIn URL parsing and validation utilities
# ==============================================================================
# Purpose: Parse, validate, and extract information from LinkedIn URLs
# Sections: Imports, URL Parsing, Validation Logic, Information Extraction
# ==============================================================================

# Standard Library --------------------------------------------------------------
import re
from typing import Any, Dict, Optional, Union
from urllib.parse import parse_qs, urlparse

# Core (App-wide) ---------------------------------------------------------------
from core.utils.url_utils import normalize_url


def extract_profile_id(linkedin_url: str) -> str:
    """Extract profile ID from LinkedIn URL in various formats."""
    if not linkedin_url:
        raise ValueError("LinkedIn URL cannot be empty")
    
    # Normalize URL
    url = linkedin_url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Parse URL
        parsed = urlparse(url)
        
        # Validate domain
        if 'linkedin.com' not in parsed.netloc:
            raise ValueError("URL must be from linkedin.com domain")
        
        # Extract path components
        path_parts = [part for part in parsed.path.split('/') if part]
        
        # Look for 'in' followed by profile identifier
        if len(path_parts) >= 2 and path_parts[0] == 'in':
            profile_id = path_parts[1]
            
            # Validate profile ID format
            if _is_valid_profile_id(profile_id):
                return profile_id
            else:
                raise ValueError(f"Invalid profile ID format: {profile_id}")
        else:
            raise ValueError("URL must contain '/in/' followed by profile identifier")
            
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to parse LinkedIn URL: {str(e)}")


def _is_valid_profile_id(profile_id: str) -> bool:
    """Validate LinkedIn profile ID format."""
    if not profile_id:
        return False
    
    # LinkedIn profile IDs typically contain alphanumeric characters, hyphens, and underscores
    # They are usually 3-100 characters long
    pattern = r'^[a-zA-Z0-9_-]{3,100}$'
    return bool(re.match(pattern, profile_id))


def is_valid_linkedin_url(url: str) -> bool:
    """Check if URL is a valid LinkedIn profile URL."""
    try:
        extract_profile_id(url)
        return True
    except ValueError:
        return False


def normalize_linkedin_url(url: str) -> str:
    """Normalize LinkedIn URL to standard format."""
    try:
        profile_id = extract_profile_id(url)
        return f"https://www.linkedin.com/in/{profile_id}"
    except ValueError:
        raise ValueError(f"Cannot normalize invalid LinkedIn URL: {url}")


def get_profile_url_from_id(profile_id: str) -> str:
    """
    Generate LinkedIn profile URL from profile ID.
    
    Args:
        profile_id: LinkedIn profile identifier
        
    Returns:
        LinkedIn profile URL
        
    Examples:
        >>> get_profile_url_from_id("johndoe")
        'https://www.linkedin.com/in/johndoe'
    """
    if not _is_valid_profile_id(profile_id):
        raise ValueError(f"Invalid profile ID: {profile_id}")
    
    return f"https://www.linkedin.com/in/{profile_id}" 