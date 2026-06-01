"""Audit control framework builder."""

from app.operational_governance.models import AuditControl, governance_category


class AuditControlBuilder:
    """Build audit control framework."""

    def build(self) -> AuditControl:
        return governance_category(
            AuditControl,
            "audit_controls",
            "Audit Control Framework",
            [
                "Audit event requirements",
                "Control checks",
                "Evidence records",
                "Review intervals",
                "Control owners",
                "Exception handling",
                "Audit trail requirements",
            ],
        )
