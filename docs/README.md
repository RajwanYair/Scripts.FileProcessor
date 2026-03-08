# Documentation Structure

This directory contains all documentation for the File Processing Suite, organized into clear subdirectories.

## 📁 Directory Structure

```
docs/
├── guides/              # User and developer guides
│   ├── QUICK_START.md   # Get started in 5 minutes
│   ├── PLUGIN_SDK.md    # Plugin development guide
│   ├── INSTALLATION_GUIDE.md
│   ├── CONFIGURATION_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── ...
│
├── api/                 # API documentation
│   ├── REST_API.md      # REST API reference
│   ├── PLUGIN_API.md    # Plugin API reference
│   └── WEBSOCKET_API.md # WebSocket API reference
│
├── tutorials/           # Step-by-step tutorials
│   ├── creating_first_plugin.md
│   ├── building_workflow.md
│   └── deploying_docker.md
│
├── architecture/        # System architecture docs
│   ├── SYSTEM_DESIGN.md
│   ├── DATABASE_SCHEMA.md
│   └── PLUGIN_ARCHITECTURE.md
│
├── releases/            # Release notes and history
│   ├── SPRINT_1_SUMMARY.md
│   ├── RELEASE_NOTES_V6.md
│   ├── ENHANCEMENT_PLAN.md
│   └── ...
│
└── README.md           # This file
```

## 📖 Documentation Overview

### For Users

**Getting Started:**

1. [Quick Start Guide](guides/QUICK_START.md) - Get running in 5 minutes
2. [Installation Guide](guides/INSTALLATION_GUIDE.md) - Detailed installation
3. [Configuration Guide](guides/CONFIGURATION_GUIDE.md) - Configure the suite

**Using Features:**

- [Feature List](releases/FEATURE_LIST.md) - All available features
- [Password Scanner Guide](guides/PASSWORD_SCANNER_GUIDE.md)
- [Cross-Platform Guide](guides/CROSS_PLATFORM_GUIDE.md)

**Deployment:**

- [Docker Guide](guides/DOCKER_GUIDE.md) - Container deployment
- [Production Deployment](guides/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [System-Level Deployment](guides/SYSTEM_LEVEL_DEPLOYMENT_GUIDE.md)

### For Developers

**Development:**

- [Developer Documentation](guides/DEVELOPER_DOCUMENTATION.md)
- [Plugin SDK](guides/PLUGIN_SDK.md) - Create your own plugins
- [Contributing Guide](../CONTRIBUTING.md)

**API Reference:**

- [REST API Documentation](api/REST_API.md)
- [Plugin API Reference](api/PLUGIN_API.md)
- [WebSocket API](api/WEBSOCKET_API.md)

**Tutorials:**

- [Creating Your First Plugin](tutorials/creating_first_plugin.md)
- [Building Automated Workflows](tutorials/building_workflow.md)
- [Deploying with Docker](tutorials/deploying_docker.md)

**Architecture:**

- [System Design](architecture/SYSTEM_DESIGN.md)
- [Plugin Architecture](architecture/PLUGIN_ARCHITECTURE.md)
- [Database Schema](architecture/DATABASE_SCHEMA.md)

### For System Administrators

**Deployment:**

- [Docker Guide](guides/DOCKER_GUIDE.md)
- [Production Deployment](guides/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Performance Tuning](guides/PERFORMANCE_TUNING_GUIDE.md)

**Operations:**

- [Dependency Management](guides/DEPENDENCY_MANAGEMENT_GUIDE.md)
- [Monitoring Guide](guides/MONITORING_GUIDE.md)
- [Security Best Practices](guides/SECURITY_GUIDE.md)

### Project Information

**Releases:**

- [Sprint 1 Summary](releases/SPRINT_1_SUMMARY.md)
- [Release Notes v6.0](releases/RELEASE_NOTES_V6.md)
- [Enhancement Plans](releases/ENHANCEMENT_PLAN.md)

**Roadmap:**

- [Product Roadmap](../ROADMAP.md) - Long-term vision and plans
- [Project Status](guides/PROJECT_STATUS.md) - Current status

## 🔍 Finding Documentation

### By Topic

- **Installation**: [guides/INSTALLATION_GUIDE.md](guides/INSTALLATION_GUIDE.md)
- **Configuration**: [guides/CONFIGURATION_GUIDE.md](guides/CONFIGURATION_GUIDE.md)
- **Plugins**: [guides/PLUGIN_SDK.md](guides/PLUGIN_SDK.md)
- **API**: [api/REST_API.md](api/REST_API.md)
- **Docker**: [guides/DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md)
- **Performance**: [guides/PERFORMANCE_TUNING_GUIDE.md](guides/PERFORMANCE_TUNING_GUIDE.md)

### By Role

**End Users:**

- Start with [Quick Start](guides/QUICK_START.md)
- Then [Feature List](releases/FEATURE_LIST.md)

**Developers:**

- Start with [Developer Guide](guides/DEVELOPER_DOCUMENTATION.md)
- Then [Plugin SDK](guides/PLUGIN_SDK.md)
- Review [Architecture Docs](architecture/)

**DevOps/SysAdmins:**

- Start with [Docker Guide](guides/DOCKER_GUIDE.md)
- Then [Production Deployment](guides/PRODUCTION_DEPLOYMENT_GUIDE.md)
- Review [Performance Tuning](guides/PERFORMANCE_TUNING_GUIDE.md)

## 📝 Contributing to Documentation

We welcome documentation improvements!

### How to Contribute

1. **Fix Typos**: Submit PR directly
2. **Improve Clarity**: Open issue first, then PR
3. **Add Examples**: Always welcome!
4. **New Guides**: Discuss in GitHub Discussions first

### Documentation Standards

- Use Markdown format
- Include table of contents for long docs
- Add code examples where applicable
- Use screenshots for UI documentation
- Keep language clear and concise
- Follow existing structure

### Building Documentation

```bash
# Install dependencies
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## 🔗 External Resources

- **GitHub Repository**: [github.com/fileprocessor](https://github.com/fileprocessor)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (when running)
- **Community Forum**: [forum.fileprocessor.com](https://forum.fileprocessor.com)
- **Discord**: [discord.gg/fileprocessor](https://discord.gg/fileprocessor)

## 📄 License

Documentation is licensed under [Creative Commons BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Code examples in documentation are licensed under [MIT License](../LICENSE).

---

**Last Updated**: January 7, 2026  
**Documentation Version**: 7.0
