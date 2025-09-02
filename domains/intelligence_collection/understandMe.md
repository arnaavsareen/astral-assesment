# Intelligence Collection Domain - Quick Reference

## Purpose (1-2 lines)
Orchestrates end-to-end business intelligence gathering from websites and LinkedIn profiles.
Processes user registrations and generates comprehensive analysis reports.

## Key Capabilities
- `process_registration()` - Main workflow orchestration
- `discover_company_urls()` - Website URL discovery
- `filter_valuable_urls()` - AI-powered URL filtering
- `extract_content()` - Content scraping and processing
- `analyze_linkedin_profile()` - LinkedIn profile analysis

## Internal Structure
- `common/` - Shared domain utilities and validation
- `discovery/` - URL discovery using Firecrawl
- `filtering/` - AI-powered URL scoring and classification
- `extraction/` - Content extraction and processing
- `linkedin/` - LinkedIn profile analysis and parsing

## How It Works (5-10 lines max)
1. User calls `process_registration()` with website/LinkedIn URLs
2. Discovers all URLs on company website using Firecrawl
3. Filters URLs for business intelligence value using AI
4. Extracts content from valuable URLs in markdown format
5. Analyzes LinkedIn profiles using ScrapingDog API
6. Returns structured AnalysisOutput with all findings

## Events Published
- None (domain layer)

## Events Consumed
- None (domain layer)

## Key Decisions
- Pure functions for testability and composability
- Clear separation from external services
- Fail-fast validation at domain boundaries
- Markdown format for downstream LLM processing 