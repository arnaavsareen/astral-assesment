# Core Types - Quick Reference

## Purpose (1-2 lines)
Data models and validation schemas.
Pydantic v2 models for API request/response validation and data structures.

## Key Capabilities
- `models.py` - RegistrationRequest and AnalysisOutput models
- Pydantic v2 validation with custom validators
- Type-safe data structures for domain operations

## Internal Structure
- `models.py` - Pydantic model definitions
- `__init__.py` - Exports all model classes

## How It Works (5-10 lines max)
1. Models define data contracts for API boundaries
2. Pydantic v2 handles validation and serialization
3. Custom validators ensure business rules (e.g., at least one URL)
4. Models used throughout domain and API layers
5. Type hints provide compile-time safety

## Events Published
- None (types layer)

## Events Consumed
- None (types layer)

## Key Decisions
- Pydantic v2 for all data validation
- Custom validators for business rules
- Type hints everywhere for clarity
- Models as single source of truth for data contracts 