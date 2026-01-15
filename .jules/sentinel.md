## 2026-01-15 - Payment Verification Bypass
**Vulnerability:** The `/payment/success` endpoint allowed requests without a `session_id` to proceed and add credits, logging only a warning.
**Learning:** "Strict mode" checks were commented out in favor of "allow for now", leaving a critical financial gap. Explicit TODOs for security should never be left active in production code.
**Prevention:** Enforce strict validation on all financial endpoints. Reject by default.
