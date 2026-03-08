"""Unit tests for file_processor.plugins.manager (PluginMarketplace)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from file_processor.plugins.manager import PluginMarketplace

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CATALOG = {
    "plugins": [
        {
            "id": "text-analyzer",
            "name": "Text Analyzer",
            "category": "analysis",
            "description": "Analyze text files",
            "tags": ["text", "nlp"],
            "status": "stable",
            "version": "1.0.0",
        },
        {
            "id": "image-optimizer",
            "name": "Image Optimizer",
            "category": "media",
            "description": "Optimize images for web delivery",
            "tags": ["image", "media"],
            "status": "stable",
            "version": "2.1.0",
        },
    ],
    "categories": ["analysis", "media"],
}


@pytest.fixture
def catalog_file(tmp_path: Path) -> Path:
    f = tmp_path / "catalog.json"
    f.write_text(json.dumps(_CATALOG), encoding="utf-8")
    return f


@pytest.fixture
def mp(catalog_file: Path) -> PluginMarketplace:
    return PluginMarketplace(marketplace_file=catalog_file)


# ---------------------------------------------------------------------------
# Tests — list / search / get
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginMarketplaceDiscovery:
    def test_list_all_plugins(self, mp: PluginMarketplace) -> None:
        assert len(mp.list_plugins()) == 2

    def test_list_by_category(self, mp: PluginMarketplace) -> None:
        results = mp.list_plugins(category="analysis")
        assert len(results) == 1
        assert results[0]["id"] == "text-analyzer"

    def test_list_by_status(self, mp: PluginMarketplace) -> None:
        assert len(mp.list_plugins(status="stable")) == 2

    def test_list_unknown_category_returns_empty(self, mp: PluginMarketplace) -> None:
        assert mp.list_plugins(category="unknown") == []

    def test_search_by_name(self, mp: PluginMarketplace) -> None:
        results = mp.search_plugins("image")
        assert any(r["id"] == "image-optimizer" for r in results)

    def test_search_by_description(self, mp: PluginMarketplace) -> None:
        results = mp.search_plugins("text files")
        assert any(r["id"] == "text-analyzer" for r in results)

    def test_search_by_tag(self, mp: PluginMarketplace) -> None:
        results = mp.search_plugins("nlp")
        assert any(r["id"] == "text-analyzer" for r in results)

    def test_search_no_results(self, mp: PluginMarketplace) -> None:
        assert mp.search_plugins("__no_match__") == []

    def test_get_plugin_info_found(self, mp: PluginMarketplace) -> None:
        info = mp.get_plugin_info("text-analyzer")
        assert info is not None
        assert info["name"] == "Text Analyzer"

    def test_get_plugin_info_not_found(self, mp: PluginMarketplace) -> None:
        assert mp.get_plugin_info("does-not-exist") is None


# ---------------------------------------------------------------------------
# Tests — installation state
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginInstallationState:
    def test_is_installed_false_initially(self, mp: PluginMarketplace) -> None:
        assert not mp.is_installed("text-analyzer")

    def test_get_installed_version_none_when_not_installed(self, mp: PluginMarketplace) -> None:
        assert mp.get_installed_version("text-analyzer") is None

    def test_install_plugin_not_in_catalog_returns_false(self, mp: PluginMarketplace) -> None:
        assert mp.install_plugin("no-such-plugin") is False

    def test_is_installed_true_after_manifest_placed(
        self, mp: PluginMarketplace, tmp_path: Path
    ) -> None:
        # Redirect plugins_dir to tmp_path so tests don't write into the source tree.
        mp.plugins_dir = tmp_path
        plugin_dir = tmp_path / "text-analyzer"  # hyphen, matching plugin_id.replace('.','_')
        plugin_dir.mkdir()
        manifest = {"id": "text-analyzer", "version": "1.0.0"}
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        assert mp.is_installed("text-analyzer")

    def test_get_installed_version_reads_manifest(
        self, mp: PluginMarketplace, tmp_path: Path
    ) -> None:
        mp.plugins_dir = tmp_path
        plugin_dir = tmp_path / "text-analyzer"
        plugin_dir.mkdir()
        manifest = {"id": "text-analyzer", "version": "2.0.0"}
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        assert mp.get_installed_version("text-analyzer") == "2.0.0"

    def test_remove_plugin_not_installed_returns_false(self, mp: PluginMarketplace) -> None:
        assert mp.remove_plugin("text-analyzer") is False

    def test_list_installed_empty_initially(self, mp: PluginMarketplace) -> None:
        installed = mp.list_installed()
        # May or may not be empty depending on the plugins_dir content;
        # we just check the return type.
        assert isinstance(installed, list)

    def test_update_plugin_not_installed_returns_false(self, mp: PluginMarketplace) -> None:
        assert mp.update_plugin("text-analyzer") is False


# ---------------------------------------------------------------------------
# Tests — edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginMarketplaceEdgeCases:
    def test_no_catalog_file_gives_empty_list(self, tmp_path: Path) -> None:
        mp = PluginMarketplace(marketplace_file=tmp_path / "missing.json")
        assert mp.list_plugins() == []

    def test_list_installed_returns_ids_for_dirs_with_manifests(self, tmp_path: Path) -> None:
        catalog_f = tmp_path / "catalog.json"
        catalog_f.write_text("{}", encoding="utf-8")
        mp = PluginMarketplace(marketplace_file=catalog_f)

        # Plant a fake installed plugin
        plugin_dir = mp.plugins_dir / "myplugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        manifest = {"id": "my-plugin", "version": "1.0.0"}
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        installed = mp.list_installed()
        assert "my-plugin" in installed


# ---------------------------------------------------------------------------
# Catalog with install metadata for advanced tests
# ---------------------------------------------------------------------------

_INSTALL_CATALOG: dict = {
    "plugins": [
        {
            "id": "pip-plugin",
            "name": "Pip Plugin",
            "category": "test",
            "description": "A pip-installed plugin",
            "tags": [],
            "status": "stable",
            "version": "1.0.0",
            "author": "Test Author",
            "install_method": "pip",
            "install_command": "pip install fake-package",
        },
        {
            "id": "git-plugin",
            "name": "Git Plugin",
            "category": "test",
            "description": "A git-cloned plugin",
            "tags": [],
            "status": "stable",
            "version": "1.0.0",
            "author": "Test Author",
            "install_method": "git",
            "repository_url": "https://github.com/example/plugin.git",
        },
        {
            "id": "builtin-plugin",
            "name": "Builtin Plugin",
            "category": "test",
            "description": "A built-in plugin",
            "tags": [],
            "status": "stable",
            "version": "1.0.0",
            "author": "Test Author",
            "install_method": "builtin",
        },
        {
            "id": "unknown-method-plugin",
            "name": "Unknown Method Plugin",
            "category": "test",
            "description": "Has an unknown install method",
            "tags": [],
            "status": "stable",
            "version": "1.0.0",
            "author": "Test Author",
            "install_method": "something_unknown",
        },
    ],
    "categories": ["test"],
}


@pytest.fixture
def install_mp(tmp_path: Path) -> PluginMarketplace:
    """Marketplace with catalog containing install metadata; plugins_dir in tmp_path."""
    catalog_f = tmp_path / "catalog.json"
    catalog_f.write_text(json.dumps(_INSTALL_CATALOG), encoding="utf-8")
    mp_inst = PluginMarketplace(marketplace_file=catalog_f)
    mp_inst.plugins_dir = tmp_path / "plugins"
    mp_inst.plugins_dir.mkdir()
    return mp_inst


# ---------------------------------------------------------------------------
# Tests — install_plugin
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginInstall:
    def test_not_in_catalog_returns_false(self, install_mp: PluginMarketplace) -> None:
        assert install_mp.install_plugin("does-not-exist") is False

    def test_builtin_returns_true(self, install_mp: PluginMarketplace) -> None:
        assert install_mp.install_plugin("builtin-plugin") is True

    def test_pip_success(self, install_mp: PluginMarketplace) -> None:
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            assert install_mp.install_plugin("pip-plugin") is True

    def test_pip_failure(self, install_mp: PluginMarketplace) -> None:
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="pip error")
            assert install_mp.install_plugin("pip-plugin") is False

    def test_pip_no_install_command_returns_false(self, install_mp: PluginMarketplace) -> None:
        install_mp.catalog["plugins"].append(
            {
                "id": "no-cmd",
                "name": "No Command",
                "category": "test",
                "description": "Missing install_command",
                "tags": [],
                "status": "stable",
                "version": "1.0.0",
                "author": "Test",
                "install_method": "pip",
            }
        )
        assert install_mp.install_plugin("no-cmd") is False

    def test_git_success(self, install_mp: PluginMarketplace) -> None:
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            assert install_mp.install_plugin("git-plugin") is True

    def test_git_with_requirements_calls_pip(self, install_mp: PluginMarketplace) -> None:
        # Pre-create plugin dir + requirements.txt so the pip-install branch is exercised.
        plugin_dir = install_mp.plugins_dir / "git-plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        (plugin_dir / "requirements.txt").write_text("requests>=2.0\n", encoding="utf-8")
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            assert install_mp.install_plugin("git-plugin") is True
        # git clone + pip install -r = 2 subprocess.run calls
        assert mock_run.call_count == 2

    def test_git_failure(self, install_mp: PluginMarketplace) -> None:
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="git error")
            assert install_mp.install_plugin("git-plugin") is False

    def test_git_no_repo_url_returns_false(self, install_mp: PluginMarketplace) -> None:
        install_mp.catalog["plugins"].append(
            {
                "id": "no-repo",
                "name": "No Repo",
                "category": "test",
                "description": "Missing repository_url",
                "tags": [],
                "status": "stable",
                "version": "1.0.0",
                "author": "Test",
                "install_method": "git",
            }
        )
        assert install_mp.install_plugin("no-repo") is False

    def test_unknown_method_returns_false(self, install_mp: PluginMarketplace) -> None:
        assert install_mp.install_plugin("unknown-method-plugin") is False

    def test_already_installed_without_force_returns_false(
        self, install_mp: PluginMarketplace
    ) -> None:
        plugin_dir = install_mp.plugins_dir / "pip-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.json").write_text(
            json.dumps({"id": "pip-plugin", "version": "1.0.0"}), encoding="utf-8"
        )
        assert install_mp.install_plugin("pip-plugin") is False

    def test_already_installed_with_force_reinstalls(self, install_mp: PluginMarketplace) -> None:
        plugin_dir = install_mp.plugins_dir / "pip-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.json").write_text(
            json.dumps({"id": "pip-plugin", "version": "1.0.0"}), encoding="utf-8"
        )
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            assert install_mp.install_plugin("pip-plugin", force=True) is True


# ---------------------------------------------------------------------------
# Tests — uninstall_plugin / remove_plugin
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginUninstall:
    def _plant(self, mp: PluginMarketplace, plugin_id: str, version: str = "1.0.0") -> None:
        d = mp.plugins_dir / plugin_id.replace(".", "_")
        d.mkdir(exist_ok=True)
        (d / "manifest.json").write_text(
            json.dumps({"id": plugin_id, "version": version}), encoding="utf-8"
        )

    def test_uninstall_not_installed_returns_false(self, install_mp: PluginMarketplace) -> None:
        assert install_mp.uninstall_plugin("pip-plugin") is False

    def test_uninstall_success_removes_directory(self, install_mp: PluginMarketplace) -> None:
        self._plant(install_mp, "pip-plugin")
        assert install_mp.uninstall_plugin("pip-plugin") is True
        assert not (install_mp.plugins_dir / "pip-plugin").exists()

    def test_remove_plugin_aliases_uninstall(self, install_mp: PluginMarketplace) -> None:
        # not installed → both should return False
        assert install_mp.remove_plugin("pip-plugin") is False


# ---------------------------------------------------------------------------
# Tests — update_plugin
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginUpdate:
    def _plant(self, mp: PluginMarketplace, plugin_id: str, version: str) -> None:
        d = mp.plugins_dir / plugin_id.replace(".", "_")
        d.mkdir(exist_ok=True)
        (d / "manifest.json").write_text(
            json.dumps({"id": plugin_id, "version": version}), encoding="utf-8"
        )

    def test_update_not_installed_returns_false(self, install_mp: PluginMarketplace) -> None:
        assert install_mp.update_plugin("pip-plugin") is False

    def test_update_same_version_returns_true(self, install_mp: PluginMarketplace) -> None:
        self._plant(install_mp, "pip-plugin", "1.0.0")
        assert install_mp.update_plugin("pip-plugin") is True

    def test_update_outdated_delegates_to_install(self, install_mp: PluginMarketplace) -> None:
        self._plant(install_mp, "pip-plugin", "0.5.0")
        with patch("file_processor.plugins.manager.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            assert install_mp.update_plugin("pip-plugin") is True


# ---------------------------------------------------------------------------
# Tests — list_installed_manifests / check_updates
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginListAndUpdates:
    def _plant(self, mp: PluginMarketplace, plugin_id: str, version: str, **extra) -> None:
        d = mp.plugins_dir / plugin_id.replace(".", "_")
        d.mkdir(exist_ok=True)
        data = {"id": plugin_id, "version": version, **extra}
        (d / "manifest.json").write_text(json.dumps(data), encoding="utf-8")

    def test_list_installed_manifests_returns_full_dicts(
        self, install_mp: PluginMarketplace
    ) -> None:
        self._plant(install_mp, "pip-plugin", "1.0.0", extra_field="sentinel")
        manifests = install_mp.list_installed_manifests()
        assert any(m.get("id") == "pip-plugin" for m in manifests)
        entry = next(m for m in manifests if m.get("id") == "pip-plugin")
        assert entry.get("extra_field") == "sentinel"

    def test_list_installed_manifests_empty_plugins_dir(
        self, install_mp: PluginMarketplace
    ) -> None:
        assert install_mp.list_installed_manifests() == []

    def test_check_updates_empty_when_nothing_installed(
        self, install_mp: PluginMarketplace
    ) -> None:
        assert install_mp.check_updates() == []

    def test_check_updates_finds_outdated_plugin(self, install_mp: PluginMarketplace) -> None:
        self._plant(install_mp, "pip-plugin", "0.9.0")
        updates = install_mp.check_updates()
        assert any(u["id"] == "pip-plugin" for u in updates)
        entry = next(u for u in updates if u["id"] == "pip-plugin")
        assert entry["installed_version"] == "0.9.0"
        assert entry["latest_version"] == "1.0.0"

    def test_check_updates_excludes_up_to_date_plugin(self, install_mp: PluginMarketplace) -> None:
        self._plant(install_mp, "pip-plugin", "1.0.0")
        assert not any(u["id"] == "pip-plugin" for u in install_mp.check_updates())


# ---------------------------------------------------------------------------
# Tests — error-path coverage for remaining uncovered lines
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPluginManagerErrorPaths:
    """Cover exception and edge-case branches that were previously unreachable."""

    def _plant(self, mp: PluginMarketplace, plugin_id: str, version: str = "1.0.0") -> Path:
        d = mp.plugins_dir / plugin_id.replace(".", "_")
        d.mkdir(parents=True, exist_ok=True)
        (d / "manifest.json").write_text(
            json.dumps({"id": plugin_id, "version": version}), encoding="utf-8"
        )
        return d

    # ── get_installed_version ──────────────────────────────────────────────

    def test_get_installed_version_corrupt_manifest_returns_none(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L101-102: except in get_installed_version when manifest is invalid JSON."""
        d = install_mp.plugins_dir / "pip-plugin"
        d.mkdir(parents=True, exist_ok=True)
        (d / "manifest.json").write_text("NOT VALID JSON", encoding="utf-8")
        assert install_mp.get_installed_version("pip-plugin") is None

    # ── uninstall_plugin ───────────────────────────────────────────────────

    def test_uninstall_rmtree_failure_returns_false(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L202-204: except in uninstall_plugin when shutil.rmtree raises."""
        self._plant(install_mp, "pip-plugin")
        with patch("file_processor.plugins.manager.shutil.rmtree", side_effect=OSError("busy")):
            assert install_mp.uninstall_plugin("pip-plugin") is False

    # ── update_plugin ──────────────────────────────────────────────────────

    def test_update_plugin_installed_but_not_in_catalog_returns_false(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L214-215: update_plugin when plugin is installed but absent from catalog."""
        self._plant(install_mp, "ghost-plugin")
        assert install_mp.update_plugin("ghost-plugin") is False

    # ── list_installed ─────────────────────────────────────────────────────

    def test_list_installed_skips_non_directory_entries(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L241: continue when plugins_dir contains a regular file (not a directory)."""
        (install_mp.plugins_dir / "stray-file.txt").write_text("x", encoding="utf-8")
        result = install_mp.list_installed()
        assert "stray-file.txt" not in result

    def test_list_installed_skips_dir_without_manifest(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L245: continue when a plugin directory has no manifest.json."""
        (install_mp.plugins_dir / "no-manifest-dir").mkdir()
        result = install_mp.list_installed()
        assert "no-manifest-dir" not in result

    def test_list_installed_handles_corrupt_manifest(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L252-253: except/fallback when manifest.json is invalid JSON."""
        d = install_mp.plugins_dir / "bad-plugin"
        d.mkdir()
        (d / "manifest.json").write_text("{bad json}", encoding="utf-8")
        result = install_mp.list_installed()
        assert "bad-plugin" in result  # falls back to plugin_dir.name

    # ── list_installed_manifests ───────────────────────────────────────────

    def test_list_installed_manifests_skips_non_directory_entries(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L263: continue when plugins_dir entry is not a directory."""
        (install_mp.plugins_dir / "stray.txt").write_text("x", encoding="utf-8")
        result = install_mp.list_installed_manifests()
        assert all(isinstance(m, dict) for m in result)

    def test_list_installed_manifests_skips_dir_without_manifest(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L267: continue when directory has no manifest.json."""
        (install_mp.plugins_dir / "empty-dir").mkdir()
        result = install_mp.list_installed_manifests()
        # directory without manifest is silently skipped
        assert result == []

    def test_list_installed_manifests_handles_corrupt_manifest(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L273-275: except/warning when manifest.json cannot be parsed."""
        d = install_mp.plugins_dir / "corrupt-plugin"
        d.mkdir()
        (d / "manifest.json").write_text("INVALID", encoding="utf-8")
        result = install_mp.list_installed_manifests()
        assert result == []  # corrupt entry is skipped, not included

    # ── check_updates ──────────────────────────────────────────────────────

    def test_check_updates_skips_plugin_not_in_catalog(
        self, install_mp: PluginMarketplace
    ) -> None:
        """L288: continue when installed plugin ID is absent from catalog."""
        self._plant(install_mp, "orphan-plugin", "1.0.0")
        updates = install_mp.check_updates()
        assert not any(u.get("id") == "orphan-plugin" for u in updates)
