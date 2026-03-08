# Test Suite Documentation

## Overview

This directory contains comprehensive test suites for the Enhanced File Processing Suite v5.0.

## Test Files

### 1. test_comprehensive_suite.py
**Purpose:** Full unit test coverage of all core modules  
**Test Count:** 31 test cases  
**Requirements:** Core dependencies (aiofiles, psutil, pyyaml)

**Test Coverage:**
- UnifiedFilenameProcessor (6 tests)
- AdvancedSimilarityMatcher (3 tests)
- EnhancedFormatDetector (4 tests)
- HardwareDetector (3 tests)
- CrossPlatformUtils (2 tests)
- AsyncFileProcessor (1 test)
- ProcessingResult (2 tests)
- FileInfo (1 test)
- ManagedFileOperation (2 tests)
- EnhancedDeduplicator (1 test)
- AdvancedMetadataExtractor (1 test)
- AdvancedSeriesGrouper (1 test)
- ToolDetector (2 tests)

**Usage:**
```bash
python tests/test_comprehensive_suite.py
```

### 2. test_basic_integration.py
**Purpose:** Basic integration tests without external dependencies  
**Test Count:** 6 test suites  
**Requirements:** None (uses fallback implementations)

**Test Coverage:**
- Core module imports
- Duplicate class detection
- Basic functionality verification
- Immutability checks

**Usage:**
```bash
python tests/test_basic_integration.py
```

### 3. analyze_deduplication.py
**Purpose:** Code duplication analysis and reporting  
**Requirements:** None

**Features:**
- Automatic duplicate class detection
- Import pattern analysis
- Consolidation recommendations
- Migration guidance

**Usage:**
```bash
python tests/analyze_deduplication.py
```

### 4. demo_reorganization.py
**Purpose:** Interactive demo of the reorganized project structure  
**Type:** GUI demonstration  
**Requirements:** tkinter

### 5. test_reorganization.py
**Purpose:** Basic structural tests  
**Type:** Simple verification script

## Running Tests

### Prerequisites

Install core dependencies:
```bash
pip install aiofiles psutil pyyaml
```

For full feature testing:
```bash
pip install -r ../requirements.txt
```

### Run All Tests

```bash
# Run basic tests (no dependencies required)
python test_basic_integration.py

# Run comprehensive tests (requires dependencies)
python test_comprehensive_suite.py

# Run deduplication analysis
python analyze_deduplication.py
```

### Expected Results

**With Dependencies:**
- test_comprehensive_suite.py: 31/31 tests pass
- test_basic_integration.py: 6/6 tests pass

**Without Dependencies:**
- test_basic_integration.py: Limited functionality
- test_comprehensive_suite.py: Will report missing dependencies

## Test Structure

### Test Organization

```
tests/
├── test_comprehensive_suite.py    # Full unit tests
├── test_basic_integration.py      # Integration tests
├── analyze_deduplication.py       # Code analysis tool
├── demo_reorganization.py         # Interactive demo
├── test_reorganization.py         # Basic structural tests
└── README.md                      # This file
```

### Adding New Tests

1. Create a new test class inheriting from `unittest.TestCase`
2. Add test methods starting with `test_`
3. Update the test suite in `run_all_tests()`
4. Document in this README

Example:
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Setup test fixtures."""
        pass
    
    def test_feature_works(self):
        """Test that feature works correctly."""
        result = new_feature()
        self.assertTrue(result)
```

## Continuous Integration

### Recommended CI/CD Setup

```yaml
# Example .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python tests/test_basic_integration.py
          python tests/test_comprehensive_suite.py
```

## Test Coverage Goals

- **Current:** ~60% (core modules)
- **Target:** 90% (all modules)
- **Critical paths:** 100% (file operations, data integrity)

## Troubleshooting

### Common Issues

**1. Import Errors**
```
ModuleNotFoundError: No module named 'aiofiles'
```
**Solution:** Install dependencies: `pip install aiofiles psutil pyyaml`

**2. Test Failures**
```
AttributeError: 'NoneType' object has no attribute 'category'
```
**Solution:** Check if format_detector is properly initialized

**3. Permission Errors**
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** Run tests from project root with proper permissions

## Contributing

When adding new features:
1. Add corresponding tests
2. Ensure 80%+ test coverage
3. Update this README
4. Run all tests before committing

## Support

For test-related issues:
- Check docs/releases/CODE_CONSOLIDATION_REPORT.md
- Review individual test file docstrings
- Run analyze_deduplication.py for code structure analysis

---

**Last Updated:** October 19, 2025  
**Test Suite Version:** 5.0.0
