"""Paper-only outcome evaluator using local report data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.paper_execution.models import (
    DIRECTION_NO_TRADE,
    STATUS_ACTIVE,
    STATUS_BREAKEVEN,
    STATUS_LOSS,
    STATUS_REJECTED,
    STATUS_UNRESOLVED,
    STATUS_WIN,
    PaperOrder,
    PaperResult,
)


class PaperOutcomeEvaluator:
    """Evaluate local paper outcomes without external data fetching."""

    def evaluate(
        self,
        orders: tuple[PaperOrder, ...],
        context: dict[str, Any],
    ) -> tuple[PaperResult, ...]:
        results: list[PaperResult] = []
        quality_bias = self._score(context.get("market_observation_score", 70.0))
        lifecycle_bias = self._score(context.get("trade_lifecycle_score", 70.0))
        confluence_bias = self._score(context.get("confluence_score", 70.0))
        for index, order in enumerate(orders, start=1):
            if order.status == STATUS_REJECTED or order.direction == DIRECTION_NO_TRADE:
                results.append(self._result(order, STATUS_UNRESOLVED, 0.0, "paper order rejected"))
                continue
            if order.status != STATUS_ACTIVE:
                results.append(self._result(order, STATUS_UNRESOLVED, 0.0, "paper order inactive"))
                continue
            composite = (
                order.confidence * 0.30
                + order.readiness_score * 0.35
                + confluence_bias * 0.15
                + quality_bias * 0.10
                + lifecycle_bias * 0.10
            )
            if composite >= 86 or (composite >= 74 and index % 3 != 0):
                results.append(self._result(order, STATUS_WIN, 1.0, "local paper score won"))
            elif composite >= 66:
                results.append(self._result(order, STATUS_BREAKEVEN, 0.0, "local paper score flat"))
            else:
                results.append(self._result(order, STATUS_LOSS, -1.0, "local paper score lost"))
        return tuple(results)

    def _result(
        self,
        order: PaperOrder,
        outcome: str,
        simulated_return: float,
        reason: str,
    ) -> PaperResult:
        return PaperResult(
            order_id=order.order_id,
            candidate_id=order.candidate_id,
            signal_id=order.signal_id,
            outcome=outcome,
            simulated_return=simulated_return,
            evaluated_at=datetime.now(UTC).isoformat(),
            reason=reason,
        )

    def _score(self, value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 70.0
