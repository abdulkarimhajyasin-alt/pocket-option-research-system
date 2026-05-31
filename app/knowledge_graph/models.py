"""Typed models for the research knowledge graph."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


RELATIONSHIP_TYPES = (
    "influences",
    "confirms",
    "contradicts",
    "improves",
    "degrades",
    "correlates_with",
    "linked_to",
    "derived_from",
)


@dataclass(frozen=True)
class GraphNode:
    """One research knowledge graph node."""

    node_id: str
    entity_type: str
    label: str
    confidence: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "entity_type": self.entity_type,
            "label": self.label,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class GraphEdge:
    """One research-only relationship between graph nodes."""

    edge_id: str
    source_id: str
    target_id: str
    relationship_type: str
    weight: float
    confidence: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "weight": self.weight,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class KnowledgeGraphResult:
    """Knowledge graph build result."""

    graph_id: str
    generated_at: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    node_count: int
    edge_count: int
    strongest_relationship: str
    weakest_relationship: str
    relationship_density: float
    knowledge_score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "generated_at": self.generated_at,
            "nodes": [item.to_dict() for item in self.nodes],
            "edges": [item.to_dict() for item in self.edges],
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "strongest_relationship": self.strongest_relationship,
            "weakest_relationship": self.weakest_relationship,
            "relationship_density": self.relationship_density,
            "knowledge_score": self.knowledge_score,
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_broker_access": True,
        }


@dataclass(frozen=True)
class KnowledgeDiagnostic:
    """Arabic diagnostic for graph quality."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class KnowledgeRecommendation:
    """Arabic graph recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class KnowledgeGraphRun:
    """Complete research knowledge graph run."""

    timestamp: datetime
    graph: KnowledgeGraphResult
    intelligence: dict[str, Any]
    analytics: dict[str, Any]
    diagnostics: tuple[KnowledgeDiagnostic, ...]
    recommendations: tuple[KnowledgeRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "graph": self.graph.to_dict(),
            "intelligence": self.intelligence,
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_broker_access": True,
            "not_browser_automation": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_live_trading": True,
            "not_money_handling": True,
            "not_external_execution_adapter": True,
            "not_trading_automation": True,
        }
