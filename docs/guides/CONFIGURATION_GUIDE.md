# Configuration Guide - Enhanced File Processing Suite v5.0

## 📋 Overview

The Enhanced File Processing Suite v5.0 uses a comprehensive YAML configuration system that allows you to customize every aspect of file processing. This guide explains all configuration options and provides examples for common use cases.

## 🗃️ Configuration File Location

**Primary Configuration**: `file_processing_suite_config.yaml`  
**Backup/Templates**: `./config/` directory (created automatically)

## 🎯 Quick Configuration Examples

### Example 1: High-Performance Setup
```yaml
performance:
  enable_gpu: true
  max_workers: "auto"
  memory_limit_gb: 32
  gpu_batch_size: 2000

formats:
  images:
    default_output_format: "webp"
    webp_quality: 95
    preserve_metadata: true
```

### Example 2: Conservative Processing
```yaml
performance:
  enable_gpu: false
  max_workers: 2
  memory_limit_gb: 4

security:
  create_backup_before_processing: true
  verify_file_integrity: true
  quarantine_corrupted_files: true
```

### Example 3: Batch Automation
```yaml
general:
  log_level: "INFO"
  default_source_directory: "./batch_input"
  default_output_directory: "./batch_output"

organization:
  create_date_folders: true
  duplicate_action: "rename"
  enable_series_detection: true
```

## 📖 Complete Configuration Reference

### 🔧 General Settings

```yaml
general:
  application_name: "Enhanced File Processing Suite"
  version: "5.0.0"
  release_date: "2025-09-04"
  
  # Directory Settings
  default_source_directory: "./input"      # Where to look for files
  default_output_directory: "./output"     # Where to save processed files
  
  # Logging Configuration
  log_level: "INFO"                        # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file: "file_processing_suite.log"    # Log file name
  log_max_size_mb: 50                      # Max log file size before rotation
  log_backup_count: 5                      # Number of backup log files to keep
```

**Options Explained:**
- `log_level`: Controls verbosity of logging
  - `DEBUG`: Very detailed information for troubleshooting
  - `INFO`: General information about processing
  - `WARNING`: Important issues that don't stop processing
  - `ERROR`: Serious problems that may affect results
  - `CRITICAL`: Fatal errors that stop processing

### ⚡ Performance Configuration

```yaml
performance:
  # CPU and Threading
  max_workers: "auto"                      # "auto" = CPU count, or specific number
  io_workers: 4                            # Separate workers for file I/O
  
  # GPU Acceleration
  enable_gpu: true                         # Enable GPU processing when available
  gpu_backend: "auto"                      # "auto", "cupy", "cuda", "disabled"
  gpu_memory_limit_gb: 8                   # Max GPU memory to use
  gpu_batch_size: 1000                     # Files per GPU batch
  
  # Memory Management
  memory_limit_gb: 16                      # Max system memory to use
  enable_memory_monitoring: true           # Monitor and prevent memory overload
  
  # Performance Profiling
  enable_profiling: false                  # Enable detailed performance tracking
  profile_output_dir: "./profiles"         # Where to save profile data
```

**Performance Tuning Tips:**
- **max_workers**: Start with "auto", reduce if system becomes unresponsive
- **gpu_batch_size**: Increase for large datasets, decrease if GPU memory errors occur
- **memory_limit_gb**: Set to 75% of total system RAM for optimal performance

### 🖼️ Image Format Configuration

```yaml
formats:
  images:
    # Supported Input Formats (200+ total)
    supported_input: 
      - "jpg"        # Standard JPEG
      - "png"        # Portable Network Graphics
      - "webp"       # Modern web format
      - "heic"       # Apple format
      - "avif"       # Next-gen format
      - "raw"        # Camera RAW
      - "cr2"        # Canon RAW
      - "nef"        # Nikon RAW
      - "arw"        # Sony RAW
      # ... and many more
    
    # Output Settings
    default_output_format: "webp"           # Format for conversions
    
    # Quality Settings
    jpeg_quality: 95                        # JPEG quality (1-100)
    webp_quality: 90                        # WebP quality (1-100)
    png_compression: 6                      # PNG compression (0-9)
    
    # Processing Options
    preserve_metadata: true                 # Keep EXIF data
    auto_rotate: true                       # Auto-rotate based on EXIF
    resize_large_images: false              # Auto-resize large images
    max_image_dimension: 4096               # Max width/height if resizing
```

**Image Quality Guidelines:**
- **JPEG Quality**: 95+ for professional, 85-90 for web, 70-80 for storage
- **WebP Quality**: Generally 10-15 points lower than JPEG for same quality
- **PNG Compression**: Higher values = smaller files but slower processing

### 📄 Document Processing

```yaml
formats:
  documents:
    supported_input:
      - "pdf"        # Portable Document Format
      - "epub"       # E-book format
      - "mobi"       # Kindle format
      - "doc"        # Microsoft Word (legacy)
      - "docx"       # Microsoft Word (modern)
      - "odt"        # OpenDocument Text
    
    default_output_format: "pdf"            # Convert to PDF by default
    
    # PDF Settings
    pdf_compression: true                   # Compress PDF output
    pdf_quality: "high"                     # "low", "medium", "high", "maximum"
    preserve_bookmarks: true                # Keep PDF bookmarks
```

### 🗜️ Archive Configuration

```yaml
formats:
  archives:
    supported_input:
      - "zip"        # Standard ZIP
      - "rar"        # WinRAR format
      - "7z"         # 7-Zip format
      - "tar"        # TAR archive
      - "cbz"        # Comic book ZIP
      - "cbr"        # Comic book RAR
    
    default_output_format: "zip"            # Convert archives to ZIP
    compression_level: 6                    # Compression level (0-9)
```

### 📁 File Organization

```yaml
organization:
  # Directory Structure
  create_date_folders: true               # Create YYYY/MM folder structure
  date_folder_format: "YYYY/MM"          # "YYYY", "YYYY/MM", "YYYY/MM/DD"
  
  # File Naming
  preserve_original_names: true          # Keep original filenames
  normalize_filenames: true              # Clean up special characters
  remove_special_characters: true       # Remove problematic characters
  max_filename_length: 255               # Maximum filename length
  
  # Duplicate Handling
  duplicate_detection: true              # Enable duplicate detection
  duplicate_action: "rename"             # "skip", "rename", "replace"
  hash_algorithm: "md5"                  # "md5", "sha1", "sha256"
  
  # Series and Grouping
  enable_series_detection: true          # Group related files
  similarity_threshold: 0.85             # Similarity threshold (0.0-1.0)
  min_group_size: 2                      # Minimum files to form a group
```

**Organization Strategies:**
- **Date-based**: Great for photos and time-sensitive documents
- **Type-based**: Organize by file type (images/, documents/, etc.)
- **Hybrid**: Combine date and type organization

### 🎨 GUI Configuration

```yaml
gui:
  # Window Settings
  window_title: "Enhanced File Processing Suite v5.0"
  window_width: 1200                     # Initial window width
  window_height: 800                     # Initial window height
  resizable: true                        # Allow window resizing
  
  # Interface Options
  theme: "system"                        # "light", "dark", "system"
  show_advanced_options: true           # Show advanced settings
  show_progress_details: true           # Show detailed progress info
  enable_real_time_preview: true        # Preview results in real-time
  
  # Default Tab
  default_tab: "file_organizer"          # Starting tab
  
  # Progress and Status
  update_interval_ms: 100                # Progress update frequency
  show_file_count: true                  # Show number of files processed
  show_processing_speed: true            # Show files per second
```

### 🔒 Security and Safety

```yaml
security:
  # File Permissions
  preserve_permissions: true             # Keep original file permissions
  set_readonly_on_complete: false        # Make processed files read-only
  
  # Backup Settings
  create_backup_before_processing: false # Create backup copy before processing
  backup_directory: "./backups"          # Where to store backups
  backup_retention_days: 30              # How long to keep backups
  
  # File Validation
  verify_file_integrity: true            # Check file integrity after processing
  quarantine_corrupted_files: true       # Move corrupted files to quarantine
  quarantine_directory: "./quarantine"   # Quarantine location
  
  # Safety Features
  block_executable_files: true           # Don't process .exe, .bat, etc.
  scan_for_malware: false                # Enable if antivirus tools available
```

### 🔍 Advanced Features

```yaml
advanced:
  # Metadata Extraction
  extract_metadata: true                 # Extract file metadata
  metadata_output_format: "json"         # "json", "yaml", "xml"
  include_exif_data: true                # Include camera/GPS data
  include_file_hashes: true              # Include file checksums
  
  # Translation Support
  enable_filename_translation: false     # Translate non-English filenames
  translation_service: "google"          # "google", "deepl", "offline"
  target_language: "en"                  # Target language code
  translate_metadata: false              # Translate metadata text
  
  # Similarity Matching
  similarity_algorithm: "advanced"       # "basic", "advanced", "gpu"
  use_content_analysis: true             # Analyze file contents for similarity
  enable_image_similarity: false         # Visual similarity (requires OpenCV)
  
  # File Validation
  verify_file_integrity: true            # Verify files after processing
  quarantine_corrupted_files: true       # Isolate problematic files
```

### 📊 Filtering and Selection

```yaml
filters:
  # Size Filters
  min_file_size_bytes: 0                 # Minimum file size (0 = no limit)
  max_file_size_bytes: 0                 # Maximum file size (0 = no limit)
  
  # Date Filters
  process_files_newer_than_days: 0       # Only process recent files
  process_files_older_than_days: 0       # Only process old files
  
  # Name Filters
  exclude_patterns:                      # Skip files matching these patterns
    - ".*"                               # Hidden files
    - "Thumbs.db"                        # Windows thumbnails
    - ".DS_Store"                        # macOS metadata
    - "desktop.ini"                      # Windows folder settings
  
  include_patterns: []                   # Only process files matching these patterns
  
  # Directory Filters
  exclude_directories:                   # Skip these directories
    - "__pycache__"                      # Python cache
    - ".git"                             # Git repository
    - "node_modules"                     # Node.js modules
    - ".vscode"                          # VS Code settings
```

### 📱 Platform-Specific Settings

```yaml
platform:
  # Windows Specific
  windows:
    use_windows_api: true                # Use native Windows APIs
    handle_long_paths: true              # Support paths >260 characters
    preserve_alternate_streams: false    # Keep NTFS alternate data streams
  
  # Linux/WSL Specific
  linux:
    preserve_permissions: true           # Keep Unix file permissions
    follow_symlinks: false               # Follow symbolic links
    use_native_tools: true               # Prefer system tools over Python
  
  # macOS Specific
  macos:
    preserve_resource_forks: false       # Keep macOS resource forks
    handle_case_sensitivity: true        # Handle case-sensitive filesystems
```

## 🛠️ Configuration Management

### Creating Configuration Templates

```bash
# Save current config as template
python file_processing_suite_main.py --save-config-template "high_performance"

# Load configuration template
python file_processing_suite_main.py --load-config-template "high_performance"
```

### Environment Variables

You can override any configuration setting using environment variables:

```bash
# Override GPU setting
export FPS_PERFORMANCE_ENABLE_GPU=false

# Override output directory
export FPS_GENERAL_DEFAULT_OUTPUT_DIRECTORY="/custom/output"

# Override log level
export FPS_GENERAL_LOG_LEVEL=DEBUG
```

### Configuration Validation

The suite automatically validates configuration on startup:

```bash
# Validate configuration file
python file_processing_suite_main.py --validate-config

# Check configuration and show effective settings
python file_processing_suite_main.py --show-config
```

## 🎯 Use Case Examples

### High-Volume Photo Processing
```yaml
performance:
  enable_gpu: true
  max_workers: "auto"
  memory_limit_gb: 32

formats:
  images:
    default_output_format: "webp"
    webp_quality: 90
    preserve_metadata: true

organization:
  create_date_folders: true
  enable_series_detection: true
  similarity_threshold: 0.90
```

### Document Archive Processing
```yaml
performance:
  enable_gpu: false
  max_workers: 4

formats:
  documents:
    default_output_format: "pdf"
    pdf_compression: true
    pdf_quality: "high"

security:
  create_backup_before_processing: true
  verify_file_integrity: true
```

### Comic Book Collection Management
```yaml
formats:
  archives:
    default_output_format: "zip"
    compression_level: 9

organization:
  enable_series_detection: true
  similarity_threshold: 0.75
  normalize_filenames: true

advanced:
  similarity_algorithm: "advanced"
  use_content_analysis: true
```

## 🚨 Troubleshooting Configuration

### Common Issues

1. **GPU Not Detected**
   ```yaml
   performance:
     enable_gpu: false  # Disable GPU if having issues
   ```

2. **Memory Errors**
   ```yaml
   performance:
     memory_limit_gb: 4  # Reduce memory usage
     max_workers: 2      # Reduce parallel processing
   ```

3. **Slow Performance**
   ```yaml
   performance:
     enable_gpu: true    # Enable GPU acceleration
     max_workers: "auto" # Use all CPU cores
   ```

### Validation Errors

The suite will report configuration errors with specific guidance:

```
Configuration Error: Invalid gpu_backend 'invalid_value'
Valid options: 'auto', 'cupy', 'cuda', 'disabled'
Location: performance.gpu_backend
```

## 📞 Support

For configuration assistance:
1. Check the validation output: `--validate-config`
2. Review effective settings: `--show-config`
3. Enable debug logging: `log_level: "DEBUG"`
4. Check system compatibility: `--system-info`

---

**Note**: Configuration changes take effect on next application startup. For immediate changes, use the GUI's "Reload Configuration" option.
