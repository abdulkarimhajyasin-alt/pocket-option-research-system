"""Governance readiness gate engine."""

from app.operational_governance.schemas import GOVERNANCE_ONLY_FLAGS


class GovernanceReadinessGateEngine:
    """Evaluate governance gates for design review readiness."""

    def build(self) -> dict[str, object]:
        gate_titles = [
            "Authority model approved",
            "Approval workflows documented",
            "Change management documented",
            "Release governance documented",
            "Incident escalation documented",
            "Emergency stop governance documented",
            "Audit controls documented",
            "Policy registry complete",
            "Review boards defined",
            "Evidence requirements defined",
        ]
        gates = [
            {
                "gate_id": f"GOV-GATE-{index:02d}",
                "title": title,
                "required": True,
                "current_status": "missing",
                "blocks_progress": True,
                "may_approve_live_trading": False,
                **GOVERNANCE_ONLY_FLAGS,
            }
            for index, title in enumerate(gate_titles, 1)
        ]
        return {
            "readiness_state": "Not Ready",
            "gate_count": len(gates),
            "blocking_gate_count": len(gates),
            "missing_approval_count": len(gates),
            "gates": gates,
            **GOVERNANCE_ONLY_FLAGS,
        }
