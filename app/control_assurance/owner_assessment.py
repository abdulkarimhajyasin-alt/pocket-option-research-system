"""Owner clarity assessment."""

from app.control_assurance.models import OwnerAssessment, assurance_item


class OwnerClarityAssessmentEngine:
    """Assess owner and authority clarity."""

    AREAS = [
        "clear owner",
        "accountable role",
        "reviewer role",
        "escalation path",
        "decision authority",
    ]

    def assess(self) -> dict[str, object]:
        items = [
            assurance_item(
                index,
                area,
                "owner",
                86,
                "Operations Lead",
                ["owner evidence", "decision authority evidence"],
            )
            for index, area in enumerate(self.AREAS, 1)
        ]
        return OwnerAssessment(items=items).to_dict()
