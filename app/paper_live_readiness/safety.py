"""Safety checks for readiness-only paper-to-live assessment."""

from __future__ import annotations

from typing import Any

from app.paper_live_readiness.models import FAIL, PASS


class PaperToLiveSafetyEngine:
    """Guarantee the phase remains readiness-only and non-executing."""

    REQUIRED_FLAGS = (
        "not_execution",
        "not_real_execution",
        "not_order_placement",
        "not_real_order_placement",
        "not_live_trading",
        "not_broker_access",
        "not_broker_api",
        "not_browser_automation",
        "not_authentication",
        "not_account_login",
        "not_credential_handling",
        "not_real_money",
        "not_position_management",
        "not_trading_automation",
        "not_broker_control",
    )

    def evaluate(self, metadata: dict[str, bool]) -> dict[str, Any]:
        missing = [flag for flag in self.REQUIRED_FLAGS if metadata.get(flag) is not True]
        status = PASS if not missing else FAIL
        return {
            "status": status,
            "safety_score": 100.0 if status == PASS else 0.0,
            "missing_flags": missing,
            "no_execution": metadata.get("not_execution") is True,
            "no_live_trading": metadata.get("not_live_trading") is True,
            "no_broker_access": metadata.get("not_broker_access") is True,
            "no_browser_automation": metadata.get("not_browser_automation") is True,
            "no_authentication": metadata.get("not_authentication") is True,
            "no_credential_handling": metadata.get("not_credential_handling") is True,
            "no_order_placement": metadata.get("not_order_placement") is True,
            "readiness_only": True,
            "paper_only": True,
            "research_only": True,
        }
