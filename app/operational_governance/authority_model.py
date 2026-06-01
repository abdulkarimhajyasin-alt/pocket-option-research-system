"""Operational authority model builder."""

from app.operational_governance.models import AuthorityRole, governance_category


class OperationalAuthorityModelBuilder:
    """Build future authority roles without user accounts."""

    def build(self) -> AuthorityRole:
        return governance_category(
            AuthorityRole,
            "authority_model",
            "Operational Authority Model",
            [
                "System owner responsibility",
                "Risk owner responsibility",
                "Operations lead responsibility",
                "Compliance reviewer responsibility",
                "Technical reviewer responsibility",
                "Incident commander responsibility",
                "Audit reviewer responsibility",
                "Approval board responsibility",
            ],
        )
