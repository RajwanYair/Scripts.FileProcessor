#!/usr/bin/env python3
"""
Feature Registry System for Enhanced File Processing Suite v5.0
==============================================================

Central registry for all file processing features with metadata,
categories, and execution management.
"""

from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import Any

logger = logging.getLogger(__name__)


class FeatureCategory(Enum):
    """Feature categories for organization."""

    FILE_ORGANIZATION = "File Organization"
    FILE_CLEANUP = "File Cleanup"
    CONTENT_PROCESSING = "Content Processing"
    SECURITY_PRIVACY = "Security & Privacy"
    IMAGE_PROCESSING = "Image Processing"
    DOCUMENT_PROCESSING = "Document Processing"
    MEDIA_PROCESSING = "Media Processing"
    ARCHIVE_MANAGEMENT = "Archive Management"
    ANALYSIS_REPORTS = "Analysis & Reports"
    AUTOMATION_WORKFLOWS = "Automation & Workflows"


class FeatureComplexity(Enum):
    """Feature complexity levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class FeatureMetadata:
    """Metadata for a file processing feature."""

    id: str  # Internal ID (e.g., "smart_organizer")
    name: str  # User-friendly name (e.g., "Smart Organizer")
    description: str  # Short description
    category: FeatureCategory
    icon: str  # Emoji or icon identifier
    complexity: FeatureComplexity
    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

    # Capabilities
    supports_preview: bool = True
    supports_undo: bool = False
    supports_batch: bool = True
    is_destructive: bool = False
    requires_dest: bool = False

    # Documentation
    long_description: str = ""
    examples: list[str] = field(default_factory=list)
    tips: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Technical
    required_modules: list[str] = field(default_factory=list)
    optional_modules: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=lambda: ["windows", "linux", "macos", "wsl"])

    # Usage statistics (can be tracked)
    usage_count: int = 0
    is_favorite: bool = False
    is_new: bool = False  # Badge for new features


class FeatureRegistry:
    """Central registry for all file processing features."""

    def __init__(self):
        self.features: dict[str, FeatureMetadata] = {}
        self.categories: dict[FeatureCategory, list[str]] = {}
        self._initialize_features()

    def _initialize_features(self):
        """Initialize all available features."""

        # Category 1: File Organization
        self.register_feature(
            FeatureMetadata(
                id="smart_organizer",
                name="Smart Organizer",
                description="Automatically organize files by date, type, or custom rules",
                category=FeatureCategory.FILE_ORGANIZATION,
                icon="📂",
                complexity=FeatureComplexity.BEGINNER,
                tags=["organize", "auto", "date", "type"],
                keywords=["organize", "sort", "arrange", "categorize", "tidy"],
                long_description="""
Smart Organizer automatically organizes your files into logical folder structures:
• Organize by date (daily, monthly, yearly)
• Organize by file type (documents, images, videos, etc.)
• Custom folder rules based on filename patterns
• Tag-based organization
• Smart suggestions for messy folders
            """,
                examples=[
                    "Organize downloads by file type",
                    "Sort photos by date taken",
                    "Group documents by project",
                ],
                tips=[
                    "Use dry-run mode first to preview changes",
                    "Create custom rules for your workflow",
                ],
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="batch_renamer",
                name="Batch Renamer",
                description="Rename multiple files with patterns, numbering, and rules",
                category=FeatureCategory.FILE_ORGANIZATION,
                icon="✏️",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["rename", "batch", "pattern", "sequential"],
                keywords=["rename", "name", "change", "title", "sequential", "number"],
                supports_undo=True,
                long_description="""
Powerful batch renaming with multiple patterns and rules:
• Pattern-based renaming with variables
• Sequential numbering (001, 002, etc.)
• Date/time stamps in filenames
• Case conversion (UPPER, lower, Title Case)
• Find & replace with regex support
• Preview before applying
            """,
                examples=[
                    "Rename photos: Photo_001.jpg, Photo_002.jpg",
                    "Add date prefix: 2025-01-15_document.pdf",
                    "Find 'IMG' replace with 'Photo'",
                ],
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="series_manager",
                name="Series Manager",
                description="Detect and organize series (volumes, episodes, parts)",
                category=FeatureCategory.FILE_ORGANIZATION,
                icon="📚",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["series", "volumes", "episodes", "collection"],
                keywords=["series", "volume", "episode", "season", "part", "chapter"],
                long_description="""
Automatically detect and organize file series:
• Auto-detect volumes (vol.1, vol.2, v01, v02)
• Organize episodes (S01E01, S01E02)
• Find missing files in series
• Extract series metadata
• Create series folders automatically
            """,
                examples=[
                    "Organize comic volumes into series folders",
                    "Detect missing episodes in TV series",
                    "Group book chapters together",
                ],
            )
        )

        # Category 2: File Cleanup
        self.register_feature(
            FeatureMetadata(
                id="duplicate_finder",
                name="Duplicate Finder",
                description="Find and remove duplicate files with visual comparison",
                category=FeatureCategory.FILE_CLEANUP,
                icon="🔄",
                complexity=FeatureComplexity.BEGINNER,
                tags=["duplicate", "same", "identical", "copy"],
                keywords=["duplicate", "same", "identical", "copy", "redundant", "clone"],
                is_destructive=True,
                long_description="""
Find and manage duplicate files intelligently:
• Hash-based comparison (MD5, SHA-256)
• Visual comparison for images
• Keep best quality automatically
• Move to folder or delete
• Adjustable similarity threshold
• Handle similar but not identical files
            """,
                examples=[
                    "Find duplicate photos and keep highest resolution",
                    "Remove duplicate downloads",
                    "Find similar images (not exactly same)",
                ],
                warnings=["Deleting duplicates is permanent - use dry-run first!"],
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="file_sanitizer",
                name="File Sanitizer",
                description="Clean filenames and fix illegal characters",
                category=FeatureCategory.FILE_CLEANUP,
                icon="🧹",
                complexity=FeatureComplexity.BEGINNER,
                tags=["sanitize", "clean", "fix", "illegal"],
                keywords=["sanitize", "clean", "fix", "illegal", "characters", "unicode"],
                supports_undo=True,
                long_description="""
Clean and standardize filenames:
• Remove illegal characters (< > : " / \\ | ? *)
• Fix Unicode issues
• Normalize spaces and underscores
• Remove leading/trailing dots
• Handle special characters
• Cross-platform filename compatibility
            """,
                examples=[
                    'Fix "bad<name>.txt" to "bad_name.txt"',
                    "Remove Unicode characters for compatibility",
                    "Standardize spacing in filenames",
                ],
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="extension_manager",
                name="Extension Manager",
                description="Fix, standardize, and manage file extensions",
                category=FeatureCategory.FILE_CLEANUP,
                icon="📝",
                complexity=FeatureComplexity.BEGINNER,
                tags=["extension", "ext", "format"],
                keywords=["extension", "ext", "suffix", "format", "type"],
                long_description="""
Manage and standardize file extensions:
• Fix wrong extensions based on content
• Standardize extensions (.jpeg → .jpg)
• Bulk extension change
• Remove duplicate extensions (.pdf.pdf)
• Add missing extensions
• Case normalization (.JPG → .jpg)
            """,
                examples=[
                    "Change all .jpeg to .jpg",
                    "Fix misnamed files (image.txt that's actually .jpg)",
                    "Normalize all extensions to lowercase",
                ],
            )
        )

        # Category 3: Content Processing
        self.register_feature(
            FeatureMetadata(
                id="format_converter",
                name="Format Converter",
                description="Convert files between different formats",
                category=FeatureCategory.CONTENT_PROCESSING,
                icon="🔄",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["convert", "transform", "format"],
                keywords=["convert", "transform", "change", "format", "export"],
                requires_dest=True,
                long_description="""
Convert files between formats:
• Image conversion (PNG, JPG, WebP, etc.)
• Document conversion (PDF, DOCX, TXT)
• Audio/Video conversion
• Archive conversion (ZIP, RAR, 7Z)
• Quality and settings control
• Batch processing
            """,
                examples=[
                    "Convert PNG to JPG (smaller size)",
                    "Convert Word documents to PDF",
                    "Convert MP3 to WAV",
                ],
                required_modules=["PIL", "pdf2image"],
                optional_modules=["ffmpeg", "imagemagick"],
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="metadata_editor",
                name="Metadata Editor",
                description="View, edit, and manage file metadata",
                category=FeatureCategory.CONTENT_PROCESSING,
                icon="📊",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["metadata", "exif", "info", "properties"],
                keywords=["metadata", "exif", "properties", "info", "tags", "attributes"],
                long_description="""
Comprehensive metadata management:
• View all metadata (EXIF, XMP, IPTC)
• Edit metadata fields
• Remove metadata for privacy
• Copy metadata between files
• Batch metadata operations
• Extract metadata to CSV/JSON
            """,
                examples=[
                    "View camera settings from photos",
                    "Remove location data from images",
                    "Copy metadata from one photo to others",
                ],
                required_modules=["PIL", "exifread"],
                optional_modules=["exiftool"],
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="format_detective",
                name="Format Detective",
                description="Identify file types and detect misnamed files",
                category=FeatureCategory.CONTENT_PROCESSING,
                icon="🔍",
                complexity=FeatureComplexity.BEGINNER,
                tags=["detect", "identify", "format", "type"],
                keywords=["detect", "identify", "find", "discover", "determine", "type"],
                long_description="""
Intelligent file format detection:
• Identify real file type by content (not extension)
• Detect misnamed files
• Fix corrupted headers
• Support for 200+ file formats
• Generate format statistics
• Batch format validation
            """,
                examples=[
                    "Find .txt files that are actually .pdf",
                    "Identify unknown file types",
                    "Validate archive integrity",
                ],
            )
        )

        # Category 4: Security & Privacy
        self.register_feature(
            FeatureMetadata(
                id="password_manager",
                name="Password Manager & Scanner",
                description="Scan for password-protected files and crack passwords with intelligent brute-force",
                category=FeatureCategory.SECURITY_PRIVACY,
                icon="🔐",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=[
                    "password",
                    "protected",
                    "encrypted",
                    "unlock",
                    "scan",
                    "bruteforce",
                    "crack",
                ],
                keywords=[
                    "password",
                    "protected",
                    "encrypted",
                    "locked",
                    "unlock",
                    "decrypt",
                    "scan",
                    "detect",
                    "crack",
                    "bruteforce",
                    "brute-force",
                ],
                long_description="""
Advanced password detection and cracking system:

**Detection Features:**
• Scan entire directories for password-protected files
• Detect protection on PDF, ZIP, RAR, 7Z, Office documents
• Identify encryption method for each file
• Batch scanning with progress tracking

**Password Cracking:**
• Test customer-provided passwords first
• Try 1000+ common passwords automatically
• Numeric brute-force (4-8 digits)
• Alphabetic brute-force (4-6 characters)
• Alphanumeric combinations
• Dictionary attack mode
• Parallel processing for multiple files

**Smart Features:**
• Custom password lists per file
• Attack mode prioritization
• Progress callbacks and statistics
• Success rate tracking
• Password attempt history
            """,
                examples=[
                    "Scan Downloads folder for password-protected PDFs",
                    "Test custom password list on ZIP archive",
                    "Brute-force 4-digit numeric password on PDF",
                    "Try 100 most common passwords on all protected files",
                    "Crack multiple files in parallel with different passwords",
                ],
                tips=[
                    "Always try custom/known passwords first before brute-force",
                    "Numeric brute-force is fast (4-8 digits)",
                    "Alpha brute-force can take hours - use with caution",
                    "Common password mode often succeeds on weak passwords",
                    "Use parallel mode for multiple files to save time",
                ],
                warnings=[
                    "Password cracking may violate security policies or laws",
                    "Only use on files you own or have permission to access",
                    "Brute-force attacks can take very long time",
                    "Alpha/alphanumeric brute-force is exponentially slow",
                    "Some encryption methods are effectively uncrackable",
                ],
                required_modules=["PyPDF2"],
                optional_modules=["pikepdf", "py7zr", "rarfile"],
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="privacy_cleaner",
                name="Privacy Cleaner",
                description="Remove metadata and personal information from files",
                category=FeatureCategory.SECURITY_PRIVACY,
                icon="🛡️",
                complexity=FeatureComplexity.BEGINNER,
                tags=["privacy", "clean", "metadata", "anonymous"],
                keywords=["privacy", "clean", "remove", "metadata", "exif", "anonymous", "strip"],
                is_destructive=True,
                long_description="""
Protect your privacy by removing metadata:
• Remove EXIF data from photos
• Strip location information
• Remove author/creator info
• Clean document properties
• Anonymize filenames
• Batch privacy cleaning
            """,
                examples=[
                    "Remove GPS location from photos before sharing",
                    "Strip author info from documents",
                    "Remove all metadata from images",
                ],
                warnings=["Metadata removal is permanent!"],
                is_new=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="file_encryptor",
                name="File Encryptor",
                description="Encrypt and decrypt files for security",
                category=FeatureCategory.SECURITY_PRIVACY,
                icon="🔒",
                complexity=FeatureComplexity.ADVANCED,
                tags=["encrypt", "decrypt", "secure", "protection"],
                keywords=["encrypt", "decrypt", "secure", "protect", "lock", "unlock"],
                is_destructive=True,
                long_description="""
Secure file encryption and decryption:
• AES-256 encryption
• Password-based encryption
• Batch encryption/decryption
• Secure file deletion
• Create encrypted archives
            """,
                examples=[
                    "Encrypt sensitive documents",
                    "Decrypt files with password",
                    "Create encrypted ZIP archives",
                ],
                warnings=["Lost passwords cannot be recovered!", "Keep backup of encryption keys"],
                required_modules=["cryptography"],
                is_new=True,
            )
        )

        # Category 5: Image Processing
        self.register_feature(
            FeatureMetadata(
                id="image_optimizer",
                name="Image Optimizer",
                description="Resize, compress, and optimize images",
                category=FeatureCategory.IMAGE_PROCESSING,
                icon="🖼️",
                complexity=FeatureComplexity.BEGINNER,
                tags=["image", "resize", "compress", "optimize"],
                keywords=["image", "photo", "picture", "resize", "compress", "optimize", "reduce"],
                requires_dest=True,
                long_description="""
Optimize images for size and quality:
• Resize images (pixels or percentage)
• Compress with quality control
• Convert formats for better compression
• Batch watermarking
• Remove image metadata
• Progressive JPEG conversion
            """,
                examples=[
                    "Resize images to 1920x1080",
                    "Compress images to 80% quality",
                    "Add watermark to all photos",
                ],
                required_modules=["PIL"],
                is_new=True,
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="photo_organizer",
                name="Photo Organizer",
                description="Organize photos by date, location, and more",
                category=FeatureCategory.IMAGE_PROCESSING,
                icon="📸",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["photo", "organize", "exif", "date"],
                keywords=["photo", "image", "picture", "organize", "sort", "date", "location"],
                long_description="""
Intelligent photo organization:
• Sort by date taken (EXIF data)
• Sort by location (GPS coordinates)
• Face detection grouping
• Duplicate photo finder (visual similarity)
• Create year/month folder structure
• Handle RAW + JPG pairs
            """,
                examples=[
                    "Organize 10,000 photos by year and month",
                    "Group photos by location",
                    "Find duplicate/similar photos",
                ],
                required_modules=["PIL", "exifread"],
                optional_modules=["face_recognition"],
                is_new=True,
            )
        )

        # Category 6: Document Processing
        self.register_feature(
            FeatureMetadata(
                id="pdf_tools",
                name="PDF Tools",
                description="Merge, split, and manipulate PDF files",
                category=FeatureCategory.DOCUMENT_PROCESSING,
                icon="📄",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["pdf", "merge", "split", "combine"],
                keywords=["pdf", "merge", "split", "combine", "extract", "pages"],
                requires_dest=True,
                long_description="""
Comprehensive PDF manipulation:
• Merge multiple PDFs into one
• Split PDF into separate files
• Extract specific pages
• PDF to images conversion
• Compress PDFs
• Add/Remove passwords
• Rotate pages
            """,
                examples=[
                    "Merge all PDFs in folder",
                    "Split PDF into individual pages",
                    "Extract pages 1-10 from PDF",
                ],
                required_modules=["PyPDF2"],
                optional_modules=["pikepdf", "pdf2image"],
                is_new=True,
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="text_extractor",
                name="Text Extractor",
                description="Extract text from images and documents (OCR)",
                category=FeatureCategory.DOCUMENT_PROCESSING,
                icon="📝",
                complexity=FeatureComplexity.ADVANCED,
                tags=["ocr", "text", "extract", "scan"],
                keywords=["ocr", "text", "extract", "read", "scan", "recognize"],
                long_description="""
Extract text from various sources:
• OCR on images (Tesseract)
• Extract text from PDFs
• Batch text extraction
• Language detection
• Export to TXT/CSV/JSON
• Searchable PDF creation
            """,
                examples=[
                    "Extract text from scanned documents",
                    "Convert image-based PDF to searchable PDF",
                    "Batch OCR on receipts",
                ],
                required_modules=["pytesseract", "PIL"],
                optional_modules=["pdf2image"],
                is_new=True,
            )
        )

        # Category 7: Media Processing
        self.register_feature(
            FeatureMetadata(
                id="video_tools",
                name="Video Tools",
                description="Process videos: extract audio, create thumbnails, convert",
                category=FeatureCategory.MEDIA_PROCESSING,
                icon="🎬",
                complexity=FeatureComplexity.ADVANCED,
                tags=["video", "audio", "thumbnail", "convert"],
                keywords=["video", "movie", "film", "convert", "extract", "thumbnail"],
                requires_dest=True,
                long_description="""
Video processing capabilities:
• Extract audio from videos
• Create video thumbnails
• Convert video formats
• Compress videos
• Extract frames at intervals
• Trim/Cut videos
• Add watermarks
            """,
                examples=[
                    "Extract MP3 audio from MP4 videos",
                    "Create thumbnails for all videos",
                    "Convert AVI to MP4",
                ],
                required_modules=["ffmpeg-python"],
                optional_modules=["moviepy"],
                is_new=True,
            )
        )

        # Category 8: Archive Management
        self.register_feature(
            FeatureMetadata(
                id="archive_manager",
                name="Archive Manager",
                description="Extract, create, and convert archive files",
                category=FeatureCategory.ARCHIVE_MANAGEMENT,
                icon="📦",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["archive", "zip", "rar", "7z", "extract"],
                keywords=["archive", "zip", "rar", "7z", "extract", "compress", "unzip"],
                long_description="""
Complete archive management:
• Extract archives (ZIP, RAR, 7Z, TAR, GZ)
• Create archives with compression
• Convert between formats
• Test archive integrity
• Password operations
• Batch extraction/creation
            """,
                examples=[
                    "Extract all ZIP files in folder",
                    "Convert RAR to ZIP",
                    "Create 7Z archive with maximum compression",
                ],
                required_modules=["zipfile", "tarfile"],
                optional_modules=["py7zr", "rarfile"],
            )
        )

        # Category 9: Analysis & Reports
        self.register_feature(
            FeatureMetadata(
                id="file_analyzer",
                name="File Analyzer",
                description="Analyze disk space, file types, and generate statistics",
                category=FeatureCategory.ANALYSIS_REPORTS,
                icon="📊",
                complexity=FeatureComplexity.BEGINNER,
                tags=["analyze", "statistics", "report", "disk"],
                keywords=["analyze", "analysis", "statistics", "report", "disk", "space", "usage"],
                long_description="""
Comprehensive file analysis:
• Disk space analysis with charts
• File type statistics
• Duplicate analysis
• Extension distribution
• Size distribution
• Largest files report
• File age analysis
            """,
                examples=[
                    "Find what's taking up disk space",
                    "Generate file type report",
                    "Find largest files",
                ],
                is_new=True,
                is_favorite=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="similarity_finder",
                name="Similarity Finder",
                description="Find similar images, documents, and files",
                category=FeatureCategory.ANALYSIS_REPORTS,
                icon="🔍",
                complexity=FeatureComplexity.INTERMEDIATE,
                tags=["similar", "similarity", "compare", "match"],
                keywords=["similar", "similarity", "compare", "match", "alike", "resembling"],
                long_description="""
Find similar files intelligently:
• Find similar images (perceptual hashing)
• Find similar documents (content analysis)
• Adjustable similarity threshold
• Visual comparison interface
• Group similar files
• Handle near-duplicates
            """,
                examples=[
                    "Find similar photos (different sizes/crops)",
                    "Find documents with similar content",
                    "Group similar images together",
                ],
                required_modules=["PIL"],
                optional_modules=["imagehash"],
                is_new=True,
            )
        )

        # Category 10: Automation & Workflows
        self.register_feature(
            FeatureMetadata(
                id="workflow_builder",
                name="Workflow Builder",
                description="Create automated workflows and chains of operations",
                category=FeatureCategory.AUTOMATION_WORKFLOWS,
                icon="🤖",
                complexity=FeatureComplexity.ADVANCED,
                tags=["workflow", "automation", "chain", "sequence"],
                keywords=["workflow", "automation", "chain", "sequence", "pipeline", "automate"],
                long_description="""
Build custom automated workflows:
• Chain multiple operations
• Conditional logic (if-then-else)
• Save and load workflows
• Schedule workflows
• Share workflows
• Variable support
            """,
                examples=[
                    "Workflow: Organize → Rename → Optimize",
                    "If image, then compress, else archive",
                    "Daily workflow at 2 AM",
                ],
                is_new=True,
            )
        )

        self.register_feature(
            FeatureMetadata(
                id="watch_folders",
                name="Watch Folders",
                description="Monitor folders and auto-process new files",
                category=FeatureCategory.AUTOMATION_WORKFLOWS,
                icon="👁️",
                complexity=FeatureComplexity.ADVANCED,
                tags=["watch", "monitor", "automatic", "auto"],
                keywords=["watch", "monitor", "automatic", "auto", "observe", "detect"],
                long_description="""
Automated folder monitoring:
• Monitor folders for new files
• Auto-process based on rules
• Move/Copy/Rename automatically
• Notification system
• Multi-folder monitoring
• Filter by file type/size
            """,
                examples=[
                    "Watch Downloads → auto-organize new files",
                    "Monitor camera folder → auto-backup photos",
                    "Watch scan folder → auto-OCR documents",
                ],
                is_new=True,
            )
        )

    def register_feature(self, feature: FeatureMetadata):
        """Register a new feature."""
        self.features[feature.id] = feature

        # Add to category
        if feature.category not in self.categories:
            self.categories[feature.category] = []
        self.categories[feature.category].append(feature.id)

        logger.debug(f"Registered feature: {feature.name} ({feature.id})")

    def get_feature(self, feature_id: str) -> FeatureMetadata | None:
        """Get feature by ID."""
        return self.features.get(feature_id)

    def get_features_by_category(self, category: FeatureCategory) -> list[FeatureMetadata]:
        """Get all features in a category."""
        feature_ids = self.categories.get(category, [])
        return [self.features[fid] for fid in feature_ids]

    def get_all_categories(self) -> list[FeatureCategory]:
        """Get all categories."""
        return list(self.categories.keys())

    def search_features(self, query: str) -> list[FeatureMetadata]:
        """Search features by query string."""
        query = query.lower()
        results = []

        for feature in self.features.values():
            # Search in name, description, keywords, tags
            if (
                query in feature.name.lower()
                or query in feature.description.lower()
                or any(query in kw.lower() for kw in feature.keywords)
                or any(query in tag.lower() for tag in feature.tags)
            ):
                results.append(feature)

        return results

    def get_favorites(self) -> list[FeatureMetadata]:
        """Get all favorite features."""
        return [f for f in self.features.values() if f.is_favorite]

    def get_new_features(self) -> list[FeatureMetadata]:
        """Get all new features."""
        return [f for f in self.features.values() if f.is_new]

    def get_beginner_features(self) -> list[FeatureMetadata]:
        """Get beginner-friendly features."""
        return [f for f in self.features.values() if f.complexity == FeatureComplexity.BEGINNER]

    def increment_usage(self, feature_id: str):
        """Increment usage count for a feature."""
        if feature_id in self.features:
            self.features[feature_id].usage_count += 1

    def toggle_favorite(self, feature_id: str):
        """Toggle favorite status for a feature."""
        if feature_id in self.features:
            self.features[feature_id].is_favorite = not self.features[feature_id].is_favorite

    def get_feature_count(self) -> int:
        """Get total number of features."""
        return len(self.features)

    def get_statistics(self) -> dict[str, Any]:
        """Get feature statistics."""
        return {
            "total_features": len(self.features),
            "categories": len(self.categories),
            "favorites": len(self.get_favorites()),
            "new_features": len(self.get_new_features()),
            "by_category": {
                cat.value: len(self.get_features_by_category(cat)) for cat in self.categories
            },
            "by_complexity": {
                "beginner": len(
                    [
                        f
                        for f in self.features.values()
                        if f.complexity == FeatureComplexity.BEGINNER
                    ]
                ),
                "intermediate": len(
                    [
                        f
                        for f in self.features.values()
                        if f.complexity == FeatureComplexity.INTERMEDIATE
                    ]
                ),
                "advanced": len(
                    [
                        f
                        for f in self.features.values()
                        if f.complexity == FeatureComplexity.ADVANCED
                    ]
                ),
                "expert": len(
                    [f for f in self.features.values() if f.complexity == FeatureComplexity.EXPERT]
                ),
            },
        }


# Global registry instance
_registry = None


def get_registry() -> FeatureRegistry:
    """Get the global feature registry instance."""
    global _registry
    if _registry is None:
        _registry = FeatureRegistry()
    return _registry


# Convenience functions
def get_all_features() -> list[FeatureMetadata]:
    """Get all registered features."""
    return list(get_registry().features.values())


def get_feature_by_id(feature_id: str) -> FeatureMetadata | None:
    """Get a specific feature by ID."""
    return get_registry().get_feature(feature_id)


def search_features(query: str) -> list[FeatureMetadata]:
    """Search for features."""
    return get_registry().search_features(query)


if __name__ == "__main__":
    # Demo/Test
    registry = get_registry()

    print("Feature Registry Statistics")
    print("=" * 50)
    stats = registry.get_statistics()
    print(f"Total Features: {stats['total_features']}")
    print(f"Categories: {stats['categories']}")
    print(f"Favorites: {stats['favorites']}")
    print(f"New Features: {stats['new_features']}")

    print("\nFeatures by Category:")
    for cat, count in stats["by_category"].items():
        print(f"  {cat}: {count} features")

    print("\nFeatures by Complexity:")
    for level, count in stats["by_complexity"].items():
        print(f"  {level.title()}: {count} features")

    print("\nFavorite Features:")
    for feature in registry.get_favorites():
        print(f"  {feature.icon} {feature.name}")

    print("\nNew Features:")
    for feature in registry.get_new_features():
        print(f"  {feature.icon} {feature.name}")
