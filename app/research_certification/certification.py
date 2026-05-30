"""Research certification and maturity engines."""

from __future__ import annotations

from app.research_certification.models import CertificationScore, ResearchMaturityScore
from app.research_certification.models import ResearchRobustnessScore
from app.research_certification.models import ResearchConsistencyScore
from app.research_certification.models import ResearchStabilityScore
from app.research_certification.scoring import average, certification_state


class ResearchCertificationEngine:
    """Evaluate the complete research stack for advanced research certification."""

    def evaluate(
        self,
        inputs: dict[str, float],
        robustness: ResearchRobustnessScore,
        consistency: ResearchConsistencyScore,
        stability: ResearchStabilityScore,
    ) -> CertificationScore:
        components = {
            "research_quality": inputs.get("research_quality", 0),
            "signal_quality": inputs.get("signal_quality", 0),
            "stability": stability.score,
            "consistency": consistency.score,
            "robustness": robustness.score,
            "readiness": inputs.get("readiness_score", 0),
            "lifecycle_quality": inputs.get("lifecycle_quality", 0),
            "benchmark_quality": inputs.get("benchmark_score", 0),
            "pattern_quality": inputs.get("pattern_quality", 0),
            "regime_quality": inputs.get("regime_score", 0),
        }
        score = average(*components.values())
        state = certification_state(score)
        explanation = f"قرار اعتماد بحثي فقط بحالة {state} ودرجة {score}."
        return CertificationScore(score, state, explanation, components)


class ResearchMaturityEngine:
    """Generate research maturity score."""

    def evaluate(
        self,
        inputs: dict[str, float],
        certification_score: float,
    ) -> ResearchMaturityScore:
        architecture = 85.0
        validation = average(inputs.get("readiness_score", 0), inputs.get("benchmark_score", 0))
        data = min(inputs.get("sample_size", 0) * 2, 100.0)
        pattern = average(
            inputs.get("pattern_quality", 0),
            inputs.get("pattern_reliability", 0),
        )
        readiness = certification_score
        score = average(architecture, validation, data, pattern, readiness)
        return ResearchMaturityScore(score, architecture, validation, data, pattern, readiness)
