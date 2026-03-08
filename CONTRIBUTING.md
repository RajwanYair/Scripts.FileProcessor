# Contributing to File Processing Suite

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Plugin Development](#plugin-development)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🚀 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable
- **Error messages** and stack traces

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Features

Feature suggestions are welcome! Please:

- **Check existing feature requests** first
- **Provide clear use cases** and benefits
- **Consider implementation complexity**
- **Suggest potential solutions**

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Creating Plugins

We encourage community plugin development! See:

- [Plugin SDK](docs/guides/PLUGIN_SDK.md) for comprehensive guide
- [Plugin examples](examples/plugins/) for reference implementations
- Submit to our [Plugin Marketplace](plugins/plugin_marketplace.json)

### Improving Documentation

Documentation improvements are always appreciated:

- Fix typos or clarify existing docs
- Add examples and tutorials
- Improve API documentation
- Translate documentation

## 🛠️ Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Docker (optional, for containerized development)

### Local Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/file-processor.git
cd file-processor

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r deployment/requirements.txt
pip install -r deployment/requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
pytest tests/ -v
```

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test
pytest tests/
python -m pylint core/ plugins/

# 3. Commit with descriptive messages
git commit -m "feat: add new feature"

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Create Pull Request
```

## 📝 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventions
- [ ] Branch is up-to-date with main

### PR Guidelines

1. **Fill out the PR template** completely
2. **Link related issues** using keywords (fixes #123)
3. **Keep PRs focused** - one feature/fix per PR
4. **Request review** from maintainers
5. **Respond to feedback** promptly
6. **Squash commits** before merging (if requested)

### Review Process

- Maintainers will review within 48-72 hours
- Address feedback in new commits
- Once approved, maintainers will merge
- CI/CD must pass before merge

## 💻 Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some exceptions:

```python
# Maximum line length: 100 characters
# Use 4 spaces for indentation (no tabs)
# Use double quotes for strings
# Use type hints for function signatures

def process_file(file_path: Path, options: Dict[str, Any]) -> ProcessResult:
    """
    Process a file with given options.
    
    Args:
        file_path: Path to the file to process
        options: Processing options dictionary
    
    Returns:
        ProcessResult object with results
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ProcessingError: If processing fails
    """
    pass
```

### Code Quality Tools

We use automated tools to maintain quality:

```bash
# Linting
pylint core/ plugins/ --max-line-length=100

# Type checking
mypy core/ --strict

# Code formatting
black core/ plugins/ --line-length=100

# Import sorting
isort core/ plugins/
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**

```
feat(plugin): add image classification plugin

Implements ResNet50-based image classifier with GPU support.
Includes batch processing and confidence scoring.

Closes #123
```

## 🔌 Plugin Development

### Plugin Structure

```
plugins/your_plugin_name/
├── manifest.json       # Plugin metadata
├── plugin.py          # Main plugin class
├── __init__.py        # Package initialization
├── README.md          # Plugin documentation
├── requirements.txt   # Plugin dependencies (optional)
├── tests/            # Plugin tests
│   └── test_plugin.py
└── examples/         # Usage examples
    └── example.py
```

### Plugin Checklist

- [ ] Inherits from appropriate base class (ProcessorPlugin, etc.)
- [ ] Implements all required methods
- [ ] Includes comprehensive manifest.json
- [ ] Has unit tests with >80% coverage
- [ ] Documentation with usage examples
- [ ] Error handling and validation
- [ ] Thread-safe if processing concurrently
- [ ] Resource cleanup in shutdown()

### Plugin Submission

1. Develop and test plugin locally
2. Create PR with plugin code
3. Update `plugins/plugin_marketplace.json`
4. Provide demo/screenshots
5. Maintainers will review and test
6. Once approved, plugin goes live in marketplace

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── test_core.py
│   └── test_plugins.py
├── integration/       # Integration tests
│   └── test_workflows.py
├── e2e/              # End-to-end tests
│   └── test_api.py
└── fixtures/         # Test fixtures
    └── sample_files/
```

### Writing Tests

```python
import pytest
from pathlib import Path

class TestImageOptimizer:
    """Test suite for image optimizer plugin"""
    
    @pytest.fixture
    def sample_image(self, tmp_path):
        """Create sample test image"""
        # Setup code
        return image_path
    
    def test_compress_image(self, sample_image):
        """Test image compression"""
        plugin = ImageOptimizerPlugin()
        result = plugin.process(sample_image, quality=85)
        
        assert result["success"] is True
        assert result["size_reduction"] > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, tmp_path):
        """Test batch image processing"""
        # Test code
        pass
```

### Test Requirements

- **Coverage**: Minimum 80% for new code
- **Performance**: Tests should complete in <5 seconds
- **Isolation**: Tests must be independent
- **Naming**: `test_<functionality>_<condition>`
- **Documentation**: Docstrings for test classes/methods

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_plugins.py

# Run with coverage
pytest --cov=core --cov=plugins --cov-report=html

# Run specific test
pytest tests/unit/test_plugins.py::TestImageOptimizer::test_compress_image

# Run integration tests only
pytest tests/integration/
```

## 📚 Documentation

### Documentation Standards

- **Clear and concise** writing
- **Code examples** for all features
- **Up-to-date** with current implementation
- **Well-organized** with table of contents
- **Searchable** with good headings

### Documentation Structure

```
docs/
├── guides/              # User guides
│   ├── getting-started.md
│   ├── installation.md
│   └── deployment.md
├── tutorials/           # Step-by-step tutorials
│   ├── creating-first-plugin.md
│   └── building-workflow.md
├── api/                # API documentation
│   ├── rest-api.md
│   └── plugin-api.md
└── architecture/       # System architecture
    ├── overview.md
    └── plugin-system.md
```

### API Documentation

Use docstrings for auto-generated API docs:

```python
def process_file(file_path: Path, options: Dict[str, Any]) -> ProcessResult:
    """
    Process a file with specified options.
    
    This function handles all file processing operations including
    validation, transformation, and result generation.
    
    Args:
        file_path: Absolute path to the file to process. Must exist
            and be readable.
        options: Dictionary of processing options:
            - quality (int): Compression quality 1-100
            - resize (bool): Whether to resize the file
            - format (str): Output format (jpeg, png, webp)
    
    Returns:
        ProcessResult object containing:
            - success (bool): Whether processing succeeded
            - output_path (Path): Path to processed file
            - metadata (dict): Processing metadata
    
    Raises:
        FileNotFoundError: If file_path doesn't exist
        PermissionError: If file is not readable
        ProcessingError: If processing fails
    
    Example:
        >>> result = process_file(
        ...     Path("image.jpg"),
        ...     {"quality": 85, "resize": True}
        ... )
        >>> print(result.success)
        True
    """
    pass
```

## 🏆 Recognition

Contributors will be:

- Listed in [AUTHORS.md](AUTHORS.md)
- Credited in release notes
- Featured on project website (if applicable)
- Given contributor badge in GitHub
- Invited to maintainer team (for significant contributions)

## 📞 Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/YOUR_ORG/file-processor/discussions)
- **Chat**: Join our [Discord server](https://discord.gg/fileprocessor)
- **Email**: <contribute@fileprocessor.dev>
- **Office Hours**: Weekly video calls (see calendar)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to File Processing Suite! 🎉

**Questions?** Check our [FAQ](docs/guides/FAQ.md) or reach out to maintainers.
