"""Tests for reusable technical indicators."""

from datetime import UTC, datetime, timedelta

from app.data.models import Candle
from app.indicators.momentum import RSI
from app.indicators.trend import EMA, SMA
from app.indicators.volatility import ATR


def _candle(index: int, close: float) -> Candle:
    return Candle(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index),
        open=close - 0.0001,
        high=close + 0.0002,
        low=close - 0.0002,
        close=close,
        volume=100,
    )


def test_sma_calculates_latest_average() -> None:
    assert SMA(period=3).calculate([1.0, 2.0, 3.0, 4.0]) == 3.0


def test_ema_returns_value_when_ready() -> None:
    value = EMA(period=3).calculate([1.0, 2.0, 3.0, 4.0])

    assert value is not None
    assert value > 2.0


def test_rsi_returns_bounded_value() -> None:
    value = RSI(period=3).calculate([1.0, 1.1, 1.05, 1.2, 1.15])

    assert value is not None
    assert 0 <= value <= 100


def test_atr_returns_positive_value() -> None:
    candles = [_candle(index, 1.08 + index * 0.0001) for index in range(5)]
    value = ATR(period=3).calculate(candles)

    assert value is not None
    assert value > 0
