# ==============================================================================
# url_utils.py — URL validation and manipulation utilities
# ==============================================================================
# Purpose: Provide URL parsing, validation, and transformation functions
# Sections: Imports, URL Validation, URL Parsing, URL Transformation
# ==============================================================================

# Standard Library --------------------------------------------------------------
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse, urlunparse

# Third Party -------------------------------------------------------------------
from pydantic import HttpUrl, ValidationError


def normalize_url(url: str) -> str:
    """Normalize URL to consistent format with scheme and lowercase components."""
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
    """Check if URL is likely a business intelligence or analytics platform."""
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