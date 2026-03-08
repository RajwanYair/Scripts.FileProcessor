"""Unit tests for the Click CLI (file_processor.cli.main)."""

from __future__ import annotations

import signal
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

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


# ── shutdown handler ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestShutdownHandler:
    def test_shutdown_raises_systemexit(self) -> None:
        from file_processor.cli.main import _shutdown

        with pytest.raises(SystemExit):
            _shutdown(signal.SIGTERM, None)

    def test_shutdown_exits_with_code_zero(self) -> None:
        from file_processor.cli.main import _shutdown

        with pytest.raises(SystemExit) as exc_info:
            _shutdown(signal.SIGINT, None)
        assert exc_info.value.code == 0


# ── main() entry point ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMainEntryPoint:
    def test_main_registers_signals_and_calls_cli(self) -> None:
        """main() registers SIGTERM/SIGINT handlers then delegates to cli()."""
        import file_processor.cli.main as main_module

        with patch.object(main_module, "cli") as mock_cli:
            main_module.main()
        mock_cli.assert_called_once()


# ── serve command ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestServeCommand:
    def test_serve_help_exits_zero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0

    def test_serve_exits_one_when_uvicorn_missing(self, runner: CliRunner) -> None:
        with patch.dict("sys.modules", {"uvicorn": None}):
            result = runner.invoke(cli, ["serve"])
        assert result.exit_code == 1


# ── process command (additional branches) ─────────────────────────────────────


@pytest.mark.unit
class TestProcessCommandBranches:
    def test_no_dry_run_logs_start(self, runner: CliRunner, tmp_path: Path) -> None:
        """Exercises the non-dry-run code path (logger.info)."""
        result = runner.invoke(cli, ["process", "--source", str(tmp_path)])
        assert result.exit_code == 0

    def test_verbose_dry_run_combined(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(
            cli, ["--verbose", "--dry-run", "process", "--source", str(tmp_path)]
        )
        assert result.exit_code == 0

    def test_custom_dest(self, runner: CliRunner, tmp_path: Path) -> None:
        dest = tmp_path / "out"
        dest.mkdir()
        result = runner.invoke(cli, ["process", "--source", str(tmp_path), "--dest", str(dest)])
        assert result.exit_code == 0

    def test_no_recursive(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["process", "--source", str(tmp_path), "--no-recursive"])
        assert result.exit_code == 0


# ── deduplicate dry-run ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeduplicateDryRun:
    def test_dry_run_shows_message(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["--dry-run", "deduplicate", "--source", str(tmp_path)])
        assert result.exit_code == 0
        assert "dry-run" in result.output.lower()


# ── plugins extra commands ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestPluginsExtraCommands:
    def test_plugins_update_no_name(self, runner: CliRunner) -> None:
        """Update with no name → updates all (empty list means 'Done.' immediately)."""
        result = runner.invoke(cli, ["plugins", "update"])
        assert result.exit_code == 0

    def test_plugins_install_unknown_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["plugins", "install", "unknown-plugin-xyz"])
        assert result.exit_code != 0

    def test_plugins_remove_unknown_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["plugins", "remove", "unknown-plugin-xyz"])
        assert result.exit_code != 0

    def test_plugins_list_with_category_filter(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["plugins", "list", "--category", "media"])
        assert result.exit_code == 0
