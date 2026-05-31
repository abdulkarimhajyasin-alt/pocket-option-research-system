"""Research knowledge graph engine."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.knowledge_graph.entities import KnowledgeEntityBuilder
from app.knowledge_graph.models import GraphEdge, GraphNode, KnowledgeGraphResult
from app.knowledge_graph.relations import KnowledgeRelationBuilder


class KnowledgeGraphEngine:
    """Build graph nodes, edges, metrics, and relationship strength."""

    def __init__(self) -> None:
        self.entities = KnowledgeEntityBuilder()
        self.relations = KnowledgeRelationBuilder()

    def build(self, sources: dict[str, Any], metadata: dict[str, bool]) -> KnowledgeGraphResult:
        nodes = self.entities.build(sources)
        edges = self.relations.build(nodes)
        density = self._density(nodes, edges)
        score = self._score(nodes, edges, density)
        strongest = self._relationship_label(self._strongest(edges))
        weakest = self._relationship_label(self._weakest(edges))
        now = datetime.now(UTC)
        return KnowledgeGraphResult(
            graph_id=f"knowledge_graph_{now.strftime('%Y%m%d%H%M%S')}",
            generated_at=now.isoformat(),
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges),
            strongest_relationship=strongest,
            weakest_relationship=weakest,
            relationship_density=density,
            knowledge_score=score,
            metadata=metadata,
        )

    def _density(self, nodes: tuple[GraphNode, ...], edges: tuple[GraphEdge, ...]) -> float:
        possible = len(nodes) * max(1, len(nodes) - 1)
        return round(len(edges) / possible, 4) if possible else 0.0

    def _score(
        self,
        nodes: tuple[GraphNode, ...],
        edges: tuple[GraphEdge, ...],
        density: float,
    ) -> float:
        if not nodes:
            return 0.0
        avg_node = sum(node.confidence for node in nodes) / len(nodes)
        avg_edge = sum(edge.confidence for edge in edges) / len(edges) if edges else 0.0
        density_score = min(100.0, density * 400.0)
        return round((avg_node * 0.4) + (avg_edge * 0.4) + (density_score * 0.2), 2)

    def _strongest(self, edges: tuple[GraphEdge, ...]) -> GraphEdge | None:
        return max(edges, key=lambda edge: edge.weight) if edges else None

    def _weakest(self, edges: tuple[GraphEdge, ...]) -> GraphEdge | None:
        return min(edges, key=lambda edge: edge.weight) if edges else None

    def _relationship_label(self, edge: GraphEdge | None) -> str:
        if edge is None:
            return "غير متاح"
        return f"{edge.source_id}->{edge.target_id}:{edge.relationship_type}"
