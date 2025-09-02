# URL Filtering - Quick Reference

## Purpose (1-2 lines)
AI-powered URL filtering for business intelligence value.
Scores and classifies URLs to identify high-value content for analysis.

## Key Capabilities
- `filter_valuable_urls()` - Main URL filtering function
- AI-powered scoring with OpenAI integration
- Fallback to pattern-based filtering
- Diversity algorithm for balanced results

## Internal Structure
- `url_filter.py` - URL filtering logic and AI integration
- `__init__.py` - Exports filtering functions

## How It Works (5-10 lines max)
1. Receives list of discovered URLs from discovery layer
2. Uses AI to score URLs for business intelligence value
3. Applies diversity algorithm for balanced category coverage
4. Falls back to pattern-based filtering if AI fails
5. Returns ranked list of URLs with scores and reasons

## Events Published
- None (subdomain layer)

## Events Consumed
- None (subdomain layer)

## Key Decisions
- AI-powered scoring for intelligent filtering
- Diversity algorithm for balanced results
- Fallback mechanisms for reliability
- Clear scoring explanations for transparency 