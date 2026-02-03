## 2024-05-23 - Async/Sync Mixing in FastAPI
**Learning:** Even in `async def` endpoints, calling synchronous third-party SDK methods (like `google.genai` or `openai`) directly blocks the main event loop, causing the entire API to freeze during the request.
**Action:** Always wrap synchronous SDK calls (that do network I/O) in `await asyncio.to_thread(...)` when working within an async FastAPI context. Verify with a concurrent heartbeat test if unsure.
