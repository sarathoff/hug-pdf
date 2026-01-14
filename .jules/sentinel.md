## 2024-05-22 - Path Traversal Vulnerability
**Vulnerability:** The `/temp-images/{filename}` endpoint was vulnerable to path traversal attacks using `..` sequences, allowing access to arbitrary files on the server (including source code and `.env` files).
**Learning:** `pathlib`'s `/` operator blindly joins paths. `FileResponse` serves files if they exist, regardless of location. Explicit validation using `resolve()` and `is_relative_to()` is mandatory for any user-controlled file path.
**Prevention:** Always resolve paths to absolute paths and check if they are relative to the intended base directory before serving.

## 2024-05-22 - Payment Bypass Logic
**Vulnerability:** The `/payment/success` endpoint explicitly permits requests without `session_id` verification, logging a warning but granting credits.
**Learning:** Security controls (payment verification) were bypassed by design for development convenience ("For now, we'll allow it"), creating a critical vulnerability in production.
**Prevention:** Never allow "dev-only" bypasses in production code paths without strict environment checks (e.g., `if env == 'DEV'`).
