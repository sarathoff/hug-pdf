# Bolt's Journal

## 2025-02-18 - Blocking I/O in Asyncio
**Learning:** `subprocess.run` inside an `async def` method is strictly blocking and freezes the entire FastAPI event loop, preventing concurrent requests.
**Action:** Always wrap `subprocess.run` (and other heavy sync I/O) in `asyncio.to_thread` or `loop.run_in_executor` to offload it to a thread pool.
