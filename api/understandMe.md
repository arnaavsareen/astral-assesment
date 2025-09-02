# API Layer - Quick Reference

## Purpose (1-2 lines)
HTTP interface layer exposing domain functionality through REST endpoints.
Handles request/response, triggers background jobs, no business logic.

## Key Capabilities
- `/health` - Basic health check endpoint
- `/health/detailed` - Comprehensive system status
- `/register` - User registration triggering background processing
- `/docs` - OpenAPI documentation and testing interface

## Internal Structure
- `main.py` - FastAPI application setup and lifespan management
- `routers/` - Endpoint definitions grouped by concern
- `routers/health.py` - Health check endpoints
- `routers/register.py` - Registration endpoint

## How It Works (5-10 lines max)
1. FastAPI app receives HTTP request
2. Router validates input using Pydantic models
3. Triggers Inngest event for background processing
4. Returns immediate response with request_id
5. Background job processes asynchronously

## Events Published
- None (triggers Inngest events)

## Events Consumed
- None (HTTP layer)

## Key Decisions
- FastAPI for modern async Python web framework
- Immediate responses with background processing
- Pydantic validation at API boundaries
- No business logic in API layer 