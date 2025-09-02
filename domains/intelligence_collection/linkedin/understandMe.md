# LinkedIn Analysis - Quick Reference

## Purpose (1-2 lines)
LinkedIn profile analysis and intelligence extraction.
Processes LinkedIn URLs and extracts professional insights using ScrapingDog API.

## Key Capabilities
- `analyze_linkedin_profile()` - Main LinkedIn analysis function
- `extract_profile_id()` - LinkedIn URL parsing and validation
- `LinkedInProfileAnalyzer` - Profile data analysis and insights

## Internal Structure
- `analyzer.py` - Main LinkedIn analysis orchestration
- `profile_analyzer.py` - Profile data processing and AI integration
- `url_parser.py` - LinkedIn URL validation and parsing
- `scrapingdog_client.py` - ScrapingDog API integration

## How It Works (5-10 lines max)
1. Validates and parses LinkedIn profile URLs
2. Extracts profile ID using ScrapingDog API
3. Analyzes profile data for professional insights
4. Integrates with AI for enhanced analysis
5. Returns structured analysis with fallback support

## Events Published
- None (subdomain layer)

## Events Consumed
- None (subdomain layer)

## Key Decisions
- ScrapingDog API for reliable profile scraping
- AI integration with fallback analysis
- Clean URL parsing and validation
- Structured output for downstream processing 