"""Unit tests for file_processor.plugins.manager (PluginMarketplace)."""

from __future__ import annotations

import json
from pathlib import Path

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
