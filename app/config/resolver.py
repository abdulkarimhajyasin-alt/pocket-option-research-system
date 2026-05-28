"""Configuration resolution and override helpers."""

import os
from collections.abc import Mapping
from typing import Any


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge two mappings without mutating inputs."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def parse_env_value(value: str) -> object:
    """Parse simple environment override values."""
    lowered = value.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


class ConfigResolver:
    """Resolves layered configuration dictionaries with environment overrides."""

    def __init__(self, env_prefix: str = "TRADING") -> None:
        self.env_prefix = env_prefix

    def resolve(self, layers: list[Mapping[str, Any]]) -> dict[str, Any]:
        """Resolve ordered config layers and apply environment variable overrides."""
        resolved: dict[str, Any] = {}
        for layer in layers:
            resolved = deep_merge(resolved, layer)
        return deep_merge(resolved, self._environment_overrides())

    def _environment_overrides(self) -> dict[str, Any]:
        prefix = f"{self.env_prefix}_"
        overrides: dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            path = key[len(prefix) :].lower().split("__")
            cursor = overrides
            for part in path[:-1]:
                cursor = cursor.setdefault(part, {})
            cursor[path[-1]] = parse_env_value(value)
        return overrides
