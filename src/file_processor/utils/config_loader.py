"""
config_loader.py — YAML configuration loader with environment-variable substitution.

Supports  ``${VAR_NAME:default_value}``  placeholders in YAML values.
Merges multiple config sources with priority:
  CLI args  >  env vars  >  user config file  >  default config file.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import re
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Pattern: ${VAR_NAME}  or  ${VAR_NAME:default}
_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")

_DEFAULT_CONFIG = Path(__file__).parent.parent.parent.parent / "config" / "default_config.yaml"


def _substitute_env(value: str) -> str:
    """Replace ``${VAR:default}`` tokens in a string with env-var values."""

    def _replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        default = match.group(2) or ""
        return os.environ.get(var_name, default)

    return _ENV_PATTERN.sub(_replace, value)


def _walk_and_substitute(node: Any) -> Any:
    """Recursively apply env-var substitution to all string leaves."""
    if isinstance(node, dict):
        return {k: _walk_and_substitute(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_walk_and_substitute(item) for item in node]
    if isinstance(node, str):
        return _substitute_env(node)
    return node


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file with env-var substitution; return empty dict on missing file."""
    if not path.exists():
        logger.debug("Config file not found, skipping: %s", path)
        return {}
    with path.open(encoding="utf-8") as fh:
        raw: Any = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Expected a YAML mapping at top level, got {type(raw).__name__}: {path}")
    return _walk_and_substitute(raw)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *override* into *base* (override wins on conflicts)."""
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(user_config: Path | None = None) -> dict[str, Any]:
    """
    Load and merge configuration layers.

    Parameters
    ----------
    user_config:
        Optional path to a user-supplied config file.

    Returns
    -------
    dict
        Merged configuration dictionary (env vars substituted).
    """
    config = load_yaml(_DEFAULT_CONFIG)
    if user_config:
        config = _deep_merge(config, load_yaml(user_config))
    return config


def merge_configs(*paths: Path) -> dict[str, Any]:
    """
    Load and deep-merge an arbitrary number of YAML config files.

    Files are applied left-to-right; later files override earlier ones.
    Missing files are silently skipped (load_yaml returns ``{}`` for them).

    Parameters
    ----------
    *paths:
        One or more paths to YAML config files.

    Returns
    -------
    dict
        Merged configuration dictionary (env vars substituted).
    """
    result: dict[str, Any] = {}
    for path in paths:
        result = _deep_merge(result, load_yaml(path))
    return result
