"""Broker constraints documents."""

from __future__ import annotations

from app.trading_requirements.models import ConstraintCategory, ConstraintItem


class BrokerConstraintsBuilder:
    """Build broker constraints without broker access."""

    def build(self) -> ConstraintCategory:
        topics = [
            "Broker isolation requirement",
            "No direct broker coupling",
            "Credential vault requirement for any hypothetical future system",
            "Session management requirement",
            "Broker terms review requirement",
            "External integration approval requirement",
        ]
        return ConstraintCategory(
            category_id="broker",
            title="Broker Constraints",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return ConstraintItem(
            constraint_id=f"BROKER-{index:02d}",
            title=title,
            description=f"Define {title.lower()} as a constraint; do not implement broker access.",
            category="broker",
            constraint_type="forbidden-now",
            priority="مرتفع",
            safety_notes=["Broker access remains forbidden in the current repository."],
        ).to_dict()
