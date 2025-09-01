# Test Suite Documentation

This document explains the testing strategy and structure for the astral-assessment project.

## Testing Philosophy

Following the development philosophy of simplicity and clarity:

1. **Test the domain in isolation** - Mock external dependencies
2. **Test public interfaces only** - Don't test internal implementation details
3. **Use descriptive test names** - Clear about what is being tested
4. **Keep tests simple** - One assertion per test concept
5. **Mock external services** - No real API calls in tests

## Test Structure

```
tests/
├── __init__.py
├── domains/
│   ├── __init__.py
│   └── intelligence_collection/
│       ├── __init__.py
│       └── test_process.py
└── README.md
```

## Test Categories

### 1. Domain Tests (`tests/domains/`)
- **Purpose**: Test business logic in isolation
- **Scope**: Public domain functions only
- **Dependencies**: All external services mocked
- **Examples**: `process_registration`, validation logic

### 2. Integration Tests (Future)
- **Purpose**: Test component interactions
- **Scope**: API endpoints with mocked external services
- **Dependencies**: Real FastAPI app, mocked external APIs

### 3. End-to-End Tests (Future)
- **Purpose**: Test complete workflows
- **Scope**: Full system with real external services
- **Dependencies**: All services running

## Current Test Coverage

### Intelligence Collection Domain (`test_process.py`)

**Test Cases:**

1. **`test_website_only_registration`**
   - Tests registration with only company website
   - Verifies website analysis workflow
   - Mocks URL discovery, filtering, and content extraction

2. **`test_linkedin_only_registration`**
   - Tests registration with only LinkedIn URL
   - Verifies LinkedIn analysis workflow
   - Mocks LinkedIn profile analysis

3. **`test_both_urls_provided`**
   - Tests registration with both website and LinkedIn
   - Verifies both analysis workflows run
   - Tests complete end-to-end processing

4. **`test_missing_urls_raises_error`**
   - Tests validation error when no URLs provided
   - Verifies proper error handling
   - Tests Pydantic validation

5. **`test_save_analysis_failure_does_not_fail_process`**
   - Tests graceful handling of save failures
   - Verifies process continues even if saving fails
   - Tests error isolation

6. **`test_discovery_failure_handled_gracefully`**
   - Tests handling of empty discovery results
   - Verifies graceful degradation
   - Tests empty state handling

7. **`test_request_id_uniqueness`**
   - Tests unique request ID generation
   - Verifies UUID generation works correctly
   - Tests idempotency

8. **`test_timestamp_is_recent`**
   - Tests timestamp accuracy
   - Verifies timezone handling
   - Tests data integrity

## Mocking Strategy

### External Dependencies Mocked

1. **FirecrawlClient** - Web scraping service
   - `discover_company_urls()` - URL discovery
   - `extract_content()` - Content extraction

2. **LinkedIn Analyzer** - Profile analysis service
   - `analyze_linkedin_profile()` - Profile analysis

3. **File System** - JSON storage
   - `save_analysis()` - Result persistence

### Mock Data Fixtures

```python
@pytest.fixture
def sample_website_data() -> Dict[str, Any]:
    """Sample registration data with website only."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "company_website": "https://example.com",
        "linkedin": None
    }
```

### Mock Response Fixtures

```python
@pytest.fixture
def mock_discovered_urls() -> list:
    """Mock discovered URLs from website crawling."""
    return [
        {"url": "https://example.com/about", "title": "About Us"},
        {"url": "https://example.com/services", "title": "Services"},
        # ... more URLs
    ]
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/domains/intelligence_collection/test_process.py

# Run with verbose output
python -m pytest -v

# Run specific test
python -m pytest tests/domains/intelligence_collection/test_process.py::TestProcessRegistration::test_website_only_registration
```

### Test Discovery

```bash
# List all tests without running
python -m pytest --collect-only

# List tests in specific file
python -m pytest tests/domains/intelligence_collection/test_process.py --collect-only
```

### Test Configuration

The project uses `pytest.ini` for configuration:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    asyncio: marks tests as async
    slow: marks tests as slow
    integration: marks tests as integration tests
asyncio_mode = auto
```

## Test Best Practices

### 1. **Arrange-Act-Assert Pattern**
```python
# Arrange
registration_data = RegistrationRequest(**sample_website_data)

# Act
result = await process_registration(registration_data)

# Assert
assert isinstance(result, AnalysisOutput)
assert result.request_id is not None
```

### 2. **Descriptive Test Names**
```python
async def test_website_only_registration(self):
    """Test registration with website URL only."""
```

### 3. **Comprehensive Mocking**
```python
with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
     patch('domains.intelligence_collection.filter_valuable_urls', return_value=mock_filtered_urls) as mock_filter:
    # Test implementation
```

### 4. **Error Testing**
```python
with pytest.raises(ValueError, match="At least one URL.*must be provided"):
    await process_registration(registration_data)
```

### 5. **Edge Case Testing**
```python
# Test empty results
mock_discover.return_value = []

# Test save failures
mock_save.side_effect = Exception("Save failed")
```

## Future Test Enhancements

### 1. **API Integration Tests**
- Test FastAPI endpoints with mocked services
- Verify request/response handling
- Test error responses

### 2. **Inngest Function Tests**
- Test background job processing
- Verify event handling
- Test retry logic

### 3. **Performance Tests**
- Test processing time limits
- Verify memory usage
- Test concurrent processing

### 4. **Data Validation Tests**
- Test edge cases in data validation
- Verify Pydantic model behavior
- Test URL normalization

## Continuous Integration

### GitHub Actions (Future)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest
```

## Debugging Tests

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python path includes project root

2. **Mock Assertion Failures**
   - Verify mock call arguments match exactly
   - Check for URL normalization differences

3. **Async Test Issues**
   - Use `@pytest.mark.asyncio` decorator
   - Ensure proper async/await usage

### Debug Commands

```bash
# Run with detailed output
python -m pytest -v --tb=long

# Run single test with debugger
python -m pytest tests/domains/intelligence_collection/test_process.py::TestProcessRegistration::test_website_only_registration --pdb

# Run with coverage (future)
python -m pytest --cov=domains --cov-report=html
```

## Test Data Management

### Fixture Organization
- **Sample Data**: Realistic test inputs
- **Mock Responses**: Expected external service responses
- **Edge Cases**: Boundary conditions and error scenarios

### Test Data Isolation
- Each test uses fresh fixtures
- No shared state between tests
- Clean setup and teardown

This testing strategy ensures the codebase remains reliable, maintainable, and follows the project's development philosophy of simplicity and clarity. 