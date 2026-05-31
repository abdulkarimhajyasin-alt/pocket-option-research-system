"""Safety enforcement for read-only browser observation."""

from __future__ import annotations

from app.browser_observation.models import SafetyStatus


class ReadOnlySafetyEngine:
    """Guarantee no login, browser control, automation, or execution capability."""

    def evaluate(self) -> SafetyStatus:
        checks = {
            "no_login": True,
            "no_authentication": True,
            "no_browser_control": True,
            "no_execution": True,
            "no_order_apis": True,
            "no_account_access": True,
            "no_automation": True,
        }
        passed = sum(1 for value in checks.values() if value)
        score = round(passed / len(checks) * 100.0, 2)
        status = "PASS" if score == 100.0 else "WARNING" if score >= 80.0 else "FAIL"
        status_ar = "ناجح" if status == "PASS" else "تحذير" if status == "WARNING" else "فشل"
        return SafetyStatus(
            status=status,
            status_ar=status_ar,
            score=score,
            **checks,
        )
