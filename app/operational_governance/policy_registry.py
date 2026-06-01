"""Operational policy registry builder."""

from app.operational_governance.models import OperationalPolicy, governance_category


class PolicyRegistryBuilder:
    """Build operational policy registry."""

    def build(self) -> OperationalPolicy:
        return governance_category(
            OperationalPolicy,
            "policy_registry",
            "Operational Policy Registry",
            [
                "Safety policy",
                "Risk policy",
                "Release policy",
                "Incident policy",
                "Monitoring policy",
                "Audit policy",
                "Change policy",
                "Compliance policy",
            ],
        )
