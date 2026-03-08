# Standalone Filename Processor v1.0

🚀 **Comprehensive Filename Manipulation Tool for Side Projects**

A complete, self-contained script that incorporates all the advanced filename processing features from the Enhanced File Processing Suite into a single, portable file perfect for team collaboration and side projects.

## ✨ Features

### 🔧 **Core Filename Processing**
- **Sanitization**: Remove illegal characters, noise patterns, and normalize spacing
- **Extension Normalization**: Standardize file extensions (`.jpeg` → `.jpg`, `.mpeg` → `.mpg`)
- **Translation Support**: Convert non-ASCII characters to English equivalents
- **Series Detection**: Automatically detect and organize series, volumes, episodes, chapters
- **Metadata Extraction**: Extract and utilize file metadata for better naming

### 🛡️ **Advanced File Management**
- **Duplicate Detection**: Multiple detection methods (size, hash, content)
- **Smart Backup System**: Automatic backup creation before processing
- **Parallel Processing**: Multi-threaded processing for performance
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Dry Run Mode**: Preview changes before applying them

### 🎯 **Flexible Configuration**
- **Top-Level Configuration**: All settings documented in the CONFIG dictionary
- **JSON Configuration Files**: Load custom configurations from external files
- **Command-Line Overrides**: Override any setting from the command line
- **File Type Specific Settings**: Different processing rules per file type

## 🚀 Quick Start

### Basic Usage
```bash
# Process all files in a directory
python standalone_filename_processor.py /path/to/files

# Preview changes without applying (recommended first)
python standalone_filename_processor.py /path/to/files --dry-run --verbose

# Process specific file types
python standalone_filename_processor.py . --patterns "*.jpg" "*.png" "*.mp4"
```

### Advanced Usage
```bash
# Use custom configuration
python standalone_filename_processor.py /media --config custom_config.json

# Enable translation and disable backups
python standalone_filename_processor.py ~/Downloads --translate --no-backup

# High-performance processing
python standalone_filename_processor.py /large/directory --threads 8 --no-duplicates
```

## ⚙️ Configuration

### Configuration Methods

1. **Edit CONFIG Dictionary** (Top of file, lines 32-120)
2. **JSON Configuration File** (Use `--config` parameter)
3. **Command Line Options** (Override specific settings)

### Key Configuration Sections

#### General Settings
```python
"dry_run": False,                    # Preview mode
"verbose": True,                     # Detailed logging
"max_workers": 4,                    # Parallel threads
"backup_originals": True,            # Create backups
```

#### Filename Processing
```python
"sanitize_filenames": True,          # Clean illegal characters
"normalize_extensions": True,        # Standardize extensions
"translate_filenames": False,        # ASCII conversion
"process_series": True,              # Series detection
```

#### Duplicate Detection
```python
"duplicate_detection": {
    "method": "size_and_hash",       # Detection method
    "action": "move_to_folder",      # What to do with duplicates
    "keep_newest": True              # Which file to keep
}
```

## 📊 File Type Support

### Images
- **Extensions**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`
- **Features**: Metadata extraction, date organization, size optimization

### Videos
- **Extensions**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`
- **Features**: Metadata extraction, series detection, compression options

### Documents
- **Extensions**: `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`
- **Features**: Metadata extraction, type organization, OCR support

### Archives
- **Extensions**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`
- **Features**: Integrity verification, content extraction, cleanup

### Comics/eBooks
- **Extensions**: `.cbr`, `.cbz`, `.cb7`, `.cbt`
- **Features**: Series organization, PDF conversion, metadata extraction

## 🎯 Series Detection

Automatically detects and organizes series with patterns like:
- `Series Name Vol.1` → `Series_Name_001`
- `Show Season 2` → `Show_Season_002`
- `Book Part 3` → `Book_Part_003`
- `Game Episode 4` → `Game_Episode_004`
- `Manga Chapter 5` → `Manga_Chapter_005`

## 🔍 Duplicate Detection

### Detection Methods
- **size**: Compare file sizes
- **hash**: Compare file hashes (MD5, SHA1, SHA256)
- **size_and_hash**: Combine both methods
- **content**: Deep content comparison

### Handling Options
- **delete**: Remove duplicate files
- **move_to_folder**: Move to designated folder
- **rename**: Add suffix to duplicates
- **ask**: Interactive prompts (future feature)

## 📋 Command Line Options

```
usage: standalone_filename_processor.py [-h] [--patterns [PATTERNS ...]] 
                                        [--dry-run] [--verbose] [--no-backup] 
                                        [--no-duplicates] [--translate] 
                                        [--config CONFIG] [--threads THREADS] 
                                        [--version] directory

positional arguments:
  directory             Directory to process recursively

options:
  --patterns [PATTERNS ...]    File patterns to match (e.g., '*.jpg' '*.mp4')
  --dry-run                    Preview changes without applying them
  --verbose                    Enable verbose logging
  --no-backup                  Disable backup creation
  --no-duplicates              Disable duplicate detection
  --translate                  Enable filename translation
  --config CONFIG              Path to custom configuration JSON file
  --threads THREADS            Number of processing threads (default: 4)
  --version                    Show version information
```

## 📁 Example Configuration File

Create `config_example.json`:

```json
{
  "dry_run": false,
  "verbose": true,
  "max_workers": 6,
  "backup_directory": "_backup_originals",
  
  "normalize_extensions": true,
  "sanitize_filenames": true,
  "translate_filenames": true,
  "remove_duplicates": true,
  "process_series": true,
  
  "duplicate_detection": {
    "method": "size_and_hash",
    "hash_algorithm": "sha256",
    "action": "move_to_folder",
    "duplicate_folder": "_duplicates_found",
    "keep_newest": true
  },
  
  "translation": {
    "enabled": true,
    "preserve_original": true
  }
}
```

## 🎨 Example Transformations

### Before Processing
```
My Weird_Movie__[2023](HD).mpeg
Another-Movie---Part__2.m4v
游戏截图_001.jpeg
Series_Vol.1_[Clean].cbr
duplicate_file.jpg
duplicate_file (1).jpg
```

### After Processing
```
My_Weird_Movie_2023.mpg
Another_Movie_Part_002.mp4
youxi_jietú_001.jpg  (translated)
Series_001.cbr
original_file.jpg
_duplicates/duplicate_file_dup_001.jpg
```

## 📊 Performance Monitoring

The script provides comprehensive statistics:

```
==================================================
PROCESSING COMPLETE
==================================================
Files processed: 1,247
Files renamed: 892
Duplicates found: 34
Errors encountered: 0
Processing time: 12.34 seconds
Processing rate: 101.05 files/second
==================================================
```

## 🛠️ Integration with Side Projects

### As a Git Submodule
```bash
git submodule add https://github.com/yourteam/filename-processor.git tools/
```

### As a Standalone Script
```bash
# Copy the script to your project
cp standalone_filename_processor.py your_project/tools/
# Customize the CONFIG dictionary for your needs
```

### In CI/CD Pipelines
```yaml
- name: Process Uploaded Files
  run: |
    python tools/standalone_filename_processor.py uploads/ --dry-run
    python tools/standalone_filename_processor.py uploads/ --config production.json
```

## 🚨 Best Practices

### Before First Use
1. **Always use `--dry-run` first** to preview changes
2. **Enable `--verbose`** to understand what's happening
3. **Test with a small subset** of files initially
4. **Keep backups enabled** until you're confident

### For Production Use
1. **Create custom configuration files** for different scenarios
2. **Use appropriate thread counts** based on your system
3. **Monitor log files** for errors and performance
4. **Implement error handling** in automated scripts

### Team Collaboration
1. **Document your CONFIG changes** in version control
2. **Share configuration files** with team members
3. **Use consistent patterns** across projects
4. **Test thoroughly** before processing important files

## 🔧 Customization

### Adding New File Types
Edit the `file_type_settings` in CONFIG:

```python
"file_type_settings": {
    "audio": {
        "extensions": [".mp3", ".flac", ".wav", ".aac"],
        "extract_metadata": True,
        "organize_by_album": True,
        "normalize_bitrate": False
    }
}
```

### Custom Noise Patterns
Add to `noise_patterns`:

```python
"noise_patterns": [
    r'\[.*?\]',           # Remove bracketed content
    r'_SAMPLE_',          # Remove sample markers
    r'(?i)temp.*',        # Remove temp files
    r'\.tmp$'             # Remove .tmp extensions
]
```

### Series Detection Patterns
Extend `series_patterns`:

```python
"series_patterns": [
    r'(.+?)\s*S(\d+)E(\d+)',     # TV show format
    r'(.+?)\s*(\d{4})',          # Year-based
    r'(.+?)\s*#(\d+)',           # Comic issue format
]
```

## 🐛 Troubleshooting

### Common Issues

**Permission Errors**
```bash
# Ensure you have write permissions
chmod +w /path/to/files
```

**Memory Issues with Large Directories**
```python
# Reduce max_workers in CONFIG
"max_workers": 2
```

**Hash Calculation Slow**
```python
# Use faster hash algorithm
"hash_algorithm": "md5"  # instead of sha256
```

### Debugging

Enable debug logging:
```python
"logging": {
    "level": "DEBUG",
    "log_file": "debug.log"
}
```

## 📝 License

MIT License - Feel free to use in your side projects and team collaborations.

## 🤝 Contributing

This script is designed to be self-contained and customizable. To contribute:

1. Fork the script for your specific needs
2. Document your configuration changes
3. Share useful patterns and configurations with the team
4. Report bugs or suggest enhancements

---

**Created by**: Enhanced File Processing Suite Team  
**Date**: September 10, 2025  
**Version**: 1.0  
**Purpose**: Portable filename processing for side projects and team collaboration
