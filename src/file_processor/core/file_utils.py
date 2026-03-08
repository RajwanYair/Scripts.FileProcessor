#!/usr/bin/env python3
"""
file_utils.py — Core filename and path utilities.

Provides:
- ``sanitize_filename``   — safe, cross-platform filename cleaning
- ``translate_filename``  — optional non-ASCII → English translation
- ``normalize_extension`` — map aliased extensions to canonical forms
"""

from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional googletrans support
try:
    from googletrans import Translator

    TRANSLATION_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    TRANSLATION_AVAILABLE = False
    Translator = None  # type: ignore[assignment,misc]
    logger.debug(
        "googletrans not installed — filename translation disabled. "
        "Install with: pip install googletrans==4.0.0rc1"
    )

# Canonical extension map: alias → preferred extension
EXT_MAP: dict[str, str] = {
    ".jpeg": ".jpg",
    ".jpe": ".jpg",
    ".jfif": ".jpg",
    ".cbz": ".zip",
    ".cbr": ".rar",
    ".cbt": ".tar",
    ".cb7": ".7z",
    ".tiff": ".tif",
    ".epub": ".zip",
    ".bmp": ".png",
    ".gif": ".png",
    ".webp": ".png",
    ".tar": ".tar",
    ".7z": ".7z",
    ".rar": ".rar",
    ".zip": ".zip",
}


def sanitize_filename(name: str) -> str:
    """Return a safe, cross-platform filename (no path traversal, no control chars)."""
    # Replace forbidden characters
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Strip non-printable control characters (must happen before collapse so that
    # a control char between two underscores doesn't leave a double-underscore)
    name = "".join(c for c in name if c.isprintable())
    # Collapse multiple underscores (after control-char removal for idempotency)
    name = re.sub(r"_+", "_", name)
    # NFC Unicode normalisation (always available in stdlib)
    name = unicodedata.normalize("NFC", name)
    # Strip leading/trailing punctuation
    name = name.strip("_.")
    return name or "unnamed"


def translate_filename(name: str, translator: object | None = None) -> str:
    """
    Translate non-ASCII words in *name* to English.

    No-op when ``googletrans`` is unavailable or *translator* is ``None``.
    """
    if not TRANSLATION_AVAILABLE or translator is None:
        return name

    base, ext = Path(name).stem, Path(name).suffix
    words = re.split(r"[_\s\-\.\[\]()]+", base)
    translated: list[str] = []
    for word in words:
        if not word.strip():
            continue
        if any(ord(c) > 127 for c in word):
            try:
                result = translator.translate(word, dest="en")  # type: ignore[union-attr]
                translated.append(result.text)
            except Exception as exc:
                logger.warning("Translation failed for %r: %s", word, exc)
                translated.append(word)
        else:
            translated.append(word)
    return "_".join(translated) + ext


def normalize_extension(filename: str) -> str:
    """Return *filename* with its extension mapped to the canonical form (if known)."""
    path = Path(filename)
    canonical = EXT_MAP.get(path.suffix.lower())
    return str(path.with_suffix(canonical)) if canonical else str(path)
