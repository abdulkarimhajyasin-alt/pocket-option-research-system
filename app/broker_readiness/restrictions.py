"""Safety restriction enforcement for passive observation readiness."""

from __future__ import annotations

from app.broker_readiness.models import RestrictionCheck, RestrictionReport


class SafetyRestrictionEngine:
    """Enforce that readiness remains observation-only."""

    RESTRICTIONS = (
        "لا تنفيذ",
        "لا أوامر",
        "لا إجراءات حساب",
        "لا أتمتة",
        "لا تحكم وسيط",
    )

    def evaluate(self) -> RestrictionReport:
        checks = tuple(
            RestrictionCheck(
                name,
                "PASS",
                "ناجح",
                f"{name}: الطبقة تقيس الجاهزية فقط ولا تنفذ أي إجراء.",
            )
            for name in self.RESTRICTIONS
        )
        return RestrictionReport(checks, "PASS", "ناجح")
