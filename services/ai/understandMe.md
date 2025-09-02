# AI Service - Quick Reference

## Purpose (1-2 lines)
AI-powered URL scoring and business intelligence analysis using OpenAI.
Provides intelligent filtering and classification of web content.

## Key Capabilities
- `ai_client.score_urls_for_business_intelligence()` - AI-powered URL scoring
- `AIClient` - Singleton client for OpenAI operations
- Intelligent prompt building and response parsing
- Fallback handling when AI fails

## Internal Structure
- `client.py` - OpenAI API client with singleton pattern
- `__init__.py` - Clean public API exports

## How It Works (5-10 lines max)
1. Client receives URLs and company context
2. Builds intelligent scoring prompt for OpenAI
3. Makes API call with proper error handling
4. Parses and validates AI response
5. Returns scored URLs with categories and reasoning
6. Handles failures gracefully with logging

## Events Published
- None (service layer, not domain)

## Events Consumed
- None (service layer, not domain)

## Key Decisions
- Singleton pattern for expensive API client
- OpenAI GPT-4o-mini for cost-effective scoring
- Structured JSON responses for reliability
- Comprehensive error handling and fallbacks 