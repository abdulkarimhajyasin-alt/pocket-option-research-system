"""Reporting helpers for explainable strategy decisions."""

from collections import Counter
from typing import Any

from app.strategies.research.models import StrategyDecision


class StrategyResearchReporter:
    """Generate summaries, evidence breakdowns, and quality explanations."""

    def decision_summary(self, decision: StrategyDecision) -> dict[str, Any]:
        """Return one compact decision summary."""
        return {
            "strategy_name": decision.strategy_name,
            "symbol": decision.symbol,
            "timeframe": decision.timeframe,
            "timestamp": decision.timestamp.isoformat(),
            "direction": decision.direction.value if decision.direction else None,
            "confidence": round(decision.confidence, 4),
            "generated_signal": decision.generated_signal,
            "evidence_count": len(decision.evidence),
            "rejection_count": len(decision.rejections),
            "quality_explanation": self.signal_quality_explanation(decision),
        }

    def evidence_breakdown(self, decision: StrategyDecision) -> dict[str, int]:
        """Return evidence frequency for one decision."""
        return dict(Counter(item.name for item in decision.evidence))

    def rejection_summary(self, decisions: list[StrategyDecision]) -> dict[str, int]:
        """Return rejection reason counts for decisions."""
        counter: Counter[str] = Counter()
        for decision in decisions:
            for rejection in decision.rejections:
                counter[rejection.reason] += 1
        return dict(counter)

    def signal_quality_explanation(self, decision: StrategyDecision) -> str:
        """Return a concise human-readable quality explanation."""
        if decision.generated_signal and decision.direction:
            return (
                f"{decision.direction.value} signal with confidence "
                f"{decision.confidence:.2f} from {len(decision.evidence)} evidence items"
            )
        if decision.rejections:
            return f"no signal: {decision.rejections[-1].reason}"
        return "no signal: insufficient directional evidence"
