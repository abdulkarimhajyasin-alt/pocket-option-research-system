"""Lifecycle state machine for research opportunities."""

from __future__ import annotations

from datetime import datetime

from app.trade_lifecycle.models import LIFECYCLE_STATES, LifecycleState
from app.trade_lifecycle.models import LifecycleTransition


class LifecycleStateMachine:
    """Track valid deterministic lifecycle transitions."""

    def build(self, outcome: str, timestamp: datetime, rejected: bool) -> LifecycleState:
        transitions: list[LifecycleTransition] = []
        current = "فرصة جديدة"
        for next_state, reason in self._path(outcome, rejected):
            transitions.append(
                LifecycleTransition(
                    from_state=current,
                    to_state=next_state,
                    timestamp=timestamp,
                    reason=reason,
                )
            )
            current = next_state
        return LifecycleState(current=current, transitions=tuple(transitions))

    def _path(self, outcome: str, rejected: bool) -> list[tuple[str, str]]:
        if rejected:
            return [
                ("بانتظار التأكيد", "تم فتح دورة بحثية للمراجعة"),
                ("مرفوضة", "لم تستوف شروط الدراسة البحثية"),
            ]
        outcome_state = {
            "WIN": "ناجحة",
            "LOSS": "خاسرة",
            "BREAKEVEN": "محايدة",
            "UNRESOLVED": "انتهت",
        }.get(outcome, "انتهت")
        return [
            ("بانتظار التأكيد", "تم انتظار اكتمال عوامل التأكيد"),
            ("مؤهلة للدراسة", "اكتملت شروط الدراسة البحثية"),
            ("قيد المحاكاة", "تم بدء محاكاة بحثية دون تنفيذ"),
            ("انتهت", "انتهت نافذة التقييم البحثي"),
            (outcome_state, "تم تسجيل نتيجة المحاكاة البحثية"),
        ]

    def is_supported(self, state: str) -> bool:
        return state in LIFECYCLE_STATES
