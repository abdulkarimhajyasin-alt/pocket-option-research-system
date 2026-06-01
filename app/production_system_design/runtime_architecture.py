"""Runtime architecture design blueprint."""

from app.production_system_design.models import RuntimeBlueprint, design_category


class RuntimeArchitectureBuilder:
    """Build runtime architecture design only."""

    def build(self) -> RuntimeBlueprint:
        return design_category(
            RuntimeBlueprint,
            "runtime_architecture",
            "Runtime Architecture",
            [
                "Process model",
                "Worker model",
                "Scheduler model",
                "Event flow",
                "Failure isolation",
                "Restart behavior",
                "Health checks",
                "Safe degraded mode",
            ],
        )
