# Core Utils - Quick Reference

## Purpose (1-2 lines)
Pure utility functions for common operations.
Provides reusable, stateless functions for URL processing and JSON operations.

## Key Capabilities
- `url_utils.py` - URL normalization and validation
- `json_handler.py` - Async JSON file operations
- Pure functions with no side effects

## Internal Structure
- `url_utils.py` - URL processing utilities
- `json_handler.py` - File I/O operations
- `__init__.py` - Exports utility functions

## How It Works (5-10 lines max)
1. Pure functions with no external dependencies
2. URL utilities handle normalization and validation
3. JSON handler provides async file operations
4. All functions are stateless and testable
5. Used by domains and services for common operations

## Events Published
- None (utils layer)

## Events Consumed
- None (utils layer)

## Key Decisions
- Pure functions for testability
- No external dependencies
- Async support for file operations
- Clear separation of concerns 