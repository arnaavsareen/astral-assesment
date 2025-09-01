# Intelligence Collection Domain

## Purpose

The Intelligence Collection domain orchestrates the end-to-end process of gathering and analyzing business intelligence from user-provided data sources (websites and LinkedIn profiles).

## Domain Boundaries

**What's Inside:**
- Registration data validation and processing
- URL discovery and filtering for business intelligence value
- Content extraction and analysis orchestration
- Result aggregation and output generation

**What's Outside:**
- External API integrations (handled by services layer)
- Data persistence (handled by core utils)
- HTTP request handling (handled by API layer)
- Background job processing (handled by Inngest services)

## Core Workflow

```
RegistrationRequest → Validate → Discover → Filter → Extract → Analyze → Save → AnalysisOutput
```

1. **Validate**: Ensure at least one data source (website or LinkedIn) is provided
2. **Discover**: Find all URLs on the website using Firecrawl
3. **Filter**: Identify URLs with business intelligence value
4. **Extract**: Scrape content from valuable URLs
5. **Analyze**: Process LinkedIn profiles and website content
6. **Save**: Store analysis results to filesystem
7. **Return**: Structured AnalysisOutput with all findings

## Key Principles

- **Single Responsibility**: Each function has one clear purpose
- **Fail Fast**: Validate inputs early and clearly
- **Pure Functions**: Business logic should be testable and predictable
- **Clear Boundaries**: Domain doesn't know about external services directly
- **Composable**: Functions can be combined in different workflows

## Data Flow

**Input**: `RegistrationRequest` with user data and URLs
**Output**: `AnalysisOutput` with structured analysis results
**Side Effects**: Files saved to outputs/ directory

## Dependencies

- **Core Layer**: For data models and utilities
- **Services Layer**: For external API calls (Firecrawl, LinkedIn)
- **No Direct Dependencies**: On HTTP, database, or background jobs 