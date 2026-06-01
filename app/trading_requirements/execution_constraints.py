"""Execution constraints documents."""

from __future__ import annotations

from app.trading_requirements.models import ConstraintCategory, ConstraintItem


class ExecutionConstraintsBuilder:
    """Build execution constraints without execution code."""

    def build(self) -> ConstraintCategory:
        topics = [
            "Execution gateway requirements",
            "Command validation requirements",
            "Pre-execution checks",
            "Approval gates",
            "Order audit requirements",
            "Emergency stop requirements",
        ]
        return ConstraintCategory(
            category_id="execution",
            title="Execution Constraints",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return ConstraintItem(
            constraint_id=f"EXEC-{index:02d}",
            title=title,
            description=f"Specify {title.lower()} for future review; do not implement execution.",
            category="execution",
            constraint_type="forbidden-now",
            priority="مرتفع",
            safety_notes=["Execution remains forbidden in the current repository."],
        ).to_dict()
