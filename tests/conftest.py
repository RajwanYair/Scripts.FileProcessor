"""
conftest.py — Shared pytest fixtures.

Available markers (configure in pyproject.toml [tool.pytest.ini_options]):
  @pytest.mark.unit       — pure Python, no I/O
  @pytest.mark.integration — file-system / OS interaction
  @pytest.mark.slow       — long-running tests
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ── directory fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Temporary directory, cleaned up automatically after each test."""
    return tmp_path


@pytest.fixture
def source_dir(tmp_path: Path) -> Path:
    """Source directory pre-populated with a few sample files."""
    src = tmp_path / "source"
    src.mkdir()
    (src / "a.txt").write_text("hello world", encoding="utf-8")
    (src / "b.jpg").write_bytes(b"\xff\xd8\xff")  # minimal JPEG magic bytes
    (src / "c.jpeg").write_bytes(b"\xff\xd8\xff")  # alias — should normalise to .jpg
    sub = src / "sub"
    sub.mkdir()
    (sub / "d.txt").write_text("nested", encoding="utf-8")
    return src


@pytest.fixture
def dest_dir(tmp_path: Path) -> Path:
    """Empty destination directory."""
    d = tmp_path / "dest"
    d.mkdir()
    return d


# ── config fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
def minimal_config_file(tmp_path: Path) -> Path:
    """Write and return a minimal YAML config file."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text("dry_run: true\nverbose: false\nmax_workers: 2\n", encoding="utf-8")
    return cfg


@pytest.fixture
def processing_config(source_dir: Path):
    """Return a `ProcessingConfig` pointing at the source_dir fixture."""
    from file_processor.core.base import ProcessingConfig

    return ProcessingConfig(source_dir=source_dir, dry_run=True, verbose=False)
