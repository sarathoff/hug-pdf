## 2026-01-17 - Synchronous Clients in FastAPI Async Routes
**Learning:** Using synchronous clients (like `google.genai`, `requests`) directly inside FastAPI `async def` route handlers blocks the event loop, causing severe performance degradation where one long-running request (e.g., LLM generation) blocks all other requests.
**Action:** Always wrap synchronous blocking calls with `await asyncio.to_thread(...)` when using them in `async def` endpoints, or switch to asynchronous clients (e.g., `httpx`).
