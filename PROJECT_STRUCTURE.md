# Project Structure

```
astral-assesment/
├── 📁 api/                           # FastAPI application layer
│   ├── __init__.py
│   ├── main.py                       # Main application entry point
│   └── routers/                      # API route definitions
│       ├── __init__.py
│       ├── health.py                 # Health check endpoints
│       └── register.py               # User registration endpoints
│
├── 📁 core/                          # Shared utilities and types
│   ├── __init__.py
│   ├── config/                       # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py              # Application settings
│   ├── types/                        # Data models and types
│   │   ├── __init__.py
│   │   └── models.py                # Pydantic models
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── json_handler.py           # JSON processing utilities
│       └── url_utils.py              # URL processing utilities
│
├── 📁 domains/                       # Business logic domains
│   └── intelligence_collection/      # Core intelligence gathering
│       ├── __init__.py               # Main domain interface
│       ├── common/                   # Shared domain utilities
│       │   ├── __init__.py
│       │   └── validators.py         # Data validation
│       ├── discovery/                # URL discovery logic
│       │   ├── __init__.py
│       │   └── url_discoverer.py     # Company URL discovery
│       ├── extraction/               # Content extraction
│       │   ├── __init__.py
│       │   └── content_extractor.py  # Web content extraction
│       └── filtering/                # URL filtering
│           ├── __init__.py
│           └── url_filter.py         # AI-powered URL filtering
│
├── 📁 services/                      # External service integrations
│   ├── __init__.py
│   ├── ai/                           # AI client for content analysis
│   │   ├── __init__.py
│   │   └── client.py                 # AI service client
│   ├── firecrawl/                    # Web scraping service
│   │   ├── __init__.py
│   │   └── client.py                 # Firecrawl API client
│   ├── inngest/                      # Background job processing
│   │   ├── __init__.py
│   │   ├── client.py                 # Inngest client
│   │   ├── functions.py              # Background job functions
│   │   └── README.md                 # Inngest integration docs
│   └── linkedin/                     # LinkedIn profile analysis
│       ├── __init__.py
│       ├── analyzer.py                # Main LinkedIn analyzer
│       ├── profile_analyzer.py       # Profile data analysis
│       ├── scrapingdog_client.py     # ScrapingDog API client
│       └── url_parser.py             # LinkedIn URL parsing
│
├── 📁 tests/                         # Comprehensive test suite
│   ├── __init__.py
│   ├── domains/                      # Domain-specific tests
│   │   └── intelligence_collection/  # Core business logic tests
│   │       ├── test_process.py       # Main workflow tests
│   │       └── test_url_filtering.py # URL filtering tests
│   ├── test_examples.py              # Real company examples
│   ├── test_inngest_integration.py   # Inngest integration tests
│   ├── test_linkedin_integration.py  # LinkedIn integration tests
│   └── README.md                     # Test documentation
│
├── 📁 .cursor/                       # Cursor IDE configuration
│   └── rules/                        # Development rules and guidelines
│       ├── architecture.mdc          # Architecture principles
│       ├── core.mdc                  # Core development philosophy
│       ├── python-rules.mdc          # Python-specific guidelines
│       └── ts-tsx-rules.mdc         # TypeScript/React guidelines
│
├── 📄 .cursorrules                   # Cursor IDE rules
├── 📄 .gitignore                     # Git ignore patterns
├── 📄 README.md                      # Main project documentation
├── 📄 DELIVERABLE_SUMMARY.md         # Complete deliverable overview
├── 📄 PROJECT_STRUCTURE.md           # This file - project structure
├── 📄 requirements.txt               # Python dependencies
├── 📄 pytest.ini                    # Pytest configuration
├── 📄 setup.sh                      # Automated setup script
├── 📄 run_tests.py                  # Test runner script
└── 📄 env.example                   # Environment variables template
```

## 🏗️ Architecture Principles

### **Domain-Driven Design**
- **Core Layer**: Shared utilities, configs, and types
- **Domain Modules**: Self-contained business logic
- **Services Layer**: External integrations and cross-cutting concerns
- **API Layer**: HTTP interface and routing

### **Key Design Patterns**
- **Function-First**: Prefer functions over classes
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Services injected where needed
- **Interface Segregation**: Clean boundaries between layers

### **Testing Strategy**
- **Unit Tests**: Business logic in isolation
- **Integration Tests**: Component interactions
- **Real Examples**: Actual company data for realistic testing
- **Mocked Dependencies**: Fast, reliable test execution

## 🔧 Development Workflow

### **1. Setup Environment**
```bash
./setup.sh  # Automated setup
# or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Configuration**
```bash
cp env.example .env
# Edit .env with your API keys
```

### **3. Development**
```bash
uvicorn api.main:app --reload  # Start development server
python run_tests.py all          # Run all tests
python run_tests.py quick        # Quick validation
```

### **4. Testing**
```bash
# Run specific test categories
python run_tests.py core         # Business logic
python run_tests.py examples     # Real company examples
python run_tests.py linkedin     # LinkedIn functionality
python run_tests.py inngest      # Background processing
```

## 📚 Key Files Explained

### **Entry Points**
- **`api/main.py`**: FastAPI application with lifespan management
- **`domains/intelligence_collection/__init__.py`**: Main business logic interface
- **`services/linkedin/analyzer.py`**: LinkedIn profile analysis entry point

### **Configuration**
- **`core/config/settings.py`**: Centralized configuration management
- **`env.example`**: Environment variables template
- **`pytest.ini`**: Test configuration

### **Documentation**
- **`README.md`**: Comprehensive project overview and setup
- **`DELIVERABLE_SUMMARY.md`**: Complete deliverable status
- **`.cursor/rules/`**: Development philosophy and guidelines

## 🎯 Getting Started

1. **Clone the repository**
2. **Run `./setup.sh`** for automated setup
3. **Copy `env.example` to `.env`** and add your API keys
4. **Start the application** with `uvicorn api.main:app --reload`
5. **Run tests** to verify functionality
6. **Explore the API** at `http://localhost:8000/docs`

## 🔍 Understanding the Codebase

### **Start Here**
1. **`README.md`** - Project overview and quick start
2. **`api/main.py`** - Application entry point
3. **`domains/intelligence_collection/__init__.py`** - Core business logic
4. **`tests/`** - Examples of how everything works

### **Key Concepts**
- **Registration Workflow**: User registration → Background processing → Intelligence collection
- **Multi-Source Analysis**: Website + LinkedIn profile analysis
- **Async Processing**: Inngest for background job management
- **Domain Isolation**: Clean separation of business logic

This structure follows the astral-os architecture principles with clear domain boundaries, function-first design, and comprehensive testing coverage. 