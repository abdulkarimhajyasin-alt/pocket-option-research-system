"""Strategy registry for dynamic loading."""

from collections.abc import Callable

from loguru import logger

from app.config.strategy_config import StrategyConfig
from app.strategies.base_strategy import (
    BaseStrategy,
    StrategyParameters,
    StrategySessionRestriction,
)
from app.strategies.cisd_fvg_strategy import CisdFvgStrategy
from app.strategies.sample_strategy import SampleCandleDirectionStrategy

StrategyFactory = Callable[..., BaseStrategy]


class StrategyRegistry:
    """Registry that maps strategy names to factories."""

    def __init__(self) -> None:
        self._factories: dict[str, StrategyFactory] = {}

    def register(self, name: str, factory: StrategyFactory) -> None:
        """Register a strategy factory by name."""
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("Strategy name is required")
        self._factories[normalized_name] = factory
        logger.info("Registered strategy: {}", normalized_name)

    def get(self, name: str) -> StrategyFactory:
        """Return a strategy factory by name."""
        normalized_name = name.strip().lower()
        if normalized_name not in self._factories:
            raise KeyError(f"Unknown strategy: {name}")
        return self._factories[normalized_name]

    def create(self, name: str, parameters: StrategyParameters | None = None) -> BaseStrategy:
        """Create a strategy instance by name."""
        logger.info("Creating strategy {} with parameters={}", name, parameters)
        return self.get(name)(parameters=parameters)

    def create_from_config(self, config: StrategyConfig) -> BaseStrategy:
        """Create a strategy instance from validated configuration."""
        parameters = StrategyParameters(
            values=config.parameters,
            confidence_threshold=config.confidence_threshold,
            session_restriction=StrategySessionRestriction(
                enabled=bool(config.session_filters),
                sessions=tuple(config.session_filters),
            ),
            symbols=tuple(config.symbols),
            timeframes=tuple(config.timeframes),
        )
        return self.create(config.name, parameters=parameters)

    def names(self) -> tuple[str, ...]:
        """Return registered strategy names."""
        return tuple(sorted(self._factories))


def default_strategy_registry() -> StrategyRegistry:
    """Build the default strategy registry."""
    registry = StrategyRegistry()
    registry.register("sample_candle_direction_strategy", SampleCandleDirectionStrategy)
    registry.register("cisd_fvg_strategy", CisdFvgStrategy)
    return registry
