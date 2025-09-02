# Firecrawl Service - Quick Reference

## Purpose (1-2 lines)
Web scraping service for URL discovery and content extraction.
Handles website mapping and markdown content scraping via Firecrawl API.

## Key Capabilities
- `firecrawl_client.map_website()` - Fast URL discovery
- `firecrawl_client.scrape_url()` - Content extraction
- Rate limit handling with exponential backoff
- Markdown format content delivery

## Internal Structure
- `client.py` - Firecrawl API client with singleton pattern
- `__init__.py` - Clean public API exports

## How It Works (5-10 lines max)
1. Map endpoint discovers all URLs on website quickly
2. Scrape endpoint extracts markdown content from individual URLs
3. Implements exponential backoff for rate limits
4. Handles API errors gracefully with logging
5. Returns structured data for domain processing

## Events Published
- None (service layer, not domain)

## Events Consumed
- None (service layer, not domain)

## Key Decisions
- Singleton pattern for API client efficiency
- Map endpoint for fast discovery, scrape for content
- Exponential backoff for rate limit handling
- Markdown format for clean content extraction 