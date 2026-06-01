"""Gate maturity assessment."""

from app.control_assurance.models import GateAssessment, assurance_item


class GateMaturityAssessmentEngine:
    """Assess governance readiness gate maturity."""

    AREAS = [
        "clear criteria",
        "evidence requirements",
        "gate owner",
        "review process",
        "blocker logic",
        "forbidden approval state prevention",
    ]

    def assess(self) -> dict[str, object]:
        items = [
            assurance_item(
                index,
                area,
                "gate",
                82,
                "Approval Board",
                ["gate evidence", "review evidence"],
            )
            for index, area in enumerate(self.AREAS, 1)
        ]
        return GateAssessment(items=items).to_dict()
