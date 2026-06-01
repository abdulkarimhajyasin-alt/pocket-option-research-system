"""Governance review board builder."""

from app.operational_governance.models import ReviewBoard, governance_category


class ReviewBoardBuilder:
    """Build future review board definitions."""

    def build(self) -> ReviewBoard:
        return governance_category(
            ReviewBoard,
            "review_boards",
            "Review Boards",
            [
                "Architecture Review Board",
                "Risk Review Board",
                "Compliance Review Board",
                "Operations Review Board",
                "Release Review Board",
                "Incident Review Board",
            ],
        )
