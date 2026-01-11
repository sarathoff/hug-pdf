## 2024-01-01 - Hardcoded Secrets in Repository
**Vulnerability:** Several files (`reconstruct_env.py`, `.env_clean`, `backend/list_models_v2.py`, etc.) contained plaintext API keys (GEMINI_API_KEY, SUPABASE_KEY, etc.) and were committed to the repository.
**Learning:** Utility scripts and debug files created during development can accidentally leak secrets if not properly gitignored or if created outside of the standard `.env` workflow.
**Prevention:**
1.  Ensure all scripts generating or handling secrets use `os.environ` or a secure secrets manager.
2.  Add `*.env*` and `debug_*.py` to `.gitignore` (already partially done but needs strict enforcement).
3.  Implement a pre-commit hook to scan for high-entropy strings or known key patterns.
