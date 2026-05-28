"""Timeframe conversion and comparison helpers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeframeManager:
    """Provides timeframe conversion and ordering helpers."""

    aliases: dict[str, str] | None = None

    DEFAULT_SECONDS = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "30m": 1800,
        "1h": 3600,
        "4h": 14400,
        "1d": 86400,
    }

    def normalize(self, timeframe: str) -> str:
        """Normalize a timeframe string."""
        normalized = timeframe.strip().lower()
        aliases = self.aliases or {"m1": "1m", "m5": "5m", "h1": "1h", "d1": "1d"}
        return aliases.get(normalized, normalized)

    def to_seconds(self, timeframe: str) -> int:
        """Convert a supported timeframe to seconds."""
        normalized = self.normalize(timeframe)
        if normalized not in self.DEFAULT_SECONDS:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self.DEFAULT_SECONDS[normalized]

    def compare(self, left: str, right: str) -> int:
        """Compare two timeframes by duration."""
        left_seconds = self.to_seconds(left)
        right_seconds = self.to_seconds(right)
        return (left_seconds > right_seconds) - (left_seconds < right_seconds)

    def higher_timeframes(self, timeframe: str) -> tuple[str, ...]:
        """Return configured higher timeframes for future lookup support."""
        seconds = self.to_seconds(timeframe)
        return tuple(name for name, value in self.DEFAULT_SECONDS.items() if value > seconds)

    def aggregation_target(self, source: str, target: str) -> tuple[str, str]:
        """Validate and return a future aggregation source-target pair."""
        if self.compare(source, target) >= 0:
            raise ValueError("Aggregation target must be higher than source timeframe")
        return self.normalize(source), self.normalize(target)
