"""Strategy base abstractions."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from app.signals.signal import TradeSignal


@dataclass(frozen=True)
class StrategyMetadata:
    """Describes a strategy module without coupling it to execution."""

    name: str
    description: str
    version: str = "0.1.0"
    required_indicators: tuple[str, ...] = ()
    supports_multi_timeframe: bool = False


@dataclass(frozen=True)
class StrategySessionRestriction:
    """Defines optional session restrictions for a strategy."""

    enabled: bool = False
    sessions: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategyParameters:
    """Configurable strategy parameters shared by backtesting and demo flows."""

    values: dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.60
    session_restriction: StrategySessionRestriction = field(
        default_factory=StrategySessionRestriction
    )
    symbols: tuple[str, ...] = ()
    timeframes: tuple[str, ...] = ()


class BaseStrategy(ABC):
    """Abstract base class for all experimental trading strategies."""

    metadata = StrategyMetadata(
        name="base_strategy",
        description="Base strategy abstraction",
    )

    def __init__(self, parameters: StrategyParameters | None = None) -> None:
        self.parameters = parameters or StrategyParameters()
        self.initialized = False

    @property
    def name(self) -> str:
        """Return the stable strategy name."""
        return self.metadata.name

    @property
    def required_indicators(self) -> tuple[str, ...]:
        """Return required indicator names."""
        return self.metadata.required_indicators

    def initialize(self) -> None:
        """Initialize strategy resources without creating execution side effects."""
        logger.info("Initializing strategy {}", self.name)
        self.validate_environment()
        self.initialized = True

    def on_candle(self, market_data: Any) -> TradeSignal | None:
        """Process a candle context and optionally generate a signal."""
        if not self.initialized:
            self.initialize()
        return self.generate_signal(market_data)

    @abstractmethod
    def generate_signal(self, market_data: Any) -> TradeSignal | None:
        """Generate a trade signal from market data, or return None."""

    def validate_environment(self) -> bool:
        """Validate strategy configuration before signal generation."""
        threshold = self.parameters.confidence_threshold
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Strategy confidence threshold must be between 0 and 1")
        logger.info("Strategy {} environment validated", self.name)
        return True

    def score_confidence(self, scores: Sequence[float]) -> float:
        """Return a normalized confidence score from simple component scores."""
        valid_scores = [score for score in scores if 0.0 <= score <= 1.0]
        if not valid_scores:
            return 0.0
        return sum(valid_scores) / len(valid_scores)
