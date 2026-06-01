"""Safety requirements documents."""

from __future__ import annotations

from app.trading_requirements.models import RequirementCategory, RequirementItem


class SafetyRequirementsBuilder:
    """Build safety requirements only."""

    def build(self) -> RequirementCategory:
        topics = [
            "Safety boundary requirements",
            "Kill switch requirements",
            "Manual approval requirements",
            "Stop condition requirements",
            "Fail-safe behavior requirements",
            "No-autonomous-live-action requirements",
            "Incident escalation requirements",
        ]
        return RequirementCategory(
            category_id="safety",
            title="Safety Requirements",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return RequirementItem(
            requirement_id=f"SAFE-{index:02d}",
            title=title,
            description=f"Document {title.lower()} before any future program can progress.",
            category="safety",
            priority="مرتفع",
            rationale="Safety controls are mandatory prerequisites.",
            verification_method="safety review",
            safety_notes=["Current repository remains research-only and local-only."],
        ).to_dict()
