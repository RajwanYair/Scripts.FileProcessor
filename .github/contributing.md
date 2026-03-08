# Contributing Guidelines

Thank you for your interest in contributing! This document provides guidelines for contributing to projects in this workspace.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- VS Code (recommended)

### Setup Steps

1. Clone the repository
2. Install system dependencies:

   ```bash
   # Ubuntu/Debian
   sudo apt install $(grep -v '^#' apt-packages.txt | grep -v '^$' | xargs)
   ```

3. Install Python dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

5. Run tests:

   ```bash
   pytest tests/ -v
   ```

## Coding Standards

### Python Style

- Follow PEP 8 with 100-character line limit
- Use type hints for all functions
- Write Google-style docstrings
- Use `ruff` for linting and formatting (replaces black, flake8, isort)
- Run `ruff check src/ tests/` and `ruff format src/ tests/` before committing

### Architecture Principles

- **Single Entry Point**: One main executable per project
- **Portability**: No hardcoded paths — use `Path(__file__).parent`
- **Configuration**: YAML with environment variable substitution
- **Three Interfaces**: CLI (Click), Desktop GUI (Tkinter), Web GUI (FastAPI)

### Example Code

```python
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Result:
    """Operation result with status and message."""
    success: bool
    message: str

def process_file(file_path: Path, verbose: bool = False) -> Result:
    """Process a file and return the result."""

    Returns:
        Result object with operation status.
    """
    if not file_path.exists():
        return Result(success=False, message=f"File not found: {file_path}")

    # Process the file...
    return Result(success=True, message="File processed successfully")
```

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Make your changes** following the coding standards
4. **Write tests** for new functionality
5. **Run the test suite**: `pytest tests/ -v`
6. **Run linting**: `black . && flake8 src/`
7. **Commit** with a descriptive message
8. **Push** to your fork
9. **Create a Pull Request**

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] No hardcoded paths or credentials
- [ ] Commits are atomic and well-described

## Testing

- Write tests for all new features
- Maintain 90%+ code coverage
- Test on multiple platforms when possible
- Include unit and integration tests

```bash
# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include examples for new features
- Keep CHANGELOG.md updated

## Questions?

Open an issue for questions or discussions about potential contributions.
