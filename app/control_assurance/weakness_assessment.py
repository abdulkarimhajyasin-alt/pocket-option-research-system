"""Weakness severity assessment."""

from app.control_assurance.models import WeaknessAssessment, assurance_item


class WeaknessAssessmentEngine:
    """Classify assurance weaknesses."""

    AREAS = [
        "weak mapping review",
        "missing evidence review",
        "missing owner review",
        "missing policy review",
        "missing gate review",
        "unsafe wording review",
    ]

    def assess(self) -> dict[str, object]:
        items = [
            assurance_item(
                index,
                area,
                "weakness",
                75,
                "Audit Reviewer",
                ["weakness register", "mitigation evidence"],
                weaknesses=["Requires formal governance review"],
            )
            for index, area in enumerate(self.AREAS, 1)
        ]
        return WeaknessAssessment(items=items).to_dict()
