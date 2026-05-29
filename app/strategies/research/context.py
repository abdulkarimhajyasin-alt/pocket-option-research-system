"""Market context builders for strategy research."""

from __future__ import annotations

from datetime import UTC
from typing import Any

from app.data.models import Candle, CandleSeries
from app.signals.session_filter import SessionFilter
from app.strategies.research.models import MarketContext, StrategyContext


class MarketContextBuilder:
    """Build strategy-independent market context from backtest/runtime payloads."""

    def __init__(self, session_filter: SessionFilter | None = None) -> None:
        self.session_filter = session_filter or SessionFilter()

    def from_market_data(self, market_data: Any) -> StrategyContext:
        """Build a research context from the existing strategy market_data shape."""
        if isinstance(market_data, dict):
            current = market_data.get("current_candle")
            history = market_data.get("history", ())
            series = market_data.get("series")
            if not isinstance(current, Candle):
                raise TypeError("market_data requires current_candle")
            candles = tuple(history) if history else (current,)
            if isinstance(series, CandleSeries) and not candles:
                candles = tuple(series)
            return self.from_candles(candles, current)
        if isinstance(market_data, Candle):
            return self.from_candles((market_data,), market_data)
        raise TypeError("Unsupported market_data for strategy research context")

    def from_candles(
        self, candles: tuple[Candle, ...], current: Candle | None = None
    ) -> StrategyContext:
        """Build context from candle history."""
        if not candles:
            raise ValueError("At least one candle is required")
        latest = current or candles[-1]
        market = MarketContext(
            candles=candles,
            latest_candle=latest,
            symbol=latest.symbol,
            timeframe=latest.timeframe,
            session=self.detect_session(latest),
            volatility_state=self._volatility_state(candles),
            trend_state=self._trend_state(candles),
            detected_patterns=(),
            higher_timeframe={"available": False},
        )
        return StrategyContext(market=market)

    def detect_session(self, candle: Candle) -> str:
        """Return the first matching configured UTC session name."""
        timestamp = candle.timestamp.astimezone(UTC)
        for name, window in self.session_filter.sessions.items():
            if window.contains(timestamp):
                return name
        return "off_session"

    def _volatility_state(self, candles: tuple[Candle, ...]) -> str:
        if len(candles) < 5:
            return "unknown"
        ranges = [candle.high - candle.low for candle in candles[-10:]]
        average = sum(ranges) / len(ranges)
        latest = ranges[-1]
        if latest > average * 1.4:
            return "expanding"
        if latest < average * 0.6:
            return "compressed"
        return "normal"

    def _trend_state(self, candles: tuple[Candle, ...]) -> str:
        if len(candles) < 4:
            return "neutral"
        first = candles[-4].close
        last = candles[-1].close
        if last > first:
            return "bullish"
        if last < first:
            return "bearish"
        return "neutral"
