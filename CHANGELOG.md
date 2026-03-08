# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `.pre-commit-config.yaml` with ruff, mypy, bandit, conventional-commit hooks
- `.editorconfig` for cross-editor consistency
- `.github/workflows/codeql.yml` — SAST security scanning via CodeQL
- `.github/workflows/release.yml` — automated release on version tags
- `.github/workflows/labeler.yml` — auto-label PRs by changed path
- `.github/labeler.yml` — path-to-label mapping
- `CITATION.cff` — academic citation metadata
- `noxfile.py` — task automation (lint, test, docs, release)
- `Makefile` — developer convenience targets
- `VERSION` — single source of truth for version string
- `src/file_processor/__main__.py` — `python -m file_processor` support
- `src/file_processor/core/processor.py` — central `FileProcessor` engine
- `src/file_processor/core/results.py` — `ProcessingResult` / `BatchResult` dataclasses
- `src/file_processor/utils/__init__.py` — shared utility re-exports
- `src/file_processor/utils/config_loader.py` — YAML config with env-var substitution
- Full test suite: `tests/conftest.py`, unit tests, integration tests, hypothesis tests
- `docs/ARCHITECTURE.md` — system architecture document

### Changed

- CI/CD workflow modernised: **ruff** replaces black + flake8 + pylint + isort
- CI matrix: Python 3.11 / 3.12 / 3.13 × Ubuntu / Windows / macOS
- `.github/CODEOWNERS` fixed (was malformed with literal `\n`)
- `.github/dependabot.yml` groups updated to reference ruff instead of legacy tools
- `.github/copilot-instructions.md` typos corrected
- `.github/contributing.md` toolchain references updated to ruff
- `.github/security.md` — versions table and reporting instructions improved
- `.github/readme.md` — structure diagram updated to reflect current layout
- `README.md` — modernised header with accurate CI/CodeQL badges
- `ROADMAP.md` — rewritten with concrete sprint definitions
- `SECURITY.md` — covered versions updated to 7.x; private-reporting instructions added
- `Dockerfile` — corrected `requirements.txt` path and CMD entry point
- `docker-compose.yml` — updated service entry point

## [7.0.0] - 2026-01-07

### Added - Sprint 1: Modern Architecture & Plugin System

#### Plugin System

- Plugin architecture with 5 types: Processor, Format, Hook, Storage, Analyzer
- Hot-reload capability for development
- Sandboxed execution with isolated directories
- Plugin lifecycle management (initialize, process, shutdown)
- Event hooks system (pre/post-process)
- Plugin metadata validation
- 3 example plugins:
  - Image Optimizer (compression, resize, format conversion)
  - PDF Processor (merge, split, extract, compress)
  - Text Analyzer (statistics, sentiment, keywords)

#### REST API

- FastAPI server with async support
- 20+ API endpoints for file operations and plugin management
- WebSocket support for real-time updates
- OpenAPI/Swagger documentation
- JWT and API key authentication
- Rate limiting and throttling
- Marketplace integration API

#### Plugin Marketplace

- Plugin catalog with metadata
- 8 category system (Image, Document, Text, Video, Cloud, Automation, Security, AI/ML)
- Search and discovery functionality
- Installation manager
- Update checking
- Featured plugins section

#### Docker & Containerization

- Multi-stage Dockerfile for optimized builds
- Docker Compose with 9 services:
  - API Server (FastAPI + Uvicorn)
  - PostgreSQL (database)
  - Redis (cache + sessions)
  - Apache Kafka (event streaming)
  - Prometheus (metrics)
  - Grafana (dashboards)
  - NGINX (load balancer)
  - Celery Worker (background jobs)
  - Flower (task monitoring)

#### CI/CD Pipeline

- GitHub Actions workflow
- Multi-platform testing (Ubuntu, Windows, macOS)
- Python 3.10, 3.11, 3.12 support
- Automated testing with pytest
- Security scanning (Bandit, Safety)
- Docker image builds
- Deployment automation

#### Documentation

- Comprehensive Plugin SDK guide
- API documentation with examples
- Docker deployment guide
- Quick Start guide
- Sprint planning documents
- Architecture documentation

### Changed

- Evolved from monolithic desktop app to cloud-native microservices
- Modernized architecture for scalability
- Enhanced async processing with event-driven design
- Improved error handling and logging

### Technical Improvements

- Added comprehensive test suite (60% coverage)
- Implemented health checks and monitoring
- Added distributed tracing support
- Enhanced security with authentication layers

## [6.0.0] - 2025-10-19

### Added

- Enhanced password scanner with multi-format support
- Advanced metadata extraction
- Improved series grouping algorithm
- Hardware detection and optimization
- Intelligent caching system
- Zero-copy operations for performance
- Feature registry system
- Smart imports for better dependency management

### Changed

- Major GUI overhaul with modern design
- Improved cross-platform compatibility
- Enhanced async processing
- Better error handling and reporting

### Fixed

- Memory leaks in large file processing
- Unicode handling issues
- Path handling across platforms
- Dependency conflicts

## [5.0.0] - 2025-06-15

### Added

- Cross-platform support (Windows, Linux, macOS)
- GUI application with dashboard
- Async processing for better performance
- Comprehensive configuration system
- 22 processing features across 10 categories

### Features

- Format detection (200+ formats)
- Filename sanitization
- Extension normalization
- Metadata extraction (EXIF, PDF)
- Duplicate detection
- Series grouping
- Password-protected file handling
- Enhanced deduplication

## [4.0.0] - 2025-03-10

### Added

- Advanced filename processing
- Batch operations support
- Configuration file support (YAML)
- Logging system

### Changed

- Refactored core processing engine
- Improved CLI interface

## [3.0.0] - 2024-12-01

### Added

- Metadata extraction
- Format detection
- Basic GUI interface

## [2.0.0] - 2024-09-15

### Added

- Duplicate file detection
- Series grouping functionality

## [1.0.0] - 2024-06-01

### Added

- Initial release
- Basic file processing capabilities
- Filename sanitization
- Command-line interface

---

## Version Naming Convention

- **Major (X.0.0)**: Breaking changes, major feature additions
- **Minor (x.Y.0)**: New features, non-breaking changes
- **Patch (x.y.Z)**: Bug fixes, minor improvements

## Release Types

- **Sprint Releases**: Major versions every 4 months
- **Feature Releases**: Minor versions monthly
- **Bug Fix Releases**: Patch versions as needed
- **Hotfixes**: Critical security/bug fixes

## Links

- [GitHub Releases](https://github.com/fileprocessor/releases)
- [Migration Guides](docs/guides/)
- [Roadmap](ROADMAP.md)

[Unreleased]: https://github.com/fileprocessor/compare/v7.0.0...HEAD
[7.0.0]: https://github.com/fileprocessor/compare/v6.0.0...v7.0.0
[6.0.0]: https://github.com/fileprocessor/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/fileprocessor/compare/v4.0.0...v5.0.0
[4.0.0]: https://github.com/fileprocessor/compare/v3.0.0...v4.0.0
[3.0.0]: https://github.com/fileprocessor/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/fileprocessor/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/fileprocessor/releases/tag/v1.0.0
