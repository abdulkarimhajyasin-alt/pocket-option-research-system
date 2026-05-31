"""Paper-only execution engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.paper_execution.analytics import PaperExecutionAnalytics
from app.paper_execution.evaluator import PaperOutcomeEvaluator
from app.paper_execution.lifecycle import PaperOrderLifecycleEngine
from app.paper_execution.models import PaperOrder, PaperResult, PaperRiskGate
from app.paper_execution.orders import PaperOrderFactory
from app.paper_execution.risk import PaperRiskEngine


@dataclass(frozen=True)
class PaperExecutionEngineResult:
    """Core paper execution result."""

    orders: tuple[PaperOrder, ...]
    lifecycle: tuple[Any, ...]
    results: tuple[PaperResult, ...]
    risk_gates: tuple[PaperRiskGate, ...]
    analytics: dict[str, Any]
    score: float


class PaperExecutionEngine:
    """Create and evaluate local paper-only orders."""

    def __init__(self) -> None:
        self.orders = PaperOrderFactory()
        self.risk = PaperRiskEngine()
        self.lifecycle = PaperOrderLifecycleEngine(self.risk)
        self.evaluator = PaperOutcomeEvaluator()
        self.analytics = PaperExecutionAnalytics()

    def run(
        self,
        candidates: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> PaperExecutionEngineResult:
        created = self.orders.create(candidates)
        processed, lifecycle = self.lifecycle.process(created)
        results = self.evaluator.evaluate(processed, context)
        completed, completion_events = self.lifecycle.complete(
            processed,
            {item.order_id: item.outcome for item in results},
        )
        analytics = self.analytics.summarize(completed, results)
        risk_gates = self.risk.evaluate(completed, results)
        score = self._score(analytics, risk_gates)
        return PaperExecutionEngineResult(
            orders=completed,
            lifecycle=tuple([*lifecycle, *completion_events]),
            results=results,
            risk_gates=risk_gates,
            analytics=analytics,
            score=score,
        )

    def _score(
        self,
        analytics: dict[str, Any],
        risk_gates: tuple[PaperRiskGate, ...],
    ) -> float:
        win_rate = float(analytics.get("win_rate", 0.0)) * 100
        readiness = float(analytics.get("average_readiness", 0.0))
        risk = sum(item.score for item in risk_gates) / len(risk_gates) if risk_gates else 0.0
        return round(max(0.0, min(100.0, (win_rate + readiness + risk) / 3)), 2)
