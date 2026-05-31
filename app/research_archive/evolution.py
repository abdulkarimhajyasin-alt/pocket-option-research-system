"""Research archive evolution engine."""

from __future__ import annotations

from typing import Any

from app.research_archive.models import ResearchEvolution

IMPROVING = "يتحسن"
STABLE = "مستقر"
DECLINING = "يتراجع"
INSUFFICIENT = "غير كاف للتقييم"


class ResearchEvolutionEngine:
    """Analyze historical research quality across archive versions."""

    def analyze(
        self,
        versions: list[dict[str, Any]],
        snapshots: list[dict[str, Any]],
        diagnostics: list[dict[str, Any]],
        recommendations: list[str],
    ) -> ResearchEvolution:
        if len(snapshots) < 2:
            return ResearchEvolution(
                version_count=len(versions),
                readiness_trend=INSUFFICIENT,
                knowledge_score_trend=INSUFFICIENT,
                graph_density_trend=INSUFFICIENT,
                diagnostics_trend=INSUFFICIENT,
                recommendation_trend=INSUFFICIENT,
                source_coverage_trend=INSUFFICIENT,
                research_quality_trend=INSUFFICIENT,
                recurring_diagnostics=self._recurring(diagnostics),
            )
        coverage = [self._metric(item, "source_summary.source_coverage") for item in snapshots]
        missing = [self._metric(item, "source_summary.missing_source_count") for item in snapshots]
        included = [
            self._metric(item, "source_summary.included_source_count")
            for item in snapshots
        ]
        return ResearchEvolution(
            version_count=len(versions),
            readiness_trend=self._trend(coverage),
            knowledge_score_trend=self._trend(included),
            graph_density_trend=self._trend(included),
            diagnostics_trend=self._reverse_trend(missing),
            recommendation_trend=STABLE if recommendations else INSUFFICIENT,
            source_coverage_trend=self._trend(coverage),
            research_quality_trend=self._trend(coverage),
            recurring_diagnostics=self._recurring(diagnostics),
        )

    def _metric(self, payload: dict[str, Any], dotted: str) -> float:
        value: Any = payload
        for part in dotted.split("."):
            if not isinstance(value, dict):
                return 0.0
            value = value.get(part)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _trend(self, values: list[float]) -> str:
        if len(values) < 2:
            return INSUFFICIENT
        if values[-1] > values[0]:
            return IMPROVING
        if values[-1] < values[0]:
            return DECLINING
        return STABLE

    def _reverse_trend(self, values: list[float]) -> str:
        if len(values) < 2:
            return INSUFFICIENT
        if values[-1] < values[0]:
            return IMPROVING
        if values[-1] > values[0]:
            return DECLINING
        return STABLE

    def _recurring(self, diagnostics: list[dict[str, Any]]) -> list[str]:
        counts: dict[str, int] = {}
        for item in diagnostics:
            code = str(item.get("code", "unknown"))
            counts[code] = counts.get(code, 0) + 1
        return sorted(code for code, count in counts.items() if count > 1)
