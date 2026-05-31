"""Knowledge graph relationship builders."""

from __future__ import annotations

from app.knowledge_graph.models import GraphEdge, GraphNode


class KnowledgeRelationBuilder:
    """Create research-only relationships between graph entities."""

    RELATIONS = (
        ("signal", "opportunity", "influences", 0.78),
        ("opportunity", "confluence", "confirms", 0.82),
        ("confluence", "paperresult", "derived_from", 0.74),
        ("paperresult", "portfolio", "improves", 0.68),
        ("portfolio", "readiness", "influences", 0.72),
        ("pattern", "signal", "correlates_with", 0.70),
        ("regime", "pattern", "influences", 0.66),
        ("session", "pattern", "linked_to", 0.62),
        ("asset", "pattern", "linked_to", 0.65),
        ("regime", "opportunity", "confirms", 0.58),
        ("signal", "regime", "contradicts", 0.42),
        ("paperresult", "readiness", "degrades", 0.36),
    )

    def build(self, nodes: tuple[GraphNode, ...]) -> tuple[GraphEdge, ...]:
        node_ids = {node.node_id for node in nodes}
        edges: list[GraphEdge] = []
        for index, (source, target, relation, weight) in enumerate(self.RELATIONS, start=1):
            if source not in node_ids or target not in node_ids:
                continue
            edges.append(
                GraphEdge(
                    edge_id=f"edge_{index:03d}",
                    source_id=source,
                    target_id=target,
                    relationship_type=relation,
                    weight=round(weight, 2),
                    confidence=round(weight * 100.0, 2),
                    metadata={"research_only": True},
                )
            )
        return tuple(edges)
