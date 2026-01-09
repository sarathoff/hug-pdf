# Sentinel Journal

## 2024-05-22 - Payment Verification Bypass
**Vulnerability:** The `payment_success` endpoint in `backend/server.py` allowed users to bypass payment verification by omitting `session_id` or using a `test_session_` prefix, even in production.
**Learning:** Checking for "test" strings in user input is dangerous without checking environment configuration (e.g., `PAYMENT_TEST_MODE`). Default fallback logic (`else` blocks) should always fail securely (reject) rather than warn and proceed.
**Prevention:**
1. Always validate critical parameters (`session_id`) exist.
2. Restrict "test mode" logic to environments where a specific flag (like `PAYMENT_TEST_MODE`) is explicitly enabled.
3. Use "fail-secure" defaults: if verification logic is skipped or fails, the transaction must be rejected.
