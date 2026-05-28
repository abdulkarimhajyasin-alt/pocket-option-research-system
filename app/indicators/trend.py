"""Trend indicators."""

from collections.abc import Sequence

from loguru import logger

from app.indicators.base_indicator import BaseIndicator, IndicatorMetadata


class SMA(BaseIndicator[float]):
    """Simple moving average indicator."""

    metadata = IndicatorMetadata(
        name="sma",
        category="trend",
        description="Simple moving average",
        default_parameters={"period": 14},
    )

    def __init__(self, period: int = 14) -> None:
        self.validate_period(period)
        self.period = period
        logger.info("Initialized SMA indicator period={}", period)

    def calculate(self, values: Sequence[float]) -> float | None:
        """Calculate the latest simple moving average."""
        if len(values) < self.period:
            return None
        window = values[-self.period :]
        return sum(window) / self.period


class EMA(BaseIndicator[float]):
    """Exponential moving average indicator."""

    metadata = IndicatorMetadata(
        name="ema",
        category="trend",
        description="Exponential moving average",
        default_parameters={"period": 14},
    )

    def __init__(self, period: int = 14) -> None:
        self.validate_period(period)
        self.period = period
        logger.info("Initialized EMA indicator period={}", period)

    def calculate(self, values: Sequence[float]) -> float | None:
        """Calculate the latest exponential moving average."""
        if len(values) < self.period:
            return None

        multiplier = 2 / (self.period + 1)
        ema = sum(values[: self.period]) / self.period
        for value in values[self.period :]:
            ema = (value - ema) * multiplier + ema
        return ema
