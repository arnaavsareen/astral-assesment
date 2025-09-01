# Astral Assessment — Business Intelligence Collection Platform

A FastAPI-based platform that collects and analyzes business intelligence from company websites and LinkedIn profiles. The system follows a domain-driven, function-first architecture and emphasizes clarity, testability, and operational reliability.

## Overview / Background

This project tests the ability to problem solve, quickly internalize engineering principles, and build at a fast pace. At astral, nearly every problem we tackle is novel. We operate at the edge of what’s possible through software and AI.

We do not consider astral a typical startup. While we adopt Silicon Valley principles—building quickly, being relentlessly resourceful—we believe many core engineering values were lost in the recent AI boom. Everyone is chasing short-term gains without a meaningful technical moat. We’re building something different: an experimentation lab for what’s possible within the rapidly growing AI ecosystem.

To dominate, we follow one maxim: wars are won with logistics and propaganda.

For astral, “logistics” means systematically architecting AI-enhanced software across operations to maximize leverage. “Propaganda” means the ability to produce and distribute high-quality, educational content at scale. Advertising will become a commodity in the age of AI. The advantage is delivering individually tailored value through writing and visuals—helping people understand what new capabilities mean for them.

This MVP demonstrates the first phase of that pipeline.

## Engineering Principles

You must read and understand the engineering principles. All work is evaluated against these standards.

Astral-OS principles: `https://www.notion.so/astral-os-25e0798f38db803289a3c9a9d2d099c8?pvs=21`

Key themes adopted here:
- Delete before you build; prefer no feature to a complex feature
- Simple over clever; function-first design; single responsibility
- Fail fast; validate only uncertain inputs; meaningful logging
- Domains own business logic; services integrate external systems

## Project Resources

1. Inngest docs: `https://www.inngest.com/docs?ref=nav`
2. Firecrawl docs: `https://docs.firecrawl.dev/introduction`
3. Firecrawl playground: `https://www.firecrawl.dev/playground`
4. API keys: OpenAI or Anthropic (on request)

## What You’ll Build

A FastAPI application with two routers:
- Health checks: two GET endpoints at `/health` and `/health/detailed`
- Execution workflow: a single POST endpoint `/register`

Request contract (Pydantic v2):
- `first_name` (required)
- `last_name` (required)
- `company_website` (optional)
- `linkedin` (optional)

Validation rule: At least one of `company_website` or `linkedin` must be provided, otherwise fail fast with a validation error.

### Async & Reliable Queue Management (Inngest)

Inngest is used to handle background job processing without maintaining brokers/workers. The `/register` endpoint:
1. Validates input and immediately enqueues an event `registration.received`
2. Returns success or meaningful error immediately
3. A background function processes the heavy workflow asynchronously

Why Inngest for this problem:
- Reliability: automatic retries, exponential backoff, durable execution
- Observability: function logs, metrics, and retries visible in the Inngest dashboard
- Simplicity: no Redis/RabbitMQ required; focus stays on business logic
- Asynchronous by default: ideal for I/O heavy scraping and API calls

### Data Collection Logic

There are three potential paths:
- Website URL only
- LinkedIn URL only
- Both provided

Goal: Learn as much as possible about the individual and their company.

#### 1) LinkedIn Research Task

We integrate ScrapingDog’s LinkedIn API for profile data to avoid building a brittle scraper. The chosen approach reduces failure points and keeps the system simple. See `services/linkedin/scrapingdog_client.py`. We also provide `services/linkedin/profile_analyzer.py` to extract structured business intelligence from the API response.

Concise integration plan:
- Use ScrapingDog’s LinkedIn endpoint with `type=profile` and `linkId` extracted from the URL
- Normalize and validate LinkedIn URLs (see `services/linkedin/url_parser.py`)
- If API key is missing, return mock profile data for development/testing
- Analyze returned profile data into structured BI fields: profile summary, professional info, experience, education, content and network insights, business intelligence

Key docs: `https://www.scrapingdog.com/linkedin-scraper-api`

#### 2) Website Analysis (Firecrawl)

Firecrawl is used for:
- URL discovery (map endpoint) — fast, lightweight, and credit-efficient
- Content scraping (scrape endpoint) — returns content in markdown format

Phases:
- URL Discovery: `services/firecrawl/client.py#map_website`
- Intelligent Filtering: AI-powered scoring with fallback to pattern-based filtering (`domains/intelligence_collection/filtering/url_filter.py`)
- Content Extraction: Markdown format chosen for downstream LLM processing due to human-readability, structural fidelity, and low parsing cost (`domains/intelligence_collection/extraction/content_extractor.py`)

If rate limits are encountered during development, the scraping calls can be mocked (as done in tests) while preserving end-to-end logic.

### Inngest Integration Strategy

- API triggers an Inngest event from `/register`
- The background function `process-registration` orchestrates the entire pipeline
- Retries and observability are handled by Inngest

### Output Requirements

Each `/register` call creates a JSON file in `outputs/` (no database). Filename format: `analysis_<request_id>_<timestamp>.json`.

Required structure:

```json
{
  "request_id": "unique-identifier",
  "timestamp": "2025-08-31T14:30:22Z",
  "input_data": {
    "first_name": "...",
    "last_name": "...",
    "company_website": "...",
    "linkedin": "..."
  },
  "linkedin_analysis": {
    "status": "not_implemented"
  },
  "website_analysis": {
    "discovered_urls": ["list of all URLs found"],
    "filtered_urls": ["URLs selected for scraping with filtering logic explained"],
    "scraped_content": {
      "url": "content in your chosen format"
    }
  }
}
```

Critical question: Why Inngest here? Because reliability and observability are non-negotiable at scale. The ability to see, retry, and reason about background processes while keeping API latency low is central to the operational “logistics” necessary to win.

## Project Structure

```
astral-assesment/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── routers/
│       ├── __init__.py
│       ├── health.py
│       └── register.py
│
├── core/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── types/
│   │   ├── __init__.py
│   │   └── models.py
│   └── utils/
│       ├── __init__.py
│       ├── json_handler.py
│       └── url_utils.py
│
├── domains/
│   └── intelligence_collection/
│       ├── __init__.py
│       ├── common/
│       │   ├── __init__.py
│       │   └── validators.py
│       ├── discovery/
│       │   ├── __init__.py
│       │   └── url_discoverer.py
│       ├── extraction/
│       │   ├── __init__.py
│       │   └── content_extractor.py
│       └── filtering/
│           ├── __init__.py
│           └── url_filter.py
│
├── services/
│   ├── __init__.py
│   ├── ai/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── firecrawl/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── inngest/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── functions.py
│   │   └── README.md
│   └── linkedin/
│       ├── __init__.py
│       ├── analyzer.py
│       ├── profile_analyzer.py
│       ├── scrapingdog_client.py
│       └── url_parser.py
│
├── tests/
│   ├── __init__.py
│   ├── domains/
│   │   └── intelligence_collection/
│   │       ├── test_process.py
│   │       └── test_url_filtering.py
│   ├── test_examples.py
│   ├── test_inngest_integration.py
│   ├── test_linkedin_integration.py
│   └── README.md
│
├── .cursor/
│   └── rules/
│       ├── architecture.mdc
│       ├── core.mdc
│       ├── python-rules.mdc
│       └── ts-tsx-rules.mdc
│
├── .cursorrules
├── .gitignore
├── README.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── pytest.ini
├── setup.sh
└── run_tests.py
```

## Design Choices and Rationale

### Architecture
- Domain-driven layout: business logic lives under `domains/`; external systems under `services/`; shared types/utilities under `core/`; HTTP-only concerns in `api/`
- Function-first: favors small, composable, pure functions; classes limited to clients/singletons for external services
- Interface boundaries: domains do not import from API or services internals; services expose focused APIs

### Validation
- Pydantic v2 models for request validation (`core/types/models.py`)
- Post-init validation ensures at least one URL is provided
- Fail-fast principle applied at API boundary and domain entry points

### Inngest
- Event `registration.received` queues heavy work without blocking API
- Function `process-registration` orchestrates domain workflow with retries and logging
- Chosen over ad-hoc background tasks for durability and observability

### Firecrawl
- Map endpoint for fast URL discovery with minimal credits
- Scrape endpoint for markdown extraction suitable for downstream LLM processing
- Clear separation of concerns: discovery → filtering → extraction

### LinkedIn
- ScrapingDog used to avoid reinventing scraping; minimizes fragility and maintenance
- URL parsing/normalization centralizes correctness and testability
- Analyzer transforms raw data into BI structures aligned with business questions

### Testing
- 56 tests, covering domain logic, integration surfaces, and realistic examples
- External dependencies mocked to ensure fast, deterministic tests
- Examples include small/mid-size companies (Replicate, Airtable) to reflect real-world patterns

## Setup

### Prerequisites
- Python 3.11+
- pip

### Automated Setup (recommended)

```bash
# Clone
git clone <your-repo-url>
cd astral-assesment

# One command setup
./setup.sh
```

What the script does:
- Verifies Python version
- Creates and activates a virtual environment
- Installs dependencies
- Generates a `.env` template if missing
- Runs a smoke test

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the repo root (values can be empty during dev):

```env
APP_NAME=astral-assessment
APP_VERSION=1.0.0
ENVIRONMENT=development

FIRECRAWL_API_KEY=
SCRAPINGDOG_API_KEY=
INNGEST_EVENT_KEY=
INNGEST_SERVE_URL=
```

## Running the App

```bash
uvicorn api.main:app --reload
```

API docs: `http://localhost:8000/docs`

Health checks:
- `GET /health`
- `GET /health/detailed`

Register endpoint:
- `POST /register`

Example request:

```http
POST /register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "company_website": "https://example.com",
  "linkedin": "https://linkedin.com/in/johndoe"
}
```

## Running Tests

Using the test runner script:

```bash
python run_tests.py quick
python run_tests.py core
python run_tests.py examples
python run_tests.py linkedin
python run_tests.py inngest
python run_tests.py all
```

Or directly with pytest:

```bash
python -m pytest
```

## Time Expectations and Priorities

Target completion: 8–12 hours. Focus on core workflow and clear thinking over perfect prompts or exhaustive tuning. Keep momentum: research quickly, implement pragmatically, and ship working software.

Priorities:
- Don’t over-engineer prompts or internals
- Keep the core workflow functional end-to-end
- Mock external APIs where useful during development
- Document improvements for later if time-constrained

## Deliverable and Evaluation Criteria

The repository includes:
- A clear README (this document)
- Working tests for all configurations:
  - Website only
  - LinkedIn only
  - Both provided
- Real company examples (small to mid-size)
- Code structure following astral-os guidelines while prioritizing working code

## Future Improvements

- Harden CORS and security for production (restrict origins, add rate limiting)
- Structured logging with request IDs and context everywhere
- Health checks for external dependencies with circuit breakers
- Caching and backoff policies tuned to vendor limits
- Additional data sources; knowledge graph construction for multi-entity insights

## License

Add your preferred license here. 