## 2024-05-23 - Async Event Loop Blocking
**Learning:** The codebase mixes asynchronous FastAPI/Service methods with synchronous library calls (like `requests` and synchronous service clients). This causes two major issues:
1. **Event Loop Blocking:** Synchronous calls inside `async def` functions block the main event loop, freezing the entire server during I/O operations (e.g., generating PDFs, fetching images).
2. **Runtime Crashes:** Some code (e.g., `PPTGeneratorService`) attempted to `await` synchronous functions, leading to `TypeError: object dict can't be used in 'await' expression`.

**Action:**
- Always wrap synchronous I/O bound calls (API requests, File I/O, heavy computation) in `await asyncio.to_thread(...)` when calling them from `async def` functions.
- Verify that `await` is only used on awaitables (coroutines, Tasks, Futures) or the result of `asyncio.to_thread`.
