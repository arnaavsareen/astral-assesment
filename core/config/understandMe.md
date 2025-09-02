# Core Config - Quick Reference

## Purpose (1-2 lines)
Application configuration and environment management.
Centralized settings loading from environment variables and .env files.

## Key Capabilities
- `settings.py` - Pydantic settings with environment loading
- Environment variable validation and defaults
- Type-safe configuration access

## Internal Structure
- `settings.py` - Settings class with environment loading
- `__init__.py` - Exports settings instance

## How It Works (5-10 lines max)
1. Settings class inherits from pydantic-settings BaseSettings
2. Automatically loads from .env file and environment variables
3. Validates and provides type-safe access to all config
4. Sensible defaults for development
5. Single source of truth for all application settings

## Events Published
- None (config layer)

## Events Consumed
- None (config layer)

## Key Decisions
- Pydantic-settings for type-safe configuration
- Environment variables as primary config source
- Sensible defaults for development
- Single settings instance across application 