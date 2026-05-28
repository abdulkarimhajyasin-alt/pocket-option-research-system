"""Volatility indicators."""

from collections.abc import Sequence

from loguru import logger

from app.data.models import Candle
from app.indicators.base_indicator import BaseIndicator, IndicatorMetadata


class ATR(BaseIndicator[Candle]):
    """Average true range indicator."""

    metadata = IndicatorMetadata(
        name="atr",
        category="volatility",
        description="Average true range",
        default_parameters={"period": 14},
    )

    def __init__(self, period: int = 14) -> None:
        self.validate_period(period)
        self.period = period
        logger.info("Initialized ATR indicator period={}", period)

    def calculate(self, values: Sequence[Candle]) -> float | None:
        """Calculate the latest average true range."""
        if len(values) <= self.period:
            return None

        true_ranges: list[float] = []
        for index in range(1, len(values)):
            candle = values[index]
            previous_close = values[index - 1].close
            true_ranges.append(
                max(
                    candle.high - candle.low,
                    abs(candle.high - previous_close),
                    abs(candle.low - previous_close),
                )
            )

        return sum(true_ranges[-self.period :]) / self.period
