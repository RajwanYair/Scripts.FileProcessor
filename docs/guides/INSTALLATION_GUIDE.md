# Installation and Setup Guide - Enhanced File Processing Suite v5.0

## 🚀 Quick Start Installation (System-Level)

### Minimum Requirements
- **Python**: 3.9+ (Recommended: 3.12+ for optimal performance)
- **Operating System**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+), WSL2
- **Memory**: 4GB RAM minimum (16GB+ recommended for large datasets)
- **Storage**: 1GB free space for temporary files

### Basic Installation (2 minutes)

1. **Download the Suite**
   ```bash
   # Clone the repository
   git clone https://github.com/yourrepo/enhanced-file-suite.git
   cd enhanced-file-suite
   
   # Or download and extract the ZIP file
   ```

2. **Install Core Dependencies (System-Level)**
   ```bash
   # Install required packages directly to system Python
   pip install -r requirements.txt
   
   # Verify installation
   python enhanced_dependency_manager.py
   python file_processing_suite_main.py --help
   ```

3. **Launch the Application**
   ```bash
   # GUI Mode (Recommended)
   python enhanced_gui_v5.py
   
   # CLI Mode
   python file_processing_suite_main.py --help
   ```

### Full Installation (Advanced Features)

For maximum performance and all features:

```bash
# Install all dependencies including optional packages
pip install -r requirements.txt

# Install GPU acceleration (NVIDIA only)
pip install cupy-cuda12x torch

# Install advanced image processing
pip install opencv-python numpy scikit-image

# Install video processing support
pip install imageio[ffmpeg]
```

## 🔧 Detailed Installation Guide

### Step 1: Python Environment Setup

#### Option A: Using Python Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv file_suite_env

# Activate environment
# On Windows:
file_suite_env\Scripts\activate
# On macOS/Linux:
source file_suite_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### Option B: Using Conda
```bash
# Create conda environment
conda create -n file_suite python=3.11
conda activate file_suite

# Install pip in conda environment
conda install pip
```

### Step 2: Core Package Installation

```bash
# Install core requirements
pip install pyyaml>=6.0.1 pillow>=10.1.0 tqdm>=4.65.0
pip install rarfile py7zr patoolib reportlab PyPDF2
pip install python-magic psutil rapidfuzz

# Verify core installation
python -c "import yaml, PIL, tqdm; print('Core packages installed successfully')"
```

### Step 3: Platform-Specific Setup

#### Windows Setup
```bash
# Install Windows-specific packages
pip install pywin32

# For advanced file type detection
pip install python-magic-bin

# Verify Windows setup
python -c "import win32api; print('Windows integration ready')"
```

#### macOS Setup
```bash
# Install macOS-specific packages
pip install pyobjc

# Install Homebrew packages for better file type detection
brew install libmagic

# Verify macOS setup
python -c "import objc; print('macOS integration ready')"
```

#### Linux/WSL Setup
```bash
# Install system packages (Ubuntu/Debian)
sudo apt update
sudo apt install python3-magic libmagic1 libmagic-dev

# Install Linux-specific Python packages
pip install python-magic-bin

# Verify Linux setup
python -c "import magic; print('Linux integration ready')"
```

### Step 4: GPU Acceleration Setup (Optional)

#### NVIDIA GPU Setup
```bash
# 1. Install NVIDIA CUDA Toolkit (version 12.x recommended)
# Download from: https://developer.nvidia.com/cuda-downloads

# 2. Install CuPy for GPU acceleration
pip install cupy-cuda12x

# 3. Verify GPU installation
python -c "import cupy; print(f'GPU available: {cupy.cuda.is_available()}')"

# 4. Test GPU acceleration
python -c "
import cupy as cp
x = cp.array([1, 2, 3])
print(f'GPU test successful: {x.device}')
"
```

#### AMD GPU Setup (OpenCL)
```bash
# Install OpenCL support (experimental)
pip install pyopencl

# Note: AMD GPU acceleration is experimental and may not work with all features
```

### Step 5: External Tool Integration

#### FFmpeg (Video Processing)
```bash
# Windows (using Chocolatey)
choco install ffmpeg

# macOS (using Homebrew)  
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

#### ImageMagick (Advanced Image Processing)
```bash
# Windows: Download from https://imagemagick.org/script/download.php#windows
# macOS
brew install imagemagick

# Linux
sudo apt install imagemagick

# Verify installation
magick -version
```

#### 7-Zip (Archive Processing)
```bash
# Windows: Download from https://www.7-zip.org/
# macOS
brew install p7zip

# Linux
sudo apt install p7zip-full

# Verify installation
7z
```

#### ExifTool (Metadata Extraction)
```bash
# Windows: Download from https://exiftool.org/
# macOS
brew install exiftool

# Linux
sudo apt install exiftool

# Verify installation
exiftool -ver
```

## ⚙️ Configuration Setup

### Initial Configuration

1. **Copy Default Configuration**
   ```bash
   # The default configuration file is included
   # Customize it for your needs
   cp file_processing_suite_config.yaml my_config.yaml
   ```

2. **Edit Configuration**
   ```yaml
   # Edit the configuration file
   general:
     default_source_directory: "./my_input"
     default_output_directory: "./my_output"
   
   performance:
     enable_gpu: true  # Set to false if no GPU
     max_workers: "auto"
   ```

3. **Test Configuration**
   ```bash
   # Validate configuration
   python file_processing_suite_main.py --validate-config
   
   # Show effective configuration
   python file_processing_suite_main.py --show-config
   ```

## 🧪 Verification and Testing

### Basic Functionality Test
```bash
# Create test directories
mkdir test_input test_output

# Copy some test files to test_input
# Run basic test
python file_processing_suite_main.py --source test_input --dest test_output --organize --dry-run

# Check the dry-run results
```

### Advanced Feature Test
```bash
# Test GPU acceleration (if available)
python -c "
from core.hardware_detector import HardwareDetector
hw = HardwareDetector.detect_hardware()
print(f'GPU Available: {hw.gpu_available}')
print(f'GPU Backend: {hw.gpu_backend}')
"

# Test format support
python -c "
from core.enhanced_format_support import get_format_statistics
stats = get_format_statistics()
print(f'Supported formats: {stats[\"total_formats\"]}')
"
```

### GUI Test
```bash
# Launch GUI in test mode
python file_processing_suite_gui.py --test-mode

# Check all tabs are accessible
# Verify configuration loading
# Test file selection dialogs
```

## 🔍 Troubleshooting Installation

### Common Issues and Solutions

#### Issue: "Import Error: No module named 'yaml'"
```bash
# Solution: Install PyYAML
pip install pyyaml>=6.0.1
```

#### Issue: "CUDA not found" or GPU acceleration not working
```bash
# Solution: Install CUDA toolkit and CuPy
# 1. Download CUDA from NVIDIA website
# 2. Install appropriate CuPy version
pip install cupy-cuda12x  # For CUDA 12.x
# or
pip install cupy-cuda11x  # For CUDA 11.x
```

#### Issue: "Magic number error" or file type detection problems
```bash
# Windows solution:
pip install python-magic-bin

# macOS solution:
brew install libmagic
pip install python-magic

# Linux solution:
sudo apt install libmagic1 libmagic-dev python3-magic
```

#### Issue: GUI doesn't start or crashes
```bash
# Check tkinter installation
python -c "import tkinter; print('GUI libraries available')"

# On Linux, install tkinter:
sudo apt install python3-tk

# Test basic GUI
python -c "
import tkinter as tk
root = tk.Tk()
root.title('Test')
print('GUI test successful')
root.destroy()
"
```

#### Issue: Permission errors during processing
```bash
# Run with appropriate permissions
# Windows: Run as Administrator
# macOS/Linux: Check file permissions
chmod +x file_processing_suite_main.py
```

### Performance Issues

#### Slow Processing
1. **Enable GPU acceleration**
   ```yaml
   performance:
     enable_gpu: true
     gpu_batch_size: 1000
   ```

2. **Increase worker threads**
   ```yaml
   performance:
     max_workers: 8  # Or number of CPU cores
   ```

3. **Optimize memory usage**
   ```yaml
   performance:
     memory_limit_gb: 16  # Adjust based on available RAM
   ```

#### Memory Issues
1. **Reduce batch size**
   ```yaml
   performance:
     max_workers: 2
     memory_limit_gb: 4
   ```

2. **Enable memory monitoring**
   ```yaml
   performance:
     enable_memory_monitoring: true
   ```

## 📊 System Compatibility Testing

### Automated Compatibility Check
```bash
# Run comprehensive system check
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import yaml, PIL, tqdm
    print('✓ Core packages available')
except ImportError as e:
    print(f'✗ Missing core package: {e}')

# Test GPU availability
try:
    import cupy
    print(f'✓ GPU acceleration available: {cupy.cuda.is_available()}')
except ImportError:
    print('○ GPU acceleration not installed (optional)')

# Test platform features
import platform
print(f'Platform: {platform.system()} {platform.release()}')
"
```

### Manual Testing Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] Core packages install without errors
- [ ] GUI launches successfully
- [ ] Configuration file loads and validates
- [ ] File selection dialogs work
- [ ] Basic file processing completes
- [ ] GPU acceleration detected (if available)
- [ ] External tools accessible (if installed)
- [ ] Log files created successfully
- [ ] Output directories created properly

## 🚀 Performance Optimization

### Recommended Settings by Use Case

#### Photo Enthusiast (1,000-10,000 photos)
```yaml
performance:
  enable_gpu: true
  max_workers: "auto"
  memory_limit_gb: 8

formats:
  images:
    default_output_format: "webp"
    preserve_metadata: true
```

#### Professional Photographer (10,000+ photos)
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

#### Document Management (Office environment)
```yaml
performance:
  enable_gpu: false
  max_workers: 4
  memory_limit_gb: 8

security:
  create_backup_before_processing: true
  verify_file_integrity: true
```

## 📞 Getting Help

### Support Resources
- **Configuration Guide**: See `CONFIGURATION_GUIDE.md`
- **User Manual**: See `README.md`
- **Release Notes**: See `RELEASE_NOTES_v5.md`
- **Troubleshooting**: Enable debug logging in configuration

### Debug Information Collection
```bash
# Generate debug information
python file_processing_suite_main.py --system-info > system_info.txt
python file_processing_suite_main.py --show-config > config_dump.txt

# Include these files when requesting support
```

### Community and Support
- Check GitHub Issues for common problems
- Review documentation for advanced configuration
- Enable detailed logging for specific error analysis

---

**Installation Complete!** 🎉

Your Enhanced File Processing Suite v5.0 is now ready for professional use. Start with the GUI for an intuitive experience, or use the command line for automation and scripting.
