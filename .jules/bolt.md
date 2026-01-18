## 2025-02-19 - Caching get_current_user with TTLCache
**Learning:** `get_current_user` in FastAPI is a dependency that runs on every request. If it hits the database, it's a massive bottleneck. Implementing a simple `TTLCache` (e.g., 60s) dramatically reduces DB load.
**Action:** When caching user data, always ensure critical "write" or "spend" operations (like `download_pdf` deducting credits) explicitly bypass the cache or invalidate it immediately to prevent consistency issues (race conditions).
