"""URL utility functions for normalization and business intelligence detection."""

import re
from urllib.parse import urlparse, urlunparse, urljoin
from typing import Optional


def normalize_url(url: str) -> str:
    """
    Normalize URL to consistent format.
    
    Args:
        url: Raw URL string to normalize
        
    Returns:
        Normalized URL string
        
    Examples:
        >>> normalize_url("https://www.example.com/path?param=value#fragment")
        "https://www.example.com/path?param=value#fragment"
        >>> normalize_url("example.com")
        "https://example.com"
    """
    # 1️⃣ Normalize scheme to lowercase first ----
    url_lower = url.lower()
    if url_lower.startswith('http://'):
        url = 'http://' + url[7:]
    elif url_lower.startswith('https://'):
        url = 'https://' + url[8:]
    elif not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # 2️⃣ Parse and reconstruct URL ----
    parsed = urlparse(url)
    
    # 3️⃣ Normalize components ----
    normalized_parts = (
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip('/') or '/',
        parsed.params,
        parsed.query,
        parsed.fragment
    )
    
    return urlunparse(normalized_parts)


def is_business_intelligence_url(url: str) -> bool:
    """
    Check if URL is likely a business intelligence or analytics platform.
    
    Args:
        url: URL string to check
        
    Returns:
        True if URL appears to be a BI platform
        
    Examples:
        >>> is_business_intelligence_url("https://app.powerbi.com/report")
        True
        >>> is_business_intelligence_url("https://example.com")
        False
    """
    # 1️⃣ Normalize URL for consistent checking ----
    normalized_url = normalize_url(url).lower()
    
    # 2️⃣ Define BI platform patterns ----
    bi_patterns = [
        r'powerbi\.com',
        r'tableau\.com',
        r'looker\.com',
        r'quicksight\.amazonaws\.com',
        r'analytics\.google\.com',
        r'bi\.',
        r'dashboard\.',
        r'reports\.',
        r'analytics\.',
        r'data\.',
        r'insights\.'
    ]
    
    # 3️⃣ Check if URL matches any BI pattern ----
    for pattern in bi_patterns:
        if re.search(pattern, normalized_url):
            return True
    
    return False 