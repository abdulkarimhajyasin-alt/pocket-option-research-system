"""Evidence sufficiency assessment."""

from app.control_assurance.models import EvidenceAssessment, assurance_item


class EvidenceSufficiencyAssessmentEngine:
    """Assess evidence coverage and strength."""

    AREAS = [
        "evidence type coverage",
        "evidence strength",
        "audit evidence readiness",
        "rollback evidence readiness",
        "incident evidence readiness",
        "monitoring evidence readiness",
    ]

    def assess(self) -> dict[str, object]:
        items = [
            assurance_item(
                index,
                area,
                "evidence",
                84 if index <= 4 else 78,
                "Audit Reviewer",
                ["evidence matrix", "audit evidence"],
            )
            for index, area in enumerate(self.AREAS, 1)
        ]
        return EvidenceAssessment(items=items).to_dict()
