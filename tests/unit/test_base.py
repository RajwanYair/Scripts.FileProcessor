"""Unit tests for file_processor.core.base (ProcessingConfig, BaseProcessor)."""

from __future__ import annotations

import multiprocessing as mp
from pathlib import Path

import pytest

from file_processor.core.base import (
    BaseProcessor,
    ProcessingConfig,
    create_config_from_args,
    setup_common_arguments,
)


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

    def test_simulate_process_returns_would_process(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir, dry_run=True)
        processor = BaseProcessor(cfg)
        f = source_dir / "a.txt"
        result = processor.simulate_process(f)
        assert result["success"] is True
        assert result["action"] == "would_process"
        assert "a.txt" in result["message"]


# ── Concrete processor stubs for process_files tests ──────────────────────────


class _SucceedProcessor(BaseProcessor):
    """Test stub: always returns success."""

    def process_file(self, file_path: Path) -> dict:
        return {"success": True, "file": str(file_path)}


class _FailProcessor(BaseProcessor):
    """Test stub: always returns failure without raising."""

    def process_file(self, file_path: Path) -> dict:
        return {"success": False, "file": str(file_path)}


class _RaiseProcessor(BaseProcessor):
    """Test stub: always raises ValueError."""

    def process_file(self, file_path: Path) -> dict:
        raise ValueError(f"simulated error on {file_path.name}")


# ── process_files coverage ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestProcessFiles:
    def test_single_thread_all_succeed(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, workers=1)
        proc = _SucceedProcessor(cfg)
        files = proc.get_files()
        result = proc.process_files(files)
        assert result["processed"] == len(files)
        assert result["errors"] == 0

    def test_single_thread_all_fail(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, workers=1)
        proc = _FailProcessor(cfg)
        files = proc.get_files()
        result = proc.process_files(files)
        assert result["errors"] == len(files)
        assert result["processed"] == 0

    def test_single_thread_exception_counted_as_error(self, tmp_path: Path) -> None:
        (tmp_path / "x.txt").write_text("x", encoding="utf-8")
        cfg = ProcessingConfig(source_dir=tmp_path, workers=1)
        proc = _RaiseProcessor(cfg)
        result = proc.process_files([tmp_path / "x.txt"])
        assert result["errors"] == 1
        assert result["details"][0]["success"] is False
        assert "simulated error" in result["details"][0]["error"]

    def test_multi_thread_all_succeed(self, source_dir: Path) -> None:
        cfg = ProcessingConfig(source_dir=source_dir, workers=2)
        proc = _SucceedProcessor(cfg)
        files = proc.get_files()
        result = proc.process_files(files)
        assert result["processed"] == len(files)
        assert result["errors"] == 0

    def test_multi_thread_exception_counted_as_error(self, tmp_path: Path) -> None:
        (tmp_path / "x.txt").write_text("x", encoding="utf-8")
        cfg = ProcessingConfig(source_dir=tmp_path, workers=2)
        proc = _RaiseProcessor(cfg)
        result = proc.process_files([tmp_path / "x.txt"])
        assert result["errors"] == 1

    def test_dry_run_calls_simulate_process(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
        cfg = ProcessingConfig(source_dir=tmp_path, dry_run=True)
        proc = BaseProcessor(cfg)
        result = proc.process_files([tmp_path / "a.txt"])
        assert len(result["details"]) == 1
        assert result["details"][0]["action"] == "would_process"

    def test_empty_file_list_returns_zero_counts(self, tmp_path: Path) -> None:
        cfg = ProcessingConfig(source_dir=tmp_path, workers=1)
        result = _SucceedProcessor(cfg).process_files([])
        assert result["processed"] == 0
        assert result["errors"] == 0
        assert result["details"] == []


# ── setup_common_arguments / create_config_from_args ──────────────────────────


@pytest.mark.unit
class TestCLIHelpers:
    def test_setup_common_arguments_accepts_sourcedir(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(["--sourcedir", str(tmp_path)])
        assert args.sourcedir == str(tmp_path)

    def test_setup_common_arguments_defaults(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(["--sourcedir", str(tmp_path)])
        assert args.recursive is False
        assert args.overwrite is False
        assert args.dry_run is False
        assert args.verbose is False
        assert args.quality == 85

    def test_setup_common_arguments_boolean_flags(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(
            ["--sourcedir", str(tmp_path), "--recursive", "--overwrite", "--dry-run", "--verbose"]
        )
        assert args.recursive is True
        assert args.overwrite is True
        assert args.dry_run is True
        assert args.verbose is True

    def test_create_config_no_extensions(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(["--sourcedir", str(tmp_path)])
        cfg = create_config_from_args(args)
        assert cfg.file_extensions is None

    def test_create_config_extensions_with_dots(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(["--sourcedir", str(tmp_path), "--extensions", ".txt,.jpg"])
        cfg = create_config_from_args(args)
        assert ".txt" in (cfg.file_extensions or [])
        assert ".jpg" in (cfg.file_extensions or [])

    def test_create_config_extensions_without_dots_prefixed(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(["--sourcedir", str(tmp_path), "--extensions", "txt,jpg"])
        cfg = create_config_from_args(args)
        # Dots must be prepended automatically
        assert ".txt" in (cfg.file_extensions or [])
        assert ".jpg" in (cfg.file_extensions or [])

    def test_create_config_mixed_extensions(self, tmp_path: Path) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        setup_common_arguments(parser)
        args = parser.parse_args(["--sourcedir", str(tmp_path), "--extensions", "txt,.jpg"])
        cfg = create_config_from_args(args)
        assert ".txt" in (cfg.file_extensions or [])
        assert ".jpg" in (cfg.file_extensions or [])

    def test_simulate_process_returns_size(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir)
        processor = BaseProcessor(cfg)
        f = source_dir / "a.txt"
        result = processor.simulate_process(f)
        assert "size" in result
        assert result["size"] >= 0

    def test_get_files_excludes_oversized(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        big = source_dir / "big.dat"
        big.write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB
        cfg = ProcessingConfig(source_dir=source_dir, recursive=False, max_file_size=1)
        processor = BaseProcessor(cfg)
        files = processor.get_files()
        assert big not in files

    def test_get_files_includes_small_files_under_max_size(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir, recursive=False, max_file_size=100)
        processor = BaseProcessor(cfg)
        files = processor.get_files()
        assert len(files) == 3  # a.txt, b.jpg, c.jpeg

    def test_process_file_raises_not_implemented(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir)
        processor = BaseProcessor(cfg)
        with pytest.raises(NotImplementedError):
            processor.process_file(source_dir / "a.txt")

    def test_process_files_dry_run_calls_simulate(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        cfg = ProcessingConfig(source_dir=source_dir, dry_run=True, recursive=False)
        processor = BaseProcessor(cfg)
        files = processor.get_files()
        results = processor.process_files(files)
        assert len(results["details"]) == len(files)
        assert all(d["action"] == "would_process" for d in results["details"])

    def test_process_files_single_thread(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        class SimpleProcessor(BaseProcessor):
            def process_file(self, file_path: Path) -> dict:
                return {"success": True, "file": str(file_path)}

        cfg = ProcessingConfig(source_dir=source_dir, recursive=False, workers=1)
        processor = SimpleProcessor(cfg)
        files = processor.get_files()
        results = processor.process_files(files)
        assert results["processed"] == len(files)
        assert results["errors"] == 0

    def test_process_files_handles_exception_in_single_thread(self, source_dir: Path) -> None:
        from file_processor.core.base import ProcessingConfig

        class ErrorProcessor(BaseProcessor):
            def process_file(self, file_path: Path) -> dict:
                raise ValueError("deliberate error")

        cfg = ProcessingConfig(source_dir=source_dir, recursive=False, workers=1)
        processor = ErrorProcessor(cfg)
        files = processor.get_files()
        results = processor.process_files(files)
        assert results["errors"] == len(files)

    def test_multi_thread_all_fail_counted_as_errors(self, tmp_path: Path) -> None:
        """Cover line 156: multi-thread path where process_file returns success=False."""
        (tmp_path / "x.txt").write_text("x", encoding="utf-8")
        (tmp_path / "y.txt").write_text("y", encoding="utf-8")
        cfg = ProcessingConfig(source_dir=tmp_path, workers=2)
        result = _FailProcessor(cfg).process_files([tmp_path / "x.txt", tmp_path / "y.txt"])
        assert result["errors"] == 2
        assert result["processed"] == 0

    def test_get_files_skips_on_stat_oserror(self, tmp_path: Path) -> None:
        """Cover lines 84-85: OSError in stat() inside max_file_size check."""
        from unittest.mock import MagicMock, patch

        bad_path: MagicMock = MagicMock(spec=Path)
        bad_path.is_file.return_value = True
        bad_path.suffix = ".txt"
        bad_path.stat.side_effect = OSError("permission denied")

        cfg = ProcessingConfig(source_dir=tmp_path, recursive=False, max_file_size=100)
        processor = BaseProcessor(cfg)

        with patch.object(Path, "glob", return_value=iter([bad_path])):
            files = processor.get_files()

        assert bad_path not in files
