"""Environment strategy design blueprint."""

from app.production_system_design.models import EnvironmentPlan, design_category


class EnvironmentStrategyBuilder:
    """Build future environment strategy design only."""

    def build(self) -> EnvironmentPlan:
        return design_category(
            EnvironmentPlan,
            "environment_strategy",
            "Environment Strategy",
            [
                "Local research",
                "Staging simulation",
                "Paper operations",
                "External feasibility sandbox",
                "Production candidate",
                "Production restricted",
            ],
        )
