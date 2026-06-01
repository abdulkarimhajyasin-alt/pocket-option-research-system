"""Program registry builder for the architecture-program foundation."""

from __future__ import annotations

from app.trading_architecture_program.models import ProgramRegistry
from app.trading_architecture_program.schemas import PROGRAM_NAME, PROGRAM_STATUS


class ProgramRegistryBuilder:
    """Build the local program registry artifact."""

    def build(
        self,
        domains: list[dict[str, object]],
        workstreams: list[dict[str, object]],
        gates: list[dict[str, object]],
    ) -> ProgramRegistry:
        return ProgramRegistry(
            program_name=PROGRAM_NAME,
            program_status=PROGRAM_STATUS,
            architecture_domains=domains,
            workstreams=workstreams,
            decision_gates=gates,
            prerequisites=[
                "Research Platform v1.0 frozen",
                "Documentation complete",
                "Architecture separation approved",
                "Risk and governance documents drafted",
            ],
            blocked_items=[
                "broker API implementation",
                "execution implementation",
                "credential handling",
                "external connectivity",
                "live trading readiness claims",
            ],
            forbidden_items=[
                "Broker APIs",
                "Broker adapters",
                "Pocket Option login",
                "Credential handling",
                "Browser automation",
                "Selenium",
                "Playwright",
                "Order placement",
                "Execution engines",
                "Live trading",
                "Money handling",
                "Account monitoring",
                "Deposits",
                "Withdrawals",
                "External connectivity",
            ],
        )
