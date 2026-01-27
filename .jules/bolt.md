## 2025-02-23 - Async Sandwich in FastAPI
**Learning:** Python's `async def` endpoints in FastAPI are not truly non-blocking if they call synchronous libraries (like `supabase-py`'s `execute()` method) directly. This creates an "async sandwich" where the event loop is blocked by the sync call.
**Action:** Wrap blocking synchronous calls in `await asyncio.to_thread(...)` when using them within `async def` functions.
