"""
routes.py — FastAPI router definitions for file-processor REST API.

Registers all API routes as an `APIRouter` that the main `server.py` app mounts.
Keeping routes in a separate module allows clean unit-testable handler functions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class ProcessRequest(BaseModel):
    source_dir: str = Field(..., description="Absolute path to the source directory.")
    destination_dir: str | None = Field(None, description="Output directory (defaults to source).")
    recursive: bool = True
    dry_run: bool = False
    workers: int = Field(0, ge=0, description="0 = auto-detect.")
    extensions: list[str] = Field(default_factory=list)


class ProcessResponse(BaseModel):
    job_id: str
    total: int
    succeeded: int
    failed: int
    skipped: int
    duration_seconds: float
    summary: str


# ── Health ────────────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Return service health and running version."""
    try:
        from importlib.metadata import version

        ver = version("file-processor")
    except Exception:
        ver = "unknown"
    return HealthResponse(version=ver)


# ── File processing ───────────────────────────────────────────────────────────


@router.post(
    "/process",
    response_model=ProcessResponse,
    status_code=status.HTTP_200_OK,
    tags=["processing"],
)
async def process_files(request: ProcessRequest) -> ProcessResponse:
    """
    Batch-process files in *source_dir*.

    Runs synchronously; for long operations use `/process/async` (not yet implemented).
    """
    import uuid

    from file_processor.core.base import ProcessingConfig
    from file_processor.core.processor import FileProcessor

    source = Path(request.source_dir)
    if not source.is_dir():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"source_dir is not a directory: {request.source_dir}",
        )

    cfg = ProcessingConfig(
        source_dir=source,
        destination_dir=Path(request.destination_dir) if request.destination_dir else None,
        recursive=request.recursive,
        dry_run=request.dry_run,
        workers=request.workers,
        file_extensions=request.extensions or None,
    )
    batch = FileProcessor(cfg).run()

    return ProcessResponse(
        job_id=str(uuid.uuid4()),
        total=batch.total,
        succeeded=batch.succeeded,
        failed=batch.failed,
        skipped=batch.skipped,
        duration_seconds=batch.duration_seconds,
        summary=batch.summary(),
    )


# ── File upload ───────────────────────────────────────────────────────────────


@router.post("/upload", tags=["files"], status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    destination: str = Query(..., description="Destination directory path."),
) -> dict[str, Any]:
    """Upload a single file to *destination* on the server."""
    dest_dir = Path(destination)
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / (file.filename or "upload")
    # Prevent path traversal
    try:
        dest_path.resolve().relative_to(dest_dir.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination path.",
        ) from None

    content = await file.read()
    dest_path.write_bytes(content)
    logger.info("Uploaded %s (%d bytes) → %s", file.filename, len(content), dest_path)

    return {"filename": file.filename, "size_bytes": len(content), "saved_to": str(dest_path)}
