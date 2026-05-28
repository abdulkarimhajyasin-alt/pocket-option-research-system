"""Reusable candle pattern detection."""

from dataclasses import dataclass
from enum import StrEnum

from app.data.models import Candle


class PatternName(StrEnum):
    """Supported candle pattern names."""

    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    PIN_BAR = "pin_bar"
    STRONG_BODY = "strong_body"


@dataclass(frozen=True)
class PatternResult:
    """Structured result returned by candle pattern detectors."""

    name: PatternName
    detected: bool
    direction: str | None
    confidence: float
    reason: str


def bullish_engulfing(previous: Candle, current: Candle) -> PatternResult:
    """Detect a bullish engulfing pattern."""
    detected = (
        previous.is_bearish
        and current.is_bullish
        and current.open <= previous.close
        and current.close >= previous.open
    )
    return PatternResult(
        name=PatternName.BULLISH_ENGULFING,
        detected=detected,
        direction="call" if detected else None,
        confidence=0.75 if detected else 0.0,
        reason="bullish body engulfs previous bearish body" if detected else "not detected",
    )


def bearish_engulfing(previous: Candle, current: Candle) -> PatternResult:
    """Detect a bearish engulfing pattern."""
    detected = (
        previous.is_bullish
        and current.is_bearish
        and current.open >= previous.close
        and current.close <= previous.open
    )
    return PatternResult(
        name=PatternName.BEARISH_ENGULFING,
        detected=detected,
        direction="put" if detected else None,
        confidence=0.75 if detected else 0.0,
        reason="bearish body engulfs previous bullish body" if detected else "not detected",
    )


def pin_bar(candle: Candle, wick_ratio: float = 2.0) -> PatternResult:
    """Detect a pin bar with a dominant upper or lower wick."""
    body = abs(candle.close - candle.open)
    if body == 0:
        body = 0.0000001

    upper_wick = candle.high - max(candle.open, candle.close)
    lower_wick = min(candle.open, candle.close) - candle.low
    bullish = lower_wick >= body * wick_ratio and lower_wick > upper_wick
    bearish = upper_wick >= body * wick_ratio and upper_wick > lower_wick
    detected = bullish or bearish

    return PatternResult(
        name=PatternName.PIN_BAR,
        detected=detected,
        direction="call" if bullish else "put" if bearish else None,
        confidence=0.70 if detected else 0.0,
        reason="dominant rejection wick" if detected else "not detected",
    )


def strong_body_candle(candle: Candle, min_body_ratio: float = 0.60) -> PatternResult:
    """Detect a candle whose body dominates its total range."""
    candle_range = candle.high - candle.low
    if candle_range <= 0:
        return PatternResult(PatternName.STRONG_BODY, False, None, 0.0, "invalid range")

    body_ratio = abs(candle.close - candle.open) / candle_range
    detected = body_ratio >= min_body_ratio and not candle.is_neutral

    return PatternResult(
        name=PatternName.STRONG_BODY,
        detected=detected,
        direction="call" if candle.is_bullish and detected else "put" if detected else None,
        confidence=min(0.90, body_ratio) if detected else 0.0,
        reason=f"body ratio {body_ratio:.2f}" if detected else "not detected",
    )
