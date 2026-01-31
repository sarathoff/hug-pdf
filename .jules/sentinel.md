## 2025-02-18 - Path Traversal in File Serving
**Vulnerability:** The `serve_temp_image` endpoint blindly joined user-provided filenames with a base directory using `pathlib` (`ROOT_DIR / "temp_uploads" / filename`). This allowed path traversal (e.g., `../.env`) because `pathlib` (and `os.path.join`) does not automatically sanitize `..` components when joining, and the file was served if it existed anywhere the process could read.
**Learning:** `pathlib.Path`'s `/` operator or `joinpath` is not secure against directory traversal by itself. `resolve()` handles symlinks and `..` but does not enforce a root directory unless explicitly checked.
**Prevention:**
1. Sanitize the input `filename` using `os.path.basename(filename)` to strip directory components.
2. Resolve the resulting path to an absolute path.
3. Use `.is_relative_to(base_dir)` (Python 3.9+) to rigorously verify the resolved path is inside the intended directory.
