## 2025-02-18 - Blocking Service Calls in Async Endpoints
**Learning:** The codebase uses `async def` FastAPI endpoints but calls synchronous service methods (Gemini, Pexels, etc.) directly. This blocks the main event loop, causing requests to be processed serially instead of concurrently.
**Action:** Always wrap synchronous blocking calls (like `requests.get` or `gemini_service.generate_...`) in `await asyncio.to_thread(...)` within `async def` endpoints.
