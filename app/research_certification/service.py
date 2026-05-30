"""Research certification orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from app.research_certification.analytics import ResearchCertificationAnalytics
from app.research_certification.certification import ResearchCertificationEngine
from app.research_certification.certification import ResearchMaturityEngine
from app.research_certification.consistency import ResearchConsistencyEngine
from app.research_certification.diagnostics import CertificationDiagnosticsEngine
from app.research_certification.models import ResearchCertificationResult
from app.research_certification.recommendations import CertificationRecommendationEngine
from app.research_certification.reports import ResearchCertificationReportWriter
from app.research_certification.requirements import CertificationRequirementsEngine
from app.research_certification.robustness import ResearchRobustnessEngine
from app.research_certification.scoring import average, clamp
from app.research_certification.stability import ResearchStabilityEngine
from app.research_certification.storage import ResearchCertificationStorage


@dataclass(frozen=True)
class ResearchCertificationRunResult:
    """Result of one certification run."""

    result: ResearchCertificationResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ResearchCertificationService:
    """Evaluate the complete research stack for research certification."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.robustness = ResearchRobustnessEngine()
        self.consistency = ResearchConsistencyEngine()
        self.stability = ResearchStabilityEngine()
        self.requirements = CertificationRequirementsEngine()
        self.certification = ResearchCertificationEngine()
        self.maturity = ResearchMaturityEngine()
        self.diagnostics = CertificationDiagnosticsEngine()
        self.recommendations = CertificationRecommendationEngine()
        self.analytics = ResearchCertificationAnalytics()
        self.storage = ResearchCertificationStorage(
            self.project_root / "storage" / "research_certification"
        )
        self.reports = ResearchCertificationReportWriter(
            self.project_root / "reports" / "research_certification"
        )

    def run(self) -> ResearchCertificationRunResult:
        inputs = self._collect_inputs()
        robustness = self.robustness.evaluate(inputs)
        consistency = self.consistency.evaluate(inputs)
        stability = self.stability.evaluate(inputs)
        requirements = self.requirements.evaluate(
            inputs,
            robustness.score,
            consistency.score,
            stability.score,
        )
        certification = self.certification.evaluate(
            inputs,
            robustness,
            consistency,
            stability,
        )
        maturity = self.maturity.evaluate(inputs, certification.score)
        diagnostic_values = {
            **inputs,
            "robustness_score": robustness.score,
            "consistency_score": consistency.score,
            "stability_score": stability.score,
        }
        diagnostics = self.diagnostics.evaluate(diagnostic_values)
        recommendations = self.recommendations.generate(diagnostics)
        result = ResearchCertificationResult(
            timestamp=datetime.utcnow(),
            certification=certification,
            requirements=requirements,
            robustness=robustness,
            consistency=consistency,
            stability=stability,
            maturity=maturity,
            diagnostics=diagnostics,
            recommendations=recommendations,
            sample_size=int(inputs.get("sample_size", 0)),
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_deployment_approval": True,
                "not_broker_control": True,
                "not_account_interaction": True,
                "not_investment_advice": True,
                "not_profitability_claim": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return ResearchCertificationRunResult(result, analytics, storage_paths, report_paths)

    def _collect_inputs(self) -> dict[str, float]:
        signal = self._summary("reports/signals/signal_summary.json")
        performance = self._summary("reports/signal_performance/performance_summary.json")
        opportunity = self._summary("reports/opportunities/opportunity_summary.json")
        timeframe = self._summary("reports/multi_timeframe/confirmation_summary.json")
        confluence = self._summary("reports/confluence/confluence_summary.json")
        lifecycle = self._summary("reports/trade_lifecycle/lifecycle_summary.json")
        readiness = self._summary("reports/strategy_readiness/readiness_summary.json")
        ops = self._summary("reports/research_ops/operations_summary.json")
        benchmark = self._summary("reports/strategy_benchmark/benchmark_summary.json")
        pattern = self._summary("reports/pattern_memory/pattern_summary.json")
        regime = self._summary("reports/market_regime/regime_summary.json")
        sample_size = self._sample_size(pattern, lifecycle, signal)
        signal_quality = self._first(signal, "average_confidence", "quality_score", 60)
        opportunity_quality = self._first(opportunity, "average_score", "average_quality", 60)
        confluence_quality = self._first(confluence, "average_confluence", "average_score", 60)
        lifecycle_quality = self._first(lifecycle, "average_quality", "quality_score", 60)
        benchmark_score = self._first(benchmark, "highest_score", "average_performance", 60)
        pattern_quality = self._first(pattern, "adaptation_score", "reliability_score", 60)
        regime_score = self._first(regime, "regime_score", "quality_score", 60)
        return {
            "sample_size": sample_size,
            "research_quality": self._first(ops, "health_score", "readiness_score", 60),
            "signal_quality": signal_quality,
            "signal_consistency": self._first(
                performance,
                "consistency_score",
                default=signal_quality,
            ),
            "confidence_accuracy": self._first(performance, "confidence_accuracy", default=60),
            "opportunity_quality": opportunity_quality,
            "timeframe_quality": self._first(timeframe, "average_confirmation", default=60),
            "confluence_quality": confluence_quality,
            "lifecycle_quality": lifecycle_quality,
            "readiness_score": self._first(readiness, "readiness_score", default=60),
            "readiness_stability": self._first(readiness, "stability_score", default=60),
            "benchmark_score": benchmark_score,
            "benchmark_stability": self._first(benchmark, "highest_stability", default=60),
            "pattern_quality": pattern_quality,
            "pattern_reliability": self._first(pattern, "reliability_score", default=60),
            "pattern_stability": self._first(pattern, "stability_score", default=60),
            "pattern_adaptation": self._first(pattern, "adaptation_score", default=60),
            "regime_score": regime_score,
            "regime_stability": self._first(regime, "stability_score", default=60),
        }

    def _summary(self, relative_path: str) -> dict[str, Any]:
        payload = self._load(relative_path)
        summary = payload.get("summary") if isinstance(payload, dict) else {}
        return summary if isinstance(summary, dict) else payload

    def _load(self, relative_path: str) -> dict[str, Any]:
        path = self.project_root / relative_path
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}

    def _sample_size(self, *payloads: dict[str, Any]) -> float:
        for payload in payloads:
            for key in ("pattern_count", "total_lifecycles", "total_signals"):
                if key in payload:
                    return clamp(payload[key])
        return 0.0

    def _first(self, payload: dict[str, Any], *keys: str, default: float = 60.0) -> float:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, dict):
                value = value.get("score")
            if value is not None:
                return clamp(value)
        return average(default)
