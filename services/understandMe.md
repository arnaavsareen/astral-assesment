# Services Layer - Quick Reference

## Purpose (1-2 lines)
External service integrations and cross-cutting concerns.
Handles API clients, background jobs, and external dependencies.

## Key Capabilities
- `ai/` - OpenAI integration for intelligent analysis
- `firecrawl/` - Web scraping and URL discovery
- `linkedin/` - Profile analysis and intelligence extraction
- `inngest/` - Background job processing and orchestration

## Internal Structure
- `ai/` - AI service client with singleton pattern
- `firecrawl/` - Web scraping API client
- `linkedin/` - LinkedIn profile analysis tools
- `inngest/` - Background job management

## How It Works (5-10 lines max)
1. Each service provides clean, focused APIs
2. Singleton patterns for expensive clients
3. Comprehensive error handling and logging
4. Async support for performance
5. Clean separation from business logic

## Events Published
- None (service layer, not domain)

## Events Consumed
- None (service layer, not domain)

## Key Decisions
- Singleton pattern for stateless API clients
- Async-first design for performance
- Comprehensive error handling and fallbacks
- Clean interfaces for domain consumption 