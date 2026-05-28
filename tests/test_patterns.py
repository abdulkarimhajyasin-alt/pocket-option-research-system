"""Tests for reusable candle pattern detection."""

from datetime import UTC, datetime, timedelta

from app.data.models import Candle
from app.indicators.patterns import (
    bearish_engulfing,
    bullish_engulfing,
    pin_bar,
    strong_body_candle,
)


def _candle(index: int, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index),
        open=open_price,
        high=high,
        low=low,
        close=close,
    )


def test_bullish_engulfing_detected() -> None:
    previous = _candle(0, 1.1000, 1.1010, 1.0980, 1.0990)
    current = _candle(1, 1.0988, 1.1020, 1.0980, 1.1012)

    assert bullish_engulfing(previous, current).detected is True


def test_bearish_engulfing_detected() -> None:
    previous = _candle(0, 1.0990, 1.1010, 1.0980, 1.1000)
    current = _candle(1, 1.1002, 1.1010, 1.0975, 1.0988)

    assert bearish_engulfing(previous, current).detected is True


def test_pin_bar_detected() -> None:
    candle = _candle(0, 1.1000, 1.1003, 1.0970, 1.1001)

    assert pin_bar(candle).detected is True


def test_strong_body_candle_detected() -> None:
    candle = _candle(0, 1.1000, 1.1030, 1.0998, 1.1028)

    assert strong_body_candle(candle).detected is True
