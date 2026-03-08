#!/usr/bin/env python3
"""
enhanced_deduplicator.py

Advanced file deduplication system with size-first filtering and parallel MD5 computation.
Supports various deduplication strategies and provides detailed reporting.
"""

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import hashlib
import logging
import os
from pathlib import Path
import shutil

# Add core module to path
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from .hardware_detector import HardwareProfile, PerformanceProfile

logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate files."""

    hash_value: str
    files: list[Path]
    total_size: int
    wasted_space: int  # Size of duplicates (excluding one original)

    @property
    def original(self) -> Path:
        """Return the file to keep (first one by default)."""
        return self.files[0] if self.files else None

    @property
    def duplicates(self) -> list[Path]:
        """Return files to remove/move."""
        return self.files[1:] if len(self.files) > 1 else []


@dataclass
class DeduplicationReport:
    """Comprehensive deduplication report."""

    total_files_scanned: int
    duplicate_groups: list[DuplicateGroup]
    total_wasted_space: int
    potential_savings: int
    scan_duration: float

    @property
    def total_duplicates(self) -> int:
        """Total number of duplicate files found."""
        return sum(len(group.duplicates) for group in self.duplicate_groups)

    def print_summary(self) -> None:
        """Print a formatted summary of the deduplication results."""
        print("\n📊 Deduplication Report")
        print(f"{'=' * 50}")
        print(f"Files Scanned: {self.total_files_scanned:,}")
        print(f"Duplicate Groups: {len(self.duplicate_groups):,}")
        print(f"Total Duplicates: {self.total_duplicates:,}")
        print(f"Wasted Space: {self._format_size(self.total_wasted_space)}")
        print(f"Potential Savings: {self._format_size(self.potential_savings)}")
        print(f"Scan Duration: {self.scan_duration:.2f}s")

        if self.duplicate_groups:
            print("\n🔍 Top 5 Largest Duplicate Groups:")
            sorted_groups = sorted(
                self.duplicate_groups, key=lambda g: g.wasted_space, reverse=True
            )
            for i, group in enumerate(sorted_groups[:5], 1):
                print(
                    f"  {i}. {len(group.files)} files, "
                    f"{self._format_size(group.wasted_space)} wasted"
                )
                print(f"     Hash: {group.hash_value[:16]}...")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class EnhancedDeduplicator:
    """Advanced file deduplication with hardware-aware optimizations."""

    def __init__(
        self,
        hardware_profile: HardwareProfile | None = None,
        performance_profile: PerformanceProfile | None = None,
    ):
        from .hardware_detector import HardwareDetector, PerformanceOptimizer

        self.hw = hardware_profile or HardwareDetector.detect_hardware()
        self.perf = performance_profile or PerformanceOptimizer.optimize_for_hardware(self.hw)

        logger.info(f"Deduplicator initialized: {self.perf}")

    def compute_file_hash(self, file_path: Path, chunk_size: int | None = None) -> str | None:
        """Compute MD5 hash of a file with optimized chunk size."""
        if chunk_size is None:
            chunk_size = self.perf.hash_chunk_size

        try:
            hash_md5 = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash {file_path}: {e}")
            return None

    def group_files_by_size(self, files: list[Path]) -> dict[int, list[Path]]:
        """Group files by size for efficient duplicate detection."""
        size_groups = defaultdict(list)

        for file_path in files:
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
            except Exception as e:
                logger.warning(f"Failed to get size for {file_path}: {e}")

        # Only return groups with multiple files
        return {size: files for size, files in size_groups.items() if len(files) > 1}

    def compute_hashes_parallel(self, files: list[Path]) -> dict[str, list[Path]]:
        """Compute file hashes in parallel using ProcessPool."""
        hash_groups = defaultdict(list)

        if not files:
            return hash_groups

        max_workers = min(self.perf.max_workers, len(files))
        chunk_size = self.perf.hash_chunk_size

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all hash computation tasks
            future_to_file = {
                executor.submit(self._compute_hash_worker, str(file_path), chunk_size): file_path
                for file_path in files
            }

            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_hash = future.result()
                    if file_hash:
                        hash_groups[file_hash].append(file_path)
                except Exception as e:
                    logger.warning(f"Hash computation failed for {file_path}: {e}")

        # Only return groups with multiple files (duplicates)
        return {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}

    @staticmethod
    def _compute_hash_worker(file_path_str: str, chunk_size: int) -> str | None:
        """Worker function for parallel hash computation."""
        try:
            file_path = Path(file_path_str)
            hash_md5 = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None

    def find_duplicates(
        self, files: list[Path], progress_callback: callable | None = None
    ) -> DeduplicationReport:
        """
        Find duplicate files using size-first filtering and parallel hashing.

        Args:
            files: List of files to scan for duplicates
            progress_callback: Optional callback for progress updates

        Returns:
            DeduplicationReport with detailed results
        """
        start_time = time.time()

        logger.info(f"Starting deduplication scan of {len(files)} files...")

        if progress_callback:
            progress_callback("Grouping files by size...")

        # Phase 1: Group by size (fast)
        size_groups = self.group_files_by_size(files)
        potential_duplicates = []
        for size_files in size_groups.values():
            potential_duplicates.extend(size_files)

        logger.info(
            f"Found {len(potential_duplicates)} potential duplicates "
            f"in {len(size_groups)} size groups"
        )

        if progress_callback:
            progress_callback(f"Computing hashes for {len(potential_duplicates)} files...")

        # Phase 2: Compute hashes for potential duplicates (expensive)
        hash_groups = self.compute_hashes_parallel(potential_duplicates)

        # Phase 3: Build duplicate groups
        duplicate_groups = []
        total_wasted_space = 0

        for hash_value, file_list in hash_groups.items():
            if len(file_list) > 1:
                # Calculate sizes
                file_size = file_list[0].stat().st_size
                total_size = file_size * len(file_list)
                wasted_space = file_size * (len(file_list) - 1)

                duplicate_group = DuplicateGroup(
                    hash_value=hash_value,
                    files=file_list,
                    total_size=total_size,
                    wasted_space=wasted_space,
                )
                duplicate_groups.append(duplicate_group)
                total_wasted_space += wasted_space

        scan_duration = time.time() - start_time

        report = DeduplicationReport(
            total_files_scanned=len(files),
            duplicate_groups=duplicate_groups,
            total_wasted_space=total_wasted_space,
            potential_savings=total_wasted_space,
            scan_duration=scan_duration,
        )

        logger.info(
            f"Deduplication complete: found {len(duplicate_groups)} "
            f"duplicate groups in {scan_duration:.2f}s"
        )

        return report

    def remove_duplicates(
        self, report: DeduplicationReport, backup_dir: Path | None = None, dry_run: bool = False
    ) -> int:
        """
        Remove duplicate files, optionally backing them up.

        Args:
            report: Deduplication report from find_duplicates()
            backup_dir: Optional directory to move duplicates to instead of deleting
            dry_run: If True, only show what would be done

        Returns:
            Number of files processed
        """
        processed = 0

        for group in report.duplicate_groups:
            for duplicate_file in group.duplicates:
                if dry_run:
                    action = "move to backup" if backup_dir else "delete"
                    logger.info(f"[DRY RUN] Would {action}: {duplicate_file}")
                else:
                    try:
                        if backup_dir:
                            # Move to backup directory
                            backup_dir.mkdir(parents=True, exist_ok=True)
                            backup_path = backup_dir / duplicate_file.name

                            # Handle name conflicts
                            counter = 1
                            while backup_path.exists():
                                stem = duplicate_file.stem
                                suffix = duplicate_file.suffix
                                backup_path = backup_dir / f"{stem}_{counter}{suffix}"
                                counter += 1

                            shutil.move(str(duplicate_file), str(backup_path))
                            logger.debug(
                                f"Moved duplicate to backup: {duplicate_file} -> {backup_path}"
                            )
                        else:
                            # Delete the duplicate
                            duplicate_file.unlink()
                            logger.debug(f"Deleted duplicate: {duplicate_file}")

                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process {duplicate_file}: {e}")

        action = "Would process" if dry_run else "Processed"
        logger.info(f"{action} {processed} duplicate files")
        return processed

    def find_duplicates_in_directory(
        self,
        directory: Path,
        file_patterns: list[str] | None = None,
        recursive: bool = True,
        progress_callback: callable | None = None,
    ) -> DeduplicationReport:
        """
        Find duplicates in a directory with optional file pattern filtering.

        Args:
            directory: Directory to scan
            file_patterns: Optional list of glob patterns to match files
            recursive: Whether to scan subdirectories
            progress_callback: Optional progress callback

        Returns:
            DeduplicationReport with results
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if progress_callback:
            progress_callback("Scanning directory for files...")

        # Collect files
        files = []
        if recursive:
            if file_patterns:
                for pattern in file_patterns:
                    files.extend(directory.rglob(pattern))
            else:
                files.extend(f for f in directory.rglob("*") if f.is_file())
        else:
            if file_patterns:
                for pattern in file_patterns:
                    files.extend(directory.glob(pattern))
            else:
                files.extend(f for f in directory.iterdir() if f.is_file())

        logger.info(f"Found {len(files)} files to scan in {directory}")

        return self.find_duplicates(files, progress_callback)


# Command-line interface for testing
if __name__ == "__main__":
    import argparse

    def main():
        parser = argparse.ArgumentParser(description="Advanced file deduplication tool")
        parser.add_argument("directory", type=Path, help="Directory to scan")
        parser.add_argument("--patterns", nargs="+", help="File patterns to match")
        parser.add_argument(
            "--recursive", action="store_true", default=True, help="Scan subdirectories"
        )
        parser.add_argument(
            "--backup-dir", type=Path, help="Move duplicates to this directory instead of deleting"
        )
        parser.add_argument("--remove", action="store_true", help="Actually remove/move duplicates")
        parser.add_argument(
            "--dry-run", action="store_true", help="Show what would be done without making changes"
        )
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

        args = parser.parse_args()

        # Setup logging
        level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

        # Initialize deduplicator
        deduplicator = EnhancedDeduplicator()

        # Find duplicates
        try:
            report = deduplicator.find_duplicates_in_directory(
                args.directory, args.patterns, args.recursive
            )

            # Print report
            report.print_summary()

            # Process duplicates if requested
            if args.remove or args.dry_run:
                deduplicator.remove_duplicates(report, args.backup_dir, dry_run=args.dry_run)

        except Exception as e:
            logger.error(f"Error: {e}")
            return 1

        return 0

    exit(main())
