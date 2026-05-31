"""Arabic recommendations for the research knowledge graph."""

from __future__ import annotations

from app.knowledge_graph.models import KnowledgeDiagnostic, KnowledgeRecommendation


class KnowledgeGraphRecommendations:
    """Generate Arabic graph improvement recommendations."""

    ALLOWED = {
        "تحسين العلاقات",
        "زيادة الربط",
        "تحسين جودة البيانات",
        "تقوية سلاسل المعرفة",
        "تقليل العقد المعزولة",
    }

    def generate(
        self,
        diagnostics: tuple[KnowledgeDiagnostic, ...],
    ) -> tuple[KnowledgeRecommendation, ...]:
        recommendations: list[KnowledgeRecommendation] = []
        seen: set[str] = set()
        for item in diagnostics:
            title = item.detail if item.detail in self.ALLOWED else "تحسين العلاقات"
            if title in seen:
                continue
            seen.add(title)
            recommendations.append(
                KnowledgeRecommendation(
                    title=title,
                    priority=item.severity,
                    reason=item.name,
                )
            )
        return tuple(recommendations)
