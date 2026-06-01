"""Human approval workflow builder."""

from app.operational_governance.models import ApprovalWorkflow, governance_category


class ApprovalWorkflowBuilder:
    """Build documented approval workflows only."""

    def build(self) -> ApprovalWorkflow:
        return governance_category(
            ApprovalWorkflow,
            "approval_workflows",
            "Human Approval Workflows",
            [
                "Architecture change approval",
                "Requirements change approval",
                "Risk policy change approval",
                "Production design change approval",
                "Release candidate approval",
                "Incident response approval",
                "Emergency stop approval",
                "Rollback approval",
            ],
        )
