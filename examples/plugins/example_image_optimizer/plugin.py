#!/usr/bin/env python3
"""
Example Image Optimizer Plugin
==============================

Demonstrates how to create a processor plugin for the File Processing Suite.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

from PIL import Image

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "core"))

from plugin_system import PluginContext, PluginMetadata, PluginType, ProcessorPlugin


class ImageOptimizerPlugin(ProcessorPlugin):
    """Plugin that optimizes images by compressing and resizing."""

    def __init__(self):
        self.metadata = None
        self.context = None

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            id="com.example.image-optimizer",
            name="Image Optimizer Plugin",
            version="1.0.0",
            author="File Processing Suite Team",
            description="Optimizes images by compressing and resizing while maintaining quality",
            plugin_type=PluginType.PROCESSOR,
            supported_formats=[".jpg", ".jpeg", ".png", ".webp"],
            capabilities=["compress", "resize", "format_conversion"],
        )

    def initialize(self, context: PluginContext) -> bool:
        """Initialize the plugin."""
        try:
            self.context = context
            self.context.logger.info("Image Optimizer Plugin initialized")

            # Ensure required directories exist
            self.context.temp_dir.mkdir(parents=True, exist_ok=True)
            self.context.cache_dir.mkdir(parents=True, exist_ok=True)

            return True
        except Exception as e:
            if context:
                context.logger.error(f"Failed to initialize: {e}")
            return False

    def shutdown(self) -> bool:
        """Cleanup resources."""
        try:
            if self.context:
                self.context.logger.info("Image Optimizer Plugin shutting down")
            return True
        except Exception as e:
            if self.context:
                self.context.logger.error(f"Failed to shutdown: {e}")
            return False

    def can_process(self, file_path: Path) -> bool:
        """Check if plugin can process the given file."""
        return file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]

    async def process(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Process a single image file.

        Args:
            file_path: Path to image file
            context: Plugin execution context
            **kwargs: Additional parameters (output_path, quality, max_width, max_height)

        Returns:
            Dictionary with processing results
        """
        try:
            context.logger.info(f"Processing image: {file_path}")

            # Get configuration
            config = context.config
            quality = kwargs.get("quality", config.get("quality", 85))
            max_width = kwargs.get("max_width", config.get("max_width", 1920))
            max_height = kwargs.get("max_height", config.get("max_height", 1080))
            output_format = kwargs.get(
                "output_format", config.get("output_format", "auto")
            )
            output_path = kwargs.get("output_path")

            # Open image
            with Image.open(file_path) as img:
                original_size = img.size
                original_format = img.format
                original_file_size = file_path.stat().st_size

                # Convert to RGB if needed (for JPEG)
                if img.mode in ("RGBA", "LA", "P"):
                    if output_format == "jpeg" or (
                        output_format == "auto" and original_format == "JPEG"
                    ):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(
                            img, mask=img.split()[-1] if img.mode == "RGBA" else None
                        )
                        img = background

                # Resize if needed
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    resized = True
                else:
                    resized = False

                # Determine output path
                if not output_path:
                    output_path = (
                        file_path.parent
                        / f"{file_path.stem}_optimized{file_path.suffix}"
                    )

                # Determine output format
                if output_format == "auto":
                    save_format = original_format
                else:
                    save_format = output_format.upper()

                # Save optimized image
                save_kwargs = {}
                if save_format in ("JPEG", "JPG"):
                    save_kwargs = {"quality": quality, "optimize": True}
                elif save_format == "PNG":
                    save_kwargs = {"optimize": True}
                elif save_format == "WEBP":
                    save_kwargs = {"quality": quality}

                img.save(output_path, format=save_format, **save_kwargs)

                # Get new file size
                new_file_size = output_path.stat().st_size
                compression_ratio = (
                    (1 - new_file_size / original_file_size) * 100
                    if original_file_size > 0
                    else 0
                )

                return {
                    "success": True,
                    "input_path": str(file_path),
                    "output_path": str(output_path),
                    "original_size": original_size,
                    "new_size": img.size,
                    "original_file_size": original_file_size,
                    "new_file_size": new_file_size,
                    "compression_ratio": f"{compression_ratio:.2f}%",
                    "resized": resized,
                    "format": save_format,
                }

        except Exception as e:
            context.logger.error(f"Failed to process {file_path}: {e}")
            return {"success": False, "input_path": str(file_path), "error": str(e)}

    def configure(self, config: Dict[str, Any]) -> bool:
        """Update plugin configuration."""
        try:
            if self.context:
                self.context.config.update(config)
                self.context.logger.info(f"Configuration updated: {config}")
            return True
        except Exception as e:
            if self.context:
                self.context.logger.error(f"Failed to update configuration: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Check if Pillow is working
            from PIL import Image

            return {
                "status": "healthy",
                "message": "Plugin is operational",
                "pillow_version": Image.__version__,
            }
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}


# This is required - plugin manager will instantiate this class
Plugin = ImageOptimizerPlugin


if __name__ == "__main__":
    # Test the plugin
    import asyncio
    import logging

    logging.basicConfig(level=logging.INFO)

    # Create test context
    test_context = PluginContext(
        app_version="7.0.0",
        config={"quality": 85, "max_width": 1920, "max_height": 1080},
        logger=logging.getLogger("Test"),
        temp_dir=Path("./temp"),
        cache_dir=Path("./cache"),
        data_dir=Path("./data"),
    )

    # Initialize plugin
    plugin = ImageOptimizerPlugin()
    if plugin.initialize(test_context):
        print("Plugin initialized successfully")

        # Test health check
        health = plugin.health_check()
        print(f"Health check: {health}")

        # Cleanup
        plugin.shutdown()
