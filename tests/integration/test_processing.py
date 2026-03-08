"""Integration tests for FileProcessor end-to-end behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from file_processor.core.base import ProcessingConfig
from file_processor.core.processor import FileProcessor
from file_processor.core.results import BatchResult, OperationStatus, ProcessingResult

# ── helpers ────────────────────────────────────────────────────────────────────


def _noop_op(path: Path, cfg: ProcessingConfig) -> ProcessingResult:
    """Pass-through operation — records the file as SUCCESS."""
    return ProcessingResult(source=path, status=OperationStatus.SUCCESS, message="ok")


def _failing_op(path: Path, cfg: ProcessingConfig) -> ProcessingResult:
    """Always fails — used to test failure accounting."""
    raise RuntimeError(f"Intentional failure for {path.name}")


# ── FileProcessor.run() ────────────────────────────────────────────────────────


@pytest.mark.integration
class TestFileProcessorRun:
    def test_processes_all_files(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, recursive=True)
        batch = FileProcessor(cfg, operation=_noop_op).run()
        # source_dir has 4 files: a.txt, b.jpg, c.jpeg, sub/d.txt
        assert batch.total == 4
        assert batch.succeeded == 4

    def test_dry_run_returns_dry_run_status(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, recursive=True, dry_run=True)
        batch = FileProcessor(cfg).run()
        for result in batch.results:
            assert result.status == OperationStatus.DRY_RUN

    def test_non_recursive_omits_subdirectory(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, recursive=False)
        batch = FileProcessor(cfg, operation=_noop_op).run()
        # 3 top-level files (a.txt, b.jpg, c.jpeg); sub/d.txt excluded
        assert batch.total == 3

    def test_extension_filter_narrows_results(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, recursive=True, file_extensions=[".txt"])
        batch = FileProcessor(cfg, operation=_noop_op).run()
        # a.txt + sub/d.txt = 2
        assert batch.total == 2
        for result in batch.results:
            assert result.source.suffix == ".txt"

    def test_empty_directory_returns_empty_batch(self, tmp_path: Path) -> None:
        cfg = ProcessingConfig(source_dir=tmp_path)
        batch = FileProcessor(cfg).run()
        assert batch.total == 0

    def test_single_worker(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, recursive=True, workers=1)
        batch = FileProcessor(cfg, operation=_noop_op).run()
        assert batch.succeeded == batch.total

    def test_multiple_workers_same_result(self, source_dir: Path) -> None:
        cfg_single = ProcessingConfig(source_dir=source_dir, recursive=True, workers=1)
        cfg_multi = ProcessingConfig(source_dir=source_dir, recursive=True, workers=4)
        batch_single = FileProcessor(cfg_single, operation=_noop_op).run()
        batch_multi = FileProcessor(cfg_multi, operation=_noop_op).run()
        assert batch_single.total == batch_multi.total

    def test_failing_operation_recorded_as_failed(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, recursive=True, workers=1)
        batch = FileProcessor(cfg, operation=_failing_op).run()
        assert batch.failed == batch.total
        assert batch.succeeded == 0

    def test_batch_result_has_finish_time(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir)
        batch = FileProcessor(cfg, operation=_noop_op).run()
        assert batch.finished_at is not None
        assert batch.duration_seconds >= 0.0

    def test_batch_summary_string_format(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, workers=1)
        batch = FileProcessor(cfg, operation=_noop_op).run()
        summary = batch.summary()
        assert "succeeded" in summary
        assert "failed" in summary


# ── FileProcessor.run_async() ──────────────────────────────────────────────────


@pytest.mark.integration
class TestFileProcessorRunAsync:
    def test_async_run_returns_batch_result(self, source_dir: Path) -> None:
        import asyncio

        cfg = ProcessingConfig(source_dir=source_dir, recursive=True)
        batch = asyncio.run(FileProcessor(cfg, operation=_noop_op).run_async())
        assert isinstance(batch, BatchResult)
        assert batch.total == 4
