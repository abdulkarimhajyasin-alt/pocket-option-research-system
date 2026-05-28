"""Base abstractions for reusable indicators."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class IndicatorMetadata:
    """Describes an indicator implementation."""

    name: str
    category: str
    description: str
    default_parameters: dict[str, int | float | str] = field(default_factory=dict)


class BaseIndicator(Generic[T], ABC):
    """Abstract base class for all reusable indicators."""

    metadata: IndicatorMetadata

    @abstractmethod
    def calculate(self, values: Sequence[T]) -> float | None:
        """Calculate the latest indicator value from an ordered input sequence."""

    def validate_period(self, period: int) -> None:
        """Validate a lookback period."""
        if period <= 0:
            raise ValueError("Indicator period must be greater than zero")

    def validate_values(self, values: Sequence[T], min_length: int = 1) -> None:
        """Validate that enough input values are available."""
        if len(values) < min_length:
            raise ValueError(f"Indicator requires at least {min_length} values")
