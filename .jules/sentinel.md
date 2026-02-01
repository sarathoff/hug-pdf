## 2026-02-01 - Path Traversal Testing with FastAPI TestClient
**Vulnerability:** Path Traversal in static file serving endpoint (`serve_temp_image`).
**Learning:** `FastAPI.testclient.TestClient` (via `httpx`) normalizes URL paths (e.g., resolving `..`) *before* sending the request. This masks path traversal vulnerabilities during testing if relying solely on the client.
**Prevention:** To test path traversal, either call the endpoint function directly with the malicious input (as done in `tests/test_security_fixes.py`) or use a raw socket/client that allows sending unnormalized paths.
