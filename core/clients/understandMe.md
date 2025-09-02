# Core Clients - Quick Reference

## Purpose (1-2 lines)
Singleton API clients for external services.
Provides clean interfaces for Firecrawl, ScrapingDog, and OpenAI integrations.

## Key Capabilities
- `firecrawl_client` - Web scraping and URL discovery
- `scrapingdog_client` - LinkedIn profile scraping
- `ai_client` - OpenAI integration for content analysis

## Internal Structure
- `firecrawl.py` - Firecrawl web scraping client
- `scrapingdog.py` - ScrapingDog LinkedIn API client
- `openai.py` - OpenAI AI service client
- `__init__.py` - Exports all client instances

## How It Works (5-10 lines max)
1. Each client uses singleton pattern for connection reuse
2. API keys loaded from core config settings
3. Comprehensive error handling and retry logic
4. Async support for performance
5. Mock data fallbacks when API keys missing

## Events Published
- None (client layer)

## Events Consumed
- None (client layer)

## Key Decisions
- Singleton pattern for expensive API connections
- Mock data fallbacks for development/testing
- Async-first design for performance
- Clean error handling and logging 