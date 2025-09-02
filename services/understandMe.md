# Services Layer - Quick Reference

## Purpose (1-2 lines)
External service integrations and cross-cutting concerns.
Handles background jobs and external dependencies.

## Key Capabilities
- `inngest/` - Background job processing and orchestration
- `inngest/client.py` - Inngest client for event publishing
- `inngest/functions.py` - Background job function definitions

## Internal Structure
- `inngest/` - Background job management with Inngest
- `inngest/client.py` - Singleton Inngest client instance
- `inngest/functions.py` - Workflow function definitions

## How It Works (5-10 lines max)
1. Inngest client publishes events for background processing
2. Functions define workflows triggered by specific events
3. Singleton pattern for expensive client connections
4. Async support for performance and scalability
5. Clean separation from business logic

## Events Published
- `registration.received` - Triggers background processing

## Events Consumed
- None (service layer)

## Key Decisions
- Inngest for reliable background job processing
- Singleton pattern for stateless clients
- Async-first design for performance
- Clean interfaces for domain consumption 