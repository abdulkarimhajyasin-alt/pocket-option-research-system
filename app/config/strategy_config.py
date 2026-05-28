"""YAML-backed strategy configuration models."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger


@dataclass(frozen=True)
class StrategyConfig:
    """Validated configuration for one strategy."""

    name: str
    enabled: bool = True
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.60
    session_filters: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    timeframes: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate strategy configuration values."""
        if not self.name.strip():
            raise ValueError("Strategy config requires a name")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        if not self.symbols:
            raise ValueError("Strategy config requires at least one symbol")
        if not self.timeframes:
            raise ValueError("Strategy config requires at least one timeframe")


class StrategyConfigLoader:
    """Loads strategy configuration from YAML files."""

    def load(self, path: Path | str) -> StrategyConfig:
        """Load and validate a strategy config from YAML."""
        config_path = Path(path)
        logger.info("Loading strategy config from {}", config_path)
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

        config = StrategyConfig(
            name=str(raw.get("name", "")),
            enabled=bool(raw.get("enabled", True)),
            parameters=dict(raw.get("parameters", {})),
            confidence_threshold=float(raw.get("confidence_threshold", 0.60)),
            session_filters=list(raw.get("session_filters", [])),
            symbols=list(raw.get("symbols", [])),
            timeframes=list(raw.get("timeframes", [])),
        )
        config.validate()
        logger.info("Loaded strategy config {} enabled={}", config.name, config.enabled)
        return config
