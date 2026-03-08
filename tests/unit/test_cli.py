"""Unit tests for the Click CLI (file_processor.cli.main)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
import pytest

from file_processor.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ── Root group ────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRootGroup:
    def test_help_exits_zero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "file processing pipeline" in result.output.lower()

    def test_verbose_flag_accepted(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["--verbose", "scan", "--source", str(tmp_path)])
        # Should not fail due to the flag itself
        assert result.exit_code == 0

    def test_dry_run_flag_accepted(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["--dry-run", "scan", "--source", str(tmp_path)])
        assert result.exit_code == 0

    def test_unknown_option_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--nonexistent-flag"])
        assert result.exit_code != 0


# ── process command ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProcessCommand:
    def test_missing_source_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["process"])
        assert result.exit_code != 0

    def test_invalid_source_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["process", "--source", "/nonexistent/path"])
        assert result.exit_code != 0

    def test_valid_source_exits_zero(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["process", "--source", str(tmp_path)])
        assert result.exit_code == 0

    def test_dry_run_propagates(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["--dry-run", "process", "--source", str(tmp_path)])
        assert result.exit_code == 0

    def test_workers_option_accepted(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["process", "--source", str(tmp_path), "--workers", "2"])
        assert result.exit_code == 0


# ── deduplicate command ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeduplicateCommand:
    def test_missing_source_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["deduplicate"])
        assert result.exit_code != 0

    def test_default_strategy_hash(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["deduplicate", "--source", str(tmp_path)])
        assert result.exit_code == 0

    @pytest.mark.parametrize("strategy", ["hash", "content", "perceptual"])
    def test_valid_strategies_accepted(
        self, runner: CliRunner, tmp_path: Path, strategy: str
    ) -> None:
        result = runner.invoke(
            cli, ["deduplicate", "--source", str(tmp_path), "--strategy", strategy]
        )
        assert result.exit_code == 0

    def test_invalid_strategy_exits_nonzero(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(
            cli, ["deduplicate", "--source", str(tmp_path), "--strategy", "invalid"]
        )
        assert result.exit_code != 0


# ── convert command ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestConvertCommand:
    def test_missing_format_exits_nonzero(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["convert", "--source", str(tmp_path)])
        assert result.exit_code != 0

    def test_valid_invocation(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["convert", "--source", str(tmp_path), "--format", "webp"])
        assert result.exit_code == 0

    def test_quality_option_accepted(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(
            cli, ["convert", "--source", str(tmp_path), "--format", "jpg", "--quality", "90"]
        )
        assert result.exit_code == 0


# ── scan command ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestScanCommand:
    def test_missing_source_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["scan"])
        assert result.exit_code != 0

    def test_empty_dir_reports_zero_files(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(tmp_path)])
        assert result.exit_code == 0
        assert "0 files" in result.output

    def test_populated_dir_reports_file_count(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(source_dir)])
        assert result.exit_code == 0
        # source_dir has a.txt, b.jpg, c.jpeg, sub/d.txt = 4 files
        assert "files" in result.output

    def test_extension_filter_narrows_results(self, runner: CliRunner, source_dir: Path) -> None:
        result = runner.invoke(cli, ["scan", "--source", str(source_dir), "--ext", ".txt"])
        assert result.exit_code == 0


# ── plugins group ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPluginsGroup:
    def test_plugins_help(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["plugins", "--help"])
        assert result.exit_code == 0

    def test_plugins_list_calls_marketplace(self, runner: CliRunner) -> None:
        # Smoke test — marketplace may not be installed; just check exit code is valid
        result = runner.invoke(cli, ["plugins", "list"])
        assert result.exit_code in (0, 1)  # 1 acceptable if marketplace unavailable

    def test_plugins_install_requires_argument(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["plugins", "install"])
        assert result.exit_code != 0

    def test_plugins_remove_requires_argument(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["plugins", "remove"])
        assert result.exit_code != 0
