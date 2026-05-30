"""Typed domain event models for append-only architecture boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class BaseEvent:
    """Base event payload consumed by persistence adapters."""

    event_type: str
    aggregate_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_id: str = field(default_factory=lambda: str(uuid4()))
    domain: str = "generic"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe event dictionary."""
        return {
            "event_id": self.event_id,
            "domain": self.domain,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
        }


@dataclass(frozen=True)
class StrategyEvent(BaseEvent):
    """Strategy research or signal lifecycle event."""

    domain: str = "strategy"


@dataclass(frozen=True)
class ValidationEvent(BaseEvent):
    """Validation and robustness lifecycle event."""

    domain: str = "validation"


@dataclass(frozen=True)
class DatasetEvent(BaseEvent):
    """Dataset quality, versioning, or integrity event."""

    domain: str = "dataset"


@dataclass(frozen=True)
class RuntimeEvent(BaseEvent):
    """Runtime, stream, health, or orchestration event."""

    domain: str = "runtime"


@dataclass(frozen=True)
class AnalyticsEvent(BaseEvent):
    """Analytics snapshot or reporting event."""

    domain: str = "analytics"
