## Description

Brief description of what this PR does and why.

Closes #<!-- issue number -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Refactor / code quality improvement
- [ ] Documentation update
- [ ] CI / build / tooling change
- [ ] Security fix

## Changes Made

- `path/to/file.py`: description of change
- `path/to/other.py`: description of change

## Testing

- [ ] Unit tests added / updated
- [ ] Integration tests added / updated
- [ ] Tested manually on Windows
- [ ] Tested manually on Linux / WSL
- [ ] All existing tests pass

### How to Test

```bash
# Commands to verify the change
python -m pytest tests/ -v --tb=short
```

## Quality Checklist

- [ ] `ruff check` passes (or `flake8` if ruff unavailable)
- [ ] `mypy` type check passes (or no new regressions)
- [ ] `pytest` passes with 90%+ coverage
- [ ] `bandit` security check clean
- [ ] No hardcoded paths, secrets, or credentials
- [ ] No debug code left in production paths
- [ ] Documentation updated if behaviour changed
- [ ] `CHANGELOG.md` updated (for user-visible changes)

## Screenshots (if applicable)

GUI changes, CLI output, etc.
