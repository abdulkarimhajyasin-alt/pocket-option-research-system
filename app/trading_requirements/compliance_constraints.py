"""Compliance constraints documents."""

from __future__ import annotations

from app.trading_requirements.models import ConstraintCategory, ConstraintItem


class ComplianceConstraintsBuilder:
    """Build compliance constraints only."""

    def build(self) -> ConstraintCategory:
        topics = [
            "Legal review requirement",
            "Regulatory review requirement",
            "Broker terms review requirement",
            "Jurisdiction review requirement",
            "User responsibility notices",
            "Documentation requirements",
            "Compliance gate requirements",
        ]
        return ConstraintCategory(
            category_id="compliance",
            title="Compliance Constraints",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return ConstraintItem(
            constraint_id=f"COMP-{index:02d}",
            title=title,
            description=f"Constrain future architecture through {title.lower()}.",
            category="compliance",
            constraint_type="hard",
            safety_notes=["No compliance approval is granted by this document."],
        ).to_dict()
