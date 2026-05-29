"""Dataset layer configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DatasetLayerConfig:
    """Top-level dataset-layer switches and defaults."""

    registry_enabled: bool = True
    quality_checks_enabled: bool = True
    integrity_verification_enabled: bool = True
    normalization_enabled: bool = True
    synthetic_data_enabled: bool = True
    comparison_enabled: bool = True
    dataset_name: str = "sample_eurusd_m1"
    dataset_path: str = "data/sample_eurusd_m1.csv"
    symbol: str = "EURUSD"
    timeframe: str = "1m"
    version: str = "v1"
    tags: tuple[str, ...] = ("sample", "research")
    reports_dir: str = "reports/datasets"
    synthetic_rows: int = 200
    synthetic_seed: int = 42
    synthetic_profiles: tuple[str, ...] = field(
        default_factory=lambda: ("trending", "ranging", "volatile")
    )


class DatasetConfigLoader:
    """Load dataset-layer settings from YAML."""

    def load(self, path: Path | str) -> DatasetLayerConfig:
        """Load dataset config with safe defaults."""
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return DatasetLayerConfig(
            registry_enabled=self._enabled(raw, "dataset_registry", True),
            quality_checks_enabled=self._enabled(raw, "quality_checks", True),
            integrity_verification_enabled=self._enabled(raw, "integrity_verification", True),
            normalization_enabled=self._enabled(raw, "normalization", True),
            synthetic_data_enabled=self._enabled(raw, "synthetic_data", True),
            comparison_enabled=self._enabled(raw, "comparison", True),
            dataset_name=str(raw.get("dataset_name", "sample_eurusd_m1")),
            dataset_path=str(raw.get("dataset_path", "data/sample_eurusd_m1.csv")),
            symbol=str(raw.get("symbol", "EURUSD")),
            timeframe=str(raw.get("timeframe", "1m")),
            version=str(raw.get("version", "v1")),
            tags=tuple(raw.get("tags", ["sample", "research"])),
            reports_dir=str(raw.get("reports_dir", "reports/datasets")),
            synthetic_rows=int(raw.get("synthetic_rows", 200)),
            synthetic_seed=int(raw.get("synthetic_seed", 42)),
            synthetic_profiles=tuple(raw.get("synthetic_profiles", ["trending", "ranging"])),
        )

    def _enabled(self, raw: dict[str, Any], key: str, default: bool) -> bool:
        section = raw.get(key, {})
        if isinstance(section, dict):
            return bool(section.get("enabled", default))
        return bool(section)
