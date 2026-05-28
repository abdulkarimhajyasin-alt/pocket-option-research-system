"""Momentum indicators."""

from collections.abc import Sequence

from loguru import logger

from app.indicators.base_indicator import BaseIndicator, IndicatorMetadata


class RSI(BaseIndicator[float]):
    """Relative strength index indicator."""

    metadata = IndicatorMetadata(
        name="rsi",
        category="momentum",
        description="Relative strength index",
        default_parameters={"period": 14},
    )

    def __init__(self, period: int = 14) -> None:
        self.validate_period(period)
        self.period = period
        logger.info("Initialized RSI indicator period={}", period)

    def calculate(self, values: Sequence[float]) -> float | None:
        """Calculate the latest RSI value."""
        if len(values) <= self.period:
            return None

        changes = [values[index] - values[index - 1] for index in range(1, len(values))]
        recent_changes = changes[-self.period :]
        gains = [change for change in recent_changes if change > 0]
        losses = [abs(change) for change in recent_changes if change < 0]
        average_gain = sum(gains) / self.period
        average_loss = sum(losses) / self.period

        if average_loss == 0:
            return 100.0

        relative_strength = average_gain / average_loss
        return 100 - (100 / (1 + relative_strength))
