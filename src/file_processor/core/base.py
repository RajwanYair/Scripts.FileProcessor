#!/usr/bin/env python3
"""
base.py — Core configuration and base-class definitions.

Defines `ProcessingConfig` (validated config dataclass) and `BaseProcessor`
(abstract base for all concrete processor implementations).
"""

from __future__ import annotations

import argparse
import logging
import multiprocessing as mp
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProcessingConfig:
    """Configuration for file processing operations."""

    source_dir: Path
    destination_dir: Path | None = None
    recursive: bool = True
    overwrite: bool = False
    workers: int = mp.cpu_count()
    use_gpu: bool = False
    quality: int = 85
    verbose: bool = False
    dry_run: bool = False
    file_extensions: list[str] | None = None
    max_file_size: int | None = None  # in MB

    def __post_init__(self):
        """Validate and normalize configuration."""
        self.source_dir = Path(self.source_dir).resolve()
        if self.destination_dir:
            self.destination_dir = Path(self.destination_dir).resolve()
        else:
            self.destination_dir = self.source_dir

        # Ensure workers is reasonable
        self.workers = max(1, min(self.workers, mp.cpu_count() * 2))


class BaseProcessor:
    """Base class for all file processors."""

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.processed_count = 0
        self.error_count = 0
        self.skipped_count = 0

    def _setup_logging(self) -> logging.Logger:
        """Return a module-level logger; caller configures handlers."""
        level = logging.DEBUG if self.config.verbose else logging.INFO
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(level)
        return logger

    def get_files(self, extensions: list[str] | None = None) -> list[Path]:
        """Get all files matching the criteria."""
        files = []
        extensions = extensions or self.config.file_extensions or ["*"]

        def should_include_file(file_path: Path) -> bool:
            # Check extension
            if extensions != ["*"]:
                ext_match = any(file_path.suffix.lower() == ext.lower() for ext in extensions)
                if not ext_match:
                    return False

            # Check file size if specified
            if self.config.max_file_size:
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > self.config.max_file_size:
                        return False
                except OSError:
                    return False

            return True

        if self.config.recursive:
            for pattern in extensions:
                pattern = f"**/*{pattern}" if pattern != "*" else "**/*"
                files.extend(
                    [
                        f
                        for f in self.config.source_dir.rglob(pattern)
                        if f.is_file() and should_include_file(f)
                    ]
                )
        else:
            for pattern in extensions:
                pattern = f"*{pattern}" if pattern != "*" else "*"
                files.extend(
                    [
                        f
                        for f in self.config.source_dir.glob(pattern)
                        if f.is_file() and should_include_file(f)
                    ]
                )

        return sorted(set(files))

    def process_file(self, file_path: Path) -> dict[str, Any]:
        """Process a single file. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement process_file")

    def process_files(self, files: list[Path]) -> dict[str, Any]:
        """Process multiple files with progress tracking."""
        from tqdm import tqdm

        results = {"processed": 0, "errors": 0, "skipped": 0, "details": []}

        if self.config.dry_run:
            self.logger.info("DRY RUN MODE - No files will be modified")
            for file_path in tqdm(files, desc="Analyzing files"):
                result = self.simulate_process(file_path)
                results["details"].append(result)
            return results

        if self.config.workers == 1:
            # Single-threaded processing
            for file_path in tqdm(files, desc="Processing files"):
                try:
                    result = self.process_file(file_path)
                    if result.get("success", False):
                        results["processed"] += 1
                    else:
                        results["errors"] += 1
                    results["details"].append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    results["errors"] += 1
                    results["details"].append(
                        {"file": str(file_path), "success": False, "error": str(e)}
                    )
        else:
            # Multi-threaded processing
            with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
                futures = {executor.submit(self.process_file, f): f for f in files}

                for future in tqdm(futures, desc="Processing files"):
                    try:
                        result = future.result()
                        if result.get("success", False):
                            results["processed"] += 1
                        else:
                            results["errors"] += 1
                        results["details"].append(result)
                    except Exception as e:
                        file_path = futures[future]
                        self.logger.error(f"Error processing {file_path}: {e}")
                        results["errors"] += 1
                        results["details"].append(
                            {"file": str(file_path), "success": False, "error": str(e)}
                        )

        return results

    def simulate_process(self, file_path: Path) -> dict[str, Any]:
        """Simulate processing for dry run mode."""
        return {
            "file": str(file_path),
            "success": True,
            "action": "would_process",
            "size": file_path.stat().st_size,
            "message": f"Would process {file_path.name}",
        }


def setup_common_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Setup common CLI arguments for all utilities."""
    parser.add_argument(
        "-s", "--sourcedir", type=str, required=True, help="Source directory to process files from"
    )
    parser.add_argument(
        "-d", "--destinationdir", type=str, help="Destination directory (default: same as source)"
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="Process files recursively")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=mp.cpu_count(),
        help=f"Number of worker threads (default: {mp.cpu_count()})",
    )
    parser.add_argument("--use-gpu", action="store_true", help="Use GPU acceleration if available")
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=85,
        help="Quality setting for compression (1-100, default: 85)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--extensions", type=str, help="Comma-separated list of file extensions to process"
    )
    parser.add_argument("--max-size", type=int, help="Maximum file size in MB to process")
    return parser


def create_config_from_args(args: argparse.Namespace) -> ProcessingConfig:
    """Create ProcessingConfig from parsed arguments."""
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(",")]
        extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    return ProcessingConfig(
        source_dir=args.sourcedir,
        destination_dir=args.destinationdir,
        recursive=args.recursive,
        overwrite=args.overwrite,
        workers=args.workers,
        use_gpu=args.use_gpu,
        quality=args.quality,
        verbose=args.verbose,
        dry_run=args.dry_run,
        file_extensions=extensions,
        max_file_size=args.max_size,
    )


def install_dependencies():
    """Install required dependencies."""
    import subprocess

    dependencies = [
        "Pillow>=10.0.0",
        "tqdm>=4.65.0",
        "rarfile>=4.0",
        "py7zr>=0.20.0",
        "reportlab>=4.0.0",
        "googletrans==4.0.0rc1",
        "PyPDF2>=3.0.0",
        "python-magic>=0.4.27",
        "pillow-heif>=0.13.0",
        "PyTurboJPEG>=1.7.0",
    ]

    optional_dependencies = [
        "cupy-cuda12x",  # GPU support
        "cucim",  # GPU image processing
        "opencv-python",  # Advanced image processing
        "numpy>=1.24.0",
    ]

    print("Installing core dependencies...")
    for dep in dependencies:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            print(f"Warning: Could not install {dep}")

    print("Installing optional dependencies...")
    for dep in optional_dependencies:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            print(f"Optional dependency {dep} not installed (this is OK)")


if __name__ == "__main__":
    print("File Processing Utilities Suite")
    print("===============================")
    print("Installing dependencies...")
    install_dependencies()
    print("Dependencies installation completed.")
    print("\nAvailable utilities:")
    print("- comic_to_pdf_converter.py: Convert comic archives to PDF")
    print("- file_organizer.py: Organize and rename files")
    print("- metadata_extractor.py: Extract file metadata")
    print("- file_sanitizer.py: Sanitize filenames")
    print("- archive_format_processor.py: Process archive files")
    print("- file_processing_suite_gui.py: Launch modern GUI interface")
