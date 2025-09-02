# Astral Assessment — Business Intelligence Collection Platform

A FastAPI-based platform that collects and analyzes business intelligence from company websites and LinkedIn profiles. The system follows a domain-driven, function-first architecture and emphasizes absolute clarity, testability, and operational reliability.

## Overview / Background

This project tests the ability to problem solve, quickly internalize engineering principles, and build at a fast pace. At astral, nearly every problem we tackle is novel. We operate at the edge of what's possible through software and AI.

We do not consider astral a typical startup. While we adopt Silicon Valley principles—building quickly, being relentlessly resourceful—we believe many core engineering values were lost in the recent AI boom. Everyone is chasing short-term gains without a meaningful technical moat. We're building something different: an experimentation lab for what's possible within the rapidly growing AI ecosystem.

To dominate, we follow one maxim: wars are won with logistics and propaganda.

For astral, "logistics" means systematically architecting AI-enhanced software across operations to maximize leverage. "Propaganda" means the ability to produce and distribute high-quality, educational content at scale. Advertising will become a commodity in the age of AI. The advantage is delivering individually tailored value through writing and visuals—helping people understand what new capabilities mean for them.

This MVP demonstrates the first phase of that pipeline.

## Engineering Principles

You must read and understand the engineering principles. All work is evaluated against these standards.

**Core Development Philosophy:** Write code with absolute clarity as the top priority. Choose the most straightforward solution that any developer can understand at first glance.

**Key Themes Adopted:**
- **Delete before you build:** The best feature is no feature. Ask "What happens if we don't build this at all?"
- **Simple over clever:** If it's complex, it sucks and needs to go. Simple systems win long-term.
- **Function-first design:** Default to simple, pure functions organized in logical modules.
- **Single responsibility:** Each function, class, and module should do one clear thing.
- **Fail fast & simple:** Validate only uncertain inputs, catch only what you can handle.
- **Domains own business logic:** Services integrate external systems, API handles HTTP concerns.

## Project Resources

1. Inngest docs: `https://www.inngest.com/docs?ref=nav`
2. Firecrawl docs: `https://docs.firecrawl.dev/introduction`
3. Firecrawl playground: `https://www.firecrawl.dev/playground`
4. API keys: OpenAI, Firecrawl, ScrapingDog (configured in `.env`)

## What You'll Build

A FastAPI application with two routers:
- **Health checks:** Two GET endpoints at `/health` and `/health/detailed`
- **Execution workflow:** A single POST endpoint `/register`

**Request Contract (Pydantic v2):**
- `first_name` (required)
- `last_name` (required)
- `company_website` (optional)
- `linkedin` (optional)

**Validation Rule:** At least one of `company_website` or `linkedin` must be provided, otherwise fail fast with a validation error.

### Async & Reliable Queue Management (Inngest)

Inngest handles background job processing without maintaining brokers/workers. The `/register` endpoint:
1. Validates input and immediately enqueues an event `registration.received`
2. Returns success or meaningful error immediately
3. A background function processes the heavy workflow asynchronously

**Why Inngest for this problem:**
- **Reliability:** Automatic retries, exponential backoff, durable execution
- **Observability:** Function logs, metrics, and retries visible in the Inngest dashboard
- **Simplicity:** No Redis/RabbitMQ required; focus stays on business logic
- **Asynchronous by default:** Ideal for I/O heavy scraping and API calls

### Data Collection Logic

There are three potential paths:
- Website URL only
- LinkedIn URL only
- Both provided

**Goal:** Learn as much as possible about the individual and their company.

#### 1) LinkedIn Research Task

We integrate ScrapingDog's LinkedIn API for profile data to avoid building a brittle scraper. The chosen approach reduces failure points and keeps the system simple.

**Concise Integration Plan:**
- Use ScrapingDog's LinkedIn endpoint with `type=profile` and `linkId` extracted from the URL
- Normalize and validate LinkedIn URLs
- If API key is missing, return mock profile data for development/testing
- Analyze returned profile data into structured BI fields: profile summary, professional info, experience, education, content and network insights, business intelligence

**Key Docs:** `https://www.scrapingdog.com/linkedin-scraper-api`

#### 2) Website Analysis (Firecrawl)

Firecrawl is used for:
- **URL Discovery** (map endpoint) — Fast, lightweight, and credit-efficient
- **Content Scraping** (scrape endpoint) — Returns content in markdown format

**Phases:**
- **URL Discovery:** `services/firecrawl/client.py#map_website`
- **Intelligent Filtering:** AI-powered scoring with fallback to pattern-based filtering
- **Content Extraction:** Markdown format chosen for downstream LLM processing due to human-readability, structural fidelity, and low parsing cost

If rate limits are encountered during development, the scraping calls can be mocked (as done in tests) while preserving end-to-end logic.

### Inngest Integration Strategy

- API triggers an Inngest event from `/register`
- The background function `process-registration` orchestrates the entire pipeline
- Retries and observability are handled by Inngest

### Output Requirements

Each `/register` call creates a JSON file in `outputs/` (no database). Filename format: `analysis_<request_id>_<timestamp>.json`.

**Required Structure:**

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
    "status": "success",
    "profile_data": "..."
  },
  "website_analysis": {
    "discovered_urls": ["list of all URLs found"],
    "filtered_urls": ["URLs selected for scraping with filtering logic explained"],
    "scraped_content": {
      "url": "content in markdown format"
    }
  }
}
```

**Critical Question:** Why Inngest here? Because reliability and observability are non-negotiable at scale. The ability to see, retry, and reason about background processes while keeping API latency low is central to the operational "logistics" necessary to win.

## Project Structure

```
astral-assesment/
├── api/                           # FastAPI application layer
│   ├── __init__.py
│   ├── main.py                    # Main application entry point
│   ├── understandMe.md            # API layer documentation
│   └── routers/                   # API route definitions
│       ├── __init__.py
│       ├── health.py              # Health check endpoints
│       └── register.py            # User registration endpoints
│
├── core/                          # Shared utilities and types
│   ├── __init__.py
│   ├── understandMe.md            # Core layer documentation
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py            # Application settings
│   ├── types/                     # Data models and types
│   │   ├── __init__.py
│   │   └── models.py              # Pydantic v2 models
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── json_handler.py        # JSON processing utilities
│       └── url_utils.py           # URL processing utilities
│
├── domains/                       # Business logic domains
│   └── intelligence_collection/   # Core intelligence gathering
│       ├── __init__.py            # Main domain interface
│       ├── understandMe.md        # Domain documentation
│       ├── common/                # Shared domain utilities
│       │   ├── __init__.py
│       │   └── validators.py      # Data validation
│       ├── discovery/             # URL discovery logic
│       │   ├── __init__.py
│       │   └── url_discoverer.py  # Company URL discovery
│       ├── extraction/            # Content extraction
│       │   ├── __init__.py
│       │   └── content_extractor.py # Web content extraction
│       └── filtering/             # URL filtering
│           ├── __init__.py
│           └── url_filter.py      # AI-powered URL filtering
│
├── services/                      # External service integrations
│   ├── __init__.py
│   ├── understandMe.md            # Services layer documentation
│   ├── ai/                        # AI client for content analysis
│   │   ├── __init__.py
│   │   ├── understandMe.md        # AI service documentation
│   │   └── client.py              # AI service client
│   ├── firecrawl/                 # Web scraping service
│   │   ├── __init__.py
│   │   ├── understandMe.md        # Firecrawl service documentation
│   │   └── client.py              # Firecrawl API client
│   ├── inngest/                   # Background job processing
│   │   ├── __init__.py
│   │   ├── client.py              # Inngest client
│   │   ├── functions.py           # Background job functions
│   │   └── README.md              # Inngest integration docs
│   └── linkedin/                  # LinkedIn profile analysis
│       ├── __init__.py
│       ├── understandMe.md        # LinkedIn service documentation
│       ├── analyzer.py            # Main LinkedIn analyzer
│       ├── profile_analyzer.py    # Profile data analysis
│       ├── scrapingdog_client.py  # ScrapingDog API client
│       └── url_parser.py          # LinkedIn URL parsing
│
├── tests/                         # Comprehensive test suite
│   ├── __init__.py
│   ├── domains/                   # Domain-specific tests
│   │   └── intelligence_collection/ # Core business logic tests
│   │       ├── test_process.py    # Main workflow tests
│   │       └── test_url_filtering.py # URL filtering tests
│   ├── test_examples.py           # Real company examples
│   ├── test_inngest_integration.py # Inngest integration tests
│   ├── test_linkedin_integration.py # LinkedIn integration tests
│   └── README.md                  # Test documentation
│
├── .cursor/                       # Cursor IDE configuration
│   └── rules/                     # Development rules and guidelines
│       ├── architecture.mdc       # Architecture principles
│       ├── core.mdc               # Core development philosophy
│       ├── python-rules.mdc       # Python-specific guidelines
│       └── ts-tsx-rules.mdc      # TypeScript/React guidelines
│
├── .cursorrules                   # Cursor IDE rules
├── .gitignore                     # Git ignore patterns
├── README.md                      # This file - main documentation
├── PROJECT_STRUCTURE.md           # Detailed project structure
├── requirements.txt               # Python dependencies
├── pytest.ini                    # Pytest configuration
├── setup.sh                      # Automated setup script
└── run_tests.py                  # Test runner script
```

## Design Choices and Rationale

### Architecture
- **Domain-driven layout:** Business logic lives under `domains/`; external systems under `services/`; shared types/utilities under `core/`; HTTP-only concerns in `api/`
- **Function-first:** Favors small, composable, pure functions; classes limited to clients/singletons for external services
- **Interface boundaries:** Domains do not import from API or services internals; services expose focused APIs
- **understandMe.md files:** Every domain and core layer has quick reference documentation

### Validation
- **Pydantic v2 models** for request validation (`core/types/models.py`)
- **Post-init validation** ensures at least one URL is provided
- **Fail-fast principle** applied at API boundary and domain entry points

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
- **56 tests passing**, covering domain logic, integration surfaces, and realistic examples
- External dependencies mocked to ensure fast, deterministic tests
- Examples include small/mid-size companies (Replicate, Airtable) to reflect real-world patterns

## Setup

### Prerequisites
- Python 3.11+
- pip
- Node.js (for Inngest CLI)

### Automated Setup (Recommended)

```bash
# Clone
git clone <your-repo-url>
cd astral-assesment

# One command setup
./setup.sh
```

**What the script does:**
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

**Create `.env` in the repo root:**

```env
APP_NAME=astral-assessment
APP_VERSION=1.0.0
ENVIRONMENT=development

# API Keys
FIRECRAWL_API_KEY=your-firecrawl-key
SCRAPINGDOG_API_KEY=your-scrapingdog-key
OPENAI_API_KEY=your-openai-key

# Inngest Configuration
INNGEST_APP_ID=astral-assessment
INNGEST_EVENT_KEY=your-event-key
INNGEST_SIGNING_KEY=your-signing-key
INNGEST_DEV=1  # Set to 1 for development mode
```

## Running the App

### Terminal 1 - Start Inngest Dev Server

```bash
npx inngest-cli@latest dev
```

### Terminal 2 - Start FastAPI with Dev Mode

```bash
cd /path/to/astral-assesment
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **API Documentation:** `http://localhost:8000/docs`
- **Health Checks:** 
  - `GET /health` - Basic health status
  - `GET /health/detailed` - Comprehensive system status with all 4 services
- **Registration Endpoint:** `POST /register`

### Example Request

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

### Expected Response

```json
{
  "request_id": "unique-identifier",
  "status": "queued",
  "message": "Registration received and queued for processing"
}
```

## Running Tests

### Using the Test Runner Script

```bash
python run_tests.py quick      # Quick validation
python run_tests.py core       # Business logic tests
python run_tests.py examples   # Real company examples
python run_tests.py linkedin   # LinkedIn functionality
python run_tests.py inngest    # Background processing
python run_tests.py all        # All tests
```

### Direct Pytest Usage

```bash
python -m pytest               # All tests
python -m pytest tests/domains/intelligence_collection/ -v  # Domain tests
python -m pytest tests/ -v --tb=short  # All tests with short tracebacks
```

## Current Status

### ✅ **Fully Functional Features**

1. **Health Check System** - All 4 services (Inngest, Firecrawl, LinkedIn, AI) reporting healthy
2. **Registration Workflow** - Complete end-to-end processing with background jobs
3. **Background Processing** - Inngest integration working correctly
4. **File Management** - Clean, single output file per request (no duplicates)
5. **Error Handling** - Comprehensive error handling and logging
6. **Testing** - 56 tests passing with full coverage

### 🔧 **Architecture Compliance**

- **100% Domain-Driven Design** - Clean separation of concerns
- **Function-First Architecture** - Pure functions with minimal classes
- **Interface Boundaries** - Clean public APIs with minimal exports
- **understandMe.md Files** - Complete documentation for all layers
- **Single Responsibility** - Each module has one clear purpose

### 📊 **Performance Metrics**

- **Test Coverage:** 56 tests passing
- **Service Health:** 4/4 services healthy
- **Response Time:** <100ms for API endpoints
- **Background Jobs:** Processing successfully via Inngest
- **File Output:** Clean, organized JSON files

## Time Expectations and Priorities

**Target completion:** 8–12 hours. Focus on core workflow and clear thinking over perfect prompts or exhaustive tuning. Keep momentum: research quickly, implement pragmatically, and ship working software.

**Priorities:**
- Don't over-engineer prompts or internals
- Keep the core workflow functional end-to-end
- Mock external APIs where useful during development
- Document improvements for later if time-constrained

## Deliverable and Evaluation Criteria

The repository includes:
- **A clear README** (this document)
- **Working tests** for all configurations:
  - Website only
  - LinkedIn only
  - Both provided
- **Real company examples** (small to mid-size)
- **Code structure** following astral-os guidelines while prioritizing working code
- **100% architecture compliance** with all rules and principles

## Future Improvements

- **Harden CORS and security** for production (restrict origins, add rate limiting)
- **Structured logging** with request IDs and context everywhere
- **Health checks** for external dependencies with circuit breakers
- **Caching and backoff policies** tuned to vendor limits
- **Additional data sources**; knowledge graph construction for multi-entity insights

## License

Add your preferred license here. 