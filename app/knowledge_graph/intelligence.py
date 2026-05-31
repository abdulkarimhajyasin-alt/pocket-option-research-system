"""Relationship intelligence for the research knowledge graph."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.knowledge_graph.models import KnowledgeGraphResult


class KnowledgeIntelligenceEngine:
    """Detect recurring relationships and relationship chains."""

    def evaluate(self, graph: KnowledgeGraphResult) -> dict[str, Any]:
        relation_counts = Counter(edge.relationship_type for edge in graph.edges)
        strong = [edge.to_dict() for edge in graph.edges if edge.weight >= 0.7]
        weak = [edge.to_dict() for edge in graph.edges if edge.weight < 0.5]
        return {
            "recurring_relationships": dict(relation_counts),
            "successful_relationship_chains": strong,
            "weak_relationship_chains": weak,
            "asset_pattern_relationships": self._find(graph, "asset", "pattern"),
            "session_pattern_relationships": self._find(graph, "session", "pattern"),
            "regime_pattern_relationships": self._find(graph, "regime", "pattern"),
            "research_only": True,
        }

    def _find(self, graph: KnowledgeGraphResult, source: str, target: str) -> list[dict[str, Any]]:
        return [
            edge.to_dict()
            for edge in graph.edges
            if edge.source_id == source and edge.target_id == target
        ]
