#!/usr/bin/env python3
"""
Enhanced Unified Utilities v4.0
===============================

Unified utility functions to eliminate code duplication across the suite.
This module provides the single source of truth for all common operations.

Features:
- Modern async/await support
- Comprehensive type hints
- Advanced caching mechanisms
- Cross-platform compatibility
- Resource management with context managers
- Performance optimizations
"""

import asyncio
from asyncio import Semaphore
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from functools import lru_cache, wraps
import hashlib
import logging
import os
from pathlib import Path
import platform
import re
import time
from typing import (
    Any,
    Protocol,
)
import unicodedata

import aiofiles

# Optional imports
try:
    from googletrans import Translator

    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

try:
    import cv2
    import numpy as np

    COMPUTER_VISION_AVAILABLE = True
except ImportError:
    COMPUTER_VISION_AVAILABLE = False

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_WSL = False

if not IS_WINDOWS:

    # Enhanced WSL detection
    wsl_indicators = [
        lambda: (
            Path("/proc/version").exists()
            and "microsoft" in Path("/proc/version").read_text().lower()
        ),
        lambda: os.environ.get("WSL_DISTRO_NAME") is not None,
        lambda: Path("/mnt/c").exists(),
        lambda: "Windows" in os.environ.get("PATH", ""),
    ]
    IS_WSL = any(indicator() for indicator in wsl_indicators if callable(indicator))
else:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================================
# TYPE DEFINITIONS
# ================================


@dataclass(frozen=True)
class ProcessingResult:
    """Immutable result of a file processing operation."""

    file_path: Path
    operation: str
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    error_message: str | None = None
    original_size: int = 0
    final_size: int = 0


@dataclass
class FileInfo:
    """Comprehensive file information."""

    path: Path
    size: int
    created_time: float
    modified_time: float
    extension: str
    mime_type: str | None = None
    hash_md5: str | None = None
    hash_sha256: str | None = None


class SimilarityMethod(Protocol):
    """Protocol for similarity calculation methods."""

    def calculate(self, file1: Path, file2: Path) -> float: ...


# ================================
# ADVANCED CACHING DECORATORS
# ================================


def timed_lru_cache(seconds: int, maxsize: int = 128):
    """LRU cache with TTL (Time To Live) support."""

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds
        func.expiration = time.time() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.time() >= func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def async_lru_cache(maxsize: int = 128):
    """Async version of LRU cache."""

    def decorator(func):
        cache = {}
        cache_order = []

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))

            if key in cache:
                # Move to end (most recently used)
                cache_order.remove(key)
                cache_order.append(key)
                return cache[key]

            # Execute async function
            result = await func(*args, **kwargs)

            # Add to cache
            cache[key] = result
            cache_order.append(key)

            # Remove oldest if over limit
            if len(cache) > maxsize:
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]

            return result

        return wrapper

    return decorator


# ================================
# CONTEXT MANAGERS
# ================================


@contextmanager
def managed_file_operation(
    file_path: Path, backup: bool = True, atomic: bool = True
) -> Generator[Path, None, None]:
    """
    Context manager for safe file operations with backup and atomic writes.

    Args:
        file_path: File to operate on
        backup: Create backup before operation
        atomic: Use atomic write operations
    """
    backup_path = None
    temp_path = None

    try:
        # Create backup if requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            backup_path.write_bytes(file_path.read_bytes())

        # Use temporary file for atomic operations
        if atomic:
            temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
            yield temp_path
            # Atomic move on successful completion
            if temp_path.exists():
                temp_path.replace(file_path)
        else:
            yield file_path

    except Exception as e:
        # Restore from backup on error
        if backup_path and backup_path.exists():
            backup_path.replace(file_path)
        # Clean up temp file
        if temp_path and temp_path.exists():
            temp_path.unlink()
        logger.error(f"File operation failed for {file_path}: {e}")
        raise

    finally:
        # Clean up backup file
        if backup_path and backup_path.exists():
            backup_path.unlink()


@asynccontextmanager
async def async_file_manager(file_path: Path, mode: str = "rb") -> AsyncGenerator:
    """Async context manager for file operations."""
    try:
        async with aiofiles.open(file_path, mode) as f:
            yield f
    except Exception as e:
        logger.error(f"Async file operation failed for {file_path}: {e}")
        raise


# ================================
# UNIFIED FILENAME PROCESSING
# ================================


class UnifiedFilenameProcessor:
    """
    Unified filename processing with advanced normalization.
    Eliminates duplication across sanitize_filename, normalize_extension, translate_filename.
    """

    def __init__(self):
        self.translator = None
        if TRANSLATION_AVAILABLE:
            try:
                self.translator = Translator()
            except Exception:
                logger.warning("Failed to initialize translator")

    @timed_lru_cache(seconds=3600, maxsize=1000)
    def sanitize_filename(
        self, filename: str, max_length: int = 255, preserve_case: bool = True
    ) -> str:
        """
        Advanced filename sanitization with Unicode normalization.

        Args:
            filename: Original filename
            max_length: Maximum filename length
            preserve_case: Whether to preserve original casing

        Returns:
            Sanitized filename safe for all platforms
        """
        if not filename:
            return "unnamed_file"

        # Unicode normalization (NFC - Canonical Decomposition followed by Canonical Composition)
        filename = unicodedata.normalize("NFC", filename)

        # Platform-specific character restrictions
        if IS_WINDOWS:
            # Windows reserved characters
            invalid_chars = r'[<>:"/\\|?*]'
            # Windows reserved names
            reserved_names = {
                "CON",
                "PRN",
                "AUX",
                "NUL",
                "COM1",
                "COM2",
                "COM3",
                "COM4",
                "COM5",
                "COM6",
                "COM7",
                "COM8",
                "COM9",
                "LPT1",
                "LPT2",
                "LPT3",
                "LPT4",
                "LPT5",
                "LPT6",
                "LPT7",
                "LPT8",
                "LPT9",
            }
        else:
            # Unix-like systems (Linux, macOS)
            invalid_chars = r"[/\0]"
            reserved_names = set()

        # Remove invalid characters
        filename = re.sub(invalid_chars, "_", filename)

        # Remove control characters (0-31, 127)
        filename = "".join(char for char in filename if ord(char) > 31 and ord(char) != 127)

        # Handle reserved names
        name_part = filename.split(".")[0].upper()
        if name_part in reserved_names:
            filename = f"file_{filename}"

        # Trim whitespace and dots (Windows doesn't allow trailing dots/spaces)
        filename = filename.strip(" .")

        # Ensure reasonable length
        if len(filename) > max_length:
            # Smart truncation preserving extension
            name, ext = os.path.splitext(filename)
            available_length = max_length - len(ext)
            if available_length > 0:
                filename = name[:available_length] + ext
            else:
                filename = filename[:max_length]

        # Ensure not empty
        if not filename:
            filename = "unnamed_file"

        # Case preservation option
        if not preserve_case:
            filename = filename.lower()

        return filename

    @timed_lru_cache(seconds=1800, maxsize=500)
    def translate_filename(
        self, filename: str, target_language: str = "en", fallback_transliteration: bool = True
    ) -> str:
        """
        Advanced filename translation with fallback mechanisms.

        Args:
            filename: Original filename
            target_language: Target language code (e.g., 'en', 'es', 'fr')
            fallback_transliteration: Use transliteration if translation fails

        Returns:
            Translated filename
        """
        if not filename or not TRANSLATION_AVAILABLE or not self.translator:
            return filename

        try:
            # Separate name and extension
            name, ext = os.path.splitext(filename)

            # Skip if already in target language (heuristic)
            if self._is_likely_target_language(name, target_language):
                return filename

            # Translate the name part
            translated = self.translator.translate(name, dest=target_language)
            translated_name = translated.text if translated else name

            # Fallback to transliteration if translation failed
            if (not translated_name or translated_name == name) and fallback_transliteration:
                translated_name = self._transliterate_unicode(name)

            # Combine with extension
            result = self.sanitize_filename(translated_name + ext)
            logger.info(f"Translated filename: {filename} -> {result}")
            return result

        except Exception as e:
            logger.warning(f"Translation failed for {filename}: {e}")
            # Fallback to transliteration
            if fallback_transliteration:
                return self.sanitize_filename(self._transliterate_unicode(filename))
            return filename

    def _is_likely_target_language(self, text: str, target_lang: str) -> bool:
        """Heuristic to check if text is likely already in target language."""
        if target_lang == "en":
            # Simple check for ASCII characters (rough English heuristic)
            return all(ord(char) < 128 for char in text if char.isalpha())
        return False

    def _transliterate_unicode(self, text: str) -> str:
        """Transliterate Unicode text to ASCII."""
        try:
            # Use Unicode NFKD normalization and ASCII encoding
            normalized = unicodedata.normalize("NFKD", text)
            ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
            return ascii_text if ascii_text else text
        except Exception:
            return text

    @timed_lru_cache(seconds=3600, maxsize=1000)
    def normalize_extension(
        self, extension: str, preferred_extensions: dict[str, str] | None = None
    ) -> str:
        """
        Advanced extension normalization with format mapping.

        Args:
            extension: Original extension
            preferred_extensions: Dictionary mapping extensions to preferred formats

        Returns:
            Normalized extension
        """
        if not extension:
            return ""

        # Remove leading dot and convert to lowercase
        ext = extension.lower().lstrip(".")

        # Default preferred extensions for common formats
        default_preferred = {
            # Images
            "jpeg": "jpg",
            "tiff": "tif",
            # Archives
            "gz": "tar.gz",
            "bz2": "tar.bz2",
            "xz": "tar.xz",
            # Documents
            "htm": "html",
            "doc": "docx",
            "xls": "xlsx",
            "ppt": "pptx",
        }

        preferred = preferred_extensions or default_preferred

        # Apply preferred extension mapping
        normalized_ext = preferred.get(ext, ext)

        return normalized_ext


# ================================
# ADVANCED SIMILARITY ALGORITHMS
# ================================


class AdvancedSimilarityMatcher:
    """
    Advanced multi-method similarity matching for intelligent file grouping.
    Replaces simple difflib approach with sophisticated algorithms.
    """

    def __init__(self):
        self.filename_processor = UnifiedFilenameProcessor()

    def calculate_overall_similarity(
        self, file1: Path, file2: Path, weights: dict[str, float] | None = None
    ) -> float:
        """
        Calculate overall similarity using multiple algorithms.

        Args:
            file1, file2: Files to compare
            weights: Weight distribution for different similarity methods

        Returns:
            Similarity score (0.0 to 1.0)
        """
        default_weights = {"filename": 0.4, "content": 0.3, "metadata": 0.2, "size": 0.1}
        weights = weights or default_weights

        similarities = {}

        # Filename similarity
        similarities["filename"] = self._filename_similarity(file1, file2)

        # Content similarity (for images)
        if self._is_image(file1) and self._is_image(file2):
            similarities["content"] = self._image_content_similarity(file1, file2)
        else:
            similarities["content"] = 0.0

        # Metadata similarity
        similarities["metadata"] = self._metadata_similarity(file1, file2)

        # File size similarity
        similarities["size"] = self._file_size_similarity(file1, file2)

        # Calculate weighted average
        total_similarity = sum(
            similarities[method] * weights.get(method, 0) for method in similarities
        )

        return min(1.0, max(0.0, total_similarity))

    def _filename_similarity(self, file1: Path, file2: Path) -> float:
        """Enhanced filename similarity using multiple algorithms."""
        from difflib import SequenceMatcher

        # Extract base names without dates and extensions
        name1 = re.sub(r"^\d{8}_", "", file1.stem)
        name2 = re.sub(r"^\d{8}_", "", file2.stem)

        # Sequence matcher similarity
        seq_sim = SequenceMatcher(None, name1, name2).ratio()

        # Levenshtein distance similarity
        lev_sim = self._levenshtein_similarity(name1, name2)

        # Token-based similarity (for series with numbers)
        token_sim = self._token_similarity(name1, name2)

        # Return the maximum similarity
        return max(seq_sim, lev_sim, token_sim)

    def _levenshtein_similarity(self, str1: str, str2: str) -> float:
        """Calculate Levenshtein distance similarity."""
        if not str1 and not str2:
            return 1.0
        if not str1 or not str2:
            return 0.0

        # Dynamic programming approach
        len1, len2 = len(str1), len(str2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if str1[i - 1] == str2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # deletion
                    matrix[i][j - 1] + 1,  # insertion
                    matrix[i - 1][j - 1] + cost,  # substitution
                )

        max_len = max(len1, len2)
        distance = matrix[len1][len2]
        return 1.0 - (distance / max_len)

    def _token_similarity(self, str1: str, str2: str) -> float:
        """Token-based similarity for series detection."""
        # Extract words and numbers
        tokens1 = set(re.findall(r"\w+", str1.lower()))
        tokens2 = set(re.findall(r"\w+", str2.lower()))

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))

        return intersection / union if union > 0 else 0.0

    def _image_content_similarity(self, file1: Path, file2: Path) -> float:
        """Calculate image content similarity using computer vision."""
        if not COMPUTER_VISION_AVAILABLE or not PIL_AVAILABLE:
            return 0.0

        try:
            # Load images using PIL first (more format support)
            img1 = Image.open(file1)
            img2 = Image.open(file2)

            # Convert to RGB if necessary
            if img1.mode != "RGB":
                img1 = img1.convert("RGB")
            if img2.mode != "RGB":
                img2 = img2.convert("RGB")

            # Resize to standard size for comparison
            size = (64, 64)
            img1 = img1.resize(size)
            img2 = img2.resize(size)

            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)

            # Calculate histogram correlation
            hist1 = cv2.calcHist([arr1], [0, 1, 2], None, [32, 32, 32], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([arr2], [0, 1, 2], None, [32, 32, 32], [0, 256, 0, 256, 0, 256])

            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return max(0.0, correlation)

        except Exception as e:
            logger.debug(f"Image similarity calculation failed: {e}")
            return 0.0

    def _metadata_similarity(self, file1: Path, file2: Path) -> float:
        """Calculate metadata-based similarity."""
        try:
            stat1 = file1.stat()
            stat2 = file2.stat()

            # Compare creation times (if within 24 hours, higher similarity)
            time_diff = abs(stat1.st_ctime - stat2.st_ctime)
            time_sim = max(0.0, 1.0 - (time_diff / 86400))  # 24 hours in seconds

            return time_sim

        except Exception:
            return 0.0

    def _file_size_similarity(self, file1: Path, file2: Path) -> float:
        """Calculate file size similarity."""
        try:
            size1 = file1.stat().st_size
            size2 = file2.stat().st_size

            if size1 == 0 and size2 == 0:
                return 1.0
            if size1 == 0 or size2 == 0:
                return 0.0

            # Calculate similarity based on size ratio
            ratio = min(size1, size2) / max(size1, size2)
            return ratio

        except Exception:
            return 0.0

    def _is_image(self, file_path: Path) -> bool:
        """Check if file is an image."""
        image_extensions = {
            "jpg",
            "jpeg",
            "png",
            "gif",
            "bmp",
            "tiff",
            "tif",
            "webp",
            "heic",
            "heif",
            "cr2",
            "nef",
            "arw",
            "dng",
            "orf",
            "rw2",
        }
        return file_path.suffix.lower().lstrip(".") in image_extensions


# ================================
# ASYNC FILE OPERATIONS
# ================================


class AsyncFileProcessor:
    """High-performance async file processing."""

    def __init__(self, max_concurrent: int = 50):
        self.semaphore = Semaphore(max_concurrent)
        self.filename_processor = UnifiedFilenameProcessor()
        self.similarity_matcher = AdvancedSimilarityMatcher()

    async def process_files_batch(
        self, files: list[Path], operations: list[str] | None = None
    ) -> list[ProcessingResult]:
        """
        Process multiple files asynchronously with controlled concurrency.

        Args:
            files: List of files to process
            operations: List of operations to perform

        Returns:
            List of processing results
        """
        operations = operations or ["sanitize", "normalize_extension"]

        tasks = [self._process_single_file(file_path, operations) for file_path in files]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return valid results
        return [result for result in results if isinstance(result, ProcessingResult)]

    async def _process_single_file(
        self, file_path: Path, operations: list[str]
    ) -> ProcessingResult:
        """Process a single file with specified operations."""
        async with self.semaphore:
            start_time = time.time()

            try:
                original_size = file_path.stat().st_size
                processed_path = file_path
                metadata = {}

                for operation in operations:
                    if operation == "sanitize":
                        new_name = self.filename_processor.sanitize_filename(file_path.name)
                        if new_name != file_path.name:
                            new_path = file_path.parent / new_name
                            processed_path.rename(new_path)
                            processed_path = new_path
                            metadata["sanitized"] = True

                    elif operation == "normalize_extension":
                        normalized_ext = self.filename_processor.normalize_extension(
                            file_path.suffix
                        )
                        if normalized_ext != file_path.suffix.lstrip("."):
                            new_path = processed_path.with_suffix(f".{normalized_ext}")
                            processed_path.rename(new_path)
                            processed_path = new_path
                            metadata["extension_normalized"] = True

                    elif operation == "translate":
                        translated_name = self.filename_processor.translate_filename(
                            processed_path.name
                        )
                        if translated_name != processed_path.name:
                            new_path = processed_path.parent / translated_name
                            processed_path.rename(new_path)
                            processed_path = new_path
                            metadata["translated"] = True

                final_size = processed_path.stat().st_size
                processing_time = time.time() - start_time

                return ProcessingResult(
                    file_path=processed_path,
                    operation=",".join(operations),
                    success=True,
                    metadata=metadata,
                    processing_time=processing_time,
                    original_size=original_size,
                    final_size=final_size,
                )

            except Exception as e:
                return ProcessingResult(
                    file_path=file_path,
                    operation=",".join(operations),
                    success=False,
                    error_message=str(e),
                    processing_time=time.time() - start_time,
                )


# ================================
# CROSS-PLATFORM UTILITIES
# ================================


class CrossPlatformUtils:
    """Cross-platform utility functions."""

    @staticmethod
    def get_optimal_worker_count() -> int:
        """Get optimal number of workers based on system capabilities."""
        cpu_count = os.cpu_count() or 4

        if IS_WINDOWS:
            # Windows: Use environment variable if available
            try:
                return int(os.environ.get("NUMBER_OF_PROCESSORS", cpu_count))
            except (ValueError, TypeError):
                return cpu_count
        else:
            # Unix-like systems: Consider load average
            try:
                load_avg = os.getloadavg()[0]
                # Reduce workers if system is under load
                if load_avg > cpu_count:
                    return max(1, cpu_count // 2)
                return cpu_count
            except (AttributeError, OSError):
                return cpu_count

    @staticmethod
    def safe_file_move(src: Path, dst: Path, overwrite: bool = False) -> bool:
        """Cross-platform safe file move with atomic operations."""
        try:
            # Ensure destination directory exists
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Handle existing destination
            if dst.exists() and not overwrite:
                # Generate unique name
                counter = 1
                base_name = dst.stem
                extension = dst.suffix
                while dst.exists():
                    dst = dst.parent / f"{base_name}_{counter}{extension}"
                    counter += 1

            # Perform atomic move
            if IS_WINDOWS:
                # Windows: Use replace for atomic operation
                src.replace(dst)
            else:
                # Unix: Use rename for atomic operation
                src.rename(dst)

            return True

        except Exception as e:
            logger.error(f"Failed to move {src} to {dst}: {e}")
            return False

    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm: str = "md5", chunk_size: int = 8192) -> str:
        """Calculate file hash efficiently."""
        hash_algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }

        if algorithm not in hash_algorithms:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        hasher = hash_algorithms[algorithm]()

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()


# ================================
# INITIALIZATION
# ================================

# Global instances for easy access
filename_processor = UnifiedFilenameProcessor()
similarity_matcher = AdvancedSimilarityMatcher()
async_processor = AsyncFileProcessor()
cross_platform = CrossPlatformUtils()

# Export main functions for backward compatibility
sanitize_filename = filename_processor.sanitize_filename
normalize_extension = filename_processor.normalize_extension
translate_filename = filename_processor.translate_filename

__all__ = [
    "IS_WINDOWS",
    "IS_WSL",
    "AdvancedSimilarityMatcher",
    "AsyncFileProcessor",
    "CrossPlatformUtils",
    "FileInfo",
    "ProcessingResult",
    "SimilarityMethod",
    "UnifiedFilenameProcessor",
    "async_file_manager",
    "async_lru_cache",
    "async_processor",
    "cross_platform",
    "filename_processor",
    "managed_file_operation",
    "normalize_extension",
    "sanitize_filename",
    "similarity_matcher",
    "timed_lru_cache",
    "translate_filename",
]
