# Common Domain Utils - Quick Reference

## Purpose (1-2 lines)
Shared utilities and validation within intelligence collection domain.
Provides common functions used across domain submodules.

## Key Capabilities
- `validate_data_source()` - Data source validation logic
- Common validation and utility functions
- Shared constants and helper methods

## Internal Structure
- `validators.py` - Domain-specific validation logic
- `__init__.py` - Exports common functions

## How It Works (5-10 lines max)
1. Provides validation functions for domain data
2. Ensures consistent validation across submodules
3. Centralizes common utility functions
4. Maintains domain-specific business rules
5. Used by discovery, filtering, and extraction modules

## Events Published
- None (common layer)

## Events Consumed
- None (common layer)

## Key Decisions
- Centralized validation logic
- Domain-specific business rules
- Reusable utility functions
- Clean separation of concerns 