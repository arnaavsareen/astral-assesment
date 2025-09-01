# Inngest Integration

This document explains the Inngest integration for background job processing in the astral-assessment project.

## Overview

Inngest is an event-driven durable execution platform that provides reliable background job processing without managing infrastructure like Redis or RabbitMQ. It's perfect for this project because it handles the complex parts of background job processing while we focus on business logic.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│   Inngest Event  │───▶│  Background     │
│   (Register)    │    │   (registration. │    │  Function       │
│                 │    │    received)     │    │  (process_      │
└─────────────────┘    └──────────────────┘    │  registration)  │
                                               └─────────────────┘
```

## Key Components

### 1. Event Trigger (`api/routers/register.py`)
- **Event Name**: `registration.received`
- **Trigger**: When a user submits registration data
- **Data**: Contains `request_id` and `registration_data`

### 2. Background Function (`services/inngest/functions.py`)
- **Function ID**: `process-registration`
- **Purpose**: Orchestrates the complete intelligence collection workflow
- **Features**: Built-in retries, error handling, and observability

### 3. Webhook Endpoint (`api/main.py`)
- **Endpoint**: `/api/inngest`
- **Purpose**: Receives webhooks from Inngest platform
- **Handling**: Processes function invocations and returns responses

## Why Inngest is Valuable Here

### 1. **Reliability**
- **Automatic Retries**: Handles transient failures (API timeouts, network issues)
- **Exponential Backoff**: Smart retry strategy prevents overwhelming external services
- **Durable Execution**: Functions run to completion even if the server restarts

### 2. **Observability**
- **Real-time Dashboard**: See function execution, logs, and metrics
- **Error Tracking**: Detailed error information with stack traces
- **Performance Monitoring**: Track execution time and resource usage

### 3. **No Infrastructure Management**
- **No Redis/RabbitMQ**: Inngest handles the queue infrastructure
- **No Scaling Concerns**: Automatic scaling based on load
- **No Maintenance**: No queue monitoring or dead letter queue management

### 4. **Async by Default**
- **Perfect for I/O**: Ideal for web scraping and API calls
- **Non-blocking**: API responses are immediate while processing happens in background
- **Concurrent Processing**: Multiple registrations can be processed simultaneously

### 5. **Error Handling**
- **Graceful Degradation**: Failed jobs don't affect the API response
- **Detailed Logging**: Comprehensive error context for debugging
- **Retry Logic**: Automatic retries with configurable strategies

## Function Implementation Details

### Event Data Structure
```json
{
  "name": "registration.received",
  "data": {
    "request_id": "uuid-string",
    "registration_data": {
      "first_name": "John",
      "last_name": "Doe",
      "company_website": "https://example.com",
      "linkedin": "https://linkedin.com/in/johndoe"
    }
  }
}
```

### Function Workflow
1. **Extract & Validate**: Parse event data and validate registration request
2. **Process**: Call domain's `process_registration` function
3. **Save Results**: Store analysis results using `save_analysis`
4. **Return Status**: Provide completion status and metadata

### Error Handling Strategy
- **Validation Errors**: Fail fast, don't retry (user input issues)
- **Processing Errors**: Retry automatically (external API issues)
- **Save Errors**: Log warning but don't fail entire process

## Configuration

### Environment Variables
```bash
INNGEST_APP_ID=your-app-id
INNGEST_EVENT_KEY=your-event-key
INNGEST_SIGNING_KEY=your-signing-key
```

### Function Registration
The function is automatically registered when the module is imported:
```python
@inngest_client.create_function(
    fn_id="process-registration",
    trigger=TriggerEvent(event="registration.received")
)
```

## Monitoring & Debugging

### Inngest Dashboard
- **Function Logs**: Real-time execution logs
- **Error Tracking**: Detailed error information
- **Performance Metrics**: Execution time and throughput
- **Retry History**: See retry attempts and success rates

### Local Development
- **Inngest Dev Server**: Run `inngest dev` for local testing
- **Function Testing**: Test functions locally before deployment
- **Event Simulation**: Send test events to verify functionality

## Best Practices

### 1. **Idempotency**
- Functions should be safe to retry multiple times
- Use `request_id` to prevent duplicate processing
- Check for existing results before processing

### 2. **Error Handling**
- Distinguish between retryable and non-retryable errors
- Log sufficient context for debugging
- Don't swallow errors silently

### 3. **Performance**
- Keep functions focused on single responsibility
- Use async/await for I/O operations
- Monitor execution time and optimize slow operations

### 4. **Observability**
- Log important steps and decisions
- Include request IDs in all log messages
- Use structured logging for better analysis

## Troubleshooting

### Common Issues

1. **Function Not Triggering**
   - Check event name matches exactly
   - Verify webhook endpoint is accessible
   - Check Inngest dashboard for errors

2. **Function Failing**
   - Review logs in Inngest dashboard
   - Check external API availability
   - Verify environment variables are set

3. **Performance Issues**
   - Monitor execution time in dashboard
   - Check for external API rate limits
   - Optimize slow operations

### Debug Commands
```bash
# Test function imports
python -c "from services.inngest.functions import process_registration_task"

# Check Inngest client
python -c "from services.inngest.client import inngest_client; print(inngest_client.app_id)"

# Verify domain imports
python -c "from domains.intelligence_collection import process_registration"
```

## Future Enhancements

### Potential Improvements
1. **Step Functions**: Break down processing into smaller steps
2. **Parallel Processing**: Process LinkedIn and website analysis concurrently
3. **Caching**: Cache external API responses
4. **Rate Limiting**: Implement intelligent rate limiting for external APIs
5. **Monitoring**: Add custom metrics and alerts

### Scaling Considerations
- **Concurrency Limits**: Configure based on external API limits
- **Resource Usage**: Monitor memory and CPU usage
- **Cost Optimization**: Balance processing speed with cost 