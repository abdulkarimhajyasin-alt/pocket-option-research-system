"""Simple candle-direction strategy for pipeline validation only."""

from typing import Any

from loguru import logger

from app.data.models import Candle
from app.signals.signal import SignalDirection, TradeSignal
from app.strategies.base_strategy import BaseStrategy, StrategyMetadata


class SampleCandleDirectionStrategy(BaseStrategy):
    """Generates CALL on bullish candles and PUT on bearish candles."""

    metadata = StrategyMetadata(
        name="sample_candle_direction_strategy",
        description="Validation strategy that follows single-candle direction.",
        version="0.2.0",
    )

    def generate_signal(self, market_data: Any) -> TradeSignal | None:
        """Generate a simple signal from the current candle."""
        candle = self._extract_current_candle(market_data)
        if candle.is_neutral:
            logger.debug("Neutral candle produced no signal at {}", candle.timestamp)
            return None

        direction = SignalDirection.CALL if candle.is_bullish else SignalDirection.PUT
        confidence = self._confidence(candle)
        logger.info("Sample strategy generated {} signal at {}", direction.value, candle.timestamp)

        return TradeSignal(
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            direction=direction,
            confidence=confidence,
            timestamp=candle.timestamp,
            strategy_name=self.name,
        )

    def _extract_current_candle(self, market_data: Any) -> Candle:
        if isinstance(market_data, Candle):
            return market_data
        if isinstance(market_data, dict) and isinstance(market_data.get("current_candle"), Candle):
            return market_data["current_candle"]
        raise TypeError("Sample strategy requires a Candle or context with current_candle")

    def _confidence(self, candle: Candle) -> float:
        body_size = abs(candle.close - candle.open)
        candle_range = candle.high - candle.low
        if candle_range <= 0:
            return 0.60
        return min(0.95, max(0.60, 0.60 + body_size / candle_range * 0.35))
