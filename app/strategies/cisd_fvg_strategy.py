"""Architecture-first CISD/FVG research strategy skeleton."""

from typing import Any

from loguru import logger

from app.data.models import Candle
from app.indicators.momentum import RSI
from app.indicators.patterns import (
    bearish_engulfing,
    bullish_engulfing,
    pin_bar,
    strong_body_candle,
)
from app.indicators.trend import EMA, SMA
from app.signals.confidence import ConfidenceScorer, WeightedScore
from app.signals.session_filter import SessionFilter
from app.signals.signal import SignalDirection, TradeSignal
from app.strategies.base_strategy import BaseStrategy, StrategyMetadata, StrategyParameters


class CisdFvgStrategy(BaseStrategy):
    """Professional placeholder strategy showing reusable infrastructure usage."""

    metadata = StrategyMetadata(
        name="cisd_fvg_strategy",
        description="Research skeleton for CISD/FVG-style signal architecture.",
        version="0.1.0",
        required_indicators=("sma", "ema", "rsi"),
        supports_multi_timeframe=True,
    )

    def __init__(self, parameters: StrategyParameters | None = None) -> None:
        super().__init__(parameters=parameters)
        values = self.parameters.values
        self.fast_period = int(values.get("fast_period", 9))
        self.slow_period = int(values.get("slow_period", 21))
        self.rsi_period = int(values.get("rsi_period", 14))
        self.session_filter = SessionFilter()
        self.confidence_scorer = ConfidenceScorer(self.parameters.confidence_threshold)
        self.fast_ema = EMA(self.fast_period)
        self.slow_sma = SMA(self.slow_period)
        self.rsi = RSI(self.rsi_period)

    def validate_environment(self) -> bool:
        """Validate configured strategy parameters and sessions."""
        super().validate_environment()
        if self.fast_period >= self.slow_period:
            raise ValueError("fast_period must be lower than slow_period")
        if self.parameters.session_restriction.enabled:
            self.session_filter.validate_sessions(self.parameters.session_restriction.sessions)
        logger.info("{} configuration validated", self.name)
        return True

    def generate_signal(self, market_data: Any) -> TradeSignal | None:
        """Generate a research signal from reusable infrastructure components."""
        context = self._extract_context(market_data)
        current = context["current_candle"]
        history = context["history"]

        if not self._is_symbol_timeframe_allowed(current):
            return None
        if not self._is_session_allowed(current):
            return None
        if len(history) < self.slow_period + 1:
            logger.info("{} rejected signal: insufficient history", self.name)
            return None

        closes = [candle.close for candle in history]
        fast_value = self.fast_ema.calculate(closes)
        slow_value = self.slow_sma.calculate(closes)
        rsi_value = self.rsi.calculate(closes)
        if fast_value is None or slow_value is None or rsi_value is None:
            logger.info("{} rejected signal: indicators not ready", self.name)
            return None

        direction = self._direction(current, history[-2], fast_value, slow_value, rsi_value)
        if direction is None:
            logger.info("{} rejected signal: no directional alignment", self.name)
            return None

        confidence = self._confidence(
            direction,
            current,
            history[-2],
            fast_value,
            slow_value,
            rsi_value,
        )
        if not self.confidence_scorer.passes(confidence):
            return None

        logger.info("{} generated {} signal confidence={}", self.name, direction.value, confidence)
        return TradeSignal(
            symbol=current.symbol,
            timeframe=current.timeframe,
            direction=direction,
            confidence=confidence,
            timestamp=current.timestamp,
            strategy_name=self.name,
        )

    def _extract_context(self, market_data: Any) -> dict[str, Any]:
        if isinstance(market_data, dict) and isinstance(market_data.get("current_candle"), Candle):
            history = market_data.get("history", ())
            return {"current_candle": market_data["current_candle"], "history": history}
        if isinstance(market_data, Candle):
            return {"current_candle": market_data, "history": (market_data,)}
        raise TypeError("CISD/FVG strategy requires a Candle context")

    def _is_symbol_timeframe_allowed(self, candle: Candle) -> bool:
        symbols = self.parameters.symbols
        timeframes = self.parameters.timeframes
        if symbols and candle.symbol not in symbols:
            logger.info("{} rejected signal: symbol {} not enabled", self.name, candle.symbol)
            return False
        if timeframes and candle.timeframe not in timeframes:
            logger.info("{} rejected signal: timeframe {} not enabled", self.name, candle.timeframe)
            return False
        return True

    def _is_session_allowed(self, candle: Candle) -> bool:
        restriction = self.parameters.session_restriction
        if not restriction.enabled:
            return True
        return self.session_filter.is_allowed(candle.timestamp, restriction.sessions)

    def _direction(
        self,
        current: Candle,
        previous: Candle,
        fast_value: float,
        slow_value: float,
        rsi_value: float,
    ) -> SignalDirection | None:
        bullish_pattern = (
            bullish_engulfing(previous, current).detected
            or pin_bar(current).direction == "call"
        )
        bearish_pattern = (
            bearish_engulfing(previous, current).detected
            or pin_bar(current).direction == "put"
        )

        if fast_value > slow_value and rsi_value >= 50 and bullish_pattern:
            return SignalDirection.CALL
        if fast_value < slow_value and rsi_value <= 50 and bearish_pattern:
            return SignalDirection.PUT
        return None

    def _confidence(
        self,
        direction: SignalDirection,
        current: Candle,
        previous: Candle,
        fast_value: float,
        slow_value: float,
        rsi_value: float,
    ) -> float:
        trend_score = min(
            1.0,
            abs(fast_value - slow_value) / max(current.close * 0.001, 0.00001),
        )
        momentum_score = abs(rsi_value - 50) / 50
        body_pattern = strong_body_candle(current)
        engulfing = (
            bullish_engulfing(previous, current)
            if direction == SignalDirection.CALL
            else bearish_engulfing(previous, current)
        )
        pattern_score = max(
            body_pattern.confidence,
            engulfing.confidence,
            pin_bar(current).confidence,
        )
        return self.confidence_scorer.weighted(
            [
                WeightedScore("trend", trend_score, 0.35),
                WeightedScore("momentum", momentum_score, 0.25),
                WeightedScore("pattern", pattern_score, 0.40),
            ]
        )
