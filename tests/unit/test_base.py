"""Unit tests for file_processor.core.base (ProcessingConfig, BaseProcessor)."""

from __future__ import annotations

import multiprocessing as mp
from pathlib import Path

import pytest

from file_processor.core.base import BaseProcessor, ProcessingConfig


@pytest.mark.unit
class TestProcessingConfig:
    def test_source_dir_is_resolved(self, tmp_path: Path) -> None:
        cfg = ProcessingConfig(source_dir=tmp_path)
        assert cfg.source_dir.is_absolute()

    def test_destination_defaults_to_source(self, tmp_path: Path) -> None:
        cfg = ProcessingConfig(source_dir=tmp_path)
        assert cfg.destination_dir == tmp_path.resolve()

    def test_destination_is_resolved_when_given(self, tmp_path: Path) -> None:
        dest = tmp_path / "out"
        dest.mkdir()
        cfg = ProcessingConfig(source_dir=tmp_path, destination_dir=dest)
        assert cfg.destination_dir == dest.resolve()

    def test_workers_clamped_to_reasonable_range(self, tmp_path: Path) -> None:
        cfg_low = ProcessingConfig(source_dir=tmp_path, workers=0)
        assert cfg_low.workers >= 1

        cfg_high = ProcessingConfig(source_dir=tmp_path, workers=99999)
        assert cfg_high.workers <= mp.cpu_count() * 2

    def test_dry_run_default_is_false(self, tmp_path: Path) -> None:
        cfg = ProcessingConfig(source_dir=tmp_path)
        assert cfg.dry_run is False

    def test_recursive_default_is_true(self, tmp_path: Path) -> None:
        cfg = ProcessingConfig(source_dir=tmp_path)
        assert cfg.recursive is True


@pytest.mark.unit
class TestBaseProcessor:
    def test_get_files_returns_all_files_recursively(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir, recursive=True)
        processor = BaseProcessor(cfg)
        files = processor.get_files()
        # source_dir has a.txt, b.jpg, c.jpeg + sub/d.txt = 4 files
        assert len(files) == 4
        assert all(f.is_file() for f in files)

    def test_get_files_non_recursive(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir, recursive=False)
        processor = BaseProcessor(cfg)
        files = processor.get_files()
        # Only top-level: a.txt, b.jpg, c.jpeg
        assert len(files) == 3

    def test_get_files_with_extension_filter(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir, recursive=True, file_extensions=[".txt"])
        processor = BaseProcessor(cfg)
        files = processor.get_files()
        assert all(f.suffix == ".txt" for f in files)
        assert len(files) == 2  # a.txt + sub/d.txt

    def test_logger_name_matches_class(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir)
        processor = BaseProcessor(cfg)
        assert processor.logger.name == "BaseProcessor"

    def test_initial_counters_are_zero(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir)
        processor = BaseProcessor(cfg)
        assert processor.processed_count == 0
        assert processor.error_count == 0
        assert processor.skipped_count == 0
