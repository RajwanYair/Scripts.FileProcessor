# Enhanced File Processing Suite v5.0 - Feature List & Runnable Scripts

## 📋 Table of Contents
- [Main Features](#main-features)
- [Individually Runnable Scripts](#individually-runnable-scripts)
- [Core Modules (Library Functions)](#core-modules-library-functions)
- [Usage Examples](#usage-examples)

---

## 🌟 Main Features

### 1. **File Processing Operations**
- ✅ Filename sanitization (remove illegal characters)
- ✅ Extension normalization (standardize file extensions)
- ✅ Duplicate detection and removal
- ✅ Series detection and grouping (e.g., vol.1, vol.2)
- ✅ Metadata extraction (EXIF, PDF info, etc.)
- ✅ Password-protected file handling
- ✅ Format detection (200+ file formats)
- ✅ Similarity matching (content-based)
- ✅ Filename translation (non-English to English)

### 2. **Performance Features**
- ⚡ Async/await processing (50% faster)
- ⚡ Hardware-aware optimization (CPU/GPU/Storage)
- ⚡ Zero-copy file operations
- ⚡ Multi-level intelligent caching (L1/L2/L3)
- ⚡ Parallel processing with worker pools
- ⚡ GPU acceleration support (NVIDIA/AMD/Intel)

### 3. **Format Support**
- 📄 **Documents**: PDF, DOCX, TXT, RTF, ODT, EPUB
- 🖼️ **Images**: JPG, PNG, GIF, BMP, TIFF, WebP, SVG, RAW
- 🎬 **Videos**: MP4, AVI, MKV, MOV, WebM, FLV
- 🎵 **Audio**: MP3, WAV, FLAC, AAC, OGG
- 📦 **Archives**: ZIP, RAR, 7Z, TAR, GZ, BZ2
- 📚 **Comics**: CBR, CBZ, CB7, CBT
- 💾 **Development**: Python, JavaScript, C++, Java, and more
- 🎮 **3D/CAD**: STL, OBJ, FBX, DWG, and more

### 4. **User Interfaces**
- 🖥️ **GUI**: Tkinter-based graphical interface
- ⌨️ **CLI**: Command-line interface with full control
- 📊 **Dashboard**: Web-based performance monitoring
- 🔧 **Standalone**: Single-file processor utility

### 5. **Cross-Platform Support**
- 🪟 **Windows**: Native support with batch files
- 🐧 **Linux**: Full support with shell scripts
- 🔄 **WSL**: Windows Subsystem for Linux compatible
- 🍎 **macOS**: Intel and Apple Silicon support

### 6. **AI & Advanced Features**
- 🤖 AI-powered similarity detection
- 🧠 Intelligent format detection
- 🎯 Smart series grouping
- 🔍 Advanced duplicate detection (hash-based)
- 📈 Performance analytics and reporting

---

## 🚀 Individually Runnable Scripts

### **Main Entry Points**

#### 1. **Main Unified Launcher** ⭐ (Recommended)
```bash
python main.py [options]
```
**Features:**
- Auto-detects GUI/CLI mode
- Unified entry point for all operations
- Platform detection and optimization

**Options:**
- `--gui` - Force GUI mode
- `--cli` - Force CLI mode
- `--system-info` - Show system information
- `--benchmark` - Run performance benchmark
- `--help` - Show help

**Examples:**
```bash
# Launch GUI
python main.py --gui

# Process files via CLI
python main.py --cli /path/to/files --operations sanitize_filename

# Show system info
python main.py --system-info

# Run benchmark
python main.py --benchmark
```

---

### **GUI & Interactive Scripts**

#### 2. **Enhanced GUI v5.0**
```bash
python scripts/enhanced_gui_v5.py
```
**Features:**
- Modern tkinter interface
- Real-time progress tracking
- Batch operation selection
- Configuration management
- Results preview

**Can Run Standalone:** ✅ Yes

---

#### 3. **Performance Monitoring Dashboard**
```bash
python scripts/performance_monitoring_dashboard.py
```
**Features:**
- Web-based dashboard (Flask/Dash)
- Real-time performance metrics
- Hardware utilization graphs
- Processing statistics
- Live file processing monitor

**Can Run Standalone:** ✅ Yes

---

### **CLI Processing Scripts**

#### 4. **File Processing Suite Main (CLI)**
```bash
python scripts/file_processing_suite_main.py [directory] [options]
```
**Features:**
- Complete CLI interface
- All file operations available
- Async processing
- Progress bars
- YAML configuration support

**Options:**
- `--operations` - Specify operations (sanitize, deduplicate, etc.)
- `--recursive` - Process subdirectories
- `--config` - Use configuration file
- `--benchmark` - Run with benchmarking
- `--pattern` - File pattern filter

**Examples:**
```bash
# Sanitize filenames
python scripts/file_processing_suite_main.py /path/to/files --operations sanitize_filename

# Multiple operations
python scripts/file_processing_suite_main.py /path/to/files --operations sanitize deduplicate group_series

# With config file
python scripts/file_processing_suite_main.py /path/to/files --config config/my_config.yaml

# Recursive processing
python scripts/file_processing_suite_main.py /path/to/files --recursive --operations all
```

**Can Run Standalone:** ✅ Yes (with dependencies)

---

#### 5. **Standalone Filename Processor** ⭐ (Recommended for Quick Use)
```bash
python utilities/standalone_filename_processor.py [directory] [options]
```
**Features:**
- Zero external dependencies (except Python stdlib)
- Fast filename processing
- Dry-run mode for safety
- Backup creation
- Series detection
- Duplicate handling

**Options:**
- `--dry-run` - Preview changes without applying
- `--verbose` - Detailed output
- `--no-backup` - Skip backup creation
- `--translate` - Enable filename translation
- `--patterns` - File patterns to process

**Examples:**
```bash
# Dry run (safe preview)
python utilities/standalone_filename_processor.py /path/to/files --dry-run

# Process only images
python utilities/standalone_filename_processor.py /path/to/files --patterns "*.jpg" "*.png"

# Verbose mode
python utilities/standalone_filename_processor.py /path/to/files --verbose

# Process with translation
python utilities/standalone_filename_processor.py /path/to/files --translate
```

**Can Run Standalone:** ✅ Yes (fully independent)

---

### **Deployment & Setup Scripts**

#### 6. **Universal Launcher** ⭐ (Cross-Platform)
```bash
python deployment/universal_launcher.py [command]
```
**Features:**
- Works on ALL platforms (Windows/Linux/WSL/macOS)
- Interactive menu
- Multiple launch modes
- System checks

**Commands:**
- `gui` - Launch GUI
- `cli` - Launch CLI
- `standalone <dir>` - Launch standalone processor
- `test` - Run tests
- `info` - System information
- `help` - Show help

**Examples:**
```bash
# Interactive menu
python deployment/universal_launcher.py

# Launch GUI
python deployment/universal_launcher.py gui

# Launch standalone
python deployment/universal_launcher.py standalone /path/to/files

# Run tests
python deployment/universal_launcher.py test
```

**Can Run Standalone:** ✅ Yes

---

#### 7. **Quick Verification Script**
```bash
python deployment/quick_verify.py
```
**Features:**
- Quick installation check
- Platform detection
- Component verification
- Dependency status
- Quick start guide

**Can Run Standalone:** ✅ Yes

---

#### 8. **Comprehensive Test Runner**
```bash
python deployment/comprehensive_test_runner.py
```
**Features:**
- 10 comprehensive tests
- Platform compatibility testing
- Automatic test environment setup
- Detailed reporting

**Can Run Standalone:** ✅ Yes

---

#### 9. **Cross-Platform Test**
```bash
python deployment/cross_platform_test.py
```
**Features:**
- Basic compatibility check
- Platform information
- Dependency testing
- Installation recommendations

**Can Run Standalone:** ✅ Yes

---

#### 10. **Smart Installer**
```bash
python deployment/smart_installer.py
```
**Features:**
- Interactive dependency installation
- Tier-based installation (Essential/Standard/Advanced)
- Platform-specific guidance
- External tool setup guide
- GPU setup instructions

**Can Run Standalone:** ✅ Yes

---

#### 11. **Enhanced Dependency Manager**
```bash
python deployment/enhanced_dependency_manager.py
```
**Features:**
- System-level dependency management
- Dependency checking and installation
- Fallback handling
- Cross-platform package management

**Can Run Standalone:** ✅ Yes

---

### **Testing Scripts**

#### 12. **Test Suite**
```bash
python tests/test_enhanced_suite.py
```
**Features:**
- Unit tests for all modules
- Integration tests
- Performance benchmarks

**Can Run Standalone:** ✅ Yes

---

#### 13. **Validate Release**
```bash
python tests/validate_release.py
```
**Features:**
- Pre-release validation
- Feature verification
- Dependency checks

**Can Run Standalone:** ✅ Yes

---

#### 14. **Performance Enhancement Tests**
```bash
python tests/test_performance_enhancements.py
```
**Features:**
- Performance benchmarks
- Cache system tests
- Async processing tests
- Hardware detection tests

**Can Run Standalone:** ✅ Yes

---

### **Utility Scripts**

#### 15. **Cleanup PIP User Packages**
```bash
python utilities/cleanup_pip_user_packages.py
```
**Features:**
- Removes redundant user-level pip packages
- Cleans up conflicting installations
- Safe with confirmation prompts

**Can Run Standalone:** ✅ Yes

---

### **Setup & Configuration Scripts**

#### 16. **Setup Performance Enhancements**
```bash
python scripts/setup_performance_enhancements.py
```
**Features:**
- Configures performance settings
- Hardware detection and optimization
- Cache configuration
- Creates optimized config files

**Can Run Standalone:** ✅ Yes

---

### **Platform-Specific Launchers**

#### 17. **Launch GUI (Windows)**
```cmd
deployment\Launch_GUI.bat
```
**Can Run Standalone:** ✅ Yes (Windows only)

---

#### 18. **Launch GUI (Linux/WSL/macOS)**
```bash
chmod +x deployment/launch_gui.sh
./deployment/launch_gui.sh
```
**Can Run Standalone:** ✅ Yes (Unix-like systems)

---

#### 19. **Launch Standalone Processor (Windows)**
```cmd
deployment\Launch_Standalone_Processor.bat "C:\path\to\files"
```
**Can Run Standalone:** ✅ Yes (Windows only)

---

#### 20. **Launch Standalone Processor (Linux/WSL/macOS)**
```bash
chmod +x deployment/launch_standalone_processor.sh
./deployment/launch_standalone_processor.sh /path/to/files
```
**Can Run Standalone:** ✅ Yes (Unix-like systems)

---

## 📚 Core Modules (Library Functions)

These are library modules that can be imported but don't run standalone:

### Processing Modules
- `core/advanced_async_processor.py` - Async file processing
- `core/enhanced_filename_processor.py` - Filename operations
- `core/enhanced_deduplicator.py` - Duplicate detection
- `core/advanced_metadata_extractor.py` - Metadata extraction
- `core/password_protected_processor.py` - Password file handling
- `core/advanced_series_grouper.py` - Series detection
- `core/advanced_similarity.py` - Similarity matching

### Performance Modules
- `core/hardware_detector.py` - Hardware detection
- `core/enhanced_performance_manager.py` - Performance optimization
- `core/intelligent_cache_system.py` - Multi-level caching
- `core/zero_copy_operations.py` - Zero-copy file ops

### Utility Modules
- `core/file_utils.py` - File utility functions
- `core/unified_utilities.py` - Unified helper functions
- `core/enhanced_format_support.py` - Format detection
- `core/smart_imports.py` - Dependency management

---

## 💡 Usage Examples

### Quick Start - Most Common Use Cases

#### 1. **Clean Up Filenames in a Directory**
```bash
# Safe preview (recommended first step)
python utilities/standalone_filename_processor.py /path/to/files --dry-run

# Apply changes
python utilities/standalone_filename_processor.py /path/to/files
```

#### 2. **Remove Duplicates**
```bash
python scripts/file_processing_suite_main.py /path/to/files --operations deduplicate
```

#### 3. **Organize Series (comics, books, etc.)**
```bash
python scripts/file_processing_suite_main.py /path/to/files --operations group_series
```

#### 4. **Extract Metadata from Files**
```bash
python scripts/file_processing_suite_main.py /path/to/files --operations extract_metadata
```

#### 5. **Process Everything (Full Suite)**
```bash
python main.py --cli /path/to/files --operations sanitize deduplicate group_series extract_metadata --recursive
```

#### 6. **Launch GUI for Easy Use**
```bash
# Easiest method - auto-detect
python main.py

# Or explicitly
python main.py --gui
python deployment/universal_launcher.py gui
```

#### 7. **Check System Compatibility**
```bash
python deployment/quick_verify.py
python main.py --system-info
```

#### 8. **Run Comprehensive Tests**
```bash
python deployment/comprehensive_test_runner.py
```

---

## 📊 Feature Matrix

| Feature | Main Script | Standalone | GUI | CLI |
|---------|-------------|------------|-----|-----|
| Filename Sanitization | ✅ | ✅ | ✅ | ✅ |
| Duplicate Detection | ✅ | ✅ | ✅ | ✅ |
| Series Grouping | ✅ | ✅ | ✅ | ✅ |
| Metadata Extraction | ✅ | ✅ | ✅ | ✅ |
| Format Detection | ✅ | ❌ | ✅ | ✅ |
| Similarity Matching | ✅ | ❌ | ✅ | ✅ |
| Password Files | ✅ | ✅ | ✅ | ✅ |
| Async Processing | ✅ | ❌ | ❌ | ✅ |
| GPU Acceleration | ✅ | ❌ | ❌ | ✅ |
| Performance Dashboard | ❌ | ❌ | ❌ | ❌* |

\* Performance dashboard runs separately via `scripts/performance_monitoring_dashboard.py`

---

## 🎯 Recommendation Guide

### **For Beginners:**
1. Start with: `python deployment/universal_launcher.py`
2. Or use GUI: `python main.py --gui`
3. Or quick processing: `python utilities/standalone_filename_processor.py /path/to/files --dry-run`

### **For Power Users:**
1. CLI processing: `python scripts/file_processing_suite_main.py [dir] --operations [ops]`
2. Custom configs: `python scripts/file_processing_suite_main.py [dir] --config my_config.yaml`
3. Batch operations: Create shell scripts calling CLI with different options

### **For Developers:**
1. Import core modules in your own scripts
2. Use the test suite: `python tests/test_enhanced_suite.py`
3. Run benchmarks: `python main.py --benchmark`

### **For System Administrators:**
1. Deploy with: `python deployment/smart_installer.py`
2. Verify with: `python deployment/comprehensive_test_runner.py`
3. Monitor with: `python scripts/performance_monitoring_dashboard.py`

---

## 📝 Summary

### **Total Runnable Scripts: 20+**

**Most Important (⭐ Recommended):**
1. `main.py` - Universal entry point
2. `deployment/universal_launcher.py` - Cross-platform launcher
3. `utilities/standalone_filename_processor.py` - Quick filename processor
4. `scripts/enhanced_gui_v5.py` - GUI interface
5. `scripts/file_processing_suite_main.py` - Full CLI suite

**Testing & Verification:**
6. `deployment/quick_verify.py` - Quick check
7. `deployment/comprehensive_test_runner.py` - Full tests
8. `deployment/cross_platform_test.py` - Platform tests

**Installation & Setup:**
9. `deployment/smart_installer.py` - Interactive installer
10. `deployment/enhanced_dependency_manager.py` - Dependency manager

**Platform Launchers:**
11-14. Batch and shell scripts for Windows/Linux/macOS

**Utilities:**
15. `utilities/cleanup_pip_user_packages.py` - Package cleanup
16. `scripts/setup_performance_enhancements.py` - Performance setup
17. `scripts/performance_monitoring_dashboard.py` - Web dashboard

**Tests:**
18-20. Various test scripts for validation

---

**All scripts support `--help` for detailed usage information!**

```bash
python [script_name].py --help
```
