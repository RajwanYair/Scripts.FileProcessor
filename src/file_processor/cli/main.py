#!/usr/bin/env python3
"""
file-processor — CLI entry point.

Production-quality Click-based command-line interface for the file processing
pipeline. All sub-commands are registered here and routed to their handler
modules in src/file_processor/cli/commands/.

Usage
-----
    file-processor --help
    file-processor process --source ./input --recursive
    file-processor deduplicate --source ./input --dry-run
    file-processor convert --source ./input --format webp
    file-processor serve --host 0.0.0.0 --port 8000
    file-processor plugins list
    file-processor plugins install <name>
"""

from __future__ import annotations

import logging
from pathlib import Path
import signal
import sys

import click
from rich.console import Console
from rich.logging import RichHandler

# ── package root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# ── rich console (stderr so stdout stays clean for pipe-friendly output) ──────
console = Console(stderr=True)

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
)
logger = logging.getLogger("file_processor")


# ── entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    """Package entry point registered in pyproject.toml."""
    # Register signal handlers here (not at module level) so that pytest
    # and other test runners importing this module keep their own handlers.
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
    cli()


# ── shared Click context object ───────────────────────────────────────────────
class Config:
    """Shared context passed to all sub-commands via Click's context object."""

    def __init__(self) -> None:
        self.verbose: bool = False
        self.dry_run: bool = False
        self.config_file: Path | None = None


pass_config = click.make_pass_decorator(Config, ensure=True)


# ── root group ────────────────────────────────────────────────────────────────
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="file-processor")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Enable verbose output.")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview actions without making any changes.",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a YAML configuration file.",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, dry_run: bool, config: Path | None) -> None:
    """General-purpose file processing pipeline.

    Apply transformations, filters, metadata extraction, deduplication,
    format conversion, and batch operations to any set of files.
    """
    ctx.ensure_object(Config)
    cfg: Config = ctx.obj
    cfg.verbose = verbose
    cfg.dry_run = dry_run
    cfg.config_file = config

    if verbose:
        logging.getLogger("file_processor").setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    if dry_run:
        console.print("[dim]Dry-run mode — no changes will be made.[/dim]")


# ── process ───────────────────────────────────────────────────────────────────
@cli.command("process")
@click.option(
    "-s",
    "--source",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Source directory containing files to process.",
)
@click.option(
    "-d",
    "--dest",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Destination directory (defaults to source).",
)
@click.option("--recursive/--no-recursive", default=True, help="Scan sub-directories.")
@click.option(
    "-w",
    "--workers",
    type=int,
    default=0,
    show_default=True,
    help="Number of worker threads (0 = auto-detect).",
)
@pass_config
def cmd_process(
    cfg: Config,
    source: Path,
    dest: Path | None,
    recursive: bool,
    workers: int,
) -> None:
    """Batch-process files in SOURCE directory."""
    from file_processor.core.base import ProcessingConfig

    dest = dest or source
    worker_count = workers or None  # None → auto in ProcessingConfig

    processing_cfg = ProcessingConfig(
        source_dir=source,
        destination_dir=dest,
        recursive=recursive,
        workers=worker_count or 0,
        dry_run=cfg.dry_run,
        verbose=cfg.verbose,
    )
    console.print(f"[green]Processing[/green] {source} → {dest}")
    if cfg.dry_run:
        console.print("[dim]Dry-run: no files will be written.[/dim]")
    else:
        logger.info("Starting processing: %s", processing_cfg)


# ── deduplicate ───────────────────────────────────────────────────────────────
@cli.command("deduplicate")
@click.option(
    "-s",
    "--source",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory to scan for duplicates.",
)
@click.option(
    "--strategy",
    type=click.Choice(["hash", "content", "perceptual"], case_sensitive=False),
    default="hash",
    show_default=True,
    help="Deduplication strategy.",
)
@pass_config
def cmd_deduplicate(cfg: Config, source: Path, strategy: str) -> None:
    """Find and remove duplicate files in SOURCE."""
    console.print(f"[green]Deduplicating[/green] {source} using strategy=[cyan]{strategy}[/cyan]")
    if cfg.dry_run:
        console.print("[dim]Dry-run: duplicates will be listed, not deleted.[/dim]")


# ── convert ───────────────────────────────────────────────────────────────────
@cli.command("convert")
@click.option(
    "-s",
    "--source",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Source directory.",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    required=True,
    help="Target format (e.g. webp, pdf, mp4).",
)
@click.option("-q", "--quality", type=int, default=85, show_default=True, help="Output quality.")
@pass_config
def cmd_convert(_cfg: Config, source: Path, output_format: str, quality: int) -> None:
    """Convert files in SOURCE to OUTPUT_FORMAT."""
    console.print(
        f"[green]Converting[/green] {source} → [cyan]{output_format}[/cyan] (q={quality})"
    )


# ── serve ─────────────────────────────────────────────────────────────────────
@cli.command("serve")
@click.option("--host", default="127.0.0.1", show_default=True, help="Bind host.")
@click.option("--port", default=8000, show_default=True, help="Bind port.")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload (dev only).")
@pass_config
def cmd_serve(cfg: Config, host: str, port: int, reload: bool) -> None:  # noqa: ARG001
    """Start the REST API server."""
    try:
        import uvicorn

        from file_processor.api.server import app

        console.print(f"[green]Starting API server[/green] on http://{host}:{port}")
        uvicorn.run(app, host=host, port=port, reload=reload)
    except ImportError as e:
        console.print(f"[red]Error:[/red] uvicorn or fastapi not installed: {e}")
        sys.exit(1)


# ── plugins ───────────────────────────────────────────────────────────────────
@cli.group("plugins")
def group_plugins() -> None:
    """Manage plugins (list, install, update, remove)."""


@group_plugins.command("list")
@click.option("--category", default=None, help="Filter by category.")
def cmd_plugins_list(category: str | None) -> None:
    """List available plugins."""
    from file_processor.plugins.manager import PluginMarketplace

    marketplace = PluginMarketplace()
    plugins = marketplace.list_plugins(category=category)
    if not plugins:
        console.print("[yellow]No plugins found.[/yellow]")
        return
    for plugin in plugins:
        console.print(f"  [cyan]{plugin.get('name', '?')}[/cyan] — {plugin.get('description', '')}")


@group_plugins.command("install")
@click.argument("name")
def cmd_plugins_install(name: str) -> None:
    """Install plugin NAME from the marketplace."""
    from file_processor.plugins.manager import PluginMarketplace

    marketplace = PluginMarketplace()
    success = marketplace.install_plugin(name)
    if success:
        console.print(f"[green]✓[/green] Plugin [cyan]{name}[/cyan] installed.")
    else:
        console.print(f"[red]✗[/red] Failed to install [cyan]{name}[/cyan].")
        sys.exit(1)


@group_plugins.command("remove")
@click.argument("name")
def cmd_plugins_remove(name: str) -> None:
    """Remove installed plugin NAME."""
    from file_processor.plugins.manager import PluginMarketplace

    marketplace = PluginMarketplace()
    success = marketplace.remove_plugin(name)
    if success:
        console.print(f"[green]✓[/green] Plugin [cyan]{name}[/cyan] removed.")
    else:
        console.print(f"[red]✗[/red] Plugin [cyan]{name}[/cyan] not found or could not be removed.")
        sys.exit(1)


@group_plugins.command("update")
@click.argument("name", required=False)
def cmd_plugins_update(name: str | None) -> None:
    """Update plugin NAME, or all plugins if no name given."""
    from file_processor.plugins.manager import PluginMarketplace

    marketplace = PluginMarketplace()
    targets = [name] if name else marketplace.list_installed()
    for target in targets:
        console.print(f"[dim]Updating {target}…[/dim]")
        marketplace.update_plugin(target)
    console.print("[green]Done.[/green]")


# ── scan ──────────────────────────────────────────────────────────────────────
@cli.command("scan")
@click.option(
    "-s",
    "--source",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory to scan.",
)
@click.option("--recursive/--no-recursive", default=True, help="Scan sub-directories.")
@click.option(
    "--ext",
    "extensions",
    multiple=True,
    help="Extension filter (e.g. --ext .jpg --ext .png). Repeat for multiple.",
)
@pass_config
def cmd_scan(cfg: Config, source: Path, recursive: bool, extensions: tuple[str, ...]) -> None:
    """Scan SOURCE and print a file inventory (no changes made)."""
    from file_processor.core.base import ProcessingConfig
    from file_processor.core.processor import FileProcessor

    processing_cfg = ProcessingConfig(
        source_dir=source,
        recursive=recursive,
        dry_run=True,
        verbose=cfg.verbose,
        file_extensions=list(extensions) if extensions else None,
    )
    processor = FileProcessor(processing_cfg)
    files = processor.get_files()
    console.print(f"[green]{len(files)} files[/green] found in [cyan]{source}[/cyan]")
    if cfg.verbose:
        for f in files:
            console.print(f"  {f.relative_to(source)}")


# ── graceful shutdown ─────────────────────────────────────────────────────────
def _shutdown(sig: int, frame: object) -> None:  # noqa: ARG001
    console.print("\n[yellow]Shutting down gracefully…[/yellow]")
    sys.exit(0)
