# Architecture Overview

## System Design

`file-processor` is a layered CLI/API application with four primary layers:

```
┌──────────────────────────────────────────────────┐
│                  CLI (Click)                     │
│  process · deduplicate · convert · scan · serve  │
│  plugins list/install/remove/update              │
└─────────────────────┬────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────┐
│                REST API (FastAPI)                 │
│  GET /health · POST /process · POST /upload       │
└─────────────────────┬────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────┐
│               Core Processing Engine             │
│  FileProcessor · BaseProcessor · PluginSystem    │
│  file_utils · results · config_loader            │
└─────────────────────┬────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────┐
│             File System / Plugins                 │
│  ThreadPoolExecutor · asyncio event loop          │
│  PluginMarketplace · manifest.json schema         │
└──────────────────────────────────────────────────┘
```

## Source Layout

```
src/file_processor/
├── __init__.py          # Package metadata + public API
├── __main__.py          # python -m file_processor support
├── cli/
│   ├── __init__.py
│   └── main.py          # Click CLI — all commands defined here
├── core/
│   ├── __init__.py
│   ├── base.py          # ProcessingConfig (dataclass) + BaseProcessor (ABC)
│   ├── processor.py     # FileProcessor — parallel execution engine
│   ├── results.py       # OperationStatus, ProcessingResult, BatchResult
│   ├── file_utils.py    # sanitize_filename, normalize_extension, translate_filename
│   ├── plugin_system.py # PluginManager, PluginMarketplace, plugin loading
│   └── ...              # other domain modules
├── api/
│   ├── __init__.py
│   ├── server.py        # FastAPI app factory
│   └── routes.py        # Router with /health, /process, /upload
├── plugins/
│   └── manager.py       # Plugin discovery, install, remove, update
└── utils/
    ├── __init__.py      # Re-exports load_config, load_yaml
    └── config_loader.py # YAML loader with ${VAR:default} substitution
```

## Key Design Decisions

### Single Entry Point
All functionality is exposed through `file_processor.cli.main:main` registered as the `file-processor` console script. No secondary entry points.

### Configuration Hierarchy
Priority (highest → lowest):
1. CLI flags (`--dry-run`, `--verbose`, `--workers`)
2. Environment variables (`${VAR_NAME:default}` in YAML)
3. User config file (`-c path/to/config.yaml`)
4. Bundled `config/default_config.yaml`

### Parallel Execution
`FileProcessor.run()` uses `concurrent.futures.ThreadPoolExecutor` for I/O-bound file operations. Worker count defaults to `min(32, os.cpu_count() + 4)` via Python's default. `run_async()` wraps the same logic in `loop.run_in_executor()` for async callers.

### Plugin Architecture
Plugins are directory-based packages with a mandatory `manifest.json` and a `plugin.py` containing a class that implements the plugin interface. The `PluginMarketplace` handles discovery, install, remove, and update lifecycle.

### Result Types
All operations return `ProcessingResult` (single file) or `BatchResult` (collection). Both are plain dataclasses — no exceptions propagate past `FileProcessor._safe_process()`.

## Data Flow: `file-processor process`

```
CLI args
  └─► ProcessingConfig (validated dataclass)
        └─► FileProcessor.run()
              ├─► BaseProcessor.get_files()   → list[Path]
              └─► ThreadPoolExecutor
                    └─► operation(path, cfg)  → ProcessingResult
                          └─► BatchResult.add()
                                └─► BatchResult.finish()
                                      └─► console summary
```

## Sequence Diagram: REST API `/process`

```
Client          FastAPI Router     FileProcessor     Filesystem
  │                  │                  │                │
  │ POST /process    │                  │                │
  │─────────────────►│                  │                │
  │                  │ ProcessingConfig │                │
  │                  │─────────────────►│                │
  │                  │                  │ get_files()    │
  │                  │                  │───────────────►│
  │                  │                  │◄───────────────│
  │                  │                  │ run()          │
  │                  │                  │────────────────┤
  │                  │   BatchResult    │                │
  │                  │◄─────────────────│                │
  │  ProcessResponse │                  │                │
  │◄─────────────────│                  │                │
```

## Testing Strategy

| Layer        | Tool                   | Location                     |
|-------------|------------------------|------------------------------|
| Unit         | pytest + pytest-mock   | `tests/unit/`                |
| Integration  | pytest + CliRunner      | `tests/integration/`         |
| Property     | hypothesis              | `tests/unit/test_file_utils.py` |
| Coverage     | pytest-cov              | Reported to `coverage.xml`  |
| Security     | bandit + CodeQL         | CI/CD pipelines              |

Target: **≥ 70 % line coverage** (enforced by `--cov-fail-under=70` in `pyproject.toml`).
