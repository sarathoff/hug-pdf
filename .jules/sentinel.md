## 2026-01-21 - Path Traversal in File Serving
**Vulnerability:** The `/api/temp-images/{filename}` endpoint allowed accessing arbitrary files on the server (LFI) by using path traversal characters (`..`) or absolute paths in the `filename` parameter.
**Learning:** `pathlib`'s `/` operator creates paths blindly without validation. Furthermore, verifying this vulnerability with `TestClient` is tricky because it normalizes URLs (resolving `..`) before sending the request, which can mask the vulnerability in tests.
**Prevention:** Always use `.resolve()` to canonicalize paths and `.is_relative_to(base_dir)` to ensure the resolved path stays within the intended directory. For testing path traversal, invoke the handler function directly or use a raw socket/client that doesn't normalize paths.
