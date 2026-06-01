"""Control evidence requirement builder."""

from app.operational_governance.models import (
    ControlEvidenceRequirement,
    governance_category,
)


class ControlEvidenceBuilder:
    """Build governance evidence requirements."""

    def build(self) -> ControlEvidenceRequirement:
        return governance_category(
            ControlEvidenceRequirement,
            "control_evidence",
            "Control Evidence Requirements",
            [
                "Approval decision evidence",
                "Release decision evidence",
                "Incident decision evidence",
                "Rollback decision evidence",
                "Risk decision evidence",
                "Compliance decision evidence",
                "Monitoring readiness evidence",
            ],
        )
