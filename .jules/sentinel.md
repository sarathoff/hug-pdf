## 2024-05-23 - Permissive Fallback for Critical Operations
**Vulnerability:** The `payment_success` endpoint allowed bypassing payment verification by simply omitting the `session_id` parameter. The code explicitly logged a warning but allowed the operation to proceed, likely for development convenience or backward compatibility.
**Learning:** "Safe defaults" are critical. Security controls (like payment verification) should default to "deny" (fail closed) rather than "allow" (fail open) when validation data is missing. Temporary bypasses for development should be strictly gated by environment variables or removed before production.
**Prevention:**
1. Always implement "fail closed" logic for critical operations.
2. Use strict validation for all required parameters.
3. If a bypass is needed for testing, gate it behind a specific environment variable (e.g., `PAYMENT_TEST_MODE=true`) and never allow it in production builds.
