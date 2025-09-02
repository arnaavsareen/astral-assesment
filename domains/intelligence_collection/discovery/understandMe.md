# URL Discovery - Quick Reference

## Purpose (1-2 lines)
Website URL discovery and site structure mapping.
Uses Firecrawl to discover all URLs on company websites for analysis.

## Key Capabilities
- `discover_company_urls()` - Main URL discovery function
- Firecrawl integration for fast site mapping
- Comprehensive URL collection and validation

## Internal Structure
- `url_discoverer.py` - URL discovery logic and Firecrawl integration
- `__init__.py` - Exports discovery functions

## How It Works (5-10 lines max)
1. Receives company website URL from domain layer
2. Calls Firecrawl map endpoint for site structure
3. Processes and validates discovered URLs
4. Returns clean list of URLs for filtering
5. Handles rate limiting and error cases gracefully

## Events Published
- None (subdomain layer)

## Events Consumed
- None (subdomain layer)

## Key Decisions
- Firecrawl for fast, credit-efficient URL discovery
- Async processing for performance
- Comprehensive error handling
- Clean URL validation and normalization 