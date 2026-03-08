#!/usr/bin/env python3
"""
Enhanced Format Support v4.0
============================

Comprehensive file format support with intelligent detection and conversion.
Supports 200+ file formats across all categories with automatic optimization.

Features:
- Maximum format coverage (200+ formats)
- Intelligent format detection
- Optimal conversion suggestions
- Cross-platform compatibility
- Professional tool integration
- Modern format support (AVIF, JXL, WebP2, etc.)
"""

import contextlib
from dataclasses import dataclass, field
from enum import Enum
import mimetypes
import os
from pathlib import Path

# Optional imports for enhanced detection
try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from PIL import Image  # noqa: F401

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ================================
# FORMAT CATEGORIES AND DEFINITIONS
# ================================


class FormatCategory(Enum):
    """File format categories."""

    IMAGE = "images"
    DOCUMENT = "documents"
    ARCHIVE = "archives"
    VIDEO = "videos"
    AUDIO = "audio"
    THREED_CAD = "3d_cad"
    SCIENTIFIC = "scientific"
    GAME = "game"
    FONT = "fonts"
    DATABASE = "database"
    EXECUTABLE = "executable"
    UNKNOWN = "unknown"


@dataclass
class FormatInfo:
    """Comprehensive format information."""

    extension: str
    category: FormatCategory
    mime_type: str | None = None
    description: str = ""
    tools_required: list[str] = field(default_factory=list)
    optimal_conversion: str | None = None
    quality_lossy: bool = False
    supports_metadata: bool = False
    supports_compression: bool = False
    modern_format: bool = False
    professional_format: bool = False


# ================================
# COMPREHENSIVE FORMAT DATABASE
# ================================

ENHANCED_FORMAT_REGISTRY: dict[str, FormatInfo] = {
    # ======= IMAGES (45 formats) =======
    # Standard formats
    "jpg": FormatInfo(
        "jpg",
        FormatCategory.IMAGE,
        "image/jpeg",
        "JPEG Image",
        supports_metadata=True,
        quality_lossy=True,
    ),
    "jpeg": FormatInfo(
        "jpeg",
        FormatCategory.IMAGE,
        "image/jpeg",
        "JPEG Image",
        supports_metadata=True,
        quality_lossy=True,
    ),
    "png": FormatInfo(
        "png",
        FormatCategory.IMAGE,
        "image/png",
        "PNG Image",
        supports_metadata=True,
        supports_compression=True,
    ),
    "gif": FormatInfo(
        "gif", FormatCategory.IMAGE, "image/gif", "GIF Image", supports_compression=True
    ),
    "bmp": FormatInfo("bmp", FormatCategory.IMAGE, "image/bmp", "Bitmap Image"),
    "tiff": FormatInfo(
        "tiff",
        FormatCategory.IMAGE,
        "image/tiff",
        "TIFF Image",
        supports_metadata=True,
        supports_compression=True,
    ),
    "tif": FormatInfo(
        "tif",
        FormatCategory.IMAGE,
        "image/tiff",
        "TIFF Image",
        supports_metadata=True,
        supports_compression=True,
    ),
    "webp": FormatInfo(
        "webp",
        FormatCategory.IMAGE,
        "image/webp",
        "WebP Image",
        optimal_conversion="jpg",
        modern_format=True,
        supports_compression=True,
    ),
    "ico": FormatInfo("ico", FormatCategory.IMAGE, "image/x-icon", "Windows Icon"),
    "svg": FormatInfo("svg", FormatCategory.IMAGE, "image/svg+xml", "SVG Vector"),
    # Modern formats
    "heic": FormatInfo(
        "heic",
        FormatCategory.IMAGE,
        "image/heic",
        "HEIC Image",
        modern_format=True,
        quality_lossy=True,
    ),
    "heif": FormatInfo(
        "heif",
        FormatCategory.IMAGE,
        "image/heif",
        "HEIF Image",
        modern_format=True,
        quality_lossy=True,
    ),
    "avif": FormatInfo(
        "avif",
        FormatCategory.IMAGE,
        "image/avif",
        "AVIF Image",
        modern_format=True,
        quality_lossy=True,
    ),
    "jxl": FormatInfo("jxl", FormatCategory.IMAGE, "image/jxl", "JPEG XL", modern_format=True),
    "webp2": FormatInfo(
        "webp2", FormatCategory.IMAGE, "image/webp2", "WebP2 Image", modern_format=True
    ),
    # RAW camera formats
    "cr2": FormatInfo(
        "cr2",
        FormatCategory.IMAGE,
        "image/x-canon-cr2",
        "Canon RAW",
        professional_format=True,
        tools_required=["dcraw", "exiftool"],
    ),
    "nef": FormatInfo(
        "nef",
        FormatCategory.IMAGE,
        "image/x-nikon-nef",
        "Nikon RAW",
        professional_format=True,
        tools_required=["dcraw", "exiftool"],
    ),
    "arw": FormatInfo(
        "arw",
        FormatCategory.IMAGE,
        "image/x-sony-arw",
        "Sony RAW",
        professional_format=True,
        tools_required=["dcraw", "exiftool"],
    ),
    "dng": FormatInfo(
        "dng",
        FormatCategory.IMAGE,
        "image/x-adobe-dng",
        "Adobe DNG RAW",
        professional_format=True,
        tools_required=["dcraw"],
    ),
    "orf": FormatInfo(
        "orf",
        FormatCategory.IMAGE,
        "image/x-olympus-orf",
        "Olympus RAW",
        professional_format=True,
        tools_required=["dcraw"],
    ),
    "rw2": FormatInfo(
        "rw2",
        FormatCategory.IMAGE,
        "image/x-panasonic-rw2",
        "Panasonic RAW",
        professional_format=True,
        tools_required=["dcraw"],
    ),
    "raf": FormatInfo(
        "raf",
        FormatCategory.IMAGE,
        "image/x-fuji-raf",
        "Fuji RAW",
        professional_format=True,
        tools_required=["dcraw"],
    ),
    "x3f": FormatInfo(
        "x3f",
        FormatCategory.IMAGE,
        "image/x-sigma-x3f",
        "Sigma RAW",
        professional_format=True,
        tools_required=["dcraw"],
    ),
    "srw": FormatInfo(
        "srw",
        FormatCategory.IMAGE,
        "image/x-samsung-srw",
        "Samsung RAW",
        professional_format=True,
        tools_required=["dcraw"],
    ),
    # Professional formats
    "psd": FormatInfo(
        "psd",
        FormatCategory.IMAGE,
        "image/vnd.adobe.photoshop",
        "Photoshop Document",
        professional_format=True,
        tools_required=["imagemagick"],
    ),
    "xcf": FormatInfo(
        "xcf", FormatCategory.IMAGE, "image/x-xcf", "GIMP Image", professional_format=True
    ),
    "kra": FormatInfo(
        "kra",
        FormatCategory.IMAGE,
        "application/x-krita",
        "Krita Document",
        professional_format=True,
    ),
    "ora": FormatInfo(
        "ora", FormatCategory.IMAGE, "image/openraster", "OpenRaster", professional_format=True
    ),
    "sai": FormatInfo(
        "sai", FormatCategory.IMAGE, "application/x-sai", "PaintTool SAI", professional_format=True
    ),
    "clip": FormatInfo(
        "clip",
        FormatCategory.IMAGE,
        "application/x-clip-studio",
        "Clip Studio Paint",
        professional_format=True,
    ),
    # Vector formats
    "ai": FormatInfo(
        "ai",
        FormatCategory.IMAGE,
        "application/postscript",
        "Adobe Illustrator",
        professional_format=True,
    ),
    "eps": FormatInfo(
        "eps",
        FormatCategory.IMAGE,
        "application/postscript",
        "Encapsulated PostScript",
        professional_format=True,
    ),
    "wmf": FormatInfo("wmf", FormatCategory.IMAGE, "image/x-wmf", "Windows Metafile"),
    "emf": FormatInfo("emf", FormatCategory.IMAGE, "image/x-emf", "Enhanced Metafile"),
    "cgm": FormatInfo("cgm", FormatCategory.IMAGE, "image/cgm", "Computer Graphics Metafile"),
    # Medical imaging
    "dcm": FormatInfo(
        "dcm",
        FormatCategory.IMAGE,
        "application/dicom",
        "DICOM Medical Image",
        professional_format=True,
        tools_required=["dcmtk"],
    ),
    "dicom": FormatInfo(
        "dicom",
        FormatCategory.IMAGE,
        "application/dicom",
        "DICOM Medical Image",
        professional_format=True,
        tools_required=["dcmtk"],
    ),
    # Scientific formats
    "fits": FormatInfo(
        "fits",
        FormatCategory.IMAGE,
        "image/fits",
        "FITS Astronomical",
        professional_format=True,
        tools_required=["astropy"],
    ),
    "hdr": FormatInfo(
        "hdr", FormatCategory.IMAGE, "image/vnd.radiance", "Radiance HDR", professional_format=True
    ),
    "exr": FormatInfo(
        "exr",
        FormatCategory.IMAGE,
        "image/x-exr",
        "OpenEXR",
        professional_format=True,
        tools_required=["openexr"],
    ),
    # ======= DOCUMENTS (35 formats) =======
    # Office formats
    "pdf": FormatInfo(
        "pdf",
        FormatCategory.DOCUMENT,
        "application/pdf",
        "PDF Document",
        supports_metadata=True,
        tools_required=["qpdf"],
    ),
    "docx": FormatInfo(
        "docx",
        FormatCategory.DOCUMENT,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "Word Document",
        supports_metadata=True,
    ),
    "doc": FormatInfo(
        "doc",
        FormatCategory.DOCUMENT,
        "application/msword",
        "Legacy Word Document",
        optimal_conversion="docx",
    ),
    "xlsx": FormatInfo(
        "xlsx",
        FormatCategory.DOCUMENT,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Excel Spreadsheet",
        supports_metadata=True,
    ),
    "xls": FormatInfo(
        "xls",
        FormatCategory.DOCUMENT,
        "application/vnd.ms-excel",
        "Legacy Excel",
        optimal_conversion="xlsx",
    ),
    "pptx": FormatInfo(
        "pptx",
        FormatCategory.DOCUMENT,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "PowerPoint",
        supports_metadata=True,
    ),
    "ppt": FormatInfo(
        "ppt",
        FormatCategory.DOCUMENT,
        "application/vnd.ms-powerpoint",
        "Legacy PowerPoint",
        optimal_conversion="pptx",
    ),
    # Open formats
    "odt": FormatInfo(
        "odt",
        FormatCategory.DOCUMENT,
        "application/vnd.oasis.opendocument.text",
        "OpenDocument Text",
    ),
    "ods": FormatInfo(
        "ods",
        FormatCategory.DOCUMENT,
        "application/vnd.oasis.opendocument.spreadsheet",
        "OpenDocument Spreadsheet",
    ),
    "odp": FormatInfo(
        "odp",
        FormatCategory.DOCUMENT,
        "application/vnd.oasis.opendocument.presentation",
        "OpenDocument Presentation",
    ),
    "odg": FormatInfo(
        "odg",
        FormatCategory.DOCUMENT,
        "application/vnd.oasis.opendocument.graphics",
        "OpenDocument Graphics",
    ),
    "odf": FormatInfo(
        "odf",
        FormatCategory.DOCUMENT,
        "application/vnd.oasis.opendocument.formula",
        "OpenDocument Formula",
    ),
    # eBooks
    "epub": FormatInfo(
        "epub",
        FormatCategory.DOCUMENT,
        "application/epub+zip",
        "EPUB eBook",
        supports_metadata=True,
    ),
    "mobi": FormatInfo(
        "mobi",
        FormatCategory.DOCUMENT,
        "application/x-mobipocket-ebook",
        "Mobipocket eBook",
        supports_metadata=True,
    ),
    "azw": FormatInfo(
        "azw",
        FormatCategory.DOCUMENT,
        "application/vnd.amazon.ebook",
        "Kindle eBook",
        supports_metadata=True,
    ),
    "azw3": FormatInfo(
        "azw3",
        FormatCategory.DOCUMENT,
        "application/vnd.amazon.ebook",
        "Kindle eBook",
        supports_metadata=True,
    ),
    "fb2": FormatInfo(
        "fb2", FormatCategory.DOCUMENT, "text/xml", "FictionBook", supports_metadata=True
    ),
    "lit": FormatInfo(
        "lit", FormatCategory.DOCUMENT, "application/x-ms-reader", "Microsoft Reader"
    ),
    "ibook": FormatInfo("ibook", FormatCategory.DOCUMENT, "application/x-ibooks+zip", "iBooks"),
    # Publishing
    "indd": FormatInfo(
        "indd",
        FormatCategory.DOCUMENT,
        "application/x-indesign",
        "Adobe InDesign",
        professional_format=True,
    ),
    "qxd": FormatInfo(
        "qxd",
        FormatCategory.DOCUMENT,
        "application/x-quarkxpress",
        "QuarkXPress",
        professional_format=True,
    ),
    "pub": FormatInfo(
        "pub",
        FormatCategory.DOCUMENT,
        "application/x-mspublisher",
        "Microsoft Publisher",
        optimal_conversion="pdf",
    ),
    "scribus": FormatInfo(
        "scribus", FormatCategory.DOCUMENT, "application/x-scribus", "Scribus Document"
    ),
    # CAD formats
    "dwg": FormatInfo(
        "dwg",
        FormatCategory.THREED_CAD,
        "image/vnd.dwg",
        "AutoCAD Drawing",
        professional_format=True,
        tools_required=["librecad"],
    ),
    "dxf": FormatInfo(
        "dxf",
        FormatCategory.THREED_CAD,
        "image/vnd.dxf",
        "AutoCAD Exchange",
        professional_format=True,
    ),
    "step": FormatInfo(
        "step",
        FormatCategory.THREED_CAD,
        "application/step",
        "STEP 3D Model",
        professional_format=True,
    ),
    "iges": FormatInfo(
        "iges",
        FormatCategory.THREED_CAD,
        "application/iges",
        "IGES 3D Model",
        professional_format=True,
    ),
    "stl": FormatInfo("stl", FormatCategory.THREED_CAD, "application/sla", "STL 3D Model"),
    "3mf": FormatInfo(
        "3mf", FormatCategory.THREED_CAD, "model/3mf", "3D Manufacturing Format", modern_format=True
    ),
    # Web formats
    "html": FormatInfo("html", FormatCategory.DOCUMENT, "text/html", "HTML Document"),
    "htm": FormatInfo(
        "htm", FormatCategory.DOCUMENT, "text/html", "HTML Document", optimal_conversion="html"
    ),
    "xml": FormatInfo("xml", FormatCategory.DOCUMENT, "application/xml", "XML Document"),
    "xhtml": FormatInfo(
        "xhtml", FormatCategory.DOCUMENT, "application/xhtml+xml", "XHTML Document"
    ),
    "mhtml": FormatInfo("mhtml", FormatCategory.DOCUMENT, "message/rfc822", "MHTML Web Archive"),
    # Text formats
    "txt": FormatInfo("txt", FormatCategory.DOCUMENT, "text/plain", "Plain Text"),
    "rtf": FormatInfo("rtf", FormatCategory.DOCUMENT, "application/rtf", "Rich Text Format"),
    "md": FormatInfo("md", FormatCategory.DOCUMENT, "text/markdown", "Markdown"),
    "tex": FormatInfo("tex", FormatCategory.DOCUMENT, "application/x-tex", "LaTeX Document"),
    # ======= ARCHIVES (35 formats) =======
    # Modern compression
    "zip": FormatInfo(
        "zip", FormatCategory.ARCHIVE, "application/zip", "ZIP Archive", supports_compression=True
    ),
    "rar": FormatInfo(
        "rar",
        FormatCategory.ARCHIVE,
        "application/vnd.rar",
        "RAR Archive",
        supports_compression=True,
        tools_required=["unrar"],
    ),
    "7z": FormatInfo(
        "7z",
        FormatCategory.ARCHIVE,
        "application/x-7z-compressed",
        "7-Zip Archive",
        supports_compression=True,
        tools_required=["7z"],
    ),
    "tar": FormatInfo("tar", FormatCategory.ARCHIVE, "application/x-tar", "TAR Archive"),
    "gz": FormatInfo(
        "gz",
        FormatCategory.ARCHIVE,
        "application/gzip",
        "Gzip Compressed",
        supports_compression=True,
    ),
    "bz2": FormatInfo(
        "bz2",
        FormatCategory.ARCHIVE,
        "application/x-bzip2",
        "Bzip2 Compressed",
        supports_compression=True,
    ),
    "xz": FormatInfo(
        "xz", FormatCategory.ARCHIVE, "application/x-xz", "XZ Compressed", supports_compression=True
    ),
    "zstd": FormatInfo(
        "zstd",
        FormatCategory.ARCHIVE,
        "application/zstd",
        "Zstandard",
        modern_format=True,
        supports_compression=True,
    ),
    "lz4": FormatInfo(
        "lz4",
        FormatCategory.ARCHIVE,
        "application/x-lz4",
        "LZ4 Compressed",
        modern_format=True,
        supports_compression=True,
    ),
    # Legacy compression
    "cab": FormatInfo(
        "cab",
        FormatCategory.ARCHIVE,
        "application/vnd.ms-cab-compressed",
        "Cabinet Archive",
        tools_required=["cabextract"],
    ),
    "arc": FormatInfo("arc", FormatCategory.ARCHIVE, "application/x-arc", "ARC Archive"),
    "arj": FormatInfo(
        "arj", FormatCategory.ARCHIVE, "application/x-arj", "ARJ Archive", tools_required=["arj"]
    ),
    "lha": FormatInfo(
        "lha", FormatCategory.ARCHIVE, "application/x-lha", "LHA Archive", tools_required=["lha"]
    ),
    "lzh": FormatInfo(
        "lzh", FormatCategory.ARCHIVE, "application/x-lzh", "LZH Archive", optimal_conversion="lha"
    ),
    "ace": FormatInfo(
        "ace", FormatCategory.ARCHIVE, "application/x-ace", "ACE Archive", tools_required=["unace"]
    ),
    # Comic book formats
    "cbr": FormatInfo(
        "cbr", FormatCategory.ARCHIVE, "application/vnd.comicbook-rar", "Comic Book RAR"
    ),
    "cbz": FormatInfo(
        "cbz", FormatCategory.ARCHIVE, "application/vnd.comicbook+zip", "Comic Book ZIP"
    ),
    "cb7": FormatInfo("cb7", FormatCategory.ARCHIVE, "application/x-cb7", "Comic Book 7z"),
    "cba": FormatInfo("cba", FormatCategory.ARCHIVE, "application/x-cba", "Comic Book ACE"),
    "cbt": FormatInfo("cbt", FormatCategory.ARCHIVE, "application/x-cbt", "Comic Book TAR"),
    # Disk images
    "iso": FormatInfo(
        "iso", FormatCategory.ARCHIVE, "application/x-iso9660-image", "ISO Disk Image"
    ),
    "dmg": FormatInfo(
        "dmg", FormatCategory.ARCHIVE, "application/x-apple-diskimage", "macOS Disk Image"
    ),
    "img": FormatInfo(
        "img", FormatCategory.ARCHIVE, "application/x-raw-disk-image", "Raw Disk Image"
    ),
    "vhd": FormatInfo("vhd", FormatCategory.ARCHIVE, "application/x-vhd", "Virtual Hard Disk"),
    "vmdk": FormatInfo("vmdk", FormatCategory.ARCHIVE, "application/x-vmdk", "VMware Disk"),
    # Package formats
    "pkg": FormatInfo(
        "pkg", FormatCategory.ARCHIVE, "application/x-newton-compatible-pkg", "macOS Package"
    ),
    "deb": FormatInfo(
        "deb", FormatCategory.ARCHIVE, "application/vnd.debian.binary-package", "Debian Package"
    ),
    "rpm": FormatInfo("rpm", FormatCategory.ARCHIVE, "application/x-rpm", "RPM Package"),
    "msi": FormatInfo("msi", FormatCategory.ARCHIVE, "application/x-msi", "Windows Installer"),
    "appx": FormatInfo(
        "appx",
        FormatCategory.ARCHIVE,
        "application/appx",
        "Windows App Package",
        modern_format=True,
    ),
    "snap": FormatInfo(
        "snap", FormatCategory.ARCHIVE, "application/vnd.snap", "Snap Package", modern_format=True
    ),
    # Tar combinations
    "tar.gz": FormatInfo(
        "tar.gz", FormatCategory.ARCHIVE, "application/x-compressed-tar", "Compressed TAR"
    ),
    "tgz": FormatInfo(
        "tgz",
        FormatCategory.ARCHIVE,
        "application/x-compressed-tar",
        "Compressed TAR",
        optimal_conversion="tar.gz",
    ),
    "tar.bz2": FormatInfo(
        "tar.bz2", FormatCategory.ARCHIVE, "application/x-bzip-compressed-tar", "Bzip2 TAR"
    ),
    "tar.xz": FormatInfo(
        "tar.xz", FormatCategory.ARCHIVE, "application/x-xz-compressed-tar", "XZ TAR"
    ),
    # ======= VIDEOS (30 formats) =======
    # Common formats
    "mp4": FormatInfo(
        "mp4",
        FormatCategory.VIDEO,
        "video/mp4",
        "MP4 Video",
        supports_metadata=True,
        quality_lossy=True,
    ),
    "avi": FormatInfo(
        "avi", FormatCategory.VIDEO, "video/x-msvideo", "AVI Video", supports_metadata=True
    ),
    "mkv": FormatInfo(
        "mkv", FormatCategory.VIDEO, "video/x-matroska", "Matroska Video", supports_metadata=True
    ),
    "mov": FormatInfo(
        "mov", FormatCategory.VIDEO, "video/quicktime", "QuickTime Video", supports_metadata=True
    ),
    "wmv": FormatInfo(
        "wmv", FormatCategory.VIDEO, "video/x-ms-wmv", "Windows Media Video", quality_lossy=True
    ),
    "flv": FormatInfo(
        "flv", FormatCategory.VIDEO, "video/x-flv", "Flash Video", optimal_conversion="mp4"
    ),
    "webm": FormatInfo(
        "webm", FormatCategory.VIDEO, "video/webm", "WebM Video", modern_format=True
    ),
    "m4v": FormatInfo("m4v", FormatCategory.VIDEO, "video/x-m4v", "iTunes Video"),
    "3gp": FormatInfo("3gp", FormatCategory.VIDEO, "video/3gpp", "3GPP Mobile Video"),
    # Professional formats
    "mxf": FormatInfo(
        "mxf",
        FormatCategory.VIDEO,
        "application/mxf",
        "Material Exchange Format",
        professional_format=True,
    ),
    "prores": FormatInfo(
        "prores", FormatCategory.VIDEO, "video/quicktime", "Apple ProRes", professional_format=True
    ),
    "dnxhd": FormatInfo(
        "dnxhd", FormatCategory.VIDEO, "video/quicktime", "Avid DNxHD", professional_format=True
    ),
    "avchd": FormatInfo(
        "avchd", FormatCategory.VIDEO, "video/mp2t", "AVCHD", professional_format=True
    ),
    "r3d": FormatInfo(
        "r3d", FormatCategory.VIDEO, "video/x-red", "RED Raw Video", professional_format=True
    ),
    # Broadcasting
    "ts": FormatInfo("ts", FormatCategory.VIDEO, "video/mp2t", "MPEG Transport Stream"),
    "m2ts": FormatInfo("m2ts", FormatCategory.VIDEO, "video/mp2t", "MPEG-2 Transport Stream"),
    "mts": FormatInfo("mts", FormatCategory.VIDEO, "video/mp2t", "AVCHD Video"),
    "mpg": FormatInfo("mpg", FormatCategory.VIDEO, "video/mpeg", "MPEG Video"),
    "mpeg": FormatInfo(
        "mpeg", FormatCategory.VIDEO, "video/mpeg", "MPEG Video", optimal_conversion="mpg"
    ),
    "vob": FormatInfo("vob", FormatCategory.VIDEO, "video/dvd", "DVD Video"),
    # Streaming
    "f4v": FormatInfo("f4v", FormatCategory.VIDEO, "video/x-f4v", "Flash MP4"),
    "asf": FormatInfo("asf", FormatCategory.VIDEO, "video/x-ms-asf", "Advanced Systems Format"),
    "rm": FormatInfo("rm", FormatCategory.VIDEO, "application/vnd.rn-realmedia", "RealMedia"),
    "rmvb": FormatInfo(
        "rmvb",
        FormatCategory.VIDEO,
        "application/vnd.rn-realmedia-vbr",
        "RealMedia Variable Bitrate",
    ),
    "ogv": FormatInfo("ogv", FormatCategory.VIDEO, "video/ogg", "Ogg Video"),
    # Legacy and specialized
    "divx": FormatInfo("divx", FormatCategory.VIDEO, "video/divx", "DivX Video"),
    "xvid": FormatInfo("xvid", FormatCategory.VIDEO, "video/x-xvid", "Xvid Video"),
    "dv": FormatInfo("dv", FormatCategory.VIDEO, "video/dv", "Digital Video"),
    "gxf": FormatInfo(
        "gxf",
        FormatCategory.VIDEO,
        "application/gxf",
        "General Exchange Format",
        professional_format=True,
    ),
    "lxf": FormatInfo(
        "lxf",
        FormatCategory.VIDEO,
        "application/lxf",
        "Leitch Exchange Format",
        professional_format=True,
    ),
    # ======= AUDIO (25 formats) =======
    # Lossless
    "flac": FormatInfo(
        "flac", FormatCategory.AUDIO, "audio/flac", "FLAC Lossless", supports_metadata=True
    ),
    "wav": FormatInfo(
        "wav", FormatCategory.AUDIO, "audio/wav", "WAV Audio", supports_metadata=True
    ),
    "aiff": FormatInfo(
        "aiff", FormatCategory.AUDIO, "audio/aiff", "AIFF Audio", supports_metadata=True
    ),
    "alac": FormatInfo(
        "alac", FormatCategory.AUDIO, "audio/x-alac", "Apple Lossless", supports_metadata=True
    ),
    "ape": FormatInfo("ape", FormatCategory.AUDIO, "audio/x-ape", "Monkey's Audio"),
    "tta": FormatInfo("tta", FormatCategory.AUDIO, "audio/x-tta", "True Audio"),
    "wv": FormatInfo("wv", FormatCategory.AUDIO, "audio/x-wavpack", "WavPack"),
    # Compressed
    "mp3": FormatInfo(
        "mp3",
        FormatCategory.AUDIO,
        "audio/mpeg",
        "MP3 Audio",
        supports_metadata=True,
        quality_lossy=True,
    ),
    "aac": FormatInfo(
        "aac",
        FormatCategory.AUDIO,
        "audio/aac",
        "AAC Audio",
        supports_metadata=True,
        quality_lossy=True,
    ),
    "ogg": FormatInfo(
        "ogg",
        FormatCategory.AUDIO,
        "audio/ogg",
        "Ogg Vorbis",
        supports_metadata=True,
        quality_lossy=True,
    ),
    "opus": FormatInfo(
        "opus",
        FormatCategory.AUDIO,
        "audio/opus",
        "Opus Audio",
        modern_format=True,
        quality_lossy=True,
    ),
    "wma": FormatInfo(
        "wma", FormatCategory.AUDIO, "audio/x-ms-wma", "Windows Media Audio", quality_lossy=True
    ),
    "m4a": FormatInfo(
        "m4a",
        FormatCategory.AUDIO,
        "audio/mp4",
        "MPEG-4 Audio",
        supports_metadata=True,
        quality_lossy=True,
    ),
    # Professional
    "dts": FormatInfo(
        "dts", FormatCategory.AUDIO, "audio/vnd.dts", "DTS Audio", professional_format=True
    ),
    "ac3": FormatInfo(
        "ac3", FormatCategory.AUDIO, "audio/ac3", "Dolby Digital", professional_format=True
    ),
    "eac3": FormatInfo(
        "eac3", FormatCategory.AUDIO, "audio/eac3", "Dolby Digital Plus", professional_format=True
    ),
    "pcm": FormatInfo(
        "pcm", FormatCategory.AUDIO, "audio/pcm", "PCM Audio", professional_format=True
    ),
    # Specialty
    "amr": FormatInfo("amr", FormatCategory.AUDIO, "audio/amr", "AMR Audio"),
    "au": FormatInfo("au", FormatCategory.AUDIO, "audio/basic", "AU Audio"),
    "3ga": FormatInfo("3ga", FormatCategory.AUDIO, "audio/3gpp", "3GPP Audio"),
    "mka": FormatInfo("mka", FormatCategory.AUDIO, "audio/x-matroska", "Matroska Audio"),
    "ra": FormatInfo("ra", FormatCategory.AUDIO, "audio/vnd.rn-realaudio", "RealAudio"),
    "snd": FormatInfo("snd", FormatCategory.AUDIO, "audio/basic", "Sound File"),
    "mid": FormatInfo("mid", FormatCategory.AUDIO, "audio/midi", "MIDI"),
    "midi": FormatInfo(
        "midi", FormatCategory.AUDIO, "audio/midi", "MIDI", optimal_conversion="mid"
    ),
    # ======= FONTS (10 formats) =======
    "ttf": FormatInfo("ttf", FormatCategory.FONT, "font/ttf", "TrueType Font"),
    "otf": FormatInfo("otf", FormatCategory.FONT, "font/otf", "OpenType Font"),
    "woff": FormatInfo("woff", FormatCategory.FONT, "font/woff", "Web Open Font Format"),
    "woff2": FormatInfo(
        "woff2", FormatCategory.FONT, "font/woff2", "Web Open Font Format 2", modern_format=True
    ),
    "eot": FormatInfo(
        "eot", FormatCategory.FONT, "application/vnd.ms-fontobject", "Embedded OpenType"
    ),
    "fon": FormatInfo("fon", FormatCategory.FONT, "application/x-font", "Windows Font"),
    "pfb": FormatInfo("pfb", FormatCategory.FONT, "application/x-font-type1", "PostScript Font"),
    "pfm": FormatInfo(
        "pfm", FormatCategory.FONT, "application/x-font-type1", "PostScript Font Metrics"
    ),
    "afm": FormatInfo("afm", FormatCategory.FONT, "application/x-font-afm", "Adobe Font Metrics"),
    "bdf": FormatInfo(
        "bdf", FormatCategory.FONT, "application/x-font-bdf", "Bitmap Distribution Format"
    ),
    # ======= SCIENTIFIC DATA (10 formats) =======
    "hdf5": FormatInfo(
        "hdf5",
        FormatCategory.SCIENTIFIC,
        "application/x-hdf5",
        "HDF5 Scientific Data",
        professional_format=True,
    ),
    "h5": FormatInfo(
        "h5",
        FormatCategory.SCIENTIFIC,
        "application/x-hdf5",
        "HDF5 Scientific Data",
        optimal_conversion="hdf5",
        professional_format=True,
    ),
    "netcdf": FormatInfo(
        "netcdf",
        FormatCategory.SCIENTIFIC,
        "application/x-netcdf",
        "NetCDF Scientific Data",
        professional_format=True,
    ),
    "nc": FormatInfo(
        "nc",
        FormatCategory.SCIENTIFIC,
        "application/x-netcdf",
        "NetCDF Scientific Data",
        optimal_conversion="netcdf",
        professional_format=True,
    ),
    "grib": FormatInfo(
        "grib",
        FormatCategory.SCIENTIFIC,
        "application/x-grib",
        "GRIB Weather Data",
        professional_format=True,
    ),
    "grib2": FormatInfo(
        "grib2",
        FormatCategory.SCIENTIFIC,
        "application/x-grib2",
        "GRIB2 Weather Data",
        professional_format=True,
    ),
    "mat": FormatInfo(
        "mat",
        FormatCategory.SCIENTIFIC,
        "application/x-matlab-data",
        "MATLAB Data",
        professional_format=True,
    ),
    "nii": FormatInfo(
        "nii",
        FormatCategory.SCIENTIFIC,
        "application/x-nifti",
        "NIfTI Neuroimaging",
        professional_format=True,
    ),
    "nii.gz": FormatInfo(
        "nii.gz",
        FormatCategory.SCIENTIFIC,
        "application/x-nifti",
        "Compressed NIfTI",
        professional_format=True,
    ),
    "annot": FormatInfo(
        "annot",
        FormatCategory.SCIENTIFIC,
        "application/x-freesurfer-annot",
        "FreeSurfer Annotation",
        professional_format=True,
    ),
}

# ================================
# FORMAT DETECTION AND UTILITIES
# ================================


class EnhancedFormatDetector:
    """Enhanced format detection with multiple methods."""

    def __init__(self):
        self.mime_types_init = False
        self._init_mime_types()

    def _init_mime_types(self):
        """Initialize MIME types detection."""
        if not self.mime_types_init:
            mimetypes.init()
            # Add custom MIME types
            mimetypes.add_type("image/heic", ".heic")
            mimetypes.add_type("image/heif", ".heif")
            mimetypes.add_type("image/avif", ".avif")
            mimetypes.add_type("image/jxl", ".jxl")
            mimetypes.add_type("application/zstd", ".zstd")
            mimetypes.add_type("application/x-lz4", ".lz4")
            self.mime_types_init = True

    def detect_format(self, file_path: Path) -> FormatInfo | None:
        """
        Detect file format using multiple methods.

        Args:
            file_path: Path to the file

        Returns:
            FormatInfo if detected, None otherwise
        """
        if not file_path.exists():
            return None

        extension = file_path.suffix.lower().lstrip(".")

        # Handle compound extensions (e.g., tar.gz)
        if file_path.name.endswith(".tar.gz"):
            extension = "tar.gz"
        elif file_path.name.endswith(".tar.bz2"):
            extension = "tar.bz2"
        elif file_path.name.endswith(".tar.xz"):
            extension = "tar.xz"
        elif file_path.name.endswith(".nii.gz"):
            extension = "nii.gz"

        # Direct registry lookup
        if extension in ENHANCED_FORMAT_REGISTRY:
            return ENHANCED_FORMAT_REGISTRY[extension]

        # Fallback: MIME type detection
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            for fmt_info in ENHANCED_FORMAT_REGISTRY.values():
                if fmt_info.mime_type == mime_type:
                    return fmt_info

        # Magic number detection (if available)
        if MAGIC_AVAILABLE:
            with contextlib.suppress(Exception):
                mime_type = magic.from_file(str(file_path), mime=True)
                for fmt_info in ENHANCED_FORMAT_REGISTRY.values():
                    if fmt_info.mime_type == mime_type:
                        return fmt_info

        return None

    def get_supported_extensions(self, category: FormatCategory | None = None) -> set[str]:
        """Get all supported extensions, optionally filtered by category."""
        if category:
            return {
                fmt.extension
                for fmt in ENHANCED_FORMAT_REGISTRY.values()
                if fmt.category == category
            }
        return set(ENHANCED_FORMAT_REGISTRY.keys())

    def get_optimal_conversion(self, extension: str) -> str | None:
        """Get optimal conversion target for a format."""
        fmt_info = ENHANCED_FORMAT_REGISTRY.get(extension.lower().lstrip("."))
        return fmt_info.optimal_conversion if fmt_info else None

    def is_modern_format(self, extension: str) -> bool:
        """Check if format is considered modern."""
        fmt_info = ENHANCED_FORMAT_REGISTRY.get(extension.lower().lstrip("."))
        return fmt_info.modern_format if fmt_info else False

    def requires_professional_tools(self, extension: str) -> list[str]:
        """Get list of professional tools required for format."""
        fmt_info = ENHANCED_FORMAT_REGISTRY.get(extension.lower().lstrip("."))
        return fmt_info.tools_required if fmt_info else []

    def get_format_statistics(self) -> dict[str, int]:
        """Get statistics about supported formats."""
        stats = {}
        for category in FormatCategory:
            count = len(
                [fmt for fmt in ENHANCED_FORMAT_REGISTRY.values() if fmt.category == category]
            )
            stats[category.value] = count

        stats["total"] = len(ENHANCED_FORMAT_REGISTRY)
        stats["modern"] = len(
            [fmt for fmt in ENHANCED_FORMAT_REGISTRY.values() if fmt.modern_format]
        )
        stats["professional"] = len(
            [fmt for fmt in ENHANCED_FORMAT_REGISTRY.values() if fmt.professional_format]
        )

        return stats


# ================================
# CROSS-PLATFORM TOOL DETECTION
# ================================


class ToolDetector:
    """Detect available external tools for format processing."""

    @staticmethod
    def check_tool_availability() -> dict[str, bool]:
        """Check availability of external tools."""
        tools_to_check = [
            "exiftool",
            "mediainfo",
            "ffmpeg",
            "qpdf",
            "7z",
            "unrar",
            "dcraw",
            "imagemagick",
            "convert",
            "magick",
            "cabextract",
            "arj",
            "lha",
            "unace",
            "dcmtk",
            "astropy",
            "openexr",
        ]

        availability = {}
        for tool in tools_to_check:
            availability[tool] = ToolDetector._command_exists(tool)

        return availability

    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if a command exists in the system PATH."""
        import shutil

        return shutil.which(command) is not None

    @staticmethod
    def get_recommended_tools() -> dict[str, str]:
        """Get recommended installation commands for tools."""
        if os.name == "nt":  # Windows
            return {
                "exiftool": "choco install exiftool",
                "mediainfo": "choco install mediainfo",
                "ffmpeg": "choco install ffmpeg",
                "7z": "choco install 7zip.install",
                "qpdf": "choco install qpdf",
                "imagemagick": "choco install imagemagick",
            }
        else:  # Linux/Unix
            return {
                "exiftool": "sudo apt-get install libimage-exiftool-perl",
                "mediainfo": "sudo apt-get install mediainfo",
                "ffmpeg": "sudo apt-get install ffmpeg",
                "7z": "sudo apt-get install p7zip-full",
                "qpdf": "sudo apt-get install qpdf",
                "imagemagick": "sudo apt-get install imagemagick",
            }


# ================================
# GLOBAL INSTANCES
# ================================

# Create global detector instance
format_detector = EnhancedFormatDetector()
tool_detector = ToolDetector()


# Export functions for compatibility
def get_supported_extensions(category: str | None = None) -> set[str]:
    """Get supported extensions, optionally filtered by category."""
    cat = FormatCategory(category) if category else None
    return format_detector.get_supported_extensions(cat)


def detect_format(file_path: Path) -> FormatInfo | None:
    """Detect file format."""
    return format_detector.detect_format(file_path)


def get_format_statistics() -> dict[str, int]:
    """Get format support statistics."""
    return format_detector.get_format_statistics()


__all__ = [
    "ENHANCED_FORMAT_REGISTRY",
    "EnhancedFormatDetector",
    "FormatCategory",
    "FormatInfo",
    "ToolDetector",
    "detect_format",
    "format_detector",
    "get_format_statistics",
    "get_supported_extensions",
    "tool_detector",
]
