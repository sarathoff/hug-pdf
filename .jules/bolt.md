## 2026-01-24 - Blocking I/O in FastAPI Async Routes
**Learning:** FastAPI `async def` routes run on the main event loop. Using synchronous clients (like `supabase-py`'s `execute()` or `requests`) directly inside these routes blocks the loop, causing requests to be processed serially instead of concurrently.
**Action:** Wrap blocking synchronous calls in `await asyncio.to_thread(...)` to offload them to a separate thread pool, restoring concurrency.
