# Streaming Output Fix Design

## Problem Statement
The frontend streaming output is not working properly. Instead of displaying tokens incrementally, all content appears at once after loading. The SSE (Server-Sent Events) connection is established correctly (`text/event-stream`), but all events are returned in a single batch rather than being streamed progressively.

## Root Cause Analysis
The issue is likely caused by httpx client buffering or configuration issues when communicating with Ollama's OpenAI-compatible API. The current httpx client configuration may not be properly handling streaming responses from Ollama.

## Solution Approach
Modify the httpx client configuration in `backend/rag/generator.py` to disable buffering and optimize settings for Ollama's streaming API.

## Technical Design

### Current Configuration
```python
transport = httpx.HTTPTransport(http1=True, http2=False)
http_client = httpx.Client(transport=transport, timeout=httpx.Timeout(60.0))
```

### Proposed Changes
```python
transport = httpx.HTTPTransport(
    http1=True, 
    http2=False,
    verify=False,  # Support HTTP connections (common for local Ollama)
)
http_client = httpx.Client(
    transport=transport, 
    timeout=httpx.Timeout(60.0, connect=10.0),
    headers={"Accept": "text/event-stream"}
)
```

### Key Modifications
1. **Disable SSL verification** (`verify=False`): Supports HTTP connections common with local Ollama instances
2. **Add connect timeout**: Separate connect timeout for better error handling
3. **Add Accept header**: Explicitly request SSE format

## Implementation Steps
1. Modify the `Generator.__init__()` method in `backend/rag/generator.py`
2. Update both initial client creation and `update_config()` method
3. Test with Ollama to verify streaming behavior

## Expected Outcome
- Frontend should display tokens incrementally as they arrive
- Streaming indicator should show during response generation
- User experience should feel responsive and real-time

## Testing
1. Start the application with `npm run dev` (frontend) and backend server
2. Send a chat message
3. Verify that tokens appear incrementally in the UI
4. Check browser Network tab to confirm SSE events are arriving separately