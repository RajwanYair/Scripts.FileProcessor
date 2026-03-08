# Developer Guide

## Prerequisites

- Python 3.11+
- Git

## Setup

```bash
git clone https://github.com/<org>/file-processor.git
cd file-processor
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
# All tests with coverage
pytest

# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Specific test file
pytest tests/unit/test_file_utils.py -v
```

## Linting and Formatting

```bash
# Check and auto-fix
ruff check src/ tests/ --fix
ruff format src/ tests/

# Type checking
mypy src/file_processor

# Security scan
bandit -r src/
```

Or run all checks at once via pre-commit:

```bash
pre-commit run --all-files
```

## Project Structure

See [docs/architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) for the full system design.

Key directories:

| Path | Purpose |
|------|---------|
| `src/file_processor/core/` | Domain logic — `FileProcessor`, result types, utilities |
| `src/file_processor/cli/` | Click CLI commands |
| `src/file_processor/api/` | FastAPI app and routes |
| `src/file_processor/plugins/` | Plugin system and marketplace |
| `src/file_processor/utils/` | Config loader |
| `tests/unit/` | Fast, isolated unit tests |
| `tests/integration/` | Full-stack integration tests |
| `config/` | Default YAML config |

## Adding a New CLI Command

1. Open `src/file_processor/cli/main.py`.
2. Decorate a function with `@cli.command("name")`.
3. Use `@pass_config` to receive the shared `Config` context.
4. Write a corresponding test in `tests/unit/test_cli.py`.

```python
@cli.command("my-cmd")
@click.option("--target", required=True, type=click.Path(exists=True, path_type=Path))
@pass_config
def cmd_my_cmd(cfg: Config, target: Path) -> None:
    """Short description shown in --help."""
    console.print(f"Running on {target}")
```

## Adding a New Core Module

1. Create `src/file_processor/core/my_module.py`.
2. Export public symbols from `src/file_processor/core/__init__.py` if needed.
3. Add unit tests in `tests/unit/test_my_module.py`.

```python
# src/file_processor/core/my_module.py
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def my_function(path: Path) -> str:
    """Do something with path."""
    ...
```

## Writing a Plugin

See [docs/plugins/DEVELOPMENT_GUIDE.md](plugins/DEVELOPMENT_GUIDE.md) for the full plugin SDK guide.

## Release Process

Releases are fully automated via GitHub Actions:

1. Bump version in `pyproject.toml` and `VERSION`.
2. Update `CHANGELOG.md`.
3. Commit and tag: `git tag v7.1.0 && git push origin v7.1.0`.
4. The `release.yml` workflow builds the dist and creates the GitHub Release automatically.

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOG_LEVEL` | `WARNING` | Root log level |
| `FP_CONFIG` | — | Path to user config file |
| `FP_WORKERS` | auto | Default thread-pool size |

Variables can also be set inline in your YAML config using `${VAR_NAME:default}` syntax.
