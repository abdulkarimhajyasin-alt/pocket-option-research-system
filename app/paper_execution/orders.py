"""Paper order creation from execution-readiness candidates."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.paper_execution.models import (
    DIRECTION_CALL,
    DIRECTION_NO_TRADE,
    DIRECTION_PUT,
    STATUS_CREATED,
    PaperOrder,
)


class PaperOrderFactory:
    """Create local paper orders only."""

    def create(self, candidates: list[dict[str, Any]]) -> tuple[PaperOrder, ...]:
        orders: list[PaperOrder] = []
        for index, candidate in enumerate(candidates, start=1):
            created = str(candidate.get("timestamp") or datetime.now(UTC).isoformat())
            direction = str(candidate.get("direction") or DIRECTION_NO_TRADE)
            if direction not in {DIRECTION_CALL, DIRECTION_PUT, DIRECTION_NO_TRADE}:
                direction = DIRECTION_NO_TRADE
            orders.append(
                PaperOrder(
                    order_id=f"paper_order_{index:04d}",
                    candidate_id=str(candidate.get("candidate_id") or f"candidate_{index:04d}"),
                    signal_id=str(candidate.get("signal_id") or f"signal_{index:04d}"),
                    asset=str(candidate.get("asset") or "paper_asset"),
                    direction=direction,
                    confidence=self._score(candidate.get("confidence")),
                    readiness_score=self._score(candidate.get("readiness")),
                    qualification_state=str(candidate.get("qualification") or "غير متاح"),
                    created_at=created,
                    expiry=self._expiry(created),
                    status=STATUS_CREATED,
                    metadata={**self._metadata(), "candidate_source": "execution_readiness"},
                )
            )
        return tuple(orders)

    def _expiry(self, created_at: str) -> str:
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            created = datetime.now(UTC)
        return (created + timedelta(minutes=1)).isoformat()

    def _score(self, value: Any) -> float:
        try:
            return round(max(0.0, min(100.0, float(value))), 2)
        except (TypeError, ValueError):
            return 0.0

    def _metadata(self) -> dict[str, bool]:
        return {
            "paper_only": True,
            "research_only": True,
            "local_simulation_only": True,
            "not_real_execution": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_account_login": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_real_money": True,
            "not_position_management": True,
            "not_trading_automation": True,
        }
