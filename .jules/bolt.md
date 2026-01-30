## 2025-02-14 - Blocking Sync I/O in Async Handlers
**Learning:** Python `requests` calls inside FastAPI `async def` endpoints block the entire event loop, killing concurrency. Even if other code is async, one blocking call stops everything.
**Action:** Wrap blocking calls (like `requests.get`) in `asyncio.to_thread()` when used in async contexts, or use a native async library like `httpx`. Ensure synchronous callers have access to a sync version (e.g., `_sync`) to avoid large refactors.
