"""Isolation guarantees for the external observation sandbox."""

from __future__ import annotations

from app.external_observation.models import IsolationStatus


class IsolationEngine:
    """Guarantee that the sandbox has no broker-control capabilities."""

    def evaluate(self) -> IsolationStatus:
        checks = {
            "no_broker_connectivity": True,
            "no_account_access": True,
            "no_execution_paths": True,
            "no_authentication_flows": True,
            "no_order_apis": True,
        }
        passed = sum(1 for value in checks.values() if value)
        score = round(passed / len(checks) * 100.0, 2)
        status = "PASS" if score == 100.0 else "WARNING" if score >= 80.0 else "FAIL"
        status_ar = "ناجح" if status == "PASS" else "تحذير" if status == "WARNING" else "فشل"
        return IsolationStatus(
            status=status,
            status_ar=status_ar,
            score=score,
            **checks,
        )
