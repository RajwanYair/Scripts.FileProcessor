"""
noxfile.py — Nox automation sessions for file-processor.

Usage:
    nox                     # run default sessions (lint + tests)
    nox -s lint             # ruff check + format check
    nox -s type_check       # mypy
    nox -s security         # bandit
    nox -s tests            # pytest with coverage
    nox -s tests_integration # integration tests only
    nox -s docs             # build MkDocs site
    nox -l                  # list all sessions
"""

from __future__ import annotations

import nox

# Python version(s) to test against
PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]

# Reuse the same venv across re-runs (faster local iteration)
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "tests"]


# ── Helpers ────────────────────────────────────────────────────────────────────


def _install_project(session: nox.Session, extras: str = "dev") -> None:
    session.install("-e", f".[{extras}]")


# ── Lint ───────────────────────────────────────────────────────────────────────


@nox.session(python="3.11", tags=["lint"])
def lint(session: nox.Session) -> None:
    """Run ruff linter and format checker."""
    _install_project(session)
    session.run("ruff", "check", "src/", "tests/", external=True)
    session.run("ruff", "format", "--check", "src/", "tests/", external=True)


# ── Type checking ──────────────────────────────────────────────────────────────


@nox.session(python="3.11", tags=["lint"])
def type_check(session: nox.Session) -> None:
    """Run mypy static type analysis."""
    _install_project(session)
    session.run("mypy", "src/file_processor", external=True)


# ── Security ───────────────────────────────────────────────────────────────────


@nox.session(python="3.11", tags=["security"])
def security(session: nox.Session) -> None:
    """Run bandit security scan."""
    session.install("bandit[toml]")
    session.run("bandit", "-r", "src/", "-ll", "-c", "pyproject.toml", external=True)


# ── Tests ──────────────────────────────────────────────────────────────────────


@nox.session(python=PYTHON_VERSIONS, tags=["tests"])
def tests(session: nox.Session) -> None:
    """Run unit tests with coverage."""
    _install_project(session)
    session.run(
        "pytest",
        "tests/unit/",
        "-m",
        "unit",
        "--cov=src/file_processor",
        "--cov-report=xml",
        "--cov-fail-under=70",
        "-q",
        external=True,
    )


@nox.session(python="3.11", tags=["tests"])
def tests_integration(session: nox.Session) -> None:
    """Run integration tests."""
    _install_project(session)
    session.run(
        "pytest",
        "tests/integration/",
        "-m",
        "integration",
        "-v",
        "--tb=short",
        external=True,
    )


@nox.session(python="3.11", tags=["tests"])
def tests_all(session: nox.Session) -> None:
    """Run the full test suite."""
    _install_project(session)
    session.run("pytest", "tests/", "-q", "--tb=short", external=True)


# ── Docs ───────────────────────────────────────────────────────────────────────


@nox.session(python="3.11", tags=["docs"])
def docs(session: nox.Session) -> None:
    """Build MkDocs documentation site."""
    session.install("mkdocs", "mkdocs-material")
    session.run("mkdocs", "build", "--strict", external=True)
