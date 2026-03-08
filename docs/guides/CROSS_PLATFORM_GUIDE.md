# Cross-Platform Compatibility Guide

## Overview

The Enhanced File Processing Suite v5.0 is designed to work seamlessly across multiple platforms:

- ✅ **Windows** (Windows 10/11, PowerShell, CMD)
- ✅ **Linux** (Ubuntu, Debian, Fedora, RHEL, etc.)
- ✅ **WSL** (Windows Subsystem for Linux)
- ✅ **macOS** (Intel and Apple Silicon)

## Key Cross-Platform Features

### 1. **Universal Python Launcher**
- Single Python script works on all platforms
- Automatic platform detection
- No need for separate batch/shell scripts
- Located at: `deployment/universal_launcher.py`

### 2. **Path Handling**
- All path operations use Python's `pathlib.Path`
- Automatic path separator conversion (\ vs /)
- Handles Windows drive letters and Unix paths
- Unicode filename support across platforms

### 3. **Platform-Specific Optimizations**
- Automatic hardware detection per platform
- OS-specific file operations (sendfile, copy_file_range, etc.)
- Platform-aware subprocess calls
- Encoding handling (UTF-8 everywhere)

### 4. **Dependency Management**
- Graceful fallbacks for missing dependencies
- Platform-specific installation instructions
- System-level or user-level package installation
- Smart dependency detection

## Running on Different Platforms

### Windows

#### Method 1: PowerShell/CMD
```powershell
# GUI Mode
python main.py --gui

# CLI Mode
python main.py --cli C:\path\to\files --operations sanitize_filename

# Using Universal Launcher
python deployment\universal_launcher.py gui
```

#### Method 2: Batch Files
```cmd
deployment\Launch_GUI.bat
deployment\Launch_Standalone_Processor.bat "C:\path\to\files"
```

### Linux / macOS

#### Method 1: Direct Python
```bash
# GUI Mode
python3 main.py --gui

# CLI Mode
python3 main.py --cli /path/to/files --operations sanitize_filename

# Using Universal Launcher
python3 deployment/universal_launcher.py gui
```

#### Method 2: Shell Scripts
```bash
# Make executable
chmod +x deployment/launch_gui.sh
chmod +x deployment/launch_standalone_processor.sh

# Run
./deployment/launch_gui.sh
./deployment/launch_standalone_processor.sh /path/to/files
```

### WSL (Windows Subsystem for Linux)

WSL can run both Windows and Linux executables:

```bash
# Linux-style (recommended)
python3 main.py --gui

# Windows-style (if Python is in Windows PATH)
python.exe main.py --gui

# Using Universal Launcher
python3 deployment/universal_launcher.py
```

## Installation Per Platform

### Windows
```powershell
# Install Python 3.9+ from python.org
# Then install dependencies
pip install -r requirements.txt

# Or use smart installer
python deployment\smart_installer.py
```

### Linux (Debian/Ubuntu)
```bash
# System packages (recommended)
sudo apt update
sudo apt install python3-pip python3-pil python3-yaml python3-aiofiles

# Additional dependencies
pip3 install -r requirements.txt

# Or use smart installer
python3 deployment/smart_installer.py
```

### Linux (Fedora/RHEL)
```bash
# System packages
sudo dnf install python3-pip python3-pillow python3-pyyaml

# Additional dependencies
pip3 install -r requirements.txt
```

### macOS
```bash
# Install Homebrew if needed: https://brew.sh
brew install python3

# Install dependencies
pip3 install -r requirements.txt
```

### WSL
```bash
# Same as Linux, but note:
# - Can access Windows files via /mnt/c/
# - GUI apps may need X server (VcXsrv, WSLg)

sudo apt update
sudo apt install python3-pip python3-pil python3-yaml
pip3 install -r requirements.txt
```

## Testing Cross-Platform Compatibility

### Comprehensive Test Suite
Run the comprehensive test suite to verify all features:

```bash
# On any platform
python deployment/comprehensive_test_runner.py
```

This will test:
- ✅ Module imports
- ✅ System information
- ✅ CLI operations
- ✅ File processing
- ✅ Path handling
- ✅ File operations
- ✅ Standalone processor
- ✅ Universal launcher

### Platform-Specific Tests
```bash
# Basic compatibility check
python deployment/cross_platform_test.py

# System information
python main.py --system-info

# Help documentation
python main.py --help
```

## Cross-Platform Development Guidelines

### Do's ✅
- **Always use `pathlib.Path`** for file paths
- **Use `os.path.join()` or `Path /`** for path concatenation
- **Specify encoding** in file operations: `open(file, 'r', encoding='utf-8')`
- **Use `subprocess.run()`** with `shell=False` when possible
- **Test on multiple platforms** before committing

### Don'ts ❌
- **Don't hardcode path separators** (`\` or `/`)
- **Don't use platform-specific APIs** without fallbacks
- **Don't assume case-sensitive filenames** (Windows is case-insensitive)
- **Don't use shell-specific commands** without platform checks
- **Don't hardcode line endings** (use `\n`, Python handles it)

### Example: Cross-Platform File Operations
```python
from pathlib import Path
import shutil

# ✅ Good - works everywhere
source = Path("data") / "files" / "input.txt"
dest = Path("output") / "processed.txt"
shutil.copy2(source, dest)

# ❌ Bad - Windows-specific
source = "data\\files\\input.txt"
dest = "output\\processed.txt"
```

### Example: Platform Detection
```python
import platform
import sys

# Detect platform
system = platform.system()  # 'Windows', 'Linux', 'Darwin'

if system == 'Windows':
    # Windows-specific code
    pass
elif system == 'Linux':
    # Linux-specific code
    pass
elif system == 'Darwin':
    # macOS-specific code
    pass

# Check if WSL
def is_wsl():
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False
```

## Troubleshooting

### Issue: Python not found
**Windows:**
- Install from python.org
- Check "Add Python to PATH" during installation
- Verify: `python --version`

**Linux:**
```bash
sudo apt install python3 python3-pip  # Debian/Ubuntu
sudo dnf install python3 python3-pip  # Fedora/RHEL
```

### Issue: Permission denied (Linux/macOS)
```bash
# Make scripts executable
chmod +x deployment/*.sh

# Or run with Python
python3 deployment/universal_launcher.py
```

### Issue: GUI not working in WSL
```bash
# Install X server for Windows (VcXsrv or WSLg)
# Or use CLI mode instead
python3 main.py --cli /path/to/files
```

### Issue: Module import errors
```bash
# Ensure you're in project root
cd /path/to/Scripts.FileProcessor

# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Issue: Encoding errors on Windows
- The project automatically sets UTF-8 encoding
- If issues persist, set environment variable:
```powershell
$env:PYTHONIOENCODING = "utf-8"
```

## Platform-Specific Notes

### Windows
- Uses `\` as path separator (but pathlib handles this automatically)
- Case-insensitive filesystem
- Supports long paths (>260 chars) on Windows 10+
- PowerShell and CMD both supported

### Linux
- Uses `/` as path separator
- Case-sensitive filesystem
- Requires execute permissions for scripts
- Shell scripts use bash

### macOS
- Similar to Linux but with some differences
- Case-insensitive by default (APFS can be case-sensitive)
- Some Unix tools have BSD variants

### WSL
- Linux kernel running on Windows
- Access Windows files via `/mnt/c/`, `/mnt/d/`, etc.
- Can run both Linux and Windows executables
- GUI support via WSLg (Windows 11) or X server

## Continuous Integration

For automated testing across platforms, see `.github/workflows/` for CI/CD configurations supporting:
- Windows (latest)
- Ubuntu (latest)
- macOS (latest)

## Support

If you encounter platform-specific issues:

1. **Check system info:** `python main.py --system-info`
2. **Run tests:** `python deployment/comprehensive_test_runner.py`
3. **Review logs:** Check `enhanced_suite.log`
4. **Report issues:** Include platform details and error messages

## Version History

- **v5.0.0** - Full cross-platform support with universal launcher
- **v4.0.0** - Basic Windows/Linux support
- **v3.0.0** - Windows-only release

---

**Note:** This project aims to work seamlessly on all major platforms. If you find any platform-specific issues, please report them with full platform details.
