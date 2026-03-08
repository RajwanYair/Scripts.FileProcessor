"""Unit tests for file_processor.core.file_utils."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from file_processor.core.file_utils import EXT_MAP, normalize_extension, sanitize_filename

# Characters that are always forbidden in cross-platform filenames
_FORBIDDEN = set('<>:"/\\|?*')
# ASCII control characters (0x00-0x1F)
_CONTROL_CHARS = {chr(i) for i in range(0x20)}


@pytest.mark.unit
class TestSanitizeFilename:
    def test_replaces_forbidden_chars(self) -> None:
        # Single forbidden char → single underscore
        assert sanitize_filename("bad/name") == "bad_name"

    def test_collapses_consecutive_forbidden_chars(self) -> None:
        # Multiple consecutive forbidden chars → collapsed to one underscore
        result = sanitize_filename("bad<>name")
        assert "__" not in result
        assert "_" in result

    def test_collapses_multiple_underscores(self) -> None:
        result = sanitize_filename("a___b")
        assert "__" not in result

    def test_strips_leading_trailing_dots_and_underscores(self) -> None:
        result = sanitize_filename("._hello_.")
        assert not result.startswith((".", "_"))
        assert not result.endswith((".", "_"))

    def test_strips_control_characters(self) -> None:
        result = sanitize_filename("name\x00\x1f.txt")
        assert "\x00" not in result
        assert "\x1f" not in result

    def test_empty_string_returns_unnamed(self) -> None:
        assert sanitize_filename("") == "unnamed"

    def test_only_forbidden_chars_returns_unnamed(self) -> None:
        assert sanitize_filename('<>:"/\\|?*') == "unnamed"

    def test_unicode_preserved(self) -> None:
        result = sanitize_filename("ñoño_文件")
        assert "ñoño" in result
        assert "文件" in result

    def test_normal_filename_unchanged(self) -> None:
        assert sanitize_filename("report_2026.pdf") == "report_2026.pdf"


@pytest.mark.unit
class TestNormalizeExtension:
    @pytest.mark.parametrize(
        "input_ext, expected_ext",
        [
            (".jpeg", ".jpg"),
            (".JPEG", ".jpg"),
            (".tiff", ".tif"),
            (".jpe", ".jpg"),
            (".jfif", ".jpg"),
        ],
    )
    def test_maps_alias_to_canonical(self, input_ext: str, expected_ext: str) -> None:
        result = normalize_extension(f"photo{input_ext}")
        assert result.endswith(expected_ext)

    def test_unknown_extension_unchanged(self) -> None:
        assert normalize_extension("file.py") == "file.py"

    def test_no_extension_unchanged(self) -> None:
        assert normalize_extension("Makefile") == "Makefile"

    def test_all_registered_aliases_present(self) -> None:
        # Ensure EXT_MAP is not empty
        assert len(EXT_MAP) > 5


# ── Hypothesis property-based tests ───────────────────────────────────────────


@pytest.mark.unit
class TestSanitizeFilenameProperties:
    @given(st.text(min_size=1))
    @settings(max_examples=200)
    def test_result_never_empty(self, name: str) -> None:
        """sanitize_filename always returns a non-empty string."""
        assert len(sanitize_filename(name)) > 0

    @given(st.text(min_size=1))
    @settings(max_examples=200)
    def test_result_contains_no_forbidden_chars(self, name: str) -> None:
        """Output never contains forbidden cross-platform filename characters."""
        result = sanitize_filename(name)
        assert not (_FORBIDDEN & set(result))

    @given(st.text(min_size=1))
    @settings(max_examples=200)
    def test_result_contains_no_control_chars(self, name: str) -> None:
        """Output never contains non-printable control characters."""
        result = sanitize_filename(name)
        assert not (_CONTROL_CHARS & set(result))

    @given(st.text(min_size=1))
    @settings(max_examples=200)
    def test_idempotent(self, name: str) -> None:
        """Sanitizing an already-sanitized filename is a no-op."""
        once = sanitize_filename(name)
        twice = sanitize_filename(once)
        assert once == twice
