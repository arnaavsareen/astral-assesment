# ==============================================================================
# url_filter.py — URL filtering and classification logic
# ==============================================================================
# Purpose: Filter and classify URLs based on business intelligence criteria and relevance
# Sections: Imports, Filtering Rules, Classification Logic, Business Intelligence Detection
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
from typing import Dict, List, Tuple, Any
from urllib.parse import urlparse

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from core.clients.openai import ai_client

# Configure logging
logger = logging.getLogger(__name__)


async def filter_valuable_urls(
    urls: List[str], 
    company_context: Dict[str, str], 
    max_urls: int = 10
) -> List[Dict[str, Any]]:
    """Filter URLs using AI scoring and ensure category diversity."""
    if not urls:
        return []
    
    try:
        # 1️⃣ Convert company context to string for AI client ----
        context_string = str(company_context)
        
        # AI-powered scoring
        scored_urls = await ai_client.score_urls_for_business_intelligence(urls, context_string)
        logger.info("AI scoring successful", extra={"urls_selected": len(selected_urls)})
        
        # 2️⃣ Apply diversity algorithm ----
        selected_urls = _ensure_diversity(scored_urls, max_urls)
        
        logger.info("AI scoring successful", extra={"urls_selected": len(selected_urls)})
        return selected_urls
        
    except Exception as e:
        logger.warning("AI scoring failed, using fallback", extra={"error": str(e)})
        return _fallback_filter(urls, max_urls)


def _ensure_diversity(
    scored_urls: List[Dict], 
    max_urls: int
) -> List[Dict]:
    """Ensure category diversity in selected URLs with max 2 per category."""
    if not scored_urls:
        return []
    
    # Sort by score (highest first)
    scored_urls.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Track categories and build diverse selection
    selected_urls = []
    category_counts = {}
    
    for url_data in scored_urls:
        if len(selected_urls) >= max_urls:
            break
            
        category = url_data.get("category", "other")
        current_count = category_counts.get(category, 0)
        
        # Allow max 2 URLs per category for diversity
        if current_count < 2:
            selected_urls.append(url_data)
            category_counts[category] = current_count + 1
    
    # If we haven't filled max_urls, add remaining high-scoring URLs
    if len(selected_urls) < max_urls:
        remaining_urls = [u for u in scored_urls if u not in selected_urls]
        selected_urls.extend(remaining_urls[:max_urls - len(selected_urls)])
    
    logger.info("Diversity algorithm selected URLs", extra={"urls_selected": len(selected_urls), "categories_covered": len(category_counts)})
    return selected_urls


def _fallback_filter(
    urls: List[str], 
    max_urls: int
) -> List[Dict[str, str]]:
    """Basic pattern-based filtering if AI fails."""
    if not urls:
        return []
    
    # Score URLs using pattern matching
    scored_urls = []
    for url in urls:
        score, reason = _score_url_pattern_based(url)
        scored_urls.append({
            "url": url,
            "score": score,
            "reason": reason,
            "category": _extract_category_from_reason(reason)
        })
    
    # Sort by score and return top N
    scored_urls.sort(key=lambda x: x["score"], reverse=True)
    selected_urls = scored_urls[:max_urls]
    
    logger.info("Fallback filtering selected URLs", extra={"urls_selected": len(selected_urls)})
    return selected_urls


def _score_url_pattern_based(url: str) -> Tuple[int, str]:
    """Score URL using pattern matching for fallback scenarios."""
    url_lower = url.lower()
    path = urlparse(url).path.lower()
    
    # High value patterns (score: 90-100)
    if any(term in path for term in ['/about', '/company', '/mission']):
        return 95, "Company overview and mission"
    if any(term in path for term in ['/team', '/leadership', '/people']):
        return 90, "Leadership and team information"
    if any(term in path for term in ['/services', '/products', '/solutions']):
        return 85, "Core offerings"
    
    # Medium value patterns (score: 60-80)
    if '/blog' in path and any(term in path for term in ['culture', 'values', 'announcement']):
        return 75, "Company culture insights"
    if any(term in path for term in ['/customers', '/case-studies', '/testimonials']):
        return 70, "Customer success stories"
    if any(term in path for term in ['/investors', '/press', '/news']):
        return 65, "Public announcements"
    
    # Low value patterns (score: 0-50)
    if any(term in path for term in ['/privacy', '/terms', '/legal', '/cookie']):
        return 10, "Legal/compliance pages"
    if any(term in path for term in ['/login', '/signup', '/contact']):
        return 20, "Utility pages"
    
    # Default medium-low for unknown
    return 40, "Potentially relevant content"


def _extract_category_from_reason(reason: str) -> str:
    """Extract category from reason string for fallback filtering."""
    reason_lower = reason.lower()
    
    if any(term in reason_lower for term in ['mission', 'overview', 'leadership', 'team']):
        return "leadership"
    elif any(term in reason_lower for term in ['offerings', 'services', 'products']):
        return "products"
    elif any(term in reason_lower for term in ['culture', 'insights']):
        return "culture"
    elif any(term in reason_lower for term in ['customers', 'success', 'stories']):
        return "customers"
    elif any(term in reason_lower for term in ['investors', 'press', 'news']):
        return "financials"
    elif any(term in reason_lower for term in ['legal', 'compliance', 'utility']):
        return "other"
    else:
        return "other"


# TODO: Testing considerations
# - Mock AI responses in tests
# - Test diversity algorithm edge cases
# - Test fallback behavior when AI fails
# - Test category extraction logic 