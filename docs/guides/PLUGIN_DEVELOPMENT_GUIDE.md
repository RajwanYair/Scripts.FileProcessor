# Plugin Development Guide

## Overview

`file-processor` plugins extend the pipeline with custom file operations. Each plugin
is a self-contained directory with a `manifest.json` and a `plugin.py`.

## Plugin Structure

```
my-plugin/
├── manifest.json    # Required: metadata and capabilities declaration
├── plugin.py        # Required: plugin implementation
├── __init__.py      # Recommended: makes it a Python package
├── requirements.txt # Optional: extra Python dependencies
└── README.md        # Recommended: docs
```

## manifest.json Schema

```json
{
  "id": "com.example.my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "One-line description of what this plugin does.",
  "author": "Your Name <you@example.com>",
  "category": "transformation",
  "tags": ["images", "compression"],
  "entry_point": "plugin.MyPlugin",
  "file_extensions": [".jpg", ".png"],
  "min_app_version": "7.0.0",
  "install_method": "pip",
  "install_command": "pip install my-plugin-package"
}
```

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Reverse-domain unique identifier (e.g. `com.example.name`) |
| `name` | string | Human-readable display name |
| `version` | string | Semantic version (`MAJOR.MINOR.PATCH`) |
| `entry_point` | string | `module.ClassName` inside `plugin.py` |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | One of: `transformation`, `filter`, `metadata`, `export`, `other` |
| `file_extensions` | array | Extensions this plugin handles (e.g. `[".jpg", ".png"]`) |
| `install_method` | string | `pip`, `git`, or `builtin` |

## plugin.py Interface

Your plugin class must implement the `process` method:

```python
# my-plugin/plugin.py
from __future__ import annotations

from pathlib import Path

from file_processor.core.base import ProcessingConfig
from file_processor.core.results import OperationStatus, ProcessingResult


class MyPlugin:
    """Compress images in the pipeline."""

    name = "My Plugin"
    version = "1.0.0"

    def process(self, path: Path, config: ProcessingConfig) -> ProcessingResult:
        """
        Process a single file.

        Parameters
        ----------
        path:   Absolute path to the source file.
        config: Shared ProcessingConfig for this run.

        Returns
        -------
        ProcessingResult with status SUCCESS, SKIPPED, or FAILED.
        """
        if config.dry_run:
            return ProcessingResult(
                source=path,
                status=OperationStatus.DRY_RUN,
                message="dry-run: no changes made",
            )

        try:
            # --- your logic here ---
            # Example: copy the file to the destination unchanged
            dest = (config.destination_dir or config.source_dir) / path.name
            dest.write_bytes(path.read_bytes())
            return ProcessingResult(
                source=path,
                status=OperationStatus.SUCCESS,
                destination=dest,
                bytes_in=path.stat().st_size,
                bytes_out=dest.stat().st_size,
            )
        except Exception as exc:
            return ProcessingResult(
                source=path,
                status=OperationStatus.FAILED,
                message=str(exc),
            )
```

## Installing Your Plugin

### Via the marketplace (preferred)

```bash
file-processor plugins install com.example.my-plugin
```

### Manually (development)
Place your plugin directory inside `~/.local/share/file-processor/plugins/` or the
path configured in `config/default_config.yaml` under `plugins.directory`.

## Example Plugins

See [`examples/plugins/`](../../examples/plugins/) for three complete reference implementations:

| Plugin | Category | Demonstrates |
|--------|----------|--------------|
| `example_image_optimizer` | transformation | Image compression with Pillow |
| `example_pdf_processor` | transformation | PDF manipulation |
| `example_text_analyzer` | metadata | Text statistics extraction |

## Testing Your Plugin

```python
# tests/test_my_plugin.py
from pathlib import Path
from file_processor.core.base import ProcessingConfig
from file_processor.core.results import OperationStatus
from my_plugin.plugin import MyPlugin


def test_plugin_dry_run(tmp_path: Path) -> None:
    cfg = ProcessingConfig(source_dir=tmp_path, dry_run=True)
    sample = tmp_path / "file.jpg"
    sample.write_bytes(b"fake image data")
    result = MyPlugin().process(sample, cfg)
    assert result.status == OperationStatus.DRY_RUN


def test_plugin_processes_file(tmp_path: Path) -> None:
    cfg = ProcessingConfig(source_dir=tmp_path)
    sample = tmp_path / "file.jpg"
    sample.write_bytes(b"fake image data")
    result = MyPlugin().process(sample, cfg)
    assert result.status == OperationStatus.SUCCESS
```

## Publishing

1. Push to a public Git repo or publish to PyPI.
2. Submit a PR to the [plugin marketplace catalog](https://github.com/<org>/file-processor/blob/main/catalog/plugins.json) with your plugin metadata.
