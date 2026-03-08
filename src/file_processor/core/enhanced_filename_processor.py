"""
Enhanced Filename Processor
===========================
Advanced filename processing with internationalization support, translation,
sanitization, and cross-platform compatibility.

DEPRECATION WARNING:
====================
This module is maintained for backward compatibility.
For new code, please use: from core.unified_utilities import UnifiedFilenameProcessor

The UnifiedFilenameProcessor provides the same functionality with:
- Better performance through caching
- Consolidated implementation (no code duplication)
- Active maintenance and updates
- Full backward compatibility

This module provides comprehensive filename processing capabilities including:
- Cross-platform filename sanitization
- Automatic translation to English
- Date prefix handling and normalization
- Extension normalization
- Series and sequence detection
"""

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Any
import unicodedata

# Import from unified utilities
try:
    from .unified_utilities import UnifiedFilenameProcessor as _UnifiedProcessor

    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False
    _UnifiedProcessor = None

# Optional imports for translation
try:
    from googletrans import Translator

    TRANSLATOR = Translator()
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False


@dataclass
class FilenameProcessingResult:
    """Result of filename processing operations."""

    original_name: str
    processed_name: str
    sanitized: bool = False
    translated: bool = False
    date_prefix_added: bool = False
    extension_normalized: bool = False
    encoding_fixed: bool = False
    changes_made: list[str] = None

    def __post_init__(self):
        if self.changes_made is None:
            self.changes_made = []


class EnhancedFilenameProcessor:
    """
    Advanced filename processor with internationalization and cross-platform support.

    Features:
    - Cross-platform filename sanitization
    - Automatic translation of non-English text
    - Date prefix handling and extraction
    - Extension normalization
    - Unicode normalization and encoding fixes
    - Series and sequence detection
    - Configurable sanitization rules
    """

    def __init__(
        self, enable_translation: bool = True, translation_cache_size: int = 1000, log_callback=None
    ):
        """
        Initialize the filename processor.

        Args:
            enable_translation: Whether to attempt translation of non-English text
            translation_cache_size: Size of translation cache to avoid repeated API calls
            log_callback: Function to call for logging messages
        """
        self.enable_translation = enable_translation and GOOGLETRANS_AVAILABLE
        self.translation_cache = {}
        self.translation_cache_size = translation_cache_size
        self.log_callback = log_callback or print

        # Platform-specific forbidden characters
        self.forbidden_chars = self._get_forbidden_chars()

        # Extension normalization mapping
        self.extension_mapping = self._get_extension_mapping()

        # Common date patterns
        self.date_patterns = self._get_date_patterns()

    def _get_forbidden_chars(self) -> dict[str, str]:
        """Get forbidden characters for current platform."""
        # Windows forbidden characters
        windows_forbidden = r'<>:"/\|?*'

        # Additional characters to replace for better compatibility
        additional_chars = {
            "…": "...",
            "–": "-",
            "—": "-",
            """: "'",
            """: "'",
            '"': '"',
            "«": '"',
            "»": '"',
            "‹": "'",
            "›": "'",
            "°": "deg",
            "™": "TM",
            "®": "R",
            "©": "C",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
            "§": "section",
            "¶": "para",
            "†": "+",
            "‡": "++",
            "•": "-",
            "‰": "permille",
            "№": "No",
        }

        # Base forbidden characters (Windows is most restrictive)
        base_mapping = dict.fromkeys(windows_forbidden, "_")

        # Add additional character mappings
        base_mapping.update(additional_chars)

        return base_mapping

    def _get_extension_mapping(self) -> dict[str, str]:
        """Get extension normalization mapping."""
        return {
            # Image formats
            "jpeg": "jpg",
            "tiff": "tif",
            "jpe": "jpg",
            "jfif": "jpg",
            # Document formats
            "doc": "docx",
            "xls": "xlsx",
            "ppt": "pptx",
            "htm": "html",
            # Archive formats
            "cbz": "zip",  # Comic book ZIP
            "cbr": "rar",  # Comic book RAR
            "cb7": "7z",  # Comic book 7Z
            "cbt": "tar",  # Comic book TAR
            "cba": "ace",  # Comic book ACE
            # Video formats
            "mpeg": "mpg",
            "m4v": "mp4",
            "qt": "mov",
            # Audio formats
            "m4a": "mp4",  # Keep as m4a for audio
            "aiff": "aif",
            "wave": "wav",
        }

    def _get_date_patterns(self) -> list[tuple[str, str]]:
        """Get common date patterns for extraction."""
        return [
            (r"(\d{4})[-_\s](\d{2})[-_\s](\d{2})", r"\1\2\3"),  # YYYY-MM-DD
            (r"(\d{2})[-_\s](\d{2})[-_\s](\d{4})", r"\3\1\2"),  # DD-MM-YYYY
            (r"(\d{2})[-_\s](\d{2})[-_\s](\d{2})", r"20\3\1\2"),  # DD-MM-YY (assume 2000s)
            (r"(\d{8})", r"\1"),  # YYYYMMDD
            (r"(\d{6})", r"20\1"),  # YYMMDD (assume 2000s)
        ]

    def sanitize_filename(self, filename: str, max_length: int = 255) -> str:
        """
        Sanitize filename for cross-platform compatibility.

        Args:
            filename: Original filename
            max_length: Maximum allowed filename length

        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed_file"

        # Normalize Unicode characters
        normalized = unicodedata.normalize("NFKD", filename)

        # Convert to ASCII, replacing non-ASCII characters
        ascii_filename = normalized.encode("ascii", "ignore").decode("ascii")

        # If too much was lost in ASCII conversion, use transliteration
        if len(ascii_filename) < len(filename) * 0.5:
            ascii_filename = self._transliterate_unicode(filename)

        # Replace forbidden characters
        for forbidden, replacement in self.forbidden_chars.items():
            ascii_filename = ascii_filename.replace(forbidden, replacement)

        # Replace multiple consecutive underscores/spaces/dashes with single underscore
        ascii_filename = re.sub(r"[_\s-]+", "_", ascii_filename)

        # Remove leading/trailing underscores and dots
        ascii_filename = ascii_filename.strip("_.")

        # Ensure filename isn't empty
        if not ascii_filename:
            ascii_filename = "unnamed_file"

        # Handle Windows reserved names
        ascii_filename = self._handle_reserved_names(ascii_filename)

        # Truncate if too long, preserving extension
        if len(ascii_filename) > max_length:
            ascii_filename = self._truncate_filename(ascii_filename, max_length)

        return ascii_filename

    def _transliterate_unicode(self, text: str) -> str:
        """Transliterate Unicode characters to ASCII equivalents."""
        # Common Unicode to ASCII transliterations
        transliterations = {
            # Cyrillic
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "yo",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "h",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "sch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya",
            # Greek
            "α": "a",
            "β": "b",
            "γ": "g",
            "δ": "d",
            "ε": "e",
            "ζ": "z",
            "η": "e",
            "θ": "th",
            "ι": "i",
            "κ": "k",
            "λ": "l",
            "μ": "m",
            "ν": "n",
            "ξ": "x",
            "ο": "o",
            "π": "p",
            "ρ": "r",
            "σ": "s",
            "τ": "t",
            "υ": "y",
            "φ": "f",
            "χ": "ch",
            "ψ": "ps",
            "ω": "o",
            # Arabic numerals
            "٠": "0",
            "١": "1",
            "٢": "2",
            "٣": "3",
            "٤": "4",
            "٥": "5",
            "٦": "6",
            "٧": "7",
            "٨": "8",
            "٩": "9",
            # Chinese/Japanese common characters
            "的": "de",
            "是": "shi",
            "在": "zai",
            "了": "le",
            "和": "he",
            "を": "wo",
            "は": "ha",
            "が": "ga",
            "に": "ni",
            "の": "no",
        }

        result = text.lower()
        for unicode_char, ascii_equiv in transliterations.items():
            result = result.replace(unicode_char, ascii_equiv)

        # Remove remaining non-ASCII characters
        result = re.sub(r"[^\x00-\x7F]+", "", result)

        return result

    def _handle_reserved_names(self, filename: str) -> str:
        """Handle Windows reserved filenames."""
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

        name_part = filename.split(".")[0].upper()
        if name_part in reserved_names:
            return f"_{filename}"

        return filename

    def _truncate_filename(self, filename: str, max_length: int) -> str:
        """Truncate filename while preserving extension."""
        if "." in filename:
            name, ext = filename.rsplit(".", 1)
            max_name_length = max_length - len(ext) - 1  # -1 for the dot
            if max_name_length > 0:
                return f"{name[:max_name_length]}.{ext}"
            else:
                return f"file.{ext}"
        else:
            return filename[:max_length]

    def translate_text(self, text: str, target_language: str = "en") -> str:
        """
        Translate text to target language using Google Translate.

        Args:
            text: Text to translate
            target_language: Target language code (default: 'en' for English)

        Returns:
            Translated text or original if translation fails
        """
        if not self.enable_translation or not text.strip():
            return text

        # Check cache first
        cache_key = f"{text}:{target_language}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        try:
            # Detect if text is already in target language
            detection = TRANSLATOR.detect(text)
            if detection.lang == target_language:
                return text

            # Translate text
            result = TRANSLATOR.translate(text, dest=target_language)
            translated_text = result.text

            # Cache the result
            if len(self.translation_cache) < self.translation_cache_size:
                self.translation_cache[cache_key] = translated_text

            return translated_text

        except Exception as e:
            self.log_callback(f"Translation failed for '{text}': {e}")
            return text

    def normalize_extension(self, extension: str) -> str:
        """
        Normalize file extension to standard format.

        Args:
            extension: File extension (with or without dot)

        Returns:
            Normalized extension (without dot)
        """
        if not extension:
            return ""

        # Remove leading dot and convert to lowercase
        ext = extension.lower().lstrip(".")

        # Apply normalization mapping
        return self.extension_mapping.get(ext, ext)

    def extract_date_prefix(self, filename: str) -> tuple[str | None, str]:
        """
        Extract date prefix from filename.

        Args:
            filename: Filename to analyze

        Returns:
            Tuple of (date_prefix, remaining_filename)
        """
        # Look for existing 8-digit date prefix
        match = re.match(r"^(\d{8})_(.+)$", filename)
        if match:
            return match.group(1), match.group(2)

        # Look for other date patterns in filename
        for pattern, replacement in self.date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = re.sub(pattern, replacement, match.group(0))
                # Validate date format (YYYYMMDD)
                if len(date_str) == 8 and date_str.isdigit():
                    year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
                    try:
                        # Basic date validation
                        if (
                            1900 <= int(year) <= 2100
                            and 1 <= int(month) <= 12
                            and 1 <= int(day) <= 31
                        ):
                            # Remove date from filename
                            remaining = re.sub(pattern, "", filename).strip("_-. ")
                            return date_str, remaining
                    except ValueError:
                        continue

        return None, filename

    def add_date_prefix(self, filename: str, date_prefix: str) -> str:
        """
        Add date prefix to filename, removing any existing date prefix.

        Args:
            filename: Original filename
            date_prefix: Date prefix to add (YYYYMMDD format)

        Returns:
            Filename with date prefix
        """
        # Remove existing date prefix
        _, clean_filename = self.extract_date_prefix(filename)

        # Add new date prefix
        return f"{date_prefix}_{clean_filename}"

    def detect_series_info(self, filename: str) -> dict[str, Any]:
        """
        Detect series information from filename (volume, chapter, part, etc.).

        Args:
            filename: Filename to analyze

        Returns:
            Dictionary with series information
        """
        series_info = {
            "is_series": False,
            "volume": None,
            "chapter": None,
            "part": None,
            "episode": None,
            "season": None,
            "series_name": filename,
        }

        # Common series patterns
        patterns = [
            (r"(?i)vol(?:ume)?[\s._-]*(\d+)", "volume"),
            (r"(?i)ch(?:apter)?[\s._-]*(\d+)", "chapter"),
            (r"(?i)part[\s._-]*(\d+)", "part"),
            (r"(?i)ep(?:isode)?[\s._-]*(\d+)", "episode"),
            (r"(?i)season[\s._-]*(\d+)", "season"),
            (r"(?i)s(\d+)e(\d+)", "season_episode"),  # S01E01 format
            (r"\b(\d{1,3})\b", "number"),  # Generic number
        ]

        for pattern, info_type in patterns:
            match = re.search(pattern, filename)
            if match:
                series_info["is_series"] = True
                if info_type == "season_episode":
                    series_info["season"] = int(match.group(1))
                    series_info["episode"] = int(match.group(2))
                else:
                    series_info[info_type] = int(match.group(1))

        return series_info

    def process_filename(
        self,
        filepath: Path,
        add_date_prefix: str | None = None,
        translate_to_english: bool = True,
        normalize_extension: bool = True,
    ) -> FilenameProcessingResult:
        """
        Comprehensive filename processing.

        Args:
            filepath: Path to the file
            add_date_prefix: Date prefix to add (YYYYMMDD format)
            translate_to_english: Whether to translate non-English text
            normalize_extension: Whether to normalize file extension

        Returns:
            FilenameProcessingResult with processing details
        """
        original_name = filepath.name
        changes = []

        # Separate name and extension
        if "." in original_name:
            name_part, ext_part = original_name.rsplit(".", 1)
        else:
            name_part, ext_part = original_name, ""

        # Process name part
        processed_name = name_part

        # Extract existing date prefix
        existing_date, clean_name = self.extract_date_prefix(processed_name)
        if existing_date:
            changes.append("removed_existing_date_prefix")
            processed_name = clean_name

        # Translate if requested and possible
        translated = False
        if translate_to_english and self.enable_translation:
            # Split by common separators and translate each part
            parts = re.split(r"[_\s-]+", processed_name)
            translated_parts = []

            for part in parts:
                if part and not part.isdigit() and len(part) > 1:
                    translated_part = self.translate_text(part)
                    if translated_part != part:
                        translated = True
                        translated_parts.append(translated_part)
                    else:
                        translated_parts.append(part)
                else:
                    translated_parts.append(part)

            if translated:
                processed_name = "_".join(translated_parts)
                changes.append("translated_to_english")

        # Sanitize filename
        original_processed = processed_name
        processed_name = self.sanitize_filename(processed_name)
        if processed_name != original_processed:
            changes.append("sanitized_characters")

        # Normalize extension
        extension_normalized = False
        if normalize_extension and ext_part:
            normalized_ext = self.normalize_extension(ext_part)
            if normalized_ext != ext_part.lower():
                ext_part = normalized_ext
                extension_normalized = True
                changes.append("normalized_extension")

        # Add date prefix if requested
        date_prefix_added = False
        if add_date_prefix:
            processed_name = f"{add_date_prefix}_{processed_name}"
            date_prefix_added = True
            changes.append("added_date_prefix")

        # Reconstruct full filename
        final_name = f"{processed_name}.{ext_part}" if ext_part else processed_name

        return FilenameProcessingResult(
            original_name=original_name,
            processed_name=final_name,
            sanitized=(processed_name != name_part),
            translated=translated,
            date_prefix_added=date_prefix_added,
            extension_normalized=extension_normalized,
            changes_made=changes,
        )

    def batch_process_filenames(
        self,
        file_paths: list[Path],
        add_date_prefix: str | None = None,
        translate_to_english: bool = True,
        normalize_extension: bool = True,
        apply_changes: bool = False,
    ) -> dict[str, FilenameProcessingResult]:
        """
        Process multiple filenames in batch.

        Args:
            file_paths: List of file paths to process
            add_date_prefix: Date prefix to add to all files
            translate_to_english: Whether to translate non-English text
            normalize_extension: Whether to normalize file extensions
            apply_changes: Whether to actually rename the files

        Returns:
            Dictionary mapping original paths to processing results
        """
        results = {}

        for file_path in file_paths:
            try:
                result = self.process_filename(
                    file_path,
                    add_date_prefix=add_date_prefix,
                    translate_to_english=translate_to_english,
                    normalize_extension=normalize_extension,
                )

                results[str(file_path)] = result

                # Apply changes if requested
                if apply_changes and result.processed_name != result.original_name:
                    new_path = file_path.parent / result.processed_name
                    try:
                        file_path.rename(new_path)
                        self.log_callback(
                            f"Renamed: {result.original_name} -> {result.processed_name}"
                        )
                    except Exception as e:
                        self.log_callback(f"Failed to rename {file_path}: {e}")
                        result.changes_made.append("rename_failed")

            except Exception as e:
                self.log_callback(f"Error processing {file_path}: {e}")
                results[str(file_path)] = FilenameProcessingResult(
                    original_name=file_path.name,
                    processed_name=file_path.name,
                    changes_made=["processing_error"],
                )

        return results

    def get_processing_stats(self) -> dict[str, Any]:
        """Get processing statistics and capabilities."""
        return {
            "translation_available": self.enable_translation,
            "translation_cache_size": len(self.translation_cache),
            "supported_extensions": len(self.extension_mapping),
            "forbidden_chars_mapped": len(self.forbidden_chars),
            "date_patterns_supported": len(self.date_patterns),
            "platform": os.name,
        }
