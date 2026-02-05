## 2026-01-16 - Hardcoded JWT Secret Vulnerability
**Vulnerability:** The `auth_service.py` contained a hardcoded fallback secret (`'your-secret-key'`) for `JWT_SECRET`. This allowed attackers to forge authentication tokens if the environment variable was missing.
**Learning:** Default values for security-critical secrets in code are dangerous because they fail "open" rather than "closed" when configuration is missing.
**Prevention:** Never provide default values for secrets. If a secret is missing, the application should either fail to start or generate a secure random value (fail secure) and log a warning.
