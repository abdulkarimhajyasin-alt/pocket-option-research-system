"""Session factor scoring."""

from __future__ import annotations

from typing import Any

from app.confluence.models import SessionFactorScore


class SessionFactorEngine:
    """Evaluate session quality, activity, and performance."""

    def evaluate(
        self,
        opportunity: dict[str, Any],
        session_performance: dict[str, Any],
    ) -> SessionFactorScore:
        session_quality = self._float(opportunity.get("session_score"))
        session = self._session_name(opportunity)
        performance = self._float(session_performance.get(session)) * 100
        if performance == 0:
            performance = self._float(session_performance.get("غير متاح"))
        activity = min(100.0, session_quality * 1.05)
        score = round(
            session_quality * 0.45 + activity * 0.25 + performance * 0.30,
            2,
        )
        strengths = []
        weaknesses = []
        warnings = []
        if session_quality >= 65:
            strengths.append("جودة الجلسة داعمة")
        else:
            weaknesses.append("جودة الجلسة محدودة")
        if performance <= 0:
            warnings.append("أداء الجلسة غير كاف في العينة")
        return SessionFactorScore(
            name="عامل الجلسة",
            score=self._bound(score),
            explanation=("تقييم بحثي لجودة الجلسة ونشاطها وأدائها."),
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metrics={
                "session": session,
                "session_quality": session_quality,
                "session_activity": activity,
                "session_performance": performance,
            },
        )

    def _session_name(self, opportunity: dict[str, Any]) -> str:
        factors = opportunity.get("supporting_factors", [])
        if isinstance(factors, list):
            for item in factors:
                text = str(item)
                if "جلسة" in text or text in {"آسيا", "لندن", "نيويورك"}:
                    return text
        return "غير متاح"

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
