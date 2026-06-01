"""Data constraints documents."""

from __future__ import annotations

from app.trading_requirements.models import ConstraintCategory, ConstraintItem


class DataConstraintsBuilder:
    """Build data constraints only."""

    def build(self) -> ConstraintCategory:
        topics = [
            "Data quality requirements",
            "Timestamp consistency requirements",
            "Dataset versioning requirements",
            "Audit trail requirements",
            "Snapshot retention requirements",
            "Source validation requirements",
        ]
        return ConstraintCategory(
            category_id="data",
            title="Data Constraints",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return ConstraintItem(
            constraint_id=f"DATA-{index:02d}",
            title=title,
            description=f"Define {title.lower()} for future data architecture.",
            category="data",
            constraint_type="hard",
            priority="متوسط",
            safety_notes=["Local research data remains separate from future external systems."],
        ).to_dict()
