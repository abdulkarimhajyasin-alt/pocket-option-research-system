"""Architecture-only future risk governance blueprint."""

from __future__ import annotations

from app.post_research_architecture.models import FutureRiskArchitectureBlueprint


class RiskBlueprintBuilder:
    """Build a documents-only future risk architecture blueprint."""

    def build(self) -> FutureRiskArchitectureBlueprint:
        return FutureRiskArchitectureBlueprint(
            risk_domains=[
                "Capital exposure",
                "Daily loss",
                "Drawdown",
                "Instrument concentration",
                "Operational dependency failure",
                "Human override governance",
            ],
            hard_limits=[
                "Global disable threshold",
                "Per-strategy exposure ceiling",
                "Per-session stop condition",
                "Maximum command rate",
            ],
            kill_switch_requirements=[
                "Independent from strategy code",
                "Manual and automated disable modes",
                "Audited activation reason",
                "Fail-closed default",
            ],
            max_loss_rules=[
                "Daily loss threshold",
                "Rolling-period loss threshold",
                "Consecutive-loss stop condition",
            ],
            drawdown_rules=[
                "Peak-to-trough limit",
                "Recovery confirmation requirement",
                "Escalation after repeated drawdown events",
            ],
            exposure_rules=[
                "Single-asset cap",
                "Correlated-asset cap",
                "Strategy-level cap",
                "Time-window cap",
            ],
            incident_response=[
                "Immediate disable",
                "Evidence preservation",
                "Human review",
                "Post-incident corrective action",
            ],
            audit_requirements=[
                "Risk decision log",
                "Limit-change history",
                "Override approval trail",
                "Incident timeline",
            ],
        )
