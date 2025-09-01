# Core Architecture Quick Reference

## Domain-Driven Design Layers

**Core Layer** - Pure business logic, no external dependencies
- `config/` - Application configuration and settings
- `types/` - Pydantic models for data validation
- `utils/` - Pure utility functions

## Key Patterns

**Settings Management**
- Pydantic v2 Settings for type-safe config
- Environment variables loaded from .env
- Validation on startup

**Data Models**
- Pydantic v2 models with strict validation
- HttpUrl fields for URL validation
- Custom validators for business rules

**File Operations**
- Async JSON handling for analysis outputs
- Structured output to outputs/ directory
- Error handling with context

**URL Utilities**
- URL normalization for consistency
- Business intelligence URL detection
- Pure functions with no side effects

## Development Principles

- Functions under 50 lines max
- Single responsibility per function
- Descriptive names over short ones
- Fail fast with clear error messages
- No external dependencies in core layer 