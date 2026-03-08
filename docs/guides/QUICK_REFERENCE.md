# 🎯 Quick Reference Card - Enhanced File Processing Suite v5.0

## 📌 Most Used Commands (Copy & Paste Ready)

### 🚀 **Quick Start (Easiest)**
```bash
# Universal launcher with interactive menu
python deployment/universal_launcher.py

# Or launch GUI directly
python main.py --gui
python main.py
```

### 🔧 **Filename Processing (Most Common Use Case)**
```bash
# Safe preview (ALWAYS DO THIS FIRST!)
python utilities/standalone_filename_processor.py /path/to/files --dry-run

# Apply changes after reviewing
python utilities/standalone_filename_processor.py /path/to/files

# Process only specific file types
python utilities/standalone_filename_processor.py /path/to/files --patterns "*.jpg" "*.png" "*.mp4"

# Verbose output to see what's happening
python utilities/standalone_filename_processor.py /path/to/files --dry-run --verbose
```

### 📋 **Common Operations**
```bash
# Sanitize filenames (remove illegal characters)
python main.py --cli /path/to/files --operations sanitize_filename

# Remove duplicates
python main.py --cli /path/to/files --operations deduplicate

# Group series (vol.1, vol.2, etc.)
python main.py --cli /path/to/files --operations group_series

# Extract metadata
python main.py --cli /path/to/files --operations extract_metadata

# Do everything
python main.py --cli /path/to/files --operations sanitize deduplicate group_series extract_metadata --recursive
```

### ℹ️ **System Information & Testing**
```bash
# Quick system check (fast)
python deployment/quick_verify.py

# Detailed system info
python main.py --system-info

# Full test suite (takes a few minutes)
python deployment/comprehensive_test_runner.py

# Cross-platform compatibility test
python deployment/cross_platform_test.py
```

### 🛠️ **Installation & Setup**
```bash
# Install dependencies (interactive)
python deployment/smart_installer.py

# Check and install dependencies
python deployment/enhanced_dependency_manager.py

# Verify installation
python deployment/quick_verify.py
```

### 📊 **Performance & Monitoring**
```bash
# Run benchmark
python main.py --benchmark

# Launch performance dashboard (web interface)
python scripts/performance_monitoring_dashboard.py
```

---

## 🎯 Platform-Specific Commands

### Windows (PowerShell/CMD)
```powershell
# Using batch files
.\deployment\Launch_GUI.bat
.\deployment\Launch_Standalone_Processor.bat "C:\path\to\files"

# Using Python directly
python main.py --gui
python utilities\standalone_filename_processor.py C:\path\to\files --dry-run
```

### Linux / WSL / macOS
```bash
# Using shell scripts (make executable first)
chmod +x deployment/*.sh
./deployment/launch_gui.sh
./deployment/launch_standalone_processor.sh /path/to/files

# Using Python directly
python3 main.py --gui
python3 utilities/standalone_filename_processor.py /path/to/files --dry-run
```

---

## 📚 20+ Runnable Scripts Summary

| # | Script | Purpose | Standalone |
|---|--------|---------|------------|
| 1 | `main.py` | Universal entry point | ✅ |
| 2 | `deployment/universal_launcher.py` | Cross-platform launcher | ✅ |
| 3 | `utilities/standalone_filename_processor.py` | Quick filename processor | ✅ |
| 4 | `scripts/enhanced_gui_v5.py` | GUI interface | ✅ |
| 5 | `scripts/file_processing_suite_main.py` | Full CLI suite | ✅ |
| 6 | `scripts/performance_monitoring_dashboard.py` | Web dashboard | ✅ |
| 7 | `deployment/quick_verify.py` | Quick verification | ✅ |
| 8 | `deployment/comprehensive_test_runner.py` | Full test suite | ✅ |
| 9 | `deployment/cross_platform_test.py` | Platform tests | ✅ |
| 10 | `deployment/smart_installer.py` | Interactive installer | ✅ |
| 11 | `deployment/enhanced_dependency_manager.py` | Dependency manager | ✅ |
| 12 | `deployment/Launch_GUI.bat` | Windows GUI launcher | ✅ |
| 13 | `deployment/launch_gui.sh` | Linux GUI launcher | ✅ |
| 14 | `deployment/Launch_Standalone_Processor.bat` | Windows processor | ✅ |
| 15 | `deployment/launch_standalone_processor.sh` | Linux processor | ✅ |
| 16 | `utilities/cleanup_pip_user_packages.py` | Package cleanup | ✅ |
| 17 | `scripts/setup_performance_enhancements.py` | Performance setup | ✅ |
| 18 | `tests/test_enhanced_suite.py` | Unit tests | ✅ |
| 19 | `tests/validate_release.py` | Release validation | ✅ |
| 20+ | Various other test scripts | Testing & validation | ✅ |

---

## 💡 Workflow Recommendations

### **For First-Time Users**
1. Run verification: `python deployment/quick_verify.py`
2. Try the universal launcher: `python deployment/universal_launcher.py`
3. Start with dry-run: `python utilities/standalone_filename_processor.py . --dry-run`

### **For Batch Processing**
1. Preview changes: Add `--dry-run` to any command
2. Test on small directory first
3. Always create backups (enabled by default)
4. Use `--verbose` to see detailed progress

### **For Developers**
1. Check system: `python main.py --system-info`
2. Run tests: `python deployment/comprehensive_test_runner.py`
3. Run benchmarks: `python main.py --benchmark`
4. Import core modules in your scripts

### **For Automation**
1. Use CLI mode: `python main.py --cli [dir] --operations [ops]`
2. Create config files: `--config my_config.yaml`
3. Use `--pattern` to filter files: `--pattern "*.jpg"`
4. Output results to file: `--output results.json`

---

## 🔥 Top 5 Most Used Commands

### 1️⃣ **Launch GUI** (Easiest for beginners)
```bash
python main.py
```

### 2️⃣ **Clean Filenames (Safe Preview)**
```bash
python utilities/standalone_filename_processor.py /path/to/files --dry-run
```

### 3️⃣ **Process Files (Apply Changes)**
```bash
python utilities/standalone_filename_processor.py /path/to/files
```

### 4️⃣ **System Check**
```bash
python deployment/quick_verify.py
```

### 5️⃣ **Full Suite Processing**
```bash
python main.py --cli /path/to/files --operations all --recursive
```

---

## ❓ Help Commands

Every script supports `--help`:
```bash
python main.py --help
python utilities/standalone_filename_processor.py --help
python deployment/universal_launcher.py --help
python scripts/file_processing_suite_main.py --help
```

---

## 📖 Documentation Files

- 📄 **FEATURE_LIST.md** - Complete feature list and script details
- 📄 **CROSS_PLATFORM_COMPLETE.md** - Cross-platform enhancements summary
- 📄 **docs/CROSS_PLATFORM_GUIDE.md** - Platform-specific instructions
- 📄 **docs/CROSS_PLATFORM_ENHANCEMENT_SUMMARY.md** - Technical details
- 📄 **README.md** - Main project documentation

---

## 🎓 Learning Path

1. **Week 1**: Start with GUI and standalone processor
2. **Week 2**: Learn CLI commands and operations
3. **Week 3**: Explore configuration files and automation
4. **Week 4**: Dive into core modules and custom scripts

---

**Pro Tip:** Always use `--dry-run` first to preview changes before applying them!

**Safety First:** The suite creates backups by default. You can disable with `--no-backup` if needed.

**Get Help:** Run any script with `--help` for detailed usage information.
