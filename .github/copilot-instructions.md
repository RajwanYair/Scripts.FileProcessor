# GitHub Copilot Instructions — FileProcessor

> Part of the **Universal Project Enhancement Framework v12.0.0**

## Project Purpose

General-purpose file processing pipeline — apply transformations, filters, and operations to file sets.

## Language & Stack

- **Python 3.9+** (system-wide, no venv by default)
- **Click 8.1+** for CLI, **Rich 13+** for terminal output
- **Pydantic 2+** for config validation
- **pytest** for testing (90%+ coverage target)
- **ruff** for linting + formatting (replaces flake8/black/isort)
- **mypy + pyright** for type checking

## Code Standards

- Type hints on **every** function signature
- pathlib.Path over os.path — always
- logging / rich.console over print()
- Specific exceptions only — no bare except:
- No hardcoded absolute paths — use Path(__file__).parent.resolve()
- No mutable default arguments
- Signal handlers for SIGTERM/SIGINT in entry points
- Dataclasses for structured data, Enums for constants

## Entry Point Pattern

`python
#!/usr/bin/env python3
import signal, sys
from pathlib import Path
import click
from rich.console import Console

PROJECT_ROOT = Path(__file__).parent.resolve()
console = Console()

def _shutdown(sig, frame):
    console.print("\n[yellow]Shutting down...[/yellow]")
    sys.exit(0)

signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)

@click.group()
@click.version_option()
def cli() -> None:
    """General-purpose file processing pipeline — apply transformations, filters, and operations to file sets"""

if __name__ == "__main__":
    cli()
`

## Project Structure

`
Scripts.FileProcessor/
├── src/cli/        # Click commands
├── src/core/       # Business logic
├── src/utils/      # Shared helpers
├── config/         # YAML config (with \ substitution)
├── tests/unit/
└── tests/integration/
`

## References

See [workspace instructions](../../../.github/instructions/workspace.instructions.md) for full workspace standards.
See [python instructions](instructions/python.instructions.md) for Python coding rules.
See [testing instructions](instructions/testing.instructions.md) for test structure.
