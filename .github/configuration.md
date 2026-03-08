# GitHub Configuration Guide

## Overview

This guide explains all GitHub-specific configurations for the File Processing Suite project. Follow these instructions to properly configure your fork or maintain the project.

---

## 📋 Table of Contents

1. [Repository Settings](#repository-settings)
2. [Branch Protection](#branch-protection)
3. [Secrets Configuration](#secrets-configuration)
4. [Issue Templates](#issue-templates)
5. [Workflows](#workflows)
6. [Labels](#labels)
7. [Discussions](#discussions)
8. [Security](#security)

---

## 🔧 Repository Settings

### General Settings

Navigate to **Settings** → **General**:

```yaml
Repository name: file-processing-suite
Description: AI-powered, cloud-native file processing platform with plugin architecture
Website: https://fileprocessor.com
Topics:
  - file-processing
  - python
  - fastapi
  - plugins
  - docker
  - ai-ml
  - microservices
  - cross-platform

Features:
  ✓ Wikis (for additional documentation)
  ✓ Issues
  ✓ Discussions
  ✓ Projects (for roadmap tracking)
  ✗ Sponsorships (enable when ready)

Pull Requests:
  ✓ Allow squash merging
  ✓ Allow rebase merging
  ✗ Allow merge commits
  ✓ Automatically delete head branches
  ✓ Allow auto-merge
```

---

## 🛡️ Branch Protection

### Main Branch Protection

Navigate to **Settings** → **Branches** → **Add rule**:

**Branch name pattern:** `main`

```yaml
Protect matching branches:
  ✓ Require pull request reviews before merging
    - Required approvals: 1
    ✓ Dismiss stale reviews when new commits are pushed
    ✓ Require review from Code Owners
    ✗ Restrict who can dismiss pull request reviews

  ✓ Require status checks to pass before merging
    ✓ Require branches to be up to date before merging
    Required status checks:
      - lint
      - test (ubuntu-latest, 3.11)
      - test (windows-latest, 3.11)
      - test (macos-latest, 3.11)
      - security

  ✓ Require conversation resolution before merging
  ✓ Require signed commits
  ✓ Require linear history
  ✓ Include administrators
  ✗ Allow force pushes
  ✗ Allow deletions
```

### Develop Branch Protection

**Branch name pattern:** `develop`

```yaml
Protect matching branches:
  ✓ Require pull request reviews before merging
    - Required approvals: 1
  ✓ Require status checks to pass before merging
  ✗ Require linear history
  ✗ Include administrators
```

---

## 🔐 Secrets Configuration

Navigate to **Settings** → **Secrets and variables** → **Actions**:

### Required Secrets

```bash
# Docker Registry
DOCKER_USERNAME       # Docker Hub username
DOCKER_PASSWORD       # Docker Hub access token (not password!)

# Package Registry
PYPI_API_TOKEN       # PyPI API token for package publishing

# Security Scanning
SAFETY_API_KEY       # PyUp Safety API key (optional)

# Deployment (Production)
PROD_SSH_KEY         # SSH key for production deployment
PROD_HOST            # Production server hostname
PROD_USER            # Production server username

# Monitoring (Optional)
SENTRY_DSN           # Sentry error tracking DSN
DATADOG_API_KEY      # Datadog monitoring API key
```

### How to Add Secrets

1. Go to repository Settings
2. Navigate to Secrets and variables → Actions
3. Click "New repository secret"
4. Enter name and value
5. Click "Add secret"

### Best Practices

- **Never commit secrets** to the repository
- **Rotate secrets** every 90 days
- **Use fine-grained tokens** with minimal permissions
- **Document secret requirements** in deployment guides
- **Use organization secrets** for shared credentials

---

## 🏷️ Labels

Navigate to **Issues** → **Labels**:

### Standard Labels

```yaml
Type Labels:
  - bug (color: d73a4a) - Something isn't working
  - enhancement (color: a2eeef) - New feature or request
  - documentation (color: 0075ca) - Documentation improvements
  - plugin (color: 7057ff) - Plugin-related
  - security (color: d93f0b) - Security vulnerability or concern

Priority Labels:
  - priority: critical (color: b60205) - Urgent, blocking issue
  - priority: high (color: d93f0b) - Important, needs attention soon
  - priority: medium (color: fbca04) - Standard priority
  - priority: low (color: 0e8a16) - Nice to have

Status Labels:
  - triage (color: ffffff) - Needs initial review
  - in-progress (color: yellow) - Currently being worked on
  - blocked (color: red) - Blocked by dependencies
  - needs-info (color: d876e3) - Needs more information
  - duplicate (color: cfd3d7) - Duplicate issue

Component Labels:
  - api (color: 1d76db) - REST API related
  - gui (color: 5319e7) - GUI application
  - plugin-system (color: 7057ff) - Plugin architecture
  - docker (color: 0db7ed) - Docker/containerization
  - ci-cd (color: 2cbe4e) - CI/CD pipeline
  - performance (color: fbca04) - Performance improvement
```

### Bulk Label Creation Script

Save as `.github/scripts/create-labels.sh`:

```bash
#!/bin/bash

labels=(
  "bug:d73a4a:Something isn't working"
  "enhancement:a2eeef:New feature or request"
  "documentation:0075ca:Documentation improvements"
  "plugin:7057ff:Plugin-related"
  "security:d93f0b:Security vulnerability"
  "priority: critical:b60205:Urgent issue"
  "priority: high:d93f0b:Important issue"
  "priority: medium:fbca04:Standard priority"
  "priority: low:0e8a16:Nice to have"
  "triage:ffffff:Needs review"
)

for label in "${labels[@]}"; do
  IFS=':' read -r name color description <<< "$label"
  gh label create "$name" --color "$color" --description "$description" --force
done
```

Run: `bash .github/scripts/create-labels.sh`

---

## 📝 Issue Templates

Located in `.github/ISSUE_TEMPLATE/`:

### Available Templates

1. **bug_report.yml** - Bug reporting form
2. **feature_request.yml** - Feature request form
3. **plugin_request.yml** - Plugin suggestions
4. **documentation.yml** - Documentation improvements
5. **config.yml** - Template configuration

### Template Configuration

The `config.yml` controls template behavior:

```yaml
blank_issues_enabled: true  # Allow blank issues
contact_links:
  - name: 💬 Community Discussion
    url: https://github.com/fileprocessor/discussions
    about: Ask questions and discuss ideas
  - name: 📚 Documentation
    url: https://github.com/fileprocessor/docs
    about: Read the comprehensive documentation
  - name: 🔒 Security Issue
    url: https://github.com/fileprocessor/security
    about: Report security vulnerabilities privately
```

---

## ⚙️ Workflows

Located in `.github/workflows/`:

### CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests
- Release publication

**Jobs:**
- Linting and code quality
- Security scanning
- Multi-platform testing
- Docker builds
- Deployment

**Configuration:**

```yaml
Environment Variables (set in workflow):
  PYTHON_VERSION: "3.11"
  DOCKER_REGISTRY: ghcr.io

Job Matrix:
  OS: [ubuntu-latest, windows-latest, macos-latest]
  Python: [3.10, 3.11, 3.12]
```

### Workflow Permissions

Navigate to **Settings** → **Actions** → **General**:

```yaml
Actions permissions:
  ✓ Allow all actions and reusable workflows

Workflow permissions:
  ✓ Read and write permissions
  ✓ Allow GitHub Actions to create and approve pull requests

Fork pull request workflows:
  ✓ Run workflows from fork pull requests
  - Require approval for first-time contributors
```

---

## 💬 Discussions

Navigate to **Settings** → **General** → **Features** → **Discussions**:

### Categories to Create

```yaml
Categories:
  📢 Announcements (Read-only, maintainers only)
    - Release announcements
    - Important updates

  💡 Ideas
    - Feature suggestions
    - Brainstorming

  🙏 Q&A
    - Questions and answers
    - Help requests

  📚 Show and Tell
    - Plugin showcases
    - Success stories
    - Tutorials

  🔧 Development
    - Technical discussions
    - Architecture decisions

  🗳️ Polls
    - Community voting
    - Feature prioritization
```

### Discussion Templates

Create `.github/DISCUSSION_TEMPLATE/`:

1. `ideas.md` - Template for feature ideas
2. `show-and-tell.md` - Template for showcasing work
3. `q-and-a.md` - Template for asking questions

---

## 🔒 Security

### Security Policy

Configure in **Settings** → **Security** → **Policy**:

- ✓ Private vulnerability reporting
- Security policy: `SECURITY.md` in root

### Dependabot

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "python"

  # Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "ci-cd"
```

### Code Scanning

Enable in **Settings** → **Security** → **Code scanning**:

- ✓ CodeQL analysis
- Languages: Python
- Schedule: Weekly

---

## 📊 Projects

Navigate to **Projects** → **New project**:

### Roadmap Project

```yaml
Name: Product Roadmap
Template: Roadmap
Views:
  - Roadmap (timeline view)
  - By Sprint (board view)
  - By Priority (table view)

Fields:
  - Status (Sprint 1, Sprint 2, ...)
  - Priority (Critical, High, Medium, Low)
  - Category (Feature, Bug, Docs, etc.)
  - Sprint
  - Estimated Effort
```

---

## 🔄 Automation

### GitHub Actions Workflows

All automation is handled through `.github/workflows/`:

- `ci-cd.yml` - Main CI/CD pipeline
- `labeler.yml` (create) - Auto-label PRs
- `stale.yml` (create) - Close stale issues

### Probot Apps (Optional)

Consider installing:
- **Stale** - Close inactive issues
- **Request Info** - Request more info on issues
- **Welcome** - Welcome first-time contributors
- **Auto-assign** - Auto-assign reviewers

---

## 📖 Additional Documentation

- [Workflow Documentation](workflows/README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Security Policy](../SECURITY.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)

---

## ✅ Configuration Checklist

Before going public, ensure:

- [ ] Branch protection rules configured
- [ ] All required secrets added
- [ ] Labels created and organized
- [ ] Issue templates tested
- [ ] Workflows passing successfully
- [ ] Discussions enabled and categorized
- [ ] Security features enabled
- [ ] Dependabot configured
- [ ] Code scanning enabled
- [ ] Documentation reviewed
- [ ] README updated with badges
- [ ] License file present
- [ ] Contributing guide clear

---

**Last Updated**: January 7, 2026  
**Maintainers**: File Processing Suite Team
