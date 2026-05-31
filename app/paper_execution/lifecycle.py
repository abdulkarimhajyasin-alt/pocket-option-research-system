"""Paper order lifecycle transitions."""

from __future__ import annotations

from datetime import UTC, datetime
from dataclasses import replace

from app.paper_execution.models import (
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_CREATED,
    STATUS_EXPIRED,
    STATUS_REJECTED,
    STATUS_UNRESOLVED,
    PaperLifecycleEvent,
    PaperOrder,
)
from app.paper_execution.risk import PaperRiskEngine


class PaperOrderLifecycleEngine:
    """Manage paper-only order state transitions."""

    def __init__(self, risk: PaperRiskEngine | None = None) -> None:
        self.risk = risk or PaperRiskEngine()

    def process(
        self,
        orders: tuple[PaperOrder, ...],
    ) -> tuple[tuple[PaperOrder, ...], tuple[PaperLifecycleEvent, ...]]:
        processed: list[PaperOrder] = []
        lifecycle: list[PaperLifecycleEvent] = []
        for order in orders:
            lifecycle.append(self._event(order, STATUS_CREATED, "paper order created"))
            if not self.risk.allow_order(order, processed):
                rejected = replace(order, status=STATUS_REJECTED)
                processed.append(rejected)
                lifecycle.append(self._transition(order, STATUS_REJECTED, "paper risk rejected"))
                continue
            accepted = replace(order, status=STATUS_ACCEPTED)
            lifecycle.append(self._transition(order, STATUS_ACCEPTED, "paper order accepted"))
            active = replace(accepted, status=STATUS_ACTIVE)
            lifecycle.append(self._transition(accepted, STATUS_ACTIVE, "paper order active"))
            processed.append(active)
        return tuple(processed), tuple(lifecycle)

    def complete(
        self,
        orders: tuple[PaperOrder, ...],
        outcomes: dict[str, str],
    ) -> tuple[tuple[PaperOrder, ...], tuple[PaperLifecycleEvent, ...]]:
        completed: list[PaperOrder] = []
        lifecycle: list[PaperLifecycleEvent] = []
        for order in orders:
            outcome = outcomes.get(order.order_id, order.status)
            final_status = STATUS_EXPIRED if outcome == STATUS_UNRESOLVED else outcome
            completed_order = replace(order, status=final_status)
            completed.append(completed_order)
            if final_status != order.status:
                lifecycle.append(
                    self._transition(order, final_status, "paper outcome evaluated")
                )
        return tuple(completed), tuple(lifecycle)

    def _event(self, order: PaperOrder, to_status: str, reason: str) -> PaperLifecycleEvent:
        return PaperLifecycleEvent(
            order_id=order.order_id,
            candidate_id=order.candidate_id,
            from_status="",
            to_status=to_status,
            timestamp=datetime.now(UTC).isoformat(),
            reason=reason,
        )

    def _transition(
        self,
        order: PaperOrder,
        to_status: str,
        reason: str,
    ) -> PaperLifecycleEvent:
        return PaperLifecycleEvent(
            order_id=order.order_id,
            candidate_id=order.candidate_id,
            from_status=order.status,
            to_status=to_status,
            timestamp=datetime.now(UTC).isoformat(),
            reason=reason,
        )
