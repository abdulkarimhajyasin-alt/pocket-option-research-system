"""Architecture-only future execution blueprint."""

from __future__ import annotations

from app.post_research_architecture.models import FutureExecutionBlueprint


class ExecutionBlueprintBuilder:
    """Build a documents-only execution architecture blueprint."""

    def build(self) -> FutureExecutionBlueprint:
        return FutureExecutionBlueprint(
            required_components=[
                "Separate gateway boundary specification",
                "Command approval model",
                "Immutable audit log",
                "Idempotency and duplicate-command prevention",
                "Independent safety governor",
                "Manual disable procedure",
            ],
            forbidden_current_implementation=[
                "No real order placement in this repository",
                "No broker commands",
                "No account state mutation",
                "No external gateway code",
            ],
            safety_controls=[
                "Human approval gate before any future build",
                "Independent risk validation before command creation",
                "Command dry-run evidence before external feasibility review",
                "Documented rollback and disable process",
            ],
            audit_requirements=[
                "Every future command must have a deterministic request id",
                "Every state transition must be recorded",
                "Every rejection must include a reason",
            ],
            failure_modes=[
                "Duplicate command",
                "Delayed acknowledgement",
                "Partial state update",
                "Risk service unavailable",
                "External dependency outage",
            ],
            prerequisites=[
                "Separate future program approved",
                "Risk governance designed",
                "Broker isolation designed",
                "Compliance review completed",
            ],
        )
