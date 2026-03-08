#!/usr/bin/env python3
"""
PDF Processor Plugin
===================

Comprehensive PDF operations: merge, split, extract, compress, and convert.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "core"))

from plugin_system import PluginContext, PluginMetadata, PluginType, ProcessorPlugin

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFProcessorPlugin(ProcessorPlugin):
    """Plugin for PDF processing operations."""

    def __init__(self):
        self.context = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="com.example.pdf-processor",
            name="PDF Processor Plugin",
            version="1.0.0",
            author="File Processing Suite Team",
            description="Comprehensive PDF processing: merge, split, extract, compress",
            plugin_type=PluginType.PROCESSOR,
            supported_formats=[".pdf"],
            capabilities=[
                "merge",
                "split",
                "extract_pages",
                "extract_text",
                "compress",
            ],
        )

    def initialize(self, context: PluginContext) -> bool:
        try:
            self.context = context

            if not PYPDF2_AVAILABLE:
                context.logger.error(
                    "PyPDF2 not available. Install with: pip install PyPDF2>=3.0.0"
                )
                return False

            # Ensure directories exist
            self.context.temp_dir.mkdir(parents=True, exist_ok=True)
            self.context.cache_dir.mkdir(parents=True, exist_ok=True)

            context.logger.info("PDF Processor Plugin initialized successfully")
            return True
        except Exception as e:
            if context:
                context.logger.error(f"Failed to initialize: {e}")
            return False

    def shutdown(self) -> bool:
        if self.context:
            self.context.logger.info("PDF Processor Plugin shutting down")
        return True

    def can_process(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    async def process(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Process a PDF file based on the operation specified.

        Args:
            file_path: Path to PDF file
            context: Plugin execution context
            **kwargs: Operation parameters
                - operation: 'merge', 'split', 'extract_pages', 'extract_text', 'compress'
                - pages: List of page numbers (for extract)
                - output_path: Output file path
                - files_to_merge: List of PDF paths (for merge)
        """
        try:
            operation = kwargs.get("operation", "info")
            context.logger.info(
                f"Processing PDF: {file_path} with operation: {operation}"
            )

            if operation == "info":
                return await self._get_pdf_info(file_path, context)
            elif operation == "merge":
                return await self._merge_pdfs(file_path, context, **kwargs)
            elif operation == "split":
                return await self._split_pdf(file_path, context, **kwargs)
            elif operation == "extract_pages":
                return await self._extract_pages(file_path, context, **kwargs)
            elif operation == "extract_text":
                return await self._extract_text(file_path, context, **kwargs)
            elif operation == "compress":
                return await self._compress_pdf(file_path, context, **kwargs)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            context.logger.error(f"Failed to process {file_path}: {e}")
            return {"success": False, "input_path": str(file_path), "error": str(e)}

    async def _get_pdf_info(
        self, file_path: Path, context: PluginContext
    ) -> Dict[str, Any]:
        """Get PDF information."""
        try:
            reader = PdfReader(str(file_path))

            # Extract metadata
            metadata = reader.metadata if hasattr(reader, "metadata") else {}

            return {
                "success": True,
                "input_path": str(file_path),
                "num_pages": len(reader.pages),
                "metadata": {
                    "title": metadata.get("/Title", "") if metadata else "",
                    "author": metadata.get("/Author", "") if metadata else "",
                    "subject": metadata.get("/Subject", "") if metadata else "",
                    "creator": metadata.get("/Creator", "") if metadata else "",
                },
                "file_size": file_path.stat().st_size,
                "encrypted": (
                    reader.is_encrypted if hasattr(reader, "is_encrypted") else False
                ),
            }
        except Exception as e:
            context.logger.error(f"Failed to get PDF info: {e}")
            return {"success": False, "error": str(e)}

    async def _merge_pdfs(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Merge multiple PDFs into one."""
        try:
            files_to_merge = kwargs.get("files_to_merge", [])
            output_path = kwargs.get("output_path")

            if not files_to_merge:
                files_to_merge = [file_path]

            if not output_path:
                output_path = file_path.parent / f"{file_path.stem}_merged.pdf"

            writer = PdfWriter()

            # Add all PDFs
            for pdf_file in files_to_merge:
                reader = PdfReader(str(pdf_file))
                for page in reader.pages:
                    writer.add_page(page)

            # Write output
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            return {
                "success": True,
                "operation": "merge",
                "input_files": [str(f) for f in files_to_merge],
                "output_path": str(output_path),
                "total_pages": len(writer.pages),
                "output_size": Path(output_path).stat().st_size,
            }

        except Exception as e:
            context.logger.error(f"Failed to merge PDFs: {e}")
            return {"success": False, "error": str(e)}

    async def _split_pdf(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Split PDF into separate pages."""
        try:
            output_dir = kwargs.get(
                "output_dir", file_path.parent / f"{file_path.stem}_split"
            )
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            reader = PdfReader(str(file_path))
            output_files = []

            for i, page in enumerate(reader.pages, 1):
                writer = PdfWriter()
                writer.add_page(page)

                output_path = output_dir / f"page_{i:03d}.pdf"
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)

                output_files.append(str(output_path))

            return {
                "success": True,
                "operation": "split",
                "input_path": str(file_path),
                "output_dir": str(output_dir),
                "num_pages": len(reader.pages),
                "output_files": output_files,
            }

        except Exception as e:
            context.logger.error(f"Failed to split PDF: {e}")
            return {"success": False, "error": str(e)}

    async def _extract_pages(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Extract specific pages from PDF."""
        try:
            pages = kwargs.get("pages", [1])
            output_path = kwargs.get("output_path")

            if not output_path:
                output_path = file_path.parent / f"{file_path.stem}_extracted.pdf"

            reader = PdfReader(str(file_path))
            writer = PdfWriter()

            for page_num in pages:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])

            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            return {
                "success": True,
                "operation": "extract_pages",
                "input_path": str(file_path),
                "output_path": str(output_path),
                "pages_extracted": pages,
                "total_pages": len(writer.pages),
            }

        except Exception as e:
            context.logger.error(f"Failed to extract pages: {e}")
            return {"success": False, "error": str(e)}

    async def _extract_text(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Extract text from PDF."""
        try:
            reader = PdfReader(str(file_path))
            text_content = []

            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                text_content.append(
                    {"page": i, "text": text, "word_count": len(text.split())}
                )

            # Optionally save to file
            output_path = kwargs.get("output_path")
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    for page_data in text_content:
                        f.write(f"=== Page {page_data['page']} ===\n")
                        f.write(page_data["text"])
                        f.write("\n\n")

            total_words = sum(p["word_count"] for p in text_content)

            return {
                "success": True,
                "operation": "extract_text",
                "input_path": str(file_path),
                "num_pages": len(reader.pages),
                "total_words": total_words,
                "pages": text_content[:3],  # First 3 pages preview
                "output_path": str(output_path) if output_path else None,
            }

        except Exception as e:
            context.logger.error(f"Failed to extract text: {e}")
            return {"success": False, "error": str(e)}

    async def _compress_pdf(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Compress PDF by removing unnecessary elements."""
        try:
            output_path = kwargs.get("output_path")
            if not output_path:
                output_path = file_path.parent / f"{file_path.stem}_compressed.pdf"

            reader = PdfReader(str(file_path))
            writer = PdfWriter()

            # Add all pages
            for page in reader.pages:
                writer.add_page(page)

            # Compress
            for page in writer.pages:
                page.compress_content_streams()

            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            original_size = file_path.stat().st_size
            compressed_size = Path(output_path).stat().st_size
            reduction = ((original_size - compressed_size) / original_size) * 100

            return {
                "success": True,
                "operation": "compress",
                "input_path": str(file_path),
                "output_path": str(output_path),
                "original_size": original_size,
                "compressed_size": compressed_size,
                "reduction_percent": f"{reduction:.2f}%",
            }

        except Exception as e:
            context.logger.error(f"Failed to compress PDF: {e}")
            return {"success": False, "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            if not PYPDF2_AVAILABLE:
                return {"status": "unhealthy", "message": "PyPDF2 not installed"}

            return {
                "status": "healthy",
                "message": "Plugin is operational",
                "pypdf2_version": (
                    PyPDF2.__version__ if hasattr(PyPDF2, "__version__") else "unknown"
                ),
            }
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}


Plugin = PDFProcessorPlugin
