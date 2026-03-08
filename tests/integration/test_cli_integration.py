"""Integration tests — CLI commands executed end-to-end via CliRunner."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
import pytest

from file_processor.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.mark.integration
class TestScanCLI:
    def test_scan_empty_dir(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(tmp_path)])
        assert result.exit_code == 0
        assert "0 files" in result.output

    def test_scan_reports_correct_count(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(source_dir)])
        assert result.exit_code == 0
        # source_dir has 4 files recursively
        assert "4 files" in result.output

    def test_scan_non_recursive(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(source_dir), "--no-recursive"])
        assert result.exit_code == 0
        assert "3 files" in result.output

    def test_scan_extension_filter(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(source_dir), "--ext", ".txt"])
        assert result.exit_code == 0
        assert "2 files" in result.output


@pytest.mark.integration
class TestProcessCLI:
    def test_process_dry_run_succeeds(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["--dry-run", "process", "--source", str(source_dir)])
        assert result.exit_code == 0

    def test_process_with_dest(self, runner: CliRunner, source_dir: Path, dest_dir: Path) -> None:
        result = runner.invoke(
            cli,
            ["--dry-run", "process", "--source", str(source_dir), "--dest", str(dest_dir)],
        )
        assert result.exit_code == 0

    def test_process_invalid_source_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["process", "--source", "/absolutely/nonexistent"])
        assert result.exit_code != 0


@pytest.mark.integration
class TestDeduplicateCLI:
    def test_deduplicate_dry_run(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["--dry-run", "deduplicate", "--source", str(source_dir)])
        assert result.exit_code == 0

    def test_deduplicate_strategy_perceptual(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(
            cli,
            ["deduplicate", "--source", str(source_dir), "--strategy", "perceptual"],
        )
        assert result.exit_code == 0


@pytest.mark.integration
class TestConvertCLI:
    def test_convert_valid(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["convert", "--source", str(source_dir), "--format", "webp"])
        assert result.exit_code == 0

    def test_convert_with_quality(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(
            cli,
            ["convert", "--source", str(source_dir), "--format", "jpg", "--quality", "95"],
        )
        assert result.exit_code == 0
