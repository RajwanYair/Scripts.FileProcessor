# Enhanced Password Manager - Feature Documentation

## 🔐 Password Scanner & Brute-Force System

### Overview

The Enhanced Password Manager is a comprehensive system for detecting, analyzing, and cracking password-protected files. It combines intelligent scanning, customer password testing, and sophisticated brute-force algorithms to help you regain access to protected files.

---

## 🌟 Key Features

### 1. **Intelligent File Scanning**

**Capabilities:**
- Scan entire directories for password-protected files
- Recursive scanning of subdirectories
- Support for multiple file types:
  - PDF documents (.pdf)
  - ZIP archives (.zip)
  - RAR archives (.rar)
  - 7-Zip archives (.7z)
  - Word documents (.docx, .doc)
  - Excel spreadsheets (.xlsx, .xls)
  - PowerPoint presentations (.pptx, .ppt)

**Detection Features:**
- Automatic file type identification
- Encryption method detection
- File metadata extraction
- Batch scanning with progress tracking
- Error handling and reporting

### 2. **Multi-Mode Password Cracking**

**Attack Modes:**

#### **Custom Password Mode**
- Test customer-provided passwords first
- Support for password lists
- Per-file custom passwords
- Most efficient mode (tries known passwords)

#### **Common Passwords Mode**
- 1000+ most common passwords
- Password variations (capitalization, numbers)
- Word + year combinations (2020-2025)
- Number patterns (1234, 0000, etc.)
- Success rate: ~30% on weak passwords

#### **Numeric Brute-Force**
- 4-8 digit combinations
- 10,000 to 100,000,000 attempts
- Fast execution (seconds to minutes)
- Good for PIN-style passwords
- Example: 0000 to 99999999

#### **Alphabetic Brute-Force**
- 4-6 character combinations
- Lowercase letters only
- 456,976 to 308,915,776 attempts
- Moderate speed (minutes to hours)
- Warning: Can be very slow

#### **Alphanumeric Brute-Force**
- 4-6 character combinations
- Letters + numbers
- 1,679,616 to 2,176,782,336 attempts
- Slow execution (hours to days)
- Use with caution

### 3. **Parallel Processing**

**Features:**
- Multi-threaded password testing
- Configurable worker threads (default: 4)
- Process multiple files simultaneously
- Efficient CPU utilization
- Progress tracking per file

### 4. **Smart Features**

**Intelligence:**
- Attack mode prioritization
- Success rate tracking
- Password attempt history
- Automatic best-mode selection
- Resource usage optimization

**Progress Monitoring:**
- Real-time attempt counting
- Current password display
- Per-file progress
- Overall statistics
- Time estimation

---

## 📊 Usage Examples

### Example 1: Scan Directory for Protected Files

```python
from pathlib import Path
from core.enhanced_password_scanner import EnhancedPasswordScanner

# Create scanner
scanner = EnhancedPasswordScanner(max_workers=4)

# Scan directory
result = scanner.scan_directory(
    directory=Path("C:/Downloads"),
    recursive=True,
    file_extensions={'.pdf', '.zip', '.rar'}
)

# Display results
print(f"Protected files found: {len(result.protected_files)}")
for file_info in result.protected_files:
    print(f"  • {file_info.path.name} ({file_info.file_type.value})")
```

### Example 2: Crack Password with Custom Passwords

```python
# Customer-provided passwords
custom_passwords = ["password", "123456", "MySecretPwd2024"]

# Attempt to crack
success = scanner.crack_password(
    file_info,
    custom_passwords=custom_passwords,
    attack_modes=[AttackMode.CUSTOM, AttackMode.COMMON],
    max_attempts=5000
)

if success:
    print(f"Password found: {file_info.found_password}")
else:
    print("Password not found")
```

### Example 3: Brute-Force Numeric Password

```python
from core.enhanced_password_scanner import AttackMode

# Try numeric brute-force (4-8 digits)
success = scanner.crack_password(
    file_info,
    attack_modes=[AttackMode.BRUTEFORCE_NUMERIC],
    max_attempts=100000000  # 100 million attempts
)

# With progress callback
def progress_callback(attempts, password):
    if attempts % 1000 == 0:
        print(f"Attempt {attempts}: {password}")

scanner.crack_password(
    file_info,
    attack_modes=[AttackMode.BRUTEFORCE_NUMERIC],
    max_attempts=100000,
    callback=progress_callback
)
```

### Example 4: Parallel Cracking Multiple Files

```python
# Crack multiple files with different passwords
custom_passwords = {
    "document1.pdf": ["password1", "secret1"],
    "archive2.zip": ["password2", "secret2"],
}

results = scanner.crack_multiple(
    protected_files=result.protected_files,
    custom_passwords=custom_passwords,
    attack_modes=[AttackMode.CUSTOM, AttackMode.COMMON],
    max_attempts_per_file=10000
)

# Check results
for filename, success in results.items():
    print(f"{filename}: {'✓ Cracked' if success else '✗ Failed'}")
```

---

## 🎯 GUI Usage

### Launch Password Scanner GUI

```bash
python scripts/password_scanner_gui.py
```

### GUI Features

#### **Tab 1: Scan for Protected Files**

1. **Select Directory**
   - Click "Browse..." to select folder
   - Choose recursive or single-level scan
   - Select file types to scan

2. **File Types**
   - PDF Documents
   - ZIP Archives
   - RAR Archives
   - 7-Zip Archives
   - Word Documents
   - Excel Spreadsheets
   - PowerPoint Presentations

3. **Start Scan**
   - Click "🔍 Start Scan" button
   - View progress bar
   - See results in text area

4. **Results**
   - Total files scanned
   - Protected files found
   - File details (path, type, encryption)
   - Error report

#### **Tab 2: Crack Passwords**

1. **Custom Passwords**
   - Enter known passwords (one per line)
   - These are tried first
   - Most efficient approach

2. **Attack Modes**
   - ☑ Try custom passwords first
   - ☑ Try 1000+ common passwords
   - ☑ Numeric brute-force (4-8 digits)
   - ☐ Alpha brute-force (SLOW!)
   - ☐ Alphanumeric brute-force (VERY SLOW!)

3. **Limits**
   - Set max attempts per file
   - Default: 10,000 attempts
   - Higher = longer time, better chance

4. **Start Cracking**
   - Click "🔓 Start Cracking" button
   - View real-time progress
   - See successful cracks

#### **Tab 3: Results**

1. **Results Table**
   - File name
   - File type
   - Found password
   - Number of attempts
   - Attack mode used

2. **Export Results**
   - Save to TXT or CSV
   - Includes all cracked passwords
   - Easy to share or backup

3. **Clear Results**
   - Clear results table
   - Start fresh scan

---

## ⚡ Performance Guide

### Speed Estimates

**Custom Password Mode**
- Speed: Instant to seconds
- Attempts: 1-100
- Use when: You know possible passwords

**Common Password Mode**
- Speed: Seconds to minutes
- Attempts: 1,000-5,000
- Success rate: 30% on weak passwords
- Use when: Testing weak passwords

**Numeric Brute-Force (4 digits)**
- Speed: Seconds
- Attempts: 10,000
- Use when: Short PIN suspected

**Numeric Brute-Force (6 digits)**
- Speed: Minutes
- Attempts: 1,000,000
- Use when: Medium PIN suspected

**Numeric Brute-Force (8 digits)**
- Speed: Hours
- Attempts: 100,000,000
- Use when: Long PIN suspected

**Alpha Brute-Force (4 chars)**
- Speed: Minutes
- Attempts: 456,976
- Use when: Short word suspected

**Alpha Brute-Force (6 chars)**
- Speed: Days
- Attempts: 308,915,776
- Use when: Desperate (last resort)

### Optimization Tips

1. **Always try custom passwords first**
   - If you know possible passwords, test them
   - Saves hours of brute-forcing

2. **Use common password mode**
   - Very effective on weak passwords
   - Takes only minutes
   - High success rate

3. **Limit numeric brute-force**
   - 4-6 digits is reasonable
   - 8+ digits can take hours
   - Consider probability

4. **Avoid alpha/alphanumeric brute-force**
   - Exponentially slow
   - Only for very short passwords
   - Last resort option

5. **Use parallel processing**
   - Process multiple files at once
   - Utilize all CPU cores
   - Set max_workers=4 or higher

---

## ⚠️ Important Warnings

### Legal & Ethical Considerations

**⚠️ CRITICAL WARNINGS:**

1. **Only use on files you own or have permission to access**
   - Password cracking without authorization is illegal
   - Respect copyright and intellectual property
   - Follow company/organizational policies

2. **Password removal may violate security policies**
   - Some organizations prohibit password removal
   - Check compliance requirements
   - Document authorization

3. **Some encryption is uncrackable**
   - Modern encryption (AES-256) is very strong
   - Long, random passwords are effectively uncrackable
   - Brute-force may be impossible

### Technical Limitations

1. **Brute-force can take very long**
   - Alphanumeric 8+ characters: Years
   - Not practical for strong passwords
   - Consider password recovery instead

2. **No guarantee of success**
   - Strong passwords won't be cracked
   - Maximum attempts may be insufficient
   - Some files may be unrecoverable

3. **Resource intensive**
   - High CPU usage during cracking
   - Can slow down computer
   - Monitor system temperature

---

## 🔧 Technical Details

### Supported File Types

| File Type | Extension | Library | Detection | Cracking |
|-----------|-----------|---------|-----------|----------|
| PDF | .pdf | PyPDF2 | ✓ | ✓ |
| ZIP | .zip | zipfile | ✓ | ✓ |
| RAR | .rar | rarfile | ✓ | ✓ |
| 7-Zip | .7z | py7zr | ✓ | ✓ |
| Word | .docx | zipfile | ✓ | Limited |
| Excel | .xlsx | zipfile | ✓ | Limited |
| PowerPoint | .pptx | zipfile | ✓ | Limited |

### Password Attack Complexity

| Mode | Charset Size | 4 chars | 6 chars | 8 chars |
|------|--------------|---------|---------|---------|
| Numeric | 10 | 10K | 1M | 100M |
| Alpha | 26 | 457K | 309M | 209B |
| Alphanum | 36 | 1.7M | 2.2B | 2.8T |
| Full ASCII | 94 | 78M | 690B | 6,095T |

### Common Password Statistics

**Top 10 Most Common:**
1. 123456 (23%)
2. password (7%)
3. 123456789 (5%)
4. 12345678 (4%)
5. 12345 (3%)
6. 1234567 (2%)
7. password1 (2%)
8. 123123 (2%)
9. qwerty (1%)
10. abc123 (1%)

**Success Rates:**
- Top 100 passwords: ~30% success
- Top 1000 passwords: ~40% success
- Common variations: ~50% success
- Numeric 4-6 digits: ~10% success

---

## 📝 Best Practices

### Before Cracking

1. **Verify ownership**
   - Ensure you have legal right to crack
   - Get written authorization if needed
   - Document the reason

2. **Try to remember**
   - Think about possible passwords
   - Check password managers
   - Ask file creator

3. **Check backups**
   - Look for unprotected copies
   - Check cloud storage
   - Ask colleagues

### During Cracking

1. **Start with custom passwords**
   - Most efficient approach
   - Try variations (caps, numbers)
   - Common patterns

2. **Use common password mode**
   - Quick test of weak passwords
   - Takes only minutes
   - Good success rate

3. **Limit brute-force**
   - Set reasonable max attempts
   - Monitor progress
   - Know when to stop

4. **Save results**
   - Export successful cracks
   - Document passwords found
   - Update password managers

### After Cracking

1. **Change the password**
   - Set a strong, unique password
   - Use password manager
   - Document securely

2. **Remove protection if needed**
   - Only if appropriate
   - Keep original backup
   - Document action

3. **Learn from experience**
   - Use better passwords
   - Enable password recovery
   - Keep passwords documented

---

## 🚀 Advanced Usage

### Custom Password Lists

```python
# Load passwords from file
with open('passwords.txt', 'r') as f:
    passwords = [line.strip() for line in f]

# Add variations
def add_variations(password):
    variations = [
        password,
        password.capitalize(),
        password.upper(),
        password.lower(),
    ]
    # Add numbers
    for i in range(10):
        variations.append(f"{password}{i}")
        variations.append(f"{i}{password}")
    return variations

all_passwords = []
for pwd in passwords:
    all_passwords.extend(add_variations(pwd))

# Use in cracking
scanner.crack_password(file_info, custom_passwords=all_passwords)
```

### Progress Monitoring

```python
import time

start_time = time.time()
attempts_count = [0]

def detailed_callback(attempts, password):
    attempts_count[0] = attempts
    elapsed = time.time() - start_time
    rate = attempts / elapsed if elapsed > 0 else 0
    
    print(f"\rAttempts: {attempts:,} | Rate: {rate:.0f}/s | Current: {password[:20]}", end='')

scanner.crack_password(
    file_info,
    attack_modes=[AttackMode.COMMON, AttackMode.BRUTEFORCE_NUMERIC],
    max_attempts=100000,
    callback=detailed_callback
)

print(f"\nCompleted in {time.time() - start_time:.2f}s")
```

### Batch Processing with Results

```python
import json
from pathlib import Path

# Scan directory
result = scanner.scan_directory(Path("C:/Documents"), recursive=True)

# Crack all files
results = {}
for file_info in result.protected_files:
    success = scanner.crack_password(
        file_info,
        attack_modes=[AttackMode.CUSTOM, AttackMode.COMMON],
        max_attempts=5000
    )
    
    results[str(file_info.path)] = {
        'success': success,
        'password': file_info.found_password if success else None,
        'attempts': len(file_info.attempts),
        'type': file_info.file_type.value
    }

# Save results
with open('crack_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## 📦 Dependencies

### Required

```bash
pip install PyPDF2
```

### Optional (for full functionality)

```bash
# RAR support
pip install rarfile

# 7-Zip support
pip install py7zr

# Better PDF support
pip install pikepdf

# Office document support
pip install python-docx openpyxl python-pptx
```

### Install All

```bash
pip install PyPDF2 rarfile py7zr pikepdf python-docx openpyxl python-pptx
```

---

## 🆘 Troubleshooting

### "Module not found" Error

**Solution:**
```bash
pip install <module_name>
```

### "Password detection not working"

**Causes:**
- Missing optional modules
- Unsupported file format
- Corrupted file

**Solution:**
- Install optional dependencies
- Check file integrity
- Try different file

### "Brute-force too slow"

**Solution:**
- Reduce character set (numeric only)
- Reduce max length (4-6 chars)
- Lower max attempts
- Use parallel processing

### "No password found"

**Reasons:**
- Password is strong/long
- Wrong attack modes
- Insufficient attempts
- Encryption too strong

**Solution:**
- Try custom passwords
- Increase max attempts
- Use multiple attack modes
- Consider password recovery tools

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review error messages
3. Check dependencies installed
4. Test with sample files
5. Review code examples

---

## 🎓 Summary

The Enhanced Password Manager provides:

✅ **Intelligent Scanning** - Find all protected files  
✅ **Multi-Mode Cracking** - Custom, common, brute-force  
✅ **Parallel Processing** - Fast multi-file handling  
✅ **Progress Tracking** - Real-time monitoring  
✅ **GUI Interface** - Easy to use  
✅ **Batch Operations** - Process many files  
✅ **Export Results** - Save cracked passwords  

**Remember:** Always use responsibly and legally!

---

*Enhanced File Processing Suite v6.0 - Password Scanner & Brute-Force System*
