## 2026-01-29 - LFI in Internal Service Logic
**Vulnerability:** Local File Inclusion (LFI) in `PDFService` where internal logic copied files from `temp_uploads` based on unvalidated URL path components.
**Learning:** Services that blindly trust internal URLs or manipulate paths based on URL string splitting are vulnerable to traversal, even if the initial request was authenticated.
**Prevention:** Always validate and sanitize filenames extracted from URLs before using them in file system operations. Use `pathlib.Path.is_relative_to()` to enforce directory confinement.
