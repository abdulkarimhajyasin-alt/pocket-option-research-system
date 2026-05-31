"""Compliance validation for integration safety boundary."""

from __future__ import annotations

from typing import Any


class IntegrationComplianceEngine:
    """Evaluate research, observation, paper, and non-execution compliance."""

    REQUIRED_FLAGS = (
        "research_only",
        "observation_only",
        "paper_only",
        "not_execution",
        "not_real_execution",
        "not_broker_access",
        "not_broker_api",
        "not_browser_automation",
        "not_authentication",
        "not_account_login",
        "not_credential_handling",
        "not_order_placement",
        "not_real_order_placement",
        "not_real_money",
        "not_position_management",
        "not_live_trading",
        "not_external_execution_adapter",
        "not_trading_automation",
    )

    def evaluate(self, metadata: dict[str, bool]) -> dict[str, Any]:
        missing = [flag for flag in self.REQUIRED_FLAGS if metadata.get(flag) is not True]
        passed = len(self.REQUIRED_FLAGS) - len(missing)
        score = round((passed / len(self.REQUIRED_FLAGS)) * 100.0, 2)
        return {
            "research_only_compliance": metadata.get("research_only") is True,
            "observation_only_compliance": metadata.get("observation_only") is True,
            "paper_only_compliance": metadata.get("paper_only") is True,
            "no_execution_compliance": metadata.get("not_execution") is True,
            "no_broker_compliance": metadata.get("not_broker_access") is True,
            "no_browser_automation_compliance": (
                metadata.get("not_browser_automation") is True
            ),
            "missing_flags": missing,
            "compliance_score": score,
            "safety_boundary_only": True,
        }
