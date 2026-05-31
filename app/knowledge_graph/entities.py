"""Knowledge graph entity builders."""

from __future__ import annotations

from typing import Any

from app.knowledge_graph.models import GraphNode


class KnowledgeEntityBuilder:
    """Build canonical graph nodes from local research report summaries."""

    ENTITY_TYPES = (
        "SignalEntity",
        "AssetEntity",
        "SessionEntity",
        "PatternEntity",
        "RegimeEntity",
        "OpportunityEntity",
        "ConfluenceEntity",
        "PaperResultEntity",
        "PortfolioEntity",
        "ReadinessEntity",
    )

    def build(self, sources: dict[str, Any]) -> tuple[GraphNode, ...]:
        return tuple(
            GraphNode(
                node_id=self._node_id(entity_type),
                entity_type=entity_type,
                label=entity_type.replace("Entity", ""),
                confidence=self._confidence(entity_type, sources),
                metadata={"research_only": True, "source": self._source_name(entity_type)},
            )
            for entity_type in self.ENTITY_TYPES
        )

    def _node_id(self, entity_type: str) -> str:
        return entity_type.replace("Entity", "").lower()

    def _source_name(self, entity_type: str) -> str:
        mapping = {
            "SignalEntity": "signal_intelligence",
            "AssetEntity": "paper_portfolio",
            "SessionEntity": "signal_intelligence",
            "PatternEntity": "pattern_memory",
            "RegimeEntity": "market_regime",
            "OpportunityEntity": "opportunity_engine",
            "ConfluenceEntity": "confluence",
            "PaperResultEntity": "paper_execution",
            "PortfolioEntity": "paper_portfolio",
            "ReadinessEntity": "paper_control_center",
        }
        return mapping[entity_type]

    def _confidence(self, entity_type: str, sources: dict[str, Any]) -> float:
        source = sources.get(self._source_name(entity_type), {})
        if not isinstance(source, dict) or not source:
            return 35.0
        summary = source.get("summary", source)
        if not isinstance(summary, dict):
            return 50.0
        for key in (
            "confidence_score",
            "quality_score",
            "readiness_score",
            "portfolio_score",
            "overall_score",
            "certification_score",
            "health_score",
        ):
            value = self._score(summary.get(key))
            if value > 0:
                return value
        return 70.0

    def _score(self, value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
