# ==============================================================================
# validators.py — Common validation utilities for intelligence collection
# ==============================================================================
# Purpose: Shared validation functions and business logic for data quality assurance
# Sections: Imports, Validation Functions, Business Logic Rules, Error Handling
# ==============================================================================

# Standard Library --------------------------------------------------------------
import re
from typing import Any, Dict, List, Optional, Union

# Third Party -------------------------------------------------------------------
from pydantic import BaseModel, ValidationError

# Core (App-wide) ---------------------------------------------------------------
from core.types.models import RegistrationRequest
from core.utils.url_utils import is_business_intelligence_url


def validate_data_source(data: RegistrationRequest) -> None:
    """Ensure at least one data source (website or LinkedIn) is provided."""
    if not data.company_website and not data.linkedin:
        raise ValueError(
            "At least one data source must be provided: "
            "company_website or linkedin"
        )


def is_valuable_url(url: str) -> bool:
    """Check if URL contains valuable business intelligence information."""
    url_lower = url.lower()
    
    # High-value business intelligence pages
    valuable_patterns = [
        '/about', '/company', '/team', '/leadership', '/management',
        '/services', '/products', '/solutions', '/offerings',
        '/careers', '/jobs', '/work-with-us', '/join-us',
        '/news', '/blog', '/press', '/media',
        '/contact', '/locations', '/offices',
        '/investors', '/investor-relations',
        '/partners', '/partnerships',
        '/customers', '/case-studies', '/success-stories'
    ]
    
    # Check for valuable page patterns
    for pattern in valuable_patterns:
        if pattern in url_lower:
            return True
    
    # Check for business intelligence platforms
    if is_business_intelligence_url(url):
        return True
    
    # Check for root domain (often contains company overview)
    if url.count('/') <= 2:  # Root or near-root pages
        return True
    
    return False 