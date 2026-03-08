"""
Advanced Metadata Extractor Module
==================================
Multi-method metadata extraction with cross-platform external tool integration.
Enhanced fallback chain and password-protected file support.

This module provides comprehensive metadata extraction using multiple libraries
and external tools, with graceful fallbacks and cross-platform compatibility.
"""

from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

# Optional imports with graceful fallback
try:
    from PIL import ExifTags, Image

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from googletrans import Translator

    TRANSLATOR = Translator()
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

try:
    from ebooklib import epub

    EBOOKLIB_AVAILABLE = True
except ImportError:
    EBOOKLIB_AVAILABLE = False

try:
    from hachoir.metadata import extractMetadata
    from hachoir.parser import createParser

    HACHOIR_AVAILABLE = True
except ImportError:
    HACHOIR_AVAILABLE = False

# Cross-platform file locking
if os.name != "nt":
    import fcntl
else:
    import msvcrt


@dataclass
class MetadataResult:
    """Container for metadata extraction results."""

    creation_date: str | None = None
    modification_date: str | None = None
    camera_make: str | None = None
    camera_model: str | None = None
    gps_coordinates: tuple | None = None
    file_size: int | None = None
    duration: float | None = None
    dimensions: tuple | None = None
    format_info: str | None = None
    extraction_method: str | None = None
    metadata_dict: dict[str, Any] | None = None


class AdvancedMetadataExtractor:
    """
    Advanced metadata extractor with multiple fallback methods and external tool integration.

    Features:
    - Multi-method extraction chain with fallbacks
    - External tool integration (exiftool, mediainfo, ffmpeg)
    - Password-protected file handling
    - Cross-platform compatibility
    - Comprehensive format support
    """

    def __init__(self, log_file: Path | None = None):
        """Initialize the advanced metadata extractor."""
        self.log_file = log_file or Path("metadata_extraction.log")
        self.external_tools = self._detect_external_tools()
        self.supported_formats = self._get_supported_formats()

    def _detect_external_tools(self) -> dict[str, bool]:
        """Detect available external tools."""
        tools = {}
        for tool in ["exiftool", "mediainfo", "ffmpeg", "qpdf", "7z"]:
            tools[tool] = self._command_exists(tool)
        return tools

    def _command_exists(self, cmd: str) -> bool:
        """Check if an external command exists in the system PATH."""
        import shutil

        return shutil.which(cmd) is not None

    def _get_supported_formats(self) -> dict[str, list[str]]:
        """Get supported file formats organized by category."""
        return {
            "images": [
                "jpg",
                "jpeg",
                "png",
                "tiff",
                "tif",
                "bmp",
                "gif",
                "heic",
                "heif",
                "cr2",
                "nef",
                "arw",
                "dng",
                "orf",
                "rw2",
                "raf",
                "svg",
                "webp",
            ],
            "videos": [
                "mp4",
                "avi",
                "mkv",
                "mov",
                "wmv",
                "flv",
                "webm",
                "m4v",
                "3gp",
                "mts",
                "m2ts",
                "asf",
                "mxf",
                "mod",
            ],
            "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma", "alac", "amr"],
            "documents": ["pdf", "docx", "xlsx", "pptx", "odt", "ods", "odp", "rtf"],
            "ebooks": ["epub", "mobi", "azw", "azw3", "fb2", "lit"],
            "archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "cbz", "cbr"],
        }

    def _safe_log(self, message: str) -> None:
        """Thread-safe logging with cross-platform file locking."""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{timestamp} {message}\n"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                if os.name != "nt":
                    # Linux/macOS: use fcntl
                    fcntl.flock(f, fcntl.LOCK_EX)
                else:
                    # Windows: use msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, len(full_message))

                f.write(full_message)
                f.flush()

                if os.name != "nt":
                    fcntl.flock(f, fcntl.LOCK_UN)
                else:
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, len(full_message))

        except Exception as e:
            print(f"Error writing to log: {e}", file=sys.stderr)

    def extract_metadata(self, file_path: Path) -> MetadataResult:
        """
        Extract metadata using multiple methods with fallback chain.

        Args:
            file_path: Path to the file to analyze

        Returns:
            MetadataResult with extracted metadata
        """
        result = MetadataResult()

        # Determine file category
        file_ext = file_path.suffix.lower().lstrip(".")
        category = self._get_file_category(file_ext)

        # Extraction method chain (ordered by reliability)
        methods = [
            self._extract_with_exiftool,
            self._extract_with_pillow,
            self._extract_with_mediainfo,
            self._extract_with_hachoir,
            self._extract_with_ebooklib,
            self._extract_from_filesystem,
            self._extract_from_filename,
        ]

        for method in methods:
            try:
                method_result = method(file_path, category)
                if method_result and not result.creation_date and method_result.creation_date:
                    result = method_result
                    break
            except Exception as e:
                self._safe_log(f"Method {method.__name__} failed for {file_path}: {e}")
                continue

        # Enhance with basic file information
        try:
            stat = file_path.stat()
            result.file_size = stat.st_size
            if not result.modification_date:
                result.modification_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y:%m:%d %H:%M:%S"
                )
        except Exception as e:
            self._safe_log(f"Error getting file stats for {file_path}: {e}")

        return result

    def _get_file_category(self, extension: str) -> str:
        """Determine file category based on extension."""
        for category, extensions in self.supported_formats.items():
            if extension in extensions:
                return category
        return "unknown"

    def _extract_with_exiftool(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract metadata using exiftool (most comprehensive)."""
        if not self.external_tools.get("exiftool", False):
            return None

        try:
            cmd = ["exiftool", "-json", str(file_path)]
            output = subprocess.check_output(
                cmd, stderr=subprocess.DEVNULL, universal_newlines=True
            )
            data = json.loads(output)[0]

            result = MetadataResult()
            result.extraction_method = "exiftool"
            result.metadata_dict = data

            # Extract creation date (try multiple fields)
            date_fields = [
                "CreateDate",
                "DateTimeOriginal",
                "MediaCreateDate",
                "QuickTime:CreateDate",
                "ASF:FileCreateDate",
                "FileCreateDate",
            ]

            for field in date_fields:
                if data.get(field):
                    result.creation_date = self._normalize_date(data[field])
                    break

            # Extract other metadata
            if "Make" in data:
                result.camera_make = data["Make"]
            if "Model" in data:
                result.camera_model = data["Model"]
            if "GPSLatitude" in data and "GPSLongitude" in data:
                result.gps_coordinates = (data["GPSLatitude"], data["GPSLongitude"])
            if "ImageWidth" in data and "ImageHeight" in data:
                result.dimensions = (data["ImageWidth"], data["ImageHeight"])
            if "Duration" in data:
                result.duration = (
                    float(data["Duration"].split()[0])
                    if isinstance(data["Duration"], str)
                    else data["Duration"]
                )

            return result

        except Exception as e:
            self._safe_log(f"Exiftool extraction failed for {file_path}: {e}")
            return None

    def _extract_with_pillow(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract metadata using Pillow (for images)."""
        if not PILLOW_AVAILABLE or category != "images":
            return None

        try:
            with Image.open(file_path) as img:
                result = MetadataResult()
                result.extraction_method = "pillow"
                result.dimensions = img.size
                result.format_info = img.format

                # Extract EXIF data
                exif = img._getexif()
                if exif:
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)

                        if tag_name in ["DateTimeOriginal", "DateTime"]:
                            result.creation_date = self._normalize_date(value)
                        elif tag_name == "Make":
                            result.camera_make = str(value)
                        elif tag_name == "Model":
                            result.camera_model = str(value)

                return result

        except Exception as e:
            self._safe_log(f"Pillow extraction failed for {file_path}: {e}")
            return None

    def _extract_with_mediainfo(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract metadata using mediainfo (for media files)."""
        if not self.external_tools.get("mediainfo", False) or category not in ["videos", "audio"]:
            return None

        try:
            cmd = ["mediainfo", "--Output=JSON", str(file_path)]
            output = subprocess.check_output(
                cmd, stderr=subprocess.DEVNULL, universal_newlines=True
            )
            data = json.loads(output)

            result = MetadataResult()
            result.extraction_method = "mediainfo"
            result.metadata_dict = data

            # Parse tracks
            for track in data.get("media", {}).get("track", []):
                track_type = track.get("@type", "").lower()

                if track_type == "general":
                    # Extract creation date
                    for date_field in ["Encoded_Date", "Tagged_Date", "File_Created_Date"]:
                        if date_field in track:
                            result.creation_date = self._normalize_date(track[date_field])
                            break

                    # Extract duration
                    if "Duration" in track:
                        result.duration = float(track["Duration"])

                elif track_type == "video":
                    # Extract video dimensions
                    if "Width" in track and "Height" in track:
                        result.dimensions = (int(track["Width"]), int(track["Height"]))

            return result

        except Exception as e:
            self._safe_log(f"Mediainfo extraction failed for {file_path}: {e}")
            return None

    def _extract_with_hachoir(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract metadata using hachoir (universal parser)."""
        if not HACHOIR_AVAILABLE:
            return None

        try:
            parser = createParser(str(file_path))
            if not parser:
                return None

            metadata = extractMetadata(parser)
            if not metadata:
                return None

            result = MetadataResult()
            result.extraction_method = "hachoir"

            # Extract creation date
            if metadata.has("creation_date"):
                date_val = metadata.get("creation_date")
                if isinstance(date_val, datetime):
                    result.creation_date = date_val.strftime("%Y:%m:%d %H:%M:%S")
                else:
                    result.creation_date = self._normalize_date(str(date_val))

            # Extract dimensions
            if metadata.has("width") and metadata.has("height"):
                result.dimensions = (metadata.get("width"), metadata.get("height"))

            # Extract duration
            if metadata.has("duration"):
                duration = metadata.get("duration")
                result.duration = (
                    duration.total_seconds()
                    if hasattr(duration, "total_seconds")
                    else float(duration)
                )

            return result

        except Exception as e:
            self._safe_log(f"Hachoir extraction failed for {file_path}: {e}")
            return None

    def _extract_with_ebooklib(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract metadata from EPUB files using ebooklib."""
        if not EBOOKLIB_AVAILABLE or category != "ebooks" or file_path.suffix.lower() != ".epub":
            return None

        try:
            book = epub.read_epub(str(file_path))
            result = MetadataResult()
            result.extraction_method = "ebooklib"

            # Extract publication date
            dates = book.get_metadata("DC", "date")
            if dates:
                date_str = dates[0][0]
                result.creation_date = self._normalize_date(date_str)

            return result

        except Exception as e:
            self._safe_log(f"EbookLib extraction failed for {file_path}: {e}")
            return None

    def _extract_from_filesystem(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract metadata from filesystem (fallback method)."""
        try:
            stat = file_path.stat()
            result = MetadataResult()
            result.extraction_method = "filesystem"
            result.creation_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y:%m:%d %H:%M:%S"
            )
            result.file_size = stat.st_size

            return result

        except Exception as e:
            self._safe_log(f"Filesystem extraction failed for {file_path}: {e}")
            return None

    def _extract_from_filename(self, file_path: Path, category: str) -> MetadataResult | None:
        """Extract date from filename patterns (last resort)."""
        try:
            filename = file_path.name

            # Try various date patterns
            patterns = [
                r"(\d{4})[-_\s]?(\d{2})[-_\s]?(\d{2})",  # YYYY-MM-DD
                r"(\d{2})[-_\s]?(\d{2})[-_\s]?(\d{4})",  # DD-MM-YYYY or MM-DD-YYYY
                r"(\d{8})",  # YYYYMMDD
            ]

            for pattern in patterns:
                match = re.search(pattern, filename)
                if match:
                    groups = match.groups()

                    if len(groups) == 3:
                        # Determine if it's YYYY-MM-DD or DD-MM-YYYY
                        if len(groups[0]) == 4:  # YYYY-MM-DD
                            year, month, day = groups
                        else:  # DD-MM-YYYY or MM-DD-YYYY (assume MM-DD-YYYY)
                            month, day, year = groups
                    else:  # Single 8-digit number
                        date_str = groups[0]
                        year, month, day = date_str[:4], date_str[4:6], date_str[6:8]

                    # Validate date
                    try:
                        datetime(int(year), int(month), int(day))
                        result = MetadataResult()
                        result.extraction_method = "filename"
                        result.creation_date = f"{year}:{month.zfill(2)}:{day.zfill(2)}"
                        return result
                    except ValueError:
                        continue

            return None

        except Exception as e:
            self._safe_log(f"Filename extraction failed for {file_path}: {e}")
            return None

    def _normalize_date(self, date_str: str) -> str:
        """Normalize various date formats to YYYY:MM:DD HH:MM:SS."""
        if not date_str:
            return ""

        # Remove timezone info and extra whitespace
        date_str = re.sub(r"[+-]\d{2}:?\d{2}$", "", str(date_str)).strip()

        # Try to parse common formats
        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y:%m:%d",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y:%m:%d %H:%M:%S")
            except ValueError:
                continue

        # If no format matches, try regex extraction
        match = re.search(r"(\d{4})[-/:]\s*(\d{1,2})[-/:]\s*(\d{1,2})", date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}:{month.zfill(2)}:{day.zfill(2)} 00:00:00"

        return date_str

    def get_extraction_stats(self) -> dict[str, Any]:
        """Get statistics about available extraction methods."""
        return {
            "external_tools": self.external_tools,
            "optional_libraries": {
                "pillow": PILLOW_AVAILABLE,
                "googletrans": GOOGLETRANS_AVAILABLE,
                "ebooklib": EBOOKLIB_AVAILABLE,
                "hachoir": HACHOIR_AVAILABLE,
            },
            "supported_formats": {k: len(v) for k, v in self.supported_formats.items()},
            "total_formats": sum(len(v) for v in self.supported_formats.values()),
        }
