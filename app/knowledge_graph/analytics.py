"""Analytics for the research knowledge graph."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.knowledge_graph.models import KnowledgeGraphResult


class KnowledgeGraphAnalytics:
    """Generate graph statistics and quality metrics."""

    def summarize(
        self,
        graph: KnowledgeGraphResult,
        intelligence: dict[str, Any],
    ) -> dict[str, Any]:
        node_stats = Counter(node.entity_type for node in graph.nodes)
        edge_stats = Counter(edge.relationship_type for edge in graph.edges)
        strongest = sorted(graph.edges, key=lambda edge: edge.weight, reverse=True)[:5]
        weakest = sorted(graph.edges, key=lambda edge: edge.weight)[:5]
        return {
            "node_statistics": dict(node_stats),
            "edge_statistics": dict(edge_stats),
            "strongest_relationships": {
                f"{edge.source_id}->{edge.target_id}": edge.confidence for edge in strongest
            },
            "weakest_relationships": {
                f"{edge.source_id}->{edge.target_id}": edge.confidence for edge in weakest
            },
            "relationship_density": {"density": graph.relationship_density * 100.0},
            "graph_quality": {
                "knowledge_score": graph.knowledge_score,
                "node_count": graph.node_count,
                "edge_count": graph.edge_count,
            },
            "intelligence": intelligence,
            "research_only": True,
        }
