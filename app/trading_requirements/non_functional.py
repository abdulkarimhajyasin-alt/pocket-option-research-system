"""Non-functional requirements documents."""

from __future__ import annotations

from app.trading_requirements.models import RequirementCategory, RequirementItem


class NonFunctionalRequirementsBuilder:
    """Build non-functional requirements only."""

    def build(self) -> RequirementCategory:
        topics = [
            "Reliability requirements",
            "Performance requirements",
            "Determinism requirements",
            "Maintainability requirements",
            "Observability requirements",
            "Testability requirements",
            "Recoverability requirements",
            "Scalability requirements",
        ]
        return RequirementCategory(
            category_id="non_functional",
            title="Non-Functional Requirements",
            items=[self._item(index, title) for index, title in enumerate(topics, 1)],
        )

    def _item(self, index: int, title: str) -> dict[str, object]:
        return RequirementItem(
            requirement_id=f"NFR-{index:02d}",
            title=title,
            description=f"Specify {title.lower()} for future architecture review.",
            category="non_functional",
            priority="متوسط",
            rationale="Non-functional constraints must be known before implementation planning.",
            verification_method="quality attribute review",
            safety_notes=["No runtime capability is added by this requirement."],
        ).to_dict()
