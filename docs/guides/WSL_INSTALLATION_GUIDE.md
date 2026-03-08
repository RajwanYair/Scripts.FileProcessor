# WSL (Windows Subsystem for Linux) Installation Guide

## System-Level Installation for Enhanced File Processing Suite v5.0

### Prerequisites
Ensure WSL is installed and you have a Linux distribution (Ubuntu recommended).

### 1. Install Python Development Tools
```bash
# Update package list
sudo apt update

# Install Python development tools and essential packages
sudo apt install python3-pip python3-dev build-essential

# Install core dependencies via system packages (recommended)
sudo apt install python3-aiofiles python3-psutil python3-pil python3-yaml
```

### 2. Install Additional Dependencies (System-Level)
```bash
# Navigate to the project directory
cd "/mnt/c/Users/ryair/OneDrive - Intel Corporation/Documents/Scripts"

# Install remaining dependencies via pip (system-level)
pip install -r requirements.txt

# Or use the smart installer for guided installation
python3 smart_installer.py
```

### 3. Install Optional External Tools
```bash
# FFmpeg for video processing
sudo apt install ffmpeg

# ImageMagick for advanced image processing
sudo apt install imagemagick

# 7-Zip for archive handling
sudo apt install p7zip-full

# ExifTool for metadata extraction
sudo apt install libimage-exiftool-perl
```

### 4. Test Installation
```bash
# Run compatibility test
python3 cross_platform_test.py

# Run dependency check
python3 enhanced_dependency_manager.py

# Test CLI functionality
python3 file_processing_suite_main.py --help
```

### 5. GUI Usage in WSL
For GUI applications in WSL, you may need X11 forwarding:

```bash
# Install X11 server (if GUI is needed)
# Option 1: Use VcXsrv on Windows
# Option 2: Use Windows 11's built-in WSLg

# Test GUI (requires X11 forwarding)
export DISPLAY=:0
python3 enhanced_gui_v5.py
```

### System-Level Installation Benefits
- **No Environment Management**: Direct installation to system Python
- **Persistent Installation**: Dependencies remain available across sessions
- **System Integration**: Better integration with system tools and services
- **Simplified Deployment**: No need to manage virtual environment activation
- **Performance**: Slightly better performance without virtualization overhead

### Troubleshooting

#### Permission Issues
```bash
# If you encounter permission issues with mounted drives
sudo chmod +x *.py
```

#### Python Module Issues
```bash
# Verify system-level installation
python3 -m pip list | grep -E "(aiofiles|psutil|pyyaml|pillow)"

# If modules aren't found, reinstall
pip install --upgrade aiofiles psutil pyyaml pillow

# For system package conflicts, prefer system packages
sudo apt install python3-aiofiles python3-psutil python3-pil python3-yaml
```

#### Path Issues
```bash
# Ensure proper path to Windows files
ls -la "/mnt/c/Users/ryair/OneDrive - Intel Corporation/Documents/Scripts"
```

### Performance Notes
- WSL provides near-native Linux performance
- File operations on mounted Windows drives may be slower
- For best performance, copy files to WSL filesystem: `cp -r . ~/enhanced_suite/`
- System-level installation provides better performance than virtual environments

### Cross-Platform File Sharing
The suite works seamlessly with files on both WSL and Windows filesystems:
- Windows path: `C:\Users\...`
- WSL mounted path: `/mnt/c/Users/...`
- WSL native path: `~/` or `/home/username/`
