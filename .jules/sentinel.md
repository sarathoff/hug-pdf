## 2025-01-25 - Path Traversal Vulnerability
**Vulnerability:** User input used directly in file paths allowing access to sensitive files (../server.py) and potential file overwrite in PDF generation.
**Learning:** FastAPI/Starlette TestClient normalizes paths (resolves '..') before sending requests, making it unsuitable for testing path traversal. Direct function calls or raw socket tests are required.
**Prevention:** Always use `pathlib.Path.resolve()` and `.is_relative_to()` to validate that resolved paths are within the expected directory.
