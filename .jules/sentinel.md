## 2026-01-26 - Path Traversal in File Serving
**Vulnerability:** Unrestricted file access in `serve_temp_image` endpoint allowed path traversal via `../` sequences in filename.
**Learning:** `pathlib`'s `/` operator does not prevent traversal; `resolve()` must be called to canonicalize paths, and containment must be explicitly verified.
**Prevention:** Always use `path.resolve().is_relative_to(base_dir)` when serving files based on user input.
