"""Typed models for deterministic live observation replay."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LiveObservation:
    """One passive observation replayed as a simulated live event."""

    observation_id: str
    timestamp: str
    source: str
    asset: str
    session: str
    market_state: str
    confidence: float
    quality: float
    readiness: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "asset": self.asset,
            "session": self.session,
            "market_state": self.market_state,
            "confidence": self.confidence,
            "quality": self.quality,
            "readiness": self.readiness,
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
        }


@dataclass(frozen=True)
class ReplayEvent:
    """A deterministic simulated replay event."""

    sequence: int
    observation: LiveObservation
    simulated_offset_seconds: float
    speed_multiplier: int
    state: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "observation": self.observation.to_dict(),
            "simulated_offset_seconds": self.simulated_offset_seconds,
            "speed_multiplier": self.speed_multiplier,
            "state": self.state,
        }


@dataclass(frozen=True)
class ReplayResult:
    """Replay execution summary."""

    score: float
    speed_multiplier: int
    state: str
    event_count: int
    pause_supported: bool
    resume_supported: bool
    reset_supported: bool
    events: tuple[ReplayEvent, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "speed_multiplier": self.speed_multiplier,
            "state": self.state,
            "event_count": self.event_count,
            "pause_supported": self.pause_supported,
            "resume_supported": self.resume_supported,
            "reset_supported": self.reset_supported,
            "events": [item.to_dict() for item in self.events],
        }


@dataclass(frozen=True)
class TimelineResult:
    """Timeline sequence and replay progression."""

    score: float
    sequence_count: int
    coverage: float
    progression: dict[str, float]
    timeline: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "sequence_count": self.sequence_count,
            "coverage": self.coverage,
            "progression": self.progression,
            "timeline": list(self.timeline),
        }


@dataclass(frozen=True)
class ReplayStateResult:
    """Current replay state."""

    state: str
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "score": self.score, "reason": self.reason}


@dataclass(frozen=True)
class ReplayQualityResult:
    """Replay quality dimensions."""

    score: float
    consistency: float
    completeness: float
    reliability: float
    stability: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "consistency": self.consistency,
            "completeness": self.completeness,
            "reliability": self.reliability,
            "stability": self.stability,
        }


@dataclass(frozen=True)
class ReplayReadinessResult:
    """Replay readiness dimensions."""

    score: float
    replay_readiness: float
    timeline_readiness: float
    observation_readiness: float
    infrastructure_readiness: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "replay_readiness": self.replay_readiness,
            "timeline_readiness": self.timeline_readiness,
            "observation_readiness": self.observation_readiness,
            "infrastructure_readiness": self.infrastructure_readiness,
        }


@dataclass(frozen=True)
class ReplayValidationResult:
    """Replay validation dimensions."""

    score: float
    sequence_integrity: float
    timeline_integrity: float
    observation_completeness: float
    replay_consistency: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "sequence_integrity": self.sequence_integrity,
            "timeline_integrity": self.timeline_integrity,
            "observation_completeness": self.observation_completeness,
            "replay_consistency": self.replay_consistency,
        }


@dataclass(frozen=True)
class ReplayDiagnostic:
    """Arabic diagnostic for replay weaknesses."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ReplayRecommendation:
    """Arabic replay recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class LiveObservationResult:
    """Complete deterministic live observation replay result."""

    timestamp: datetime
    observations: tuple[LiveObservation, ...]
    replay: ReplayResult
    timeline: TimelineResult
    state: ReplayStateResult
    quality: ReplayQualityResult
    readiness: ReplayReadinessResult
    validation: ReplayValidationResult
    diagnostics: tuple[ReplayDiagnostic, ...]
    recommendations: tuple[ReplayRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "observations": [item.to_dict() for item in self.observations],
            "replay": self.replay.to_dict(),
            "timeline": self.timeline.to_dict(),
            "state": self.state.to_dict(),
            "quality": self.quality.to_dict(),
            "readiness": self.readiness.to_dict(),
            "validation": self.validation.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
            "live_observation_replay": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
