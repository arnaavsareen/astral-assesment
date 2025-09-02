# Core Layer - Quick Reference

## Purpose (1-2 lines)
Shared utilities, configuration, and types used across the application.
Foundation layer providing common functionality without business logic.

## Key Capabilities
- `config/settings.py` - Application configuration from environment
- `types/models.py` - Pydantic v2 models for data validation
- `utils/json_handler.py` - Async JSON file operations
- `utils/url_utils.py` - URL normalization and validation
- `clients/` - External service clients (Firecrawl, ScrapingDog, OpenAI)

## Internal Structure
- `config/` - Settings and environment management
- `types/` - Data models and validation schemas
- `utils/` - Pure utility functions with no side effects
- `clients/` - Singleton API clients for external services

## How It Works (5-10 lines max)
1. Settings load from .env on startup via pydantic-settings
2. Models validate data at API boundaries using Pydantic v2
3. Utilities provide pure functions for common operations
4. Clients use singleton pattern for expensive API connections
5. All domains and services can depend on core

## Events Published
- None (foundation layer)

## Events Consumed
- None (foundation layer)

## Key Decisions
- Pydantic v2 for all data validation
- Settings from environment variables only
- Pure functions with no external dependencies
- Singleton pattern for stateless API clients
- Type hints on everything for clarity 