## 2024-05-22 - Async Blocking Operations
**Learning:** Python's `async def` does not magically make synchronous code asynchronous. Calling blocking synchronous functions (like `requests.get`, `subprocess.run`, or synchronous DB clients) inside an `async def` function blocks the entire asyncio event loop, freezing the application for all users until the operation completes.
**Action:** Always wrap blocking synchronous calls in `asyncio.to_thread()` when calling them from async functions, or use asynchronous alternatives (like `httpx` instead of `requests`).
