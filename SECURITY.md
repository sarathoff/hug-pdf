# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | ✅ Active support  |
| 1.x.x   | ❌ End of life     |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in HugPDF, please report it responsibly.

### How to Report

**Do NOT** open a public GitHub issue for security vulnerabilities.

Instead, please email us at: **security@hugpdf.app**

Include in your report:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution**: We aim to patch critical issues within 14 days

### Responsible Disclosure

We ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Don't exploit the vulnerability beyond what's necessary to demonstrate it
- Don't access or modify other users' data

### Out of Scope

The following are not in scope:
- Denial of service attacks
- Social engineering attacks
- Issues in third-party dependencies (report those to the dependency maintainers)
- Rate limiting abuse

## Security Best Practices for Contributors

When contributing to HugPDF:

1. **Never commit secrets** - Use environment variables for API keys, passwords, and tokens
2. **Validate user input** - Always sanitize and validate input on both frontend and backend
3. **Use HTTPS** - All external communications must use HTTPS
4. **Follow least privilege** - Request only necessary permissions
5. **Keep dependencies updated** - Regularly update dependencies to patch known vulnerabilities

## Security Features

HugPDF implements the following security measures:

- API key authentication with hashed storage
- Rate limiting per API key
- CORS protection
- Input validation and sanitization
- Secure JWT token handling via Supabase Auth
- Credit-based access control

Thank you for helping keep HugPDF secure! 🔐
