#!/usr/bin/env python3
"""Plugin Manager - Install, update, and manage plugins."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

logger = logging.getLogger(__name__)


class PluginMarketplace:
    """Manage plugin discovery, installation, and updates"""

    def __init__(self, marketplace_file: Path | None = None):
        if marketplace_file is None:
            marketplace_file = Path(__file__).parent / "plugins" / "plugin_marketplace.json"

        self.marketplace_file = marketplace_file
        self.plugins_dir = Path(__file__).parent / "plugins"
        self.plugins_dir.mkdir(exist_ok=True)

        # Load marketplace catalog
        if self.marketplace_file.exists():
            with open(self.marketplace_file, encoding="utf-8") as f:
                self.catalog = json.load(f)
        else:
            self.catalog = {"plugins": [], "categories": []}

    def list_plugins(self, category: str | None = None, status: str | None = None) -> list[dict]:
        """List available plugins"""
        plugins = self.catalog.get("plugins", [])

        if category:
            plugins = [p for p in plugins if p.get("category") == category]

        if status:
            plugins = [p for p in plugins if p.get("status") == status]

        return plugins

    def search_plugins(self, query: str) -> list[dict]:
        """Search plugins by name, description, or tags"""
        query = query.lower()
        results = []

        for plugin in self.catalog.get("plugins", []):
            # Search in name
            if query in plugin.get("name", "").lower():
                results.append(plugin)
                continue

            # Search in description
            if query in plugin.get("description", "").lower():
                results.append(plugin)
                continue

            # Search in tags
            tags = plugin.get("tags", [])
            if any(query in tag.lower() for tag in tags):
                results.append(plugin)
                continue

        return results

    def get_plugin_info(self, plugin_id: str) -> dict | None:
        """Get detailed info about a plugin"""
        for plugin in self.catalog.get("plugins", []):
            if plugin.get("id") == plugin_id:
                return plugin
        return None

    def is_installed(self, plugin_id: str) -> bool:
        """Check if a plugin is installed"""
        # Check for plugin directory
        plugin_dir = self.plugins_dir / plugin_id.replace(".", "_")
        if not plugin_dir.exists():
            return False

        # Check for manifest
        manifest_file = plugin_dir / "manifest.json"
        return manifest_file.exists()

    def get_installed_version(self, plugin_id: str) -> str | None:
        """Get installed plugin version"""
        if not self.is_installed(plugin_id):
            return None

        plugin_dir = self.plugins_dir / plugin_id.replace(".", "_")
        manifest_file = plugin_dir / "manifest.json"

        try:
            with open(manifest_file, encoding="utf-8") as f:
                manifest = json.load(f)
                return manifest.get("version")
        except Exception:
            return None

    def install_plugin(self, plugin_id: str, force: bool = False) -> bool:
        """Install a plugin"""
        plugin_info = self.get_plugin_info(plugin_id)
        if not plugin_info:
            print(f"❌ Plugin '{plugin_id}' not found in marketplace")
            return False

        # Check if already installed
        if self.is_installed(plugin_id) and not force:
            installed_version = self.get_installed_version(plugin_id)
            marketplace_version = plugin_info.get("version")
            print(f"⚠️  Plugin already installed (v{installed_version})")
            print(f"   Marketplace version: v{marketplace_version}")
            print("   Use --force to reinstall")
            return False

        print(f"📦 Installing: {plugin_info['name']} v{plugin_info['version']}")
        print(f"   Author: {plugin_info['author']}")
        print(f"   Category: {plugin_info['category']}")

        # Check installation method
        install_method = plugin_info.get("install_method", "pip")

        if install_method == "builtin":
            print("✅ Plugin is built-in, already available")
            return True

        elif install_method == "pip":
            # Install via pip
            install_cmd = plugin_info.get("install_command")
            if not install_cmd:
                print("❌ No install command specified")
                return False

            print(f"   Running: {install_cmd}")
            result = subprocess.run(shlex.split(install_cmd), capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Plugin installed successfully")
                return True
            else:
                print(f"❌ Installation failed: {result.stderr}")
                return False

        elif install_method == "git":
            # Clone from git repository
            repo_url = plugin_info.get("repository_url")
            if not repo_url:
                print("❌ No repository URL specified")
                return False

            plugin_dir = self.plugins_dir / plugin_id.replace(".", "_")

            print(f"   Cloning from: {repo_url}")
            result = subprocess.run(
                ["git", "clone", repo_url, str(plugin_dir)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Install dependencies
                requirements_file = plugin_dir / "requirements.txt"
                if requirements_file.exists():
                    print("   Installing dependencies...")
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            str(requirements_file),
                        ]
                    )

                print("✅ Plugin installed successfully")
                return True
            else:
                print(f"❌ Installation failed: {result.stderr}")
                return False

        else:
            print(f"❌ Unknown installation method: {install_method}")
            return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        if not self.is_installed(plugin_id):
            print(f"⚠️  Plugin '{plugin_id}' is not installed")
            return False

        plugin_dir = self.plugins_dir / plugin_id.replace(".", "_")

        try:
            shutil.rmtree(plugin_dir)
            print(f"✅ Plugin '{plugin_id}' uninstalled successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to uninstall: {e}")
            return False

    def update_plugin(self, plugin_id: str) -> bool:
        """Update a plugin to latest version"""
        if not self.is_installed(plugin_id):
            print(f"⚠️  Plugin '{plugin_id}' is not installed")
            return False

        plugin_info = self.get_plugin_info(plugin_id)
        if not plugin_info:
            print(f"❌ Plugin '{plugin_id}' not found in marketplace")
            return False

        installed_version = self.get_installed_version(plugin_id)
        marketplace_version = plugin_info.get("version")

        if installed_version == marketplace_version:
            print(f"✅ Plugin is already up to date (v{installed_version})")
            return True

        print(f"🔄 Updating: {plugin_info['name']}")
        print(f"   Current version: v{installed_version}")
        print(f"   Latest version: v{marketplace_version}")

        # Reinstall
        return self.install_plugin(plugin_id, force=True)

    def remove_plugin(self, plugin_id: str) -> bool:
        """Alias for uninstall_plugin — remove an installed plugin."""
        return self.uninstall_plugin(plugin_id)

    def list_installed(self) -> list[str]:
        """Return IDs of all installed plugins."""
        ids: list[str] = []

        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue

            manifest_file = plugin_dir / "manifest.json"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file, encoding="utf-8") as f:
                    manifest = json.load(f)
                    pid = manifest.get("id") or plugin_dir.name
                    ids.append(pid)
            except Exception:
                ids.append(plugin_dir.name)

        return ids

    def list_installed_manifests(self) -> list[dict]:
        """Return full manifest dicts for all installed plugins."""
        installed = []

        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue

            manifest_file = plugin_dir / "manifest.json"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file, encoding="utf-8") as f:
                    manifest = json.load(f)
                    installed.append(manifest)
            except Exception:
                logger.warning("Failed to read manifest: %s", manifest_file)
                continue

        return installed

    def check_updates(self) -> list[dict]:
        """Check for plugin updates."""
        updates_available = []

        for plugin_id in self.list_installed():
            installed_version = self.get_installed_version(plugin_id)

            plugin_info = self.get_plugin_info(plugin_id)
            if not plugin_info:
                continue

            marketplace_version = plugin_info.get("version")

            if installed_version != marketplace_version:
                updates_available.append(
                    {
                        "id": plugin_id,
                        "name": plugin_info["name"],
                        "installed_version": installed_version,
                        "latest_version": marketplace_version,
                    }
                )

        return updates_available
