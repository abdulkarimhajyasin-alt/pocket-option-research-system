"""Research consistency engine."""

from __future__ import annotations

from app.research_certification.models import ResearchConsistencyScore
from app.research_certification.scoring import average


class ResearchConsistencyEngine:
    """Evaluate consistency across research subsystems."""

    def evaluate(self, inputs: dict[str, float]) -> ResearchConsistencyScore:
        signal = inputs.get("signal_consistency", inputs.get("signal_quality", 0))
        opportunity = inputs.get("opportunity_quality", 0)
        confluence = inputs.get("confluence_quality", 0)
        lifecycle = inputs.get("lifecycle_quality", 0)
        benchmark = inputs.get("benchmark_score", 0)
        score = average(signal, opportunity, confluence, lifecycle, benchmark)
        return ResearchConsistencyScore(
            score,
            signal,
            opportunity,
            confluence,
            lifecycle,
            benchmark,
        )
