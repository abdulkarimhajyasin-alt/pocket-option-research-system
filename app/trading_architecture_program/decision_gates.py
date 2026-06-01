"""Decision gates for the future architecture program."""

from __future__ import annotations

from app.trading_architecture_program.models import DecisionGate


class DecisionGateBuilder:
    """Build formal gates that cannot approve live trading."""

    def build(self) -> list[DecisionGate]:
        gates = [
            ("gate-1", "Research Platform Frozen", "Confirm v1.0 research freeze."),
            ("gate-2", "Documentation Complete", "Confirm final architecture documentation."),
            (
                "gate-3",
                "Architecture Separation Approved",
                "Confirm future program separation.",
            ),
            ("gate-4", "Risk Architecture Approved", "Approve risk architecture documents."),
            ("gate-5", "Governance Approved", "Approve governance and review model."),
            (
                "gate-6",
                "External Integration Review Approved",
                "Approve feasibility review only.",
            ),
            ("gate-7", "Future Program Approval", "Approve future architecture program scope."),
        ]
        return [
            DecisionGate(
                gate_id=gate_id,
                name=name,
                approval_scope=scope,
                required_evidence=[
                    "architecture document",
                    "safety boundary review",
                    "human approval record",
                ],
                may_approve_live_trading=False,
            )
            for gate_id, name, scope in gates
        ]
