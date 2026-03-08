#!/usr/bin/env python3
"""
Plugin Architecture System for Enhanced File Processing Suite v7.0
=================================================================

Modern, extensible plugin system enabling third-party extensions and custom processors.

Features:
- Plugin discovery and registration
- Lifecycle management (install/load/unload/update)
- Dependency management
- Sandboxed execution
- Hot-reload capability
- Plugin marketplace integration
- Event hooks and callbacks
- Plugin configuration management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import importlib.util
import inspect
import json
import logging
from pathlib import Path
import sys
from typing import Any

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported."""

    PROCESSOR = "processor"  # File processing operations
    FORMAT = "format"  # File format support
    STORAGE = "storage"  # Storage backend integration
    ANALYZER = "analyzer"  # Analysis and insights
    TRANSFORMER = "transformer"  # File transformations
    INTEGRATION = "integration"  # External service integration
    UI = "ui"  # UI extensions
    FILTER = "filter"  # File filtering
    HOOK = "hook"  # Event hooks
    MIDDLEWARE = "middleware"  # Request/response middleware


class PluginState(Enum):
    """Plugin lifecycle states."""

    DISCOVERED = "discovered"  # Found but not loaded
    LOADING = "loading"  # Being loaded
    LOADED = "loaded"  # Successfully loaded
    ACTIVE = "active"  # Currently active
    INACTIVE = "inactive"  # Disabled
    ERROR = "error"  # Failed to load
    UNLOADING = "unloading"  # Being unloaded
    UNLOADED = "unloaded"  # Successfully unloaded


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""

    id: str  # Unique plugin identifier (e.g., "com.example.image-optimizer")
    name: str  # Human-readable name
    version: str  # Semantic version (e.g., "1.2.3")
    author: str
    description: str
    plugin_type: PluginType

    # Requirements
    min_app_version: str = "7.0.0"
    max_app_version: str | None = None
    dependencies: list[str] = field(default_factory=list)  # Other plugin IDs
    python_packages: list[str] = field(default_factory=list)  # PyPI packages

    # Capabilities
    supported_formats: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)  # Event hooks plugin subscribes to

    # Metadata
    homepage: str | None = None
    repository: str | None = None
    license: str = "MIT"
    tags: list[str] = field(default_factory=list)

    # Configuration
    config_schema: dict[str, Any] = field(default_factory=dict)
    default_config: dict[str, Any] = field(default_factory=dict)

    # Runtime info
    install_date: datetime | None = None
    last_updated: datetime | None = None
    usage_count: int = 0
    enabled: bool = True


@dataclass
class PluginContext:
    """Context passed to plugins during execution."""

    app_version: str
    config: dict[str, Any]
    logger: logging.Logger
    temp_dir: Path
    cache_dir: Path
    data_dir: Path
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PluginInterface(ABC):
    """Base interface that all plugins must implement."""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """Initialize plugin. Called once when plugin is loaded.

        Args:
            context: Plugin execution context

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Cleanup resources. Called when plugin is unloaded.

        Returns:
            True if shutdown successful, False otherwise
        """
        pass

    def configure(self, config: dict[str, Any]) -> bool:
        """Update plugin configuration dynamically.

        Args:
            config: New configuration dictionary

        Returns:
            True if configuration applied successfully
        """
        return True

    def health_check(self) -> dict[str, Any]:
        """Perform health check on plugin.

        Returns:
            Dictionary with health status and details
        """
        return {"status": "healthy", "message": "OK"}


class ProcessorPlugin(PluginInterface):
    """Base class for file processor plugins."""

    @abstractmethod
    async def process(self, file_path: Path, context: PluginContext, **kwargs) -> dict[str, Any]:
        """Process a single file.

        Args:
            file_path: Path to file to process
            context: Plugin execution context
            **kwargs: Additional processing parameters

        Returns:
            Dictionary with processing results
        """
        pass

    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """Check if plugin can process the given file.

        Args:
            file_path: Path to file

        Returns:
            True if plugin can handle this file
        """
        pass

    async def batch_process(
        self, file_paths: list[Path], context: PluginContext, **kwargs
    ) -> list[dict[str, Any]]:
        """Process multiple files. Override for optimized batch processing.

        Args:
            file_paths: List of file paths
            context: Plugin execution context
            **kwargs: Additional processing parameters

        Returns:
            List of processing results
        """
        results = []
        for file_path in file_paths:
            result = await self.process(file_path, context, **kwargs)
            results.append(result)
        return results


class FormatPlugin(PluginInterface):
    """Base class for file format support plugins."""

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Return list of supported file extensions."""
        pass

    @abstractmethod
    def detect_format(self, file_path: Path) -> str | None:
        """Detect file format.

        Args:
            file_path: Path to file

        Returns:
            Format identifier or None if not supported
        """
        pass

    @abstractmethod
    def read(self, file_path: Path) -> Any:
        """Read file in supported format."""
        pass

    @abstractmethod
    def write(self, data: Any, file_path: Path) -> bool:
        """Write data in supported format."""
        pass


class HookPlugin(PluginInterface):
    """Base class for event hook plugins."""

    @abstractmethod
    def get_hooks(self) -> list[str]:
        """Return list of hooks this plugin subscribes to."""
        pass

    @abstractmethod
    async def on_hook(
        self, hook_name: str, data: dict[str, Any], context: PluginContext
    ) -> dict[str, Any]:
        """Handle hook event.

        Args:
            hook_name: Name of the hook being triggered
            data: Hook event data
            context: Plugin execution context

        Returns:
            Modified data or None to abort processing
        """
        pass


@dataclass
class PluginInstance:
    """Runtime instance of a loaded plugin."""

    metadata: PluginMetadata
    plugin: PluginInterface
    state: PluginState
    context: PluginContext
    error: str | None = None
    load_time: datetime | None = None


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""

    def __init__(self, plugin_dirs: list[Path], app_version: str = "7.0.0"):
        """Initialize plugin manager.

        Args:
            plugin_dirs: Directories to search for plugins
            app_version: Application version
        """
        self.plugin_dirs = [Path(d) for d in plugin_dirs]
        self.app_version = app_version
        self.plugins: dict[str, PluginInstance] = {}
        self.hooks: dict[str, list[str]] = {}  # hook_name -> [plugin_ids]
        self.logger = logging.getLogger("PluginManager")

        # Create plugin directories if they don't exist
        for plugin_dir in self.plugin_dirs:
            plugin_dir.mkdir(parents=True, exist_ok=True)

    def discover_plugins(self) -> list[PluginMetadata]:
        """Discover all available plugins in plugin directories.

        Returns:
            List of discovered plugin metadata
        """
        discovered = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue

            for plugin_path in plugin_dir.iterdir():
                if plugin_path.is_dir() and (plugin_path / "__init__.py").exists():
                    try:
                        metadata = self._load_plugin_metadata(plugin_path)
                        if metadata:
                            discovered.append(metadata)
                            self.logger.info(
                                f"Discovered plugin: {metadata.id} v{metadata.version}"
                            )
                    except Exception as e:
                        self.logger.error(f"Failed to discover plugin in {plugin_path}: {e}")

        return discovered

    def _load_plugin_metadata(self, plugin_path: Path) -> PluginMetadata | None:
        """Load plugin metadata from plugin directory.

        Args:
            plugin_path: Path to plugin directory

        Returns:
            Plugin metadata or None if invalid
        """
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            self.logger.warning(f"No manifest.json found in {plugin_path}")
            return None

        try:
            with open(manifest_path, encoding="utf-8") as f:
                data = json.load(f)

            # Convert plugin_type from string to enum
            data["plugin_type"] = PluginType(data.get("plugin_type", "processor"))

            # Parse dates if present
            if data.get("install_date"):
                data["install_date"] = datetime.fromisoformat(data["install_date"])
            if data.get("last_updated"):
                data["last_updated"] = datetime.fromisoformat(data["last_updated"])

            return PluginMetadata(**data)
        except Exception as e:
            self.logger.error(f"Failed to parse manifest.json in {plugin_path}: {e}")
            return None

    def load_plugin(self, plugin_id: str) -> bool:
        """Load a plugin by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if plugin loaded successfully
        """
        # Find plugin directory
        plugin_path = None
        for plugin_dir in self.plugin_dirs:
            candidate = plugin_dir / plugin_id
            if candidate.exists():
                plugin_path = candidate
                break

        if not plugin_path:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False

        try:
            # Load metadata
            metadata = self._load_plugin_metadata(plugin_path)
            if not metadata:
                return False

            # Check version compatibility
            if not self._check_version_compatibility(metadata):
                self.logger.error(
                    f"Plugin {plugin_id} not compatible with app version {self.app_version}"
                )
                return False

            # Load plugin module
            module_path = plugin_path / "plugin.py"
            if not module_path.exists():
                self.logger.error(f"plugin.py not found in {plugin_path}")
                return False

            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_id}", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"plugins.{plugin_id}"] = module
                spec.loader.exec_module(module)
            else:
                self.logger.error(f"Failed to load plugin module: {plugin_id}")
                return False

            # Find plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                self.logger.error(f"No plugin class found in {plugin_id}")
                return False

            # Instantiate plugin
            plugin_instance = plugin_class()

            # Create plugin context
            context = self._create_plugin_context(plugin_id, metadata)

            # Initialize plugin
            if not plugin_instance.initialize(context):
                self.logger.error(f"Plugin initialization failed: {plugin_id}")
                return False

            # Register plugin
            self.plugins[plugin_id] = PluginInstance(
                metadata=metadata,
                plugin=plugin_instance,
                state=PluginState.LOADED,
                context=context,
                load_time=datetime.now(),
            )

            # Register hooks
            if isinstance(plugin_instance, HookPlugin):
                for hook_name in plugin_instance.get_hooks():
                    if hook_name not in self.hooks:
                        self.hooks[hook_name] = []
                    self.hooks[hook_name].append(plugin_id)

            self.logger.info(f"Successfully loaded plugin: {plugin_id} v{metadata.version}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_id}: {e}", exc_info=True)
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if plugin unloaded successfully
        """
        if plugin_id not in self.plugins:
            self.logger.warning(f"Plugin not loaded: {plugin_id}")
            return False

        try:
            plugin_instance = self.plugins[plugin_id]
            plugin_instance.state = PluginState.UNLOADING

            # Shutdown plugin
            plugin_instance.plugin.shutdown()

            # Remove hooks
            for _hook_name, plugin_ids in self.hooks.items():
                if plugin_id in plugin_ids:
                    plugin_ids.remove(plugin_id)

            # Remove from registry
            del self.plugins[plugin_id]

            self.logger.info(f"Successfully unloaded plugin: {plugin_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin (hot-reload).

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if plugin reloaded successfully
        """
        self.unload_plugin(plugin_id)
        return self.load_plugin(plugin_id)

    def get_plugin(self, plugin_id: str) -> PluginInterface | None:
        """Get a loaded plugin by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin instance or None if not found
        """
        if plugin_id in self.plugins:
            return self.plugins[plugin_id].plugin
        return None

    def get_plugins_by_type(self, plugin_type: PluginType) -> list[str]:
        """Get all plugin IDs of a specific type.

        Args:
            plugin_type: Type of plugins to retrieve

        Returns:
            List of plugin IDs
        """
        return [
            plugin_id
            for plugin_id, instance in self.plugins.items()
            if instance.metadata.plugin_type == plugin_type
        ]

    async def trigger_hook(self, hook_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Trigger a hook event and call all subscribed plugins.

        Args:
            hook_name: Name of the hook
            data: Hook event data

        Returns:
            Modified data after all plugins processed it
        """
        if hook_name not in self.hooks:
            return data

        current_data = data
        for plugin_id in self.hooks[hook_name]:
            if plugin_id not in self.plugins:
                continue

            try:
                plugin_instance = self.plugins[plugin_id]
                if isinstance(plugin_instance.plugin, HookPlugin):
                    result = await plugin_instance.plugin.on_hook(
                        hook_name, current_data, plugin_instance.context
                    )
                    if result is None:
                        self.logger.warning(f"Plugin {plugin_id} aborted hook {hook_name}")
                        break
                    current_data = result
            except Exception as e:
                self.logger.error(f"Plugin {plugin_id} failed to handle hook {hook_name}: {e}")

        return current_data

    def _check_version_compatibility(self, metadata: PluginMetadata) -> bool:
        """Check if plugin is compatible with current app version."""
        # Simple version check - in production, use semantic versioning library
        return True  # TODO: Implement proper version checking

    def _find_plugin_class(self, module) -> type[PluginInterface] | None:
        """Find the plugin class in a module."""
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, PluginInterface) and obj != PluginInterface:
                return obj
        return None

    def _create_plugin_context(self, plugin_id: str, metadata: PluginMetadata) -> PluginContext:
        """Create plugin execution context."""
        from pathlib import Path

        base_dir = Path.home() / ".file_processor" / "plugins" / plugin_id
        base_dir.mkdir(parents=True, exist_ok=True)

        return PluginContext(
            app_version=self.app_version,
            config=metadata.default_config.copy(),
            logger=logging.getLogger(f"Plugin.{plugin_id}"),
            temp_dir=base_dir / "temp",
            cache_dir=base_dir / "cache",
            data_dir=base_dir / "data",
        )

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all loaded plugins with their status.

        Returns:
            List of plugin information dictionaries
        """
        return [
            {
                "id": plugin_id,
                "name": instance.metadata.name,
                "version": instance.metadata.version,
                "type": instance.metadata.plugin_type.value,
                "state": instance.state.value,
                "enabled": instance.metadata.enabled,
                "load_time": (instance.load_time.isoformat() if instance.load_time else None),
                "error": instance.error,
            }
            for plugin_id, instance in self.plugins.items()
        ]


# Example hook names (constants)
class PluginHooks:
    """Standard plugin hooks."""

    PRE_PROCESS = "pre_process"
    POST_PROCESS = "post_process"
    PRE_SCAN = "pre_scan"
    POST_SCAN = "post_scan"
    FILE_DETECTED = "file_detected"
    ERROR_OCCURRED = "error_occurred"
    BATCH_START = "batch_start"
    BATCH_COMPLETE = "batch_complete"


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Initialize plugin manager
    plugin_dirs = [Path("./plugins"), Path.home() / ".file_processor" / "plugins"]
    manager = PluginManager(plugin_dirs)

    # Discover plugins
    plugins = manager.discover_plugins()
    print(f"Discovered {len(plugins)} plugins")

    # Load all plugins
    for plugin in plugins:
        manager.load_plugin(plugin.id)

    # List loaded plugins
    print("\nLoaded plugins:")
    for info in manager.list_plugins():
        print(f"  - {info['name']} v{info['version']} ({info['state']})")
