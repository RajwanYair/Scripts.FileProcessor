# 🚀 Quick Start Guide - File Processing Suite v7.0

Get up and running with the world's most advanced file processing platform in minutes!

## 📋 Table of Contents

1. [Installation](#installation)
2. [First Steps](#first-steps)
3. [Try the GUI](#try-the-gui)
4. [Try the API](#try-the-api)
5. [Create Your First Plugin](#create-your-first-plugin)
6. [Deploy with Docker](#deploy-with-docker)
7. [Next Steps](#next-steps)

---

## ⚡ Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourorg/file-processor.git
cd file-processor

# Install dependencies
pip install -r deployment/requirements.txt

# Verify installation
python file_processor.py --version
```

### Verify Installation

```bash
python -c "import core.plugin_system; print('✓ Plugin system ready')"
python -c "import fastapi; print('✓ API ready')"
```

---

## 🎯 First Steps

### 1. Launch the GUI (Traditional Mode)

```bash
python file_processor.py
```

This launches the familiar v6.0 GUI with all 22 features.

### 2. Test the Plugin System

```bash
# List available plugins
python -c "
from core.plugin_system import PluginManager
from pathlib import Path

manager = PluginManager([Path('./plugins')])
plugins = manager.discover_plugins()
print(f'Found {len(plugins)} plugins:')
for p in plugins:
    print(f'  - {p.name} v{p.version}')
"
```

Expected output:

```
Found 3 plugins:
  - Image Optimizer Plugin v1.0.0
  - PDF Processor Plugin v1.0.0
  - Text Analyzer Plugin v1.0.0
```

---

## 🖥️ Try the GUI

### Launch GUI

```bash
python file_processor.py --gui
```

### Features Available

- Smart Organizer
- Batch Renamer
- Duplicate Finder
- Image Optimizer
- PDF Tools
- And 17 more!

---

## 🌐 Try the API

### 1. Start the API Server

```bash
# Install FastAPI dependencies (if not already installed)
pip install fastapi uvicorn[standard]

# Start server
python api_server.py
```

Server will start at: <http://localhost:8000>

### 2. Access Interactive Documentation

Open your browser: **<http://localhost:8000/docs>**

You'll see the beautiful Swagger UI with all endpoints!

### 3. Test Endpoints

#### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-07T...",
  "plugins_loaded": 3
}
```

#### List Plugins

```bash
curl http://localhost:8000/api/v1/plugins \
  -H "X-API-Key: test-key"
```

#### Upload a File

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "X-API-Key: test-key" \
  -F "file=@yourfile.jpg"
```

Response:

```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "yourfile.jpg",
  "size": 245760,
  "message": "File uploaded successfully"
}
```

#### Process the File

```bash
curl -X POST http://localhost:8000/api/v1/process/{file_id} \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "optimize_image",
    "options": {"quality": 85}
  }'
```

### 4. Try WebSocket (Real-time Updates)

```javascript
// In browser console or Node.js
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  console.log('Update:', JSON.parse(event.data));
};

ws.onopen = () => {
  console.log('Connected to real-time updates!');
};
```

---

## 🔌 Create Your First Plugin

### 1. Create Plugin Directory

```bash
mkdir -p plugins/my-first-plugin
cd plugins/my-first-plugin
```

### 2. Create manifest.json

```json
{
  "id": "com.yourname.my-first-plugin",
  "name": "My First Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "My awesome first plugin!",
  "plugin_type": "processor",
  "min_app_version": "7.0.0",
  "supported_formats": [".txt"],
  "license": "MIT",
  "enabled": true
}
```

### 3. Create plugin.py

```python
#!/usr/bin/env python3
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'core'))

from plugin_system import ProcessorPlugin, PluginMetadata, PluginContext, PluginType

class MyFirstPlugin(ProcessorPlugin):
    def get_metadata(self):
        return PluginMetadata(
            id="com.yourname.my-first-plugin",
            name="My First Plugin",
            version="1.0.0",
            author="Your Name",
            description="My awesome first plugin!",
            plugin_type=PluginType.PROCESSOR
        )
    
    def initialize(self, context):
        self.context = context
        context.logger.info("🎉 My First Plugin initialized!")
        return True
    
    def shutdown(self):
        self.context.logger.info("👋 My First Plugin shutting down")
        return True
    
    def can_process(self, file_path):
        return file_path.suffix == '.txt'
    
    async def process(self, file_path, context, **kwargs):
        # Read the file
        content = file_path.read_text()
        
        # Do something cool!
        lines = content.split('\n')
        word_count = len(content.split())
        
        # Return results
        return {
            "success": True,
            "input_path": str(file_path),
            "lines": len(lines),
            "words": word_count,
            "message": f"Processed {file_path.name} successfully!"
        }

Plugin = MyFirstPlugin
```

### 4. Create **init**.py

```python
from .plugin import MyFirstPlugin
__version__ = "1.0.0"
```

### 5. Test Your Plugin

```bash
# Test the plugin directly
python plugin.py

# Or load it via plugin manager
python -c "
from core.plugin_system import PluginManager
from pathlib import Path

manager = PluginManager([Path('./plugins')])
success = manager.load_plugin('com.yourname.my-first-plugin')
print('Plugin loaded:', success)
"
```

### 6. Use Your Plugin via API

```bash
# Start API server
python api_server.py

# Your plugin is now available via API!
curl http://localhost:8000/api/v1/plugins \
  -H "X-API-Key: test-key" \
  | grep "my-first-plugin"
```

**🎉 Congratulations! You've created your first plugin!**

---

## 🐳 Deploy with Docker

### 1. Build and Start

```bash
# Start all services
docker-compose up -d
```

This starts:

- API Server (port 8000)
- PostgreSQL Database
- Redis Cache
- Apache Kafka
- Prometheus (port 9090)
- Grafana (port 3000)
- NGINX Load Balancer

### 2. Verify Services

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 3. Access Services

- **API**: <http://localhost:8000/docs>
- **Grafana**: <http://localhost:3000> (admin/admin)
- **Prometheus**: <http://localhost:9090>

### 4. Scale the API

```bash
# Run 5 API instances
docker-compose up -d --scale api=5

# Check instances
docker-compose ps api
```

### 5. Stop Services

```bash
docker-compose down
```

---

## 📚 Next Steps

### Explore Examples

```bash
# Try the image optimizer plugin
cd examples/plugins/example_image_optimizer
python plugin.py

# Try the PDF processor
cd examples/plugins/example_pdf_processor
python plugin.py

# Try the text analyzer
cd examples/plugins/example_text_analyzer
python plugin.py
```

### Read Documentation

1. **[Plugin SDK](PLUGIN_SDK.md)** - Complete plugin development guide
2. **[API Reference](http://localhost:8000/docs)** - Interactive API docs
3. **[Docker Guide](DOCKER_GUIDE.md)** - Production deployment
4. **[Enhancement Plan](WORLD_CLASS_ENHANCEMENT_PLAN.md)** - Future roadmap

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_plugin_system.py -v
pytest tests/test_api_server.py -v
```

### Create More Plugins

Study the example plugins:

- `examples/plugins/example_image_optimizer/` - Image processing
- `examples/plugins/example_pdf_processor/` - PDF operations
- `examples/plugins/example_text_analyzer/` - Text analysis

### Join the Community

- **Discord**: <https://discord.gg/fileprocessor>
- **GitHub**: <https://github.com/fileprocessor/issues>
- **Docs**: <https://docs.fileprocessor.com>

---

## 🎓 Learning Path

### Beginner (Week 1)

1. ✅ Install and run GUI
2. ✅ Try API endpoints
3. ✅ Create simple plugin
4. ✅ Deploy with Docker

### Intermediate (Week 2-4)

1. Create custom processor plugins
2. Implement hook plugins for workflows
3. Add storage plugins for cloud
4. Build complex processing pipelines

### Advanced (Month 2+)

1. Contribute to core development
2. Create marketplace-ready plugins
3. Deploy to production (Kubernetes)
4. Build ML-powered features

---

## 💡 Tips & Tricks

### Speed Up Development

```bash
# Auto-reload API server during development
uvicorn api_server:app --reload

# Watch for plugin changes
# Hot-reload is automatic!
```

### Debug Plugin Issues

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python api_server.py

# Check plugin health
curl http://localhost:8000/api/v1/plugins/com.example.my-plugin
```

### Performance Optimization

```bash
# Use multiple workers
uvicorn api_server:app --workers 4

# Scale with Docker
docker-compose up -d --scale api=10
```

---

## ❓ Troubleshooting

### Plugin Not Loading?

1. Check manifest.json is valid JSON
2. Ensure plugin.py has `Plugin = YourClass`
3. Verify dependencies are installed
4. Check logs: `docker-compose logs api`

### API Not Starting?

1. Check port 8000 is available: `netstat -an | grep 8000`
2. Install FastAPI: `pip install fastapi uvicorn`
3. Check Python version: `python --version` (need 3.9+)

### Docker Issues?

1. Check Docker is running: `docker ps`
2. Rebuild images: `docker-compose build --no-cache`
3. Check logs: `docker-compose logs`

---

## 🎉 You're Ready

You now have:

- ✅ Working installation
- ✅ API server running
- ✅ First plugin created
- ✅ Docker deployment
- ✅ Tests passing

**Start building amazing file processing solutions!** 🚀

---

**Questions?** Open an issue on GitHub or join our Discord community!

**Version**: 7.0.0  
**Updated**: January 7, 2026
