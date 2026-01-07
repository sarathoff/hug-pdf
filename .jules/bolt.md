## 2024-05-23 - Blocking Operations in Async
**Learning:**
1. **Sync DB calls**: `supabase-py` synchronous client blocks the event loop when used in `async def` routes. Switching dependency to `def` unblocks it by using threadpool.
2. **Sync Subprocess**: `subprocess.run` blocks the event loop. `async def generate_pdf` in this codebase is deceptive because it uses `subprocess.run` internally. It should use `asyncio.create_subprocess_exec` or `run_in_threadpool`.
3. **Dependency Check**: Always double check `requirements.txt` before assuming a package is missing. `cachetools` was present but initially missed in review.
**Action:**
When optimizing FastAPI apps, audit all `async def` functions for blocking calls like `subprocess.run`, `time.sleep`, or synchronous DB/API clients. Use `def` or `run_in_threadpool` for them.