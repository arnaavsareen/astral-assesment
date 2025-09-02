# Inngest Service - Quick Reference

## Purpose (1-2 lines)
Background job processing and workflow orchestration.
Handles asynchronous processing of registration requests via Inngest.

## Key Capabilities
- `inngest_client` - Event publishing and workflow management
- `process-registration` - Background job function
- Event-driven architecture for reliable job processing

## Internal Structure
- `client.py` - Inngest client singleton instance
- `functions.py` - Background job function definitions
- `README.md` - Detailed integration documentation

## How It Works (5-10 lines max)
1. API triggers `registration.received` event
2. Inngest routes event to `process-registration` function
3. Function orchestrates domain workflow asynchronously
4. Automatic retries and exponential backoff
5. Full observability through Inngest dashboard

## Events Published
- `registration.received` - Triggers background processing

## Events Consumed
- None (service layer)

## Key Decisions
- Inngest for reliable background job processing
- Event-driven architecture for decoupling
- Automatic retries and observability
- Clean separation from business logic 