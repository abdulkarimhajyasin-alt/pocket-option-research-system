"""Risk requirements documents."""

from __future__ import annotations

from app.trading_requirements.models import RequirementCategory, RequirementItem


class RiskRequirementsBuilder:
    """Build future risk requirements only."""

    def build(self) -> RequirementCategory:
        topics = [
            "Max loss policy requirements",
            "Exposure policy requirements",
            "Drawdown policy requirements",
            "Account protection requirements",
            "Risk approval requirements",
            "Simulation-before-action requirements",
            "Risk audit requirements",
        ]
        return RequirementCategory(
            category_id="risk",
            title="Risk Requirements",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return RequirementItem(
            requirement_id=f"RISK-{index:02d}",
            title=title,
            description=f"Define {title.lower()} as a future governance prerequisite.",
            category="risk",
            priority="مرتفع",
            rationale="Risk governance must exist before any future implementation.",
            verification_method="risk governance review",
            safety_notes=["Requirement only; no account or money handling is added."],
        ).to_dict()
