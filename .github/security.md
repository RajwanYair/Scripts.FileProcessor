# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 7.x     | :white_check_mark: |
| < 7.0   | :x:                |

## Reporting a Vulnerability

> **Please do NOT open a public GitHub issue for security vulnerabilities.**

To report a security vulnerability privately:

1. Use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) (preferred), or
2. Email a maintainer listed in `CODEOWNERS` with:
   - A description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Any suggested mitigations

We aim to respond within **72 hours** and publish a fix within **14 days** for critical issues.

## Security Best Practices for Contributors

### Code Security (OWASP Top 10)

- **No hardcoded credentials** — use environment variables or `keyring`
- **No hardcoded paths** — use `Path(__file__).parent.resolve()`
- **Input validation** — validate and sanitize all user-provided input at system boundaries
- **Parameterized commands** — never build shell strings from user input (`subprocess` list form only)
- **Least privilege** — request admin/elevated rights only when absolutely necessary
- **No secrets in git** — `.env` is in `.gitignore`; use `pre-commit` detect-private-key hook

### Configuration Security

- Use environment variables for sensitive data: `${ENV_VAR:default}`
- Never log sensitive information
- Implement proper proxy cleanup after use

### Dependency Security

- Keep dependencies updated via Dependabot
- Review security advisories for dependencies
- Use `pip audit` to check for known vulnerabilities

## Security Checklist

- [ ] No hardcoded credentials in code
- [ ] No hardcoded absolute paths
- [ ] All user input validated
- [ ] Shell commands use parameterized execution
- [ ] Sensitive data uses environment variables
- [ ] Logging does not expose secrets
- [ ] Dependencies are up-to-date
- [ ] Code passes `bandit` security linting
