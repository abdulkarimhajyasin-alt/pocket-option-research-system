"""Typed models for research-only signal stream events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class SignalDirection(str, Enum):
    """Research-only signal classifications."""

    CALL = "CALL"
    PUT = "PUT"
    NO_TRADE = "NO_TRADE"


@dataclass(frozen=True)
class SignalEvent:
    """One research signal generated from passive observation flow."""

    signal_id: str
    timestamp: str
    asset: str
    session: str
    direction: SignalDirection
    confidence: float
    quality: float
    source: str
    observation_id: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "timestamp": self.timestamp,
            "asset": self.asset,
            "session": self.session,
            "direction": self.direction.value,
            "confidence": self.confidence,
            "quality": self.quality,
            "source": self.source,
            "observation_id": self.observation_id,
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_order_placement": True,
        }


@dataclass(frozen=True)
class SignalStreamResult:
    """Generated signal stream result."""

    score: float
    event_count: int
    events: tuple[SignalEvent, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "event_count": self.event_count,
            "events": [item.to_dict() for item in self.events],
        }


@dataclass(frozen=True)
class SignalQueueResult:
    """Signal queue state summary."""

    score: float
    pending: tuple[SignalEvent, ...]
    active: tuple[SignalEvent, ...]
    expired: tuple[SignalEvent, ...]
    rejected: tuple[SignalEvent, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "pending": [item.to_dict() for item in self.pending],
            "active": [item.to_dict() for item in self.active],
            "expired": [item.to_dict() for item in self.expired],
            "rejected": [item.to_dict() for item in self.rejected],
            "pending_count": len(self.pending),
            "active_count": len(self.active),
            "expired_count": len(self.expired),
            "rejected_count": len(self.rejected),
        }


@dataclass(frozen=True)
class SignalTimelineResult:
    """Signal sequence, frequency, density, and activity."""

    score: float
    sequence_count: int
    frequency: float
    density: float
    activity: dict[str, float]
    timeline: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "sequence_count": self.sequence_count,
            "frequency": self.frequency,
            "density": self.density,
            "activity": self.activity,
            "timeline": list(self.timeline),
        }


@dataclass(frozen=True)
class SignalScoreResult:
    """Signal stream scoring dimensions."""

    score: float
    state: str
    explanation: str
    confidence_quality: float
    signal_quality: float
    stream_stability: float
    signal_consistency: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "confidence_quality": self.confidence_quality,
            "signal_quality": self.signal_quality,
            "stream_stability": self.stream_stability,
            "signal_consistency": self.signal_consistency,
        }


@dataclass(frozen=True)
class SignalValidationResult:
    """Signal stream validation dimensions."""

    score: float
    signal_integrity: float
    timeline_integrity: float
    confidence_bounds: float
    stream_consistency: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "signal_integrity": self.signal_integrity,
            "timeline_integrity": self.timeline_integrity,
            "confidence_bounds": self.confidence_bounds,
            "stream_consistency": self.stream_consistency,
        }


@dataclass(frozen=True)
class SignalDiagnostic:
    """Arabic diagnostic for signal stream issues."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class SignalRecommendation:
    """Arabic recommendation for signal stream improvements."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class SignalStreamRun:
    """Complete signal stream engine result."""

    timestamp: datetime
    stream: SignalStreamResult
    queue: SignalQueueResult
    timeline: SignalTimelineResult
    scoring: SignalScoreResult
    validation: SignalValidationResult
    diagnostics: tuple[SignalDiagnostic, ...]
    recommendations: tuple[SignalRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "stream": self.stream.to_dict(),
            "queue": self.queue.to_dict(),
            "timeline": self.timeline.to_dict(),
            "scoring": self.scoring.to_dict(),
            "validation": self.validation.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "signal_generation_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
