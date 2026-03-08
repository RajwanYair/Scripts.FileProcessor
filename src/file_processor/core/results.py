"""
results.py — Typed result objects for file processing operations.

All processor implementations return these dataclasses so callers
always deal with a consistent, structured result rather than raw dicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path


class OperationStatus(StrEnum):
    """Outcome of a single file operation."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    DRY_RUN = "dry_run"


@dataclass
class ProcessingResult:
    """Result of processing a single file."""

    source: Path
    status: OperationStatus
    message: str = ""
    destination: Path | None = None
    duration_seconds: float = 0.0
    bytes_in: int = 0
    bytes_out: int = 0
    extra: dict[str, object] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def ok(self) -> bool:
        return self.status in (OperationStatus.SUCCESS, OperationStatus.DRY_RUN)

    @property
    def compression_ratio(self) -> float | None:
        if self.bytes_in and self.bytes_out:
            return self.bytes_out / self.bytes_in
        return None


@dataclass
class BatchResult:
    """Aggregated result of a batch of file operations."""

    results: list[ProcessingResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None

    def add(self, result: ProcessingResult) -> None:
        self.results.append(result)

    def finish(self) -> None:
        self.finished_at = datetime.now(UTC)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def succeeded(self) -> int:
        return sum(1 for r in self.results if r.status == OperationStatus.SUCCESS)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == OperationStatus.FAILED)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == OperationStatus.SKIPPED)

    @property
    def duration_seconds(self) -> float:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        return self.succeeded / self.total if self.total else 0.0

    def summary(self) -> str:
        return (
            f"{self.succeeded}/{self.total} succeeded, "
            f"{self.failed} failed, "
            f"{self.skipped} skipped "
            f"in {self.duration_seconds:.2f}s"
        )
