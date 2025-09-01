"""LinkedIn URL parsing utilities for extracting profile identifiers."""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


def extract_profile_id(linkedin_url: str) -> str:
    """
    Extract profile ID from LinkedIn URL.
    
    Args:
        linkedin_url: LinkedIn profile URL in various formats
        
    Returns:
        Profile identifier (e.g., 'johndoe' from 'https://linkedin.com/in/johndoe')
        
    Raises:
        ValueError: If URL format is invalid or profile ID cannot be extracted
        
    Examples:
        >>> extract_profile_id("https://linkedin.com/in/johndoe")
        'johndoe'
        >>> extract_profile_id("https://www.linkedin.com/in/johndoe/")
        'johndoe'
        >>> extract_profile_id("https://linkedin.com/in/johndoe?trk=profile")
        'johndoe'
    """
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
    """
    Validate LinkedIn profile ID format.
    
    Args:
        profile_id: Profile identifier to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not profile_id:
        return False
    
    # LinkedIn profile IDs typically contain alphanumeric characters, hyphens, and underscores
    # They are usually 3-100 characters long
    pattern = r'^[a-zA-Z0-9_-]{3,100}$'
    return bool(re.match(pattern, profile_id))


def is_valid_linkedin_url(url: str) -> bool:
    """
    Check if URL is a valid LinkedIn profile URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid LinkedIn profile URL, False otherwise
    """
    try:
        extract_profile_id(url)
        return True
    except ValueError:
        return False


def normalize_linkedin_url(url: str) -> str:
    """
    Normalize LinkedIn URL to standard format.
    
    Args:
        url: LinkedIn URL to normalize
        
    Returns:
        Normalized LinkedIn URL
        
    Examples:
        >>> normalize_linkedin_url("linkedin.com/in/johndoe")
        'https://www.linkedin.com/in/johndoe'
        >>> normalize_linkedin_url("https://linkedin.com/in/johndoe?trk=profile")
        'https://www.linkedin.com/in/johndoe'
    """
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