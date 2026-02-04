## 2024-05-22 - [Blocking Sync Calls in FastAPI]
**Learning:** Found critical bottleneck: `PexelsService` used blocking `requests` library inside `async def` endpoints and services. This blocked the event loop and serialized what should have been parallel image fetches for PPT generation.
**Action:** Always verify if "async" services are actually non-blocking. Use `asyncio.to_thread()` to wrap unavoidable synchronous I/O libraries.
