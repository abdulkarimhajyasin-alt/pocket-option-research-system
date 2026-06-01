"""Monitoring constraints documents."""

from __future__ import annotations

from app.trading_requirements.models import ConstraintCategory, ConstraintItem


class MonitoringConstraintsBuilder:
    """Build monitoring constraints only."""

    def build(self) -> ConstraintCategory:
        topics = [
            "Health check requirements",
            "Alerting requirements",
            "Metrics requirements",
            "Dashboard requirements",
            "Failure detection requirements",
            "Incident reporting requirements",
        ]
        return ConstraintCategory(
            category_id="monitoring",
            title="Monitoring Constraints",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return ConstraintItem(
            constraint_id=f"MON-{index:02d}",
            title=title,
            description=f"Document {title.lower()} before future operational design.",
            category="monitoring",
            constraint_type="future-only",
            priority="متوسط",
            safety_notes=["Monitoring design only; no external connectivity is added."],
        ).to_dict()
