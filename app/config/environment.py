"""Environment profile models for centralized configuration."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EnvironmentName(StrEnum):
    """Supported application environment profiles."""

    LOCAL = "local"
    RESEARCH = "research"
    PAPER = "paper"
    DEBUG = "debug"


@dataclass(frozen=True)
class EnvironmentProfile:
    """Resolved environment profile with optional inheritance metadata."""

    name: EnvironmentName
    inherits: str | None = None
    runtime_config: str = "configs/runtime/paper_runtime.yaml"
    strategy_config: str = "configs/strategies/sample_strategy.yaml"
    risk_config: str = "configs/risk/base_risk.yaml"
    broker_config: str = "configs/brokers/demo_broker.yaml"
    storage_config: str = "configs/storage/persistence.yaml"
    connectivity_config: str = "configs/connectivity/demo_research.yaml"
    mode: str = "paper"
    settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EnvironmentProfile":
        """Create a profile from YAML data."""
        return cls(
            name=EnvironmentName(str(raw.get("name", EnvironmentName.LOCAL.value))),
            inherits=raw.get("inherits"),
            runtime_config=str(raw.get("runtime_config", cls.runtime_config)),
            strategy_config=str(raw.get("strategy_config", cls.strategy_config)),
            risk_config=str(raw.get("risk_config", cls.risk_config)),
            broker_config=str(raw.get("broker_config", cls.broker_config)),
            storage_config=str(raw.get("storage_config", cls.storage_config)),
            connectivity_config=str(raw.get("connectivity_config", cls.connectivity_config)),
            mode=str(raw.get("mode", "paper")),
            settings=dict(raw.get("settings", {})),
        )
