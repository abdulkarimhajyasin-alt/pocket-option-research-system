"""Aggregation logic for the unified research API."""

from __future__ import annotations

from typing import Any

from app.research_api.filters import ResearchDataFilter
from app.research_api.models import (
    GENERATED_AT,
    SNAPSHOT_ID,
    ResearchView,
    UnifiedResearchSnapshot,
)
from app.research_api.schemas import schema_metadata


class ResearchAggregationEngine:
    """Aggregate local reports into stable canonical research views."""

    def __init__(self) -> None:
        self.filter = ResearchDataFilter()

    def build_snapshot(
        self,
        sources: dict[str, dict[str, Any]],
        diagnostics: dict[str, Any],
        recommendations: dict[str, Any],
        metadata: dict[str, Any],
    ) -> UnifiedResearchSnapshot:
        labels = self.labels_ar()
        signals = self._view(
            "signals",
            labels["signals"],
            {
                "signals": self.filter.normalize(sources.get("signals", {})),
                "signal_stream": self.filter.normalize(sources.get("signal_stream", {})),
                "confluence": self.filter.normalize(sources.get("confluence", {})),
            },
        )
        opportunities = self._view(
            "opportunities",
            labels["opportunities"],
            {
                "opportunities": self.filter.normalize(sources.get("opportunities", {})),
                "market_regimes": self.filter.normalize(sources.get("market_regimes", {})),
                "pattern_memory": self.filter.normalize(sources.get("pattern_memory", {})),
            },
        )
        paper = self._view(
            "paper",
            labels["paper"],
            {
                "paper_execution": self.filter.normalize(sources.get("paper_execution", {})),
                "paper_portfolio": self.filter.normalize(sources.get("paper_portfolio", {})),
            },
        )
        readiness = self._view(
            "readiness",
            labels["readiness"],
            {
                "readiness": self.filter.normalize(sources.get("readiness", {})),
                "architecture_audit": self.filter.normalize(
                    sources.get("architecture_audit", {})
                ),
                "observation_pipeline": self.filter.normalize(
                    sources.get("observation_pipeline", {})
                ),
            },
        )
        knowledge = self._view(
            "knowledge_graph",
            labels["knowledge_graph"],
            {
                "knowledge_graph": self.filter.normalize(sources.get("knowledge_graph", {})),
            },
        )
        diagnostics_view = self._view("diagnostics", labels["diagnostics"], diagnostics)
        recommendations_view = self._view(
            "recommendations",
            labels["recommendations"],
            recommendations,
        )
        return UnifiedResearchSnapshot(
            snapshot_id=SNAPSHOT_ID,
            generated_at=GENERATED_AT,
            signals=signals,
            opportunities=opportunities,
            paper=paper,
            readiness=readiness,
            knowledge_graph=knowledge,
            diagnostics=diagnostics_view,
            recommendations=recommendations_view,
            labels_ar=labels,
            metadata={**metadata, **schema_metadata()},
        )

    def labels_ar(self) -> dict[str, str]:
        """Return dashboard-ready Arabic labels."""
        return {
            "snapshot": "لقطة البحث الموحدة",
            "signals": "ذكاء الإشارات الموحد",
            "opportunities": "الفرص الموحدة",
            "paper": "التداول الورقي الموحد",
            "readiness": "الجاهزية الموحدة",
            "knowledge_graph": "ملخص خريطة المعرفة",
            "diagnostics": "التشخيص الموحد",
            "recommendations": "التوصيات الموحدة",
        }

    def _view(self, view_id: str, label_ar: str, data: dict[str, Any]) -> ResearchView:
        return ResearchView(
            view_id=view_id,
            label_ar=label_ar,
            data=data,
            available=bool(data),
            metadata={
                "research_only": True,
                "local_only": True,
                "stable_schema": True,
            },
        )
