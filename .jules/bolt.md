## 2026-01-12 - [User Auth Caching]
**Learning:** The `get_current_user` dependency in FastAPI was hitting the database on every request, causing unnecessary latency and load. Supabase (and PostgREST) calls are HTTP requests, so they are not cheap.
**Action:** Implemented a short-lived (60s) TTL cache using `cachetools` for user profiles. Critical: Added cache invalidation on credit deduction/addition to prevent race conditions where a user might spend credits they don't have or not see credits they just bought.
