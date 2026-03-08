# Plugin SDK Documentation - File Processing Suite v7.0

## 🚀 Introduction

The File Processing Suite Plugin SDK enables developers to extend the platform with custom processors, file format support, integrations, and more. This guide covers everything you need to build, test, and publish plugins.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Plugin Types](#plugin-types)
3. [Plugin Structure](#plugin-structure)
4. [Development Guide](#development-guide)
5. [API Reference](#api-reference)
6. [Testing](#testing)
7. [Publishing](#publishing)
8. [Best Practices](#best-practices)

---

## Quick Start

### Prerequisites

- Python 3.9+
- File Processing Suite v7.0+
- Basic understanding of async/await

### Create Your First Plugin

1. **Create plugin directory**

```bash
mkdir -p plugins/my-first-plugin
cd plugins/my-first-plugin
```

1. **Create manifest.json**

```json
{
  "id": "com.yourname.my-first-plugin",
  "name": "My First Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Description of what your plugin does",
  "plugin_type": "processor",
  "min_app_version": "7.0.0",
  "supported_formats": [".txt"],
  "license": "MIT"
}
```

1. **Create plugin.py**

```python
from pathlib import Path
from core.plugin_system import ProcessorPlugin, PluginMetadata, PluginContext

class MyFirstPlugin(ProcessorPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="com.yourname.my-first-plugin",
            name="My First Plugin",
            version="1.0.0",
            author="Your Name",
            description="Description of what your plugin does",
            plugin_type=PluginType.PROCESSOR
        )
    
    def initialize(self, context: PluginContext) -> bool:
        self.context = context
        context.logger.info("Plugin initialized!")
        return True
    
    def shutdown(self) -> bool:
        self.context.logger.info("Plugin shutting down")
        return True
    
    def can_process(self, file_path: Path) -> bool:
        return file_path.suffix == '.txt'
    
    async def process(self, file_path: Path, context: PluginContext, **kwargs):
        # Your processing logic here
        content = file_path.read_text()
        result = content.upper()  # Example: convert to uppercase
        
        return {
            "success": True,
            "result": result
        }

Plugin = MyFirstPlugin  # Required: export your plugin class
```

1. **Test your plugin**

```bash
python plugin.py
```

1. **Load in application**

```python
from core.plugin_system import PluginManager

manager = PluginManager(["./plugins"])
manager.load_plugin("com.yourname.my-first-plugin")
```

---

## Plugin Types

### 1. Processor Plugin

Process and transform files.

**Use Cases**: Image optimization, file conversion, compression

**Base Class**: `ProcessorPlugin`

**Example**:

```python
class ImageOptimizerPlugin(ProcessorPlugin):
    async def process(self, file_path: Path, context: PluginContext, **kwargs):
        # Optimize image
        return {"success": True, "size_reduced": "50%"}
```

### 2. Format Plugin

Add support for new file formats.

**Use Cases**: Custom file formats, specialized formats

**Base Class**: `FormatPlugin`

**Example**:

```python
class CustomFormatPlugin(FormatPlugin):
    def get_supported_formats(self) -> List[str]:
        return [".custom", ".myformat"]
    
    def read(self, file_path: Path) -> Any:
        # Read custom format
        pass
    
    def write(self, data: Any, file_path: Path) -> bool:
        # Write custom format
        pass
```

### 3. Hook Plugin

React to events in the processing pipeline.

**Use Cases**: Logging, notifications, workflow automation

**Base Class**: `HookPlugin`

**Example**:

```python
class NotificationPlugin(HookPlugin):
    def get_hooks(self) -> List[str]:
        return ["pre_process", "post_process", "error_occurred"]
    
    async def on_hook(self, hook_name: str, data: Dict, context: PluginContext):
        if hook_name == "error_occurred":
            # Send notification
            await send_email(f"Error: {data['error']}")
        return data
```

### 4. Storage Plugin

Integrate with storage backends.

**Use Cases**: Cloud storage, custom databases

**Base Class**: `StoragePlugin`

### 5. Analyzer Plugin

Analyze files and extract insights.

**Use Cases**: File analysis, metadata extraction

**Base Class**: `AnalyzerPlugin`

---

## Plugin Structure

### Directory Layout

```
my-plugin/
├── __init__.py          # Package initialization
├── manifest.json        # Plugin metadata (required)
├── plugin.py           # Main plugin code (required)
├── README.md           # Documentation
├── requirements.txt    # Python dependencies
├── config/
│   └── schema.json     # Configuration schema
├── tests/
│   ├── test_plugin.py
│   └── fixtures/
└── docs/
    └── usage.md
```

### Manifest.json Schema

```json
{
  "id": "string (required, unique)",
  "name": "string (required)",
  "version": "string (required, semver)",
  "author": "string (required)",
  "description": "string (required)",
  "plugin_type": "processor|format|hook|storage|analyzer|...",
  
  "min_app_version": "string (semver)",
  "max_app_version": "string (semver, optional)",
  
  "dependencies": ["array of plugin IDs"],
  "python_packages": ["array of PyPI packages"],
  
  "supported_formats": ["array of file extensions"],
  "capabilities": ["array of capability strings"],
  "hooks": ["array of hook names"],
  
  "homepage": "string (URL)",
  "repository": "string (URL)",
  "license": "string",
  "tags": ["array of tags"],
  
  "config_schema": {
    "property_name": {
      "type": "string|integer|boolean|array|object",
      "default": "any",
      "description": "string"
    }
  },
  
  "default_config": {
    "property_name": "default_value"
  }
}
```

---

## Development Guide

### Plugin Lifecycle

1. **Discovery**: Plugin found in plugin directory
2. **Loading**: Manifest parsed, dependencies checked
3. **Initialization**: `initialize()` called
4. **Active**: Plugin ready to process files
5. **Shutdown**: `shutdown()` called before unload

### PluginContext

Every plugin receives a `PluginContext` with:

```python
@dataclass
class PluginContext:
    app_version: str           # Application version
    config: Dict[str, Any]     # Plugin configuration
    logger: logging.Logger     # Plugin-specific logger
    temp_dir: Path            # Temporary directory
    cache_dir: Path           # Cache directory
    data_dir: Path            # Persistent data directory
    user_id: Optional[str]     # Current user (if authenticated)
    session_id: Optional[str]  # Session ID
    metadata: Dict[str, Any]   # Additional metadata
```

### Processing Files

```python
async def process(self, file_path: Path, context: PluginContext, **kwargs) -> Dict[str, Any]:
    """
    Process a single file.
    
    Args:
        file_path: Path to file
        context: Execution context
        **kwargs: Additional options
    
    Returns:
        Dictionary with results:
        {
            "success": bool,
            "result": Any,
            "error": Optional[str],
            "metadata": Dict[str, Any]
        }
    """
    try:
        # Your processing logic
        result = await self._do_processing(file_path)
        
        return {
            "success": True,
            "result": result,
            "metadata": {
                "processed_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        context.logger.error(f"Processing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### Batch Processing

For optimized batch processing, override `batch_process()`:

```python
async def batch_process(self, file_paths: List[Path], context: PluginContext, **kwargs):
    """Process multiple files efficiently."""
    tasks = [self.process(fp, context, **kwargs) for fp in file_paths]
    return await asyncio.gather(*tasks)
```

### Configuration

Access configuration:

```python
quality = context.config.get('quality', 85)
max_size = context.config.get('max_size', 1920)
```

Update configuration:

```python
def configure(self, config: Dict[str, Any]) -> bool:
    self.context.config.update(config)
    self.context.logger.info(f"Configuration updated: {config}")
    return True
```

### Logging

```python
context.logger.debug("Debug message")
context.logger.info("Info message")
context.logger.warning("Warning message")
context.logger.error("Error message")
```

### Caching

Use cache directory for temporary data:

```python
cache_file = context.cache_dir / f"{file_hash}.cache"
if cache_file.exists():
    return pickle.load(cache_file.open('rb'))
```

### Error Handling

Always handle errors gracefully:

```python
try:
    result = await self.risky_operation()
except SpecificError as e:
    context.logger.error(f"Specific error: {e}")
    return {"success": False, "error": str(e)}
except Exception as e:
    context.logger.exception("Unexpected error")
    return {"success": False, "error": "Internal error"}
```

---

## API Reference

### PluginInterface

Base interface all plugins must implement.

#### Methods

**`get_metadata() -> PluginMetadata`**

- Returns plugin metadata
- Called during plugin discovery

**`initialize(context: PluginContext) -> bool`**

- Initialize plugin resources
- Return True if successful
- Called once when plugin loads

**`shutdown() -> bool`**

- Cleanup resources
- Return True if successful
- Called when plugin unloads

**`configure(config: Dict[str, Any]) -> bool`**

- Update configuration dynamically
- Return True if successful

**`health_check() -> Dict[str, Any]`**

- Perform health check
- Return status dictionary

### ProcessorPlugin

Extends `PluginInterface` for file processors.

#### Methods

**`async process(file_path: Path, context: PluginContext, **kwargs) -> Dict[str, Any]`**

- Process single file
- Return results dictionary

**`can_process(file_path: Path) -> bool`**

- Check if plugin can handle file
- Return True if supported

**`async batch_process(file_paths: List[Path], context: PluginContext, **kwargs) -> List[Dict[str, Any]]`**

- Process multiple files
- Override for optimizations

### FormatPlugin

Extends `PluginInterface` for format support.

#### Methods

**`get_supported_formats() -> List[str]`**

- Return supported extensions

**`detect_format(file_path: Path) -> Optional[str]`**

- Detect file format
- Return format ID or None

**`read(file_path: Path) -> Any`**

- Read file content

**`write(data: Any, file_path: Path) -> bool`**

- Write data to file

### HookPlugin

Extends `PluginInterface` for event hooks.

#### Methods

**`get_hooks() -> List[str]`**

- Return subscribed hook names

**`async on_hook(hook_name: str, data: Dict[str, Any], context: PluginContext) -> Dict[str, Any]`**

- Handle hook event
- Return modified data or None to abort

### Standard Hooks

- `pre_process` - Before processing starts
- `post_process` - After processing completes
- `pre_scan` - Before directory scan
- `post_scan` - After directory scan
- `file_detected` - When file is found
- `error_occurred` - When error happens
- `batch_start` - Batch processing starts
- `batch_complete` - Batch processing completes

---

## Testing

### Unit Tests

```python
import pytest
from pathlib import Path
from core.plugin_system import PluginContext

@pytest.fixture
def plugin():
    from plugin import MyPlugin
    return MyPlugin()

@pytest.fixture
def context():
    return PluginContext(
        app_version="7.0.0",
        config={},
        logger=logging.getLogger("test"),
        temp_dir=Path("./temp"),
        cache_dir=Path("./cache"),
        data_dir=Path("./data")
    )

def test_initialize(plugin, context):
    assert plugin.initialize(context) == True

@pytest.mark.asyncio
async def test_process(plugin, context, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    result = await plugin.process(test_file, context)
    assert result["success"] == True
```

### Integration Tests

```python
def test_plugin_integration():
    from core.plugin_system import PluginManager
    
    manager = PluginManager(["./plugins"])
    assert manager.load_plugin("com.yourname.my-plugin")
    
    plugin = manager.get_plugin("com.yourname.my-plugin")
    assert plugin is not None
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test
pytest tests/test_plugin.py::test_process
```

---

## Publishing

### 1. Package Your Plugin

```bash
# Create distribution
tar -czf my-plugin-1.0.0.tar.gz my-plugin/
```

### 2. Submit to Marketplace

1. Create account at marketplace.fileprocessor.com
2. Upload plugin package
3. Fill in metadata
4. Submit for review

### 3. Versioning

Follow semantic versioning (semver):

- `1.0.0` - Major.Minor.Patch
- `1.1.0` - New feature (backward compatible)
- `1.0.1` - Bug fix
- `2.0.0` - Breaking change

### 4. Documentation

Include:

- README.md with overview
- Usage examples
- Configuration options
- Troubleshooting guide
- Changelog

---

## Best Practices

### Performance

1. **Use async/await** for I/O operations

```python
async def process(self, file_path: Path, context: PluginContext, **kwargs):
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
```

1. **Implement batch processing** for efficiency
2. **Cache results** when appropriate
3. **Use memory efficiently** - process streams, not entire files
4. **Optimize algorithms** - O(n) > O(n²)

### Security

1. **Validate inputs**

```python
if not file_path.exists():
    raise ValueError("File not found")
```

1. **Sanitize file paths**

```python
file_path = file_path.resolve()  # Prevent directory traversal
```

1. **Limit resource usage**

```python
if file_path.stat().st_size > MAX_FILE_SIZE:
    raise ValueError("File too large")
```

1. **Handle sensitive data** - Don't log passwords, API keys
2. **Use dependencies wisely** - Audit packages

### Compatibility

1. **Specify version ranges** in manifest
2. **Test on multiple platforms** (Windows, Linux, macOS)
3. **Handle missing dependencies** gracefully
4. **Provide fallbacks** when possible

### User Experience

1. **Provide clear error messages**
2. **Log useful information**
3. **Include progress tracking**
4. **Document configuration options**
5. **Provide examples**

### Code Quality

1. **Follow PEP 8** style guide
2. **Add type hints**

```python
async def process(self, file_path: Path, context: PluginContext, **kwargs) -> Dict[str, Any]:
```

1. **Write docstrings**
2. **Add unit tests** (>80% coverage)
3. **Use linters** (pylint, flake8, mypy)

---

## Examples

### Complete Examples

See `plugins/` directory for complete examples:

- `example_image_optimizer` - Image processing
- `example_text_analyzer` - Text analysis
- `example_cloud_storage` - Cloud integration
- `example_notification` - Event hooks

### Code Snippets

**Progress Tracking**:

```python
from tqdm import tqdm

async def batch_process(self, file_paths: List[Path], context: PluginContext, **kwargs):
    results = []
    for file_path in tqdm(file_paths, desc="Processing"):
        result = await self.process(file_path, context, **kwargs)
        results.append(result)
    return results
```

**Parallel Processing**:

```python
import asyncio

async def batch_process(self, file_paths: List[Path], context: PluginContext, **kwargs):
    tasks = [self.process(fp, context, **kwargs) for fp in file_paths]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

**Configuration Validation**:

```python
def configure(self, config: Dict[str, Any]) -> bool:
    # Validate configuration
    if 'quality' in config:
        if not 1 <= config['quality'] <= 100:
            return False
    
    self.context.config.update(config)
    return True
```

---

## Support & Resources

- **Documentation**: <https://docs.fileprocessor.com/plugins>
- **API Reference**: <https://api.fileprocessor.com/docs>
- **Examples**: <https://github.com/fileprocessor/plugin-examples>
- **Community**: <https://discord.gg/fileprocessor>
- **Issues**: <https://github.com/fileprocessor/issues>

---

**Version**: 7.0.0  
**Last Updated**: January 7, 2026  
**License**: MIT
