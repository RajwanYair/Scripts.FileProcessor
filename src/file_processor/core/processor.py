"""
processor.py — Central FileProcessor orchestration engine.

Coordinates file discovery, optional filtering, parallel execution of
operations, and result aggregation.  Designed to be subclassed or used
directly with a callable `operation` parameter.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from pathlib import Path

from file_processor.core.base import BaseProcessor, ProcessingConfig
from file_processor.core.results import BatchResult, OperationStatus, ProcessingResult

logger = logging.getLogger(__name__)

# Type alias for a file-level operation
OperationFn = Callable[[Path, ProcessingConfig], ProcessingResult]


def _default_operation(path: Path, cfg: ProcessingConfig) -> ProcessingResult:
    """No-op passthrough operation — useful for scanning/dry-run."""
    return ProcessingResult(
        source=path,
        status=OperationStatus.DRY_RUN if cfg.dry_run else OperationStatus.SUCCESS,
        message="passthrough",
    )


class FileProcessor(BaseProcessor):
    """
    General-purpose parallel file processor.

    Parameters
    ----------
    config:
        Fully validated `ProcessingConfig` instance.
    operation:
        A callable ``(path, config) -> ProcessingResult`` applied to each
        discovered file.  Defaults to a no-op passthrough.
    extensions:
        Override the extensions filter just for this run.

    Example
    -------
    >>> from pathlib import Path
    >>> from file_processor.core.base import ProcessingConfig
    >>> from file_processor.core.processor import FileProcessor
    >>> cfg = ProcessingConfig(source_dir=Path("/tmp/test"))
    >>> result = FileProcessor(cfg).run()
    >>> print(result.summary())
    """

    def __init__(
        self,
        config: ProcessingConfig,
        operation: OperationFn | None = None,
        extensions: list[str] | None = None,
    ) -> None:
        super().__init__(config)
        self._operation: OperationFn = operation or _default_operation
        self._extensions = extensions

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> BatchResult:
        """Discover files and process them in parallel; return aggregated result."""
        files = self.get_files(self._extensions)
        if not files:
            logger.info("No files found matching criteria in %s", self.config.source_dir)
            batch = BatchResult()
            batch.finish()
            return batch

        logger.info("Processing %d files with %d workers", len(files), self.config.workers)
        batch = BatchResult()

        with ThreadPoolExecutor(max_workers=self.config.workers or None) as pool:
            futures = {pool.submit(self._safe_process, f): f for f in files}
            for future in as_completed(futures):
                batch.add(future.result())

        batch.finish()
        logger.info(batch.summary())
        return batch

    async def run_async(self) -> BatchResult:
        """Async variant — offloads blocking work to the default executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _safe_process(self, path: Path) -> ProcessingResult:
        """Wrap the operation in a try/except so one failure never stops the batch."""
        try:
            return self._operation(path, self.config)
        except Exception as exc:
            logger.error("Failed to process %s: %s", path, exc)
            return ProcessingResult(
                source=path,
                status=OperationStatus.FAILED,
                message=str(exc),
            )
