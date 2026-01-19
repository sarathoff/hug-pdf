## 2025-02-20 - [CRITICAL] Fixed Path Traversal in Image Serving
**Vulnerability:** The `/api/temp-images/{filename}` endpoint allowed path traversal (e.g., `../requirements.txt`) because it simply joined the input filename with the directory path without validation. The internal `PDFService` also had a similar vulnerability when processing local image URLs.
**Learning:** Using `pathlib.Path` joining (e.g., `root / filename`) does NOT prevent traversal if the filename contains `..`. The path must be resolved and checked against the parent directory using `is_relative_to()`.
**Prevention:** Always use `.resolve()` on constructed paths and verify containment with `.is_relative_to(root_dir)`. Never trust filenames from user input blindly.
