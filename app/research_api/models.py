"""Typed models for the unified research API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SNAPSHOT_ID = "unified_research_snapshot"
GENERATED_AT = "deterministic-local-research-snapshot"


@dataclass(frozen=True)
class ResearchView:
    """Canonical research view payload."""

    view_id: str
    label_ar: str
    data: dict[str, Any]
    available: bool
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "label_ar": self.label_ar,
            "data": self.data,
            "available": self.available,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class UnifiedResearchSnapshot:
    """Stable local research snapshot exposed by the unified API."""

    snapshot_id: str
    generated_at: str
    signals: ResearchView
    opportunities: ResearchView
    paper: ResearchView
    readiness: ResearchView
    knowledge_graph: ResearchView
    diagnostics: ResearchView
    recommendations: ResearchView
    labels_ar: dict[str, str]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "generated_at": self.generated_at,
            "signals": self.signals.to_dict(),
            "opportunities": self.opportunities.to_dict(),
            "paper": self.paper.to_dict(),
            "readiness": self.readiness.to_dict(),
            "knowledge_graph": self.knowledge_graph.to_dict(),
            "diagnostics": self.diagnostics.to_dict(),
            "recommendations": self.recommendations.to_dict(),
            "labels_ar": self.labels_ar,
            "metadata": self.metadata,
            "research_only": True,
            "local_only": True,
            "not_execution": True,
            "not_broker_access": True,
            "not_browser_automation": True,
        }
