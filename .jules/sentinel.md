## 2024-05-22 - Path Traversal in File Serving
**Vulnerability:** Path Traversal (LFI) in `serve_temp_image` endpoint.
**Learning:** Using `pathlib`'s `/` operator or `os.path.join` does not automatically sanitize ".." components. Simply checking `.exists()` allows access to parent directories.
**Prevention:** Always `resolve()` user-provided paths and verify they start with the expected root directory using `is_relative_to()` or string comparison.
