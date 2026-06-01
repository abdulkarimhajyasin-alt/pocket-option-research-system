"""Policy coverage mapping builder."""

from app.governance_traceability.models import PolicyCoverageMapping, mapping_item


class PolicyMappingBuilder:
    """Map operational policies to design areas and evidence."""

    def build(self) -> dict[str, object]:
        policies = [
            "safety policy",
            "risk policy",
            "release policy",
            "incident policy",
            "monitoring policy",
            "audit policy",
            "change policy",
            "compliance policy",
        ]
        items = [
            mapping_item(
                index,
                policy,
                "production design area and governance gate",
                "policy",
                "Compliance Reviewer",
                ["policy evidence", "control evidence", "review evidence"],
            )
            for index, policy in enumerate(policies, 1)
        ]
        return PolicyCoverageMapping(items=items).to_dict()
