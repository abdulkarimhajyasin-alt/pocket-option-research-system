"""Streaming configuration loading."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from app.streaming.models import normalize_timeframe


@dataclass(frozen=True)
class StreamingConfig:
    """Configuration for read-only stream diagnostics and runtime integration."""

    stream_type: str = "simulated"
    symbols: list[str] = field(default_factory=lambda: ["EURUSD"])
    timeframes: list[str] = field(default_factory=lambda: ["1m"])
    update_interval_seconds: float = 1.0
    latency_ms: float = 25.0
    buffer_size: int = 500
    candle_buffer_size: int = 200
    stale_data_threshold_seconds: float = 120.0
    speed_multiplier: float = 1.0
    validation_strict: bool = False
    seed: int | None = 7
    csv_path: str = "data/sample_eurusd_m1.csv"
    persist_ticks: bool = False

    @classmethod
    def from_yaml(cls, path: Path | str) -> "StreamingConfig":
        """Load streaming configuration from YAML."""
        raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls(
            stream_type=str(raw.get("stream_type", "simulated")),
            symbols=[str(symbol).upper() for symbol in raw.get("symbols", ["EURUSD"])],
            timeframes=[normalize_timeframe(str(tf)) for tf in raw.get("timeframes", ["1m"])],
            update_interval_seconds=float(raw.get("update_interval_seconds", 1.0)),
            latency_ms=float(raw.get("latency_ms", 25.0)),
            buffer_size=int(raw.get("buffer_size", 500)),
            candle_buffer_size=int(raw.get("candle_buffer_size", 200)),
            stale_data_threshold_seconds=float(raw.get("stale_data_threshold_seconds", 120.0)),
            speed_multiplier=float(raw.get("speed_multiplier", 1.0)),
            validation_strict=bool(raw.get("validation_strict", False)),
            seed=raw.get("seed"),
            csv_path=str(raw.get("csv_path", "data/sample_eurusd_m1.csv")),
            persist_ticks=bool(raw.get("persist_ticks", False)),
        )
