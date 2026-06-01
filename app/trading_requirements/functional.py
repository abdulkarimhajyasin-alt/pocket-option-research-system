"""Functional requirements documents for future architecture work."""

from __future__ import annotations

from app.trading_requirements.models import RequirementCategory, RequirementItem


class FunctionalRequirementsBuilder:
    """Build high-level functional requirements only."""

    def build(self) -> RequirementCategory:
        return RequirementCategory(
            category_id="functional",
            title="Functional Requirements",
            items=[
                self._item("signal-consumption", "Signal consumption requirements"),
                self._item("decision-review", "Human decision review requirements"),
                self._item("paper-boundary", "Paper-to-external boundary requirements"),
                self._item("audit-events", "Audit event requirements"),
                self._item("approval", "Human approval requirements"),
                self._item("configuration-review", "Configuration review requirements"),
            ],
        )

    def _item(self, suffix: str, title: str) -> dict[str, object]:
        return RequirementItem(
            requirement_id=f"FR-{suffix}",
            title=title,
            description=f"Define {title.lower()} for a future program without implementation.",
            category="functional",
            priority="مرتفع",
            rationale="Future system behavior must be documented before design can progress.",
            verification_method="architecture requirements review",
            safety_notes=["Requirement only; no current implementation is allowed."],
        ).to_dict()
