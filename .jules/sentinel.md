## 2026-01-14 - Permissive Payment Verification
**Vulnerability:** The `/payment/success` endpoint accepted requests without a `session_id`, allowing attackers to add credits without proof of payment. The code explicitly noted this as "suspicious" but only logged a warning.
**Learning:** Developers sometimes leave permissive logic for testing or convenience ("For now, we'll allow it"), which becomes a production vulnerability.
**Prevention:** Enforce strict validation by default. Use `start_live_preview` or specific flags for test modes, rather than weakening production logic.
