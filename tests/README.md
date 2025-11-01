# Test Suite Documentation

This directory contains comprehensive unit tests for the Financial Asset Relationship Database.

## Test Coverage

### Python Backend Tests

#### `unit/test_api_main.py`
Comprehensive tests for the FastAPI backend (`api/main.py`):
- **CORS Configuration**: Tests for origin validation and security
- **Graph Initialization**: Thread-safety and singleton behavior
- **All API Endpoints**: Root, health, assets, relationships, metrics, visualization
- **Error Handling**: 404s, 500s, malformed requests
- **Concurrency**: Multi-threaded request handling
- **Pydantic Models**: Response validation

**Test Count**: 60+ test cases covering all endpoints and edge cases

**Run with**: `pytest tests/unit/test_api_main.py -v`

#### `unit/test_config_validation.py`
Configuration file validation tests:
- JSON syntax validation
- Required fields verification
- Configuration consistency checks

**Run with**: `pytest tests/unit/test_config_validation.py -v`

### Frontend Tests

#### `frontend/__tests__/lib/api.test.ts`
Comprehensive tests for the API client library (`app/lib/api.ts`):
- **All API Methods**: Health check, assets, relationships, metrics, visualization
- **Request Parameters**: Filters, pagination, query parameters
- **Response Validation**: Type checking and structure validation
- **Error Handling**: Network errors, HTTP errors, timeouts
- **Axios Configuration**: Base URL, headers, interceptors

**Test Count**: 50+ test cases covering all API client methods

**Run with**: 
```bash
cd frontend
npm test
```

## Running Tests

### Python Tests (Backend)

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=src

# Run specific test file
pytest tests/unit/test_api_main.py

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_assets"
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- api.test.ts
```

## Test Structure