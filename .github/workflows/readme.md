# GitHub Workflows

This directory contains automated CI/CD workflows for the File Processing Suite.

## Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Release publications

**Jobs:**

#### Code Quality & Linting

- Black (code formatting)
- isort (import sorting)
- Flake8 (linting)
- Pylint (static analysis)
- MyPy (type checking)

#### Security Scanning

- Bandit (security linter)
- Safety (dependency vulnerability scanning)

#### Unit Tests

- Multi-platform testing (Ubuntu, Windows, macOS)
- Python 3.10, 3.11, 3.12
- Coverage reporting

#### Integration Tests

- API endpoint testing
- Plugin system validation
- Docker deployment verification

#### Build & Package

- Docker image build
- Multi-arch support (amd64, arm64)
- PyPI package build

#### Deploy

- Docker registry push (on release)
- PyPI publication (on release)
- Documentation deployment

## Environment Variables

Required secrets in repository settings:

```
DOCKER_USERNAME      # Docker registry username
DOCKER_PASSWORD      # Docker registry password/token
PYPI_API_TOKEN       # PyPI API token for package publishing
SAFETY_API_KEY       # Safety API key for vulnerability scanning
```

## Usage

### Running Locally

Simulate CI checks before pushing:

```bash
# Code quality
black --check .
isort --check-only .
flake8 .
pylint core/
mypy core/

# Security
bandit -r core/

# Tests
pytest tests/ -v --cov=core
```

### Matrix Testing

The workflow tests across:

- **OS**: Ubuntu 22.04, Windows Server 2022, macOS 13
- **Python**: 3.10, 3.11, 3.12

### Caching

Workflows use caching for:

- Python pip dependencies
- Docker layers
- Test fixtures

## Best Practices

1. **Pull Requests**: All checks must pass before merging
2. **Branch Protection**: Enable required status checks on `main`
3. **Secrets Management**: Never commit secrets; use GitHub Secrets
4. **Workflow Permissions**: Use least-privilege principle
5. **Artifact Retention**: Set appropriate retention periods (default: 90 days)

## Adding New Workflows

When adding workflows:

1. Use semantic naming: `<purpose>-<trigger>.yml`
2. Add comprehensive comments
3. Use matrix strategy for multi-platform/version testing
4. Implement proper error handling with `continue-on-error`
5. Add timeout limits to prevent runaway jobs
6. Update this README

## Troubleshooting

### Common Issues

**Workflow not triggering:**

- Check branch name matches trigger configuration
- Verify workflow file syntax (use `yamllint`)
- Check repository workflow permissions

**Tests failing on specific OS:**

- Review OS-specific dependencies in `requirements.txt`
- Check file path separators (use `pathlib.Path`)
- Verify environment variables are set correctly

**Docker build failures:**

- Check Docker registry credentials
- Verify Dockerfile multi-stage build syntax
- Review layer caching configuration

## Related Documentation

- [Contributing Guide](../../CONTRIBUTING.md)
- [Development Setup](../../docs/guides/DEVELOPER_GUIDE.md)
- [Release Process](../../docs/guides/RELEASE_PROCESS.md)
