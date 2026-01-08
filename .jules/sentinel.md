## 2024-05-23 - Critical Payment Verification Bypass
**Vulnerability:** The `payment_success` endpoint allowed callers to bypass payment verification by simply omitting the `session_id` parameter. The code contained a comment explicitly acknowledging this "loose" check was for development but it was active in the codebase.
**Learning:** "Temporary" development bypasses often persist into production code if not strictly managed. Code comments like `TODO` or `In strict mode` are red flags that should be treated as vulnerabilities.
**Prevention:**
1. Never commit bypass logic for critical financial or auth flows.
2. Use feature flags (env vars) if development bypasses are absolutely necessary, and ensure they default to SECURE.
3. Treat comments suggesting security improvements as immediate blockers for production readiness.
