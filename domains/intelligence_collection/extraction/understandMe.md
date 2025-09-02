# Content Extraction - Quick Reference

## Purpose (1-2 lines)
Web content extraction and processing.
Scrapes content from filtered URLs using Firecrawl and converts to markdown.

## Key Capabilities
- `extract_content()` - Main content extraction function
- Concurrent scraping with rate limiting
- Markdown format conversion for downstream processing
- Error handling and fallback mechanisms

## Internal Structure
- `content_extractor.py` - Content extraction logic and Firecrawl integration
- `__init__.py` - Exports extraction functions

## How It Works (5-10 lines max)
1. Receives filtered URL list from filtering layer
2. Creates concurrent scraping tasks with semaphore control
3. Calls Firecrawl scrape endpoint for each URL
4. Converts HTML content to markdown format
5. Returns URL-to-content mapping with error handling

## Events Published
- None (subdomain layer)

## Events Consumed
- None (subdomain layer)

## Key Decisions
- Markdown format for LLM compatibility
- Concurrent processing with rate limiting
- Comprehensive error handling
- Clean content structure for analysis 