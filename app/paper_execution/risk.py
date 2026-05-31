"""Paper-only risk gates."""

from __future__ import annotations

from app.paper_execution.analytics import PaperExecutionAnalytics
from app.paper_execution.models import (
    RISK_FAIL,
    RISK_PASS,
    RISK_WARNING,
    STATUS_LOSS,
    STATUS_REJECTED,
    PaperOrder,
    PaperResult,
    PaperRiskGate,
)


class PaperRiskEngine:
    """Evaluate local paper-only risk gates without real money."""

    max_paper_orders = 20
    max_consecutive_paper_losses = 3
    minimum_readiness_score = 70.0
    minimum_confidence = 60.0
    maximum_simulated_drawdown = 4.0

    def evaluate(
        self,
        orders: tuple[PaperOrder, ...],
        results: tuple[PaperResult, ...],
    ) -> tuple[PaperRiskGate, ...]:
        analytics = PaperExecutionAnalytics().summarize(orders, results)
        return (
            self._gate(
                "max_paper_orders",
                "حد الأوامر الورقية",
                self.max_paper_orders - len(orders),
                len(orders) <= self.max_paper_orders,
                len(orders) <= self.max_paper_orders + 5,
            ),
            self._gate(
                "max_consecutive_paper_losses",
                "حد الخسائر الورقية المتتالية",
                self.max_consecutive_paper_losses
                - analytics["paper_streaks"]["max_paper_loss_streak"],
                analytics["paper_streaks"]["max_paper_loss_streak"]
                <= self.max_consecutive_paper_losses,
                analytics["paper_streaks"]["max_paper_loss_streak"]
                <= self.max_consecutive_paper_losses + 1,
            ),
            self._score_gate(
                "minimum_readiness_score",
                "حد الجاهزية الورقية",
                analytics["average_readiness"],
                self.minimum_readiness_score,
            ),
            self._score_gate(
                "minimum_confidence",
                "حد الثقة الورقية",
                analytics["average_confidence"],
                self.minimum_confidence,
            ),
            self._gate(
                "maximum_simulated_drawdown",
                "حد التراجع الورقي",
                self.maximum_simulated_drawdown - analytics["paper_drawdown"],
                analytics["paper_drawdown"] <= self.maximum_simulated_drawdown,
                analytics["paper_drawdown"] <= self.maximum_simulated_drawdown + 2,
            ),
        )

    def allow_order(self, order: PaperOrder, current_orders: list[PaperOrder]) -> bool:
        if len(current_orders) >= self.max_paper_orders:
            return False
        if order.direction == "NO_TRADE":
            return False
        if order.readiness_score < self.minimum_readiness_score:
            return False
        if order.confidence < self.minimum_confidence:
            return False
        return order.status != STATUS_REJECTED

    def _score_gate(
        self,
        name: str,
        label: str,
        score: float,
        threshold: float,
    ) -> PaperRiskGate:
        if score >= threshold:
            status = RISK_PASS
        elif score >= threshold - 10:
            status = RISK_WARNING
        else:
            status = RISK_FAIL
        return PaperRiskGate(
            name=name,
            arabic_label=label,
            status=status,
            score=round(max(0.0, min(100.0, score)), 2),
            detail=f"{label}: {round(score, 2)}",
        )

    def _gate(
        self,
        name: str,
        label: str,
        margin: float,
        passed: bool,
        warned: bool,
    ) -> PaperRiskGate:
        status = RISK_PASS if passed else RISK_WARNING if warned else RISK_FAIL
        score = 100.0 if passed else 65.0 if warned else 25.0
        return PaperRiskGate(
            name=name,
            arabic_label=label,
            status=status,
            score=score,
            detail=f"{label}: هامش ورقي {round(margin, 2)}",
        )

    def consecutive_losses(self, results: tuple[PaperResult, ...]) -> int:
        count = 0
        for result in reversed(results):
            if result.outcome == STATUS_LOSS:
                count += 1
            else:
                break
        return count
