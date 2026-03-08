"""Unit tests for file_processor.utils.config_loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from file_processor.utils.config_loader import (
    _deep_merge,
    _substitute_env,
    load_config,
    load_yaml,
    merge_configs,
)

# ── _substitute_env ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSubstituteEnv:
    def test_replaces_set_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_VAR", "hello")
        assert _substitute_env("${MY_VAR}") == "hello"

    def test_uses_default_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("UNSET_VAR", raising=False)
        assert _substitute_env("${UNSET_VAR:fallback}") == "fallback"

    def test_empty_default_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("UNSET_VAR", raising=False)
        assert _substitute_env("${UNSET_VAR:}") == ""

    def test_no_placeholder_unchanged(self) -> None:
        assert _substitute_env("plain string") == "plain string"

    def test_partial_substitution(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PORT", "9000")
        result = _substitute_env("http://localhost:${PORT}/api")
        assert result == "http://localhost:9000/api"


# ── _deep_merge ────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeepMerge:
    def test_override_wins_on_conflict(self) -> None:
        merged = _deep_merge({"a": 1}, {"a": 2})
        assert merged["a"] == 2

    def test_base_preserved_when_no_conflict(self) -> None:
        merged = _deep_merge({"a": 1, "b": 2}, {"b": 3})
        assert merged["a"] == 1

    def test_nested_dicts_merged_recursively(self) -> None:
        base: dict[str, Any] = {"db": {"host": "localhost", "port": 5432}}
        override: dict[str, Any] = {"db": {"port": 5433}}
        merged = _deep_merge(base, override)
        assert merged["db"]["host"] == "localhost"
        assert merged["db"]["port"] == 5433

    def test_non_dict_override_replaces_dict(self) -> None:
        merged = _deep_merge({"a": {"x": 1}}, {"a": "scalar"})
        assert merged["a"] == "scalar"

    def test_empty_override_returns_base_copy(self) -> None:
        base = {"k": "v"}
        merged = _deep_merge(base, {})
        assert merged == base
        # Ensure it's a copy, not the same object
        merged["k"] = "changed"
        assert base["k"] == "v"


# ── load_yaml ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLoadYaml:
    def test_returns_empty_dict_for_missing_file(self, tmp_path: Path) -> None:
        result = load_yaml(tmp_path / "nonexistent.yaml")
        assert result == {}

    def test_parses_valid_yaml(self, tmp_path: Path) -> None:
        cfg = tmp_path / "conf.yaml"
        cfg.write_text("key: value\nnumber: 42\n", encoding="utf-8")
        result = load_yaml(cfg)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_raises_for_non_mapping_yaml(self, tmp_path: Path) -> None:
        cfg = tmp_path / "list.yaml"
        cfg.write_text("- item1\n- item2\n", encoding="utf-8")
        with pytest.raises(ValueError, match="mapping"):
            load_yaml(cfg)

    def test_env_var_substitution_applied(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TEST_HOST", "myhost")
        cfg = tmp_path / "env.yaml"
        cfg.write_text("host: ${TEST_HOST:localhost}\n", encoding="utf-8")
        result = load_yaml(cfg)
        assert result["host"] == "myhost"

    def test_default_used_when_env_unset(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MISSING_VAR", raising=False)
        cfg = tmp_path / "defaults.yaml"
        cfg.write_text("value: ${MISSING_VAR:default_val}\n", encoding="utf-8")
        result = load_yaml(cfg)
        assert result["value"] == "default_val"

    def test_empty_yaml_returns_empty_dict(self, tmp_path: Path) -> None:
        cfg = tmp_path / "empty.yaml"
        cfg.write_text("", encoding="utf-8")
        assert load_yaml(cfg) == {}


# ── load_config ────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLoadConfig:
    def test_returns_dict(self) -> None:
        # Default config always exists in the package
        config = load_config()
        assert isinstance(config, dict)

    def test_user_config_overrides_default(self, tmp_path: Path) -> None:
        user = tmp_path / "user.yaml"
        user.write_text("log_level: DEBUG\n", encoding="utf-8")
        config = load_config(user_config=user)
        assert config.get("log_level") == "DEBUG"

    def test_nonexistent_user_config_falls_back_to_default(self, tmp_path: Path) -> None:
        config = load_config(user_config=tmp_path / "nope.yaml")
        assert isinstance(config, dict)  # No exception; falls back gracefully


# ── merge_configs ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMergeConfigs:
    def _write(self, path: Path, content: str) -> Path:
        path.write_text(content, encoding="utf-8")
        return path

    def test_single_file_returned_as_is(self, tmp_path: Path) -> None:
        f = self._write(tmp_path / "a.yaml", "x: 1\ny: 2\n")
        result = merge_configs(f)
        assert result == {"x": 1, "y": 2}

    def test_later_file_overrides_earlier(self, tmp_path: Path) -> None:
        a = self._write(tmp_path / "a.yaml", "level: info\nport: 8080\n")
        b = self._write(tmp_path / "b.yaml", "level: debug\n")
        result = merge_configs(a, b)
        assert result["level"] == "debug"
        assert result["port"] == 8080  # preserved from first file

    def test_nested_keys_merged_recursively(self, tmp_path: Path) -> None:
        a = self._write(tmp_path / "a.yaml", "db:\n  host: localhost\n  port: 5432\n")
        b = self._write(tmp_path / "b.yaml", "db:\n  port: 5433\n")
        result = merge_configs(a, b)
        assert result["db"]["host"] == "localhost"
        assert result["db"]["port"] == 5433

    def test_missing_file_silently_skipped(self, tmp_path: Path) -> None:
        a = self._write(tmp_path / "a.yaml", "key: value\n")
        missing = tmp_path / "missing.yaml"
        result = merge_configs(a, missing)
        assert result == {"key": "value"}

    def test_no_args_returns_empty_dict(self) -> None:
        assert merge_configs() == {}

    def test_three_file_merge_order(self, tmp_path: Path) -> None:
        a = self._write(tmp_path / "a.yaml", "x: 1\ny: 1\nz: 1\n")
        b = self._write(tmp_path / "b.yaml", "x: 2\ny: 2\n")
        c = self._write(tmp_path / "c.yaml", "x: 3\n")
        result = merge_configs(a, b, c)
        assert result["x"] == 3  # last wins
        assert result["y"] == 2  # second wins over first
        assert result["z"] == 1  # only in first, preserved
