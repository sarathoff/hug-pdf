## 2026-01-23 - Blocking Sync Operations in Async FastAPI
**Learning:** Using `async def` endpoints with synchronous clients (like `supabase-py`'s standard client) blocks the entire event loop, causing requests to be processed sequentially instead of concurrently.
**Action:** Always verify if a library is async. If not, wrap blocking calls in `asyncio.to_thread()` or use `def` endpoints (thread pool). For high-frequency dependencies like authentication, use caching (`cachetools.TTLCache`) to minimize blocking calls.
