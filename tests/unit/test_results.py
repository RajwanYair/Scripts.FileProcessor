"""Unit tests for file_processor.core.results."""

from __future__ import annotations

from pathlib import Path
import time

import pytest

from file_processor.core.results import BatchResult, OperationStatus, ProcessingResult


@pytest.mark.unit
class TestOperationStatus:
    def test_values(self) -> None:
        assert OperationStatus.SUCCESS == "success"
        assert OperationStatus.FAILED == "failed"
        assert OperationStatus.SKIPPED == "skipped"
        assert OperationStatus.DRY_RUN == "dry_run"

    def test_all_are_strings(self) -> None:
        for status in OperationStatus:
            assert isinstance(status, str)


@pytest.mark.unit
class TestProcessingResult:
    def _result(self, status: OperationStatus = OperationStatus.SUCCESS) -> ProcessingResult:
        return ProcessingResult(source=Path("test.txt"), status=status)

    def test_ok_true_on_success(self) -> None:
        assert self._result(OperationStatus.SUCCESS).ok is True

    def test_ok_true_on_dry_run(self) -> None:
        assert self._result(OperationStatus.DRY_RUN).ok is True

    def test_ok_false_on_failed(self) -> None:
        assert self._result(OperationStatus.FAILED).ok is False

    def test_ok_false_on_skipped(self) -> None:
        assert self._result(OperationStatus.SKIPPED).ok is False

    def test_compression_ratio_none_when_bytes_zero(self) -> None:
        assert self._result().compression_ratio is None

    def test_compression_ratio_none_when_bytes_in_zero(self) -> None:
        r = ProcessingResult(
            source=Path("f"), status=OperationStatus.SUCCESS, bytes_in=0, bytes_out=100
        )
        assert r.compression_ratio is None

    def test_compression_ratio_computed(self) -> None:
        r = ProcessingResult(
            source=Path("f"), status=OperationStatus.SUCCESS, bytes_in=100, bytes_out=50
        )
        assert r.compression_ratio == pytest.approx(0.5)

    def test_defaults(self) -> None:
        r = self._result()
        assert r.message == ""
        assert r.destination is None
        assert r.duration_seconds == 0.0
        assert r.bytes_in == 0
        assert r.bytes_out == 0
        assert r.extra == {}

    def test_timestamp_is_timezone_aware(self) -> None:
        r = self._result()
        assert r.timestamp.tzinfo is not None


@pytest.mark.unit
class TestBatchResult:
    @pytest.fixture
    def batch(self) -> BatchResult:
        b = BatchResult()
        b.add(ProcessingResult(source=Path("a"), status=OperationStatus.SUCCESS))
        b.add(ProcessingResult(source=Path("b"), status=OperationStatus.FAILED))
        b.add(ProcessingResult(source=Path("c"), status=OperationStatus.SKIPPED))
        return b

    def test_total(self, batch: BatchResult) -> None:
        assert batch.total == 3

    def test_succeeded(self, batch: BatchResult) -> None:
        assert batch.succeeded == 1

    def test_failed(self, batch: BatchResult) -> None:
        assert batch.failed == 1

    def test_skipped(self, batch: BatchResult) -> None:
        assert batch.skipped == 1

    def test_success_rate(self, batch: BatchResult) -> None:
        assert batch.success_rate == pytest.approx(1 / 3)

    def test_success_rate_empty_batch(self) -> None:
        assert BatchResult().success_rate == 0.0

    def test_duration_before_finish(self) -> None:
        assert BatchResult().duration_seconds == 0.0

    def test_duration_after_finish(self) -> None:
        b = BatchResult()
        time.sleep(0.01)
        b.finish()
        assert b.duration_seconds > 0.0

    def test_summary_format(self, batch: BatchResult) -> None:
        batch.finish()
        s = batch.summary()
        assert "1/3 succeeded" in s
        assert "1 failed" in s
        assert "1 skipped" in s

    def test_empty_batch_summary(self) -> None:
        b = BatchResult()
        b.finish()
        s = b.summary()
        assert "0/0 succeeded" in s


# ---------------------------------------------------------------------------
# BatchResult.to_json / to_csv
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBatchResultExport:
    """Tests for the to_json() and to_csv() export methods."""

    @pytest.fixture
    def batch(self) -> BatchResult:
        b = BatchResult()
        b.add(ProcessingResult(
            source=Path("a.txt"),
            status=OperationStatus.SUCCESS,
            message="done",
            destination=Path("out/a.txt"),
            duration_seconds=0.5,
            bytes_in=100,
            bytes_out=80,
        ))
        b.add(ProcessingResult(
            source=Path("b.txt"),
            status=OperationStatus.FAILED,
            message="oops",
        ))
        b.finish()
        return b

    # ── to_json ──────────────────────────────────────────────────────────

    def test_to_json_is_valid_json(self, batch: BatchResult) -> None:
        import json
        data = json.loads(batch.to_json())
        assert isinstance(data, dict)

    def test_to_json_top_level_fields(self, batch: BatchResult) -> None:
        import json
        data = json.loads(batch.to_json())
        assert data["total"] == 2
        assert data["succeeded"] == 1
        assert data["failed"] == 1
        assert data["skipped"] == 0
        assert "started_at" in data
        assert "finished_at" in data
        assert "duration_seconds" in data
        assert "success_rate" in data

    def test_to_json_results_list(self, batch: BatchResult) -> None:
        import json
        data = json.loads(batch.to_json())
        assert len(data["results"]) == 2
        first = data["results"][0]
        assert first["source"] == "a.txt"
        assert first["status"] == "success"
        assert first["ok"] is True
        assert first["destination"] == str(Path("out/a.txt"))
        assert first["bytes_in"] == 100
        assert first["bytes_out"] == 80

    def test_to_json_null_destination(self, batch: BatchResult) -> None:
        import json
        data = json.loads(batch.to_json())
        second = data["results"][1]
        assert second["destination"] is None

    def test_to_json_empty_batch(self) -> None:
        import json
        b = BatchResult()
        b.finish()
        data = json.loads(b.to_json())
        assert data["total"] == 0
        assert data["results"] == []

    def test_to_json_unfinished_batch_has_null_finished_at(self) -> None:
        import json
        b = BatchResult()
        data = json.loads(b.to_json())
        assert data["finished_at"] is None

    # ── to_csv ───────────────────────────────────────────────────────────

    def test_to_csv_has_header_row(self, batch: BatchResult) -> None:
        csv_str = batch.to_csv()
        lines = csv_str.strip().splitlines()
        header = lines[0]
        assert "source" in header
        assert "status" in header
        assert "ok" in header

    def test_to_csv_correct_row_count(self, batch: BatchResult) -> None:
        csv_str = batch.to_csv()
        lines = csv_str.strip().splitlines()
        assert len(lines) == 3  # header + 2 data rows

    def test_to_csv_data_values(self, batch: BatchResult) -> None:
        import csv, io
        reader = csv.DictReader(io.StringIO(batch.to_csv()))
        rows = list(reader)
        assert rows[0]["source"] == "a.txt"
        assert rows[0]["status"] == "success"
        assert rows[0]["ok"] == "True"
        assert rows[0]["destination"] == str(Path("out/a.txt"))
        assert rows[1]["source"] == "b.txt"
        assert rows[1]["status"] == "failed"
        assert rows[1]["destination"] == ""  # no destination → empty string

    def test_to_csv_empty_batch_only_header(self) -> None:
        csv_str = BatchResult().to_csv()
        lines = csv_str.strip().splitlines()
        assert len(lines) == 1  # header only
