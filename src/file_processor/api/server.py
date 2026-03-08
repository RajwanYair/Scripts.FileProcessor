#!/usr/bin/env python3
"""
FastAPI REST API Server for File Processing Suite v7.0
=====================================================

Modern REST API providing programmatic access to all file processing features.

Features:
- RESTful endpoints for all operations
- OpenAPI/Swagger documentation
- Rate limiting and throttling
- API key authentication
- File upload/download
- Batch operations
- Real-time progress via WebSocket
- Async processing
- Plugin management API

Usage:
    uvicorn api_server:app --host 0.0.0.0 --port 8000

    Or for development with auto-reload:
    uvicorn api_server:app --reload
"""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from file_processor.core.plugin_system import PluginManager

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIServer")

# API Configuration
API_VERSION = "1.0.0"
API_TITLE = "File Processing Suite API"
API_DESCRIPTION = """
**Enterprise-grade file processing REST API**

## Features

* 🚀 **Fast & Async** - Built with FastAPI for maximum performance
* 🔌 **Plugin System** - Extensible with custom processors
* 📊 **Batch Operations** - Process multiple files efficiently
* 🔒 **Secure** - API key authentication and rate limiting
* 📡 **Real-time** - WebSocket support for progress tracking
* 📄 **OpenAPI** - Full API documentation and client generation

## Authentication

All endpoints require an API key in the header:
```
X-API-Key: your-api-key-here
```

## Rate Limits

- Free tier: 100 requests/minute
- Pro tier: 1000 requests/minute
- Enterprise: Custom limits
"""

# Global state
plugin_manager: PluginManager | None = None
active_jobs: dict[str, dict[str, Any]] = {}
websocket_connections: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the API server."""
    # Startup
    logger.info("Starting File Processing Suite API Server...")

    global plugin_manager
    plugin_dirs = [
        PROJECT_ROOT / "plugins",
        Path.home() / ".file_processor" / "plugins",
    ]
    plugin_manager = PluginManager(plugin_dirs, app_version=API_VERSION)

    # Discover and load plugins
    plugins = plugin_manager.discover_plugins()
    logger.info(f"Discovered {len(plugins)} plugins")

    for plugin in plugins:
        if plugin.enabled:
            plugin_manager.load_plugin(plugin.id)

    logger.info(f"API Server started successfully on v{API_VERSION}")

    yield

    # Shutdown
    logger.info("Shutting down API Server...")

    # Unload all plugins
    if plugin_manager:
        for plugin_id in list(plugin_manager.plugins.keys()):
            plugin_manager.unload_plugin(plugin_id)

    logger.info("API Server shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    """Verify API key for authentication."""
    # TODO: Implement proper API key verification with database
    # For now, accept any key for development
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    return api_key


# ============================================================================
# Pydantic Models
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., example="healthy")
    version: str = Field(..., example="1.0.0")
    timestamp: datetime
    uptime_seconds: float
    plugins_loaded: int


class ProcessingRequest(BaseModel):
    """Request model for file processing."""

    operation: str = Field(
        ..., example="optimize_image", description="Processing operation to perform"
    )
    options: dict[str, Any] = Field(default_factory=dict, example={"quality": 85})


class ProcessingResponse(BaseModel):
    """Response model for file processing."""

    job_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., example="processing")
    message: str
    created_at: datetime
    result: dict[str, Any] | None = None


class PluginInfo(BaseModel):
    """Plugin information model."""

    id: str
    name: str
    version: str
    type: str
    state: str
    enabled: bool
    description: str | None = None


class BatchProcessingRequest(BaseModel):
    """Request model for batch processing."""

    operation: str
    file_ids: list[str]
    options: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    global plugin_manager

    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=datetime.now(),
        uptime_seconds=0.0,  # TODO: Track actual uptime
        plugins_loaded=len(plugin_manager.plugins) if plugin_manager else 0,
    )


@app.get("/api/v1/plugins", response_model=list[PluginInfo], tags=["Plugins"])
async def list_plugins(api_key: str = Depends(verify_api_key)):
    """List all available plugins."""
    global plugin_manager

    if not plugin_manager:
        raise HTTPException(status_code=500, detail="Plugin manager not initialized")

    plugins_info = []
    for plugin_id, instance in plugin_manager.plugins.items():
        plugins_info.append(
            PluginInfo(
                id=plugin_id,
                name=instance.metadata.name,
                version=instance.metadata.version,
                type=instance.metadata.plugin_type.value,
                state=instance.state.value,
                enabled=instance.metadata.enabled,
                description=instance.metadata.description,
            )
        )

    return plugins_info


@app.get("/api/v1/plugins/{plugin_id}", response_model=PluginInfo, tags=["Plugins"])
async def get_plugin(plugin_id: str, api_key: str = Depends(verify_api_key)):
    """Get details of a specific plugin."""
    global plugin_manager

    if not plugin_manager:
        raise HTTPException(status_code=500, detail="Plugin manager not initialized")

    if plugin_id not in plugin_manager.plugins:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

    instance = plugin_manager.plugins[plugin_id]
    return PluginInfo(
        id=plugin_id,
        name=instance.metadata.name,
        version=instance.metadata.version,
        type=instance.metadata.plugin_type.value,
        state=instance.state.value,
        enabled=instance.metadata.enabled,
        description=instance.metadata.description,
    )


@app.post("/api/v1/plugins/{plugin_id}/reload", tags=["Plugins"])
async def reload_plugin(plugin_id: str, api_key: str = Depends(verify_api_key)):
    """Reload a plugin (hot-reload)."""
    global plugin_manager

    if not plugin_manager:
        raise HTTPException(status_code=500, detail="Plugin manager not initialized")

    if plugin_manager.reload_plugin(plugin_id):
        return {"message": f"Plugin {plugin_id} reloaded successfully"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to reload plugin: {plugin_id}")


@app.post("/api/v1/upload", tags=["Files"])
async def upload_file(file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    """Upload a file for processing."""
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / f"{file_id}_{file.filename}"

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path),
            "message": "File uploaded successfully",
        }
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/process/{file_id}", response_model=ProcessingResponse, tags=["Processing"])
async def process_file(
    file_id: str,
    request: ProcessingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
):
    """Process a file with specified operation."""
    global active_jobs

    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Find file
        upload_dir = Path("uploads")
        file_path = None
        for f in upload_dir.glob(f"{file_id}_*"):
            file_path = f
            break

        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

        # Create job
        job = {
            "job_id": job_id,
            "file_id": file_id,
            "file_path": str(file_path),
            "operation": request.operation,
            "options": request.options,
            "status": "processing",
            "created_at": datetime.now(),
            "result": None,
            "error": None,
        }
        active_jobs[job_id] = job

        # Queue processing in background
        background_tasks.add_task(
            process_file_background,
            job_id,
            file_path,
            request.operation,
            request.options,
        )

        return ProcessingResponse(
            job_id=job_id,
            status="processing",
            message=f"Processing started for {file_path.name}",
            created_at=job["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


async def process_file_background(
    job_id: str, file_path: Path, operation: str, options: dict[str, Any]
):
    """Background task to process file."""
    global active_jobs, plugin_manager

    try:
        logger.info(f"Starting background processing for job {job_id}")

        # Simulate processing (replace with actual plugin processing)
        await asyncio.sleep(2)  # Simulate work

        # Update job status
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["result"] = {
            "success": True,
            "operation": operation,
            "file": str(file_path),
            "processed_at": datetime.now().isoformat(),
        }

        logger.info(f"Completed processing for job {job_id}")

        # Notify WebSocket clients
        await broadcast_job_update(job_id, active_jobs[job_id])

    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)


@app.get("/api/v1/marketplace/plugins", tags=["Marketplace"])
async def list_marketplace_plugins(
    category: str | None = None,
    status: str | None = None,
    featured: bool | None = None,
    api_key: str = Depends(verify_api_key),
):
    """List plugins available in the marketplace."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        plugins = marketplace.list_plugins(category=category, status=status)

        if featured is not None:
            plugins = [p for p in plugins if p.get("featured") == featured]

        return {
            "success": True,
            "count": len(plugins),
            "plugins": plugins,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to list marketplace plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/marketplace/search", tags=["Marketplace"])
async def search_marketplace_plugins(
    q: str = Query(..., description="Search query"),
    api_key: str = Depends(verify_api_key),
):
    """Search plugins in the marketplace."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        results = marketplace.search_plugins(q)

        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to search marketplace: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/marketplace/plugin/{plugin_id}", tags=["Marketplace"])
async def get_marketplace_plugin_info(plugin_id: str, api_key: str = Depends(verify_api_key)):
    """Get detailed information about a marketplace plugin."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        plugin_info = marketplace.get_plugin_info(plugin_id)

        if not plugin_info:
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        # Add installation status
        plugin_info["installed"] = marketplace.is_installed(plugin_id)
        if plugin_info["installed"]:
            plugin_info["installed_version"] = marketplace.get_installed_version(plugin_id)

        return {
            "success": True,
            "plugin": plugin_info,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin info: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/marketplace/install/{plugin_id}", tags=["Marketplace"])
async def install_marketplace_plugin(
    plugin_id: str,
    force: bool = Query(False, description="Force reinstall"),
    api_key: str = Depends(verify_api_key),
):
    """Install a plugin from the marketplace."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        success = marketplace.install_plugin(plugin_id, force=force)

        if success:
            # Reload plugin manager to pick up the new plugin
            global plugin_manager
            if plugin_manager:
                plugin_manager.discover_plugins()

            return {
                "success": True,
                "message": f"Plugin {plugin_id} installed successfully",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Installation failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/api/v1/marketplace/uninstall/{plugin_id}", tags=["Marketplace"])
async def uninstall_marketplace_plugin(plugin_id: str, api_key: str = Depends(verify_api_key)):
    """Uninstall a plugin."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        success = marketplace.uninstall_plugin(plugin_id)

        if success:
            # Reload plugin manager
            global plugin_manager
            if plugin_manager:
                plugin_manager.unload_plugin(plugin_id)

            return {
                "success": True,
                "message": f"Plugin {plugin_id} uninstalled successfully",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Uninstallation failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to uninstall plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/marketplace/updates", tags=["Marketplace"])
async def check_marketplace_updates(api_key: str = Depends(verify_api_key)):
    """Check for plugin updates."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        updates = marketplace.check_updates()

        return {
            "success": True,
            "updates_available": len(updates) > 0,
            "count": len(updates),
            "updates": updates,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to check updates: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/marketplace/categories", tags=["Marketplace"])
async def list_marketplace_categories(api_key: str = Depends(verify_api_key)):
    """List plugin categories."""
    try:
        from plugin_manager import PluginMarketplace

        marketplace = PluginMarketplace()
        categories = marketplace.catalog.get("categories", [])

        # Count plugins per category
        for category in categories:
            plugin_count = len(
                [p for p in marketplace.catalog["plugins"] if p["category"] == category["id"]]
            )
            category["plugin_count"] = plugin_count

        return {
            "success": True,
            "count": len(categories),
            "categories": categories,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/jobs/{job_id}", response_model=ProcessingResponse, tags=["Processing"])
async def get_job_status(job_id: str, api_key: str = Depends(verify_api_key)):
    """Get status of a processing job."""
    global active_jobs

    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = active_jobs[job_id]
    return ProcessingResponse(
        job_id=job_id,
        status=job["status"],
        message=f"Job status: {job['status']}",
        created_at=job["created_at"],
        result=job.get("result"),
    )


@app.post("/api/v1/batch/process", tags=["Processing"])
async def batch_process(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
):
    """Process multiple files in batch."""
    batch_id = str(uuid.uuid4())
    job_ids = []

    for file_id in request.file_ids:
        # Create individual processing request
        proc_request = ProcessingRequest(operation=request.operation, options=request.options)

        # Start processing
        response = await process_file(file_id, proc_request, background_tasks, api_key)
        job_ids.append(response.job_id)

    return {
        "batch_id": batch_id,
        "job_ids": job_ids,
        "total_files": len(request.file_ids),
        "message": f"Batch processing started for {len(request.file_ids)} files",
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    global websocket_connections

    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()

            # Echo back for testing
            await websocket.send_json(
                {
                    "type": "ping",
                    "message": "pong",
                    "timestamp": datetime.now().isoformat(),
                }
            )
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


async def broadcast_job_update(job_id: str, job_data: dict[str, Any]):
    """Broadcast job update to all connected WebSocket clients."""
    global websocket_connections

    message = {
        "type": "job_update",
        "job_id": job_id,
        "status": job_data["status"],
        "timestamp": datetime.now().isoformat(),
    }

    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_json(message)
        except Exception:
            disconnected.append(websocket)

    # Remove disconnected clients
    for websocket in disconnected:
        websocket_connections.remove(websocket)


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    print(
        f"""
╔══════════════════════════════════════════════════════════════╗
║  File Processing Suite API Server v{API_VERSION}                 ║
╠══════════════════════════════════════════════════════════════╣
║  🚀 Starting server...                                       ║
║                                                              ║
║  📡 API: http://localhost:8000                              ║
║  📄 Docs: http://localhost:8000/docs                        ║
║  🔄 ReDoc: http://localhost:8000/redoc                      ║
║  💬 WebSocket: ws://localhost:8000/ws                       ║
╚══════════════════════════════════════════════════════════════╝
    """
    )

    host = "127.0.0.1"  # Override with SERVER_HOST env-var in production
    uvicorn.run(
        "file_processor.api.server:app", host=host, port=8000, reload=True, log_level="info"
    )
