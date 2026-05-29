"""Reusable research filters for strategy signal generation."""

from dataclasses import dataclass

from app.data.models import Candle
from app.indicators.volatility import ATR


@dataclass(frozen=True)
class FilterResult:
    """Structured filter result."""

    name: str
    passed: bool
    reason: str = ""
    value: float | str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return serializable filter result."""
        return {
            "name": self.name,
            "passed": self.passed,
            "reason": self.reason,
            "value": self.value,
        }


class ResearchFilters:
    """Volatility, session, and candle-shape filters for research strategies."""

    def __init__(self, atr_period: int = 14) -> None:
        self.atr = ATR(atr_period)

    def atr_between(
        self,
        candles: tuple[Candle, ...],
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> FilterResult:
        """Require ATR to sit inside optional min/max thresholds."""
        value = self.atr.calculate(candles)
        if value is None:
            return FilterResult("atr_between", False, "atr_not_ready")
        if minimum is not None and value < minimum:
            return FilterResult("atr_between", False, "atr_below_minimum", round(value, 6))
        if maximum is not None and value > maximum:
            return FilterResult("atr_between", False, "atr_above_maximum", round(value, 6))
        return FilterResult("atr_between", True, "volatility_acceptable", round(value, 6))

    def session_allowed(self, session: str, allowed_sessions: tuple[str, ...]) -> FilterResult:
        """Require current session to be allowlisted."""
        if not allowed_sessions or session in allowed_sessions:
            return FilterResult("session_allowed", True, "session_allowed", session)
        return FilterResult("session_allowed", False, "session_not_allowed", session)

    def candle_body_strength(self, candle: Candle, minimum_ratio: float) -> FilterResult:
        """Require candle body to be large enough relative to range."""
        ratio = self._body_ratio(candle)
        if ratio < minimum_ratio:
            return FilterResult(
                "candle_body_strength",
                False,
                "weak_candle_body",
                round(ratio, 4),
            )
        return FilterResult("candle_body_strength", True, "body_confirmed", round(ratio, 4))

    def avoid_low_range(self, candle: Candle, minimum_range: float) -> FilterResult:
        """Reject candles with very small high-low range."""
        candle_range = candle.high - candle.low
        if candle_range < minimum_range:
            return FilterResult(
                "avoid_low_range", False, "low_range_candle", round(candle_range, 6)
            )
        return FilterResult("avoid_low_range", True, "range_acceptable", round(candle_range, 6))

    def avoid_excessive_wick(self, candle: Candle, maximum_wick_ratio: float) -> FilterResult:
        """Reject candles dominated by wicks."""
        candle_range = max(candle.high - candle.low, 0.0000001)
        body = abs(candle.close - candle.open)
        wick_ratio = (candle_range - body) / candle_range
        if wick_ratio > maximum_wick_ratio:
            return FilterResult(
                "avoid_excessive_wick",
                False,
                "excessive_wick",
                round(wick_ratio, 4),
            )
        return FilterResult("avoid_excessive_wick", True, "wick_acceptable", round(wick_ratio, 4))

    def _body_ratio(self, candle: Candle) -> float:
        candle_range = max(candle.high - candle.low, 0.0000001)
        return abs(candle.close - candle.open) / candle_range
