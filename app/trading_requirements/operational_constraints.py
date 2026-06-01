"""Operational constraints documents."""

from __future__ import annotations

from app.trading_requirements.models import ConstraintCategory, ConstraintItem


class OperationalConstraintsBuilder:
    """Build operational constraints only."""

    def build(self) -> ConstraintCategory:
        topics = [
            "Deployment constraints",
            "Runtime constraints",
            "Incident response constraints",
            "Logging constraints",
            "Change management constraints",
            "Rollback constraints",
            "Maintenance constraints",
        ]
        return ConstraintCategory(
            category_id="operational",
            title="Operational Constraints",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return ConstraintItem(
            constraint_id=f"OPS-{index:02d}",
            title=title,
            description=f"Document {title.lower()} for future operational architecture.",
            category="operational",
            constraint_type="future-only",
            priority="متوسط",
            safety_notes=["Future-only planning constraint."],
        ).to_dict()
