#!/usr/bin/env python3
"""
Advanced Similarity Analysis - Standalone Module
===============================================

GPU-accelerated file similarity matching with intelligent bucketing and n-gram analysis.
Supports both CPU and GPU backends for large-scale similarity computations.

This module can be run standalone or imported as part of the Enhanced File Processing Suite.

Usage:
    python advanced_similarity.py /path/to/files --threshold 0.8 --patterns "*.py" "*.txt"
    python advanced_similarity.py . --verbose --gpu
"""

from collections import defaultdict
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import re
import sys
import time

# Add core module to path for when running standalone
sys.path.insert(0, os.path.dirname(__file__))

# Import from unified utilities (single source of truth)
try:
    from unified_utilities import AdvancedSimilarityMatcher as UnifiedSimilarityMatcher

    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False
    UnifiedSimilarityMatcher = None

# Try to import hardware detector with fallback
try:
    from .hardware_detector import HardwareProfile, PerformanceProfile

    HARDWARE_AVAILABLE = True
except ImportError:
    # Fallback classes for standalone operation
    HARDWARE_AVAILABLE = False

    @dataclass
    class HardwareProfile:
        cpu_cores: int = 4
        ram_gb: int = 8
        has_gpu: bool = False
        gpu_memory_gb: int = 0

    @dataclass
    class PerformanceProfile:
        cpu_cores: int = 4
        ram_gb: int = 8
        gpu_enabled: bool = False
        chunk_size: int = 1000


logger = logging.getLogger(__name__)


@dataclass
class SimilarityGroup:
    """Represents a group of similar files."""

    files: list[Path]
    normalized_names: list[str]
    similarity_scores: dict[tuple[int, int], float]  # (i, j) -> similarity
    group_label: str

    @property
    def size(self) -> int:
        return len(self.files)


@dataclass
class SimilarityReport:
    """Report of similarity grouping results."""

    total_files: int
    groups: list[SimilarityGroup]
    singleton_files: list[Path]  # Files that didn't match anything
    processing_time: float
    gpu_accelerated: bool

    @property
    def grouped_files(self) -> int:
        return sum(group.size for group in self.groups)

    def print_summary(self) -> None:
        """Print formatted summary."""
        print("\n🔍 Similarity Analysis Report")
        print(f"{'=' * 50}")
        print(f"Total Files: {self.total_files:,}")
        print(f"Groups Found: {len(self.groups):,}")
        print(f"Grouped Files: {self.grouped_files:,}")
        print(f"Singleton Files: {len(self.singleton_files):,}")
        print(f"Processing Time: {self.processing_time:.2f}s")
        print(f"GPU Accelerated: {'Yes' if self.gpu_accelerated else 'No'}")

        if self.groups:
            print("\n📊 Largest Groups:")
            sorted_groups = sorted(self.groups, key=lambda g: g.size, reverse=True)
            for i, group in enumerate(sorted_groups[:5], 1):
                print(f"  {i}. '{group.group_label}' - {group.size} files")


class AdvancedFilenameProcessor:
    """Advanced filename normalization and preprocessing."""

    # Common noise patterns to remove
    NOISE_PATTERNS = [
        r"^(?:chapter|chap|c)\s*\d+_?",  # Chapter prefixes
        r"^(?:part|pt)\s*\d+_?",  # Part prefixes
        r"^(?:volume|vol)\s*\d+_?",  # Volume prefixes
        r"^\d{4}[-_]\d{2}[-_]\d{2}_?",  # Date prefixes
        r"^(?:new|old|revised)_",  # Version prefixes
    ]

    # Common unwanted prefixes (from the advanced script)
    NOISY_PREFIXES = [
        "0069_",
        "mafia_",
        "the_",
        "arhp_club_",
        "arhp_",
        "tmp_",
        "temp_",
        "copy_of_",
        "backup_",
        "old_",
    ]

    # Unwanted suffixes
    UNWANTED_SUFFIXES = [
        "_epub",
        "_pdf",
        "_cbr",
        "_cbz",
        "_zip",
        "_rar",
        "_backup",
        "_copy",
        "_old",
        "_new",
        "_final",
    ]

    @staticmethod
    def strip_prefixes(text: str) -> str:
        """Remove noise prefixes iteratively."""
        # First handle regex patterns
        for pattern in AdvancedFilenameProcessor.NOISE_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Then handle known prefixes
        changed = True
        while changed and text:
            changed = False
            text_lower = text.lower()
            for prefix in AdvancedFilenameProcessor.NOISY_PREFIXES:
                if text_lower.startswith(prefix):
                    text = text[len(prefix) :]
                    changed = True
                    break

        return text

    @staticmethod
    def strip_suffixes(text: str) -> str:
        """Remove unwanted suffixes."""
        text_lower = text.lower()
        for suffix in AdvancedFilenameProcessor.UNWANTED_SUFFIXES:
            if text_lower.endswith(suffix):
                text = text[: -len(suffix)]
                break
        return text

    @staticmethod
    def normalize_numbers(text: str, pad_width: int = 4) -> str:
        """Pad numbers with zeros for consistent sorting."""

        def pad_number(match):
            number = match.group(0)
            return number.zfill(pad_width) if len(number) < pad_width else number

        return re.sub(r"\d+", pad_number, text)

    @staticmethod
    def normalize_text(text: str, translate: bool = False, pad_width: int = 4) -> str:
        """Complete text normalization pipeline."""
        # Basic cleaning
        text = AdvancedFilenameProcessor.strip_prefixes(text)
        text = AdvancedFilenameProcessor.strip_suffixes(text)

        # Translation (if available and requested)
        if translate:
            try:
                from googletrans import Translator

                translator = Translator()
                if not text.isascii():
                    result = translator.translate(text, dest="en")
                    text = result.text if hasattr(result, "text") else text
            except Exception:
                logger.debug("Translation failed, continuing without translation", exc_info=True)

        # Normalize to lowercase and clean special characters
        text = text.lower()
        text = re.sub(r"[^\w\s-]", " ", text)  # Replace special chars with spaces
        text = re.sub(r"[\s\-_]+", "_", text)  # Normalize separators
        text = re.sub(r"^_+|_+$", "", text)  # Strip leading/trailing underscores

        # Pad numbers
        text = AdvancedFilenameProcessor.normalize_numbers(text, pad_width)

        # Fallback for empty names
        if not text or not any(c.isalpha() for c in text):
            text = f"file_{'0' * pad_width}"

        return text


class GPUSimilarityEngine:
    """GPU-accelerated similarity computation using n-gram vectors."""

    def __init__(self, backend: str = "auto"):
        self.backend = None
        self.device = None

        if backend in ("auto", "cupy"):
            try:
                import cupy as cp

                self.backend = "cupy"
                self.cp = cp
                logger.info("GPU similarity engine initialized with CuPy")
            except ImportError:
                if backend == "cupy":
                    raise ImportError("CuPy not available") from None

        if self.backend is None and backend in ("auto", "torch"):
            try:
                import torch

                if torch.cuda.is_available():
                    self.backend = "torch"
                    self.torch = torch
                    self.device = torch.device("cuda")
                    logger.info("GPU similarity engine initialized with PyTorch CUDA")
                elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    self.backend = "torch"
                    self.torch = torch
                    self.device = torch.device("mps")
                    logger.info("GPU similarity engine initialized with PyTorch MPS")
            except ImportError:
                if backend == "torch":
                    raise ImportError("PyTorch not available") from None

        if self.backend is None:
            logger.info("No GPU backend available, falling back to CPU")

    def extract_ngrams(self, text: str, n: int = 3) -> list[str]:
        """Extract n-grams from text."""
        # Pad text for better edge handling
        padded = f"^{text}$" if len(text) >= n else text
        return [padded[i : i + n] for i in range(max(1, len(padded) - n + 1))]

    def hash_ngram(self, ngram: str, dimension: int) -> int:
        """Hash an n-gram to a dimension index."""
        # FNV-1a hash
        hash_value = 2166136261
        for char in ngram:
            hash_value ^= ord(char)
            hash_value = (hash_value * 16777619) & 0xFFFFFFFF
        return hash_value % dimension

    def build_ngram_matrix_numpy(self, texts: list[str], dimension: int = 2048, n: int = 3):
        """Build n-gram matrix using NumPy (CPU fallback)."""
        try:
            import numpy as np
        except ImportError:
            # Pure Python fallback if numpy not available
            logger.warning("NumPy not available, using pure Python implementation")
            return self._build_ngram_matrix_python(texts, dimension, n)

        matrix = np.zeros((len(texts), dimension), dtype=np.float32)

        for i, text in enumerate(texts):
            ngrams = self.extract_ngrams(text, n)
            for ngram in ngrams:
                idx = self.hash_ngram(ngram, dimension)
                matrix[i, idx] += 1.0

        # Normalize rows
        norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8
        matrix = matrix / norms

        return matrix

    def _build_ngram_matrix_python(self, texts: list[str], dimension: int = 2048, n: int = 3):
        """Pure Python implementation as ultimate fallback."""
        matrix = []
        for text in texts:
            vector = [0.0] * dimension
            ngrams = self.extract_ngrams(text, n)
            for ngram in ngrams:
                idx = self.hash_ngram(ngram, dimension)
                vector[idx] += 1.0

            # Normalize vector
            norm = sum(x * x for x in vector) ** 0.5 + 1e-8
            vector = [x / norm for x in vector]
            matrix.append(vector)
        return matrix

    def compute_similarity_matrix_cupy(self, texts: list[str], dimension: int = 2048, n: int = 3):
        """Compute similarity matrix using CuPy."""
        # Build matrix on CPU first (could optimize this further)
        cpu_matrix = self.build_ngram_matrix_numpy(texts, dimension, n)

        # Transfer to GPU
        gpu_matrix = self.cp.asarray(cpu_matrix)

        # Compute cosine similarity matrix
        similarity_matrix = gpu_matrix @ gpu_matrix.T

        # Transfer back to CPU
        return similarity_matrix.get()

    def compute_similarity_matrix_torch(self, texts: list[str], dimension: int = 2048, n: int = 3):
        """Compute similarity matrix using PyTorch."""
        # Build matrix on CPU first
        cpu_matrix = self.build_ngram_matrix_numpy(texts, dimension, n)

        # Transfer to GPU
        gpu_matrix = self.torch.from_numpy(cpu_matrix).to(self.device)

        # Compute cosine similarity matrix
        similarity_matrix = gpu_matrix @ gpu_matrix.T

        # Transfer back to CPU
        return similarity_matrix.cpu().numpy()

    def compute_similarity_matrix(self, texts: list[str], dimension: int = 2048, n: int = 3):
        """Compute similarity matrix using available backend."""
        if self.backend == "cupy":
            return self.compute_similarity_matrix_cupy(texts, dimension, n)
        elif self.backend == "torch":
            return self.compute_similarity_matrix_torch(texts, dimension, n)
        else:
            # CPU fallback with direct similarity computation
            try:
                import numpy as np  # noqa: F401

                matrix = self.build_ngram_matrix_numpy(texts, dimension, n)
                return matrix @ matrix.T
            except ImportError:
                # Pure Python fallback
                matrix = self._build_ngram_matrix_python(texts, dimension, n)
                # Compute similarity matrix in pure Python
                similarity_matrix = []
                for i in range(len(matrix)):
                    row = []
                    for j in range(len(matrix)):
                        # Cosine similarity
                        dot_product = sum(a * b for a, b in zip(matrix[i], matrix[j], strict=False))
                        row.append(dot_product)
                    similarity_matrix.append(row)
                return similarity_matrix

    def find_similar_pairs(
        self, texts: list[str], threshold: float = 0.7, dimension: int = 2048, n: int = 3
    ) -> list[tuple[int, int, float]]:
        """Find pairs of texts above similarity threshold."""
        similarity_matrix = self.compute_similarity_matrix(texts, dimension, n)

        pairs = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                # Handle both numpy arrays and pure Python lists
                if hasattr(similarity_matrix, "shape"):  # numpy array
                    similarity = similarity_matrix[i, j]
                else:  # Python list
                    similarity = similarity_matrix[i][j]
                if similarity >= threshold:
                    pairs.append((i, j, similarity))

        return pairs


# ==================================================================
# NOTE: AdvancedSimilarityMatcher is now consolidated in unified_utilities.py
# This version is kept for GPU-specific extensions and standalone operation
# For new code, import from: from core.unified_utilities import AdvancedSimilarityMatcher
# ==================================================================


class AdvancedSimilarityMatcher:
    """
    Advanced similarity matching with bucketing and GPU acceleration.

    DEPRECATION NOTE:
    This class is maintained here for GPU-specific features and standalone operation.
    For general similarity matching, use: from core.unified_utilities import AdvancedSimilarityMatcher
    """

    def __init__(
        self,
        hardware_profile: HardwareProfile | None = None,
        performance_profile: PerformanceProfile | None = None,
    ):

        # Try to import hardware detector with fallback
        if HARDWARE_AVAILABLE:
            try:
                from .hardware_detector import HardwareDetector, PerformanceOptimizer

                self.hw = hardware_profile or HardwareDetector.detect_hardware()
                self.perf = performance_profile or PerformanceOptimizer.optimize_for_hardware(
                    self.hw
                )
            except ImportError:
                # Fallback to default profiles
                self.hw = hardware_profile or HardwareProfile()
                self.perf = performance_profile or PerformanceProfile()
        else:
            # Use fallback profiles for standalone operation
            self.hw = hardware_profile or HardwareProfile()
            self.perf = performance_profile or PerformanceProfile()

        # Initialize GPU engine if available
        self.gpu_engine = None
        if self.perf.gpu_enabled and self.hw.gpu_backend:
            try:
                self.gpu_engine = GPUSimilarityEngine(self.hw.gpu_backend)
            except Exception as e:
                logger.warning(f"Failed to initialize GPU engine: {e}")

        self.processor = AdvancedFilenameProcessor()

    def create_bucket_key(self, normalized_name: str, depth: int = 2) -> str:
        """Create bucket key for initial grouping."""
        parts = normalized_name.split("_")
        return (
            "_".join(parts[:depth])
            if len(parts) >= depth
            else parts[0]
            if parts
            else normalized_name
        )

    def group_into_buckets(
        self, files: list[Path], normalized_names: list[str]
    ) -> dict[str, list[tuple[int, Path, str]]]:
        """Group files into buckets for efficient processing."""
        buckets = defaultdict(list)

        for idx, (file_path, norm_name) in enumerate(zip(files, normalized_names, strict=False)):
            bucket_key = self.create_bucket_key(norm_name)
            buckets[bucket_key].append((idx, file_path, norm_name))

        return buckets

    def find_similarity_groups_cpu(
        self, files: list[Path], names: list[str], threshold: float = 0.85
    ) -> list[list[int]]:
        """CPU-based similarity grouping using Union-Find."""
        try:
            from rapidfuzz import fuzz

            def similarity_func(a, b):
                return fuzz.token_set_ratio(a, b) / 100.0
        except ImportError:
            import difflib

            def similarity_func(a, b):
                return difflib.SequenceMatcher(None, a, b).ratio()

        n = len(files)
        parent = list(range(n))
        rank = [0] * n

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return
            if rank[px] < rank[py]:
                parent[px] = py
            elif rank[px] > rank[py]:
                parent[py] = px
            else:
                parent[py] = px
                rank[px] += 1

        # Compare all pairs
        for i in range(n):
            for j in range(i + 1, n):
                similarity = similarity_func(names[i], names[j])
                if similarity >= threshold:
                    union(i, j)

        # Group by root parent
        groups = defaultdict(list)
        for i in range(n):
            groups[find(i)].append(i)

        return [group for group in groups.values() if len(group) > 1]

    def find_similarity_groups_gpu(
        self, files: list[Path], names: list[str], threshold: float = 0.85
    ) -> list[list[int]]:
        """GPU-accelerated similarity grouping."""
        if not self.gpu_engine:
            return self.find_similarity_groups_cpu(files, names, threshold)

        try:
            # Get similar pairs from GPU
            pairs = self.gpu_engine.find_similar_pairs(names, threshold)

            # Build groups using Union-Find
            n = len(files)
            parent = list(range(n))

            def find(x):
                if parent[x] != x:
                    parent[x] = find(parent[x])
                return parent[x]

            def union(x, y):
                px, py = find(x), find(y)
                if px != py:
                    parent[py] = px

            # Process GPU pairs
            for i, j, _ in pairs:
                union(i, j)

            # Group by root parent
            groups = defaultdict(list)
            for i in range(n):
                groups[find(i)].append(i)

            return [group for group in groups.values() if len(group) > 1]

        except Exception as e:
            logger.warning(f"GPU grouping failed, falling back to CPU: {e}")
            return self.find_similarity_groups_cpu(files, names, threshold)

    def generate_group_label(self, names: list[str]) -> str:
        """Generate a meaningful label for a group of similar files."""
        if not names:
            return "Ungrouped"

        # Find common words across all names
        word_sets = [set(name.split("_")) for name in names if name]
        if not word_sets:
            return "Ungrouped"

        common_words = set.intersection(*word_sets)

        if common_words:
            # Use the order from the first name to preserve sequence
            first_words = names[0].split("_")
            ordered_common = [word for word in first_words if word in common_words]
            label = "_".join(ordered_common)
        else:
            # Fallback: use first significant word from first name
            first_words = names[0].split("_")
            label = first_words[0] if first_words else "Ungrouped"

        # Clean up the label
        label = self.processor.strip_suffixes(label)

        # Ensure the label has alphabetic content
        if not any(c.isalpha() for c in label):
            return "Ungrouped"

        return label.strip("_") or "Ungrouped"

    def group_files_by_similarity(
        self,
        files: list[Path],
        threshold: float = 0.85,
        translate: bool = False,
        pad_width: int = 4,
        min_group_size: int = 2,
    ) -> SimilarityReport:
        """
        Group files by similarity with hardware-optimized processing.

        Args:
            files: List of files to group
            threshold: Similarity threshold (0.0 to 1.0)
            translate: Whether to translate non-ASCII names
            pad_width: Width for number padding
            min_group_size: Minimum size for a group

        Returns:
            SimilarityReport with grouped results
        """
        start_time = time.time()

        logger.info(f"Starting similarity analysis of {len(files)} files...")

        # Normalize all filenames
        normalized_names = [
            self.processor.normalize_text(f.stem, translate, pad_width) for f in files
        ]

        # Group into buckets for efficient processing
        buckets = self.group_into_buckets(files, normalized_names)

        logger.info(f"Created {len(buckets)} buckets for processing")

        all_groups = []
        singleton_files = []
        gpu_used = False

        for bucket_key, bucket_items in buckets.items():
            if len(bucket_items) < min_group_size:
                # Add to singletons
                singleton_files.extend([item[1] for item in bucket_items])
                continue

            bucket_files = [item[1] for item in bucket_items]
            bucket_names = [item[2] for item in bucket_items]
            [item[0] for item in bucket_items]

            # Determine processing method based on bucket size
            use_gpu = self.perf.gpu_enabled and self.perf.gpu_batch_size >= len(bucket_items) >= 50

            if use_gpu:
                groups = self.find_similarity_groups_gpu(bucket_files, bucket_names, threshold)
                gpu_used = True
                logger.debug(f"GPU processed bucket '{bucket_key}' with {len(bucket_items)} items")
            else:
                groups = self.find_similarity_groups_cpu(bucket_files, bucket_names, threshold)
                logger.debug(f"CPU processed bucket '{bucket_key}' with {len(bucket_items)} items")

            # Convert local indices to global and create similarity groups
            for group_indices in groups:
                if len(group_indices) >= min_group_size:
                    group_files = [bucket_files[i] for i in group_indices]
                    group_names = [bucket_names[i] for i in group_indices]
                    group_label = self.generate_group_label(group_names)

                    # Calculate similarity scores (simplified)
                    similarity_scores = {}
                    for i in range(len(group_indices)):
                        for j in range(i + 1, len(group_indices)):
                            similarity_scores[(i, j)] = threshold  # Simplified

                    similarity_group = SimilarityGroup(
                        files=group_files,
                        normalized_names=group_names,
                        similarity_scores=similarity_scores,
                        group_label=group_label,
                    )
                    all_groups.append(similarity_group)
                else:
                    # Add small groups to singletons
                    singleton_files.extend([bucket_files[i] for i in group_indices])

        processing_time = time.time() - start_time

        report = SimilarityReport(
            total_files=len(files),
            groups=all_groups,
            singleton_files=singleton_files,
            processing_time=processing_time,
            gpu_accelerated=gpu_used,
        )

        logger.info(
            f"Similarity analysis complete: {len(all_groups)} groups found "
            f"in {processing_time:.2f}s (GPU: {gpu_used})"
        )

        return report


# Example usage and testing
if __name__ == "__main__":
    import argparse

    def main():
        parser = argparse.ArgumentParser(
            description="Advanced file similarity matching - Standalone Module",
            epilog="""
Examples:
  python advanced_similarity.py /path/to/files --threshold 0.8
  python advanced_similarity.py . --patterns "*.py" "*.txt" --verbose
  python advanced_similarity.py /media --gpu --translate
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("directory", type=Path, help="Directory to analyze")
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.85,
            help="Similarity threshold (0.0-1.0, default: 0.85)",
        )
        parser.add_argument(
            "--patterns",
            nargs="+",
            default=["*"],
            help="File patterns to match (default: all files)",
        )
        parser.add_argument(
            "--translate", action="store_true", help="Translate non-ASCII filenames to English"
        )
        parser.add_argument(
            "--gpu", action="store_true", help="Force GPU acceleration (requires CUDA)"
        )
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
        parser.add_argument("--version", action="version", version="Advanced Similarity v5.0")

        args = parser.parse_args()

        # Validate directory
        if not args.directory.exists():
            print(f"Error: Directory '{args.directory}' does not exist")
            return 1

        if not args.directory.is_dir():
            print(f"Error: '{args.directory}' is not a directory")
            return 1

        # Validate threshold
        if not 0.0 <= args.threshold <= 1.0:
            print(f"Error: Threshold must be between 0.0 and 1.0, got {args.threshold}")
            return 1

        # Setup logging
        level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(levelname)s: %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )

        logger.info("Advanced Similarity Analysis v5.0")
        logger.info(f"Analyzing directory: {args.directory}")
        logger.info(f"Hardware detection: {'Available' if HARDWARE_AVAILABLE else 'Fallback mode'}")

        # Collect files
        files = []
        try:
            for pattern in args.patterns:
                pattern_files = list(args.directory.rglob(pattern))
                files.extend([f for f in pattern_files if f.is_file()])
        except Exception as e:
            logger.error(f"Error collecting files: {e}")
            return 1

        if not files:
            print(f"No files found matching patterns {args.patterns} in {args.directory}")
            return 1

        logger.info(f"Found {len(files)} files to analyze")

        # Initialize matcher
        try:
            matcher = AdvancedSimilarityMatcher()

            # Force GPU if requested
            if args.gpu:
                if hasattr(matcher, "perf") and matcher.perf:
                    matcher.perf.gpu_enabled = True
                    logger.info("GPU acceleration requested")
                else:
                    logger.warning("GPU acceleration requested but not available")

        except Exception as e:
            logger.error(f"Error initializing similarity matcher: {e}")
            return 1

        # Analyze similarity
        try:
            start_time = time.time()
            report = matcher.group_files_by_similarity(files, args.threshold, args.translate)
            elapsed = time.time() - start_time

            # Print results
            print("\n" + "=" * 50)
            print("🎯 SIMILARITY ANALYSIS COMPLETE")
            print("=" * 50)
            report.print_summary()

            if args.verbose:
                print("\n📊 Performance Details:")
                print(f"   Processing time: {elapsed:.3f}s")
                print(f"   Files per second: {len(files) / elapsed:.1f}")
                print(f"   GPU acceleration: {'Yes' if report.gpu_accelerated else 'No'}")
                print(f"   Hardware detection: {'Available' if HARDWARE_AVAILABLE else 'Fallback'}")

            return 0

        except KeyboardInterrupt:
            print("\n⚠️  Analysis interrupted by user")
            return 1
        except Exception as e:
            logger.error(f"Error during similarity analysis: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            return 1

    sys.exit(main())
